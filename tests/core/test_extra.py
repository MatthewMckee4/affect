from affect import as_result


@as_result()
def divide(a: float, b: float) -> float:
    return a / b


def test_divide_success() -> None:
    result = divide(10, 2)
    assert result.is_ok()
    assert result.unwrap() == 5.0


def test_divide_by_zero() -> None:
    result = divide(10, 0)
    assert result.is_err()
    assert isinstance(result.unwrap_err(), Exception)


def test_divide_with_non_number() -> None:
    @as_result(TypeError)
    def divide(a: float, b: float) -> float:
        return a / b

    result = divide(10, "a")  # type: ignore[arg-type]
    assert result.is_err() is True
    assert isinstance(result.unwrap_err(), TypeError)


def test_divide_with_multiple_exceptions() -> None:
    @as_result(ZeroDivisionError, TypeError)
    def safe_divide(a: float, b: float) -> float:
        return a / b

    result = safe_divide(10, 0)
    assert result.is_err() is True
    assert isinstance(result.unwrap_err(), ZeroDivisionError)
