#!/usr/bin/env python3
"""List abstract FAC demo archetypes from the workflow skill reference."""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REF = ROOT / "skills" / "fac-demo-workflow" / "references" / "demo-archetypes.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", default=str(REF), help="Path to demo-archetypes.md.")
    args = parser.parse_args(argv)

    path = Path(args.reference).resolve()
    if not path.is_file():
        print(f"Reference not found: {path}")
        return 2

    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] in {"原型", "---"} or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells[0])

    for row in rows:
        print(row)
    print(f"\nTotal archetypes: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
