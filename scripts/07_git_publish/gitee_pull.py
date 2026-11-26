#!/usr/bin/env python3
"""一键从 Gitee 拉取并以 Gitee 内容覆盖本地 fac 项目。

与旧版 `git pull --ff-only` 不同：这里把 Gitee 当作事实源，只覆盖工作区中
官方路径下内容不同的文件；根目录 `.gitignore` 与 `README.md` 受保护不覆盖，
本地独有文件默认保留。凭据经 credential helper 管道传递，不写配置、不进命令行。

注意：本脚本只同步工作区文件，不改写本地 Git 历史；提交/推送请用 gitee_push.py。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from _git_auth import auth_prefix, ensure_gitee_remote, repo_root, repo_url, run_git  # noqa: E402  # pyright: ignore[reportImplicitRelativeImport]
from gitee_pull_github import backup_and_overwrite, scan_local, sha256_file, verify  # noqa: E402  # pyright: ignore[reportImplicitRelativeImport]


def _git_branch(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "master"


def _clone_gitee(url: str, branch: str, dest: Path, namespace: str) -> None:
    env = os.environ.copy()
    env["FAC_CRED_NAMESPACE"] = namespace
    command = ["git", *auth_prefix(), "clone", "--depth", "1", "--branch", branch, url, str(dest)]
    result = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            "从 Gitee 克隆失败：" + ((result.stderr or "").strip()[:400] or "(无 stderr)")
        )


def _official_hashes(clone_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in clone_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(clone_dir)
        if rel.parts and rel.parts[0] == ".git":
            continue
        result[rel.as_posix()] = sha256_file(path)
    if not result:
        raise RuntimeError("Gitee 仓库中没有可比对的普通文件。")
    return result


def _print_list(title: str, items: list[str], limit: int = 20) -> None:
    if not items:
        print(f"{title}: 无")
        return
    print(f"{title}（共 {len(items)} 个）:")
    for item in items[:limit]:
        print(f"  - {item}")
    if len(items) > limit:
        print(f"  … 其余 {len(items) - limit} 个省略")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("--branch", default="")
    parser.add_argument("--workers", type=int, default=8, help="并行哈希线程数。")
    parser.add_argument("-n", "--dry-run", action="store_true", help="只报告差异，不覆盖文件。")
    args = parser.parse_args(argv)

    script_dir = Path(__file__).resolve().parent
    try:
        os.chdir(script_dir.parents[1])
        root = repo_root()
    except Exception as exc:  # noqa: BLE001
        print(f"定位 Git 仓库根失败：{exc}")
        return 2

    branch = args.branch or _git_branch(root)
    url = repo_url(args.namespace)
    print(f"本地仓库  : {root}")
    print(f"Gitee 地址: {url or '未配置'}")
    print(f"分支      : {branch}")
    if args.workers < 1:
        print("参数错误：--workers >= 1。")
        return 2

    try:
        if not ensure_gitee_remote(args.namespace, root, args.dry_run):
            return 2
        run_git(["fetch", "origin", branch], root, namespace=args.namespace, dry_run=args.dry_run)

        with tempfile.TemporaryDirectory(prefix="fac-gitee-pull-") as tmp:
            clone_dir = Path(tmp) / "gitee"
            print("克隆 Gitee 源码用于逐文件比对…")
            _clone_gitee(url, branch, clone_dir, args.namespace)

            official = _official_hashes(clone_dir)
            print(f"Gitee 文件数: {len(official)}")

            conflicts, protected, untracked = scan_local(root, official, args.workers)
            _print_list("保护跳过（保持本地现状）", protected)
            _print_list("冲突文件（将以 Gitee 内容覆盖）", [rel for rel, _s, _a in conflicts])
            print(f"本地独有文件: {untracked} 个（默认保留）")

            if args.dry_run:
                print(
                    f"DRY-RUN 结束：待覆盖 {len(conflicts)} 个，保护 {len(protected)} 个；"
                    "未写入任何文件。"
                )
                return 0

            timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            written, backup_dir = backup_and_overwrite(
                root,
                clone_dir,
                conflicts,
                dry_run=False,
                timestamp=timestamp,
            )
            mismatch = verify(root, official, args.workers)
            if mismatch:
                _print_list("复核失败，内容仍不一致", mismatch)
                if backup_dir:
                    print(f"备份保留在: {backup_dir}")
                return 1

            print(f"已覆盖    : {len(written)} 个文件")
            print(f"备份位置  : {backup_dir if backup_dir else '无需备份（无被覆盖文件）'}")
            print(
                f"复核通过  : {len(official) - len(protected)} 个 Gitee 路径一致，"
                f"{len(protected)} 个保护路径跳过。"
            )
            print("说明      : 仅同步工作区文件，未改写 Git 历史；需要提交请用 gitee_push.py。")
            return 0
    except RuntimeError as exc:
        print(f"错误：{exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"未预期错误：{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
