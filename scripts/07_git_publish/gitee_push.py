#!/usr/bin/env python3
"""一键提交并推送到 Gitee，令牌不进入命令行。"""

from __future__ import annotations

import argparse
import subprocess

from _git_auth import ensure_origin, repo_root, run_git


def git_output(args: list[str], cwd) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("-m", "--message", default="chore: auto commit by fac git_push")
    parser.add_argument("--branch", default="")
    parser.add_argument("--tag", help="推送指定标签而不是分支。")
    parser.add_argument("--allow-deletes", action="store_true", help="允许提交删除。")
    parser.add_argument("--pull-first", action="store_true", help="推送前先 ff-only 拉取。")
    parser.add_argument("--status", action="store_true", help="仅查看状态，不提交不推送。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("--no-commit", action="store_true", help="只推送已有提交。")
    args = parser.parse_args(argv)

    root = repo_root()
    branch = args.branch or git_output(["rev-parse", "--abbrev-ref", "HEAD"], root).strip() or "master"
    status = git_output(["status", "--porcelain"], root)
    deletions = [line for line in status.splitlines() if line.startswith(" D") or line.startswith("D ")]

    print(f"仓库     : {root}")
    print(f"分支     : {branch}")
    if args.status:
        print(status if status else "工作区干净。")
        return 0

    if deletions and not args.allow_deletes:
        print(f"检测到 {len(deletions)} 个删除；确认无误后加 --allow-deletes。")
        return 2
    if not ensure_origin(args.namespace, root, args.dry_run):
        return 2

    try:
        if args.pull_first:
            run_git(["pull", "--ff-only", "origin", branch], root, namespace=args.namespace, dry_run=args.dry_run)
        if not args.no_commit:
            if status:
                run_git(["add", "-A"], root, namespace=args.namespace, dry_run=args.dry_run)
                run_git(["commit", "-m", args.message], root, namespace=args.namespace, dry_run=args.dry_run, check=False)
            else:
                print("工作区干净，跳过提交。")
        if args.tag:
            run_git(["push", "origin", args.tag], root, namespace=args.namespace, dry_run=args.dry_run)
        else:
            run_git(["push", "origin", branch], root, namespace=args.namespace, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
