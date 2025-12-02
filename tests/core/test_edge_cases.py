import karva
import pytest

from affect import Failure, Success
from affect.exceptions import PanicError


def test_success_with_none_value() -> None:
    success = Success(value=None)
    assert success.is_ok()
    assert success.unwrap() is None


def test_failure_with_none_value() -> None:
    failure = Failure(value=None)
    assert failure.is_err()
    assert failure.unwrap_err() is None


def test_success_with_empty_string() -> None:
    success = Success(value="")
    assert success.is_ok()
    assert success.unwrap() == ""


def test_failure_with_empty_string() -> None:
    failure = Failure(value="")
    assert failure.is_err()
    assert failure.unwrap_err() == ""


def test_success_with_zero() -> None:
    success = Success(value=0)
    assert success.is_ok()
    assert success.unwrap() == 0


def test_failure_with_zero() -> None:
    failure = Failure(value=0)
    assert failure.is_err()
    assert failure.unwrap_err() == 0


def test_success_with_false() -> None:
    success = Success(value=False)
    assert success.is_ok()
    assert success.unwrap() is False


def test_failure_with_false() -> None:
    failure = Failure(value=False)
    assert failure.is_err()
    assert failure.unwrap_err() is False


@karva.tags.parametrize("value", [[], {}, set(), tuple()])
def test_success_with_empty_collections(value) -> None:
    success = Success(value=value)
    assert success.is_ok()
    assert success.unwrap() == value


@karva.tags.parametrize("value", [[], {}, set(), tuple()])
def test_failure_with_empty_collections(value) -> None:
    failure = Failure(value=value)
    assert failure.is_err()
    assert failure.unwrap_err() == value


def test_success_with_complex_nested_structure() -> None:
    value = {"key": [1, 2, {"nested": "value"}], "other": (3, 4)}
    success = Success(value=value)
    assert success.unwrap() == value


def test_success_map_chain() -> None:
    success = Success(value=2)
    result = success.map(lambda x: x * 2).map(lambda x: x + 1).map(lambda x: str(x))
    assert result.unwrap() == "5"


def test_failure_map_err_chain() -> None:
    failure = Failure(value="error")
    result = (
        failure.map_err(lambda x: f"{x}1")
        .map_err(lambda x: f"{x}2")
        .map_err(lambda x: f"{x}3")
    )
    assert result.unwrap_err() == "error123"


def test_success_inspect_side_effects() -> None:
    calls = []
    success = Success(value=42)
    result = (
        success.inspect(lambda x: calls.append(x))
        .inspect(lambda x: calls.append(x * 2))
        .inspect(lambda x: calls.append(x * 3))
    )
    assert calls == [42, 84, 126]
    assert result.unwrap() == 42


def test_failure_inspect_err_side_effects() -> None:
    calls = []
    failure = Failure(value="error")
    result = (
        failure.inspect_err(lambda x: calls.append(x))
        .inspect_err(lambda x: calls.append(f"{x}2"))
        .inspect_err(lambda x: calls.append(f"{x}3"))
    )
    assert calls == ["error", "error2", "error3"]
    assert result.unwrap_err() == "error"


def test_success_is_ok_and_with_complex_predicate() -> None:
    success = Success(value=[1, 2, 3, 4, 5])
    assert success.is_ok_and(lambda x: len(x) == 5)
    assert success.is_ok_and(lambda x: sum(x) == 15)
    assert not success.is_ok_and(lambda x: len(x) > 10)


def test_failure_is_err_and_with_complex_predicate() -> None:
    failure = Failure(value={"code": 404, "message": "Not Found"})
    assert failure.is_err_and(lambda x: x["code"] == 404)
    assert failure.is_err_and(lambda x: "message" in x)
    assert not failure.is_err_and(lambda x: x["code"] == 200)


