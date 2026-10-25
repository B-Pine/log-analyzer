"""Command-line interface for the log analyzer.

Usage:
    log-analyzer data/access.log
    log-analyzer data/access.log data/access_2.log -o reports/summary.json --top 10 -v
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from .exceptions import LogAnalyzerError
from .file_io import write_report
from .reports import build_summary
from .schemas import SummaryReport

BAR_WIDTH = 30


def main(argv: Sequence[str] | None = None) -> int:
    """Run the analyzer: read the logs, build the report, write it, print a summary.

    Returns:
        Exit code: 0 on success, 1 if the logs could not be processed.
        Invalid arguments exit with code 2 (handled by argparse).
    """
    args = _build_parser().parse_args(argv)
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format="  [%(levelname)s] %(message)s")

    try:
        report = build_summary(args.logs, top_n=args.top)
        path = write_report(report, args.output)
    except LogAnalyzerError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    _print_summary(report, path)
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Define the command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze web server access logs and write a JSON report.",
    )
    parser.add_argument("logs", nargs="+", type=Path,
                        help="one or more log files, in chronological order")
    parser.add_argument("-o", "--output", type=Path, default=Path("reports/summary.json"),
                        help="where to write the JSON report (default: reports/summary.json)")
    parser.add_argument("--top", type=_positive_int, default=5,
                        help="entries per top list (default: 5)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="show how long each analysis step takes")
    return parser


def _positive_int(value: str) -> int:
    """argparse type that only accepts integers of 1 or more."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {number}")
    return number


def _print_summary(report: SummaryReport, path: Path) -> None:
    """Print a short, human-readable version of the report."""
    print(f"\nLog Analysis: {', '.join(report['source_files'])}")
    print(f"Lines: {report['total_lines']} | Parsed: {report['parsed_entries']} "
          f"| Malformed: {report['malformed_lines']} | Error rate: {report['error_rate']}%")
    span = report["time_range"]
    print(f"From {span['first']} to {span['last']}")

    print("\nStatus classes")
    total = report["parsed_entries"] or 1
    for family, count in report["status_classes"].items():
        bar = "█" * round(count / total * BAR_WIDTH)
        print(f"  {family}  {bar:<{BAR_WIDTH}} {count}")

    _print_counts("Top IPs", report["top_ips"])
    _print_counts("Top paths", report["top_paths"])
    _print_counts("Top error paths", report["top_error_paths"])

    hourly = report["requests_per_hour"]
    if hourly:
        busiest = max(hourly, key=lambda hour: hourly[hour])
        print(f"\nBusiest hour: {busiest} ({hourly[busiest]} requests)")

    print(f"\nReport written to {path}")


def _print_counts(title: str, counts: dict[str, int]) -> None:
    """Print one "top" list as an aligned two-column table."""
    print(f"\n{title}")
    for value, count in counts.items():
        print(f"  {value:<20} {count}")