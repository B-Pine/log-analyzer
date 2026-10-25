"""Aggregations with functools.reduce()."""

from collections.abc import Callable, Hashable, Iterable
from datetime import datetime
from functools import reduce
from itertools import groupby
from operator import attrgetter
from typing import TypeVar

from ..decorators import timer, log_call
from ..models import LogEntry

K = TypeVar("K", bound=Hashable)


def _increment(counts: dict[K, int], key: K) -> dict[K, int]:
    """Reducer step: add one to the count for key."""
    counts[key] = counts.get(key, 0) + 1
    return counts

@timer
@log_call
def count_by(key: Callable[[LogEntry], K], entries: Iterable[LogEntry]) -> dict[K, int]:
    """Count entries per key, e.g. per IP or per status code.

    map() extracts the key from each entry, and reduce() folds the keys
    into one dictionary of counts.

    Example:
        >>> from operator import attrgetter
        >>> from log_analyzer.pipeline.transforms import parse_lines
        >>> lines = [
        ...     "2026-10-20 08:00:00 192.168.1.10 GET /home 200",
        ...     "2026-10-20 08:01:00 192.168.1.10 GET /cart 200",
        ...     "2026-10-20 08:02:00 192.168.1.12 GET /missing 404",
        ... ]
        >>> count_by(attrgetter("ip"), parse_lines(lines))
        {'192.168.1.10': 2, '192.168.1.12': 1}
    """
    return reduce(_increment, map(key, entries), {})


def _tally(totals: tuple[int, int], entry: LogEntry) -> tuple[int, int]:
    """Reducer step: count one more request, and one more error if it failed."""
    requests, errors = totals
    return requests + 1, errors + entry.is_error


@timer
@log_call
def error_rate(entries: Iterable[LogEntry]) -> float:
    """Percentage of requests that ended in a 4xx or 5xx error.

    Counts requests and errors together in a single pass, so it also
    works on iterators, which can only be read once.

    Example:
        >>> from log_analyzer.pipeline.transforms import parse_lines
        >>> lines = [
        ...     "2026-10-20 08:00:00 192.168.1.10 GET /home 200",
        ...     "2026-10-20 08:01:00 192.168.1.11 GET /missing 404",
        ... ]
        >>> error_rate(parse_lines(lines))
        50.0
    """
    requests, errors = reduce(_tally, entries, (0, 0))
    return errors / requests * 100 if requests else 0.0


def top(counts: dict[K, int], n: int = 5) -> list[tuple[K, int]]:
    """The n keys with the highest counts, highest first.

    Example:
        >>> top({"/home": 5, "/cart": 9, "/login": 2}, n=2)
        [('/cart', 9), ('/home', 5)]
    """
    return sorted(counts.items(), key=lambda item: item[1], reverse=True)[:n]


def _hour_of(entry: LogEntry) -> datetime:
    """The start of the hour the entry falls in, e.g. 08:00 for 08:15:32."""
    return entry.timestamp.replace(minute=0, second=0, microsecond=0)


@timer
def requests_per_hour(entries: Iterable[LogEntry]) -> dict[datetime, int]:
    """Count requests per hour with itertools.groupby.

    groupby only groups items that are next to each other, so entries must
    already be in time order. Log files are, so no sorting is needed and
    this works in a single streaming pass.

    Example:
        >>> from log_analyzer.pipeline.transforms import parse_lines
        >>> lines = [
        ...     "2026-10-20 08:05:00 192.168.1.10 GET /home 200",
        ...     "2026-10-20 08:40:00 192.168.1.11 GET /cart 200",
        ...     "2026-10-20 09:10:00 192.168.1.12 GET /login 200",
        ... ]
        >>> {hour.strftime("%H:%M"): n for hour, n in requests_per_hour(parse_lines(lines)).items()}
        {'08:00': 2, '09:00': 1}
    """
    return {hour: sum(1 for _ in group) for hour, group in groupby(entries, key=_hour_of)}


@timer
def group_by_status(entries: Iterable[LogEntry]) -> dict[int, list[LogEntry]]:
    """Group entries by status code with itertools.groupby.

    Entries are not in status order, so they are sorted first; without
    sorting, groupby would start a new group every time the status changes.
    Sorting needs every entry in memory, so prefer count_by for plain counts.
    """
    by_status = attrgetter("status")
    return {
        status: list(group)
        for status, group in groupby(sorted(entries, key=by_status), key=by_status)
    }