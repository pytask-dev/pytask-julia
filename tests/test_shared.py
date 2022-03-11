from __future__ import annotations

import pytest
from pytask_julia.shared import julia


@pytest.mark.unit
@pytest.mark.parametrize(
    "inputs, expected",
    [
        ({}, (None, [], None, None, None)),
        (
            {
                "script": "script.jl",
                "options": "--option",
                "serializer": "json",
                "suffix": ".json",
                "project": "some_path",
            },
            ("script.jl", ["--option"], "json", ".json", "some_path"),
        ),
        (
            {
                "script": "script.jl",
                "options": [1],
                "serializer": "yaml",
                "suffix": ".yaml",
                "project": "some_path",
            },
            ("script.jl", ["1"], "yaml", ".yaml", "some_path"),
        ),
    ],
)
def test_julia(inputs, expected):
    result = julia(**inputs)
    assert result == expected
