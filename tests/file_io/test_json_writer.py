"""Tests for writing reports as JSON."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from log_analyzer.exceptions import LogFileError
from log_analyzer.file_io import write_report
from log_analyzer.reports import build_summary


def test_round_trip(write_log: Callable[..., Path], lines: list[str], tmp_path: Path) -> None:
    report = build_summary([write_log(lines)])
    path = write_report(report, tmp_path / "out" / "summary.json")
    assert json.loads(path.read_text(encoding="utf-8")) == report


def test_unwritable_location(write_log: Callable[..., Path], lines: list[str], tmp_path: Path) -> None:
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("I am a file")
    with pytest.raises(LogFileError):
        write_report(build_summary([write_log(lines)]), blocker / "summary.json")
