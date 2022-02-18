"""This module contains the code to serialize keyword arguments to the task."""
import json
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import Union

from _pytask.nodes import MetaTask


_HIDDEN_FOLDER = ".pytask"


SERIALIZER = {
    "json": {"serializer": json.dumps, "suffix": ".json"},
}

try:
    import yaml
except ImportError:
    pass
else:
    SERIALIZER["yaml"] = {"serializer": yaml.dump, "suffix": ".yaml"}
    SERIALIZER["yml"] = {"serializer": yaml.dump, "suffix": ".yml"}


def create_path_to_serialized(task: MetaTask, suffix: str) -> Path:
    """Create path to serialized."""
    parent = task.path.parent
    file_name = create_file_name(task)
    path = parent.joinpath(_HIDDEN_FOLDER, file_name).with_suffix(suffix)
    return path


def create_file_name(task: MetaTask, suffix: str) -> str:
    """Create the file name of the file containing the serialized kwargs.

    Some characters need to be escaped since they are not valid characters on file
    systems.

    """
    return (
        task.short_name.replace("[", "_")
        .replace("]", "_")
        .replace("::", "_")
        .replace(".", "_")
        .replace("/", "_")
        + suffix
    )


def serialize_keyword_arguments(
    serializer: Union[str, Callable[Dict[str, Any], str]],
    path_to_serialized: Path,
    kwargs: Dict[str, Any],
) -> None:
    if callable(serializer):
        serializer_func = serializer
    elif isinstance(serializer, str) and serializer in SERIALIZER:
        serializer_func = SERIALIZER[serializer]
    else:
        raise ValueError(f"Serializer {serializer!r} is not known.")

    serialized = serializer_func(kwargs)
    path_to_serialized.write_text(serialized)
