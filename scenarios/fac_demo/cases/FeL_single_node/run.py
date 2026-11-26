#!/usr/bin/env python3
"""FeL single-node demo scene (Python 3.6 compatible).

--cores records the SLURM CPU allocation; --mpi controls fac.InitializeMPI.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAC_ROOT = HERE.parents[3]
DEMO_FEL = FAC_ROOT / "demo" / "FeL"


def patch_fel_script(src, dst, mpi):
    text = src.read_text(encoding="utf-8")
    if "fac.InitializeMPI" not in text:
        marker = "from pfac import fac\n"
        if marker in text:
            text = text.replace(marker, marker + "fac.InitializeMPI(%d)\n" % mpi, 1)
        else:
            text = "from pfac import fac\n" + "fac.InitializeMPI(%d)\n" % mpi + text
    dst.write_text(text, encoding="utf-8")


def prepare_work_dir(work, mpi):
    work.mkdir(parents=True, exist_ok=True)
    for name in ("fe.py", "spec.py"):
        patch_fel_script(DEMO_FEL / name, work / name, mpi)


def count(pattern, base):
    return len(list(base.glob(pattern)))


def verify(work, cores, mpi, return_codes, timings):
    data = work / "data"
    fe08 = work / "Fe08"
    checks = {
        "fe_exit": return_codes.get("fe.py", -1),
        "spec_exit": return_codes.get("spec.py", -1),
        "data_files": count("*", data),
        "data_en": count("*.en", data),
        "data_tr": count("*.tr", data),
        "data_ce": count("*.ce", data),
        "data_ci": count("*.ci", data),
        "data_ai": count("*.ai", data),
        "data_rr": count("*.rr", data),
        "fe08_files": count("*", fe08),
        "fe08_rt": count("*.rt", fe08),
        "fe08_sp": count("*.sp", fe08),
        "slurm_cores": cores,
        "fac_mpi_threads": mpi,
    }
    checks.update(timings)
    checks["ok"] = (
        checks["fe_exit"] == 0
        and checks["spec_exit"] == 0
        and checks["data_files"] >= 36
        and checks["fe08_files"] >= 210
    )
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    parser.add_argument("--work-dir", default="")
    parser.add_argument("--inside", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    cores = os.cpu_count() or 1 if args.cores in ("", "auto") else int(args.cores)
    mpi = cores if args.mpi in ("", "auto") else int(args.mpi)
    work = Path(args.work_dir).resolve() if args.work_dir else HERE / "work_FeL_single_node"
    work.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("work_dir=%s" % work)
        print("cores=%d mpi=%d" % (cores, mpi))
        print("commands: python fe.py ; python spec.py")
        return 0

    prepare_work_dir(work, mpi)
    codes = {}
    timings = {}
    total_start = time.time()
    for script in ("fe.py", "spec.py"):
        print("+ python %s" % script)
        sys.stdout.flush()
        start = time.time()
        codes[script] = subprocess.run([sys.executable, script], cwd=str(work), check=False).returncode
        timings[script.replace(".py", "") + "_wall_seconds"] = round(time.time() - start, 3)
        if codes[script] != 0:
            break
    timings["total_wall_seconds"] = round(time.time() - total_start, 3)

    summary = verify(work, cores, mpi, codes, timings)
    (work / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
