"""The functional core: transform with map, select with filter, aggregate with reduce."""

from .aggregations import count_by, error_rate, top
from .filters import (
    Predicate,
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
)
from .transforms import parse_lines, to_dict, to_dicts

__all__ = [
    "parse_lines", "to_dict", "to_dicts",
    "Predicate", "select", "has_status", "has_status_class", "has_method", "in_time_range",
    "is_error", "is_not_found", "is_unauthorized", "is_client_error", "is_server_error",
    "is_get", "is_post",
    "count_by", "error_rate", "top",
]