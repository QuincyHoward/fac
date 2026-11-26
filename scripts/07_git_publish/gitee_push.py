#!/usr/bin/env python3
"""一键提交并推送到 Gitee（不再误走 GitHub origin）。

认证走同目录 credential helper：token 不写 .git/config、不进命令行。
原 GitHub origin 会被保留为 upstream，origin 固定为无凭据的 Gitee URL。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _git_auth import ensure_gitee_remote, repo_root, repo_url, run_git  # noqa: E402  # pyright: ignore[reportImplicitRelativeImport]


def git_output(args: list[str], cwd) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def staged_deletions(cwd) -> list[str]:
    out = git_output(["diff", "--cached", "--name-status", "--diff-filter=D"], cwd)
    paths: list[str] = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            paths.append(parts[-1])
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("-m", "--message", default="chore: auto commit by fac git_push")
    parser.add_argument("--branch", default="")
    parser.add_argument("--tag", help="推送指定标签而不是分支。")
    parser.add_argument("-f", "--force", action="store_true", help="强制推送。")
    parser.add_argument("--allow-deletes", action="store_true", help="允许提交删除。")
    parser.add_argument("--pull-first", action="store_true", help="推送前先从 Gitee ff-only 拉取。")
    parser.add_argument("--status", action="store_true", help="仅查看状态，不提交不推送。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("--no-commit", action="store_true", help="只推送已有提交。")
    args = parser.parse_args(argv)

    root = repo_root()
    branch = args.branch or git_output(["rev-parse", "--abbrev-ref", "HEAD"], root).strip() or "master"
    status = git_output(["status", "--porcelain"], root)

    print(f"仓库     : {root}")
    print(f"分支     : {branch}")
    print(f"目标     : Gitee（{repo_url(args.namespace) or '未配置'}）")
    if args.status:
        print(status if status else "工作区干净。")
        return 0

    if not ensure_gitee_remote(args.namespace, root, args.dry_run):
        return 2

    try:
        if args.pull_first:
            run_git(["pull", "--ff-only", "origin", branch], root, namespace=args.namespace, dry_run=args.dry_run)

        if not args.no_commit and status:
            run_git(["add", "-A"], root, namespace=args.namespace, dry_run=args.dry_run, auth=False)
            deletions = staged_deletions(root)
            if deletions and not args.allow_deletes and not args.dry_run:
                run_git(["reset"], root, namespace=args.namespace, dry_run=False, auth=False, check=False)
                print(f"检测到 {len(deletions)} 个已暂存删除，已中止提交；确认无误后加 --allow-deletes。")
                for path in deletions[:10]:
                    print(f"  D {path}")
                return 2
            run_git(
                ["commit", "-m", args.message],
                root,
                namespace=args.namespace,
                dry_run=args.dry_run,
                auth=False,
                check=False,
            )
        elif not args.no_commit:
            print("工作区干净，跳过提交。")

        push_args = ["push", "origin", args.tag if args.tag else branch]
        if args.force:
            push_args.append("--force")
        run_git(push_args, root, namespace=args.namespace, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
