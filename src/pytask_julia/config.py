"""Configure pytask."""
from __future__ import annotations

from pytask import hookimpl


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the julia marker."""
    config["markers"]["julia"] = "Tasks which are executed with Julia."
    config["julia_serializer"] = config_from_file.get("julia_serializer", "toml")
    config["julia_suffix"] = config_from_file.get("julia_suffix", ".toml")
    options = config_from_file.get("julia_options")
    config["julia_options"] = options.split(" ") if isinstance(options, str) else []
    config["julia_project"] = config_from_file.get("julia_project")
