from __future__ import annotations

import textwrap

import pytest
from pytask import cli

from tests.conftest import needs_julia
from tests.conftest import ROOT


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "parse_config_code",
    [
        "import JSON; config = JSON.parse(read(ARGS[1], String))",
        "import YAML; config = YAML.load_file(ARGS[1])",
    ],
)
def test_parametrized_execution_of_jl_script(runner, tmp_path, parse_config_code):
    task_source = f"""
    import pytask

    @pytask.mark.parametrize("julia, content, produces", [
        (
            {{"script": "script_1.jl", "project": "{ROOT.as_posix()}"}},
            "Cities breaking down on a camel's back", "0.txt"),
        (
            {{"script": "script_2.jl", "project": "{ROOT.as_posix()}"}},
            "They just have to go 'cause they don't know whack",
            "1.txt"
        ),
    ])
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name in ["script_1.jl", "script_2.jl"]:
        julia_script = f"""
        {parse_config_code}
        write(config["produces"], config["content"])
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0


@needs_julia
@pytest.mark.end_to_end
@pytest.mark.parametrize(
    "parse_config_code",
    [
        "import JSON; config = JSON.parse(read(ARGS[1], String))",
        "import YAML; config = YAML.load_file(ARGS[1])",
    ],
)
def test_parametrize_jl_options_and_product_paths(runner, tmp_path, parse_config_code):
    task_source = f"""
    import pytask
    from pathlib import Path

    @pytask.mark.parametrize("produces, julia, i", [
        ("0.csv", {{"script": "script.jl", "project": "{ROOT.as_posix()}"}}, 0),
        ("1.csv", {{"script": "script.jl", "project": "{ROOT.as_posix()}"}}, 1),
    ])
    def task_run_jl_script():
        pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    julia_script = f"""
    {parse_config_code}
    write(config["produces"], config["i"])
    """
    tmp_path.joinpath("script.jl").write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == 0
