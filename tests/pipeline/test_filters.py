"""Tests for the filter() stage, partial() filters and takewhile()."""

from collections.abc import Iterable, Iterator
from datetime import datetime
from functools import partial
from itertools import count

from log_analyzer.models import LogEntry
from log_analyzer.pipeline import (
    between,
    in_time_range,
    is_client_error,
    is_error,
    is_get,
    is_not_found,
    is_post,
    is_server_error,
    is_unauthorized,
    select,
    until,
)


def paths(entries: Iterable[LogEntry]) -> list[str]:
    return [entry.path for entry in entries]


def test_is_error(entries: list[LogEntry]) -> None:
    assert paths(filter(is_error, entries)) == ["/login", "/missing", "/checkout"]


def test_partial_filters(entries: list[LogEntry]) -> None:
    assert paths(filter(is_not_found, entries)) == ["/missing"]
    assert paths(filter(is_unauthorized, entries)) == ["/login"]
    assert paths(filter(is_client_error, entries)) == ["/login", "/missing"]
    assert paths(filter(is_server_error, entries)) == ["/checkout"]
    assert paths(filter(is_get, entries)) == ["/home", "/products", "/missing"]


def test_partial_keeps_the_original_function_and_arguments() -> None:
    assert is_post.args == ("POST",)


def test_select_combines_predicates_with_and(entries: list[LogEntry]) -> None:
    assert paths(select(entries, is_post, is_error)) == ["/login", "/checkout"]


def test_select_without_predicates_keeps_everything(entries: list[LogEntry]) -> None:
    assert len(list(select(entries))) == 5


def test_time_range_is_half_open(entries: list[LogEntry]) -> None:
    eight_to_nine = partial(in_time_range, datetime(2026, 10, 20, 8), datetime(2026, 10, 20, 9))
    nine_to_ten = partial(in_time_range, datetime(2026, 10, 20, 9), datetime(2026, 10, 20, 10))
    assert len(list(filter(eight_to_nine, entries))) == 3
    assert len(list(filter(nine_to_ten, entries))) == 2


def test_between_matches_filter_on_sorted_entries(entries: list[LogEntry]) -> None:
    start, end = datetime(2026, 10, 20, 8, 10), datetime(2026, 10, 20, 9, 10)
    in_range = partial(in_time_range, start, end)
    assert list(between(start, end, entries)) == list(filter(in_range, entries))


def test_until_stops_reading_at_the_first_late_entry(entries: list[LogEntry]) -> None:
    consumed = 0

    def counting() -> Iterator[LogEntry]:
        nonlocal consumed
        for entry in entries:
            consumed += 1
            yield entry

    result = list(until(datetime(2026, 10, 20, 8, 30), counting()))
    assert len(result) == 2
    assert consumed == 3      # read the first late entry, then stopped


def test_until_works_on_endless_streams() -> None:
    endless = (LogEntry(datetime(2026, 10, 20, 8, n % 60), "1.1.1.1", "GET", "/", 200)
               for n in count())
    assert len(list(until(datetime(2026, 10, 20, 8, 5), endless))) == 5
