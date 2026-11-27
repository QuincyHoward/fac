#!/usr/bin/env python3
"""Regenerate full Fe08/Fe09/Fe10 CRM populations using PFAC spm.spectrum."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from opacity_tables_full import load_csv  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--artifacts-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    parser.add_argument("--allow-fallback", action="store_true", default=True)
    parser.add_argument("--no-fallback", dest="allow_fallback", action="store_false")
    args = parser.parse_args(argv)

    started = time.time()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    artifacts = Path(args.artifacts_dir).resolve()
    output = Path(args.output_dir).resolve()
    crm_dir = output / "crm_pop"
    crm_dir.mkdir(parents=True, exist_ok=True)

    status = {
        "stage": "crm-pop",
        "source": "",
        "pfac_available": False,
        "ions": {},
        "warnings": [],
    }
    try:
        from pfac import fac, spm
        status["pfac_available"] = True
    except ImportError as exc:
        if not args.allow_fallback:
            print("PFAC unavailable: %s" % exc, file=sys.stderr)
            return 2
        status["source"] = "existing_artifacts_fallback"
        status["warnings"].append("PFAC unavailable: %s" % exc)
        status["warnings"].append("Fe10 full populations unavailable; ground_state fallback remains active.")
        for ion in config["ions"]:
            status["ions"][ion["prefix"]] = {
                "output_dir": str(crm_dir / ion["prefix"]),
                "generated": False,
            }
        status["wall_seconds"] = round(time.time() - started, 3)
        (crm_dir / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0

    temps = {row["t_index"]: row for row in load_csv(artifacts / "plots_inputs" / "temperatures.csv")}
    indices = [indices for indices in config["temperature_indices"]]
    temperatures = [float(temps[index]["T_K"]) for index in indices]
    densities = [1.0] * len(temperatures)
    mpi = 1 if args.mpi in ("", "auto") else int(args.mpi)
    if mpi > 1:
        fac.InitializeMPI(mpi)

    try:
        for ion in config["ions"]:
            nele = int(ion["nele"])
            prefix = ion["prefix"]
            out_dir = crm_dir / prefix
            out_dir.mkdir(parents=True, exist_ok=True)
            _, _, abund = spm.get_tgrid(26, nele)
            spm.spectrum([nele], temperatures, densities, abund, "Fe",
                         dir0=str(artifacts / "data") + "/",
                         dir1=str(out_dir) + "/",
                         nion=3)
            status["ions"][prefix] = {"output_dir": str(out_dir), "generated": True, "nele": nele}
            print("generated CRM populations for %s" % prefix)
    finally:
        if mpi > 1:
            fac.FinalizeMPI()

    status["source"] = "pfac_spm_spectrum"
    status["wall_seconds"] = round(time.time() - started, 3)
    (crm_dir / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
