"""Parametrize tasks."""
from __future__ import annotations

import pytask
from pytask import hookimpl


@hookimpl
def pytask_parametrize_kwarg_to_marker(obj, kwargs):
    """Attach parametrized Julia arguments to the function with a marker."""
    if callable(obj):
        if "julia" in kwargs:
            pytask.mark.julia(**kwargs.pop("julia"))(obj)
