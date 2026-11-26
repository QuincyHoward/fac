#!/usr/bin/env python3
"""Inspect key lines of an output table."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SCEN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCEN))

from common.readers import describe_table, read_table_lines  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", help="Generated table path.")
    parser.add_argument("--limit", type=int, default=12)
    args = parser.parse_args(argv)

    path = Path(args.table).resolve()
    print(describe_table(path, args.limit))
    print("\nFirst lines:")
    print("\n".join(read_table_lines(path, min(args.limit, 8))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
