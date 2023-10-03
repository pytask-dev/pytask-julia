"""Execute tasks."""
from __future__ import annotations

import functools
import shutil
from typing import Any

from pybaum.tree_util import tree_map
from pytask import get_marks
from pytask import hookimpl
from pytask import PPathNode
from pytask import Task
from pytask_julia.serialization import create_path_to_serialized
from pytask_julia.serialization import serialize_keyword_arguments
from pytask_julia.shared import julia
from pytask_julia.shared import JULIA_SCRIPT_KEY


@hookimpl
def pytask_execute_task_setup(task: Task) -> None:
    """Check whether environment allows executing Julia files."""
    marks = get_marks(task, "julia")
    if marks:
        if shutil.which("julia") is None:
            raise RuntimeError(
                "julia is needed to run Julia scripts, but it is not found on your "
                "PATH.",
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
    kwargs = {
        "depends_on": tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.depends_on,
        ),
        "produces": tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.produces,
        ),
    }
    kwargs["depends_on"].pop(JULIA_SCRIPT_KEY)
    return kwargs
