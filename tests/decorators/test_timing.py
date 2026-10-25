"""Tests for the @timer decorator."""

import logging

import pytest

from log_analyzer.decorators import timer


@timer
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@timer
def explode() -> None:
    raise RuntimeError("boom")


def test_returns_the_original_result() -> None:
    assert add(2, 3) == 5


def test_keeps_name_and_docstring() -> None:
    assert add.__name__ == "add"
    assert add.__doc__ == "Add two numbers."


def test_logs_the_duration(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="log_analyzer"):
        add(1, 1)
    assert "add took" in caplog.text
    assert "ms" in caplog.text


def test_logs_even_when_the_function_fails(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="log_analyzer"), pytest.raises(RuntimeError):
        explode()
    assert "explode took" in caplog.text
