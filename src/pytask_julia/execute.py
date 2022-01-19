"""Execute tasks."""
import shutil

from _pytask.config import hookimpl
from _pytask.mark_utils import get_specific_markers_from_task


@hookimpl
def pytask_execute_task_setup(task):
    """Check whether environment allows executing Julia files."""
    if get_specific_markers_from_task(task, "julia"):
        if shutil.which("julia") is None:
            raise RuntimeError(
                "julia is needed to run Julia scripts, but it is not found on your "
                "PATH."
            )
