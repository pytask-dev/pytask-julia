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


def xxxxx(options: Optional[Union[str, Iterable[str]]] = None):
    """Specify command line options for YYYYY.

    Parameters
    ----------
    options : Optional[Union[str, Iterable[str]]]
        One or multiple command line options passed to YYYYY.

    """
    options = [] if options is None else _to_list(options)
    options = [str(i) for i in options]
    return options


def run_xxxxx_script(xxxxx):
    """Run an R script."""
    print("Executing " + " ".join(xxxxx) + ".")  # noqa: T001
    subprocess.run(xxxxx, check=True)


@hookimpl
def pytask_collect_task(session, path, name, obj):
    """Collect a task which is a function.

    There is some discussion on how to detect functions in this `thread
    <https://stackoverflow.com/q/624926/7523785>`_. :class:`types.FunctionType` does not
    detect built-ins which is not possible anyway.

    """
    if name.startswith("task_") and callable(obj) and has_marker(obj, "xxxxx"):
        task = PythonFunctionTask.from_path_name_function_session(
            path, name, obj, session
        )

        return task


@hookimpl
def pytask_collect_task_teardown(session, task):
    """Perform some checks."""
    if get_specific_markers_from_task(task, "xxxxx"):
        source = _get_node_from_dictionary(task.depends_on, "source")
        if isinstance(source, FilePathNode) and source.value.suffix not in [
            ".xxxxxWHATEVERxxxxx"
        ]:
            raise ValueError(
                "The first dependency of a YYYYY task must be the script to be executed."
            )

        xxxxx_function = _copy_func(run_xxxxx_script)
        xxxxx_function.pytaskmark = copy.deepcopy(task.function.pytaskmark)

        merged_marks = _merge_all_markers(task)
        args = xxxxx(*merged_marks.args, **merged_marks.kwargs)
        options = _prepare_cmd_options(session, task, args)
        xxxxx_function = functools.partial(xxxxx_function, xxxxx=options)

        task.function = r_function


def _get_node_from_dictionary(obj, key, fallback=0):
    """Get node from dictionary."""
    if isinstance(obj, dict):
        obj = obj.get(key) or obj.get(fallback)
    return obj


def _merge_all_markers(task):
    """Combine all information from markers for the compile xxxxx function."""
    xxxxx_marks = get_specific_markers_from_task(task, "xxxxx")
    mark = xxxxx_marks[0]
    for mark_ in xxxxx_marks[1:]:
        mark = mark.combined_with(mark_)
    return mark


def _prepare_cmd_options(session, task, args):
    """Prepare the command line arguments to execute the do-file.

    The last entry changes the name of the log file. We take the task id as a name which
    is unique and does not cause any errors when parallelizing the execution.

    """
    source = _get_node_from_dictionary(
        task.depends_on, session.config["xxxxx_source_key"]
    )
    return ["ZZZZZ", source.path.as_posix(), *args]


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
