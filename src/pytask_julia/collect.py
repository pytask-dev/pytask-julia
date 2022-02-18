"""Collect tasks."""
import copy
import functools
import itertools
import subprocess
import types
from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark import Mark
from _pytask.mark_utils import has_marker
from _pytask.mark_utils import remove_markers_from_func
from _pytask.nodes import PythonFunctionTask


_SEPARATOR: str = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def julia(
    *,
    script: Union[str, Path] = None,
    options: Optional[Union[str, Iterable[str]]] = None,
    serializer: Optional[Union[str, Callable[..., Union[str, bytes]], str]] = None,
    suffix: Optional[str] = None,
) -> Tuple[
    Union[str, Path, None],
    Optional[Union[str, Iterable[str]]],
    Optional[Union[str, Callable[..., Union[str, bytes]], str]],
    Optional[str],
]:
    """Specify command line options for Julia.

    Parameters
    ----------
    script : Union[str, Path]
        The path to the Julia script which is executed.
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to the interpreter for Julia.
    serializer: Optional[Callable[Any, Union[str, bytes]]]
        A function to serialize data for the task which accepts a dictionary with all
        the information. If the value is `None`, use either the value specified in the
        configuration file under ``julia_serializer`` or fall back to ``"json"``.
    suffix: Optional[str]
        A suffix for the serialized file. If the value is `None`, use either the value
        specified in the configuration file under ``julia_suffix`` or fall back to
        ``".json"``.

    """
    options = [] if options is None else list(map(str, _to_list(options)))
    return script, options, serializer, suffix


def run_jl_script(script: Path, options: list[str], serialized: Path) -> None:
    """Run a Julia script."""
    args = ["julia"] + options + [_SEPARATOR, str(script), str(serialized)]
    print("Executing " + " ".join(args) + ".")  # noqa: T001
    subprocess.run(args, check=True)


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

    if name.startswith("task_") and callable(obj) and has_marker(obj, "julia"):
        obj, markers = remove_markers_from_func(obj, "julia")
        julia_marker = _merge_all_markers(
            markers=markers,
            default_options=session.config["julia_options"],
            default_serializer=session.config["julia_serializer"],
            default_suffix=session.config["julia_suffix"],
        )
        script, options, _, _ = julia(**julia_marker.kwargs)

        if script is None:
            raise ValueError(_ERROR_MSG_MISSING_SCRIPT.format(name=name, path=path))

        julia_function = _copy_func(run_jl_script)
        julia_function.pytaskmark = copy.deepcopy(obj.pytaskmark)
        julia_function.pytaskmark.extend(
            [julia_marker, Mark("depends_on", ({"script": script},), {})]
        )
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, julia_function, session
        )
        task.function = functools.partial(
            task.function,
            script=task.depends_on["script"].path,
            options=options,
        )

        return task


def _merge_all_markers(markers, default_options, default_serializer, default_suffix):
    """Combine all information from markers for the compile_julia function."""
    values = []
    for marker in markers:
        parsed_args = dict(
            zip(["script", "options", "serializer", "suffix"], julia(**marker.kwargs))
        )
        values.append(parsed_args)

    kwargs = {
        "script": next(
            (Path(v["script"]) for v in values if v["script"] is not None), None
        ),
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
        "suffix": next(
            (v["suffix"] for v in values if v["suffix"] is not None), default_suffix
        ),
    }
    mark = Mark("julia", (), kwargs)
    return mark


def _to_list(scalar_or_iter):
    """Convert scalars and iterables to list.

    Parameters
    ----------
    scalar_or_iter : str or list

    Returns
    -------
    list

    Examples
    --------
    >>> _to_list("a")
    ['a']
    >>> _to_list(["b"])
    ['b']

    """
    return (
        [scalar_or_iter]
        if isinstance(scalar_or_iter, str) or not isinstance(scalar_or_iter, Sequence)
        else list(scalar_or_iter)
    )


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
