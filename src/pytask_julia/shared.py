from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Sequence


_ERROR_MSG = """The old syntax for @pytask.mark.julia was suddenly deprecated starting \
with pytask-julia v0.2 to provide a better user experience. Thank you for your \
understanding!

It is recommended to upgrade to the new syntax, so you enjoy all the benefits of v0.2 of
pytask and pytask-julia which are

- Access to 'depends_on' and 'produces', and other kwargs inside the Julia script.
- Support for Julia environments for running scripts with certain packages.

You can find a manual here: \
https://github.com/pytask-dev/pytask-julia/blob/v0.2.0/README.md

Upgrading can be as easy as rewriting your current task from

    @pytask.mark.julia(["--threads", 2, "--", "path_to_dependency.txt"])
    @pytask.mark.depends_on("script.jl")
    @pytask.mark.produces("out.csv")
    def task_julia():
        ...

to

    @pytask.mark.julia(script="script.jl", options=("--threads", 2))
    @pytask.mark.depends_on("path_to_dependency.txt")
    @pytask.mark.produces("out.csv")
    def task_julia():
        ...

You can also fix the version of pytask and pytask-julia to <0.2, so you do not have to \
to upgrade. At the same time, you will not enjoy the improvements released with \
version v0.2 of pytask and pytask-julia.

"""


def julia(
    *args,
    script: str | Path | None = None,
    options: str | Iterable[str] | None = None,
    serializer: str | Callable[..., str] | str | None = None,
    suffix: str | None = None,
    project: str | Path = None,
) -> tuple[
    str | Path | None,
    str | Iterable[str] | None,
    str | Callable[..., str] | str | None,
    str | None,
    str | Path | None,
]:
    """Parse input to the ``@pytask.mark.julia`` decorator.

    Parameters
    ----------
    script : str | Path | None
        The path to the Julia script which is executed.
    options : str | Iterable[str] | None
        One or multiple command line options passed to the interpreter for Julia.
    serializer : Callable[Any, str] | None
        A function to serialize data for the task which accepts a dictionary with all
        the information. If the value is `None`, use either the value specified in the
        configuration file under ``julia_serializer`` or fall back to ``"json"``.
    suffix : str | None
        A suffix for the serialized file. If the value is `None`, use either the value
        specified in the configuration file under ``julia_suffix`` or fall back to
        ``".json"``.
    project : str | Path | None
        A path to an Julia environment used to execute this task.

    """
    if args or script is None:
        raise RuntimeError(_ERROR_MSG)

    options = [] if options is None else list(map(str, _to_list(options)))
    return script, options, serializer, suffix, project


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


def parse_relative_path(path: str | Path, root: Path) -> Path:
    """Parse a relative path."""
    if isinstance(path, str):
        path = Path(path)

    if not path.is_absolute():
        path = root / path

    return path.resolve()
