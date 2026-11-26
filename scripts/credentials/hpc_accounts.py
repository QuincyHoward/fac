#!/usr/bin/env python3
"""按命名空间管理 HPC 账户非敏感基础信息，密码写入加密库。"""

from __future__ import annotations

if __name__ == "__main__" and __package__ is None:
    import runpy
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    runpy.run_module("credentials.hpc_accounts", run_name="__main__")
    raise SystemExit(0)

import argparse
import copy
import json
from typing import Any

from ._config import DEFAULT_HPC_ACCOUNTS, DEFAULT_NAMESPACE
from ._core import config_path, load_json, save_json
from ._core import get as get_secret
from ._core import set as set_secret

FILE_NAME = "hpc_accounts.json"


def _ask(prompt: str, eof: str = "") -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n已取消输入。")
        return eof


def load(namespace: str = DEFAULT_NAMESPACE) -> dict[str, Any]:
    data = load_json(config_path(namespace, FILE_NAME), copy.deepcopy(DEFAULT_HPC_ACCOUNTS))
    if not isinstance(data, dict):
        return copy.deepcopy(DEFAULT_HPC_ACCOUNTS)
    data.setdefault("accounts", {})
    return data


def save(namespace: str, data: dict[str, Any]) -> None:
    save_json(config_path(namespace, FILE_NAME), data)


def password_key(name: str) -> str:
    return f"hpc.{name}.password"


def account_names(namespace: str = DEFAULT_NAMESPACE) -> list[str]:
    return sorted(load(namespace)["accounts"].keys())


def example() -> dict[str, Any]:
    return {
        "_comment": ["仅使用占位符；真实主机、账号与密码不要写入文档或示例。"],
        "accounts": {
            "hpc_ssh": {
                "title": "示例 HPC 账户",
                "ssh_username": "user@cluster",
                "username": "platform_user",
                "route_key": "example",
                "routes": [{"host": "ssh.example.com", "port": 22, "label": "线路 A"}],
            }
        },
    }


def set_basics(
    namespace: str,
    name: str,
    *,
    title: str | None = None,
    ssh_username: str | None = None,
    username: str | None = None,
    route_key: str | None = None,
    routes: list[dict[str, Any]] | None = None,
) -> None:
    data = load(namespace)
    account = data["accounts"].setdefault(name, {"routes": []})
    if title:
        account["title"] = title
    if ssh_username:
        account["ssh_username"] = ssh_username
    if username:
        account["username"] = username
    if route_key:
        account["route_key"] = route_key
    if routes is not None:
        account["routes"] = routes
    save(namespace, data)


def _print_account(name: str, account: dict[str, Any]) -> None:
    print(f"  账户       : {name}")
    print(f"  标题       : {account.get('title', '')}")
    print(f"  SSH 用户名 : {account.get('ssh_username', '')}")
    print(f"  专属用户名 : {account.get('username', '')}")
    print(f"  线路标识   : {account.get('route_key', '')}")
    routes = account.get("routes", [])
    if routes:
        print("  线路       :")
        for item in routes:
            print(f"    {item.get('host')}:{item.get('port', 22)}  {item.get('label', '')}")


def _collect_basics(existing: dict[str, Any]) -> tuple[str, str, str, str, list[dict[str, Any]]]:
    title_default = str(existing.get("title", ""))
    title = _ask(f"  标题 [{title_default}]: ") or title_default

    ssh_default = str(existing.get("ssh_username", ""))
    ssh_username = _ask(f"  SSH 用户名 [{ssh_default}]: ") or ssh_default

    user_default = str(existing.get("username", ""))
    dedicated_user = _ask(f"  专属用户名 [{user_default}]: ") or user_default

    key_default = str(existing.get("route_key", ""))
    route_key = _ask(f"  线路标识 [{key_default}]: ") or key_default

    old_routes = existing.get("routes", [])
    if old_routes:
        print("  当前线路：")
        for item in old_routes:
            print(f"    {item.get('host')}:{item.get('port', 22)}  {item.get('label', '')}")
    print("  录入新线路；主机留空表示保留原线路。")
    routes: list[dict[str, Any]] = []
    while True:
        host = _ask("  SSH 主机（回车结束）: ")
        if not host:
            break
        port_text = _ask("  SSH 端口 [22]: ") or "22"
        try:
            port = int(port_text)
        except ValueError:
            port = 22
        routes.append({"host": host, "port": port, "label": f"{host}:{port}"})
    if not routes:
        routes = old_routes
    return title, ssh_username, dedicated_user, route_key, routes


