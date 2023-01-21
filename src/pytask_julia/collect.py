"""Collect tasks."""
from __future__ import annotations

import functools
import subprocess
import types
from pathlib import Path
from typing import Any
from typing import Callable

from pytask import depends_on
from pytask import has_mark
from pytask import hookimpl
from pytask import Mark
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Session
from pytask import Task
from pytask_julia.serialization import SERIALIZERS
from pytask_julia.shared import julia
from pytask_julia.shared import JULIA_SCRIPT_KEY
from pytask_julia.shared import parse_relative_path


_SEPARATOR: str = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def run_jl_script(
    script: Path,
    options: list[str],
    serialized: Path,
    project: list[str],
) -> None:
    """Run a Julia script."""
    cmd = ["julia"] + options + project + [_SEPARATOR, str(script), str(serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T201
    subprocess.run(cmd, check=True)


@hookimpl
def pytask_collect_task(
    session: Session,
    path: Path,
    name: str,
    obj: Any,
) -> Task | None:
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread

    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType`
    does notdetect built-ins which is not possible anyway.

    """
    __tracebackhide__ = True

    if (
        (name.startswith("task_") or has_mark(obj, "task"))
        and callable(obj)
        and has_mark(obj, "julia")
    ):
        obj, marks = remove_marks(obj, "julia")

        if len(marks) > 1:
            raise ValueError(
                f"Task {name!r} has multiple @pytask.mark.julia marks, but only one is "
                "allowed.",
            )

        julia_mark = _parse_julia_mark(
            mark=marks[0],
            default_options=session.config["julia_options"],
            default_serializer=session.config["julia_serializer"],
            default_suffix=session.config["julia_suffix"],
            default_project=session.config["julia_project"],
        )
        script, options, _, _, project = julia(**julia_mark.kwargs)

        obj.pytask_meta.markers.append(julia_mark)

        dependencies = parse_nodes(session, path, name, obj, depends_on)
        products = parse_nodes(session, path, name, obj, produces)

        markers = obj.pytask_meta.markers if hasattr(obj, "pytask_meta") else []
        kwargs = obj.pytask_meta.kwargs if hasattr(obj, "pytask_meta") else {}

        task = Task(
            base_name=name,
            path=path,
            function=_copy_func(run_jl_script),  # type: ignore[arg-type]
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        script_node = session.hook.pytask_collect_node(
            session=session,
            path=path,
            node=script,
        )

        if isinstance(task.depends_on, dict):
            task.depends_on[JULIA_SCRIPT_KEY] = script_node
            task.attributes["julia_keep_dict"] = True
        else:
            task.depends_on = {0: task.depends_on, JULIA_SCRIPT_KEY: script_node}
            task.attributes["julia_keep_dict"] = False

        parsed_project = _parse_project(project, task.path.parent)

        task.function = functools.partial(
            task.function,
            script=task.depends_on[JULIA_SCRIPT_KEY].path,
            options=options,
            project=parsed_project,
        )

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


def _copy_func(func: types.FunctionType) -> types.FunctionType:
    """Create a copy of a function.

    Based on https://stackoverflow.com/a/13503277/7523785.

    Example
    -------
    >>> def _func(): pass
    >>> copied_func = _copy_func(_func)
    >>> _func is copied_func
    False

    """
    new_func = types.FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    new_func = functools.update_wrapper(new_func, func)
    new_func.__kwdefaults__ = func.__kwdefaults__
    return new_func


def _parse_project(project: str | Path | None, root: Path) -> list[str]:
    if project is None:
        return []
    project = parse_relative_path(project, root)
    return ["--project=" + project.as_posix()]
