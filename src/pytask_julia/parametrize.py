"""Parametrize tasks."""
from __future__ import annotations

from typing import Any

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj: Any, kwargs: dict[str, Any]) -> None:
    """Attach parametrized Julia arguments to the function with a marker."""
    if callable(obj) and "julia" in kwargs:  # noqa: PLR2004
        pytask.mark.julia(**kwargs.pop("julia"))(obj)
