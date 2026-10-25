"""Tests for re.sub()-based cleaning."""

import pytest

from log_analyzer.patterns import clean_line


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a  b", "a b"),
        ("a\tb", "a b"),
        ("  a b  ", "a b"),
        ("a \t  b\n", "a b"),
        ("a b", "a b"),
        ("", ""),
    ],
)
def test_clean_line(raw: str, expected: str) -> None:
    assert clean_line(raw) == expected