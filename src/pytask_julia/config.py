"""Configure pytask."""
from __future__ import annotations

from typing import Any

from pytask import hookimpl
from pytask_julia.serialization import SERIALIZERS
from pytask_julia.shared import parse_relative_path


@hookimpl
def pytask_parse_config(config: dict[str, Any]) -> None:
    """Register the julia marker."""
    config["markers"]["julia"] = "Tasks which are executed with Julia."
    config["julia_serializer"] = config.get("julia_serializer", "json")
    if config["julia_serializer"] not in SERIALIZERS:
        raise ValueError(
            f"'julia_serializer' is {config['julia_serializer']} and not one of "
            f"{list(SERIALIZERS)}.",
        )
    config["julia_suffix"] = config.get("julia_suffix", "")
    config["julia_options"] = _parse_value_or_whitespace_option(
        config.get("julia_options"),
    )
    project = config.get("julia_project")
    if project is None:
        config["julia_project"] = project
    else:
        config["julia_project"] = parse_relative_path(project, config["root"])


def _parse_value_or_whitespace_option(value: Any) -> None | list[str]:
    """Parse option which can hold a single value or values separated by new lines."""
    if value is None:
        return None
    if isinstance(value, list):
        return list(map(str, value))
    raise ValueError(f"'julia_options' is {value} and not a list.")
