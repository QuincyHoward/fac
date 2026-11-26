"""Minimal output-table readers used by scenario explanations."""

from __future__ import annotations

from pathlib import Path


def read_table_lines(path: Path, limit: int = 40) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[:limit]


def describe_table(path: Path, limit: int = 12) -> str:
    lines = read_table_lines(path, limit)
    header = [line for line in lines if line.startswith(("#", "FAC", "Name", "NBlocks"))]
    return "\n".join(header) if header else "\n".join(lines[:3])
