"""Local and WSL scene execution."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from typing import Sequence

from ..env.resource_config import resolve_cores, resolve_mpi
from ..execution import SceneSpec


def allocate_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{datetime.now():%Y%m%d_%H%M%S}"


def build_command(scene: SceneSpec, args: Sequence[str], cores: str | int, mpi: str | int | None) -> list[str]:
    n = resolve_cores(cores)
    m = resolve_mpi(mpi, n)
    return [sys.executable, str(scene.path / scene.entry), "--cores", str(n), "--mpi", str(m), *args]


def run_local(scene: SceneSpec, args: Sequence[str], cores: str | int = "auto", mpi: str | int | None = None) -> int:
    command = build_command(scene, args, cores, mpi)
    print("+", " ".join(command))
    return subprocess.run(command, cwd=scene.path, check=False).returncode


def run_wsl(scene: SceneSpec, args: Sequence[str], cores: str | int = "auto", mpi: str | int | None = None) -> int:
    from shutil import which

    if not which("wsl"):
        print("未找到 wsl，可执行 local 目标。")
        return 2
    command = build_command(scene, args, cores, mpi)
    wsl_cmd = ["wsl", "--", *command]
    print("+", " ".join(wsl_cmd))
    return subprocess.run(wsl_cmd, cwd=scene.path, check=False).returncode
