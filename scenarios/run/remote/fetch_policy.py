"""默认只回传小摘要，不回传 GB 级产物。"""

from __future__ import annotations

from typing import Iterable

DEFAULT_PATTERNS = (
    "summary.json",
    "manifest.txt",
    "*.log",
    "*.sbatch",
    "checks/*.txt",
)


def select_fetch_files(files: Iterable[str], patterns: Iterable[str] = DEFAULT_PATTERNS) -> list[str]:
    import fnmatch

    selected = []
    for item in files:
        if any(fnmatch.fnmatch(item, pattern) for pattern in patterns):
            selected.append(item)
    return selected
