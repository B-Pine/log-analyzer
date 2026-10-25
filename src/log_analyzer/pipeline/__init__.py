"""The functional core: transform with map, select with filter, aggregate with reduce."""

from .aggregations import count_by, error_rate, group_by_status, requests_per_hour, top
from .filters import (
    Predicate,
    between,
    has_method,
    has_status,
    has_status_class,
    in_time_range,
    is_client_error,
    is_error,
    is_get,
    is_not_found,
    is_post,
    is_server_error,
    is_unauthorized,
    select,
    until,
)
from .transforms import parse_lines, to_dict, to_dicts

__all__ = [
    "parse_lines", "to_dict", "to_dicts",
    "Predicate", "select", "has_status", "has_status_class", "has_method", "in_time_range",
    "is_error", "is_not_found", "is_unauthorized", "is_client_error", "is_server_error",
    "is_get", "is_post", "until", "between",
    "count_by", "error_rate", "top", "requests_per_hour", "group_by_status",
]