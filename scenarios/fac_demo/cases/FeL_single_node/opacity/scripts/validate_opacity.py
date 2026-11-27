#!/usr/bin/env python3
"""No-reference physical checks for the FeL opacity example."""

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

from opacity_tables import interp_sorted, iter_rr  # noqa: E402

SCENE = HERE.parent
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "ok": bool(ok), "detail": detail})
    return bool(ok)


def read_config(path):
    with open(str(path), "r", encoding="utf-8") as handle:
        return json.load(handle)


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
    args = parser.parse_args(argv)

    config = read_config(args.config)
    artifacts = Path(args.artifacts_dir).resolve()
    output = Path(args.output_dir).resolve()
    tables = output / "tables"
    metadata_path = output / "build_metadata.json"

    check("build_metadata_exists", metadata_path.exists(), str(metadata_path))
    if not metadata_path.exists():
        return write_result(output)

    with open(str(metadata_path), "r", encoding="utf-8") as handle:
        metadata = json.load(handle)

    required_coverage = float(config["validation"].get("rtol_population_sum", 1e-3))
    rtol = float(config["validation"].get("rtol_roundtrip", 1e-6))

    all_files = True
    for t_index in config["temperature_indices"]:
        path = tables / ("opacity_t%s.csv" % t_index)
        all_files = check("csv_t%s_exists" % t_index, path.exists(), str(path)) and all_files
    if not all_files:
        return write_result(output)

    monotonic = True
    nonnegative = True
    positive = True
    fractions_ok = True
    temp_meta = metadata.get("temperatures", {})
    for t_index in config["temperature_indices"]:
        rows = read_csv(tables / ("opacity_t%s.csv" % t_index))
        energies = [float(row["energy_ev"]) for row in rows]
        kappas = [float(row["kappa_cm2_per_Fe"]) for row in rows]
        if len(energies) < 2 or any(energies[i] >= energies[i + 1] for i in range(len(energies) - 1)):
            monotonic = check("energy_monotonic_t%s" % t_index, False, "energy must be strictly increasing") and monotonic
        if any((not math.isfinite(value)) or value < 0 for value in kappas):
            nonnegative = check("kappa_nonnegative_t%s" % t_index, False, "negative or non-finite kappa") and nonnegative
        if not any(value > 0 for value in kappas):
            positive = check("kappa_positive_t%s" % t_index, False, "all kappa values are zero") and positive
        expected = temp_meta.get(t_index, {}).get("fractions", {})
        if rows and expected:
            for column, value in expected.items():
                actual = float(rows[0][column])
                if abs(actual - float(value)) > 1e-6:
                    fractions_ok = check("fraction_%s_t%s" % (column, t_index), False, "CSV/build mismatch") and fractions_ok
    check("energy_monotonic_all", monotonic)
    check("kappa_nonnegative_all", nonnegative)
    check("kappa_positive_all", positive)
    check("ion_fractions_match_metadata", fractions_ok)

    coverage_ok = True
    for t_index, info in temp_meta.items():
        for prefix, ion_info in info.get("ions", {}).items():
            if ion_info.get("fallback"):
                continue
            coverage = float(ion_info.get("population_coverage", 0.0))
            if coverage < 1.0 - required_coverage:
                coverage_ok = check("population_coverage_%s_t%s" % (prefix, t_index), False, "coverage=%.6f" % coverage) and coverage_ok
    check("population_coverage_all", coverage_ok)

    roundtrip_ok = True
    checked = 0
    for ion in config["ions"]:
        rr_path = artifacts / "data" / ("%s%s" % (ion["prefix"], config["pi"]["table_suffix"]))
        for block in iter_rr(str(rr_path)):
            xs = []
            ys = []
            for e, pi in zip(block["energy_ev"], block["pi_crosssection"]):
                if e > 0 and pi > 0:
                    xs.append(e)
                    ys.append(pi * 1.0e-20)
            if not xs:
                continue
            for e, y in zip(xs, ys):
                got = interp_sorted(xs, ys, e)
                if abs(got - y) > rtol * max(abs(y), 1e-30):
                    roundtrip_ok = check("rr_roundtrip_%s_%d" % (ion["prefix"], checked), False, "e=%g" % e) and roundtrip_ok
                checked += 1
    check("rr_roundtrip_all", roundtrip_ok, "checked %d energy points" % checked)

    literature_note = SCENE.parent / "refs" / "mds" / "reading_notes.md"
    comparison_doc = SCENE / "docs" / "literature_comparison.md"
    check("literature_notes_exist", literature_note.exists() and comparison_doc.exists())
    if literature_note.exists() and comparison_doc.exists():
        text = comparison_doc.read_text(encoding="utf-8")
        check("literature_boundary_recorded", "定性对照" in text and "无官方" not in text or "不声称" in text)

    return write_result(output)


def write_result(output):
    ok = bool(CHECKS) and all(item["ok"] for item in CHECKS)
    result = {"ok": ok, "checks": CHECKS}
    with open(str(output / "validation.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
