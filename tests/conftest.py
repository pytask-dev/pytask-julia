from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner


ROOT = Path(__file__).parent.joinpath("..").resolve()


needs_julia = pytest.mark.skipif(
    shutil.which("julia") is None, reason="julia needs to be installed.",
)


parametrize_parse_code_serializer_suffix = pytest.mark.parametrize(
    "parse_config_code, serializer, suffix",
    [
        ("import JSON; config = JSON.parse(read(ARGS[1], String))", "json", ".json"),
        ("import YAML; config = YAML.load_file(ARGS[1])", "yaml", ".yaml"),
    ],
)


@pytest.fixture()
def runner():
    return CliRunner()
