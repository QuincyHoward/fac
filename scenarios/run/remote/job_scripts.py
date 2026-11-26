"""渲染 FAC 作业脚本：stage -> build -> run -> archive。"""

from __future__ import annotations

from typing import Sequence

from ..env.resource_config import ResourceSpec
from ..execution import ExecOptions, SceneSpec
from .job_layout import JobLayout


def sbatch_directives(spec: ResourceSpec, job_name: str) -> list[str]:
    return [
        "#!/bin/bash",
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --account={spec.account}",
        f"#SBATCH --partition={spec.partition}",
        f"#SBATCH --nodes={spec.nodes}",
        f"#SBATCH --ntasks-per-node={spec.ntasks}",
        f"#SBATCH --cpus-per-task={spec.cpus_per_task}",
        f"#SBATCH --time={spec.walltime}",
        "#SBATCH --output=%x_%j.out",
        "#SBATCH --error=%x_%j.err",
    ]


def render_job_body(
    scene: SceneSpec,
    options: ExecOptions,
    spec: ResourceSpec,
    layout: JobLayout,
    args: Sequence[str],
) -> str:
    extra = " ".join(args)
    scene_entry = f"{layout.fac_root}/scenarios/fac_demo/cases/{scene.name}/{scene.entry}"
    lines = [
        "set -euo pipefail",
        f'export FAC_SLURM_CORES="{spec.ntasks}"',
        f'export FAC_MPI_THREADS="{spec.mpi_threads}"',
        'export FAC_PYTHON="${FAC_PYTHON:-/public1/soft/python/3.8.6/bin/python3.8}"',
        'export OMP_NUM_THREADS="${FAC_MPI_THREADS}"',
        f'export FAC_RUN_DIR="{layout.work_root}/run"',
        f'export FAC_BUILD_DIR="{layout.work_root}/fac_build"',
        f'export FAC_ARCHIVE_DIR="{layout.archive_root}"',
        'mkdir -p "$FAC_RUN_DIR" "$FAC_BUILD_DIR" "$FAC_ARCHIVE_DIR"',
        f'cp -a "{layout.fac_root}"/. "$FAC_BUILD_DIR"/',
        'cd "$FAC_BUILD_DIR"',
        "chmod +x configure config.guess config.sub install.sh mkinsdir.sh",
        "for f in configure config.guess config.sub install.sh mkinsdir.sh; do sed -i 's/\\r$//' \"$f\"; done",
        './configure --prefix="$FAC_BUILD_DIR/install" PYTHON="$FAC_PYTHON" --with-mpi=omp > configure.log 2>&1 || '
        './configure --prefix="$FAC_BUILD_DIR/install" PYTHON="$FAC_PYTHON" --with-cfortran=f2cFortran '
        '--with-mpi=omp >> configure.log 2>&1',
        "sed -i 's/^#undef[[:space:]]*f2cFortran.*/#define f2cFortran 1/' sysdef.h",
        "sed -i 's/^#undef[[:space:]]*USE_MPI.*/#define USE_MPI 2/' sysdef.h",
        f'make -j{spec.ntasks} > build.log 2>&1',
        "make pfac > pfac_build.log 2>&1",
        'PYFAC_LIB=$(find "$FAC_BUILD_DIR/build" -maxdepth 1 -type d -name "lib.linux-*" 2>/dev/null | head -1)',
        'export PYTHONPATH="$PYFAC_LIB:$FAC_BUILD_DIR/python:${PYTHONPATH:-}"',
        '"$FAC_PYTHON" -c "from pfac import fac, crm, pol, util"',
        f'"$FAC_PYTHON" "{scene_entry}" --inside --cores "{spec.ntasks}" '
        f'--mpi "{spec.mpi_threads}" --work-dir "$FAC_RUN_DIR" {extra} '
        '> "$FAC_ARCHIVE_DIR/run.log" 2>&1',
        'RC=$?',
        'echo "$RC" > "$FAC_ARCHIVE_DIR/fac.exit"',
        'cp -f "$FAC_RUN_DIR/summary.json" "$FAC_ARCHIVE_DIR/" 2>/dev/null || true',
        'cp -f "$FAC_RUN_DIR"/data/*.en "$FAC_ARCHIVE_DIR/" 2>/dev/null || true',
        'cp -f "$FAC_RUN_DIR"/data/*.tr "$FAC_ARCHIVE_DIR/" 2>/dev/null || true',
        'cp -f configure.log build.log pfac_build.log "$FAC_ARCHIVE_DIR/" 2>/dev/null || true',
        'exit "$RC"',
    ]
    return "\n".join(lines) + "\n"


def render_sbatch(
    scene: SceneSpec,
    options: ExecOptions,
    spec: ResourceSpec,
    layout: JobLayout,
    args: Sequence[str],
    job_name: str = "",
) -> str:
    name = (job_name or f"fac_{scene.name}_{spec.ntasks}c_{spec.mpi_threads}m")[:64]
    head = "\n".join(sbatch_directives(spec, name))
    return head + "\n" + render_job_body(scene, options, spec, layout, args)
