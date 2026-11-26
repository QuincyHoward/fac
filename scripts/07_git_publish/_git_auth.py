"""Gitee 认证与 Git 执行辅助：令牌只通过环境变量传给 git，不打印。"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from credentials._core import get as get_secret  # noqa: E402


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("当前目录不是 Git 仓库。")
    return Path(result.stdout.strip())


def repo_url(namespace: str = "specx") -> str:
    value = get_secret(namespace, "gitee.repo_url")
    return str(value).strip() if value else ""


def require_token(namespace: str = "specx") -> str:
    data = get_secret(namespace, "gitee.token")
    if isinstance(data, dict):
        token = str(data.get("token", ""))
    else:
        token = str(data or "")
    if not token:
        raise RuntimeError("未找到 Gitee 令牌；请先在凭证菜单中设置 gitee.token。")
    return token


def auth_env(namespace: str = "specx") -> dict[str, str]:
    env = os.environ.copy()
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
    env["GIT_CONFIG_VALUE_0"] = f"Authorization: token {require_token(namespace)}"
    return env


def remote_exists(name: str = "origin", cwd: Path | None = None) -> bool:
    result = subprocess.run(
        ["git", "remote", "get-url", name],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def ensure_origin(namespace: str, cwd: Path, dry_run: bool = False) -> bool:
    if remote_exists("origin", cwd):
        return True
    url = repo_url(namespace)
    if not url:
        print("未配置 origin，且未找到 gitee.repo_url；请先设置仓库地址。")
        return False
    print("+ git remote add origin <gitee.repo_url>")
    if not dry_run:
        subprocess.run(["git", "remote", "add", "origin", url], cwd=cwd, check=True)
    return True


def run_git(
    args: Iterable[str],
    cwd: Path,
    *,
    namespace: str = "specx",
    dry_run: bool = False,
    auth: bool = True,
    check: bool = True,
) -> int:
    command = ["git", *args]
    print("+", " ".join(command))
    if dry_run:
        return 0
    result = subprocess.run(
        command,
        cwd=cwd,
        env=auth_env(namespace) if auth else None,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Git 命令失败：{command[1]}（退出码 {result.returncode}）")
    return result.returncode
