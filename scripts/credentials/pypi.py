#!/usr/bin/env python3
"""管理 PyPI / TestPyPI 发布令牌。"""

from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import runpy
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.pypi", run_name="__main__")
    raise SystemExit(0)

import argparse
import json

from ._config import DEFAULT_NAMESPACE
from ._core import get, mask_secret, set

INDEXES = ("pypi", "testpypi")


def _ask(prompt: str, eof: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消输入。")
        return eof


def setup(namespace: str = DEFAULT_NAMESPACE, index: str = "pypi") -> int:
    if index not in INDEXES:
        print("索引只能是 pypi 或 testpypi。")
        return 2
    token = _ask(f"{index} API Token（输入一次，回车跳过）: ")
    if not token:
        print("Token 为空，未保存。")
        return 2
    set(namespace, index, {"token": token, "username": "__token__"})
    print(f"{index} Token 已保存，展示时脱敏。")
    return 0


def show(namespace: str = DEFAULT_NAMESPACE, index: str = "pypi") -> int:
    if index not in INDEXES:
        print("索引只能是 pypi 或 testpypi。")
        return 2
    data = get(namespace, index)
    if not data:
        print(f"尚未配置 {index} Token。")
        return 1
    print(json.dumps(mask_secret(data), ensure_ascii=False, indent=2))
    return 0


def get_config(namespace: str = DEFAULT_NAMESPACE, index: str = "pypi") -> dict[str, str] | None:
    data = get(namespace, index)
    if not isinstance(data, dict) or not data.get("token"):
        return None
    return {"username": data.get("username") or "__token__", "password": str(data["token"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("setup", "show"):
        item = sub.add_parser(command)
        item.add_argument("index", choices=INDEXES, nargs="?", default="pypi")
    args = parser.parse_args(argv)
    return setup(args.namespace, args.index) if args.command == "setup" else show(args.namespace, args.index)


if __name__ == "__main__":
    raise SystemExit(main())
