#!/usr/bin/env python3
"""Run PFAC import and demo smoke checks."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable, help="Python executable to use.")
    parser.add_argument("--pythonpath", default="", help="Extra PYTHONPATH entries, separated by os.pathsep.")
    parser.add_argument("--skip-demo", action="store_true", help="Only run the import check.")
    args = parser.parse_args(argv)

    env = os.environ.copy()
    if args.pythonpath:
        env["PYTHONPATH"] = args.pythonpath + os.pathsep + env.get("PYTHONPATH", "")

    code = "from pfac import fac, crm, pol, util; print('PFAC OK')"
    result = subprocess.run([args.python, "-c", code], env=env, check=False)
    if result.returncode != 0:
        print("PFAC import failed; check PYTHONPATH, Python version and ABI settings.")
        return result.returncode

    if args.skip_demo:
        return 0

    demo = ROOT / "demo"
    result = subprocess.run(["make", "check"], cwd=demo, env=env, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
