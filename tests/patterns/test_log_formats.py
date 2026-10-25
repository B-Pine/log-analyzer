"""Tests for the LOG_LINE regex pattern itself, independent of the parser."""

import pytest

from log_analyzer.patterns import LOG_LINE

VALID = "2026-10-20 08:15:32 192.168.1.10 GET /home 200"


def test_named_groups_capture_every_field() -> None:
    match = LOG_LINE.match(VALID)
    assert match is not None
    assert match.groupdict() == {
        "timestamp": "2026-10-20 08:15:32",
        "ip": "192.168.1.10",
        "method": "GET",
        "path": "/home",
        "status": "200",
    }


def test_groups_are_always_text() -> None:
    match = LOG_LINE.match(VALID)
    assert match is not None
    assert match["status"] == "200"   # converting to int is the parser's job


@pytest.mark.parametrize(
    "path", ["/", "/home", "/api/v1/orders", "/search?q=shoes&page=2"]
)
def test_accepts_different_paths(path: str) -> None:
    match = LOG_LINE.match(f"2026-10-20 08:15:32 192.168.1.10 GET {path} 200")
    assert match is not None and match["path"] == path


@pytest.mark.parametrize(
    "line",
    [
        "2026-10-20 08:15:32 192.168.1.10 GET /home",          # no status
        "2026-10-20 08:15:32 192.168.1.10 GET /home 2000",     # 4-digit status
        "2026-10-20 08:15:32 192.168.1.10 get /home 200",      # lowercase method
        "2026-10-20 08:15:32 192.168.1.10 GET home 200",       # path without /
        "20-10-2026 08:15:32 192.168.1.10 GET /home 200",      # wrong date order
        "2026-10-20 08:15:32 192.168.1.10 GET /home 200 x",    # trailing junk
        "",
    ],
)
def test_rejects_malformed_lines(line: str) -> None:
    assert LOG_LINE.match(line) is None


def test_anchors_reject_prefixed_lines_even_with_search() -> None:
    prefixed = "LOG: " + VALID
    assert LOG_LINE.match(prefixed) is None
    assert LOG_LINE.search(prefixed) is None   # ^ pins the pattern to the start