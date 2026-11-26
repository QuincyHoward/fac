"""Scene runner with dry-run support."""

from __future__ import annotations

import subprocess
import sys
from typing import Sequence

from common.scene import Scene


def run_scene(scene: Scene, extra_args: Sequence[str] = (), dry_run: bool = True) -> int:
    command = [sys.executable, scene.entry, *extra_args]
    print("Scene:", scene.name)
    print("Directory:", scene.path)
    print("Command:", " ".join(command))
    if dry_run:
        print("Dry run: command not executed.")
        return 0
    result = subprocess.run(command, cwd=scene.path, check=False)
    return result.returncode
