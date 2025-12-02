import karva
import pytest

from affect import as_async_result, as_result


@karva.tags.parametrize(("a", "b", "expected"), [(10, 2, 5), (20, 4, 5), (100, 10, 10)])
def test_as_result_success_parametrized(a: int, b: int, expected: int) -> None:
    @as_result()
    def divide(x: int, y: int) -> int:
        return x // y

    result = divide(a, b)
    assert result.is_ok()
    assert result.unwrap() == expected


def test_as_result_no_exception_specified() -> None:
    @as_result()
    def may_fail(value: int) -> int:
        if value < 0:
            raise ValueError("Negative value")
        return value * 2

    success_result = may_fail(5)
    assert success_result.is_ok()
    assert success_result.unwrap() == 10

    failure_result = may_fail(-5)
    assert failure_result.is_err()
    assert isinstance(failure_result.unwrap_err(), ValueError)


def test_as_result_specific_exception() -> None:
    @as_result(ValueError)
    def parse_int(value: str) -> int:
        if not value.isdigit():
            raise ValueError("Not a number")
        return int(value)

    success_result = parse_int("42")
    assert success_result.is_ok()
    assert success_result.unwrap() == 42

    failure_result = parse_int("abc")
    assert failure_result.is_err()
    assert isinstance(failure_result.unwrap_err(), ValueError)


def test_as_result_multiple_exceptions() -> None:
    @as_result(ValueError, TypeError, KeyError)
    def risky_operation(data: dict, key: str) -> int:
        value = data[key]
        if not isinstance(value, str):
            raise TypeError("Value must be string")
        if not value.isdigit():
            raise ValueError("Value must be numeric string")
        return int(value)

    success_result = risky_operation({"key": "42"}, "key")
    assert success_result.is_ok()
    assert success_result.unwrap() == 42

    key_error_result = risky_operation({}, "missing")
    assert key_error_result.is_err()
    assert isinstance(key_error_result.unwrap_err(), KeyError)

    type_error_result = risky_operation({"key": 42}, "key")
    assert type_error_result.is_err()
    assert isinstance(type_error_result.unwrap_err(), TypeError)

    value_error_result = risky_operation({"key": "abc"}, "key")
    assert value_error_result.is_err()
    assert isinstance(value_error_result.unwrap_err(), ValueError)


def test_as_result_does_not_catch_unlisted_exception() -> None:
    @as_result(ValueError)
    def may_raise_type_error(value: str) -> int:
        if not value.isdigit():
            raise TypeError("Not a valid number")
        return int(value)

    with pytest.raises(TypeError):
        may_raise_type_error("not_a_number")


def test_as_result_preserves_function_name() -> None:
    @as_result()
    def my_function() -> int:
        return 42

    assert my_function.__name__ == "my_function"


def test_as_result_preserves_docstring() -> None:
    @as_result()
    def documented_function() -> int:
        """This is a docstring."""
        return 42

    assert documented_function.__doc__ == "This is a docstring."


def test_as_result_with_kwargs() -> None:
    @as_result()
    def greet(name: str, greeting: str = "Hello") -> str:
        if not name:
            raise ValueError("Name cannot be empty")
        return f"{greeting}, {name}!"

    result1 = greet("Alice")
    assert result1.is_ok()
    assert result1.unwrap() == "Hello, Alice!"

    result2 = greet("Bob", greeting="Hi")
    assert result2.is_ok()
    assert result2.unwrap() == "Hi, Bob!"

    result3 = greet("")
    assert result3.is_err()


def test_as_result_with_args_and_kwargs() -> None:
    @as_result()
    def combine(*args: int, multiplier: int = 1) -> int:
        if not args:
            raise ValueError("Need at least one argument")
        return sum(args) * multiplier

    result1 = combine(1, 2, 3)
    assert result1.is_ok()
    assert result1.unwrap() == 6

    result2 = combine(1, 2, 3, multiplier=2)
    assert result2.is_ok()
    assert result2.unwrap() == 12

    result3 = combine()
    assert result3.is_err()


@karva.tags.parametrize(
    ("a", "b", "expected"),
    [(10, 2, 5.0), (20, 4, 5.0), (15, 3, 5.0)],
)
async def test_as_async_result_success_parametrized(
    a: float,
    b: float,
    expected: float,
) -> None:
    @as_async_result()
    async def async_divide(x: float, y: float) -> float:
        return x / y

    result = await async_divide(a, b)
    assert result.is_ok()
    assert result.unwrap() == expected


async def test_as_async_result_no_exception_specified() -> None:
    @as_async_result()
    async def async_may_fail(value: int) -> int:
        if value < 0:
            raise ValueError("Negative value")
        return value * 2

    success_result = await async_may_fail(5)
    assert success_result.is_ok()
    assert success_result.unwrap() == 10

    failure_result = await async_may_fail(-5)
    assert failure_result.is_err()
    assert isinstance(failure_result.unwrap_err(), ValueError)


async def test_as_async_result_specific_exception() -> None:
    @as_async_result(ValueError)
    async def async_parse_int(value: str) -> int:
        if not value.isdigit():
            raise ValueError("Not a number")
        return int(value)

    success_result = await async_parse_int("42")
    assert success_result.is_ok()
    assert success_result.unwrap() == 42

    failure_result = await async_parse_int("abc")
    assert failure_result.is_err()
    assert isinstance(failure_result.unwrap_err(), ValueError)


