#!/usr/bin/env python3
"""Generate example-level AI/DR resonance contributions for FeL opacity.

Streaming implementation: AI tables may contain >10 million records, so rows are
never accumulated into a list. Only resonances that fall inside the configured
photon-energy window are accumulated.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from opacity_tables_full import iter_rr  # noqa: E402


def iter_ai_rows(path):
    with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if "=" in line or not line.strip():
                continue
            parts = line.split()
            if len(parts) < 7 or not parts[0].lstrip("-").isdigit():
                continue
            try:
                yield float(parts[4]), float(parts[6])
            except ValueError:
                continue


def thresholds_from_rr(path):
    values = []
    for block in iter_rr(str(path)):
        if block["delta_e"] > 0:
            values.append(block["delta_e"])
    values.sort()
    if not values:
        return 700.0
    return values[min(len(values) - 1, int(0.75 * len(values)))]


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
    res_dir = output / "resonances"
    res_dir.mkdir(parents=True, exist_ok=True)

    rcfg = config["resonance"]
    grid = config["energy_grid"]
    lo = 12398.419843320026 / float(grid["max"])
    hi = 12398.419843320026 / float(grid["min"])
    count = int(round((float(grid["max"]) - float(grid["min"])) / float(grid["step"]))) + 1
    energies = [lo + i * (hi - lo) / (count - 1) for i in range(count)]
    gamma = float(rcfg.get("width_ev", 1.0))
    half = gamma / 2.0
    window = int(rcfg.get("window_sigmas", 8)) * gamma
    min_strength = float(rcfg.get("min_strength", 1e-8))
    max_resonances = int(rcfg.get("max_resonances", 200000))

    manifest = {
        "stage": "ai-dr",
        "source": "ai_table_lorentzian_example",
        "ions": {},
        "warnings": ["Example-level resonance model: AI photoelectron energy + upper-quartile RR threshold; not experimental-grade opacity."],
    }

    for ion in config["ions"]:
        prefix = ion["prefix"]
        ai_path = artifacts / rcfg["ai_table"].format(prefix=prefix)
        rr_path = artifacts / "data" / ("%s%s" % (prefix, config["pi"]["table_suffix"]))
        threshold = thresholds_from_rr(rr_path)
        values = [0.0] * len(energies)
        records = 0
        used = 0
        truncated = False

        if ai_path.exists():
            for e_photoelectron, strength in iter_ai_rows(ai_path):
                records += 1
                if strength < min_strength:
                    continue
                center = threshold + e_photoelectron
                left = bisect.bisect_left(energies, center - window)
                right = bisect.bisect_right(energies, center + window)
                if left >= right:
                    continue
                area = strength * 1.0e-20
                for i in range(left, right):
                    delta = energies[i] - center
                    values[i] += area * half / (math.pi * (delta * delta + half * half))
                used += 1
                if used >= max_resonances:
                    truncated = True
                    break
        else:
            if not args.allow_fallback:
                print("AI table unavailable for %s" % prefix, file=sys.stderr)
                return 2
            manifest["warnings"].append("%s: AI table missing, zero resonance contribution" % prefix)

        out_path = res_dir / ("%s_resonance.csv" % prefix)
        with open(str(out_path), "w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["energy_ev", "kappa_res_cm2_per_Fe"])
            for energy, value in zip(energies, values):
                writer.writerow(["%.6f" % energy, "%.8e" % value])
        manifest["ions"][prefix] = {
            "ai_records_scanned": records,
            "resonances_used": used,
            "truncated": truncated,
            "threshold_ev": threshold,
            "file": str(out_path),
        }
        print("%s: scanned=%d used=%d truncated=%s" % (prefix, records, used, truncated), flush=True)

    manifest["wall_seconds"] = round(time.time() - started, 3)
    (res_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
