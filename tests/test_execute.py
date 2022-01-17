import os
import textwrap
from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from _pytask.mark import Mark
from conftest import needs_julia
from pytask import main
from pytask_julia.execute import pytask_execute_task_setup


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "found_julia, expectation",
    [
        (True, does_not_raise()),
        (None, pytest.raises(RuntimeError)),
    ],
)
def test_pytask_execute_task_setup(monkeypatch, found_julia, expectation):
    """Make sure that the task setup raises errors."""
    # Act like julia is installed since we do not test this.
    monkeypatch.setattr("pytask_julia.execute.shutil.which", lambda x: found_julia)

    task = DummyTask()
    task.markers = [Mark("julia", (), {})]

    with expectation:
        pytask_execute_task_setup(task)


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "depends_on",
    [
        "'script.jl'",
        {"source": "script.jl"},
        {0: "script.jl"},
        {"script": "script.jl"},
    ],
)
def test_run_jl_script(tmp_path, depends_on):
    task_source = f"""
    import pytask

    @pytask.mark.julia
    @pytask.mark.depends_on({depends_on})
    @pytask.mark.produces("out.txt")
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = """
    write("out.txt", "So, so you think you can tell heaven from hell?")
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    if (
        isinstance(depends_on, dict)
        and "source" not in depends_on
        and 0 not in depends_on
    ):
        tmp_path.joinpath("pytask.ini").write_text(
            "[pytask]\njulia_source_key = script"
        )

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()


@pytest.mark.end_to_end
def test_raise_error_if_julia_is_not_found(tmp_path, monkeypatch):
    task_source = """
    import pytask

    @pytask.mark.julia
    @pytask.mark.depends_on("script.jl")
    @pytask.mark.produces("out.txt")
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = """
    write("out.txt", "So, so you think you can tell heaven from hell?")
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    # Hide julia if available.
    monkeypatch.setattr("pytask_julia.execute.shutil.which", lambda x: None)

    session = main({"paths": tmp_path})

    assert session.exit_code == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_julia
@pytest.mark.end_to_end
def test_run_jl_script_w_wrong_cmd_option(tmp_path):
    """Apparently, RScript simply discards wrong cmd options -- hopefully julia does better."""
    task_source = """
    import pytask

    @pytask.mark.julia("--wrong-flag")
    @pytask.mark.depends_on("script.jl")
    @pytask.mark.produces("out.txt")
    def task_run_jl_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = """
    write("out.txt", "So, so you think you can tell heaven from hell?")
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
