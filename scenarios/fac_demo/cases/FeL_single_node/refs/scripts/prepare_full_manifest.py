#!/usr/bin/env python3
"""Create a literature figure manifest that points at the full-physics FAC figures."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "figures"


def main():
    manifest = json.loads((BASE / "figure_manifest.json").read_text(encoding="utf-8"))
    for item in manifest:
        counterpart = item.get("fac_counterpart", "")
        if counterpart.startswith("opacity/outputs/figures/"):
            item["fac_counterpart"] = counterpart.replace("opacity/outputs/", "opacity_full/outputs/", 1)
        item.pop("side_by_side", None)
        item.pop("side_by_side_ok", None)
    out = BASE / "figure_manifest_full.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out, len(manifest))


if __name__ == "__main__":
    main()
