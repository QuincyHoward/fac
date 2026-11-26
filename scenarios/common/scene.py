"""Scene model and loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .manifest import load_json


@dataclass(frozen=True)
class Scene:
    path: Path
    name: str
    archetype: str
    description: str
    entry: str

    @classmethod
    def from_dir(cls, directory: Path) -> "Scene":
        data = load_json(directory / "scene.json")
        return cls(
            path=directory,
            name=str(data.get("name", directory.name)),
            archetype=str(data.get("archetype", "unknown")),
            description=str(data.get("description", "")),
            entry=str(data.get("entry", "run.py")),
        )

    def summary(self) -> str:
        rel = self.path.name
        return f"{self.name}\t[{self.archetype}]\t{rel}\t{self.description}"
