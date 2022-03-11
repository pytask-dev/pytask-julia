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
    "markers, default_options, default_serializer, default_suffix, expected",
    [
        (
            [Mark("julia", (), {})],
            [],
            None,
            ".json",
            Mark(
                "julia",
                (),
                {"script": None, "options": [], "serializer": None, "suffix": ".json"},
            ),
        ),
        (
            [Mark("julia", (), {"script": "script.jl"})],
            [],
            None,
            ".json",
            Mark(
                "julia",
                (),
                {
                    "script": "script.jl",
                    "options": [],
                    "serializer": None,
                    "suffix": ".json",
                },
            ),
        ),
        (
            [
                Mark("julia", (), {"script": "script.jl"}),
                Mark("julia", (), {"serializer": "json"}),
            ],
            [],
            None,
            None,
            Mark(
                "julia",
                (),
                {
                    "script": "script.jl",
                    "options": [],
                    "serializer": "json",
                    "suffix": SERIALIZER["json"]["suffix"],
                },
            ),
        ),
    ],
)
def test_merge_all_markers(
    markers, default_options, default_serializer, default_suffix, expected
):
    out = _merge_all_markers(
        markers, default_options, default_serializer, default_suffix
    )
    assert out == expected
