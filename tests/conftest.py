import shutil

import pytest
from click.testing import CliRunner

needs_julia = pytest.mark.skipif(
    shutil.which("julia") is None, reason="julia needs to be installed."
)


@pytest.fixture()
def runner():
    return CliRunner()
