#!/usr/bin/env python3
"""Synthesize FeL opacity spectra from existing ASCII tables (no PFAC needed)."""

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

from opacity_tables import en_level_map, interp_sorted, iter_rr, iter_sp_populations, iter_tr_transitions  # noqa: E402

HC_EV_A = 12398.419843320026
CM2_PER_UNIT = 1.0e-20
BB_INTEGRAL_CONST = 0.02654 / 4.135667696e-15  # pi*e^2/(m_e*c) / h, cm^2 eV


def read_csv_rows(path):
    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def energy_grid(config):
    grid = config["energy_grid"]
    if grid.get("mode", "wavelength") != "wavelength":
        raise ValueError("only wavelength energy_grid mode is implemented")
    lo, hi, step = float(grid["min"]), float(grid["max"]), float(grid["step"])
    count = int(round((hi - lo) / step)) + 1
    wavelengths = [lo + i * step for i in range(count)]
    energies = [HC_EV_A / wl for wl in wavelengths]
    pairs = sorted(zip(energies, wavelengths))
    return [p[0] for p in pairs], [p[1] for p in pairs]


def match_fraction(abund_rows, logt):
    best = None
    best_delta = None
    for row in abund_rows:
        delta = abs(float(row["logt"]) - logt)
        if best_delta is None or delta < best_delta:
            best, best_delta = row, delta
    return best


def load_populations(path, level_map, config, expected_nele=None):
    pc = config["population"]
    min_pop = float(pc.get("min_population", 1e-6))
    coverage = float(pc.get("coverage", 0.999))
    rows = list(iter_sp_populations(str(path), min_pop))
    if expected_nele is not None:
        rows = [row for row in rows if row["nele"] == expected_nele]
    if not rows:
        return {}, {"levels": 0, "raw_sum": 0.0, "kept_sum": 0.0, "coverage": 0.0,
                    "fallback": "ground_state", "unmapped": 0}

    by_level = defaultdict(float)
    unmapped = 0
    for row in rows:
        # crm.c SpecTable writes r.upper = global ion level index in column 1.
        global_index = row["block"]
        by_level[global_index] += row["population"]

    raw_sum = sum(by_level.values())
    if raw_sum <= 0:
        return {}, {"levels": 0, "raw_sum": 0.0, "kept_sum": 0.0, "coverage": 0.0,
                    "fallback": "ground_state", "unmapped": unmapped}

    ordered = sorted(by_level.items(), key=lambda item: item[1], reverse=True)
    kept = []
    kept_sum = 0.0
    for index, population in ordered:
        kept.append((index, population))
        kept_sum += population
        if kept_sum >= coverage * raw_sum:
            break
    normalized = {index: population / kept_sum for index, population in kept}
    return normalized, {
        "levels": len(kept),
        "raw_sum": raw_sum,
        "kept_sum": kept_sum,
        "coverage": kept_sum / raw_sum,
        "fallback": "",
        "unmapped": unmapped,
    }


def load_pi_channels(path, min_cross_section):
    channels = defaultdict(list)
    for block in iter_rr(str(path)):
        pairs = [(e, value * CM2_PER_UNIT) for e, value in zip(block["energy_ev"], block["pi_crosssection"])
                 if value > 0 and e > 0]
        if not pairs or max(item[1] for item in pairs) < min_cross_section:
            continue
        pairs.sort(key=lambda item: item[0])
        channels[block["bound_index"]].append(([item[0] for item in pairs], [item[1] for item in pairs]))
    return channels


def precompute_level_sigma(channels, energies):
    """Precompute sigma(E) per bound level; PI grids are reused across temperatures."""
    result = {}
    for level_index, grids in channels.items():
        values = [0.0] * len(energies)
        for xs, ys in grids:
            for i, photon_energy in enumerate(energies):
                values[i] += interp_sorted(xs, ys, photon_energy)
        result[level_index] = values
    return result


def add_bound_bound(kappa, energy_ev, fraction, populations, transitions, sigma_ev, window_sigmas):
    if sigma_ev <= 0:
        return
    norm = 1.0 / (sigma_ev * math.sqrt(2.0 * math.pi))
    cutoff = window_sigmas * sigma_ev
    for transition in transitions:
        population = populations.get(transition["lower_index"], 0.0)
        if population <= 0:
            continue
        center = transition["delta_e"]
        amplitude = fraction * population * BB_INTEGRAL_CONST * transition["gf"] * norm
        for i, photon_energy in enumerate(energy_ev):
            delta = photon_energy - center
            if abs(delta) > cutoff:
                continue
            kappa[i] += amplitude * math.exp(-0.5 * (delta / sigma_ev) ** 2)


