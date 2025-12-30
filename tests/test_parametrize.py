from __future__ import annotations

import textwrap

from pytask import ExitCode
from pytask import cli

from tests.conftest import ROOT
from tests.conftest import needs_julia
from tests.conftest import parametrize_parse_code_serializer_suffix


@needs_julia
@parametrize_parse_code_serializer_suffix
def test_parametrized_execution_of_jl_script_w_loop(
    runner,
    tmp_path,
    parse_config_code,
    serializer,
    suffix,
):
    task_source = f"""
    import pytask
    from pytask import task
    from pathlib import Path

    for i, content in enumerate([
        "Cities breaking down on a camel's back",
         "They just have to go 'cause they don't know whack",
    ]):

        @task(kwargs={{"content": content}})
        @pytask.mark.julia(
            script="script_1.jl",
            project="{ROOT.as_posix()}",
            serializer="{serializer}",
            suffix="{suffix}"
        )
        def task_run_jl_script(produces=Path(f"{{i}}.txt")):
            pass
    """
    tmp_path.joinpath("task_dummy.py").write_text(textwrap.dedent(task_source))

    for name in ("script_1.jl", "script_2.jl"):
        julia_script = f"""
        {parse_config_code}
        write(config["produces"], config["content"])
        """
        tmp_path.joinpath(name).write_text(textwrap.dedent(julia_script))

    result = runner.invoke(cli, [tmp_path.as_posix()])
    assert result.exit_code == ExitCode.OK
