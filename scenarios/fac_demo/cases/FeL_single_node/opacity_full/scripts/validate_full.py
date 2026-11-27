#!/usr/bin/env python3
"""No-reference validation for the full-physics opacity scene."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": detail})
    return bool(ok)


def read_csv(path):
    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    output = Path(args.output_dir).resolve()
    tables = output / "tables"
    metadata_path = output / "build_metadata_full.json"

    check("build_metadata_exists", metadata_path.exists())
    if not metadata_path.exists():
        return write_result(output)

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    all_files = True
    for t_index in config["temperature_indices"]:
        path = tables / ("opacity_full_t%s.csv" % t_index)
        all_files = check("csv_t%s_exists" % t_index, path.exists(), str(path)) and all_files
    if not all_files:
        return write_result(output)

    monotonic = True
    positive = True
    bb_nonzero = True
    line_counts = []
    for t_index in config["temperature_indices"]:
        rows = read_csv(tables / ("opacity_full_t%s.csv" % t_index))
        energies = [float(row["energy_ev"]) for row in rows]
        total = [float(row["kappa_cm2_per_Fe"]) for row in rows]
        bb = [float(row["kappa_bb_cm2_per_Fe"]) for row in rows]
        if len(energies) < 2 or any(energies[i] >= energies[i + 1] for i in range(len(energies) - 1)):
            monotonic = check("energy_monotonic_t%s" % t_index, False) and monotonic
        if not any(value > 0 and math.isfinite(value) for value in total):
            positive = check("kappa_positive_t%s" % t_index, False) and positive
        if config["validation"].get("require_bb_nonzero") and not any(value > 0 for value in bb):
            bb_nonzero = check("bb_nonzero_t%s" % t_index, False) and bb_nonzero
        info = metadata.get("temperatures", {}).get(t_index, {}).get("ions", {})
        counts = [int(item.get("bound_bound_lines", 0)) for item in info.values()]
        line_counts.append(sum(counts))

    check("energy_monotonic_all", monotonic)
    check("kappa_positive_all", positive)
    check("bound_bound_nonzero_all", bb_nonzero)
    check("bound_bound_lines_recorded", sum(line_counts) >= int(config["validation"].get("min_line_count", 1)),
          "total_lines=%d" % sum(line_counts))
    check("bound_bound_enabled", bool(metadata.get("bound_bound_enabled")))
    check("pi_source_recorded", bool(metadata.get("pi_source")))
    check("resonance_source_recorded", bool(metadata.get("resonance_source")))

    fallbacks = []
    for t_index, info in metadata.get("temperatures", {}).items():
        for prefix, ion_info in info.get("ions", {}).items():
            if ion_info.get("fallback"):
                fallbacks.append("%s_t%s" % (prefix, t_index))
    check("population_fallbacks_documented", True, "fallbacks=%s" % ",".join(fallbacks) if fallbacks else "none")

    return write_result(output)


def write_result(output):
    ok = bool(CHECKS) and all(item["ok"] for item in CHECKS)
    result = {"ok": ok, "checks": CHECKS}
    (output / "validation_full.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
