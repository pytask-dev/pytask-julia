from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from pytask_julia.collect import _merge_all_markers
from pytask_julia.collect import julia
from pytask_julia.collect import pytask_collect_task


class DummyClass:
    pass


def task_dummy():
    pass


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


@pytest.mark.unit
@pytest.mark.parametrize(
    "marks, expected",
    [
        (
            [Mark("julia", ("--a",), {}), Mark("julia", ("--b",), {})],
            Mark("julia", ("--a", "--b"), {}),
        ),
        (
            [Mark("julia", ("--a",), {}), Mark("julia", (), {"julia": "--b"})],
            Mark("julia", ("--a",), {"julia": "--b"}),
        ),
    ],
)
def test_merge_all_markers(marks, expected):
    task = DummyClass()
    task.markers = marks
    out = _merge_all_markers(task)
    assert out == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "name, expected",
    [("task_dummy", True), ("invalid_name", None)],
)
def test_pytask_collect_task(name, expected):
    session = DummyClass()
    path = Path("some_path")
    task_dummy.pytaskmark = [Mark("julia", (), {})]

    task = pytask_collect_task(session, path, name, task_dummy)

    if expected:
        assert task
    else:
        assert not task
