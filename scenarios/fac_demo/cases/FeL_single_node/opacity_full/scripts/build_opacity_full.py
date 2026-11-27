#!/usr/bin/env python3
"""Synthesize full-physics FeL opacity: bound-free + bound-bound + resonances."""

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

from opacity_tables_full import energy_grid, interp_sorted, iter_rr, iter_sp_line_widths, iter_sp_populations_full, iter_tr_transitions_full, load_csv  # noqa: E402

HC_EV_A = 12398.419843320026
CM2_PER_UNIT = 1.0e-20
BB_CONST_EV = 0.02654 / 4.135667696e-15
HBAR_EV_S = 6.582119569e-16
SQRT2LN2 = math.sqrt(2.0 * math.log(2.0))
FE_MASS_AMU = 55.845


def resolve_template(value, artifacts, output, t_index):
    text = value.format(t_index=t_index)
    if text.startswith("artifacts/"):
        return artifacts / text[len("artifacts/"):]
    if text.startswith("outputs/"):
        return output / text[len("outputs/"):]
    return Path(text)


def normalize_populations(rows, config):
    pc = config["population"]
    by_level = defaultdict(float)
    for row in rows:
        by_level[row["global_level"]] += row["population"]
    total = sum(by_level.values())
    if total <= 0:
        return {}, {"levels": 0, "raw_sum": 0.0, "kept_sum": 0.0, "coverage": 0.0}
    ordered = sorted(by_level.items(), key=lambda item: item[1], reverse=True)
    kept = []
    kept_sum = 0.0
    for level, population in ordered:
        kept.append((level, population))
        kept_sum += population
        if kept_sum >= float(pc["coverage"]) * total or len(kept) >= int(pc.get("top_n", 2000)):
            break
    return {level: population / kept_sum for level, population in kept}, {
        "levels": len(kept), "raw_sum": total, "kept_sum": kept_sum, "coverage": kept_sum / total,
    }


def ascii_pi_by_level(path):
    channels = defaultdict(list)
    for block in iter_rr(str(path)):
        pairs = [(e, pi * CM2_PER_UNIT) for e, pi in zip(block["energy_ev"], block["pi_crosssection"]) if e > 0 and pi > 0]
        if pairs:
            pairs.sort(key=lambda item: item[0])
            channels[block["bound_index"]].append(([p[0] for p in pairs], [p[1] for p in pairs]))
    result = {}
    for level, grids in channels.items():
        xs = sorted(set(e for xs, _ in grids for e in xs))
        ys = [sum(interp_sorted(a, b, e) for a, b in grids) for e in xs]
        result[level] = (xs, ys)
    return result


def dense_pi_by_level(path):
    by_level = defaultdict(list)
    for row in load_csv(path):
        by_level[int(row["level"])].append((float(row["energy_ev"]), float(row["pi_crosssection_1e-20cm2"])))
    result = {}
    for level, pairs in by_level.items():
        pairs.sort(key=lambda item: item[0])
        result[level] = ([p[0] for p in pairs], [p[1] for p in pairs])
    return result


def resonance_by_ion(path, energies):
    if not path.exists():
        return [0.0] * len(energies)
    rows = [(float(row["energy_ev"]), float(row["kappa_res_cm2_per_Fe"])) for row in load_csv(path)]
    if not rows:
        return [0.0] * len(energies)
    xs = [row[0] for row in rows]
    ys = [row[1] for row in rows]
    return [interp_sorted(xs, ys, energy) for energy in energies]


def width_to_ev(value):
    if value <= 0:
        return 0.0
    return value if value < 100.0 else value * HBAR_EV_S / (2.0 * math.pi)


def pseudo_voigt(delta, gamma, sigma):
    gamma = max(gamma, 1e-12)
    sigma = max(sigma, 1e-12)
    eta = gamma / (gamma + 2.0 * sigma * SQRT2LN2)
    lorentz = (gamma / (2.0 * math.pi)) / (delta * delta + (gamma / 2.0) ** 2)
    gauss = math.exp(-0.5 * (delta / sigma) ** 2) / (sigma * math.sqrt(2.0 * math.pi))
    return eta * lorentz + (1.0 - eta) * gauss