def test_success_map_or_else_with_unused_default() -> None:
    success = Success(value=10)
    default_called = []

    def default_fn(x):
        default_called.append(x)
        return 0

    result = success.map_or_else(default_fn, lambda x: x * 2)
    assert result == 20
    assert len(default_called) == 0


def test_failure_map_or_else_with_used_default() -> None:
    failure = Failure(value="error")
    map_called = []

    def map_fn(x):
        map_called.append(x)
        return x * 2

    result = failure.map_or_else(lambda x: f"{x}_handled", map_fn)
    assert result == "error_handled"
    assert len(map_called) == 0


@karva.tags.parametrize(
    ("value", "predicate", "expected"),
    [
        (5, lambda x: x > 0, True),
        (5, lambda x: x < 0, False),
        ("test", lambda x: len(x) == 4, True),
        ([1, 2, 3], lambda x: 2 in x, True),
    ],
)
def test_success_is_ok_and_parametrized(value, predicate, expected: bool) -> None:
    success = Success(value=value)
    assert success.is_ok_and(predicate) == expected


@karva.tags.parametrize(
    ("value", "predicate", "expected"),
    [
        (404, lambda x: x >= 400, True),
        (404, lambda x: x < 400, False),
        ("error", lambda x: "err" in x, True),
        ({"code": 500}, lambda x: x["code"] == 500, True),
    ],
)
def test_failure_is_err_and_parametrized(value, predicate, expected: bool) -> None:
    failure = Failure(value=value)
    assert failure.is_err_and(predicate) == expected


def test_success_and_with_multiple_chaining() -> None:
    result1 = Success(value=1)
    result2 = Success(value=2)
    result3 = Success(value=3)
    final = result1.and_(result2).and_(result3)
    assert final == result3
    assert final.unwrap() == 3


def test_success_and_failure_early_termination() -> None:
    result1 = Success(value=1)
    result2 = Failure(value="error")
    result3 = Success(value=3)
    final = result1.and_(result2).and_(result3)
    assert final == result2
    assert final.unwrap_err() == "error"


def test_success_iter_multiple_times() -> None:
    success = Success(value=42)
    list1 = list(success)
    list2 = list(success)
    assert list1 == list2 == [42]


def test_failure_iter_multiple_times() -> None:
    failure = Failure(value="error")
    list1 = list(failure)
    list2 = list(failure)
    assert list1 == list2 == [None]


class CustomClass:
    def __init__(self, value: int) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CustomClass):
            return False
        return self.value == other.value


def test_success_with_custom_class() -> None:
    obj = CustomClass(42)
    success = Success(value=obj)
    assert success.unwrap().value == 42


def test_failure_with_custom_exception() -> None:
    class CustomError(Exception):
        pass

    error = CustomError("custom error")
    failure = Failure(value=error)
    assert isinstance(failure.unwrap_err(), CustomError)
    assert str(failure.unwrap_err()) == "custom error"


def test_success_expect_with_unused_message() -> None:
    success = Success(value=42)
    result = success.expect("This message should not be used")
    assert result == 42


def test_failure_expect_with_custom_message() -> None:
    failure = Failure(value="error")
    with pytest.raises(PanicError) as exc_info:
        failure.expect("Custom panic message")
    assert "Custom panic message: error" in str(exc_info.value)


def test_success_expect_err_raises_with_value() -> None:
    success = Success(value="unexpected_success")
    with pytest.raises(PanicError) as exc_info:
        success.expect_err("Expected an error")
    assert "Expected an error: unexpected_success" in str(exc_info.value)


def test_failure_expect_err_returns_value() -> None:
    failure = Failure(value="expected_error")
    result = failure.expect_err("This message is not used")
    assert result == "expected_error"


@karva.tags.parametrize(
    "value",
    [
        lambda x: x + 1,
        CustomClass(10),
        {"nested": {"deeply": {"value": 42}}},
        [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
    ],
)
def test_success_with_complex_types(value) -> None:
    success = Success(value=value)
    assert success.is_ok()
    assert success.unwrap() == value
