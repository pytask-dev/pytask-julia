from pathlib import Path
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union


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
