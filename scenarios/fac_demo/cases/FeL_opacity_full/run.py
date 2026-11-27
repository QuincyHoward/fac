#!/usr/bin/env python3
"""HPC wrapper that forwards phases to the nested opacity_full scene."""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMPL = HERE.parent / "FeL_single_node" / "opacity_full" / "run.py"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="")
    args, rest = parser.parse_known_args(argv if argv is not None else sys.argv[1:])

    work = Path(args.work_dir).resolve() if args.work_dir else HERE
    work.mkdir(parents=True, exist_ok=True)

    if "--output-dir" not in rest:
        archive = os.environ.get("FAC_ARCHIVE_DIR", str(work))
        rest += ["--output-dir", str(Path(archive) / "opacity_full_outputs")]

    cmd = [sys.executable, str(IMPL)] + rest
    print("+ wrapper: %s" % " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, cwd=str(HERE), check=False).returncode

    archive = Path(os.environ.get("FAC_ARCHIVE_DIR", str(work)))
    nested_summary = archive / "opacity_full_outputs" / "summary.json"
    if nested_summary.exists():
        shutil.copyfile(str(nested_summary), str(work / "summary.json"))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
