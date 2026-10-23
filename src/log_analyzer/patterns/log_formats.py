"""Regex pattern for one access log line.

Format:
    2026-10-20 08:15:32 192.168.1.10 GET /home 200
"""

import re

LOG_LINE: re.Pattern[str] = re.compile(
    r"""
    ^(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})   # 2026-10-20 08:15:32
    \s(?P<ip>\S+)                                         # 192.168.1.10
    \s(?P<method>[A-Z]+)                                  # GET
    \s(?P<path>/\S*)                                      # /home
    \s(?P<status>\d{3})$                                  # 200
    """,
    re.VERBOSE,
)

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
"""strptime format for the timestamp group."""
