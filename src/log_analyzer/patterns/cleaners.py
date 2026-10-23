"""Cleaning raw text with re.sub()."""

import re

_WHITESPACE: re.Pattern[str] = re.compile(r"\s+")


def clean_line(line: str) -> str:
    """Collapse runs of spaces or tabs into one space and trim the ends.

    Example:
        >>> clean_line("  192.168.1.10   GET\\t/home  200 ")
        '192.168.1.10 GET /home 200'
    """
    return _WHITESPACE.sub(" ", line).strip()
