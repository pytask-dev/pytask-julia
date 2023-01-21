"""This module contains shared functions."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Sequence


JULIA_SCRIPT_KEY = "__script"


def julia(
    script: str | Path,
    options: str | Iterable[str] | None = None,
    serializer: Callable[..., str] | str | None = None,
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
    script : str | Path
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
    options = [] if options is None else list(map(str, _to_list(options)))
    return script, options, serializer, suffix, project


def _to_list(scalar_or_iter: Any) -> list[Any]:
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
