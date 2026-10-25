"""Read log files lazily, one line at a time."""

from collections.abc import Iterable, Iterator
from itertools import chain
from pathlib import Path

from ..exceptions import LogFileError


def read_lines(path: Path | str) -> Iterator[str]:
    """Yield the lines of a log file one at a time.

    Only one line is in memory at any moment, so files of any size can be
    processed. Undecodable bytes are replaced instead of crashing, since one
    corrupted line should not stop the analysis.

    Because this is a generator, nothing happens until the first line is
    requested, including the check that the file exists.

    Raises:
        LogFileError: If the file is missing or cannot be read.
    """
    path = Path(path)
    try:
        with path.open(encoding="utf-8", errors="replace") as file:
            yield from file
    except FileNotFoundError as error:
        raise LogFileError(f"File not found: {path}") from error
    except PermissionError as error:
        raise LogFileError(f"Permission denied: {path}") from error
    except OSError as error:
        raise LogFileError(f"Could not read {path}: {error}") from error


def read_many(paths: Iterable[Path | str]) -> Iterator[str]:
    """Yield the lines of several log files, one file after another.

    itertools.chain.from_iterable joins the per-file generators into one
    stream. Files are opened one at a time, only when the previous one is done.
    """
    return chain.from_iterable(map(read_lines, paths))