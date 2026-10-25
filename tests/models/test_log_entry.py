"""Tests for the LogEntry model."""

import dataclasses
from datetime import datetime

import pytest

from log_analyzer.models import LogEntry


def make_entry(status: int) -> LogEntry:
    return LogEntry(datetime(2026, 10, 20, 8), "192.168.1.10", "GET", "/home", status)


@pytest.mark.parametrize(
    ("status", "family"), [(200, "2xx"), (301, "3xx"), (404, "4xx"), (503, "5xx")]
)
def test_status_class(status: int, family: str) -> None:
    assert make_entry(status).status_class == family


@pytest.mark.parametrize(("status", "expected"), [(200, False), (399, False), (400, True), (500, True)])
def test_is_error_starts_at_400(status: int, expected: bool) -> None:
    assert make_entry(status).is_error is expected


def test_is_immutable() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        make_entry(200).status = 500  # type: ignore[misc]