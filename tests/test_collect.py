from __future__ import annotations

import pytest
from _pytask.mark import Mark
from pytask_julia.collect import _merge_all_markers
from pytask_julia.collect import SERIALIZER


class DummyClass:
    pass


def task_dummy():
    pass


@pytest.mark.unit
@pytest.mark.parametrize(
    "markers, default_options, default_serializer, default_suffix, default_project, "
    "expected",
    [
        (
            [Mark("julia", (), {})],
            [],
            None,
            ".json",
            None,
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
            [Mark("julia", (), {"script": "script.jl"})],
            [],
            None,
            ".json",
            "some_path",
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
            [
                Mark("julia", (), {"script": "script.jl"}),
                Mark("julia", (), {"serializer": "json"}),
                Mark("julia", (), {"project": "some_path"}),
            ],
            [],
            None,
            None,
            "some_other_path",
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
def test_merge_all_markers(
    markers,
    default_options,
    default_serializer,
    default_suffix,
    default_project,
    expected,
):
    out = _merge_all_markers(
        markers, default_options, default_serializer, default_suffix, default_project
    )
    assert out == expected
