"""Resolve logical anchors from the scenarios anchor table."""

from __future__ import annotations

from pathlib import Path

from common.manifest import load_json
from common.paths import SCENARIOS_ROOT

ANCHORS = SCENARIOS_ROOT / "_scene_anchors.json"


def load_anchors(path: Path | None = None) -> dict[str, str]:
    source = path or ANCHORS
    if not source.is_file():
        return {}
    data = load_json(source)
    return {key: str(value) for key, value in data.items() if not key.startswith("_")}


def resolve_anchor(name: str, path: Path | None = None) -> Path:
    anchors = load_anchors(path)
    if name not in anchors:
        raise KeyError(f"Unknown anchor: {name}")
    target = (SCENARIOS_ROOT / anchors[name]).resolve()
    if target != SCENARIOS_ROOT and SCENARIOS_ROOT not in target.parents:
        raise ValueError(f"Anchor escaped scenarios root: {name}")
    return target
