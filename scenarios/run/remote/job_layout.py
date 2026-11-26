"""作业目录拓扑与资源指令。"""

from __future__ import annotations

import posixpath
import re
from dataclasses import dataclass
from datetime import datetime

from ..env.devices import fac_remote_dir, sim_user


@dataclass(frozen=True)
class JobLayout:
    run_id: str
    home: str
    sim_user: str
    fac_root: str
    work_root: str
    archive_root: str
    scratch_root: str

    @classmethod
    def create(
        cls,
        home: str,
        namespace: str = "specx",
        run_id: str = "",
        scratch_base: str = "",
    ) -> "JobLayout":
        run_id = run_id or f"fac_{datetime.now():%Y%m%d_%H%M%S}"
        user = sim_user(namespace)
        root = posixpath.join(home, user, "fac", "fac")
        return cls(
            run_id=run_id,
            home=home,
            sim_user=user,
            fac_root=root,
            work_root=posixpath.join(home, user, "fac_jobs", run_id, "work"),
            archive_root=posixpath.join(home, user, "fac_jobs", run_id, "archive"),
            scratch_root=(scratch_base or posixpath.join(home, user, "fac_jobs", run_id, "scratch")),
        )

    def job_script(self) -> str:
        return posixpath.join(self.home, self.sim_user, "fac_jobs", self.run_id, "submit.sbatch")


def parse_job_id(text: str) -> str:
    match = re.search(r"Submitted batch job\s+(\d+)", text)
    return match.group(1) if match else ""
