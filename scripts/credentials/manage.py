#!/usr/bin/env python3
"""FAC 凭证管理统一命令行与交互菜单（输出默认脱敏）。"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.manage", run_name="__main__")
    raise SystemExit(0)

from ._config import DEFAULT_NAMESPACE, namespace_dir, validate_namespace
from ._core import delete, get, get_manager, list_all, masked_list, set
from . import api_keys, gitee, hpc_accounts, pypi, wsl


def _ask(prompt: str, eof: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消输入。")
        return eof


def _print_header(namespace: str) -> None:
    manager = get_manager(namespace)
    keys = [k for k in list_all(namespace) if k != "__meta__"]
    print(f"\n  {'=' * 56}")
    print("  FAC 凭证管理中心")
    print(f"  当前命名空间 : {namespace}")
    print(f"  存储目录     : {namespace_dir(namespace)}")
    print(f"  已保存条目   : {', '.join(keys) if keys else '无'}")
    if manager.load_error:
        print(f"  读取状态     : 错误：{manager.load_error}")
    print(f"  {'=' * 56}")


def cmd_status(namespace: str) -> int:
    base = namespace_dir(namespace)
    manager = get_manager(namespace)
    keys = [k for k in list_all(namespace) if k != "__meta__"]
    print(f"命名空间       : {namespace}")
    print(f"存储目录       : {base}")
    print(f"加密库         : {'存在' if (base / 'credentials.enc').exists() else '不存在'}")
    print(f"HPC 配置       : {'存在' if (base / 'hpc_accounts.json').exists() else '不存在'}")
    print(f"WSL 配置       : {'存在' if (base / 'wsl_config.json').exists() else '不存在'}")
    print(f"凭据条目数     : {len(keys)}")
    if manager.load_error:
        print("读取错误       :", manager.load_error)
        return 1
    return 0


def cmd_list(namespace: str) -> int:
    print(json.dumps(masked_list(namespace), ensure_ascii=False, indent=2))
    return 0


def cmd_show(namespace: str, key: str) -> int:
    from ._core import mask_secret

    value = get(namespace, key)
    if value is None:
        print("未找到该条目。")
        return 1
    print(json.dumps(mask_secret(value), ensure_ascii=False, indent=2))
    return 0


def cmd_set(namespace: str, key: str, value: str | None = None) -> int:
    value = value if value is not None else _ask("值（输入一次）: ")
    if value == "":
        print("值为空，未保存。")
        return 2
    set(namespace, key, value)
    print(f"已保存：{key}")
    return 0


def cmd_delete(namespace: str, key: str) -> int:
    print("已删除" if delete(namespace, key) else "未找到该条目")
    return 0


def _setup_gitee(namespace: str) -> int:
    return gitee.setup(namespace)


def _setup_wsl(namespace: str) -> int:
    print("  发行版名称请用 `wsl -l -v` 查看；项目根填 WSL 内路径，如 /home/<user>/fac。")
    distro = _ask("  默认 WSL 发行版: ")
    root = _ask("  WSL 项目根目录: ")
    args = ["--namespace", namespace, "set"]
    if distro:
        args += ["--default-distro", distro]
    if root:
        args += ["--project-root", root]
    return wsl.main(args)


def _setup_hpc(namespace: str) -> int:
    return hpc_accounts.interactive_setup(namespace)


def _setup_api(namespace: str) -> int:
    service = _ask("  服务名: ")
    if not service:
        return 2
    return api_keys.main(["--namespace", namespace, "set", service])


def _setup_pypi(namespace: str) -> int:
    index = _ask("  PyPI 或 TestPyPI [pypi/testpypi]: ") or "pypi"
    return pypi.setup(namespace, index)


def _setup_userpass(namespace: str) -> int:
    old_user = str(get(namespace, "account.username", "") or "")
    user_prompt = f"  用户名 [{old_user}]: " if old_user else "  用户名: "
    username = _ask(user_prompt)
    password = _ask("  密码（输入一次，回车跳过）: ")
    if username:
        set(namespace, "account.username", username)
    if password:
        set(namespace, "account.password", password)
    if username or password:
        print("  已保存用户名/密码条目（展示时脱敏）。")
    else:
        print("  未输入，未保存。")
    return 0


def setup_menu(namespace: str) -> int:
    while True:
        print("\n  凭据设置")
        print("    1) Gitee 令牌")
        print("    2) WSL 配置")
        print("    3) HPC 账户基础信息与密码")
        print("    4) API Key")
        print("    5) PyPI / TestPyPI 令牌")
        print("    6) 用户名与密码")
        print("    0) 返回")
        choice = _ask("  选择 [0-6]: ", "0")
        if choice == "0":
            return 0
        if choice == "1":
            _setup_gitee(namespace)
        elif choice == "2":
            _setup_wsl(namespace)
        elif choice == "3":
            _setup_hpc(namespace)
        elif choice == "4":
            _setup_api(namespace)
        elif choice == "5":
            _setup_pypi(namespace)
        elif choice == "6":
            _setup_userpass(namespace)
        else:
            print("  无效选择。")


def interactive_menu(namespace: str) -> int:
    while True:
        _print_header(namespace)
        print("  1) 状态")
        print("  2) 列出凭据（脱敏）")
        print("  3) 查看条目（脱敏）")
        print("  4) 设置普通键值")
        print("  5) 删除条目")
        print("  6) 常用凭据设置")
        print("  n) 切换命名空间")
        print("  0) 退出")
        choice = _ask("  选择: ", "0").lower()
        if choice == "0":
            return 0
        if choice == "1":
            cmd_status(namespace)
        elif choice == "2":
            cmd_list(namespace)
        elif choice == "3":
            key = _ask("  键名: ")
            if key:
                cmd_show(namespace, key)
        elif choice == "4":
            key = _ask("  键名: ")
            if key:
                cmd_set(namespace, key)
        elif choice == "5":
            key = _ask("  键名: ")
            if key:
                cmd_delete(namespace, key)
        elif choice == "6":
            setup_menu(namespace)
        elif choice == "n":
            new_ns = _ask(f"  命名空间 [{namespace}]: ")
            if new_ns:
                try:
                    namespace = validate_namespace(new_ns)
                except ValueError as exc:
                    print(" ", exc)
        else:
            print("  无效选择。")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE, help="~/.physimx 下的命名空间，默认 specx。")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("menu", help="打开交互式凭证菜单。")
    sub.add_parser("status", help="查看命名空间状态，不显示密钥。")
    sub.add_parser("list", help="列出凭据，值脱敏。")
    show = sub.add_parser("show", help="查看单个条目，值脱敏。")
    show.add_argument("key")
    setter = sub.add_parser("set", help="设置凭据；省略值时交互式输入。")
    setter.add_argument("key")
    setter.add_argument("value", nargs="?")
    deleter = sub.add_parser("delete", help="删除一个凭据条目。")
    deleter.add_argument("key")
    sub.add_parser("setup", help="打开凭据设置子菜单。")

    args = parser.parse_args(argv)
    namespace = validate_namespace(args.namespace)

    if args.command is None or args.command == "menu":
        return interactive_menu(namespace)
    if args.command == "status":
        return cmd_status(namespace)
    if args.command == "list":
        return cmd_list(namespace)
    if args.command == "show":
        return cmd_show(namespace, args.key)
    if args.command == "set":
        return cmd_set(namespace, args.key, args.value)
    if args.command == "delete":
        return cmd_delete(namespace, args.key)
    if args.command == "setup":
        return setup_menu(namespace)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
