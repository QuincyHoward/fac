#!/usr/bin/env python3
"""构建 FAC Python 包：优先 python -m build，回退 setup.py。"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from glob import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="运行 twine check dist/*。")
    parser.add_argument("--no-build", action="store_true", help="跳过构建，只执行 check。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not args.no_build:
        if shutil.which(sys.executable) and not args.dry_run:
            try:
                import build  # noqa: F401

                command = [sys.executable, "-m", "build"]
            except ImportError:
                command = [sys.executable, "setup.py", "sdist", "bdist_wheel"]
        else:
            command = [sys.executable, "-m", "build"]
        print("+", " ".join(command))
        if not args.dry_run:
            result = subprocess.run(command, cwd=ROOT, check=False)
            if result.returncode != 0:
                return result.returncode

    if args.check:
        dists = glob(str(ROOT / "dist" / "*"))
        if not dists:
            print("dist/ 中没有可检查的产物。")
            return 2
        command = [sys.executable, "-m", "twine", "check", *dists]
        print("+", " ".join(command))
        if not args.dry_run:
            result = subprocess.run(command, cwd=ROOT, check=False)
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
