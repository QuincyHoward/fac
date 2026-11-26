#!/usr/bin/env python3
"""发布前备份：gitee 模式按 git 文件表，full 模式近全量复制。"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL_EXCLUDE = {".git", "build", "dist", "__pycache__", "outputs", "runs", "logs"}


def gitee_files() -> list[str]:
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=False).stdout
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return sorted(set(filter(None, tracked.splitlines() + untracked.splitlines())))


def full_files() -> list[str]:
    rows = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT)
        if any(part in FULL_EXCLUDE or part.endswith(".pyc") for part in rel.parts):
            continue
        if path.is_file():
            rows.append(str(rel).replace("\\", "/"))
    return sorted(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["gitee", "full"], default="gitee")
    parser.add_argument("--dest", default=str(ROOT.parent), help="备份目标父目录。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    files = gitee_files() if args.mode == "gitee" else full_files()
    target = Path(args.dest).resolve() / f"fac_backup_{args.mode}_{dt.datetime.now():%Y%m%d_%H%M%S}"
    print(f"模式     : {args.mode}")
    print(f"文件数   : {len(files)}")
    print(f"目标     : {target}")
    if args.dry_run:
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for rel in files:
        src = ROOT / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print("备份完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
