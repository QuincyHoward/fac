"""HPC in-situ execution: called on the login node, never SSHes to itself."""

from __future__ import annotations

import subprocess
from typing import Sequence

from ..env.devices import sim_user
from ..env.resource_config import resource_spec
from ..execution import ExecOptions, SceneSpec
from ..remote.job_layout import JobLayout
from ..remote.job_scripts import render_sbatch
from ..remote.job_submit import local_job_dir, write_job_file


def run_insitu(scene: SceneSpec, options: ExecOptions, args: Sequence[str]) -> int:
    spec = resource_spec(options.cores)
    layout = JobLayout.create(
        f"/home/{sim_user(options.namespace)}",
        options.namespace,
        options.run_id,
    )
    body = render_sbatch(scene, options, spec, layout, args)
    job_file = write_job_file(local_job_dir(scene), f"{scene.name}_{layout.run_id}.sbatch", body)
    print(f"作业脚本：{job_file}")
    if options.dry_run:
        return 0
    result = subprocess.run(["sbatch", str(job_file)], check=False)
    return result.returncode
