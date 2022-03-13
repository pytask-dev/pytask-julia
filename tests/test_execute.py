from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from pytask import cli
from pytask import main
from pytask import Mark
from pytask import Task
from pytask_julia.execute import pytask_execute_task_setup

from tests.conftest import needs_julia
from tests.conftest import parametrize_parse_code_serializer_suffix
from tests.conftest import ROOT


class DummyTask:
    pass


@pytest.mark.unit
def test_pytask_execute_task_setup_missing_julia(monkeypatch):
    """Make sure that the task setup raises errors."""
    # Act like julia is installed since we do not test this.
    monkeypatch.setattr(
        "pytask_julia.execute.shutil.which", lambda x: None  # noqa: U100
    )
    task = Task(
        base_name="example", path=Path(), function=None, markers=[Mark("julia", (), {})]
    )
    with pytest.raises(RuntimeError, match="julia is needed"):
        pytask_execute_task_setup(task)


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_run_jl_script(runner, tmp_path, parse_config_code, serializer, suffix):
    task_source = f"""
    import pytask

    @pytask.mark.julia(
        script="script.jl", serializer="{serializer}", project="{ROOT.as_posix()}"
    )
    @pytask.mark.produces("out.txt")
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

    assert result.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()
    assert tmp_path.joinpath(
        ".pytask", "task_dummy_py_task_run_jl_script" + suffix
    ).exists()


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_raise_error_if_julia_is_not_found(
    tmp_path, monkeypatch, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}",
    )
    @pytask.mark.produces("out.txt")
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
        "pytask_julia.execute.shutil.which", lambda x: None  # noqa: U100
    )

    session = main({"paths": tmp_path})

    assert session.exit_code == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_run_jl_script_w_wrong_cmd_option(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    @pytask.mark.julia(
        script="script.jl",
        options=("--wrong-flag"),
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}",
    )
    @pytask.mark.produces("out.txt")
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

    assert result.exit_code == 1
    assert "--wrong-flag" in result.output


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.parametrize("n_threads", [2, 3])
@parametrize_parse_code_serializer_suffix
def test_check_passing_cmd_line_options(
    runner, tmp_path, n_threads, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    @pytask.mark.julia(
        script="script.jl",
        options=("--threads", "{n_threads}"),
        serializer="{serializer}",
        suffix="{suffix}",
        project="{ROOT.as_posix()}"
    )
    @pytask.mark.produces("out.txt")
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(config["produces"], "A heart that's full up like a landfill.")
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == 0


@needs_julia
@pytest.mark.end_to_end
@parametrize_parse_code_serializer_suffix
def test_run_jl_script_w_environment_in_config(
    runner, tmp_path, parse_config_code, serializer, suffix
):
    task_source = f"""
    import pytask

    @pytask.mark.julia(
        script="script.jl",
        serializer="{serializer}",
        suffix="{suffix}",
    )
    @pytask.mark.produces("out.txt")
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

    tmp_path.joinpath("pytask.ini").write_text(
        f"[pytask]\njulia_project={ROOT.as_posix()}"
    )

    result = runner.invoke(cli, [tmp_path.as_posix()])

    assert result.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()
    assert tmp_path.joinpath(
        ".pytask", "task_dummy_py_task_run_jl_script" + suffix
    ).exists()
