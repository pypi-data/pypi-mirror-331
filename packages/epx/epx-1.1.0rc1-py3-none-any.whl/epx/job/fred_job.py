import json
import logging
import os
import io
import shutil
import tempfile
import time
import zipfile
from datetime import date
from datetime import datetime
from itertools import chain
from pathlib import Path
from typing import (
    Iterable,
    List,
    Literal,
    Optional,
    Union,
)

import pandas as pd
import requests
from pandas._libs.tslibs.nattype import NaTType
from pydantic import BaseModel

from epx.core.cloud.auth import platform_api_headers
from epx.core.errors.api_errors import NotFoundError, UnauthorizedUserError
from epx.core.errors.validation_error import JobDoesNotExistError
from epx.core.types.common import RunParameters, UserRequests
from epx.core.types.error_type import ForbiddenResponse, NotFoundResponse
from epx.job.config.fred_model_config import FREDModelConfig, FREDModelParams
from epx.core.models.synthpop import SynthPopModel
from epx.core.utils.config import (
    default_results_dir,
    get_auth_config_dir,
    get_cache_dir,
    get_max_retry_value,
    read_auth_config,
)
from epx.job.job import Job
from epx.job.result.fred_job_results import FREDJobResults
from epx.job.status.fred_job_status import FREDJobStatus
from epx.run.exec.cloud.strategy import RunExecuteMultipleCloudStrategy
from epx.run.fred_run import FREDRun

logger = logging.getLogger(__name__)


class _ModelConfigModel(BaseModel):
    synth_pop: Optional[SynthPopModel] = None
    start_date: Optional[Union[date, str]] = None
    end_date: Optional[Union[date, str]] = None
    params: Optional[FREDModelParams] = None
    seed: Optional[Union[int, tuple[int, ...]]] = None
    n_reps: int = 1

    @staticmethod
    def from_model_config(model_config: "FREDModelConfig") -> "_ModelConfigModel":
        return _ModelConfigModel(
            synth_pop=(
                SynthPopModel.from_synth_pop(model_config.synth_pop)
                if model_config.synth_pop
                else None
            ),
            start_date=model_config.start_date,
            end_date=model_config.end_date,
            params=model_config.model_params,
            seed=model_config.seed,
            n_reps=model_config.n_reps,
        )

    def as_model_config(self) -> "FREDModelConfig":
        return FREDModelConfig(
            synth_pop=self.synth_pop.as_synth_pop() if self.synth_pop else None,
            start_date=self.start_date,
            end_date=self.end_date,
            model_params=self.params,
            seed=self.seed,
            n_reps=self.n_reps,
        )


class _JobModel(BaseModel):
    program: Path
    config: list[_ModelConfigModel]
    key: str
    size: str = "hot"
    fred_version: str = "latest"
    n: int = 1
    results_dir: Optional[Path] = None
    fred_files: Optional[Iterable[Union[Path, str]]] = None
    ref_files: Optional[dict[str, Union[Path, str]]] = None

    @staticmethod
    def from_job(job: "FREDJob") -> "_JobModel":
        return _JobModel(
            program=job.program,
            config=[_ModelConfigModel.from_model_config(x) for x in job.config],
            key=job.key,
            size=job.size,
            fred_version=job.fred_version,
            results_dir=job.results_dir,
            fred_files=job.fred_files,
            ref_files=job.ref_files,
        )

    def as_job(self) -> "FREDJob":
        return FREDJob(
            program=self.program,
            config=[x.as_model_config() for x in self.config],
            key=self.key,
            size=self.size,
            fred_version=self.fred_version,
            results_dir=self.results_dir,
            fred_files=self.fred_files,
            ref_files=self.ref_files,
        )


class _DeleteOutcome(BaseModel):
    runId: int
    reason: Literal["Success", "NotFound", "Forbidden", "InternalError"]


class _StopResponse(BaseModel):
    """Response object from the /runs endpoint for deleted SRS runs .

    Attributes
    ----------
    description : str
        The description of the status of the stop
    deletedIds: list[_DeleteOutcome], optional
        List of runIds deleted successfully
    failedIds: list[_DeleteOutcome], optional
        List of runIds deleted unsuccessfully
    """

    description: str
    deletedIds: Optional[list[_DeleteOutcome]] = None
    failedIds: Optional[list[_DeleteOutcome]] = None


