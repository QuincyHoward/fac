#!/usr/bin/env python3
"""FeL_opacity_full scene entry.

Phases:
  smoke     - local smoke build with fallback data
  crm-pop   - regenerate full Fe08/09/10 CRM populations (PFAC/HPC)
  pi-dense  - dense direct PI via TotalPICross (PFAC/HPC)
  ai-dr     - AI/DR resonance contributions (PFAC/HPC)
  build     - full opacity synthesis
  validate  - no-reference validation
  plot      - figures
  all       - build, validate, plot
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"

PHASE_SCRIPTS = {
    "smoke": HERE / "scripts" / "build_opacity_full.py",
    "crm-pop": HERE / "scripts" / "crm_populations.py",
    "pi-dense": HERE / "scripts" / "pi_dense_full.py",
    "ai-dr": HERE / "scripts" / "resonant_pi.py",
    "build": HERE / "scripts" / "build_opacity_full.py",
    "validate": HERE / "scripts" / "validate_full.py",
    "plot": HERE / "plots" / "plot_opacity_full.py",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="all",
                        choices=["all", "smoke", "crm-pop", "pi-dense", "ai-dr", "build", "validate", "plot"])
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--artifacts-dir", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    parser.add_argument("--allow-fallback", dest="allow_fallback", action="store_true", default=True)
    parser.add_argument("--no-fallback", dest="allow_fallback", action="store_false")
    parser.add_argument("--inside", action="store_true", help="accepted for HPC compatibility")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)

    artifacts = Path(args.artifacts_dir).resolve() if args.artifacts_dir else (HERE / config["artifacts_dir"]).resolve()
    output = Path(args.output_dir).resolve() if args.output_dir else (HERE / config["output_dir"]).resolve()

    phases = ["build", "validate", "plot"] if args.phase == "all" else [args.phase]
    common = [
        "--config", str(Path(args.config).resolve()),
        "--artifacts-dir", str(artifacts),
        "--output-dir", str(output),
        "--cores", str(args.cores),
        "--mpi", str(args.mpi),
    ]
    if args.allow_fallback:
        common.append("--allow-fallback")

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
        started = time.time()
        code = subprocess.run([sys.executable, str(script)] + common, cwd=str(HERE), check=False).returncode
        results[phase] = {"exit_code": code, "wall_seconds": round(time.time() - started, 3)}
        if code != 0:
            break

    summary = {
        "scene": "FeL_opacity_full",
        "artifacts_dir": str(artifacts),
        "output_dir": str(output),
        "phases": results,
        "ok": bool(results) and all(item.get("exit_code") == 0 for item in results.values()),
    }
    path = output / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
