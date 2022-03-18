"""Collect tasks."""
from __future__ import annotations

import functools
import subprocess
import types
from pathlib import Path

from pytask import depends_on
from pytask import has_mark
from pytask import hookimpl
from pytask import Mark
from pytask import parse_nodes
from pytask import produces
from pytask import remove_marks
from pytask import Task
from pytask_julia.serialization import SERIALIZER
from pytask_julia.shared import julia
from pytask_julia.shared import parse_relative_path


_SEPARATOR: str = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def run_jl_script(
    script: Path, options: list[str], serialized: Path, project: list[str]
) -> None:
    """Run a Julia script."""
    cmd = ["julia"] + options + project + [_SEPARATOR, str(script), str(serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T001
    subprocess.run(cmd, check=True)


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

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
                "allowed."
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
            function=_copy_func(run_jl_script),
            depends_on=dependencies,
            produces=products,
            markers=markers,
            kwargs=kwargs,
        )

        script_node = session.hook.pytask_collect_node(
            session=session, path=path, node=script
        )

        if isinstance(task.depends_on, dict):
            task.depends_on["__script"] = script_node
            task.attributes["julia_keep_dict"] = True
        else:
            task.depends_on = {0: task.depends_on, "__script": script_node}
            task.attributes["julia_keep_dict"] = False

        parsed_project = _parse_project(project, task.path.parent)

        task.function = functools.partial(
            task.function,
            script=task.depends_on["__script"].path,
            options=options,
            project=parsed_project,
        )

        return task


def _parse_julia_mark(
    mark, default_options, default_serializer, default_suffix, default_project
):
    """Parse a Julia mark."""
    script, options, serializer, suffix, project = julia(**mark.kwargs)

    parsed_kwargs = {}
    for arg_name, value, default in [
        ("script", script, None),
        ("options", options, default_options),
        ("serializer", serializer, default_serializer),
    ]:
        parsed_kwargs[arg_name] = value if value else default

    if (
        isinstance(parsed_kwargs["serializer"], str)
        and parsed_kwargs["serializer"] in SERIALIZER
    ):
        proposed_suffix = SERIALIZER[parsed_kwargs["serializer"]]["suffix"]
    else:
        proposed_suffix = default_suffix
    parsed_kwargs["suffix"] = suffix if suffix else proposed_suffix

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
