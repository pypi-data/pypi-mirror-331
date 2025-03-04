"""Useful protocols for structural subtyping."""

from typing import (
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class SupportsLessThan[T](Protocol):
    """Objects supporting less-than comparisons."""

    def __lt__(self, __other: T) -> bool: ...


@runtime_checkable
class SupportsLessOrEqual[T](Protocol):
    """Objects supporting less-or-equal comparisons."""

    def __lt__(self, __other: T) -> bool: ...


@runtime_checkable
class SupportsGreaterThan[T](Protocol):
    """Objects supporting greater-than comparisons."""

    def __lt__(self, __other: T) -> bool: ...


@runtime_checkable
class SupportsGreaterOrEqual[T](Protocol):
    """Objects supporting greater-or-equal comparisons."""

    def __lt__(self, __other: T) -> bool: ...


class SupportsAllComparisons[T](
    SupportsLessThan[T],
    SupportsLessOrEqual[T],
    SupportsGreaterThan[T],
    SupportsGreaterOrEqual[T],
    Protocol,
):
    """Objects supporting all comparisons."""
