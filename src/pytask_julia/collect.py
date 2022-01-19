"""Collect tasks."""
import copy
import functools
import subprocess
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Union

from _pytask.config import hookimpl
from _pytask.mark_utils import get_specific_markers_from_task
from _pytask.mark_utils import has_marker
from _pytask.nodes import FilePathNode
from _pytask.nodes import PythonFunctionTask
from _pytask.parametrize import _copy_func


_SEPARATOR = "--"
"""str: Separates options for the Julia executable and arguments to the file."""


def julia(options: Optional[Union[str, Iterable[str]]] = None):
    """Specify command line options for Julia.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to Julia.

    """
    options = [_SEPARATOR] if options is None else _to_list(options)
    options = [str(i) for i in options]

    return options


def run_jl_script(julia):
    """Run a Julia script."""
    print("Executing " + " ".join(julia) + ".")  # noqa: T001
    subprocess.run(julia, check=True)


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

    """
    if name.startswith("task_") and callable(obj) and has_marker(obj, "julia"):
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, obj, session
        )

        return task


@hookimpl
def pytask_collect_task_teardown(session, task):
    """Perform some checks."""
    if get_specific_markers_from_task(task, "julia"):
        source = _get_node_from_dictionary(task.depends_on, "source")
        if isinstance(source, FilePathNode) and source.value.suffix not in [".jl"]:
            raise ValueError(
                "The first dependency of a Julia task must be the script to be "
                "executed."
            )

        julia_function = _copy_func(run_jl_script)
        julia_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_marks = _merge_all_markers(task)
        args = julia(*merged_marks.args, **merged_marks.kwargs)
        options = _prepare_cmd_options(session, task, args)
        julia_function = functools.partial(julia_function, julia=options)

        task.function = julia_function


def _get_node_from_dictionary(obj, key, fallback=0):
    """Get node from dictionary."""
    if isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _merge_all_markers(task):
    """Combine all information from markers for the compile_julia function."""
    julia_marks = get_specific_markers_from_task(task, "julia")
    mark = julia_marks[0]
    for mark_ in julia_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark


_ERROR_MSG_MISSING_SEPARATOR = f"""The inputs of the @pytask.mark.julia decorator do not
contain the separator to differentiate between options for the julia executable and
arguments to the script. This was passed to the decorator:

{{}}

Construct the inputs to the decorator should contain, first, options to the executable,
secondly, the separator - "{_SEPARATOR}" -, thirdly, arguments to the script.

Here is an example:

@pytask.mark.julia(("--threads", "1", "{_SEPARATOR}", "input.file"))

Even if you do not need the left or the right side of the decorator, you must put the
separator at the correct position.
"""


def _prepare_cmd_options(session, task, args):
    """Prepare the command line arguments to execute the do-file.

    The last entry changes the name of the log file. We take the task id as a name which
    is unique and does not cause any errors when parallelizing the execution.

    """
    source = _get_node_from_dictionary(
        task.depends_on, session.config["julia_source_key"]
    )

    if _SEPARATOR not in args:
        raise ValueError(_ERROR_MSG_MISSING_SEPARATOR.format(args))
    else:
        idx_sep = args.index(_SEPARATOR)
        executable_options = args[:idx_sep]
        script_arguments = args[idx_sep + 1 :]

    return [
        "julia",
        *executable_options,
        _SEPARATOR,
        source.path.as_posix(),
        *script_arguments,
    ]


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
