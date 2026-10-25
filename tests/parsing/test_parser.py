"""Tests for turning raw lines into LogEntry objects."""

from datetime import datetime

import pytest

from log_analyzer.parsing import parse_line


def test_parses_a_valid_line_into_typed_fields() -> None:
    entry = parse_line("2026-10-20 08:15:32 192.168.1.10 GET /home 200")
    assert entry is not None
    assert entry.timestamp == datetime(2026, 10, 20, 8, 15, 32)
    assert (entry.ip, entry.method, entry.path, entry.status) == (
        "192.168.1.10", "GET", "/home", 200,
    )


def test_messy_spacing_and_newline_are_cleaned_first() -> None:
    entry = parse_line("2026-10-20 08:15:32  192.168.1.10\tGET   /home 200\n")
    assert entry is not None and entry.path == "/home"


@pytest.mark.parametrize(
    "line",
    [
        "this line is garbage",
        "2026-10-20 08:15:32 192.168.1.10 GET /home",           # missing status
        "2026-10-20 08:15:32 999.168.1.10 GET /home 200",       # right shape, invalid IP
        "2026-13-45 08:15:32 192.168.1.10 GET /home 200",       # right shape, impossible date
        "",
    ],
)
def test_malformed_lines_return_none(line: str) -> None:
    assert parse_line(line) is None