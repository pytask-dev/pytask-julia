from __future__ import annotations

import pytest
from pytask_julia.shared import julia


@pytest.mark.unit
@pytest.mark.parametrize(
    "julia_args, expected",
    [
        (None, ["--"]),
        ("--some-option", ["--some-option"]),
        (["--a", "--b"], ["--a", "--b"]),
    ],
)
def test_julia(julia_args, expected):
    options = julia(julia_args)
    assert options == expected
