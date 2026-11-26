"""Path helpers rooted at the scenarios directory."""

from __future__ import annotations

from pathlib import Path

SCENARIOS_ROOT = Path(__file__).resolve().parents[1]
FAC_ROOT = SCENARIOS_ROOT.parent


def resolve_scenario_path(relative: str) -> Path:
    """Resolve a path relative to scenarios/ while rejecting traversal."""
    target = (SCENARIOS_ROOT / relative).resolve()
    if target != SCENARIOS_ROOT and SCENARIOS_ROOT not in target.parents:
        raise ValueError(f"Path escaped scenarios root: {relative}")
    return target
