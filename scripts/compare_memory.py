"""Demo: memory and speed of generators versus lists on a large log.

Usage:
    python scripts/compare_memory.py                 # 200,000 lines
    python scripts/compare_memory.py --lines 1000000

Writes a temporary log file, runs the same analysis two ways, and prints
Markdown tables ready to paste into the README.
"""

import argparse
import sys
import tempfile
import time
import tracemalloc
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial
from operator import attrgetter
from pathlib import Path

from log_analyzer.file_io import read_lines
from log_analyzer.pipeline import count_by, in_time_range, parse_lines, select, until

START = datetime(2026, 10, 20)
PATHS = ["/home", "/login", "/products", "/cart", "/checkout"]
STATUSES = [200, 200, 200, 200, 404, 500]


def write_large_log(path: Path, line_count: int) -> None:
    """Write line_count valid lines spread evenly over 48 hours."""
    step = timedelta(hours=48) / line_count
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for n in range(line_count):
            timestamp = (START + step * n).strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{timestamp} 192.168.1.{10 + n % 30} GET "
                       f"{PATHS[n % len(PATHS)]} {STATUSES[n % len(STATUSES)]}\n")


def measure(work: Callable[[], object]) -> tuple[float, float]:
    """Run work twice: once for time (seconds), once for peak memory (MB)."""
    start = time.perf_counter()
    work()
    seconds = time.perf_counter() - start

    tracemalloc.start()
    work()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return seconds, peak / 1_048_576


def print_table(title: str, results: dict[str, tuple[float, float]]) -> None:
    print(f"### {title}\n")
    print("| Approach | Time | Peak memory |")
    print("|---|---|---|")
    for label, (seconds, megabytes) in results.items():
        print(f"| {label} | {seconds * 1000:.0f} ms | {megabytes:.2f} MB |")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare generators and lists.")
    parser.add_argument("--lines", type=int, default=200_000, help="lines in the test log")
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "large.log"
        write_large_log(path, args.lines)
        size_mb = path.stat().st_size / 1_048_576
        print(f"Python {sys.version.split()[0]} on {sys.platform} | "
              f"{args.lines:,} lines, {size_mb:.1f} MB log file\n")

        print_table("Reading every line", {
            "list: `read_text().splitlines()`":
                measure(lambda: path.read_text(encoding="utf-8").splitlines()),
            "generator: `read_lines()`":
                measure(lambda: sum(1 for _ in read_lines(path))),
        })

        by_status = attrgetter("status")
        print_table("Counting requests per status", {
            "list: parse everything, then count":
                measure(lambda: count_by(by_status, list(parse_lines(read_lines(path))))),
            "generator: stream through the pipeline":
                measure(lambda: count_by(by_status, parse_lines(read_lines(path)))),
        })

        first_hour = partial(in_time_range, START, START + timedelta(hours=1))
        print_table("Selecting the first hour of 48", {
            "`filter()`: checks every entry":
                measure(lambda: sum(1 for _ in select(parse_lines(read_lines(path)), first_hour))),
            "`takewhile()`: stops at the first late entry":
                measure(lambda: sum(1 for _ in until(START + timedelta(hours=1),
                                                     parse_lines(read_lines(path))))),
        })


if __name__ == "__main__":
    main()