"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the r marker."""
    config["markers"]["xxxxx"] = "Tasks which are executed with ZZZZZ."
    config["xxxxx_source_key"] = config_from_file.get("xxxxx_source_key", "source")