class _JobDetails(BaseModel):
    """Details of a single job.

    Attributes
    ----------
    userId : int
        The id of the user
    id: int
        The id of the job
    name: str
        The name of the job
    created: Date
        The date created job
    """

    id: int
    userId: int
    name: str
    created: datetime


class _GetListJobResponse(BaseModel):
    """Response object from the /jobs endpoint for get list my jobs .

    Attributes
    ----------
    jobs : list[_JobDetails]
        List of job details returned from the API.
    """

    jobs: List[_JobDetails]  # List of jobs


class _GetSignedUploadUrl(BaseModel):
    """Response object of presigned url.

    Attributes
     ----------
    url: str
        The presigned url from s3 for uploading models.
    """

    url: str


class _SignedDownloadUrlInfo(BaseModel):
    """Response object of signed url.

    Attributes
     ----------
    run_id : str
        ID for the run.
    url: str
        The signed url from s3 for downloading job outputs.
    """

    run_id: int
    url: str


class _GetSignedDownloadUrlResponse(BaseModel):
    """Response collection of signed urls from the /job?job_name= endpoint."""

    urls: list[_SignedDownloadUrlInfo]


class _ErrorRun(BaseModel):
    """Represent a failed execution attempt of a run.

    Attributes
     ----------
    runId: int
        A identifier for the retry attempt.
    retry_times: int
        Total number of retry attempts.
    """

    runId: int
    retry_times: int


class _RetryResponse(BaseModel):
    """Response object from the /runs/retry endpoint for retry SRS error runs .

    Attributes
    ----------
    status : str
         A string indicating the status of the request
    runRequestIds: list[int]
        List of submitted runRequestIds
    """

    status: str
    runRequestIds: List[int]


