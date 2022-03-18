from __future__ import annotations

from contextlib import ExitStack as does_not_raise  # noqa: N813

import pytest
from _pytask.mark import Mark
from pytask_julia.collect import _parse_julia_mark
from pytask_julia.collect import _parse_project
from pytask_julia.collect import SERIALIZER

from tests.conftest import ROOT


@pytest.mark.unit
@pytest.mark.parametrize(
    "mark, default_options, default_serializer, default_suffix, default_project, "
    "expectation, expected",
    [
        (
            Mark("julia", (), {}),
            [],
            None,
            ".json",
            None,
            pytest.raises(RuntimeError, match="The old syntax for @pytask.mark.julia"),
            Mark(
                "julia",
                (),
                {
                    "script": None,
                    "options": [],
                    "serializer": None,
                    "suffix": ".json",
                    "project": None,
                },
            ),
        ),
        (
            Mark("julia", ("-o"), {}),
            [],
            None,
            ".json",
            None,
            pytest.raises(RuntimeError, match="The old syntax for @pytask.mark.julia"),
            None,
        ),
        (
            Mark("julia", (), {"script": "script.jl"}),
            [],
            None,
            ".json",
            "some_path",
            does_not_raise(),
            Mark(
                "julia",
                (),
                {
                    "script": "script.jl",
                    "options": [],
                    "serializer": None,
                    "suffix": ".json",
                    "project": "some_path",
                },
            ),
        ),
        (
            Mark(
                "julia",
                (),
                {
                    "script": "script.jl",
                    "serializer": "json",
                    "project": "some_path",
                },
            ),
            [],
            None,
            None,
            "some_other_path",
            does_not_raise(),
            Mark(
                "julia",
                (),
                {
                    "script": "script.jl",
                    "options": [],
                    "serializer": "json",
                    "suffix": SERIALIZER["json"]["suffix"],
                    "project": "some_path",
                },
            ),
        ),
    ],
)
def test_parse_julia_mark(
    mark,
    default_options,
    default_serializer,
    default_suffix,
    default_project,
    expectation,
    expected,
):
    with expectation:
        out = _parse_julia_mark(
            mark, default_options, default_serializer, default_suffix, default_project
        )
        assert out == expected


@pytest.mark.parametrize(
    "project, root, expected",
    [
        (None, ROOT, []),
    ],
)
def test_parse_project(project, root, expected):
    result = _parse_project(project, root)
    assert result == expected
