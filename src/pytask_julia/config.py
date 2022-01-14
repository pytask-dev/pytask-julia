"""Configure pytask."""
from _pytask.config import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the julia marker."""
    config["markers"]["julia"] = "Tasks which are executed with Julia."
    config["julia_source_key"] = config_from_file.get("julia_source_key", "source")