def interactive_setup(namespace: str = DEFAULT_NAMESPACE) -> int:
    print("\n  HPC 账户设置（仿 FLASH：基础信息明文 JSON，密码加密保存）")
    data = load(namespace)
    accounts = data["accounts"]

    names = sorted(accounts.keys())
    if names:
        print("  检测到已复制或已保存的 HPC 账户配置：")
        for index, item in enumerate(names, 1):
            account = accounts[item]
            print(f"    {index}) {item}  {account.get('title', '')}  {account.get('ssh_username', '')}")
        choice = _ask("  选择账户序号或输入账户名（回车默认第一个）: ")
        if choice.isdigit() and 1 <= int(choice) <= len(names):
            name = names[int(choice) - 1]
        elif choice:
            name = choice
        else:
            name = names[0]
    else:
        name = _ask("  账户名 [hpc_ssh]: ") or "hpc_ssh"

    existing = accounts.get(name, {})
    if existing:
        print("  已读取账户信息：")
        _print_account(name, existing)
        modify = _ask("  是否修改基础信息？[是/否，默认否]: ")
        if modify in {"是", "y", "Y", "yes", "YES"}:
            title, ssh_username, dedicated_user, route_key, routes = _collect_basics(existing)
        else:
            title = str(existing.get("title", ""))
            ssh_username = str(existing.get("ssh_username", ""))
            dedicated_user = str(existing.get("username", ""))
            route_key = str(existing.get("route_key", ""))
            routes = existing.get("routes", [])
    else:
        title, ssh_username, dedicated_user, route_key, routes = _collect_basics({})

    set_basics(
        namespace,
        name,
        title=title or None,
        ssh_username=ssh_username or None,
        username=dedicated_user or None,
        route_key=route_key or None,
        routes=routes,
    )

    key = password_key(name)
    if get_secret(namespace, key) is None:
        print("  该账户尚未设置密码。")
        password = _ask("  SSH 密码（输入一次，回车跳过）: ")
    else:
        print("  该账户密码已设置。")
        change = _ask("  是否重新设置密码？[是/否，默认否]: ")
        password = _ask("  新 SSH 密码（输入一次，回车跳过）: ") if change in {"是", "y", "Y", "yes", "YES"} else ""

    if password:
        set_secret(namespace, key, password)
        print("  SSH 密码已加密保存。")
    else:
        print("  未修改密码。")
    print(f"  HPC 基础信息已写入：{config_path(namespace, FILE_NAME)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default=DEFAULT_NAMESPACE)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", help="打印当前 HPC 非敏感配置。")
    sub.add_parser("list", help="列出已发现的 HPC 账户名。")
    sub.add_parser("example", help="打印占位符示例配置。")
    sub.add_parser("setup", help="自动读取现有配置；缺密码时交互式补录。")
    setter = sub.add_parser("set", help="设置一个账户的基础信息。")
    setter.add_argument("name")
    setter.add_argument("--title")
    setter.add_argument("--ssh-username")
    setter.add_argument("--username", help="专属用户名（非 SSH 用户名）。")
    setter.add_argument("--route-key")
    setter.add_argument("--route", action="append", default=[], help="主机:端口，可重复。")
    args = parser.parse_args(argv)

    if args.command == "show":
        print(json.dumps(load(args.namespace), ensure_ascii=False, indent=2))
        return 0
    if args.command == "list":
        print("\n".join(account_names(args.namespace)))
        return 0
    if args.command == "example":
        print(json.dumps(example(), ensure_ascii=False, indent=2))
        return 0
    if args.command == "setup":
        return interactive_setup(args.namespace)

    routes = []
    for item in args.route:
        host, _, port = item.partition(":")
        try:
            port_number = int(port) if port else 22
        except ValueError:
            port_number = 22
        routes.append({"host": host, "port": port_number, "label": f"{host}:{port_number}"})
    set_basics(
        args.namespace,
        args.name,
        title=args.title,
        ssh_username=args.ssh_username,
        username=args.username,
        route_key=args.route_key,
        routes=routes or None,
    )
    print(f"HPC 基础信息已写入：{config_path(args.namespace, FILE_NAME)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
