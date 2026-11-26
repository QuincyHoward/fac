#!/usr/bin/env python3
"""Run a single table regression check through demo/check.py."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", help="Generated result table.")
    parser.add_argument("reference", help="Reference table.")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use.")
    parser.add_argument("--checker", default=str(ROOT / "demo" / "check.py"), help="Path to check.py.")
    args = parser.parse_args(argv)

    checker = Path(args.checker).resolve()
    if not checker.is_file():
        print(f"Checker not found: {checker}")
        return 2
    result = subprocess.run(
        [args.python, str(checker), args.result, args.reference],
        cwd=ROOT,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
