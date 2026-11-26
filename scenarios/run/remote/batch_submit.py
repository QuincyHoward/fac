"""提交独立参数矩阵作业：单一 SSH 会话，多个 SLURM 作业并行排队运行。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..execution import ExecOptions, SceneSpec
from .job_submit import prepare_submission
from .session import RemoteSession
from .slurm_control import submit as slurm_submit


def load_matrix(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "combinations" not in data:
        raise ValueError("矩阵配置缺少 combinations")
    return data


def scene_from_name(name: str, root: Path) -> SceneSpec:
    path = root / "scenarios" / "fac_demo" / "cases" / name
    data = json.loads((path / "scene.json").read_text(encoding="utf-8"))
    return SceneSpec(
        name=data.get("name", name),
        path=path,
        archetype=data.get("archetype", "unknown"),
        entry=data.get("entry", "run.py"),
    )


def submit_matrix(
    config_path: Path,
    root: Path,
    namespace: str = "specx",
    credential: str = "flash_ssh",
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_matrix(config_path)
    scene = scene_from_name(config["scene"], root)
    walltime = config.get("walltime", "03:00:00")
    rows = []

    with RemoteSession(namespace, credential) as session:
        home = session.home()
        for combo in config["combinations"]:
            cores = int(combo["cores"])
            mpi = int(combo["mpi"])
            run_id = f"{scene.name}_c{cores}m{mpi}"
            options = ExecOptions(
                namespace=namespace,
                credential=credential,
                cores=cores,
                mpi=mpi,
                walltime=walltime,
                dry_run=dry_run,
                run_id=run_id,
            )
            info = prepare_submission(scene, options, (), cores, home, session)
            remote_job = ""
            job_id = ""
            if not dry_run:
                session.mkdir_p(str(Path(info["remote_job"]).parent).replace("\\", "/"))
                remote_job = session.upload(info["local_job"], info["remote_job"])
                job_id = slurm_submit(session, remote_job)
            rows.append(
                {
                    "cores": cores,
                    "mpi": mpi,
                    "run_id": run_id,
                    "job_name": info["job_name"],
                    "job_id": job_id,
                    "job_script": str(info["local_job"]),
                    "remote_script": remote_job or info["remote_job"],
                    "remote_dir": info["layout"].archive_root,
                    "walltime": walltime,
                }
            )
    return {
        "scene": scene.name,
        "walltime": walltime,
        "baseline": config.get("baseline", {}),
        "dry_run": dry_run,
        "jobs": rows,
    }
