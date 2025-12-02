import pytest

from affect import Failure, Success


def test_success_equality_same_value() -> None:
    success1 = Success(value="test")
    success2 = Success(value="test")
    assert success1 == success2


def test_success_equality_different_value() -> None:
    success1 = Success(value="test1")
    success2 = Success(value="test2")
    assert success1 != success2


def test_failure_equality_same_value() -> None:
    failure1 = Failure(value="error")
    failure2 = Failure(value="error")
    assert failure1 == failure2


def test_failure_equality_different_value() -> None:
    failure1 = Failure(value="error1")
    failure2 = Failure(value="error2")
    assert failure1 != failure2


def test_success_not_equal_to_failure() -> None:
    success = Success(value="test")
    failure = Failure(value="test")
    assert success != failure


@pytest.mark.parametrize("value", [42, "test", None, [1, 2, 3]])
def test_success_equality_parametrized(value) -> None:
    success1 = Success(value=value)
    success2 = Success(value=value)
    assert success1 == success2


@pytest.mark.parametrize("value", [404, "error", None])
def test_failure_equality_parametrized(value) -> None:
    failure1 = Failure(value=value)
    failure2 = Failure(value=value)
    assert failure1 == failure2


def test_success_hash_consistency() -> None:
    success1 = Success(value="test")
    success2 = Success(value="test")
    assert hash(success1) == hash(success2)


def test_failure_hash_consistency() -> None:
    failure1 = Failure(value="error")
    failure2 = Failure(value="error")
    assert hash(failure1) == hash(failure2)


def test_success_failure_different_hash() -> None:
    success = Success(value="test")
    failure = Failure(value="test")
    assert hash(success) != hash(failure)


@pytest.mark.parametrize(("value1", "value2"), [(1, 1), ("a", "a"), (None, None)])
def test_success_hash_equality_parametrized(value1, value2) -> None:
    success1 = Success(value=value1)
    success2 = Success(value=value2)
    assert hash(success1) == hash(success2)


def test_success_in_set() -> None:
    success1 = Success(value="test")
    success2 = Success(value="test")
    success_set = {success1}
    assert success2 in success_set


def test_failure_in_set() -> None:
    failure1 = Failure(value="error")
    failure2 = Failure(value="error")
    failure_set = {failure1}
    assert failure2 in failure_set


def test_mixed_results_in_set() -> None:
    success = Success(value="test")
    failure = Failure(value="test")
    result_set = {success, failure}
    assert len(result_set) == 2
    assert success in result_set
    assert failure in result_set
