"""通用作业渲染与提交服务：只认识 SceneSpec，不认识物理场景。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from ..env.devices import sim_user
from ..env.resource_config import resource_spec, resolve_cores, resolve_mpi
from ..execution import ExecOptions, SceneSpec
from .job_layout import JobLayout
from .job_scripts import render_sbatch
from .session import RemoteSession
from .slurm_control import submit as slurm_submit


def write_job_file(local_dir: Path, name: str, body: str) -> Path:
    local_dir.mkdir(parents=True, exist_ok=True)
    path = local_dir / name
    path.write_bytes(body.replace("\r\n", "\n").encode("utf-8"))
    return path


def local_job_dir(scene: SceneSpec) -> Path:
    """本地作业脚本按发起场景归档，避免污染调用方工作目录。"""
    return scene.path / "hpc_jobs"


def prepare_submission(
    scene: SceneSpec,
    options: ExecOptions,
    args: Sequence[str],
    cores: str | int,
    home: str,
    session: RemoteSession | None = None,
) -> dict[str, Any]:
    mpi = resolve_mpi(options.mpi, resolve_cores(cores))
    spec = resource_spec(cores, mpi, options.walltime)
    layout = JobLayout.create(home, options.namespace, options.run_id)
    job_name = f"fac_{scene.name}_{spec.ntasks}c_{spec.mpi_threads}m"
    body = render_sbatch(scene, options, spec, layout, args, job_name=job_name)
    local_job = write_job_file(local_job_dir(scene), f"{job_name}_{layout.run_id}.sbatch", body)
    return {
        "spec": spec,
        "layout": layout,
        "job_name": job_name,
        "body": body,
        "local_job": local_job,
        "remote_job": layout.job_script(),
    }


def submit_scene(scene: SceneSpec, options: ExecOptions, args: Sequence[str] = ()) -> dict[str, Any]:
    if options.dry_run:
        cores = resolve_cores(options.cores)
        info = prepare_submission(
            scene,
            options,
            args,
            cores,
            f"/home/{sim_user(options.namespace)}",
        )
        spec = info["spec"]
        return {
            "job_id": "",
            "dry_run": True,
            "job_script": str(info["local_job"]),
            "remote_script": info["remote_job"],
            "run_id": info["layout"].run_id,
            "job_name": info["job_name"],
            "cores": spec.ntasks,
            "mpi": spec.mpi_threads,
        }

    with RemoteSession(options.namespace, options.credential) as session:
        home = session.home()
        cores = session.exec("nproc")[1].strip() if options.cores == "auto" else options.cores
        info = prepare_submission(scene, options, args, cores, home, session)
        session.mkdir_p(str(Path(info["remote_job"]).parent).replace("\\", "/"))
        remote_job = session.upload(info["local_job"], info["remote_job"])
        job_id = slurm_submit(session, remote_job)
        spec = info["spec"]
        return {
            "job_id": job_id,
            "dry_run": False,
            "job_script": str(info["local_job"]),
            "remote_script": remote_job,
            "remote_dir": info["layout"].archive_root,
            "run_id": info["layout"].run_id,
            "job_name": info["job_name"],
            "cores": spec.ntasks,
            "mpi": spec.mpi_threads,
        }