def write_csv(path, energies, wavelengths, kappa_bf, kappa_bb, fractions):
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "energy_ev", "wavelength_a", "kappa_bf_cm2_per_Fe", "kappa_bb_cm2_per_Fe",
            "kappa_cm2_per_Fe", "kappa_inv_cm", "transmission",
            "Fe19_fraction", "Fe18_fraction", "Fe17_fraction",
        ])
        for i, energy in enumerate(energies):
            total = kappa_bf[i] + kappa_bb[i]
            writer.writerow([
                "%.8f" % energy,
                "%.8f" % wavelengths[i],
                "%.8e" % kappa_bf[i],
                "%.8e" % kappa_bb[i],
                "%.8e" % total,
                "%.8e" % (total * fractions["n_fe_cm3"]),
                "%.8e" % math.exp(-total * fractions["n_fe_cm3"] * fractions["path_length_cm"]),
                "%.8e" % fractions["Fe19_fraction"],
                "%.8e" % fractions["Fe18_fraction"],
                "%.8e" % fractions["Fe17_fraction"],
            ])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--artifacts-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cores", default="auto")
    parser.add_argument("--mpi", default="auto")
    args = parser.parse_args(argv)

    start = time.time()
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    artifacts = Path(args.artifacts_dir).resolve()
    output = Path(args.output_dir).resolve()
    tables = output / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    temps = {row["t_index"]: row for row in read_csv_rows(artifacts / "plots_inputs" / "temperatures.csv")}
    abund_rows = read_csv_rows(artifacts / "plots_inputs" / "abund.csv")

    energies, wavelengths = energy_grid(config)
    min_cross_section = float(config["pi"].get("min_cross_section", 1e-12))
    bb_config = config.get("bound_bound", {})
    bb_enabled = bool(bb_config.get("enabled", False))
    normalization = config["normalization"]
    n_fe_cm3 = float(normalization["n_h_cm3"]) * float(normalization["n_fe_per_h"])
    path_length = float(normalization["path_length_cm"])

    ion_data = {}
    for ion in config["ions"]:
        prefix = ion["prefix"]
        data_dir = artifacts / "data"
        pi_channels = load_pi_channels(data_dir / ("%s%s" % (prefix, config["pi"]["table_suffix"])), min_cross_section)
        ion_data[ion["nele"]] = {
            "level_map": en_level_map(str(data_dir / ("%sa.en" % prefix))),
            "pi": pi_channels,
            "sigma": precompute_level_sigma(pi_channels, energies),
            "tr_path": data_dir / ("%s%s" % (prefix, bb_config.get("table_suffix", "a.tr"))),
        }

    metadata = {
        "artifacts_dir": str(artifacts),
        "energy_points": len(energies),
        "energy_min_ev": energies[0],
        "energy_max_ev": energies[-1],
        "cores": args.cores,
        "mpi": args.mpi,
        "temperatures": {},
        "warnings": [],
    }

    for t_index in config["temperature_indices"]:
        if t_index not in temps:
            raise ValueError("missing temperature index %s" % t_index)
        logt = float(temps[t_index]["log10T"])
        abund = match_fraction(abund_rows, logt)
        fractions = {ion["fraction_column"]: float(abund[ion["fraction_column"]]) for ion in config["ions"]}
        fractions["n_fe_cm3"] = n_fe_cm3
        fractions["path_length_cm"] = path_length

        kappa_bf = [0.0] * len(energies)
        kappa_bb = [0.0] * len(energies)
        temp_meta = {
            "te_ev": float(temps[t_index]["T_K"]),
            "log10t": logt,
            "matched_logt": float(abund["logt"]),
            "fractions": {},
            "ions": {},
        }

        for ion in config["ions"]:
            prefix = ion["prefix"]
            column = ion["fraction_column"]
            fraction = fractions[column]
            temp_meta["fractions"][column] = fraction
            data = ion_data[ion["nele"]]
            sp_path = artifacts / "Fe08" / config["population"]["sp_pattern"].format(prefix=prefix, t_index=t_index)
            if sp_path.exists():
                populations, pop_meta = load_populations(sp_path, data["level_map"], config, ion["nele"])
            else:
                populations = {0: 1.0}
                pop_meta = {"levels": 1, "raw_sum": 1.0, "kept_sum": 1.0, "coverage": 1.0,
                            "fallback": "ground_state", "unmapped": 0}
                metadata["warnings"].append("%s %s: %s not found, ground-state fallback" % (prefix, t_index, sp_path.name))

            missing = 0
            for level_index, population in populations.items():
                sigma_values = data["sigma"].get(level_index)
                if sigma_values is None:
                    missing += 1
                    continue
                contribution = population * fraction
                for i in range(len(energies)):
                    kappa_bf[i] += contribution * sigma_values[i]

            if bb_enabled:
                sigma_ev = float(bb_config.get("sigma_ev", 0.01))
                window_sigmas = int(bb_config.get("window_sigmas", 5))
                cutoff = window_sigmas * sigma_ev
                transitions = [
                    tr for tr in iter_tr_transitions(str(data["tr_path"]), float(bb_config.get("min_gf", 1e-6)))
                    if energies[0] - cutoff <= tr["delta_e"] <= energies[-1] + cutoff
                ]
                add_bound_bound(kappa_bb, energies, fraction, populations, transitions, sigma_ev, window_sigmas)

            temp_meta["ions"][prefix] = {
                "pi_levels": len(data["pi"]),
                "population_levels": pop_meta["levels"],
                "population_coverage": pop_meta["coverage"],
                "fallback": pop_meta["fallback"],
                "unmapped_population_rows": pop_meta.get("unmapped", 0),
                "missing_pi_levels": missing,
            }

        write_csv(tables / ("opacity_t%s.csv" % t_index), energies, wavelengths, kappa_bf, kappa_bb, fractions)
        metadata["temperatures"][t_index] = temp_meta
        print("built t%s: %d energy points" % (t_index, len(energies)))

    metadata["wall_seconds"] = round(time.time() - start, 3)
    with open(str(output / "build_metadata.json"), "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("build complete: %.3f s" % metadata["wall_seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
