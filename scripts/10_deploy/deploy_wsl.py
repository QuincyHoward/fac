#!/usr/bin/env python3
"""将当前 FAC 项目部署到 WSL 目标目录，使用 wslpath 自动转换源路径。"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(args))
    return subprocess.run(args, text=True, capture_output=check, check=False)


def wsl_source_path(source: Path, distro: str) -> str:
    candidate = str(source.resolve()).replace("\\", "/")
    result = subprocess.run(
        ["wsl", "-d", distro, "--", "wslpath", candidate],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "wslpath 转换失败")
    return result.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(ROOT), help="Windows 源目录，默认当前项目根。")
    parser.add_argument("--distro", default="Ubuntu-22.04", help="WSL 发行版名称。")
    parser.add_argument("--target", default="/root/QC/fac/fac", help="WSL 目标目录。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    source = Path(args.source).resolve()
    if not (source / "README.md").is_file():
        print(f"源目录缺少 README.md：{source}")
        return 2

    try:
        wsl_src = wsl_source_path(source, args.distro)
    except RuntimeError as exc:
        print(exc)
        return 1

    print(f"Windows 源 : {source}")
    print(f"WSL 源     : {wsl_src}")
    print(f"WSL 目标   : {args.target}")

    if args.dry_run:
        print("Dry run：未执行复制。")
        return 0

    commands = [
        ["wsl", "-d", args.distro, "--", "mkdir", "-p", args.target],
        ["wsl", "-d", args.distro, "--", "cp", "-a", f"{wsl_src}/.", args.target + "/"],
        ["wsl", "-d", args.distro, "--", "bash", "-c", f"test -f {args.target}/README.md"],
    ]
    for command in commands:
        result = run(command, check=False)
        if result.returncode != 0:
            print(f"命令失败：{command[3] if len(command) > 3 else command[0]}")
            if result.stderr:
                print(result.stderr.strip())
            return 1
    print("部署完成。")
    print(f"验证目录：{args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
