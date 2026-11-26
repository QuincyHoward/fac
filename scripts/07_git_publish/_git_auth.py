"""Gitee Git 认证统一入口：凭据只经 credential helper 管道传递。

与旧版的区别：
- 旧版 `origin` 若已存在（本仓指向 GitHub）就直接复用，并把 Gitee token 作为
  `http.extraHeader` 发给所有远端，导致推送实际走 GitHub 并要求 GitHub 凭据。
- 新版强制 `origin` 指向 **不含凭据的 Gitee URL**；原 GitHub origin 自动保留为
  `upstream`。认证由 _git_credential_helper.py 在 fetch/pull/push 时经管道提供，
  不写 .git/config、不进命令行参数。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Iterable, Sequence

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from credentials._config import DEFAULT_NAMESPACE  # noqa: E402
from credentials._core import get as get_secret  # noqa: E402

HELPER_NAME = "_git_credential_helper.py"
GITHUB_UPSTREAM = "https://github.com/flexible-atomic-code/fac.git"


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


def repo_url(namespace: str = DEFAULT_NAMESPACE) -> str:
    value = get_secret(namespace, "gitee.repo_url")
    return str(value).strip() if value else ""


def require_token(namespace: str = DEFAULT_NAMESPACE) -> str:
    data = get_secret(namespace, "gitee.token", {})
    if isinstance(data, dict):
        token = str(data.get("token") or "")
    else:
        token = str(data or "")
    if not token:
        raise RuntimeError("未找到 Gitee 令牌；请先在凭证菜单中设置 gitee.token。")
    return token


def gitee_identity(namespace: str = DEFAULT_NAMESPACE) -> tuple[str, str]:
    """返回 (login, token)；login 缺失时通过 Gitee API 查询认证登录名。"""
    data = get_secret(namespace, "gitee.token", {})
    if isinstance(data, dict):
        token = str(data.get("token") or "").strip()
        login = str(data.get("login") or data.get("username") or "").strip()
    else:
        token = str(data or "").strip()
        login = ""
    if not token:
        raise RuntimeError("未找到 Gitee 令牌；请先在凭证菜单中设置 gitee.token。")
    if login:
        return login, token

    request = urllib.request.Request(
        "https://gitee.com/api/v5/user",
        headers={"User-Agent": "fac-git-auth", "Authorization": f"token {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            login = str(json.loads(response.read().decode("utf-8")).get("login") or "").strip()
    except Exception as exc:  # noqa: BLE001
        print(f"警告：无法查询 Gitee 登录名（{exc}）；将不显式提供 username。")
    return login, token


def helper_path() -> Path:
    return Path(__file__).resolve().parent / HELPER_NAME


def auth_prefix() -> list[str]:
    """返回注入到 git 命令前的 `-c` 参数；helper 缺失时返回空列表。"""
    helper = helper_path()
    if not helper.is_file():
        return []
    python = Path(sys.executable).as_posix()
    return [
        "-c",
        "credential.helper=",
        "-c",
        f'credential.helper=!"{python}" "{helper.as_posix()}"',
        "-c",
        "core.askPass=",
    ]


def remote_exists(name: str = "origin", cwd: Path | None = None) -> bool:
    result = subprocess.run(
        ["git", "remote", "get-url", name],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git_output(args: Sequence[str], cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def run_git(
    args: Iterable[str],
    cwd: Path,
    *,
    namespace: str = DEFAULT_NAMESPACE,
    dry_run: bool = False,
    auth: bool = True,
    check: bool = True,
) -> int:
    """执行 git 命令；网络命令默认注入 Gitee credential helper。"""
    command = list(args)
    if auth:
        prefix = auth_prefix()
        if not prefix:
            print(f"警告：未找到 {HELPER_NAME}，认证可能失败。")
        command = prefix + command
    env = os.environ.copy()
    env["FAC_CRED_NAMESPACE"] = namespace
    print("+", " ".join(["git", *command]))
    if dry_run:
        return 0
    result = subprocess.run(["git", *command], cwd=cwd, env=env, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"Git 命令失败：{command[-1] if command else 'git'}（退出码 {result.returncode}）")
    return result.returncode


def ensure_gitee_remote(namespace: str, cwd: Path, dry_run: bool = False) -> bool:
    """确保 origin 是无凭据的 Gitee URL；原 GitHub origin 保留为 upstream。"""
    url = repo_url(namespace)
    if not url:
        print("未找到 gitee.repo_url；请先在凭证菜单中设置仓库地址。")
        return False

    current = _git_output(["remote", "get-url", "origin"], cwd)
    if current and "github.com" in current and not remote_exists("upstream", cwd):
        print(f"保留原 GitHub origin 为 upstream：{current}")
        run_git(["remote", "add", "upstream", current], cwd, auth=False, dry_run=dry_run)
    if not current:
        run_git(["remote", "add", "origin", url], cwd, auth=False, dry_run=dry_run)
    elif current != url:
        run_git(["remote", "set-url", "origin", url], cwd, auth=False, dry_run=dry_run)
    return True


def ensure_origin(namespace: str, cwd: Path, dry_run: bool = False) -> bool:
    """兼容旧调用名；语义已改为确保 origin 指向 Gitee。"""
    return ensure_gitee_remote(namespace, cwd, dry_run)
