"""Configure pytask."""
from __future__ import annotations

from pytask import hookimpl
from pytask_julia.shared import parse_relative_path


@hookimpl
def pytask_parse_config(config, config_from_file):
    """Register the julia marker."""
    config["markers"]["julia"] = "Tasks which are executed with Julia."
    config["julia_serializer"] = config_from_file.get("julia_serializer", "json")
    config["julia_suffix"] = config_from_file.get("julia_suffix", "")
    config["julia_options"] = _parse_value_or_whitespace_option(
        config_from_file.get("julia_options")
    )
    project = config_from_file.get("julia_project")
    if project is None:
        config["julia_project"] = project
    else:
        config["julia_project"] = parse_relative_path(project, config["root"])


def _parse_value_or_whitespace_option(value: str | None) -> None | str | list[str]:
    """Parse option which can hold a single value or values separated by new lines."""
    if value in ["none", "None", None, ""]:
        return None
    elif isinstance(value, list):
        return list(map(str, value))
    elif isinstance(value, str):
        return [v.strip() for v in value.split(" ") if v.strip()]
    else:
        raise ValueError(f"Input {value!r} is neither a 'str' nor 'None'.")
