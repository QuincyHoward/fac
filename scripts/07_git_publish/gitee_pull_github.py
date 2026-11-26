#!/usr/bin/env python3
"""从 GitHub 官方仓库拉取源码并以官方版本覆盖本地冲突文件。

 Protected by design（用户指定，硬编码在脚本中）:
     仓库根目录的 `.gitignore` 与 `README.md` 永不覆盖、永不备份、不参与复核。
 其余官方路径若本地内容不同，则以官方内容为准覆盖；本地独有文件默认保留。
 比较采用 Git index 口径：文本文件 CRLF 归一为 LF，二进制文件按原始字节比较。

 官方源码只读取，不修改。网络仅使用 api.github.com 与 codeload.github.com 的 HTTPS，
 因为实测 git ls-remote github.com:443 在本机不可达。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from _git_auth import repo_root

REPO_SLUG = "flexible-atomic-code/fac"
API_BASE = "https://api.github.com"
CODELOAD_BASE = "https://codeload.github.com"
BACKUP_ROOT = Path(__file__).resolve().parent / "backups"

# 用户明确指定：根目录这两个文件不覆盖。修改此集合即改变保护策略。
PROTECTED_PATHS = frozenset({".gitignore", "README.md"})

SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
CHUNK = 1024 * 1024
USER_AGENT = "fac-github-overwrite-sync/1.0"


def _retry(call, *, label: str, retries: int, **kwargs):
    """有限重试，最后一次失败抛出异常。"""
    last: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return call(**kwargs)
        except Exception as exc:  # noqa: BLE001 - 网络错误类型较多，统一包装
            last = exc
            if attempt <= retries:
                print(f"  {label}失败（{exc}），第 {attempt} 次重试…")
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"{label}失败（已重试 {retries} 次）：{last}")


def _request_bytes(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def resolve_ref(ref: str, timeout: float, retries: int) -> dict[str, str]:
    """把分支/标签/SHA 解析为完整 SHA 与提交信息。40 位 SHA 跳过 API 请求。"""
    if SHA_RE.fullmatch(ref):
        return {
            "sha": ref.lower(),
            "date": "",
            "message": "（直接指定完整 SHA，跳过 API 元数据解析）",
        }

    quoted = urllib.parse.quote(ref, safe="")
    url = f"{API_BASE}/repos/{REPO_SLUG}/commits/{quoted}"
    payload = _retry(_request_bytes, label=f"解析 ref {ref}", retries=retries, url=url, timeout=timeout)
    import json

    data = json.loads(payload.decode("utf-8"))
    commit = data.get("commit", {})
    committer = commit.get("committer", {})
    message = str(commit.get("message", "")).splitlines()[0] if commit.get("message") else ""
    return {
        "sha": str(data.get("sha", "")),
        "date": str(committer.get("date", "")),
        "message": message,
    }


def download_archive(sha: str, dest: Path, timeout: float, retries: int) -> None:
    """按 SHA 固定下载官方源码归档，流式落盘。"""
    url = f"{CODELOAD_BASE}/{REPO_SLUG}/tar.gz/{sha}"

    def _save() -> None:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=timeout) as response, dest.open("wb") as out:
            shutil.copyfileobj(response, out, CHUNK)

    _retry(_save, label="下载官方归档", retries=retries)
    if dest.stat().st_size == 0:
        raise RuntimeError("下载的归档为空。")


def _safe_relative_path(name: str) -> Path | None:
    """校验 tar 成员名，去掉顶层目录，返回仓库相对路径。"""
    normalized = name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if len(parts) < 2:
        return None
    if re.match(r"^[A-Za-z]:", parts[0]) or any(part == ".." for part in parts):
        return None
    return Path(*parts[1:])


def sha256_file(path: Path) -> str:
    """按 Git index 口径计算哈希：文本 CRLF 归一为 LF，二进制按原始字节。"""
    data = path.read_bytes()
    if b"\x00" not in data:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def extract_official(archive: Path, dest_dir: Path) -> dict[str, str]:
    """安全解压归档，返回 {相对路径: SHA-256}。跳过链接、设备等非普通文件。"""
    result: dict[str, str] = {}
    dest_root = dest_dir.resolve()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            if not member.isfile():
                continue
            rel = _safe_relative_path(member.name)
            if rel is None:
                continue
            target = dest_dir / rel
            if not target.resolve().is_relative_to(dest_root):
                raise RuntimeError(f"归档成员越界，已拒绝：{member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                continue
            with source, target.open("wb") as out:
                shutil.copyfileobj(source, out, CHUNK)
            result[rel.as_posix()] = sha256_file(target)
    if not result:
        raise RuntimeError("归档中没有可提取的普通文件。")
    return result


def _git_lines(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.splitlines()


def _hash_targets(official: dict[str, str], root: Path, workers: int):
    targets = [(rel, digest) for rel, digest in official.items() if rel not in PROTECTED_PATHS]

    def check(item: tuple[str, str]) -> tuple[str, str, str]:
        rel, expected = item
        local = root / rel
        if not local.is_file():
            return rel, "缺失", ""
        actual = sha256_file(local)
        return rel, ("一致" if actual == expected else "不一致"), actual

    with ThreadPoolExecutor(max_workers=workers) as pool:
        yield from pool.map(check, targets)


def scan_local(root: Path, official: dict[str, str], workers: int):
    """返回（冲突列表, 保护跳过列表, 本地独有文件数）。"""
    conflicts = [
        (rel, status, actual)
        for rel, status, actual in _hash_targets(official, root, workers)
        if status != "一致"
    ]
    protected = sorted(rel for rel in official if rel in PROTECTED_PATHS)
    untracked = len(_git_lines(root, ["ls-files", "--others", "--exclude-standard"]))
    return conflicts, protected, untracked


def backup_and_overwrite(
    root: Path,
    official_dir: Path,
    conflicts: list[tuple[str, str, str]],
    *,
    dry_run: bool,
    timestamp: str,
):
    """串行备份并覆盖非保护冲突文件；写同一文件保持串行。"""
    backup_dir = BACKUP_ROOT / timestamp
    written: list[str] = []
    for rel, _status, _actual in sorted(conflicts):
        target = root / rel
        if target.exists() and not target.is_file():
            raise RuntimeError(f"本地路径不是普通文件，拒绝覆盖：{rel}")
        if dry_run:
            written.append(rel)
            continue
        if target.exists():
            saved = backup_dir / rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(official_dir / rel, target)
        written.append(rel)
    return written, (backup_dir if written and not dry_run else None)


def verify(root: Path, official: dict[str, str], workers: int) -> list[str]:
    """复核除保护名单外的全部官方路径，返回不一致文件列表。"""
    return [
        rel
        for rel, status, _actual in _hash_targets(official, root, workers)
        if status != "一致"
    ]


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
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--ref", default="master", help="官方分支/标签/SHA，默认 master。")
    parser.add_argument("-n", "--dry-run", action="store_true", help="只报告，不覆盖任何文件。")
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4), help="并行哈希线程数，上限 8。")
    parser.add_argument("--timeout", type=float, default=60.0, help="单次网络超时秒数。")
    parser.add_argument("--retries", type=int, default=2, help="网络失败重试次数。")
    args = parser.parse_args(argv)

    if args.workers < 1 or args.retries < 0 or args.timeout <= 0:
        print("参数错误：--workers >= 1，--retries >= 0，--timeout > 0。")
        return 2

    script_dir = Path(__file__).resolve().parent
    try:
        os.chdir(script_dir.parents[1])
        root = Path(repo_root()).resolve()
    except Exception as exc:  # noqa: BLE001
        print(f"定位 Git 仓库根失败：{exc}")
        return 2

    print(f"本地仓库  : {root}")
    print(f"保护名单  : {', '.join(sorted(PROTECTED_PATHS))}（根目录，不覆盖/不备份/不复核）")

    try:
        info = resolve_ref(args.ref, args.timeout, args.retries)
        if not info["sha"] or not SHA_RE.fullmatch(info["sha"]):
            raise RuntimeError(f"未能解析出有效的完整 SHA：{info!r}")
        print(f"官方 ref  : {args.ref}")
        print(f"完整 SHA  : {info['sha']}")
        if info["date"]:
            print(f"提交时间  : {info['date']}")
        if info["message"]:
            print(f"提交标题  : {info['message']}")

        with tempfile.TemporaryDirectory(prefix="fac-github-sync-") as tmp:
            tmp_dir = Path(tmp)
            archive = tmp_dir / "official.tar.gz"
            official_dir = tmp_dir / "official"
            official_dir.mkdir()

            print("下载官方源码归档…")
            download_archive(info["sha"], archive, args.timeout, args.retries)
            print("解压并计算官方文件哈希…")
            official = extract_official(archive, official_dir)
            print(f"官方文件数: {len(official)}")

            conflicts, protected, untracked = scan_local(root, official, args.workers)
            _print_list("保护跳过（保持本地现状）", protected)
            _print_list(
                "冲突文件（将以官方内容覆盖）",
                [f"{rel} [{status}]" for rel, status, _ in conflicts],
            )
            print(f"本地独有文件: {untracked} 个（默认保留）")

            if args.dry_run:
                print(f"DRY-RUN 结束：待覆盖 {len(conflicts)} 个，保护 {len(protected)} 个；未写入任何文件。")
                return 0

            timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
            written, backup_dir = backup_and_overwrite(
                root,
                official_dir,
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
            if backup_dir:
                print(f"备份位置  : {backup_dir}")
            else:
                print("备份位置  : 无需备份（无被覆盖文件）")
            print(
                f"复核通过  : {len(official) - len(protected)} 个官方路径一致，"
                f"{len(protected)} 个保护路径跳过。"
            )
            return 0
    except RuntimeError as exc:
        print(f"错误：{exc}")
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"未预期错误：{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
