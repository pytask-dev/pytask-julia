"""Execute tasks."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING
from typing import Any

from pytask import PPathNode
from pytask import PTask
from pytask import get_marks
from pytask import hookimpl
from pytask.tree_util import tree_map

from pytask_julia.serialization import serialize_keyword_arguments
from pytask_julia.shared import julia

if TYPE_CHECKING:
    from pathlib import Path


@hookimpl
def pytask_execute_task_setup(task: PTask) -> None:
    """Check whether environment allows executing Julia files."""
    marks = get_marks(task, "julia")
    if marks:
        if shutil.which("julia") is None:
            msg = (
                "julia is needed to run Julia scripts, but it is not found on your "
                "PATH."
            )
            raise RuntimeError(
                msg,
            )

        _, _, serializer, _, _ = julia(**marks[0].kwargs)

        serialized_node = task.depends_on["_serialized"]
        path: Path = serialized_node.value  # type: ignore[assignment]
        path.parent.mkdir(parents=True, exist_ok=True)
        kwargs = collect_keyword_arguments(task)
        serialize_keyword_arguments(serializer, path, kwargs)


def collect_keyword_arguments(task: PTask) -> dict[str, Any]:
    """Collect keyword arguments for function."""
    kwargs: dict[str, Any] = {
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.depends_on,  # type: ignore[arg-type]
        ),
        **tree_map(
            lambda x: str(x.path) if isinstance(x, PPathNode) else str(x.value),
            task.produces,  # type: ignore[arg-type]
        ),
    }
    kwargs.pop("_script")
    kwargs.pop("_options")
    kwargs.pop("_project")
    kwargs.pop("_serialized")
    return kwargs
