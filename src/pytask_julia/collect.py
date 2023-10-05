"""Collect tasks."""
from __future__ import annotations

import subprocess
import warnings
from pathlib import Path
from typing import Any
from typing import Callable

from pytask import has_mark
from pytask import hookimpl
from pytask import is_task_function
from pytask import Mark
from pytask import NodeInfo
from pytask import parse_dependencies_from_task_function
from pytask import parse_products_from_task_function
from pytask import PathNode
from pytask import PTask
from pytask import PythonNode
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask import TaskWithoutPath
from pytask_julia.serialization import create_path_to_serialized
from pytask_julia.serialization import SERIALIZERS
from pytask_julia.shared import julia
from pytask_julia.shared import parse_relative_path


_SEPARATOR: str = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def run_jl_script(
    _script: Path,
    _options: list[str],
    _serialized: Path,
    _project: list[str],
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Run a Julia script."""
    cmd = ["julia", *_options, *_project, _SEPARATOR, str(_script), str(_serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T201
    subprocess.run(cmd, check=True)  # noqa: S603


@hookimpl
def pytask_collect_task(
    session: Session,
    path: Path | None,
    name: str,
    obj: Any,
) -> PTask | None:
    """Collect a task which is a function."""
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and is_task_function(obj)
        and has_mark(obj, "julia")
    ):
        # Parse the @pytask.mark.julia decorator.
        obj, marks = remove_marks(obj, "julia")
        if len(marks) > 1:
            raise ValueError(
                f"Task {name!r} has multiple @pytask.mark.julia marks, but only one is "
                "allowed.",
            )

        mark = _parse_julia_mark(
            mark=marks[0],
            default_options=session.config["julia_options"],
            default_serializer=session.config["julia_serializer"],
            default_suffix=session.config["julia_suffix"],
            default_project=session.config["julia_project"],
        )
        script, options, _, suffix, project = julia(**mark.kwargs)

        obj.pytask_meta.markers.append(mark)

        # Collect the nodes in @pytask.mark.julia and validate them.
        path_nodes = Path.cwd() if path is None else path.parent

        if isinstance(script, str):
            warnings.warn(
                "Passing a string to the @pytask.mark.julia parameter 'script' is "
                "deprecated. Please, use a pathlib.Path instead.",
                stacklevel=1,
            )
            script = Path(script)

        script_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="script", path=(), value=script, task_path=path, task_name=name
            ),
        )

        if not (isinstance(script_node, PathNode) and script_node.path.suffix == ".jl"):
            raise ValueError(
                "The 'script' keyword of the @pytask.mark.julia decorator must point "
                f"to Julia file with the .jl suffix, but it is {script_node}."
            )

        options_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_options",
                path=(),
                value=options,
                task_path=path,
                task_name=name,
            ),
        )

        parsed_project = _parse_project(project, path_nodes)
        project_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_project",
                path=(),
                value=parsed_project,
                task_path=path,
                task_name=name,
            ),
        )

        dependencies = parse_dependencies_from_task_function(
            session, path, name, path_nodes, obj
        )
        products = parse_products_from_task_function(
            session, path, name, path_nodes, obj
        )

        # Add script
        dependencies["_script"] = script_node
        dependencies["_options"] = options_node
        dependencies["_project"] = project_node

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []

        task: PTask
        if path is None:
            task = TaskWithoutPath(
                name=name,
                function=run_jl_script,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )
        else:
            task = Task(
                base_name=name,
                path=path,
                function=run_jl_script,
                depends_on=dependencies,
                produces=products,
                markers=markers,
            )

        # Add serialized node that depends on the task id.
        serialized = create_path_to_serialized(task, suffix)  # type: ignore[arg-type]
        serialized_node = session.hook.pytask_collect_node(
            session=session,
            path=path_nodes,
            node_info=NodeInfo(
                arg_name="_serialized",
                path=(),
                value=PythonNode(value=serialized),
                task_path=path,
                task_name=name,
            ),
        )
        task.depends_on["_serialized"] = serialized_node

        return task
    return None


def _parse_julia_mark(
    mark: Mark,
    default_options: list[str] | None,
    default_serializer: Callable[..., str] | str | None,
    default_suffix: str | None,
    default_project: str | None,
) -> Mark:
    """Parse a Julia mark."""
    script, options, serializer, suffix, project = julia(**mark.kwargs)

    parsed_kwargs = {}
    for arg_name, value, default in (
        ("script", script, None),
        ("options", options, default_options),
        ("serializer", serializer, default_serializer),
    ):
        parsed_kwargs[arg_name] = value or default

    proposed_suffix = (
        SERIALIZERS[parsed_kwargs["serializer"]]["suffix"]
        if isinstance(parsed_kwargs["serializer"], str)
        and parsed_kwargs["serializer"] in SERIALIZERS
        else default_suffix
    )
    parsed_kwargs["suffix"] = suffix or proposed_suffix  # type: ignore[assignment]

    if isinstance(project, (str, Path)):
        parsed_kwargs["project"] = project
    else:
        parsed_kwargs["project"] = default_project

    mark = Mark("julia", (), parsed_kwargs)
    return mark


def _parse_project(project: str | Path | None, root: Path) -> list[str]:
    if project is None:
        return []
    project = parse_relative_path(project, root)
    return ["--project=" + project.as_posix()]