def add_lines(kappa, energies, transitions, populations, fraction, widths, te_ev, config):
    bb = config["bound_bound"]
    min_width = float(bb.get("min_width_ev", 1e-4))
    max_width = float(bb.get("max_width_ev", 5.0))
    window = float(bb.get("window_sigmas", 8))
    mass_energy = FE_MASS_AMU * 931.49410242e6
    doppler_base = math.sqrt(8.0 * te_ev * math.log(2.0) / mass_energy) if bb.get("doppler", True) else 0.0
    line_count = 0

    for tr in transitions:
        population = populations.get(tr["lower_index"], 0.0)
        if population <= 0 or tr["gf"] <= 0:
            continue
        center = tr["delta_e"]
        if center < energies[0] - 5.0 or center > energies[-1] + 5.0:
            continue
        w = widths.get((tr["upper_index"], tr["lower_index"], round(center, 3))) or widths.get(
            (tr["lower_index"], tr["upper_index"], round(center, 3)), {}
        )
        gamma = 0.0
        sigma_sq = min_width * min_width
        if bb.get("natural_width", True):
            gamma += width_to_ev(tr["rate"])
        if bb.get("use_sp_widths", True):
            gamma += width_to_ev(float(w.get("wstk", 0.0)))
            impact = width_to_ev(float(w.get("wimp", 0.0)))
            sigma_sq += (impact / SQRT2LN2) ** 2
            sdev = float(w.get("sdev", 0.0))
            if sdev > 0:
                sigma_sq += sdev * sdev
        doppler = center * doppler_base
        sigma_sq += (doppler / SQRT2LN2) ** 2
        gamma = min(max(gamma, min_width), max_width)
        sigma = min(math.sqrt(sigma_sq), max_width)
        cutoff = window * max(gamma, sigma)
        amplitude = fraction * population * BB_CONST_EV * tr["gf"]
        for i, energy in enumerate(energies):
            delta = energy - center
            if abs(delta) <= cutoff:
                kappa[i] += amplitude * pseudo_voigt(delta, gamma, sigma)
        line_count += 1
    return line_count


