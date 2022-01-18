import os
import textwrap

import pytest
from conftest import needs_julia
from pytask import main


@needs_julia
@pytest.mark.end_to_end
def test_parametrized_execution_of_jl_script(tmp_path):
    task_source = """
    import pytask

    @pytask.mark.julia
    @pytask.mark.parametrize("depends_on, produces", [
        ("script_1.jl", "0.txt"),
        ("script_2.jl", "1.txt"),
    ])
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name, content, out in [
        ("script_1.jl", "Cities breaking down on a camel's back", "0.txt"),
        ("script_2.jl", "They just have to go 'cause they don't know whack", "1.txt"),
    ]:
        julia_script = f"""
        write("{out}", "{content}")
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(julia_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("0.txt").exists()
    assert tmp_path.joinpath("1.txt").exists()


@needs_julia
@pytest.mark.end_to_end
def test_parametrize_jl_options_and_product_paths(tmp_path):
    task_source = """
    import pytask
    from pathlib import Path

    SRC = Path(__file__).parent

    @pytask.mark.depends_on("script.jl")
    @pytask.mark.parametrize("produces, julia", [
        (SRC / "0.csv", ("--", 0, SRC / "0.csv")),
        (SRC / "1.csv", ("--", 1, SRC / "1.csv")),
    ])
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = """
    number = ARGS[1]
    produces = ARGS[2]
    write(produces, number)
    """

    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    os.chdir(tmp_path)
    session = main({"paths": tmp_path})

    assert session.exit_code == 0
    assert tmp_path.joinpath("0.csv").exists()
    assert tmp_path.joinpath("1.csv").exists()
