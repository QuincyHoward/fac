#!/usr/bin/env python3
"""一键从 Gitee 拉取，支持 ff-only / rebase / stash。"""

from __future__ import annotations

import argparse

from _git_auth import ensure_origin, repo_root, run_git


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("--branch", default="")
    parser.add_argument("--rebase", action="store_true", help="使用 pull --rebase。")
    parser.add_argument("--stash", action="store_true", help="拉取前 stash，拉取后恢复。")
    parser.add_argument("-n", "--dry-run", action="store_true")
    args = parser.parse_args(argv)

    root = repo_root()
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = args.branch or result.stdout.strip() or "master"
    if not ensure_origin(args.namespace, root, args.dry_run):
        return 2

    try:
        if args.stash:
            run_git(["stash", "push", "-m", "fac-auto-pull"], root, namespace=args.namespace, dry_run=args.dry_run)
        mode = ["--rebase"] if args.rebase else ["--ff-only"]
        run_git(["pull", *mode, "origin", branch], root, namespace=args.namespace, dry_run=args.dry_run)
        if args.stash:
            run_git(["stash", "pop"], root, namespace=args.namespace, dry_run=args.dry_run, check=False)
    except RuntimeError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
