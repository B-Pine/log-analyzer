"""Predicates for filter(), plus ready-made ones built with partial().

Every predicate takes its settings first and the entry last, so
functools.partial can fix the settings and leave a one-argument
function that filter() can use directly.
"""

from collections.abc import Callable, Container, Iterable, Iterator
from datetime import datetime
from functools import partial

from ..models import LogEntry

Predicate = Callable[[LogEntry], bool]
"""A function that says whether to keep an entry."""


def has_status(statuses: Container[int], entry: LogEntry) -> bool:
    """True if the entry's status is one of the given codes."""
    return entry.status in statuses


def has_status_class(status_class: str, entry: LogEntry) -> bool:
    """True if the entry's status family matches, e.g. "4xx"."""
    return entry.status_class == status_class


def has_method(method: str, entry: LogEntry) -> bool:
    """True if the entry used the given HTTP method."""
    return entry.method == method


def in_time_range(start: datetime, end: datetime, entry: LogEntry) -> bool:
    """True if start <= timestamp < end."""
    return start <= entry.timestamp < end


def is_error(entry: LogEntry) -> bool:
    """True for 4xx and 5xx responses."""
    return entry.is_error


# Specialized filters: partial() fixes the first argument.
is_not_found = partial(has_status, {404})
is_unauthorized = partial(has_status, {401, 403})
is_client_error = partial(has_status_class, "4xx")
is_server_error = partial(has_status_class, "5xx")
is_get = partial(has_method, "GET")
is_post = partial(has_method, "POST")


def select(entries: Iterable[LogEntry], *predicates: Predicate) -> Iterator[LogEntry]:
    """Keep only the entries that pass every predicate.

    Example:
        >>> from log_analyzer.pipeline.transforms import parse_lines
        >>> lines = [
        ...     "2026-10-20 08:00:00 192.168.1.10 GET /home 200",
        ...     "2026-10-20 08:01:00 192.168.1.11 GET /missing 404",
        ...     "2026-10-20 08:02:00 192.168.1.12 POST /missing 404",
        ... ]
        >>> [e.ip for e in select(parse_lines(lines), is_not_found, is_get)]
        ['192.168.1.11']
    """
    return filter(lambda entry: all(check(entry) for check in predicates), entries)

