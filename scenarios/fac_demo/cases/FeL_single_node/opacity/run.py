#!/usr/bin/env python3
"""FeL_opacity scene entry.

Discrete phases:
  build     - synthesize opacity tables from existing FeL artifacts
  dense-pi  - optional PFAC TotalPICross dense-grid path
  validate  - no-reference physical checks
  plot      - figures and summary assets
  all       - build, validate, plot (dense-pi added when --dense-pi is given)
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCENE = HERE.parent
DEFAULT_CONFIG = HERE / "config.json"

PHASE_SCRIPTS = {
    "build": HERE / "scripts" / "build_opacity.py",
    "dense-pi": HERE / "scripts" / "dense_pi.py",
    "validate": HERE / "scripts" / "validate_opacity.py",
    "plot": HERE / "plots" / "plot_opacity.py",
}


def load_config(path):
    with open(str(path), "r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_dir(value, default):
    if value:
        return Path(value).resolve()
    return (HERE / default).resolve()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="all", choices=["all", "build", "dense-pi", "validate", "plot"])
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--artifacts-dir", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    parser.add_argument("--dense-pi", action="store_true", help="include dense-pi phase when --phase all")
    parser.add_argument("--inside", action="store_true", help="accepted for compatibility with HPC run.py convention")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    config = load_config(args.config)
    artifacts = resolve_dir(args.artifacts_dir, config.get("artifacts_dir", "../artifacts/FeL_single_node_c24m16"))
    output = resolve_dir(args.output_dir, config.get("output_dir", "outputs"))

    if args.phase == "all":
        phases = ["build"]
        if args.dense_pi:
            phases.append("dense-pi")
        phases.extend(["validate", "plot"])
    else:
        phases = [args.phase]

    common = [
        "--config", str(Path(args.config).resolve()),
        "--artifacts-dir", str(artifacts),
        "--output-dir", str(output),
        "--cores", str(args.cores),
        "--mpi", str(args.mpi),
    ]

    if args.dry_run:
        print("artifacts_dir=%s" % artifacts)
        print("output_dir=%s" % output)
        for phase in phases:
            print("+ %s %s" % (sys.executable, " ".join([str(PHASE_SCRIPTS[phase])] + common)))
        return 0

    output.mkdir(parents=True, exist_ok=True)
    results = {}
    for phase in phases:
        script = PHASE_SCRIPTS[phase]
        if not script.exists():
            results[phase] = {"exit_code": 127, "wall_seconds": 0.0, "error": "missing script: %s" % script}
            break
        print("+ phase %s: %s" % (phase, script.name))
        sys.stdout.flush()
        start = time.time()
        code = subprocess.run([sys.executable, str(script)] + common, cwd=str(HERE), check=False).returncode
        results[phase] = {"exit_code": code, "wall_seconds": round(time.time() - start, 3)}
        if code != 0:
            break

    summary = {
        "scene": "FeL_opacity",
        "artifacts_dir": str(artifacts),
        "output_dir": str(output),
        "phases": results,
        "ok": bool(results) and all(item.get("exit_code") == 0 for item in results.values()),
    }
    summary_path = output / "summary.json"
    with open(str(summary_path), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
