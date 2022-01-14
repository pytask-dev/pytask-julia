"""Contains test which ensure that the plugin works with pytask-parallel."""
import os
import textwrap
import time

import pytest
from conftest import needs_ZZZZZ
from pytask import cli

try:
    import pytask_parallel  # noqa: F401
except ImportError:
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.skipif(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)


@needs_ZZZZZ
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_files(runner, tmp_path):
    """Test parallelization over source files.

    Same as in README.rst.

    """
    os.chdir(tmp_path)

    source = """
    import pytask

    @pytask.mark.xxxxx
    @pytask.mark.parametrize(
        "depends_on, produces", [("script_1.xxxxx", "1.csv"), ("script_2.xxxxx", "2.csv")]
    )
    def task_execute_ZZZZZ():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    xxxxx_script = """FIXME FOR YOUR LANGUAGE
    Sys.sleep(2)
    saveRDS(1, file=paste0(1, ".csv"))
    """
    tmp_path.joinpath("script_1.r").write_text(textwrap.dedent(xxxxx_script))

    r_script = """
    Sys.sleep(2)
    saveRDS(2, file=paste0(2, ".csv"))
    """
    tmp_path.joinpath("script_2.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in ["1.csv", "2.csv"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal


@needs_ZZZZZ
@pytest.mark.end_to_end
def test_parallel_parametrization_over_source_file(runner, tmp_path):
    """Test parallelization over the same source file.

    Same as in README.rst.

    """
    os.chdir(tmp_path)

    source = """
    import pytask
    from pathlib import Path

    SRC = Path(__file__).parent

    @pytask.mark.depends_on("script.xxxxx")
    @pytask.mark.parametrize("produces, xxxxx", [
        (SRC / "0.csv", (1, SRC / "0.csv")), (SRC / "1.csv", (1, SRC / "1.csv"))
    ])
    def task_execute_xxxxx_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    xxxxx_script = """FIXME FOR YOUR LANGUAGE
    Sys.sleep(2)
    args <- commandArgs(trailingOnly=TRUE)
    number <- args[1]
    produces <- args[2]
    saveRDS(number, file=produces)
    """
    tmp_path.joinpath("script.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
    duration_normal = time.time() - start

    for name in ["0.csv", "1.csv"]:
        tmp_path.joinpath(name).unlink()

    start = time.time()
    result = runner.invoke(cli, [tmp_path.as_posix(), "-n", 2])
    assert result.exit_code == 0
    duration_parallel = time.time() - start

    assert duration_parallel < duration_normal
