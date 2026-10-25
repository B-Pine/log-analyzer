"""Reading log files lazily, batching and paging, and writing reports."""

from .batcher import Batcher, paginate
from .json_writer import write_report
from .line_reader import read_lines, read_many

__all__ = ["Batcher", "paginate", "read_lines", "read_many", "write_report"]