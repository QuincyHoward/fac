"""Discover scenes by directory manifests."""

from __future__ import annotations

from pathlib import Path

from common.scene import Scene
from common.paths import SCENARIOS_ROOT


def discover_scenes(base: Path | None = None) -> list[Scene]:
    root = base or SCENARIOS_ROOT
    scenes = []
    for manifest in sorted(root.rglob("scene.json")):
        scenes.append(Scene.from_dir(manifest.parent))
    return scenes


def find_scene(name: str, base: Path | None = None) -> Scene | None:
    for scene in discover_scenes(base):
        if scene.name == name or scene.path.name == name:
            return scene
    return None
