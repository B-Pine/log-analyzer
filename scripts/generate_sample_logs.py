"""Generate a sample access log.

Usage:
    python scripts/generate_sample_logs.py                     # 1,500 lines
    python scripts/generate_sample_logs.py --lines 5000 -o data/big.log --seed 7
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

# START = datetime(2026, 10, 20)
DURATION = timedelta(days=2)

METHODS = {"GET": 80, "POST": 15, "PUT": 3, "DELETE": 2}
STATUSES = {200: 70, 304: 6, 404: 12, 401: 4, 403: 2, 500: 6}
PATHS = ["/home", "/login", "/products", "/cart", "/checkout",
         "/search", "/profile", "/api/orders", "/missing", "/admin"]
MALFORMED = [
    "2026-10-20 09:12:44 192.168.1.10 GET /home",        # missing status
    "this line was not written by the web server",
    "2026-13-45 08:00:00 192.168.1.10 GET /home 200",    # impossible date
    "2026-10-20 08:00:00 999.168.1.10 GET /home 200",    # invalid IP
    "",
]


def generate(line_count: int, start: datetime, rng: random.Random) -> list[str]:
    """Create line_count valid lines in time order, plus about 1% malformed."""
    ips = [f"192.168.1.{n}" for n in range(10, 40)]
    ip_weights = [1 / (rank + 1) for rank in range(len(ips))]   # a few IPs dominate

    seconds = sorted(rng.uniform(0, DURATION.total_seconds()) for _ in range(line_count))
    lines = []
    for offset in seconds:
        timestamp = (start + timedelta(seconds=offset)).strftime("%Y-%m-%d %H:%M:%S")
        ip = rng.choices(ips, weights=ip_weights)[0]
        method = rng.choices(list(METHODS), weights=list(METHODS.values()))[0]
        status = rng.choices(list(STATUSES), weights=list(STATUSES.values()))[0]
        separator = "  " if rng.random() < 0.02 else " "         # messy spacing
        lines.append(separator.join([timestamp, ip, method, rng.choice(PATHS), str(status)]))

    for _ in range(max(1, line_count // 100)):
        lines.insert(rng.randrange(len(lines)), rng.choice(MALFORMED))
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a sample access log.")
    parser.add_argument("--lines", type=int, default=1500, help="valid lines (default: 1500)")
    parser.add_argument("-o", "--output", type=Path, default=Path("data/access.log"))
    parser.add_argument("--start", type=datetime.fromisoformat, default=datetime(2026, 10, 20),
                    help="first day, e.g. 2026-10-22 (default: 2026-10-20)")
    parser.add_argument("--seed", type=int, default=42, help="random seed (default: 42)")
    args = parser.parse_args()

    lines = generate(args.lines, args.start, random.Random(args.seed))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as file:
        file.writelines(line + "\n" for line in lines)

    print(f"Wrote {len(lines)} lines to {args.output}")


if __name__ == "__main__":
    main()