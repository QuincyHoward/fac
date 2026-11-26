"""Configuration constants for FAC credentials."""

from __future__ import annotations

import re
from pathlib import Path

PHYSIMX_ROOT = Path.home() / ".physimx"
DEFAULT_NAMESPACE = "specx"
SUPPORTED_NAMESPACES = ("specx", "flychk", "flash")
_NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_-]+$")

SECRET_FIELDS = {
    "password",
    "token",
    "api_key",
    "secret",
    "access_key",
    "private_key",
}

SERVICE_KEYS = {
    "gitee.token": "Gitee Personal Access Token",
    "hpc.flash_ssh.password": "HPC SSH password",
    "wsl.default_distro": "Default WSL distribution",
    "api.deepseek.api_key": "DeepSeek API key",
}

DEFAULT_HPC_ACCOUNTS = {
    "_comment": [
        "FAC HPC 账户基础信息（非敏感）；密码等敏感信息保存在 credentials.enc。",
        "accounts.<name>.routes 每项使用 {host, port, label}；文档中只放占位符。",
    ],
    "accounts": {},
}

DEFAULT_WSL_CONFIG = {
    "_comment": "FAC WSL 环境基础信息（非敏感）。",
    "default_distro": "",
    "project_root": "",
    "notes": [],
}


def validate_namespace(namespace: str) -> str:
    namespace = namespace or DEFAULT_NAMESPACE
    if not _NAMESPACE_RE.fullmatch(namespace) or namespace.startswith("."):
        raise ValueError(f"Invalid namespace: {namespace!r}")
    return namespace


def namespace_dir(namespace: str = DEFAULT_NAMESPACE, create: bool = False) -> Path:
    path = PHYSIMX_ROOT / validate_namespace(namespace)
    if create:
        path.mkdir(parents=True, exist_ok=True)
        _lock_down(path)
    return path


def _lock_down(path: Path) -> None:
    try:
        import os

        if os.name == "posix":
            path.chmod(0o700 if path.is_dir() else 0o600)
    except OSError:
        pass
