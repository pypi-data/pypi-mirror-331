from pathlib import Path


class JobExistsError(Exception):
    """Raised when a job with a requested key already exists in the results."""

    def __init__(self, results_dir: Path, key: str):
        self.results_dir = results_dir
        self.key = key
        super().__init__(
            f"A job with key '{key}' already exists in results directory "
            f"'{results_dir}'"
        )


class JobDoesNotExistError(Exception):
    """Raised when a job with a requested key does not exist in the cache."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"No job with key '{key}' exists")


class RunExistsError(Exception):
    """Thrown when user specifies an output_dir that already contains data."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        super().__init__(
            f"Run data already exists in output_dir: {self.output_dir}. "
            "Call Run.delete to delete this data and reuse output_dir."
        )
