"""SLURM 操作唯一下沉点。"""

from __future__ import annotations

import time

from .job_layout import parse_job_id
from .session import RemoteSession


def submit(session: RemoteSession, job_script: str, timeout: int = 300) -> str:
    rc, out, err = session.exec(f"sbatch {job_script}", timeout=timeout)
    if rc != 0:
        raise RuntimeError(f"sbatch 失败：{err.strip()}")
    return parse_job_id(out)


def job_state(session: RemoteSession, job_id: str) -> str:
    rc, out, _ = session.exec(f"sacct -j {job_id} -X --noheader --format=State", timeout=120)
    if rc == 0 and out.strip():
        return out.strip().splitlines()[0].strip()
    rc, out, _ = session.exec(f"squeue -h -j {job_id} -o %T", timeout=120)
    return out.strip().splitlines()[0].strip() if rc == 0 and out.strip() else "UNKNOWN"


def wait_for_job(session: RemoteSession, job_id: str, interval: int = 30, timeout: int = 7200) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        state = job_state(session, job_id)
        print(f"[{time.strftime('%H:%M:%S')}] state={state}", flush=True)
        if state in {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY"}:
            return state
        time.sleep(interval)
    return "WAIT_TIMEOUT"


def latest_job_by_name(session: RemoteSession, name: str) -> str:
    rc, out, _ = session.exec(f"squeue -h -n {name} -o %A", timeout=120)
    if rc == 0 and out.strip():
        return out.strip().splitlines()[0]
    rc, out, _ = session.exec(f"sacct -X --noheader --format=JobID,JobName%50 | grep {name} | tail -1", timeout=120)
    return out.split()[0] if rc == 0 and out.strip() else ""
