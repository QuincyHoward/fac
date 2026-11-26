#!/usr/bin/env python3
"""检查 FAC 构建工具链与 PFAC 模块可见性。"""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import sys


def module_visible(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="工具缺失时返回非零退出码。")
    args = parser.parse_args(argv)

    print("Python:", sys.version.replace("\n", " "))
    missing = []
    for tool in ("gcc", "gfortran", "make"):
        path = shutil.which(tool)
        print(f"{tool}: {path or '缺失'}")
        if path is None:
            missing.append(tool)

    for module in ("pfac.fac", "pfac.crm", "pfac.pol", "pfac.util"):
        print(f"{module}: {'可见' if module_visible(module) else '不可见'}")

    if missing:
        print("\n缺失核心工具：", ", ".join(missing))
        print("请在具备 gcc、gfortran 与 GNU make 的 Linux/WSL 环境中构建。")
        return 1 if args.strict else 0
    print("\n核心工具链可用。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
