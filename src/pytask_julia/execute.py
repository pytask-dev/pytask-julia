"""Execute tasks."""
import shutil

from _pytask.config import hookimpl
from _pytask.mark_utils import get_specific_markers_from_task


@hookimpl
def pytask_execute_task_setup(task):
    """Check whether environment allows executing YYYYY files."""
    if get_specific_markers_from_task(task, "r"):
        if shutil.which("ZZZZZ") is None:
            raise RuntimeError(
                "ZZZZZ is needed to run YYYYY scripts, but it is not found on your PATH."
            )
