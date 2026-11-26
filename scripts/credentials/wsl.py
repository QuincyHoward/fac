#!/usr/bin/env python3
"""管理非敏感的 WSL 环境配置。"""

from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import runpy
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.wsl", run_name="__main__")
    raise SystemExit(0)

import argparse
import copy
import json

from ._config import DEFAULT_NAMESPACE, DEFAULT_WSL_CONFIG
from ._core import config_path, load_json, save_json

FILE_NAME = "wsl_config.json"


def load(namespace: str = DEFAULT_NAMESPACE) -> dict:
    data = load_json(config_path(namespace, FILE_NAME), copy.deepcopy(DEFAULT_WSL_CONFIG))
    return data if isinstance(data, dict) else copy.deepcopy(DEFAULT_WSL_CONFIG)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", help="打印当前 WSL 配置。")
    setter = sub.add_parser("set", help="设置 WSL 配置项。")
    setter.add_argument("--default-distro", help="默认 WSL 发行版名称。")
    setter.add_argument("--project-root", help="WSL 内的项目根目录。")
    setter.add_argument("--note", action="append", default=[], help="追加备注，可重复。")
    args = parser.parse_args(argv)

    data = load(args.namespace)
    if args.command == "show":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if args.default_distro:
        data["default_distro"] = args.default_distro
    if args.project_root:
        data["project_root"] = args.project_root
    if args.note:
        notes = data.setdefault("notes", [])
        notes.extend(args.note)
    save_json(config_path(args.namespace, FILE_NAME), data)
    print(f"WSL 配置已写入：{config_path(args.namespace, FILE_NAME)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
