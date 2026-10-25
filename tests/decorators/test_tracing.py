"""Tests for @log_call and for chaining decorators."""

import logging

import pytest

from log_analyzer.decorators import log_call, timer


@log_call
def greet(name: str, punctuation: str = "!") -> str:
    return f"hi {name}{punctuation}"


@timer
@log_call
def double(n: int) -> int:
    return n * 2


def test_logs_arguments_and_result(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="log_analyzer"):
        greet("Aline", punctuation="?")
    assert "calling greet('Aline', punctuation='?')" in caplog.text
    assert "greet returned 'hi Aline?'" in caplog.text


def test_long_arguments_are_shortened(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="log_analyzer"):
        greet("x" * 1000)
    assert "x" * 1000 not in caplog.text
    assert "..." in caplog.text


def test_chained_decorators_run_inside_out(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="log_analyzer"):
        assert double(21) == 42
    messages = [record.getMessage() for record in caplog.records]
    assert messages[0].startswith("calling double")     # log_call, the inner decorator
    assert messages[-1].startswith("double took")       # timer, the outer decorator