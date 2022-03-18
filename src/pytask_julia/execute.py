"""Execute tasks."""
from __future__ import annotations

import functools
import shutil
from typing import Any

from pybaum.tree_util import tree_map
from pytask import get_marks
from pytask import hookimpl
from pytask import Task
from pytask_julia.serialization import create_path_to_serialized
from pytask_julia.serialization import serialize_keyword_arguments
from pytask_julia.shared import julia


@hookimpl
def pytask_execute_task_setup(task):
    """Check whether environment allows executing Julia files."""
    marks = get_marks(task, "julia")
    if marks:
        if shutil.which("julia") is None:
            raise RuntimeError(
                "julia is needed to run Julia scripts, but it is not found on your "
                "PATH."
            )

        assert len(marks) == 1

        _, _, serializer, suffix, _ = julia(**marks[0].kwargs)

        path_to_serialized = create_path_to_serialized(task, suffix)
        path_to_serialized.parent.mkdir(parents=True, exist_ok=True)
        task.function = functools.partial(
            task.function,
            serialized=path_to_serialized,
        )
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, path_to_serialized, kwargs)


def collect_keyword_arguments(task: Task) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    # Remove all kwargs from the task so that they are not passed to the function.
    kwargs = dict(task.kwargs)
    task.kwargs = {}

    if len(task.depends_on) == 1 and "__script" in task.depends_on:
        pass
    elif not task.attributes["julia_keep_dict"] and len(task.depends_on) == 2:
        kwargs["depends_on"] = str(task.depends_on[0].value)
    else:
        kwargs["depends_on"] = tree_map(lambda x: str(x.value), task.depends_on)
        kwargs["depends_on"].pop("__script")

    if task.produces:
        kwargs["produces"] = tree_map(lambda x: str(x.value), task.produces)

    return kwargs
