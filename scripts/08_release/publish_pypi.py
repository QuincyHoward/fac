#!/usr/bin/env python3
"""使用加密令牌发布到 PyPI / TestPyPI，令牌不进入命令行。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from glob import glob
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from credentials.pypi import get_config  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
TEST_URL = "https://test.pypi.org/legacy/"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("--test", action="store_true", help="发布到 TestPyPI。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    index = "testpypi" if args.test else "pypi"
    config = get_config(args.namespace, index)
    if not config:
        print(f"尚未配置 {index} Token；请先运行 python scripts/credentials/pypi.py setup {index}")
        return 2

    dists = glob(str(ROOT / "dist" / "*"))
    if not dists:
        print("dist/ 中没有可上传的产物；请先运行 package.py。")
        return 2
    command = [sys.executable, "-m", "twine", "upload", *dists]
    if args.test:
        command += ["--repository-url", TEST_URL]
    print("+", " ".join(command))

    if args.dry_run:
        return 0
    env = os.environ.copy()
    env["TWINE_USERNAME"] = config["username"]
    env["TWINE_PASSWORD"] = config["password"]
    return subprocess.run(command, cwd=ROOT, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