async def test_as_async_result_multiple_exceptions() -> None:
    @as_async_result(ValueError, TypeError, KeyError)
    async def async_risky_operation(data: dict, key: str) -> int:
        value = data[key]
        if not isinstance(value, str):
            raise TypeError("Value must be string")
        if not value.isdigit():
            raise ValueError("Value must be numeric string")
        return int(value)

    success_result = await async_risky_operation({"key": "42"}, "key")
    assert success_result.is_ok()
    assert success_result.unwrap() == 42

    key_error_result = await async_risky_operation({}, "missing")
    assert key_error_result.is_err()
    assert isinstance(key_error_result.unwrap_err(), KeyError)


async def test_as_async_result_preserves_function_name() -> None:
    @as_async_result()
    async def my_async_function() -> int:
        return 42

    assert my_async_function.__name__ == "my_async_function"


async def test_as_async_result_preserves_docstring() -> None:
    @as_async_result()
    async def documented_async_function() -> int:
        """This is an async docstring."""
        return 42

    assert documented_async_function.__doc__ == "This is an async docstring."


async def test_as_async_result_with_kwargs() -> None:
    @as_async_result()
    async def async_greet(name: str, greeting: str = "Hello") -> str:
        if not name:
            raise ValueError("Name cannot be empty")
        return f"{greeting}, {name}!"

    result1 = await async_greet("Alice")
    assert result1.is_ok()
    assert result1.unwrap() == "Hello, Alice!"

    result2 = await async_greet("Bob", greeting="Hi")
    assert result2.is_ok()
    assert result2.unwrap() == "Hi, Bob!"

    result3 = await async_greet("")
    assert result3.is_err()


def test_as_result_with_none_return() -> None:
    @as_result()
    def returns_none() -> None:
        pass

    result = returns_none()
    assert result.is_ok()
    assert result.unwrap() is None


async def test_as_async_result_with_none_return() -> None:
    @as_async_result()
    async def async_returns_none() -> None:
        pass

    result = await async_returns_none()
    assert result.is_ok()
    assert result.unwrap() is None


def test_as_result_with_complex_return_type() -> None:
    @as_result()
    def get_user_data() -> dict[str, any]:
        return {"id": 1, "name": "Alice", "roles": ["admin", "user"]}

    result = get_user_data()
    assert result.is_ok()
    data = result.unwrap()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert len(data["roles"]) == 2


async def test_as_async_result_with_complex_return_type() -> None:
    @as_async_result()
    async def async_get_user_data() -> dict[str, any]:
        return {"id": 1, "name": "Alice", "roles": ["admin", "user"]}

    result = await async_get_user_data()
    assert result.is_ok()
    data = result.unwrap()
    assert data["id"] == 1
    assert data["name"] == "Alice"
    assert len(data["roles"]) == 2


@karva.tags.parametrize("exception_type", [ValueError, TypeError, RuntimeError])
def test_as_result_parametrized_exception_types(exception_type) -> None:
    @as_result(exception_type)
    def may_raise(should_fail: bool):
        if should_fail:
            raise exception_type("Test error")
        return "success"

    success_result = may_raise(False)
    assert success_result.is_ok()

    failure_result = may_raise(True)
    assert failure_result.is_err()
    assert isinstance(failure_result.unwrap_err(), exception_type)


def test_as_result_nested_decorators() -> None:
    @as_result(ValueError)
    def inner_function(value: int) -> int:
        if value < 0:
            raise ValueError("Negative value")
        return value * 2

    @as_result(TypeError)
    def outer_function(value: str) -> int:
        if not value.isdigit():
            raise TypeError("Not a digit")
        result = inner_function(int(value))
        if result.is_err():
            raise ValueError(result.unwrap_err())
        return result.unwrap()

    success = outer_function("10")
    assert success.is_ok()
    assert success.unwrap() == 20

    type_error = outer_function("abc")
    assert type_error.is_err()
    assert isinstance(type_error.unwrap_err(), TypeError)


def test_as_result_with_class_method() -> None:
    class Calculator:
        @as_result(ZeroDivisionError)
        def divide(self, a: float, b: float) -> float:
            if b == 0:
                raise ZeroDivisionError("Division by zero")
            return a / b

    calc = Calculator()
    success = calc.divide(10, 2)
    assert success.is_ok()
    assert success.unwrap() == 5.0

    failure = calc.divide(10, 0)
    assert failure.is_err()
    assert isinstance(failure.unwrap_err(), ZeroDivisionError)


def test_as_result_with_static_method() -> None:
    class MathUtils:
        @staticmethod
        @as_result(ValueError)
        def square_root(value: float) -> float:
            if value < 0:
                raise ValueError("Cannot take square root of negative number")
            return value**0.5

    success = MathUtils.square_root(16)
    assert success.is_ok()
    assert success.unwrap() == 4.0

    failure = MathUtils.square_root(-1)
    assert failure.is_err()
    assert isinstance(failure.unwrap_err(), ValueError)
