#!/usr/bin/env python3
"""Generate and optionally run a safe parallel FAC rebuild command.

Serial preflight steps remain the caller's responsibility: normalize line endings,
run configure, and patch ABI settings in an independent work directory.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", required=True, help="Independent writable build directory.")
    parser.add_argument("--jobs", type=int, default=2, help="Value passed to make -j.")
    parser.add_argument("--dry-run", action="store_true", help="Print commands only.")
    args = parser.parse_args(argv)

    work = Path(args.work_root).expanduser().resolve()
    if not work.is_dir():
        print(f"Work directory not found: {work}")
        return 2

    command = ["make", f"-j{args.jobs}"]
    print("Serial preflight must already be complete:")
    print("  1) CRLF -> LF for shell scripts")
    print("  2) ./configure")
    print("  3) ABI patch if needed")
    print("Command:", " ".join(command), "cwd=", work)

    if args.dry_run:
        return 0
    if shutil.which("make") is None:
        print("GNU make not found; run inside Linux/WSL.")
        return 1
    result = subprocess.run(command, cwd=work, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
