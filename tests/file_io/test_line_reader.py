"""Tests for the generator-based file reading."""

import inspect
import tracemalloc
from collections.abc import Callable
from pathlib import Path

import pytest

from log_analyzer.exceptions import LogFileError
from log_analyzer.file_io import read_lines, read_many


def test_yields_every_line(write_log: Callable[..., Path], lines: list[str]) -> None:
    assert [line.rstrip("\n") for line in read_lines(write_log(lines))] == lines


def test_is_a_generator(write_log: Callable[..., Path], lines: list[str]) -> None:
    assert inspect.isgenerator(read_lines(write_log(lines)))


def test_missing_file_fails_only_when_reading_starts(tmp_path: Path) -> None:
    reader = read_lines(tmp_path / "missing.log")     # no error yet: nothing has run
    with pytest.raises(LogFileError, match="File not found"):
        next(reader)


def test_invalid_bytes_are_replaced_not_fatal(tmp_path: Path) -> None:
    path = tmp_path / "broken.log"
    path.write_bytes(b"good line\n\xff\xfe bad bytes\n")
    assert len(list(read_lines(path))) == 2


def test_read_many_chains_files_in_order(write_log: Callable[..., Path]) -> None:
    first = write_log(["a", "b"], name="first.log")
    second = write_log(["c"], name="second.log")
    assert [line.strip() for line in read_many([first, second])] == ["a", "b", "c"]


def test_generator_uses_far_less_memory_than_a_list(write_log: Callable[..., Path]) -> None:
    path = write_log([f"2026-10-20 08:00:00 192.168.1.10 GET /line/{n} 200" for n in range(20_000)])

    tracemalloc.start()
    for _ in read_lines(path):
        pass
    _, generator_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    tracemalloc.start()
    all_lines = path.read_text(encoding="utf-8").splitlines()
    _, list_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del all_lines

    assert generator_peak * 10 < list_peak
