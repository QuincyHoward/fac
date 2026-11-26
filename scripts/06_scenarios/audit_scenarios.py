#!/usr/bin/env python3
"""Validate scenario manifests and the relative anchor table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT / "scenarios"), help="Scenarios directory.")
    args = parser.parse_args(argv)

    base = Path(args.root).resolve()
    if not base.is_dir():
        print(f"Scenarios directory not found: {base}")
        return 2

    errors = []
    manifests = sorted(base.rglob("scene.json"))
    for manifest in manifests:
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{manifest}: {exc}")
            continue
        for key in ("name", "description", "archetype"):
            if key not in data:
                errors.append(f"{manifest}: missing '{key}'")

    anchors = base / "_scene_anchors.json"
    if anchors.is_file():
        try:
            json.loads(anchors.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{anchors}: {exc}")

    print(f"Scenes found: {len(manifests)}")
    print("Errors:")
    print("\n".join(errors) if errors else "  none")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
