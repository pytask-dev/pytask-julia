from contextlib import ExitStack as does_not_raise  # noqa: N813
from pathlib import Path

import pytest
from _pytask.mark import Mark
from _pytask.nodes import FilePathNode
from pytask_julia.collect import _get_node_from_dictionary
from pytask_julia.collect import _merge_all_markers
from pytask_julia.collect import _prepare_cmd_options
from pytask_julia.collect import julia
from pytask_julia.collect import pytask_collect_task
from pytask_julia.collect import pytask_collect_task_teardown


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


@pytest.mark.unit
@pytest.mark.parametrize(
    "depends_on, produces, expectation",
    [
        (["script.jl"], ["any_out.rds"], does_not_raise()),
        (["script.txt"], ["any_out.rds"], pytest.raises(ValueError)),
        (["input.csv", "script.jl"], ["any_out.csv"], pytest.raises(ValueError)),
    ],
)
@pytest.mark.parametrize("julia_source_key", ["source", "script"])
def test_pytask_collect_task_teardown(
    tmp_path, depends_on, produces, expectation, julia_source_key
):
    session = DummyClass()
    session.config = {"julia_source_key": julia_source_key}

    task = DummyClass()
    task.path = tmp_path / "task_dummy.py"
    task.name = tmp_path.as_posix() + "task_dummy.py::task_dummy"
    task.depends_on = {
        i: FilePathNode.from_path(tmp_path / n) for i, n in enumerate(depends_on)
    }
    task.produces = {
        i: FilePathNode.from_path(tmp_path / n) for i, n in enumerate(produces)
    }
    task.markers = [Mark("julia", (), {})]
    task.function = task_dummy
    task.function.pytaskmark = task.markers

    with expectation:
        pytask_collect_task_teardown(session, task)


@pytest.mark.unit
@pytest.mark.parametrize(
    "obj, key, expected",
    [
        (1, "asds", 1),
        (1, None, 1),
        ({"a": 1}, "a", 1),
        ({0: 1}, "a", 1),
    ],
)
def test_get_node_from_dictionary(obj, key, expected):
    result = _get_node_from_dictionary(obj, key)
    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "args, expectation, expected",
    [
        (("--"), does_not_raise(), ["julia", "--", "script.jl"]),
        (
            ("--verbose", "--"),
            does_not_raise(),
            ["julia", "--verbose", "--", "script.jl"],
        ),
        (("--", "seed"), does_not_raise(), ["julia", "--", "script.jl", "seed"]),
        (("--verbose",), pytest.raises(ValueError, match="The inputs"), None),
    ],
)
@pytest.mark.parametrize("julia_source_key", ["source", "script"])
def test_prepare_cmd_options(args, expectation, expected, julia_source_key):
    session = DummyClass()
    session.config = {"julia_source_key": julia_source_key}

    node = DummyClass()
    node.path = Path("script.jl")
    task = DummyClass()
    task.depends_on = {julia_source_key: node}
    task.name = "task"

    with expectation:
        result = _prepare_cmd_options(session, task, args)
        assert result == expected
