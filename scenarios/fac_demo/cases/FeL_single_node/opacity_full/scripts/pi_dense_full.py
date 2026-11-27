#!/usr/bin/env python3
"""Generate dense direct PI grids using PFAC TotalPICross, with ASCII fallback."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from opacity_tables_full import interp_sorted, iter_rr, load_csv  # noqa: E402


def aggregate_ascii_pi(path):
    channels = defaultdict(list)
    for block in iter_rr(str(path)):
        pairs = [(e, pi) for e, pi in zip(block["energy_ev"], block["pi_crosssection"]) if e > 0 and pi > 0]
        if pairs:
            pairs.sort(key=lambda item: item[0])
            channels[block["bound_index"]].append(([p[0] for p in pairs], [p[1] for p in pairs]))
    result = {}
    for level, grids in channels.items():
        energies = sorted(set(e for xs, _ in grids for e in xs))
        values = [sum(interp_sorted(xs, ys, e) for xs, ys in grids) for e in energies]
        result[level] = (energies, values)
    return result


def write_pi_csv(path, levels, energies, values):
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["level", "energy_ev", "pi_crosssection_1e-20cm2"])
        for level in levels:
            xs, ys = level, values[level] if isinstance(values, dict) else None
        if isinstance(values, dict):
            for level in levels:
                xs, ys = values[level]
                for energy, value in zip(xs, ys):
                    writer.writerow([level, "%.6f" % energy, "%.8e" % value])
        else:
            for energy, value in zip(energies, values):
                writer.writerow(["aggregate", "%.6f" % energy, "%.8e" % value])


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
    dense_dir = output / "dense_pi"
    dense_dir.mkdir(parents=True, exist_ok=True)

    pcfg = config["pi"]
    energies = [pcfg["energy_min_ev"] + i * (pcfg["energy_max_ev"] - pcfg["energy_min_ev"]) / (int(pcfg["energy_points"]) - 1)
                for i in range(int(pcfg["energy_points"]))]

    try:
        from pfac import fac
        pfac_available = True
    except ImportError as exc:
        pfac_available = False
        if not args.allow_fallback:
            print("PFAC unavailable: %s" % exc, file=sys.stderr)
            return 2

    manifest = {
        "stage": "pi-dense",
        "pfac_available": pfac_available,
        "source": "pfac_TotalPICross" if pfac_available else "ascii_rr_loglog",
        "energy_points": len(energies),
        "ions": {},
        "warnings": [],
    }

    for ion in config["ions"]:
        prefix = ion["prefix"]
        ascii_path = artifacts / "data" / ("%s%s" % (prefix, pcfg["table_suffix"]))
        data = aggregate_ascii_pi(ascii_path)
        ranked = sorted(data.items(), key=lambda item: max(item[1][1]), reverse=True)[:int(pcfg.get("top_n", 200))]
        levels = [level for level, _ in ranked]
        out_path = dense_dir / ("%s_pi_dense.csv" % prefix)

        if pfac_available:
            en_bin = artifacts / "data" / pcfg["binary_en"].format(prefix=prefix)
            rr_bin = artifacts / "data" / pcfg["binary_rr"].format(prefix=prefix)
            fac.MemENTable(str(en_bin))
            fallback_levels = 0
            with open(str(out_path), "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["level", "energy_ev", "pi_crosssection_1e-20cm2"])
                for level in levels:
                    tmp = dense_dir / ("%s_level_%d.tmp" % (prefix, level))
                    fac.TotalPICross(str(rr_bin), str(tmp), level, energies)
                    rows = load_csv(tmp) if tmp.exists() else []
                    if rows:
                        for row in rows:
                            keys = list(row.keys())
                            writer.writerow([level, row[keys[0]], row[keys[1]]])
                    else:
                        fallback_levels += 1
                        xs, ys = data[level]
                        for energy in energies:
                            writer.writerow([level, "%.6f" % energy, "%.8e" % interp_sorted(xs, ys, energy)])
                    if tmp.exists():
                        tmp.unlink()
            if fallback_levels:
                manifest["warnings"].append("%s: %d levels used ASCII log-log fallback after TotalPICross failure" % (prefix, fallback_levels))
                manifest["source"] = "pfac_TotalPICross_with_ascii_fallback"
        else:
            with open(str(out_path), "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(["level", "energy_ev", "pi_crosssection_1e-20cm2"])
                for level in levels:
                    xs, ys = data[level]
                    for energy in energies:
                        writer.writerow([level, "%.6f" % energy, "%.8e" % interp_sorted(xs, ys, energy)])
            manifest["warnings"].append("%s dense PI generated from ASCII 6-point log-log interpolation" % prefix)

        manifest["ions"][prefix] = {"levels": len(levels), "file": str(out_path)}

    manifest["wall_seconds"] = round(time.time() - started, 3)
    (dense_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
