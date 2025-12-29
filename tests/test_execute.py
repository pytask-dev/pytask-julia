from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path
from typing import cast

import pytest
from pytask import ExitCode
from pytask import Mark
from pytask import Task
from pytask import build
from pytask import cli

from pytask_julia.execute import pytask_execute_task_setup
from tests.conftest import ROOT
from tests.conftest import needs_julia
from tests.conftest import parametrize_parse_code_serializer_suffix


@pytest.mark.unit
def test_pytask_execute_task_setup_missing_julia(monkeypatch):
    """Make sure that the task setup raises errors."""
    # Act like julia is installed since we do not test this.
    monkeypatch.setattr(
        "pytask_julia.execute.shutil.which",
        lambda x: None,  # noqa: ARG005
    )
    task = Task(
        base_name="example",
        path=Path(),
        function=lambda: None,
        markers=[Mark("julia", (), {})],
    )
    with pytest.raises(RuntimeError, match="julia is needed"):
        pytask_execute_task_setup(task)


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
@pytest.mark.parametrize("depends_on", ["'in_1.txt'", "['in_1.txt', 'in_2.txt']"])
def test_run_jl_script(  # noqa: PLR0913
    runner,
    tmp_path,
    parse_config_code,
    serializer,
    suffix,
    depends_on,
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}",
    )
    @pytask.task(kwargs={{"depends_on": {depends_on}}}, produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("in_1.txt").touch()
    tmp_path.joinpath("in_2.txt").touch()

    julia_script = f"""
    {parse_config_code}
    if length(config["depends_on"]) > 0
    else
        throw(DomainError("No dependencies"))
    end
    write(
        config["produces"],
        "Crying helps me to slow down and obsess over the weight of life's problems."
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_run_jl_script_w_task_decorator(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.task
    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}"
    )
    @pytask.task(produces=Path("out.txt"))
    def run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(
        config["produces"],
        "Crying helps me to slow down and obsess over the weight of life's problems."
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_raise_error_if_julia_is_not_found(
    tmp_path,
    monkeypatch,
    parse_config_code,
    serializer,
    suffix,
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}",
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(
        config["produces"],
        "What's going to happen? What does the future hold?"
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    # Hide julia if available.
    monkeypatch.setattr(
        "pytask_julia.execute.shutil.which",
        lambda x: None,  # noqa: ARG005
    )

    session = build(paths=tmp_path)

    assert session.exit_code == ExitCode.FAILED
    execution_reports = cast("list", session.execution_reports)
    assert isinstance(execution_reports[0].exc_info[1], RuntimeError)


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_run_jl_script_w_wrong_cmd_option(
    runner,
    tmp_path,
    parse_config_code,
    serializer,
    suffix,
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        options=("--wrong-flag"),
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}",
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(config["produces"], "So, so you think you can tell heaven from hell?")
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.FAILED
    assert "--wrong-flag" in result.output


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.parametrize("n_threads", [2, 3])
@parametrize_parse_code_serializer_suffix
def test_check_passing_cmd_line_options(  # noqa: PLR0913
    runner,
    tmp_path,
    n_threads,
    parse_config_code,
    serializer,
    suffix,
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        options=("--threads", "{n_threads}"),
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}"
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(config["produces"], "A heart that's full up like a landfill.")
    @assert Threads.nthreads() == {n_threads}
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.xfail(
    condition=sys.platform == "win32" and os.environ.get("CI") == "true",
    reason="Test folder and repo are on different drives causing relpath to fail.",
)
@parametrize_parse_code_serializer_suffix
@pytest.mark.parametrize("path", [ROOT, "relative_from_config"])
def test_run_jl_script_w_environment_in_config(  # noqa: PLR0913
    runner,
    tmp_path,
    parse_config_code,
    serializer,
    suffix,
    path,
):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(
        config["produces"],
        "Crying helps me to slow down and obsess over the weight of life's problems."
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    path_in_config = (
        path.as_posix()
        if isinstance(path, Path)
        else Path(os.path.relpath(ROOT, tmp_path)).as_posix()
    )
    tmp_path.joinpath("pyproject.toml").write_text(
        f"[tool.pytask.ini_options]\njulia_project='{path_in_config}'"
    )

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.xfail(
    condition=sys.platform == "win32" and os.environ.get("CI") == "true",
    reason="Test folder and repo are on different drives causing relpath to fail.",
)
@parametrize_parse_code_serializer_suffix
def test_run_jl_script_w_environment_relative_to_task(
    runner,
    tmp_path,
    parse_config_code,
    serializer,
    suffix,
):
    project_in_task = Path(os.path.relpath(ROOT, tmp_path)).as_posix()

    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
        project="{project_in_task}",
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(
        config["produces"],
        "Crying helps me to slow down and obsess over the weight of life's problems."
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_julia
@pytest.mark.end_to_end
def test_run_jl_script_w_custom_serializer(runner, tmp_path):
    task_source = f"""
    import pytask
    from pathlib import Path
    import json

    @pytask.mark.julia(
        script="script.jl",
        serializer=json.dumps,
        project="{ROOT.as_posix()}",
    )
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = """
    import JSON; config = JSON.parse(read(ARGS[1], String))
    write(
        config["produces"],
        "Crying helps me to slow down and obsess over the weight of life's problems."
    )
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.OK
    assert tmp_path.joinpath("out.txt").exists()


@needs_julia
@pytest.mark.end_to_end
def test_run_jl_script_fails_w_multiple_markers(runner, tmp_path):
    task_source = """
    import pytask
    from pathlib import Path

    @pytask.mark.julia(script="script.jl")
    @pytask.mark.julia(script="script.jl")
    @pytask.task(produces=Path("out.txt"))
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))
    tmp_path.joinpath("script.jl").touch()

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == ExitCode.COLLECTION_FAILED
    assert "has multiple @pytask.mark.julia marks" in result.output
