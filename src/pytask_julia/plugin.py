"""Register hook specifications and implementations."""
from _pytask.config import hookimpl
from pytask_xxxxx import collect
from pytask_xxxxx import config
from pytask_xxxxx import execute
from pytask_xxxxx import parametrize


@hookimpl
def pytask_add_hooks(pm):
    """Register hook implementations."""
    pm.register(collect)
    pm.register(config)
    pm.register(execute)
    pm.register(parametrize)
