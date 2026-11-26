#!/usr/bin/env python3
"""One-click entry for the structure + radiative transition archetype."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    data = json.loads((HERE / "scene.json").read_text(encoding="utf-8"))
    print("Scene:", data["name"])
    print("Archetype:", data["archetype"])
    print("Expected outputs:", ", ".join(data.get("expected_outputs", [])))
    print("Workflow: Config -> OptimizeRadial -> Structure -> TransitionTable -> check_en/check_tr")
    print("Template mode: no FAC calculation executed. Add a real script here when ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
