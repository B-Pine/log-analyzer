"""Reading log files lazily, batching and paging."""

from .batcher import Batcher, paginate
from .line_reader import read_lines, read_many

__all__ = ["Batcher", "paginate", "read_lines", "read_many"]