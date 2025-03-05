"""Global configuration for the EPX client."""

import os
import json
from pathlib import Path


def get_cache_dir() -> Path:
    """Return the path to the cache directory for the EPX client.

    This is used to store metadata about runs and jobs initiated through the
    client. If the environment variable ``EPX_CACHE_DIR`` is set, this is used.
    Otherwise, the default location is ``~/.epx_client``.
    """

    try:
        return Path(os.environ["EPX_CACHE_DIR"])
    except KeyError:
        return Path.home().resolve() / ".epx_client"


def default_results_dir() -> Path:
    return Path.home() / "results"


def get_auth_config_dir() -> Path:
    return Path.home() / ".epx" / "config.json"


def read_auth_config(key: str) -> str:
    config_file = get_auth_config_dir()
    if not config_file.exists():
        raise FileNotFoundError(f"Config auth file not found at {config_file}")

    # Read content file config
    with config_file.open("r") as f:
        config = json.load(f)

    if key not in config:
        raise ValueError(
            f"Key '{key}' not found in config file. Please add in file config.json"
        )

    value = config[key]
    if not value:
        raise ValueError(
            f"Key '{key}' has no value or is empty in config file. Please add in file "
            "config.json"
        )

    return value


def check_positive_integer(value, attribute_name):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(
            f"'{attribute_name}' must be a positive integer, but got {value}."
        )
    return value


def get_max_retry_value(attribute_name: str, default_value=1) -> int:
    """
    Retrieves the maximum retry value for a given attribute from the configuration.

    Arguments:
    attribute_name: str
        The name of the attribute to fetch from the configuration.
    default_value: int:
        The fallback value to use if the attribute is not found or an exception occurs.
        Default is 1.

    Returns:
        int: The maximum retry value
    Raises:
        ValueError: If the retrieved value is in valid.
    """

    try:
        max_retries = read_auth_config(attribute_name)
    except Exception:
        return default_value

    return check_positive_integer(max_retries, attribute_name)
