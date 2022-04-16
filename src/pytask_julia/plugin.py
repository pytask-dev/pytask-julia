"""Register hook specifications and implementations."""
from __future__ import annotations

from pytask import hookimpl
from pytask_julia import collect
from pytask_julia import config
from pytask_julia import execute
from pytask_julia import parametrize


@hookimpl
def pytask_add_hooks(pm):
    """Register hook implementations."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
