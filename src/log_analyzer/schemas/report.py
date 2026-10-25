"""TypedDict definitions describing the JSON report structure."""

from typing import Optional, TypedDict


class TimeRange(TypedDict):
    """First and last request in the logs, as ISO timestamps."""

    first: Optional[str]
    last: Optional[str]


class SummaryReport(TypedDict):
    """The complete analytics report written to JSON."""

    generated_at: str
    source_files: list[str]
    total_lines: int
    parsed_entries: int
    malformed_lines: int
    time_range: TimeRange
    error_rate: float
    status_classes: dict[str, int]
    status_codes: dict[str, int]
    methods: dict[str, int]
    top_ips: dict[str, int]
    top_paths: dict[str, int]
    top_error_paths: dict[str, int]
    requests_per_hour: dict[str, int]
