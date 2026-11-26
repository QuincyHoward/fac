#!/usr/bin/env python3
"""Audit README coverage and relative Markdown links."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"\]\(([^)]+)\)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Project root to audit.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    readmes = sorted(root.rglob("README.md"))
    readme_dirs = {path.parent.resolve() for path in readmes}

    missing = []
    for directory in root.rglob("*"):
        if not directory.is_dir():
            continue
        rel = directory.relative_to(root)
        parts = set(rel.parts)
        if parts & {"__pycache__", "build", "dist", ".git"}:
            continue
        if directory.resolve() not in readme_dirs:
            missing.append(str(rel).replace("\\", "/") or ".")

    broken = []
    for readme in readmes:
        text = readme.read_text(encoding="utf-8", errors="replace")
        for target in LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (readme.parent / path_part).resolve()
            if not resolved.exists():
                broken.append(f"{readme.relative_to(root)} -> {target}")

    print(f"README files: {len(readmes)}")
    print("Directories without README:")
    print("\n".join(missing) if missing else "  none")
    print("Broken relative links:")
    print("\n".join(broken) if broken else "  none")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
