"""Splitting a stream into batches and pages."""

from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Generic, TypeVar

T = TypeVar("T")


class Batcher(Generic[T]):
    """Iterator that yields items in lists of a fixed size.

    The last batch may be smaller. Works on any iterable, including
    generators, without loading everything into memory.

    Example:
        >>> list(Batcher(range(7), size=3))
        [[0, 1, 2], [3, 4, 5], [6]]
    """

    def __init__(self, items: Iterable[T], size: int) -> None:
        if size < 1:
            raise ValueError(f"size must be at least 1, got {size}")
        self._items: Iterator[T] = iter(items)
        self._size = size

    def __iter__(self) -> "Batcher[T]":
        return self

    def __next__(self) -> list[T]:
        batch = list(islice(self._items, self._size))
        if not batch:
            raise StopIteration
        return batch


def paginate(items: Iterable[T], page: int, size: int = 20) -> list[T]:
    """Return one page of items, counting pages from 1.

    islice skips the earlier items without storing them and stops right
    after the page, so the rest of the input is never read.

    Example:
        >>> paginate(range(100), page=3, size=10)
        [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
    """
    if page < 1 or size < 1:
        raise ValueError("page and size must be at least 1")
    start = (page - 1) * size
    return list(islice(items, start, start + size))