def write_csv(path, energies, wavelengths, bf, bb, res, fractions):
    with open(str(path), "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "energy_ev", "wavelength_a", "kappa_bf_cm2_per_Fe", "kappa_bb_cm2_per_Fe",
            "kappa_res_cm2_per_Fe", "kappa_cm2_per_Fe", "kappa_inv_cm", "transmission",
            "Fe19_fraction", "Fe18_fraction", "Fe17_fraction",
        ])
        for i, energy in enumerate(energies):
            total = bf[i] + bb[i] + res[i]
            n_fe = fractions["n_fe_cm3"]
            transmission = math.exp(-total * n_fe * fractions["path_length_cm"])
            writer.writerow([
                "%.8f" % energy, "%.8f" % wavelengths[i],
                "%.8e" % bf[i], "%.8e" % bb[i], "%.8e" % res[i],
                "%.8e" % total, "%.8e" % (total * n_fe), "%.8e" % transmission,
                "%.8e" % fractions["Fe19_fraction"], "%.8e" % fractions["Fe18_fraction"],
                "%.8e" % fractions["Fe17_fraction"],
            ])


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
    tables = output / "tables"
    tables.mkdir(parents=True, exist_ok=True)

    energies, wavelengths = energy_grid(config)
    temps = {row["t_index"]: row for row in load_csv(artifacts / "plots_inputs" / "temperatures.csv")}
    abund_rows = load_csv(artifacts / "plots_inputs" / "abund.csv")

    def match_abund(logt):
        return min(abund_rows, key=lambda row: abs(float(row["logt"]) - logt))

    normalization = config["normalization"]
    n_fe = float(normalization["n_h_cm3"]) * float(normalization["n_fe_per_h"])
    path_length = float(normalization["path_length_cm"])

    dense_manifest = output / "dense_pi" / "manifest.json"
    pi_source = "ascii_rr_loglog"
    if dense_manifest.exists():
        dm = json.loads(dense_manifest.read_text(encoding="utf-8"))
        pi_source = dm.get("source", pi_source)

    resonance_manifest = output / "resonances" / "manifest.json"
    resonance_source = "zero_fallback"
    if resonance_manifest.exists():
        rm = json.loads(resonance_manifest.read_text(encoding="utf-8"))
        resonance_source = "ai_table_lorentzian_example" if rm.get("ions") else "zero_fallback"

    metadata = {
        "stage": "build",
        "artifacts_dir": str(artifacts),
        "energy_points": len(energies),
        "pi_source": pi_source,
        "resonance_source": resonance_source,
        "bound_bound_enabled": bool(config["bound_bound"].get("enabled", False)),
        "temperatures": {},
        "warnings": [],
    }

    for t_index in config["temperature_indices"]:
        row_t = temps[t_index]
        logt = float(row_t["log10T"])
        abund = match_abund(logt)
        fractions = {ion["fraction_column"]: float(abund[ion["fraction_column"]]) for ion in config["ions"]}
        fractions["n_fe_cm3"] = n_fe
        fractions["path_length_cm"] = path_length

        kappa_bf = [0.0] * len(energies)
        kappa_bb = [0.0] * len(energies)
        kappa_res = [0.0] * len(energies)
        temp_meta = {"te_ev": float(row_t[config["bound_bound"].get("te_column", "T_K")]),
                     "log10t": logt, "fractions": {}, "ions": {}}

        for ion in config["ions"]:
            prefix = ion["prefix"]
            nele = int(ion["nele"])
            column = ion["fraction_column"]
            fraction = fractions[column]
            temp_meta["fractions"][column] = fraction

            sp_path = resolve_template(ion["sp_file"], artifacts, output, t_index)
            rows = list(iter_sp_populations_full(sp_path, float(config["population"]["min_population"]), nele)) if sp_path.exists() else []
            populations, pop_meta = normalize_populations(rows, config)
            fallback = not rows
            if fallback:
                populations = {0: 1.0}
                pop_meta = {"levels": 1, "raw_sum": 1.0, "kept_sum": 1.0, "coverage": 1.0}
                metadata["warnings"].append("%s t%s SP missing; ground_state fallback" % (prefix, t_index))

            rr_ascii = artifacts / "data" / ("%s%s" % (prefix, config["pi"]["table_suffix"]))
            pi_dense_csv = output / "dense_pi" / ("%s_pi_dense.csv" % prefix)
            if pi_dense_csv.exists():
                pi_data = dense_pi_by_level(pi_dense_csv)
            else:
                pi_data = ascii_pi_by_level(rr_ascii)

            missing_pi = 0
            for level, population in populations.items():
                curve = pi_data.get(level)
                if curve is None:
                    missing_pi += 1
                    continue
                xs, ys = curve
                contribution = population * fraction
                for i, energy in enumerate(energies):
                    kappa_bf[i] += contribution * interp_sorted(xs, ys, energy)

            line_count = 0
            widths = {}
            if config["bound_bound"].get("enabled") and sp_path.exists():
                if config["bound_bound"].get("use_sp_widths", True):
                    widths = {(item["upper"], item["lower"], round(item["energy_ev"], 3)): item
                              for item in iter_sp_line_widths(sp_path, float(config["bound_bound"].get("min_gf", 1e-8)))}
                lower_levels = set(populations.keys())
                tr_path = artifacts / "data" / ("%s%s" % (prefix, config["bound_bound"].get("table_suffix", "a.tr")))
                transitions = [tr for tr in iter_tr_transitions_full(tr_path, float(config["bound_bound"].get("min_gf", 1e-8)))
                               if tr["lower_index"] in lower_levels and energies[0] - 5 <= tr["delta_e"] <= energies[-1] + 5]
                line_count = add_lines(kappa_bb, energies, transitions, populations, fraction, widths,
                                       temp_meta["te_ev"], config)

            res_path = output / "resonances" / ("%s_resonance.csv" % prefix)
            ion_res = resonance_by_ion(res_path, energies)
            for i, value in enumerate(ion_res):
                kappa_res[i] += fraction * value

            temp_meta["ions"][prefix] = {
                "population_levels": pop_meta["levels"],
                "population_coverage": pop_meta["coverage"],
                "fallback": fallback,
                "pi_levels": len(pi_data),
                "missing_pi_levels": missing_pi,
                "bound_bound_lines": line_count,
                "sp_width_records": len(widths),
            }

        write_csv(tables / ("opacity_full_t%s.csv" % t_index), energies, wavelengths, kappa_bf, kappa_bb, kappa_res, fractions)
        metadata["temperatures"][t_index] = temp_meta
        print("built full t%s: bb=%d energy points" % (t_index, sum(1 for value in kappa_bb if value > 0)))

    metadata["wall_seconds"] = round(time.time() - started, 3)
    (output / "build_metadata_full.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("build complete: %.3f s" % metadata["wall_seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
