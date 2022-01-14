import shutil

import pytest
from click.testing import CliRunner

needs_ZZZZZ = pytest.mark.skipif(
    shutil.which("ZZZZZ") is None, reason="ZZZZZ needs to be installed."
)


@pytest.fixture()
def runner():
    return CliRunner()
