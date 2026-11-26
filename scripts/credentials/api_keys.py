#!/usr/bin/env python3
"""管理 api.<service>.api_key 形式的通用 API Key。"""

from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import runpy
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.api_keys", run_name="__main__")
    raise SystemExit(0)

import argparse
import json
import re

from ._config import DEFAULT_NAMESPACE
from ._core import delete, get, list_all, set

_SERVICE_RE = re.compile(r"^[a-z0-9_-]+$")


def _ask(prompt: str, eof: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消输入。")
        return eof


def key_for(service: str) -> str:
    service = service.lower()
    if not _SERVICE_RE.fullmatch(service):
        raise ValueError(f"服务名无效：{service!r}")
    return f"api.{service}.api_key"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sub = parser.add_subparsers(dest="command", required=True)
    setter = sub.add_parser("set", help="设置 API Key。")
    setter.add_argument("service")
    show = sub.add_parser("show", help="查看脱敏后的 API Key。")
    show.add_argument("service")
    deleter = sub.add_parser("delete", help="删除 API Key。")
    deleter.add_argument("service")
    sub.add_parser("list", help="列出 API Key 条目，值脱敏。")
    args = parser.parse_args(argv)

    try:
        if args.command == "list":
            data = {k: v for k, v in list_all(args.namespace).items() if k.startswith("api.")}
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        key = key_for(args.service)
        if args.command == "set":
            value = _ask(f"{args.service} API Key（输入一次）: ")
            if not value:
                print("API Key 为空，未保存。")
                return 2
            set(args.namespace, key, {"api_key": value})
            print(f"已保存：{key}，展示时脱敏。")
            return 0
        if args.command == "show":
            data = get(args.namespace, key)
            if not data:
                print("尚未配置该 API Key。")
                return 1
            if isinstance(data, dict):
                data = {k: ("****" if "key" in k or "token" in k else v) for k, v in data.items()}
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        if args.command == "delete":
            print("已删除" if delete(args.namespace, key) else "未找到该条目")
            return 0
    except ValueError as exc:
        print(exc)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
