"""Shared fixtures for the whole test suite."""

from collections.abc import Callable
from pathlib import Path

import pytest

from log_analyzer.models import LogEntry
from log_analyzer.pipeline import parse_lines

SAMPLE_LINES = [
    "2026-10-20 08:00:00 192.168.1.10 GET /home 200",
    "2026-10-20 08:20:00 192.168.1.11 POST /login 401",
    "2026-10-20 08:40:00 192.168.1.10 GET /products 200",
    "2026-10-20 09:05:00 192.168.1.12 GET /missing 404",
    "2026-10-20 09:30:00 192.168.1.10 POST /checkout 500",
    "this line is garbage",
]


@pytest.fixture
def lines() -> list[str]:
    """Five valid lines in time order, then one malformed line.

    192.168.1.10 makes 3 requests | 3 errors (401, 404, 500) out of 5
    08:00 hour: 3 requests | 09:00 hour: 2 requests
    """
    return list(SAMPLE_LINES)


@pytest.fixture
def entries(lines: list[str]) -> list[LogEntry]:
    """The five parsed entries from `lines`, as a reusable list."""
    return list(parse_lines(lines))


@pytest.fixture
def write_log(tmp_path: Path) -> Callable[..., Path]:
    """Factory that writes lines to a log file in a temporary folder."""
    def _write(lines: list[str], name: str = "access.log") -> Path:
        path = tmp_path / name
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    return _write