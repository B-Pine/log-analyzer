"""Tests for the Batcher iterator and islice pagination."""

from itertools import count

import pytest

from log_analyzer.file_io import Batcher, paginate


def test_splits_into_fixed_size_batches() -> None:
    assert list(Batcher(range(7), size=3)) == [[0, 1, 2], [3, 4, 5], [6]]


def test_exact_multiple_has_no_empty_last_batch() -> None:
    assert list(Batcher(range(6), size=3)) == [[0, 1, 2], [3, 4, 5]]


def test_empty_input_gives_no_batches() -> None:
    assert list(Batcher([], size=3)) == []


def test_follows_the_iterator_protocol() -> None:
    batcher = Batcher("abcde", size=2)
    assert iter(batcher) is batcher
    assert next(batcher) == ["a", "b"]
    assert next(batcher) == ["c", "d"]
    assert next(batcher) == ["e"]
    with pytest.raises(StopIteration):
        next(batcher)


def test_works_on_endless_streams() -> None:
    batcher = Batcher(count(), size=2)
    assert next(batcher) == [0, 1]
    assert next(batcher) == [2, 3]


@pytest.mark.parametrize("size", [0, -1])
def test_rejects_invalid_size(size: int) -> None:
    with pytest.raises(ValueError):
        Batcher(range(3), size=size)


def test_paginate() -> None:
    assert paginate(range(10), page=1, size=4) == [0, 1, 2, 3]
    assert paginate(range(10), page=3, size=4) == [8, 9]
    assert paginate(range(10), page=4, size=4) == []


def test_paginate_never_reads_past_the_page() -> None:
    assert paginate(count(), page=1000, size=5) == [4995, 4996, 4997, 4998, 4999]


@pytest.mark.parametrize(("page", "size"), [(0, 5), (1, 0)])
def test_paginate_rejects_invalid_arguments(page: int, size: int) -> None:
    with pytest.raises(ValueError):
        paginate(range(10), page=page, size=size)