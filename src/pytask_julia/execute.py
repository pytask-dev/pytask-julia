"""Execute tasks."""
from __future__ import annotations

import shutil
from typing import Any

from pytask import get_marks
from pytask import hookimpl
from pytask import PPathNode
from pytask import PTask
from pytask import PythonNode
from pytask.tree_util import tree_map
from pytask_julia.serialization import serialize_keyword_arguments
from pytask_julia.shared import julia


@hookimpl
def pytask_execute_task_setup(task: PTask) -> None:
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

        assert serializer
        assert suffix is not None

        serialized_node: PythonNode = task.depends_on["_serialized"]  # type: ignore[assignment]
        serialized_node.value.parent.mkdir(parents=True, exist_ok=True)
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, serialized_node.value, kwargs)


def collect_keyword_arguments(task: PTask) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    kwargs: dict[str, Any] = {
        **tree_map(  # type: ignore[dict-item]
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.depends_on,
        ),
        **tree_map(  # type: ignore[dict-item]
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.produces,
        ),
    }
    kwargs.pop("_script")
    kwargs.pop("_options")
    kwargs.pop("_project")
    kwargs.pop("_serialized")
    return kwargs
