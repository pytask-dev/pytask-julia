"""Collect tasks."""
from __future__ import annotations

import functools
import inspect
import itertools
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
from pytask_julia.shared import parse_project


_SEPARATOR: str = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def run_jl_script(
    script: Path, options: list[str], serialized: Path, project: list[str]
) -> None:
    """Run a Julia script."""
    cmd = ["julia"] + options + project + [_SEPARATOR, str(script), str(serialized)]
    print("Executing " + " ".join(cmd) + ".")  # noqa: T001
    subprocess.run(cmd, check=True)


_ERROR_MSG_MISSING_SCRIPT = (
    "The function {name!r} in the module {path} is marked as a task to be executed "
    "with Julia, but the script which should be executed is missing. Pass it to the "
    "decorator using the 'script' keyword."
    "\n\n    @pytask.mark.julia(script='script.jl')\n    def task_julia():\n        "
    "pass"
)


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
        obj, markers = remove_marks(obj, "julia")
        julia_mark = _merge_all_markers(
            markers=markers,
            default_options=session.config["julia_options"],
            default_serializer=session.config["julia_serializer"],
            default_suffix=session.config["julia_suffix"],
            default_project=session.config["julia_project"],
        )
        script, options, _, _, project = julia(**julia_mark.kwargs)

        if script is None:
            raise ValueError(_ERROR_MSG_MISSING_SCRIPT.format(name=name, path=path))

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

        parsed_project = parse_project(project, session.config["root"])

        task.function = functools.partial(
            task.function,
            script=task.depends_on["__script"].path,
            options=options,
            project=parsed_project,
        )

        return task


def _merge_all_markers(
    markers, default_options, default_serializer, default_suffix, default_project
):
    """Combine all information from markers for the compile_julia function."""
    values = []
    names_of_kwargs = list(inspect.signature(julia).parameters)
    for marker in markers:
        parsed_args = dict(zip(names_of_kwargs, julia(**marker.kwargs)))
        values.append(parsed_args)

    kwargs = {
        "script": next((v["script"] for v in values if v["script"] is not None), None),
        "options": default_options
        + list(
            itertools.chain.from_iterable(
                v["options"] for v in values if v["options"] is not None
            )
        ),
        "serializer": next(
            (v["serializer"] for v in values if v["serializer"] is not None),
            default_serializer,
        ),
        "project": next(
            (v["project"] for v in values if v["project"] is not None),
            default_project,
        ),
    }

    if isinstance(kwargs["serializer"], str) and kwargs["serializer"] in SERIALIZER:
        proposed_suffix = SERIALIZER[kwargs["serializer"]]["suffix"]
    else:
        proposed_suffix = default_suffix
    kwargs["suffix"] = next(
        (v["suffix"] for v in values if v["suffix"] is not None), proposed_suffix
    )
    mark = Mark("julia", (), kwargs)
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
