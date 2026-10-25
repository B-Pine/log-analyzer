"""Tests for the map() stage."""

from collections.abc import Iterator

from log_analyzer.models import LogEntry
from log_analyzer.pipeline import parse_lines, to_dict, to_dicts


def test_parse_lines_drops_malformed_lines(lines: list[str]) -> None:
    assert len(list(parse_lines(lines))) == 5


def test_parse_lines_is_lazy(lines: list[str]) -> None:
    result = parse_lines(lines)
    assert isinstance(result, Iterator)
    assert not isinstance(result, list)


def test_an_iterator_can_only_be_read_once(lines: list[str]) -> None:
    result = parse_lines(lines)
    assert len(list(result)) == 5
    assert list(result) == []


def test_to_dict_is_json_ready(entries: list[LogEntry]) -> None:
    assert to_dict(entries[0]) == {
        "timestamp": "2026-10-20T08:00:00",
        "ip": "192.168.1.10",
        "method": "GET",
        "path": "/home",
        "status": 200,
    }


def test_to_dicts_converts_every_entry(entries: list[LogEntry]) -> None:
    assert [d["status"] for d in to_dicts(entries)] == [200, 401, 200, 404, 500]