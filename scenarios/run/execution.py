"""FAC 场景统一执行契约。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

EXEC_TARGETS = ("local", "wsl", "hpc-remote", "hpc-insitu")
_ALIASES = {
    "hpc": "hpc-remote",
    "remote": "hpc-remote",
    "ssh": "hpc-remote",
    "slurm": "hpc-remote",
    "supercomputer": "hpc-remote",
    "insitu": "hpc-insitu",
}


@dataclass(frozen=True)
class ExecutionPolicy:
    allowed: tuple[str, ...] = EXEC_TARGETS
    preferred: str = "auto"
    nproc: str = "at_most"
    forbid_reason: str = ""


@dataclass(frozen=True)
class SceneSpec:
    name: str
    path: Path
    archetype: str = "unknown"
    entry: str = "run.py"
    policy: ExecutionPolicy = field(default_factory=ExecutionPolicy)


@dataclass(frozen=True)
class ExecOptions:
    mode: str = "auto"
    namespace: str = "specx"
    credential: str = "flash_ssh"
    stage: str = ""
    cores: str | int = "auto"
    mpi: str | int | None = None
    walltime: str = "12:00:00"
    dry_run: bool = False
    run_id: str = ""
    extra: tuple[str, ...] = ()


def normalize_target(value: str) -> str:
    value = (value or "").strip().lower()
    return _ALIASES.get(value, value)


def _slurm_available() -> bool:
    from shutil import which

    return which("sbatch") is not None and which("squeue") is not None


def resolve_target(scene: SceneSpec, options: ExecOptions) -> str:
    for candidate in (options.mode, os.environ.get("FAC_RUN_MODE", ""), scene.policy.preferred):
        target = normalize_target(candidate)
        if target and target != "auto":
            break
    else:
        if _slurm_available():
            target = "hpc-insitu"
        elif os.name == "nt":
            from shutil import which

            target = "wsl" if which("wsl") else "local"
        else:
            target = "local"

    if target not in EXEC_TARGETS:
        raise ValueError(f"未知执行目标：{target}")
    if target not in scene.policy.allowed:
        raise ValueError(f"场景 {scene.name} 不允许目标 {target}：{scene.policy.forbid_reason}")
    return target


def explain_target(scene: SceneSpec, options: ExecOptions) -> dict[str, Any]:
    try:
        target = resolve_target(scene, options)
        return {"ok": True, "target": target, "reason": "resolved by contract"}
    except ValueError as exc:
        return {"ok": False, "target": "", "reason": str(exc)}


def run_scene(scene: SceneSpec, options: ExecOptions, extra_args: Sequence[str] = ()) -> int:
    target = resolve_target(scene, options)
    args = list(extra_args) or list(options.extra)

    if target == "local":
        from .modes.runner import run_local

        return run_local(scene, args, cores=options.cores, mpi=options.mpi)
    if target == "wsl":
        from .modes.runner import run_wsl

        return run_wsl(scene, args, cores=options.cores, mpi=options.mpi)
    if target == "hpc-insitu":
        from .modes.hpc_insitu import run_insitu

        return run_insitu(scene, options, args)
    if target == "hpc-remote":
        from .remote.job_submit import submit_scene

        result = submit_scene(scene, options, args)
        return 0 if result.get("job_id") else 1
    raise ValueError(f"未实现执行目标：{target}")
