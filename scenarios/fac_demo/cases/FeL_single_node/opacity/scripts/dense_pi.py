#!/usr/bin/env python3
"""Optional dense-grid PI generation using PFAC TotalPICross.

Requires a PFAC build with DB_RR binary tables. Without PFAC the script records
an unavailable status and exits non-zero so callers can detect the missing path.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from build_opacity import energy_grid, load_populations, read_csv_rows  # noqa: E402
from opacity_tables import en_level_map  # noqa: E402


def write_status(output, status, reason):
    dense = output / "dense_pi"
    dense.mkdir(parents=True, exist_ok=True)
    with open(str(dense / "status.json"), "w", encoding="utf-8") as handle:
        json.dump({"status": status, "reason": reason}, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--artifacts-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    args = parser.parse_args(argv)

    start = time.time()
    output = Path(args.output_dir).resolve()
    artifacts = Path(args.artifacts_dir).resolve()
    dense = output / "dense_pi"
    dense.mkdir(parents=True, exist_ok=True)

    try:
        from pfac import fac
    except ImportError as exc:
        write_status(output, "unavailable", "PFAC import failed: %s" % exc)
        print("PFAC unavailable; dense-pi phase skipped")
        return 1

    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)

    energies, _ = energy_grid(config)
    temps = {row["t_index"]: row for row in read_csv_rows(artifacts / "plots_inputs" / "temperatures.csv")}
    min_population = float(config["population"].get("min_population", 1e-6))
    top_n = int(config["population"].get("top_n", 50))

    manifest = {"artifacts_dir": str(artifacts), "calls": [], "failures": []}
    for t_index in config["temperature_indices"]:
        for ion in config["ions"]:
            prefix = ion["prefix"]
            en_path = artifacts / "data" / ("%sb.en" % prefix)
            rr_path = artifacts / "data" / ("%sb.rr" % prefix)
            sp_path = artifacts / "Fe08" / config["population"]["sp_pattern"].format(prefix=prefix, t_index=t_index)
            if not (en_path.exists() and rr_path.exists() and sp_path.exists()):
                manifest["failures"].append("%s %s: missing binary or SP table" % (prefix, t_index))
                continue
            fac.MemENTable(str(en_path))
            level_map = en_level_map(str(artifacts / "data" / ("%sa.en" % prefix)))
            populations, _ = load_populations(sp_path, level_map, config, ion["nele"])
            levels = sorted(populations.items(), key=lambda item: item[1], reverse=True)[:top_n]
            for level_index, population in levels:
                if population < min_population:
                    continue
                out_path = dense / ("%s_t%s_level_%d.csv" % (prefix, t_index, level_index))
                fac.TotalPICross(str(rr_path), str(out_path), level_index, energies)
                manifest["calls"].append({
                    "prefix": prefix, "t_index": t_index, "level": level_index,
                    "population": population, "file": out_path.name,
                })
            print("dense PI: %s t%s levels=%d" % (prefix, t_index, len(levels)))

    manifest["wall_seconds"] = round(time.time() - start, 3)
    with open(str(dense / "manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    write_status(output, "completed" if not manifest["failures"] else "partial", "see manifest.json")
    print("dense-pi complete: %d calls" % len(manifest["calls"]))
    return 0 if not manifest["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
