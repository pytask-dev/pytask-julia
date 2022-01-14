import os
import textwrap
from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from _pytask.mark import Mark
from conftest import needs_ZZZZZ
from pytask import main
from pytask_xxxxx.execute import pytask_execute_task_setup


class DummyTask:
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "found_ZZZZZ, expectation",
    [
        (True, does_not_raise()),
        (None, pytest.raises(RuntimeError)),
    ],
)
def test_pytask_execute_task_setup(monkeypatch, found_ZZZZZ, expectation):
    """Make sure that the task setup raises errors."""
    # Act like r is installed since we do not test this.
    monkeypatch.setattr("pytask_r.execute.shutil.which", lambda x: found_ZZZZZ)

    task = DummyTask()
    task.markers = [Mark("xxxxx", (), {})]

    with expectation:
        pytask_execute_task_setup(task)


@needs_ZZZZZ
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "depends_on",
    [
        "'script.xxxxx'",
        {"source": "script.xxxxx"},
        {0: "script.xxxxx"},
        {"script": "script.xxxxx"},
    ],
)
def test_run_xxxxx_script(tmp_path, depends_on):
    task_source = f"""
    import pytask

    @pytask.mark.r
    @pytask.mark.depends_on({depends_on})
    @pytask.mark.produces("out.txt")
    def task_run_xxxxx_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    xxxxx_script = """
    file_descriptor <- file("out.txt")
    writeLines(c("So, so you think you can tell heaven from hell?"), file_descriptor)
    close(file_descriptor)
    """
    tmp_path.joinpath("script.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    if (
        isinstance(depends_on, dict)
        and "source" not in depends_on
        and 0 not in depends_on
    ):
        tmp_path.joinpath("pytask.ini").write_text("[pytask]\nr_source_key = script")

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()


@pytest.mark.end_to_end
def test_raise_error_if_ZZZZZ_is_not_found(tmp_path, monkeypatch):
    task_source = """
    import pytask

    @pytask.mark.xxxxx
    @pytask.mark.depends_on("script.xxxxx")
    @pytask.mark.produces("out.txt")
    def task_run_xxxxx_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    xxxxx_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    # Hide ZZZZZ if available.
    monkeypatch.setattr("pytask_xxxxx.execute.shutil.which", lambda x: None)

    session = main({"paths": tmp_path})

    assert session.exit_code == 1
    assert isinstance(session.execution_reports[0].exc_info[1], RuntimeError)


@needs_ZZZZZ
@pytest.mark.end_to_end
def test_run_xxxxx_script_w_saving_workspace(tmp_path):
    """Save workspace while executing the script."""
    task_source = """
    import pytask

    @pytask.mark.xxxxx("--save")
    @pytask.mark.depends_on("script.xxxxx")
    @pytask.mark.produces("out.txt")
    def task_run_xxxxx_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    xxxxx_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("out.txt").exists()


@needs_ZZZZZ
@pytest.mark.end_to_end
def test_run_xxxxx_script_w_wrong_cmd_option(tmp_path):
    """Apparently, RScript simply discards wrong cmd options -- hopefully ZZZZZ does better."""
    task_source = """
    import pytask

    @pytask.mark.xxxxx("--wrong-flag")
    @pytask.mark.depends_on("script.xxxxx")
    @pytask.mark.produces("out.txt")
    def task_run_xxxxx_script():
        pass

    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    xxxxx_script = """
    file_descr <- file("out.txt")
    writeLines(c("Birds flying high you know how I feel."), file_descr)
    close(file_descr)
    """
    tmp_path.joinpath("script.xxxxx").write_text(textwrap.dedent(xxxxx_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
