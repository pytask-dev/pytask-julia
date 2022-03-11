from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner


ROOT = Path(__file__).parent.joinpath("..").resolve()


needs_julia = pytest.mark.skipif(
    shutil.which("julia") is None, reason="julia needs to be installed."
)


@pytest.fixture()
def runner():
    return CliRunner()
