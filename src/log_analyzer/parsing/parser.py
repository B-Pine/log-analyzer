"""Turn raw log lines into LogEntry objects."""

from datetime import datetime
from typing import Optional

from ..models import LogEntry
from ..patterns import LOG_LINE, TIMESTAMP_FORMAT, clean_line, is_valid_ipv4


def parse_line(line: str) -> Optional[LogEntry]:
    """Parse one log line.

    Args:
        line: A raw line from the log file, with or without its newline.

    Returns:
        The parsed entry, or None if the line is malformed. Real log files
        always contain some broken lines, so a bad line is not an error.

    Example:
        >>> entry = parse_line("2026-10-20 08:15:32 192.168.1.10 GET /home 200")
        >>> entry.ip, entry.status, entry.timestamp.hour
        ('192.168.1.10', 200, 8)
        >>> parse_line("not a log line") is None
        True
    """
    match = LOG_LINE.match(clean_line(line))
    if match is None or not is_valid_ipv4(match["ip"]):
        return None

    try:
        timestamp = datetime.strptime(match["timestamp"], TIMESTAMP_FORMAT)
    except ValueError:
        return None   # right shape, impossible date (e.g. month 13)

    return LogEntry(
        timestamp=timestamp,
        ip=match["ip"],
        method=match["method"],
        path=match["path"],
        status=int(match["status"]),
    )
