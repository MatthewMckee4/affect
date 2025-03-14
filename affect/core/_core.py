"""Core module for affect."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Generic, Literal, Self, TypeAlias

from pydantic.dataclasses import dataclass
from typing_extensions import TypeIs

from affect.typings import FailureT, O, SuccessT, T, U

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


@dataclass(frozen=True)
class _ResultBase(Generic[T], ABC):
    """Base class for results."""

    value: T

    @abstractmethod
    def is_ok(self) -> bool:
        """Check if the result is ok."""

    def is_ok_and(self, predicate: Callable[[T], bool]) -> bool:
        return self.is_ok() and predicate(self.value)

    @abstractmethod
    def is_err(self) -> bool:
        """Check if the result is an error."""

    def is_err_and(self, predicate: Callable[[T], bool]) -> bool:
        return self.is_err() and predicate(self.value)

    @abstractmethod
    def ok(self) -> T | None:
        """Get the value if it's ok, otherwise return None."""

    @abstractmethod
    def err(self) -> T | None:
        """Get the error if it's an error, otherwise return None."""

    @abstractmethod
    def map(self, func: Callable[[T], SuccessT], /) -> Result[SuccessT, T]:
        """Map the result to a new type."""

    @abstractmethod
    def map_or(self, default: U, func: Callable[[T], U], /) -> U:
        """Map the result to a new type."""

    @abstractmethod
    def map_or_else(self, default: Callable[[T], U], func: Callable[[T], U], /) -> U:
        """Map the result to a new type."""

    @abstractmethod
    def map_err(self, func: Callable[[T], SuccessT], /) -> Result[T, SuccessT]:
        """Map the result to a new type."""

    @abstractmethod
    def inspect(self, func: Callable[[T], Any], /) -> Self:
        """Inspect the result."""

    @abstractmethod
    def inspect_err(self, func: Callable[[T], Any], /) -> Self:
        """Inspect the result."""

    @abstractmethod
    def iter(self) -> Iterator[T | None]:
        """Iterate over the result."""

    def __iter__(self) -> Iterator[T | None]:
        """Iterate over the result."""
        yield from self.iter()

    def __hash__(self) -> int:
        """Hash the result."""
        return hash((self.is_ok(), self.value))


class Success(_ResultBase[SuccessT]):
    """A successful result."""

    def is_ok(self) -> Literal[True]:
        """Check if the success is ok."""
        return True

    def is_err(self) -> Literal[False]:
        """Check if the success is an error."""
        return False

    def ok(self) -> SuccessT:
        """Get the value if it's ok, otherwise return None."""
        return self.value

    def err(self) -> None:
        """Get the error if it's an error, otherwise return None."""
        return

    def map(self, func: Callable[[SuccessT], T], /) -> Success[T]:
        """Map the result to a new type."""
        return Success(value=func(self.value))

    def map_or(self, _default: Any, func: Callable[[SuccessT], U], /) -> U:
        """Map the result to a new type."""
        return func(self.value)

    def map_or_else(
        self,
        _default: Callable[[Any], U],
        func: Callable[[SuccessT], U],
        /,
    ) -> U:
        """Map the result to a new type."""
        return func(self.value)

    def map_err(self, _func: Callable[[Any], Any], /) -> Self:
        """Map the result to a new type."""
        return self

    def inspect(self, func: Callable[[SuccessT], Any], /) -> Self:
        """Inspect the result."""
        func(self.value)
        return self

    def inspect_err(self, _func: Callable[[Any], Any], /) -> Self:
        """Inspect the result."""
        return self

    def iter(self) -> Iterator[SuccessT]:
        """Iterate over the result."""
        yield self.value


class Failure(_ResultBase[FailureT]):
    """A failed result."""

    def is_ok(self) -> Literal[False]:
        """Check if the failure is ok."""
        return False

    def is_err(self) -> Literal[True]:
        """Check if the failure is an error."""
        return True

    def ok(self) -> None:
        """Get the value if it's ok, otherwise return None."""
        return

    def err(self) -> FailureT:
        """Get the error if it's an error, otherwise return None."""
        return self.value

    def map(self, _func: Callable[[Any], Any], /) -> Self:
        """Map the result to a new type."""
        return self

    def map_or(self, default: U, _func: Callable[[Any], Any], /) -> U:
        """Map the result to a new type."""
        return default

    def map_or_else(
        self,
        default: Callable[[FailureT], U],
        _func: Callable[[Any], U],
        /,
    ) -> U:
        """Map the result to a new type."""
        return default(self.value)

    def map_err(self, func: Callable[[FailureT], O], /) -> Failure[O]:
        """Map the result to a new type."""
        return Failure(value=func(self.value))

    def inspect(self, _func: Callable[[Any], Any], /) -> Self:
        """Inspect the result."""
        return self

    def inspect_err(self, func: Callable[[FailureT], Any], /) -> Self:
        """Inspect the result."""
        func(self.value)
        return self

    def iter(self) -> Iterator[None]:
        """Iterate over the result."""
        yield None


Result: TypeAlias = Success[SuccessT] | Failure[FailureT]


def is_ok(result: Result[SuccessT, FailureT]) -> TypeIs[Success[SuccessT]]:
    """Check if the result is ok."""
    return isinstance(result, Success)


def is_err(result: Result[SuccessT, FailureT]) -> TypeIs[Failure[FailureT]]:
    """Check if the result is an error."""
    return isinstance(result, Failure)
