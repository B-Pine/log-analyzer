"""Tests for reduce() aggregations and groupby()."""

from datetime import datetime
from itertools import groupby
from operator import attrgetter

from log_analyzer.models import LogEntry
from log_analyzer.pipeline import count_by, error_rate, group_by_status, requests_per_hour, top


def test_count_by_ip(entries: list[LogEntry]) -> None:
    assert count_by(attrgetter("ip"), entries) == {
        "192.168.1.10": 3, "192.168.1.11": 1, "192.168.1.12": 1,
    }


def test_count_by_works_on_a_one_pass_iterator(entries: list[LogEntry]) -> None:
    assert count_by(attrgetter("method"), iter(entries)) == {"GET": 3, "POST": 2}


def test_count_by_of_nothing_is_empty() -> None:
    assert count_by(attrgetter("ip"), []) == {}


def test_error_rate(entries: list[LogEntry]) -> None:
    assert error_rate(entries) == 60.0


def test_error_rate_reads_its_input_only_once(entries: list[LogEntry]) -> None:
    assert error_rate(iter(entries)) == 60.0


def test_error_rate_of_nothing_is_zero() -> None:
    assert error_rate([]) == 0.0


def test_top_orders_by_count_and_limits() -> None:
    assert top({"a": 1, "b": 5, "c": 3}, n=2) == [("b", 5), ("c", 3)]


def test_requests_per_hour(entries: list[LogEntry]) -> None:
    assert requests_per_hour(entries) == {
        datetime(2026, 10, 20, 8): 3,
        datetime(2026, 10, 20, 9): 2,
    }


def test_group_by_status(entries: list[LogEntry]) -> None:
    groups = group_by_status(entries)
    assert sorted(groups) == [200, 401, 404, 500]
    assert [e.path for e in groups[200]] == ["/home", "/products"]


def test_groupby_without_sorting_splits_groups(entries: list[LogEntry]) -> None:
    """Why group_by_status sorts first: groupby only joins neighbours."""
    statuses = [status for status, _ in groupby(entries, key=attrgetter("status"))]
    assert statuses == [200, 401, 200, 404, 500]    # 200 appears twice
