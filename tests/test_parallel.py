"""Contains test which ensure that the plugin works with pytask-parallel."""
from __future__ import annotations

import textwrap
import time

import pytest
from pytask import cli

from tests.conftest import needs_julia
from tests.conftest import parametrize_parse_code_serializer_suffix

try:
    import pytask_parallel  # noqa: F401
except ImportError:
    _IS_PYTASK_PARALLEL_INSTALLED = False
else:
    _IS_PYTASK_PARALLEL_INSTALLED = True


pytestmark = pytest.mark.skipif(
    not _IS_PYTASK_PARALLEL_INSTALLED, reason="Tests require pytask-parallel."
)


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_files_w_parametrize(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over source files.

    Same as in README.rst.

    """
    source = f"""
    import pytask

    @pytask.mark.parametrize("julia, content, produces", [
        (
            {{
                "script": "script_1.jl",
                "serializer": "{serializer}",
                suffix="{suffix}"
            }},
            "1",
            "1.csv"
        ),
        (
            {{
                "script": "script_2.jl",
                "serializer": "{serializer}",
                suffix="{suffix}"
            }},
            "2",
            "2.csv"
        ),
    ])
    def task_execute_julia():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["content"])
    """
    tmp_path.joinpath("script_1.jl").write_text(textwrap.dedent(julia_script))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["content"])
    """
    tmp_path.joinpath("script_2.jl").write_text(textwrap.dedent(julia_script))

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


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_files_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over source files.

    Same as in README.rst.

    """
    source = f"""
    import pytask

    for i in range(1, 3):

        @pytask.mark.parametrize("julia, content, produces", [
            (
                {{
                    "script": "script_1.jl",
                    "serializer": "{serializer}",
                    "suffix": "{suffix}"
                }},
                "1",
                "1.csv"
            ),
            (
                {{
                    "script": "script_2.jl",
                    "serializer": "{serializer}",
                    "suffix": "{suffix}"
                }},
                "2",
                "2.csv"
            ),
        ])
        @pytask.mark.task(kwargs={{"content": i}})
        @pytask.mark.julia(
            script=f"script_{{i}}.jl", serializer="{serializer}", suffix="{suffix}"
        )
        @pytask.mark.produces(f"{{i}}.csv")
        def task_execute_julia():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["content"])
    """
    tmp_path.joinpath("script_1.jl").write_text(textwrap.dedent(julia_script))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["content"])
    """
    tmp_path.joinpath("script_2.jl").write_text(textwrap.dedent(julia_script))

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


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_file_w_parametrize(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over the same source file.

    Same as in README.rst.

    """
    source = f"""
    import pytask

    @pytask.mark.julia(script="script.jl", serializer="{serializer}", suffix="{suffix}")
    @pytask.mark.parametrize("produces, number", [
        (SRC / "0.csv", 1), (SRC / "1.csv", 2),
    ])
    def task_execute_julia_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["number"])
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

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


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_parallel_parametrization_over_source_file_w_loop(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    """Test parallelization over the same source file.

    Same as in README.rst.

    """
    source = f"""
    import pytask

    for i in range(1, 3):

        @pytask.mark.task(kwargs={{"number": i}})
        @pytask.mark.julia(
            script="script.jl", serializer="{serializer}", suffix="{suffix}"
        )
        @pytask.mark.produces(f"{{i}}.csv")
        def task_execute_julia_script():
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(source))

    julia_script = f"""
    {parse_config_code}
    sleep(4)
    write(config["produces"], config["number"])
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

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
