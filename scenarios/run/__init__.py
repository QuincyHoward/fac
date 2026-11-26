"""FAC execution layer: scene-agnostic local/wsl/HPC runners."""

from .execution import EXEC_TARGETS, ExecOptions, ExecutionPolicy, SceneSpec, explain_target, resolve_target, run_scene

__all__ = [
    "EXEC_TARGETS",
    "ExecOptions",
    "ExecutionPolicy",
    "SceneSpec",
    "explain_target",
    "resolve_target",
    "run_scene",
]
