#!/usr/bin/env python3
"""管理 Gitee 令牌，默认脱敏展示。"""

from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import runpy
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.gitee", run_name="__main__")
    raise SystemExit(0)

import argparse
import json

from ._config import DEFAULT_NAMESPACE
from ._core import get, mask_secret, set

KEY = "gitee.token"


def _ask(prompt: str, eof: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消输入。")
        return eof


def setup(namespace: str = DEFAULT_NAMESPACE) -> int:
    token = _ask("Gitee 私人访问令牌（输入一次）: ")
    if not token:
        print("令牌为空，未保存。")
        return 2
    username = _ask("Gitee 用户名（可选）: ")
    set(namespace, KEY, {"token": token, "username": username})
    print("Gitee 令牌已保存，展示时脱敏。")
    return 0


def show(namespace: str = DEFAULT_NAMESPACE) -> int:
    data = get(namespace, KEY)
    if not data:
        print("尚未配置 Gitee 令牌。")
        return 1
    print(json.dumps(mask_secret(data), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("setup", help="设置 Gitee 令牌。")
    sub.add_parser("show", help="查看脱敏后的 Gitee 凭据。")
    args = parser.parse_args(argv)
    return setup(args.namespace) if args.command == "setup" else show(args.namespace)


if __name__ == "__main__":
    raise SystemExit(main())
