"""Write reports to disk as JSON."""

import json
from pathlib import Path

from ..exceptions import LogFileError
from ..schemas import SummaryReport


def write_report(report: SummaryReport, output_path: Path | str) -> Path:
    """Write a report as pretty-printed JSON, creating folders as needed.

    Returns:
        The path the report was written to.

    Raises:
        LogFileError: If the file or its folder cannot be written.
    """
    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, ensure_ascii=False)
    except OSError as error:
        raise LogFileError(f"Could not write {path}: {error}") from error
    return path