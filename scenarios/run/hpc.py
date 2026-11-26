#!/usr/bin/env python3
"""FAC HPC CLI: status/submit/matrix/wait/nodes/download/route-test."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scenarios.run.execution import ExecOptions, SceneSpec  # noqa: E402
from scenarios.run.remote.artifacts import fetch_artifacts  # noqa: E402
from scenarios.run.remote.batch_submit import submit_matrix  # noqa: E402
from scenarios.run.remote.route_tester import test_routes  # noqa: E402
from scenarios.run.remote.session import RemoteSession  # noqa: E402
from scenarios.run.remote.slurm_control import job_state, wait_for_job  # noqa: E402


def load_scene(name: str) -> SceneSpec:
    path = ROOT / "scenarios" / "fac_demo" / "cases" / name
    data = json.loads((path / "scene.json").read_text(encoding="utf-8"))
    return SceneSpec(
        name=data.get("name", name),
        path=path,
        archetype=data.get("archetype", "unknown"),
        entry=data.get("entry", "run.py"),
    )


def print_rows(rows: list[dict]) -> None:
    for row in rows:
        print(
            f"{row['cores']}c/{row['mpi']}m\tjob_id={row['job_id']}\t"
            f"job_name={row['job_name']}\tremote_dir={row['remote_dir']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespace", default="specx")
    parser.add_argument("--credential", default="flash_ssh")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="查看作业状态。")
    status.add_argument("job")

    submit = sub.add_parser("submit", help="提交单个场景作业。")
    submit.add_argument("--scene", required=True)
    submit.add_argument("--cores", default="auto")
    submit.add_argument("--mpi", default="auto")
    submit.add_argument("--walltime", default="12:00:00")
    submit.add_argument("--run-id", default="")
    submit.add_argument("--stage", default="")
    submit.add_argument("-n", "--dry-run", action="store_true")
    submit.add_argument("extra", nargs="*")

    matrix = sub.add_parser("matrix", help="并行提交参数矩阵。")
    matrix.add_argument(
        "--config",
        default=str(ROOT / "scenarios/fac_demo/cases/FeL_single_node/matrix.json"),
    )
    matrix.add_argument("-n", "--dry-run", action="store_true")

    wait = sub.add_parser("wait", help="等待作业结束。")
    wait.add_argument("job")
    wait.add_argument("--timeout", type=int, default=7200)

    wait_many = sub.add_parser("wait-many", help="统一轮询多个作业。")
    wait_many.add_argument("jobs", nargs="+")
    wait_many.add_argument("--timeout", type=int, default=14400)

    sub.add_parser("nodes", help="查看 SLURM 分区节点。")
    sub.add_parser("route-test", help="测试 SSH 线路延迟。")

    download = sub.add_parser("download", help="回传小摘要产物。")
    download.add_argument("remote_dir")
    download.add_argument("local_dir")

    args = parser.parse_args(argv)

    if args.command == "route-test":
        for host, port, seconds, status in test_routes(args.namespace, args.credential):
            print(f"{seconds:>8.3f}s\t{host}:{port}\t{status}")
        return 0

    if args.command == "matrix":
        result = submit_matrix(
            Path(args.config),
            ROOT,
            args.namespace,
            args.credential,
            args.dry_run,
        )
        print_rows(result["jobs"])
        out = ROOT / "scenarios/fac_demo/outputs/FeL_single_node_HPC" / "matrix_jobs.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("jobs manifest:", out)
        return 0

    if args.command == "submit" and args.dry_run:
        from scenarios.run.remote.job_submit import submit_scene

        scene = load_scene(args.scene)
        options = ExecOptions(
            namespace=args.namespace,
            credential=args.credential,
            stage=args.stage,
            cores=args.cores,
            mpi=args.mpi,
            walltime=args.walltime,
            dry_run=True,
            run_id=args.run_id,
            extra=tuple(args.extra),
        )
        result = submit_scene(scene, options, args.extra)
        for key, value in result.items():
            print(f"{key}: {value}")
        return 0

    with RemoteSession(args.namespace, args.credential) as session:
        if args.command == "wait-many":
            terminal = {"COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "NODE_FAIL", "OUT_OF_MEMORY"}
            deadline = time.time() + args.timeout
            while time.time() < deadline:
                states = {job: job_state(session, job) for job in args.jobs}
                print(
                    "[%s] %s"
                    % (time.strftime("%H:%M:%S"), " ".join("%s=%s" % item for item in states.items())),
                    flush=True,
                )
                if all(state in terminal for state in states.values()):
                    return 0
                time.sleep(30)
            print("WAIT_TIMEOUT")
            return 1
        if args.command == "status":
            print(job_state(session, args.job))
            return 0
        if args.command == "wait":
            print(wait_for_job(session, args.job, timeout=args.timeout))
            return 0
        if args.command == "nodes":
            rc, out, err = session.exec("sinfo -N -o '%N %P %C'", timeout=120)
            print(out if rc == 0 else err)
            return rc
        if args.command == "download":
            saved = fetch_artifacts(session, args.remote_dir, Path(args.local_dir))
            print("\n".join(str(item) for item in saved))
            return 0
        if args.command == "submit":
            from scenarios.run.remote.job_submit import submit_scene

            scene = load_scene(args.scene)
            options = ExecOptions(
                namespace=args.namespace,
                credential=args.credential,
                stage=args.stage,
                cores=args.cores,
                mpi=args.mpi,
                walltime=args.walltime,
                dry_run=False,
                run_id=args.run_id,
                extra=tuple(args.extra),
            )
            result = submit_scene(scene, options, args.extra)
            for key, value in result.items():
                print(f"{key}: {value}")
            return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
