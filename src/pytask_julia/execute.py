"""Execute tasks."""
from __future__ import annotations

import functools
import shutil
from typing import Any

from pytask import get_marks
from pytask import hookimpl
from pytask import Task
from pytask_julia.serialization import create_path_to_serialized
from pytask_julia.serialization import serialize_keyword_arguments
from pytask_julia.shared import julia


@hookimpl
def pytask_execute_task_setup(task):
    """Check whether environment allows executing Julia files."""
    markers = get_marks(task, "julia")
    if markers:
        if shutil.which("julia") is None:
            raise RuntimeError(
                "julia is needed to run Julia scripts, but it is not found on your "
                "PATH."
            )

        if len(markers) != 1:
            raise ValueError("There should only one Julia marker.")
        marker = markers[0]

        _, _, serializer, suffix = julia(**marker.kwargs)

        path_to_serialized = create_path_to_serialized(task, suffix)
        task.function = functools.partial(
            task.function,
            serialized=path_to_serialized,
        )
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, path_to_serialized, kwargs)


def collect_keyword_arguments(task: Task) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    if isinstance(task.function, functools.partial):
        kwargs = {
            k: v
            for k, v in task.function.keywords.items()
            if k not in ("script", "options", "serialized")
        }
    else:
        kwargs = {}

    for marker_name in ("depends_on", "produces"):
        if getattr(task, marker_name):
            kwargs[marker_name] = {
                name: str(node.value)
                for name, node in getattr(task, marker_name).items()
            }
            if (
                len(kwargs[marker_name]) == 1
                and 0 in kwargs[marker_name]
                and not task.keep_dict[marker_name]
            ):
                kwargs[marker_name] = kwargs[marker_name][0]

    return kwargs
