from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from pytask_julia.shared import julia


@pytest.mark.unit()
@pytest.mark.parametrize(
    ("args", "kwargs", "expectation", "expected"),
    [
        (
            (),
            {
                "script": "script.jl",
                "options": "--option",
                "serializer": "json",
                "suffix": ".json",
                "project": "some_path",
            },
            does_not_raise(),
            ("script.jl", ["--option"], "json", ".json", "some_path"),
        ),
        (
            (),
            {
                "script": "script.jl",
                "options": [1],
                "serializer": "yaml",
                "suffix": ".yaml",
                "project": "some_path",
            },
            does_not_raise(),
            ("script.jl", ["1"], "yaml", ".yaml", "some_path"),
        ),
    ],
)
def test_julia(args, kwargs, expectation, expected):
    with expectation:
        result = julia(*args, **kwargs)
        assert result == expected
