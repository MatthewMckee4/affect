import pytest

from affect import Failure, Success, is_err, is_failure, is_ok, is_success


def test_is_ok_success() -> None:
    success_result = Success(value="Test Value")
    assert is_ok(success_result) is True


def test_is_ok_failure() -> None:
    failure_result = Failure(value="Test Error")
    assert is_ok(failure_result) is False


def test_is_err_success() -> None:
    success_result = Success(value="Test Value")
    assert is_err(success_result) is False


def test_is_err_failure() -> None:
    failure_result = Failure(value="Test Error")
    assert is_err(failure_result) is True


def test_is_success_success() -> None:
    success_result = Success(value="Test Value")
    assert is_success(success_result) is True


def test_is_success_failure() -> None:
    failure_result = Failure(value="Test Error")
    assert is_success(failure_result) is False


def test_is_failure_success() -> None:
    success_result = Success(value="Test Value")
    assert is_failure(success_result) is False


def test_is_failure_failure() -> None:
    failure_result = Failure(value="Test Error")
    assert is_failure(failure_result) is True


@pytest.mark.parametrize("value", [42, "test", [1, 2, 3], {"key": "value"}, None])
def test_is_ok_with_various_types(value):
    success_result = Success(value=value)
    assert is_ok(success_result) is True


@pytest.mark.parametrize("value", [42, "error", Exception("test"), None])
def test_is_err_with_various_types(value):
    failure_result = Failure(value=value)
    assert is_err(failure_result) is True


# Test unwrap_or
def test_success_unwrap_or() -> None:
    success = Success(value=42)
    result = success.unwrap_or(0)
    assert result == 42


def test_failure_unwrap_or() -> None:
    failure = Failure(value="error")
    result = failure.unwrap_or(0)
    assert result == 0


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [(42, 0, 42), ("test", "default", "test")],
)
def test_success_unwrap_or_parametrized(value, default, expected) -> None:
    success = Success(value=value)
    result = success.unwrap_or(default)
    assert result == expected


@pytest.mark.parametrize(
    ("error", "default", "expected"),
    [("error", 0, 0), (404, "default", "default")],
)
def test_failure_unwrap_or_parametrized(error, default, expected) -> None:
    failure = Failure(value=error)
    result = failure.unwrap_or(default)
    assert result == expected


# Test unwrap_or_else
def test_success_unwrap_or_else() -> None:
    success = Success(value=42)
    result = success.unwrap_or_else(lambda _: 0)
    assert result == 42


def test_failure_unwrap_or_else() -> None:
    failure = Failure(value="error")
    result = failure.unwrap_or_else(lambda e: f"handled: {e}")
    assert result == "handled: error"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(42, 42), ("test", "test"), ([1, 2, 3], [1, 2, 3])],
)
def test_success_unwrap_or_else_parametrized(value, expected) -> None:
    success = Success(value=value)
    result = success.unwrap_or_else(lambda _: "default")
    assert result == expected


@pytest.mark.parametrize(
    ("error", "func", "expected"),
    [
        ("error", lambda e: f"handled: {e}", "handled: error"),
        (404, lambda e: e * 2, 808),
        ("test", lambda e: e.upper(), "TEST"),
    ],
)
def test_failure_unwrap_or_else_parametrized(error, func, expected) -> None:
    failure = Failure(value=error)
    result = failure.unwrap_or_else(func)
    assert result == expected


# Test or_
def test_success_or() -> None:
    success = Success(value=42)
    other = Success(value=100)
    result = success.or_(other)
    assert result == success
    assert result.unwrap() == 42


def test_failure_or_with_success() -> None:
    failure = Failure(value="error")
    other = Success(value=100)
    result = failure.or_(other)
    assert result == other
    assert result.unwrap() == 100


def test_failure_or_with_failure() -> None:
    failure1 = Failure(value="error1")
    failure2 = Failure(value="error2")
    result = failure1.or_(failure2)
    assert result == failure2
    assert result.unwrap_err() == "error2"


@pytest.mark.parametrize(
    ("first_value", "second_value"),
    [(42, 100), ("test", "other"), ([1, 2], [3, 4])],
)
def test_success_or_parametrized(first_value, second_value) -> None:
    success = Success(value=first_value)
    other = Success(value=second_value)
    result = success.or_(other)
    assert result.unwrap() == first_value


# Test or_else
def test_success_or_else() -> None:
    success = Success(value=42)
    result = success.or_else(lambda _: Success(value=0))
    assert result == success
    assert result.unwrap() == 42


def test_failure_or_else_to_success() -> None:
    failure = Failure(value="error")
    result = failure.or_else(lambda e: Success(value=f"recovered: {e}"))
    assert result.is_ok()
    assert result.unwrap() == "recovered: error"


