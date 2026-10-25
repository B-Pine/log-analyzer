"""Transformations with map(): raw lines → LogEntry → dictionaries."""

from collections.abc import Iterable, Iterator

from ..models import LogEntry
from ..parsing import parse_line

LogDict = dict[str, str | int]


def parse_lines(lines: Iterable[str]) -> Iterator[LogEntry]:
    """Parse every line, silently dropping malformed ones.

    map() applies parse_line to each line, giving LogEntry or None;
    filter(None, ...) then keeps only the entries.

    Example:
        >>> lines = ["2026-10-20 08:15:32 192.168.1.10 GET /home 200", "garbage"]
        >>> [entry.path for entry in parse_lines(lines)]
        ['/home']
    """
    return filter(None, map(parse_line, lines))


def to_dict(entry: LogEntry) -> LogDict:
    """Convert one entry to a JSON-ready dictionary.

    Example:
        >>> from log_analyzer.parsing import parse_line
        >>> to_dict(parse_line("2026-10-20 08:15:32 192.168.1.10 GET /home 200"))
        {'timestamp': '2026-10-20T08:15:32', 'ip': '192.168.1.10', 'method': 'GET', 'path': '/home', 'status': 200}
    """
    return {
        "timestamp": entry.timestamp.isoformat(),
        "ip": entry.ip,
        "method": entry.method,
        "path": entry.path,
        "status": entry.status,
    }


def to_dicts(entries: Iterable[LogEntry]) -> Iterator[LogDict]:
    """Convert every entry to a dictionary with map()."""
    return map(to_dict, entries)
