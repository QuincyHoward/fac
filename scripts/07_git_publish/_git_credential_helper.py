#!/usr/bin/env python3
"""Git credential helper：只向 gitee.com 提供 Gitee 凭据。

凭据从 scripts/credentials 的 namespace 存储读取，经 stdin/stdout 管道传递，
不写入 .git/config，也不出现在 git 命令行参数中。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from credentials._config import DEFAULT_NAMESPACE  # noqa: E402
from credentials._core import get as get_secret  # noqa: E402


def _read_request() -> dict[str, str]:
    request: dict[str, str] = {}
    for raw in sys.stdin:
        line = raw.rstrip("\r\n")
        if not line:
            break
        if "=" in line:
            key, value = line.split("=", 1)
            request[key.strip()] = value.strip()
    return request


def main() -> int:
    request = _read_request()
    host = (request.get("host") or "").lower()
    if host and "gitee.com" not in host:
        return 0

    namespace = (
        os.environ.get("FAC_CRED_NAMESPACE") or request.get("namespace") or DEFAULT_NAMESPACE
    ).strip() or DEFAULT_NAMESPACE
    data = get_secret(namespace, "gitee.token", {})
    if isinstance(data, dict):
        token = str(data.get("token") or "").strip()
        login = str(data.get("login") or data.get("username") or "").strip()
    else:
        token = str(data or "").strip()
        login = ""

    if not token:
        return 0

    lines: list[str] = []
    if login:
        lines.append(f"username={login}")
    lines.append(f"password={token}")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
