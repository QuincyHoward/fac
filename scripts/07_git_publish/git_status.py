#!/usr/bin/env python3
"""查看当前 Git 分支、远端与工作区状态。"""

from __future__ import annotations

import argparse
import subprocess

from _git_auth import repo_root


def show(args: list[str], cwd) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout.strip() or "(无输出)"


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    root = repo_root()
    print(f"仓库 : {root}")
    print(f"分支 : {show(['rev-parse', '--abbrev-ref', 'HEAD'], root)}")
    print("远端 :")
    print(show(["remote", "-v"], root))
    print("状态 :")
    print(show(["status", "--short"], root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
