import karva
import pytest

from affect import Failure, Result, Success
from affect.exceptions import PanicError


def test_success_is_ok() -> None:
    success_result = Success(value="Test Value")
    assert success_result.is_ok() is True


def test_failure_is_ok_and() -> None:
    success_result = Success(value="Test Value")
    assert success_result.is_ok_and(lambda x: x == "Test Value") is True


def test_success_is_err() -> None:
    success_result = Success(value="Test Value")
    assert success_result.is_err() is False


def test_success_is_err_and() -> None:
    success_result = Success(value="Test Value")
    assert success_result.is_err_and(lambda x: x == "Test Value") is False


def test_success_ok() -> None:
    success_result = Success(value="Test Value")
    assert success_result.ok() == "Test Value"


def test_success_err() -> None:
    success_result: Result[str, None] = Success(value="Test Value")
    assert success_result.err() is None


@karva.tags.parametrize("value", [2, 3, 4, 5])
def test_success_map(value: int) -> None:
    success_result = Success(value=value)
    mapped_result = success_result.map(lambda x: x * 2)
    assert mapped_result.ok() == value * 2


@karva.tags.parametrize("value", [2, 3, 4, 5])
def test_success_map_or(value: int) -> None:
    success_result = Success(value=value)
    result = success_result.map_or(0, lambda x: x * 2)
    assert result == value * 2


@karva.tags.parametrize("value", [2, 3, 4, 5])
def test_success_map_or_else(value: int) -> None:
    success_result = Success(value=value)
    result = success_result.map_or_else(lambda _: 0, lambda x: x * 2)
    assert result == value * 2


def test_success_map_err() -> None:
    success_result = Success(value="Test Value")
    mapped_result = success_result.map_err(lambda _: "Error")
    assert mapped_result.ok() == "Test Value"


def test_success_inspect() -> None:
    success_result = Success(value="Test Value")

    def inspect_func(value: str) -> None:
        assert value == "Test Value"

    inspected_result = success_result.inspect(inspect_func)
    assert inspected_result.ok() == "Test Value"


def test_success_inspect_err() -> None:
    success_result = Success(value="Test Value")
    inspected_result = success_result.inspect_err(lambda _: "Error")
    assert inspected_result.ok() == "Test Value"


def test_success_hash() -> None:
    success_result = Success(value="Test Value")
    assert hash(success_result) == hash((True, "Test Value"))


def test_success_iter() -> None:
    success_result = Success(value="Test Value")
    values = list(success_result.iter())
    assert values == ["Test Value"]


def test_success_iter_method() -> None:
    success_result = Success(value="Test Value")
    values = list(success_result)
    assert values == ["Test Value"]


def test_success_expect() -> None:
    success_result = Success(value="Test Value")
    assert success_result.expect("This should return the value") == "Test Value"


def test_success_unwrap() -> None:
    success_result = Success(value="Test Value")
    assert success_result.unwrap() == "Test Value"


def test_success_expect_err() -> None:
    success_result = Success(value="Test Value")
    with pytest.raises(PanicError, match="This should panic: Test Value"):
        success_result.expect_err("This should panic")


def test_success_unwrap_err() -> None:
    success_result = Success(value="Test Value")
    with pytest.raises(PanicError, match="Test Value"):
        success_result.unwrap_err()


def test_success_and() -> None:
    success_result = Success(value="Test Value")
    other_result = Success(value="Other Value")
    assert success_result.and_(other_result) == other_result


def test_success_and_failure() -> None:
    success_result = Success(value="Test Value")
    failure_result = Failure(value="Test Error")
    assert success_result.and_(failure_result) == failure_result


@karva.tags.parametrize(
    ("value", "func", "expected"),
    [
        (10, lambda x: x + 5, 15),
        ("hello", lambda x: x.upper(), "HELLO"),
        ([1, 2, 3], lambda x: len(x), 3),
    ],
)
def test_success_map_various_types(value, func, expected) -> None:
    success_result = Success(value=value)
    mapped_result = success_result.map(func)
    assert mapped_result.ok() == expected


@karva.tags.parametrize(
    ("value", "default", "expected"),
    [(10, 0, 20), (5, 999, 10), (1, 100, 2)],
)
def test_success_map_or_parametrized(value: int, default: int, expected: int) -> None:
    success_result = Success(value=value)
    result = success_result.map_or(default, lambda x: x * 2)
    assert result == expected


def test_success_with_none() -> None:
    success_result = Success(value=None)
    assert success_result.is_ok()
    assert success_result.ok() is None
    assert success_result.unwrap() is None


def test_success_map_with_none() -> None:
    success_result = Success(value=None)
    mapped_result = success_result.map(lambda x: "mapped")
    assert mapped_result.ok() == "mapped"


@karva.tags.parametrize("value", ["", 0, False, [], {}])
def test_success_with_falsy_values(value) -> None:
    success_result = Success(value=value)
    assert success_result.is_ok()
    assert success_result.unwrap() == value


def test_success_inspect_multiple_calls() -> None:
    success_result = Success(value=10)
    call_count = []

    def track_call(value: int) -> None:
        call_count.append(value)

    result = success_result.inspect(track_call).inspect(track_call).inspect(track_call)
    assert len(call_count) == 3
    assert all(v == 10 for v in call_count)
    assert result.ok() == 10


@karva.tags.parametrize(
    ("start_value", "operations", "expected"),
    [
        (2, [lambda x: x * 2, lambda x: x + 1, lambda x: x * 3], 15),
        (5, [lambda x: x - 1, lambda x: x * 2, lambda x: x + 10], 18),
    ],
)
def test_success_map_chaining(start_value: int, operations, expected: int) -> None:
    success_result = Success(value=start_value)
    for operation in operations:
        success_result = success_result.map(operation)
    assert success_result.unwrap() == expected


def test_success_iter_in_for_loop() -> None:
    success_result = Success(value=42)
    values = []
    for value in success_result:
        values.append(value)
    assert values == [42]


def test_success_map_to_different_type() -> None:
    success_result = Success(value=42)
    string_result = success_result.map(str)
    list_result = string_result.map(list)
    assert list_result.unwrap() == ["4", "2"]