def test_failure_or_else_to_failure() -> None:
    failure = Failure(value="error")
    result = failure.or_else(lambda e: Failure(value=f"handled: {e}"))
    assert result.is_err()
    assert result.unwrap_err() == "handled: error"


@pytest.mark.parametrize(
    ("error", "recovery_func"),
    [
        ("error", lambda e: Success(value=0)),
        (404, lambda e: Success(value=200)),
        ("fail", lambda e: Failure(value=f"new: {e}")),
    ],
)
def test_failure_or_else_parametrized(error, recovery_func) -> None:
    failure = Failure(value=error)
    result = failure.or_else(recovery_func)
    assert isinstance(result, (Success, Failure))


# Test and_then
def test_success_and_then() -> None:
    success = Success(value=2)
    result = success.and_then(lambda x: Success(value=x * 2))
    assert result.is_ok()
    assert result.unwrap() == 4


def test_success_and_then_to_failure() -> None:
    success = Success(value=-5)
    result = success.and_then(
        lambda x: Failure(value="negative") if x < 0 else Success(value=x),
    )
    assert result.is_err()
    assert result.unwrap_err() == "negative"


def test_failure_and_then() -> None:
    failure = Failure(value="error")
    result = failure.and_then(lambda x: Success(value=x * 2))
    assert result.is_err()
    assert result.unwrap_err() == "error"


@pytest.mark.parametrize(
    ("value", "func", "expected"),
    [
        (2, lambda x: Success(value=x * 2), 4),
        (10, lambda x: Success(value=x + 5), 15),
        ("hello", lambda x: Success(value=x.upper()), "HELLO"),
    ],
)
def test_success_and_then_parametrized(value, func, expected) -> None:
    success = Success(value=value)
    result = success.and_then(func)
    assert result.is_ok()
    assert result.unwrap() == expected


def test_and_then_chain() -> None:
    result = (
        Success(value=2)
        .and_then(lambda x: Success(value=x * 2))
        .and_then(lambda x: Success(value=x + 1))
        .and_then(lambda x: Success(value=str(x)))
    )
    assert result.is_ok()
    assert result.unwrap() == "5"


def test_and_then_chain_with_failure() -> None:
    result = (
        Success(value=2)
        .and_then(lambda x: Success(value=x * 2))
        .and_then(lambda x: Failure(value="error"))
        .and_then(lambda x: Success(value=x + 1))
    )
    assert result.is_err()
    assert result.unwrap_err() == "error"


# Complex integration tests
def test_unwrap_or_with_none() -> None:
    success = Success(value=None)
    result = success.unwrap_or("default")
    assert result is None


def test_chaining_or_else_multiple() -> None:
    result = (
        Failure(value="error1")
        .or_else(lambda _: Failure(value="error2"))
        .or_else(lambda _: Failure(value="error3"))
        .or_else(lambda _: Success(value="finally ok"))
    )
    assert result.is_ok()
    assert result.unwrap() == "finally ok"


def test_combining_and_then_with_or_else() -> None:
    def divide(x: int, y: int) -> Success[int] | Failure[str]:
        if y == 0:
            return Failure(value="division by zero")
        return Success(value=x // y)

    result = (
        divide(10, 2)
        .and_then(lambda x: Success(value=x * 2))
        .or_else(lambda e: Success(value=0))
    )
    assert result.is_ok()
    assert result.unwrap() == 10

    result_with_error = (
        divide(10, 0)
        .and_then(lambda x: Success(value=x * 2))
        .or_else(lambda e: Success(value=0))
    )
    assert result_with_error.is_ok()
    assert result_with_error.unwrap() == 0


@pytest.mark.parametrize(
    ("operations", "expected_result"),
    [
        ([lambda x: Success(value=x * 2), lambda x: Success(value=x + 1)], 5),
        (
            [
                lambda x: Success(value=x * 2),
                lambda x: Success(value=x + 1),
                lambda x: Success(value=x * 3),
            ],
            15,
        ),
    ],
)
def test_and_then_chain_parametrized(operations, expected_result: int) -> None:
    result = Success(value=2)
    for op in operations:
        result = result.and_then(op)
    assert result.is_ok()
    assert result.unwrap() == expected_result


def test_unwrap_or_else_not_called_on_success() -> None:
    call_count = []

    def track_call(e):
        call_count.append(e)
        return "default"

    success = Success(value=42)
    result = success.unwrap_or_else(track_call)
    assert result == 42
    assert len(call_count) == 0


def test_unwrap_or_else_called_on_failure() -> None:
    call_count = []

    def track_call(e):
        call_count.append(e)
        return "default"

    failure = Failure(value="error")
    result = failure.unwrap_or_else(track_call)
    assert result == "default"
    assert len(call_count) == 1
    assert call_count[0] == "error"