class FREDJob(Job):
    def __init__(
        self,
        program: Union[Path, str],
        config: Iterable[FREDModelConfig],
        key: str,
        size: str = "hot",
        fred_version="latest",
        results_dir: Optional[Union[Path, str]] = None,
        api_url: Optional[str] = None,
        bearer_token: Optional[str] = None,
        runIds=[],
        fred_files: Optional[Iterable[Union[Path, str]]] = None,
        ref_files: Optional[dict[str, Union[Path, str]]] = None,
        jobId: Optional[int] = None,
        visualize: Optional[bool] = None,
    ):
        """Client interface for configuring and running collections of
        simulation runs.

        Parameters
        ----------
        program : Union[Path, str]
            Path to the FRED entrypoint file.
        config : Iterable[FREDModelConfig]
            Set of model run configurations to execute.
        key : str
            Unique identifier for the job.
        size : str, optional
            Instance size to use for each run in the job, by default "hot".
        fred_version : str, optional
            FRED Simulation Engine version to use for each run in the job,
            by default "latest".
        results_dir : Optional[Union[Path, str]], optional
            Root results directory to use to store simulation results. By
            default ``None``, causing results to be stored in the default
            directory, ``~/results``.
        api_url: endpoint to use for call api - str, optional
        bearer_token: token to add request header when call api - str, optional
        fred_files : list[str]
            list of all additional .fred files to be appended to the main.fred. Files are appended in the other they are listed # noqa: E501
        ref_files : dict[str, Path]
            dict with key equal to the local path to a reference file and the value as the destination path # noqa: E501
        """

        self.program = Path(program)
        self.config = list(config)
        self.key = key
        self.size = size
        self.fred_version = fred_version
        self.api_url = api_url
        self.bearer_token = bearer_token
        self.results_dir = (
            Path(results_dir).expanduser().resolve()
            if results_dir
            else default_results_dir()
        )
        self.runIds = runIds
        self.jobId = jobId
        self.visualize = visualize
        self._error_runs: List[_ErrorRun] = []
        self._runs = self._build_runs(
            self.program,
            self.config,
            self.results_dir,
            self.key,
            self.size,
            self.fred_version,
        )
        logger.info(f"Created {len(self._runs)} runs for job {self.key}")
        self.fred_files = fred_files
        self.ref_files = ref_files
        if self.api_url and self.bearer_token:
            self._create_auth_config_file(
                self.api_url,
                self.bearer_token,
            )

    @property
    def run_meta(self) -> pd.DataFrame:
        """Return metadata about each run in the job.

        Returns
        -------
        pd.DataFrame
            A DataFrame with columns:
                * ``run_id``: The index of the run in the job.
                * ``program``: The path to the FRED entrypoint file.
                * ``synth_pop``: The name of the synthetic population used.
                * ``locations``: The locations in the synthetic population.
                * ``start_date``: The start date of the simulation.
                * ``end_date``: The end date of the simulation.
                * ``params``: The model parameters.
                * ``seed``: The random seed used for the run.
                * ``size``: The instance size used for the run.
        """

        def proc_date(date: Optional[date]) -> Union[pd.Timestamp, NaTType]:
            return pd.Timestamp(date) if date is not None else pd.NaT

        return pd.DataFrame(
            {
                "run_id": run_id,
                "program": str(run.params.program),
                "synth_pop": (
                    run.params.synth_pop.name if run.params.synth_pop else None
                ),
                "locations": (
                    run.params.synth_pop.locations if run.params.synth_pop else None
                ),
                "start_date": proc_date(run.params.start_date),
                "end_date": proc_date(run.params.end_date),
                "params": run.params.model_params,
                "seed": run.params.seed,
                "size": run.size,
            }
            for run_id, run in enumerate(self._runs)
        )

    @property
    def status(self) -> FREDJobStatus:
        """Current status of the job."""
        return FREDJobStatus(
            self.key, ((run_id, run) for run_id, run in enumerate(self._runs))
        )

    @property
    def results(self) -> FREDJobResults:
        """Object providing access to simulation results.
        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
            If the results do not exist in S3.
            If the Job is not DONE.
        """

        # To check if the results exist in the user's local results cache,
        # when a user attempts to interact with results.
        error_message = "Error occurred while accessing to simulation results"
        if self.jobId is None:
            jobId = FREDJob.get_job_id_by_key(self.key)
            if jobId is None:
                raise RuntimeError(error_message)
            self.jobId = jobId

        cache_dir = self._results_cache_dir(self.jobId)
        isExist = self._check_results_cache_exist(str(cache_dir))
        if not isExist:
            # Get request to FRED Cloud API to get signed urls for downloading results
            signedUrls = self._get_signed_download_url(self.jobId).urls
            # To check if the urls is empty
            if not len(signedUrls):
                raise RuntimeError(error_message)
            # To download output files from signed url and extract them
            for run_id, url in signedUrls:
                response = requests.get(url[1])
                # Check HTTP response status code and raise exceptions as appropriate
                if not response.ok:
                    raise RuntimeError(error_message)
                # Get file content and extract all on the fly
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
                    path = self._results_cache_dir(self.jobId) / str(run_id[1])
                    zip_ref.extractall(str(path))
        run_ids = self._get_run_id_from_results_cache()
        run_ids = sorted(run_ids, key=int)

        if len(run_ids) != len(self._runs):
            raise RuntimeError(error_message)

        for idx, run in enumerate(self._runs):
            run.output_result_cache_dir = cache_dir / f"{run_ids[idx]}/work/outputs"
            run.run_id = int(run_ids[idx])

        completed_run_results_with_ids = (
            (run_id, run.results)
            for run_id, run in enumerate(self._runs)
            if run.status.name == "DONE" and run.results is not None
        )
        return FREDJobResults(completed_run_results_with_ids)

    def execute(
        self,
        time_out: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[int] = None,
    ) -> None:
        """Execute the runs comprising the job.

        Parameters
        ----------
        time_out : int, optional
            The timeout of the job execution (in seconds).
        max_retries : int, optional
            Maximum number of retry attempts.
        backoff_factor : int, optional
            Factor by which the sleep time is increased.

        Raises
        ------
        RuntimeError:
            If the execution time exceeds timeout or
            If the execution occurs error.
        """

        self._verify_output_dir_empty()
        if time_out and (not isinstance(time_out, int) or time_out < 0):
            logger.error("Invalid timeout value")
            raise ValueError("Invalid timeout value")
        self._init_cache()
        self._write_job_config()

        self._package_and_upload_models_to_s3()
        # Start time of the job execution
        start_time = time.time()

        # Create a combined execution strategy
        exec_strategy_all = RunExecuteMultipleCloudStrategy(self._runs)

        for run in self._runs:
            run._verify_job_name()
            run._verify_output_dir_empty()
            run._init_cache()
        results = exec_strategy_all.execute_all(
            max_retries=max_retries, backoff_factor=backoff_factor
        )

        for run, result in zip(self._runs, results):
            run.run_id = result.run_id
            if result.run_id:
                self.runIds.append(result.run_id)
            run._write_run_config()

        if results[0] is not None:
            self.jobId = results[0].job_id

        max_retries = get_max_retry_value("max_retries_for_run")
        if time_out:
            # Time to wait (in seconds) before checking status again
            idle_time = 3
            update_count = 0
            try:
                update_interval = int(read_auth_config("update_interval"))
            except Exception:
                update_interval = 10
            while True:
                job_status = self.status.name
                status = str(job_status.value)
                if status == "DONE":
                    break
                if status == "ERROR":
                    for runId in job_status.errors:
                        self._add_run_for_retry(runId)
                    # Get errored run with retry_times < max_retries
                    error_runs = self._get_runs_for_retry(max_retries)

                    if len(error_runs) > 0:
                        # Proceed retry
                        runIds = self._retry_runs([run.runId for run in error_runs])
                        self._update_retry_times(runIds)
                    else:
                        logs = self.status.logs
                        log_msg = "; ".join(
                            logs.loc[logs.level == "ERROR"].message.tolist()
                        )
                        raise RuntimeError(
                            f"FREDJob '{self.key}' failed with the following error:\n"
                            f"{log_msg}"
                        )
                if time.time() > start_time + (time_out):
                    msg = f"FREDJob did not finish within {time_out / 60} minutes."
                    raise RuntimeError(msg)
                elif update_count >= update_interval:
                    update_count = 0
                    elapsed_time = time.time() - start_time
                    logger.info(
                        f"Job '{self.key}' is still processing "
                        f"after {elapsed_time} seconds."
                        f"{job_status.runs_done_count} runs are DONE, "
                        f"{job_status.runs_executing_count} runs are RUNNING "
                        f"and the total runs are {job_status.runs_total_count}."
                    )

                update_count += 1
                time.sleep(idle_time)

    def stop(self) -> str:
        """Stop the running job.

        Users can only stop a job with the job status is RUNNING.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
            If the job status is different "RUNNING"
        """

        if str(self.status) != "RUNNING":
            msg = f"Can not stop the job with status is {self.status}."
            raise RuntimeError(msg)

        param = ""
        for index, id in enumerate(self.runIds):
            if index != len(self.runIds) - 1:
                param += f"id={id}&"
            else:
                param += f"id={id}"

        endpoint_url = f"{read_auth_config('api-url')}/runs?{param}"
        # Patch request to delete SRS runs
        logger.debug(f"Request params: {param}")
        response = requests.patch(endpoint_url, headers=platform_api_headers())
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        response_body = _StopResponse.model_validate_json(response_payload)

        return response_body.description

    def list(
        self,
        name: Optional[str] = None,
        start_date: Optional[Union[str, "datetime"]] = None,
        end_date: Optional[Union[str, "datetime"]] = None,
    ) -> str:
        """Lists the my jobs filtered by optional name, start_date, and end_date.

        Parameters
        ----------
        name: Optional[str], optional
            Filter jobs by  name.
        start_date: Optional[Union[str, datetime]], optional
            Filter jobs starting after this date.
        end_date: Optional[Union[str, datetime]], optional
            Filter jobs ending before this date.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        params = {}
        if name:
            params["jobName"] = name

        # Check and validate start_date by format
        if start_date:
            if isinstance(start_date, str):
                try:
                    temp_start_date = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    raise RuntimeError(
                        f"start_date must be in format YYYY-MM-DD, {start_date}"
                    )
            else:
                temp_start_date = start_date
            params["startDate"] = temp_start_date.strftime("%Y-%m-%d")

        # Check and validate end_date by format
        if end_date:
            if isinstance(end_date, str):
                try:
                    temp_end_date = datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError:
                    raise RuntimeError(
                        f"end_date must be in format YYYY-MM-DD, {end_date}"
                    )
            else:
                temp_end_date = end_date
            params["endDate"] = temp_end_date.strftime("%Y-%m-%d")

        endpoint_url = f"{read_auth_config('api-url')}/jobs/me"

        # Patch request to get list my jobs
        response = requests.get(
            endpoint_url, headers=platform_api_headers(), params=params
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.json()
        response_body = _GetListJobResponse.model_validate(response_payload)

        return response_body.model_dump_json()

    def list_runs(self) -> UserRequests:
        """Retrieve Runs associated with a particular FREDJob.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/runs"
        response = requests.get(
            endpoint_url,
            headers=platform_api_headers(),
            params={"job_name": self.key},
        )
        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text
        logger.debug(f"Response payload: {response_payload}")
        response_body = UserRequests.model_validate_json(response_payload)

        return response_body

    def delete(self, interactive=True) -> None:
        """Delete all results data for the job.

        Users should be careful to ensure that the ``results_dir`` specified in
        the constructor is indeed the targeted run directory. This is a
        destructive operation and should be used with care. E.g. if
        ``results_dir = Path('/')`` this would cause the deletion of all files
        on the system that the user has write permissions for.

        Parameters
        ----------
        interactive : bool, optional
            Whether or not the ``delete`` command should be run interactively.
            When ``True`` (the default), the user will be prompted to confirm
            the deletion of the job results data. When ``False``, no
            confirmation prompt will be given. The latter option is provided to
            support programmatic usage, e.g. to delete the data for all jobs in
            a collection of jobs.
        """

        def confirm(key: str) -> bool:
            answer = input(f"Delete job '{key}'? [y/N]")
            if answer.lower() in ["y", "yes"]:
                return True
            else:
                return False

        def proceed():
            """
            Delete all run data and metadata caches if any
            """

            output_dir = self._get_job_output_dir(self.results_dir, self.key)
            cache_dir = self._cache_dir(self.key)
            paths = [output_dir, cache_dir]
            for path in paths:
                try:
                    if os.path.exists(path):
                        shutil.rmtree(path)
                except OSError:
                    raise RuntimeError(
                        f"An error occurred while deleting job {self.key}"
                    )
            print(f"FREDJob {self.key} deleted successfully.")

        if not interactive or confirm(self.key):
            proceed()

    def _write_job_config(self) -> None:
        with open(self._cache_dir(self.key) / "job.json", "w") as f:
            f.write(_JobModel.from_job(self).model_dump_json(by_alias=True))

    def _get_runs_for_retry(self, max_retry_times=0) -> List[_ErrorRun]:
        """Return a collection of errored runs.

        Attributes
        ----------
        max_retry_times : int
            If a max_retry_times is provided, filter by max_retry_times.

        Returns
        -------
        List[ErrorRun]
            Collection of errored runs.
        """

        if max_retry_times != 0:
            return [
                run for run in self._error_runs if run.retry_times < max_retry_times
            ]
        return self._error_runs

    def _add_run_for_retry(self, runId: int):
        """Add a run for retry.

        Attributes
        ----------
        runId : int
            The id of user request in DB
        """

        for run in self._error_runs:
            if run.runId == runId:
                return
        self._error_runs.append(_ErrorRun(runId=runId, retry_times=0))

    def _update_retry_times(self, runIds: List[int]):
        """Update number of retry_times for runIds in the list

        Attributes
        ----------
        runIds : List[int]
            Submitted userRequestId collection.
        """

        for run in self._error_runs:
            if run.runId in runIds:
                run.retry_times += 1

    def _retry_runs(self, runIds: List[int]) -> List[int]:
        """Retry error runs.

        Users can retry ERROR runs in a specific job .

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/runs/retry"

        # Post request to retry SRS runs
        logger.debug(f"RunRetry - Request payload: {runIds}")
        response = requests.post(
            endpoint_url, headers=platform_api_headers(), data={"runRequestIds": runIds}
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        response_body = _RetryResponse.model_validate_json(response_payload)
        # Return submitted runIds
        return response_body.runRequestIds

    def _package_and_upload_models_to_s3(self) -> None:
        ref_files = self.ref_files
        if self.fred_files is None and ref_files is None:
            return
        # Create a tmp folder
        tmp_dir = tempfile.TemporaryDirectory()
        tmp_dir_path = tmp_dir.name
        # Concatenate the fred files together
        if self.fred_files is not None:
            filenames: List[str] = [str(file) for file in self.fred_files]
            self._concatenate_fred_files(filenames, tmp_dir_path)
        # Copy and rename
        if ref_files is not None:
            self._copy_and_rename_file(ref_files, tmp_dir_path)
        # Package all files into inputs.zip file
        input_zip_file = f"{tmp_dir_path}/inputs.zip"
        with zipfile.ZipFile(input_zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            # Iterate over all files in the folder
            for root, dirs, files in os.walk(tmp_dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    #  Zip all except inputs.zip
                    if os.path.abspath(file_path) == os.path.abspath(input_zip_file):
                        continue
                    # Add the file to the zip, using a relative path inside the zip
                    zipf.write(file_path, os.path.relpath(file_path, tmp_dir_path))

        # Get signed upload url
        url = self._get_signed_upload_url(self.key)
        isSuccess = self._upload_file_to_s3_with_presigned_url(
            f"{tmp_dir_path}/inputs.zip", url
        )

        # Detele tmp folder
        tmp_dir.cleanup()
        if not isSuccess:
            raise RuntimeError("Error occurred while uploading models")

    def _get_run_id_from_results_cache(self):
        cache_dir = self._results_cache_dir(self.jobId)
        return [folder.name for folder in Path(cache_dir).iterdir() if folder.is_dir()]

    def _init_cache(self) -> None:
        self._cache_dir(self.key).mkdir(exist_ok=True, parents=True)

    def _verify_output_dir_empty(self) -> None:
        """Ensure that ``self.results_dir/self.key`` does not contain any
        regular files.

        If ``self.results_dir/self.key`` does contain regular files, this is
        interpreted as meaning that a job of the given name already exists.

        Then output to an alternate directory ([job key]-[date]-[time]).
        """

        output_dir = self._get_job_output_dir(self.results_dir, self.key)
        logger.info(f"checking output dir: {output_dir}")
        if output_dir.is_dir():
            # output_dir exists
            if any(output_dir.iterdir()):
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                appended_job_key = f"{self.key}-{timestamp}"
                message = (
                    f"A job with key '{self.key}' already exists in results directory "
                    f"and should be removed. "
                    f"Then output to an alternate directory: {appended_job_key}."
                )
                self.key = appended_job_key
                self._runs = self._build_runs(
                    self.program,
                    self.config,
                    self.results_dir,
                    appended_job_key,
                    self.size,
                    self.fred_version,
                )
                logger.warning(message)
                print(message)

    @staticmethod
    def _create_auth_config_file(api_url: str, bearer_token: str) -> None:
        config_file = get_auth_config_dir()
        if not config_file.parent.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "api-url": api_url,
            "bearer-token": bearer_token,
        }
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)

    @staticmethod
    def _get_job_output_dir(results_dir: Path, key: str) -> Path:
        return results_dir / key

    @staticmethod
    def _concatenate_fred_files(filenames: List[str], output_path: str):
        """Concatenate the fred files together."""
        try:
            with open(f"{output_path}/main.fred", "w") as file:
                for index, fname in enumerate(filenames):
                    if os.path.exists(fname):
                        with open(fname, "r") as infile:
                            file.write(infile.read())
                            if index != len(filenames) - 1:
                                file.write("\n\n")
                    else:
                        logger.error(f"Could not find file: {fname}")
                        raise RuntimeError(
                            "Error occurred while concatenate the FRED files"
                        )
        except Exception:
            logger.error("Error occurred while concatenate the FRED files")
            raise RuntimeError("Error occurred while concatenate the FRED files")

    @staticmethod
    def _copy_and_rename_file(
        ref_files: dict[str, Union[Path, str]], output_path: str
    ) -> None:
        """
        Copy and rename reference files, ensuring subdirectories are created.
        Parameters
        ----------
        ref_files : dict[str, Union[Path, str]]
            Dictionary where keys are the file path handles (relative to `output_path`)
            and values are the fully qualified source file paths to be copied.
        output_path : str
            The root directory where the files should be copied to.
        Raises
        ------
        RuntimeError
            If a source file specified in `ref_files` does not exist.
        """

        for file in ref_files:
            src_path = ref_files[file]
            temporary_file_destination_path = os.path.join(output_path, file)
            temporary_destination_directory = os.path.dirname(
                temporary_file_destination_path
            )
            if not os.path.exists(temporary_destination_directory):
                os.makedirs(temporary_destination_directory)
            if os.path.isfile(src_path):
                shutil.copy(src_path, temporary_file_destination_path)
            else:
                logger.error(f"Unable to find file with name = {file}")
                raise RuntimeError(f"Unable to find file with name = {file}")

    @staticmethod
    def _upload_file_to_s3_with_presigned_url(file_path, presigned_url) -> bool:
        """Upload models as a zip file to FRED Cloud API using signed url."""

        try:
            # Open the file to upload
            with open(file_path, "rb") as file_data:
                # Upload the file to S3 using the presigned URL
                response = requests.put(presigned_url, data=file_data)
                # Check if the upload was successful
                if response.status_code == 200:
                    print("File uploaded successfully!")
                    logger.info("File uploaded successfully!")
                    return True
                else:
                    print("Failed to upload file.")
                    logger.error("Failed to upload file.")
                    return False

        except Exception as e:
            print("\n Exception=", e)
            logger.error("\n Exception=", e)
            return False

    @staticmethod
    def _get_signed_upload_url(key: str) -> str:
        """Request to FRED Cloud API to get signed url for uploading models.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/jobs"
        response = requests.post(
            endpoint_url, headers=platform_api_headers(), json={"job_name": key}
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                logger.error(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                logger.error(
                    f"FRED Cloud error code: {response.status_code} : {response.text}"
                )
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        logger.debug(f"Payload: {response.text}")
        response_body = _GetSignedUploadUrl.model_validate_json(response_payload)
        return response_body.url

    @staticmethod
    def _cache_dir(key: str) -> Path:
        return get_cache_dir() / "jobs" / key

    @staticmethod
    def _results_cache_dir(key: int) -> Path:
        return Path.home() / ".epx/results_cache" / str(key)

    @staticmethod
    def _check_results_cache_exist(path: str) -> bool:
        try:
            if not os.listdir(path):
                return False
            return True
        except Exception:
            return False

    @staticmethod
    def _get_signed_download_url(key: int) -> _GetSignedDownloadUrlResponse:
        """Request to FRED Cloud API to get signed url for downloading job results.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/jobs/results"

        response = requests.get(
            endpoint_url,
            headers=platform_api_headers(),
            params={"job_id": key},
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")

        response_payload = response.text
        logger.debug(f"Payload: {response.text}")
        response_body = _GetSignedDownloadUrlResponse.model_validate_json(
            response_payload
        )
        return response_body

    @classmethod
    def get_job_id_by_key(cls, key: str) -> Optional[int]:
        """Gets jobId by job key.

        Raises
        ------
        UnauthorizedUserError
            If the user does not have sufficient privileges to perform the
            specified action on FRED Cloud.
        RuntimeError
            If a FRED Cloud server error occurs.
        """

        endpoint_url = f"{read_auth_config('api-url')}/jobs"
        response = requests.get(
            endpoint_url,
            headers=platform_api_headers(),
            params={"job_name": key},
        )

        # Check HTTP response status code and raise exceptions as appropriate
        if not response.ok:
            if response.status_code == requests.codes.forbidden:
                raise UnauthorizedUserError(
                    ForbiddenResponse.model_validate_json(response.text).description
                )
            elif response.status_code == requests.codes.not_found:
                raise NotFoundError(
                    NotFoundResponse.model_validate_json(response.text).description
                )
            else:
                raise RuntimeError(f"FRED Cloud error code: {response.status_code}")
        response_payload = response.text

        response_body = _JobDetails.model_validate_json(response_payload)
        return response_body.id

    @classmethod
    def from_key(cls, job_key: str) -> "FREDJob":
        """Retrieve a Job object from a job key.

        Useful if one knows the key for a job but e.g. hadn't
        assigned the return value of `run_job` to a variable.

        Parameters
        ----------
        job_key : str
            The key of the job to retrieve.

        Raises
        ------
        JobKeyDoesNotExist
            If no job associated with the given job key exists yet.
        """

        try:
            job_config_file = cls._cache_dir(job_key) / "job.json"
            with open(job_config_file, "r") as f:
                return _JobModel.model_validate_json(f.read()).as_job()
        except FileNotFoundError as e:
            logger.error(e)
            raise JobDoesNotExistError(job_key)
        except ValueError as e:
            logger.error(e)
            raise

    @classmethod
    def list_keys(cls) -> List[str]:
        try:
            cache_dir = get_cache_dir() / "jobs"
            return [
                name
                for name in os.listdir(cache_dir)
                if os.path.isdir(os.path.join(cache_dir, name))
            ]
        except ValueError as e:
            logger.error(e)
            raise

    @classmethod
    def _build_runs(
        cls,
        program: Path,
        config: Iterable[FREDModelConfig],
        results_dir: Path,
        key: str,
        size: str,
        fred_version: str,
    ) -> tuple[FREDRun, ...]:
        def disaggregate_model_config(
            model_config: FREDModelConfig,
        ) -> list[FREDModelConfig]:
            """Convert model config representing multiple realizations into a
            list of model configs each representing a single realization.
            """
            if model_config.n_reps == 1:
                return [model_config]
            if isinstance(model_config.seed, Iterable):
                seeds: list[Optional[int]] = list(model_config.seed)
            else:
                seeds = [None for _ in range(model_config.n_reps)]
            return [
                FREDModelConfig(
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=seeds[i],
                    n_reps=1,
                )
                for i, _ in enumerate(range(model_config.n_reps))
            ]

        def validate_singular_seed(
            seed: Optional[Union[int, Iterable[int]]],
        ) -> Optional[int]:
            if seed is not None and not isinstance(seed, int):
                raise ValueError("Seed must be an integer if n_reps=1")
            return seed

        job_dir = cls._get_job_output_dir(results_dir, key)
        job_dir.mkdir(parents=True, exist_ok=True)
        return tuple(
            FREDRun(
                params=RunParameters(
                    program=program,
                    synth_pop=model_config.synth_pop,
                    start_date=model_config.start_date,
                    end_date=model_config.end_date,
                    model_params=model_config.model_params,
                    seed=validate_singular_seed(model_config.seed),
                ),
                output_dir=job_dir / str(run_id),
                size=size,
                fred_version=fred_version,
                job_name=key,
            )
            for run_id, model_config in enumerate(
                chain(
                    *[
                        disaggregate_model_config(model_config)
                        for model_config in config
                    ]
                )
            )
        )

    def __repr__(self) -> str:
        return (
            f"FREDJob("
            f"program={self.program}, "
            f"config={self.config}, "
            f"key={self.key}, "
            f"size={self.size}, "
            f"fred_version={self.fred_version}, "
            f"{f'visualize={self.visualize}, ' if self.visualize is not None else ''}"
            f"results_dir={self.results_dir}"
            f")"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FREDJob):
            return False
        return (
            self.program == other.program
            and self.config == other.config
            and self.key == other.key
            and self.size == other.size
            and self.fred_version == other.fred_version
            and self.results_dir == other.results_dir
        )
