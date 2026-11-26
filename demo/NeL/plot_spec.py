#!/usr/bin/env python3
"""Plot Ne VIII line spectrum from a FAC SP table (Ne03a.sp).

This script is standalone: it parses the ASCII SP table directly and only needs
numpy + matplotlib. It does NOT import pfac/rfac, so it runs even when the FAC
Python extension has not been built.

The horizontal axis of every panel is photon energy in eV (the native unit of
the SP table); no wavelength conversion is performed.

Default input : <script_dir>/ref/Ne03a.sp
Default output: <script_dir>/NeL_stick.png and NeL_gauss.png

Usage examples:
    python plot_spec.py
    python plot_spec.py --sigma 0.02 --gauss-range 15.9 16.3
    python plot_spec.py /path/to/Ne03a.sp --outdir /path/to/figures
    python plot_spec.py --euv-gauss          # Gaussian panel over 60-210 eV instead
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def parse_sp_table(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (energy_eV, strength_photons_per_s) of all line-emission blocks."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    energies: list[float] = []
    strengths: list[float] = []
    nblocks = 0
    nline_blocks = 0
    is_population: bool | None = None

    for row in lines:
        stripped = row.strip()
        if stripped.startswith("TYPE"):
            # Block header: NELE / NTRANS / TYPE / IBLK / ICOMP / FBLK / FCOMP
            block_type = stripped.split("=", 1)[1].strip()
            nblocks += 1
            is_population = block_type == "0000000"
            if not is_population:
                nline_blocks += 1
            continue
        if is_population is None:
            continue
        parts = stripped.split()
        # Data rows start with an integer index and have >= 8 columns.
        if len(parts) < 8 or not parts[0].lstrip("-").isdigit():
            continue
        try:
            energy = float(parts[2])
            strength = float(parts[3])
        except ValueError:
            continue
        if not is_population and energy > 0.0:
            energies.append(energy)
            strengths.append(strength)

    if not energies:
        raise ValueError(f"No line-emission records (TYPE != 0000000) found in {path}")
    print(f"Parsed {path}: {nblocks} blocks, {nline_blocks} line blocks, "
          f"{len(energies)} lines")
    return np.asarray(energies), np.asarray(strengths)


def annotate_top_lines(ax, energy: np.ndarray, strength: np.ndarray, top_n: int = 2) -> None:
    """Label the strongest lines (photon energy in eV)."""
    if len(energy) == 0:
        return
    idx = np.argsort(strength)[::-1][:top_n]
    ymax = float(np.max(strength[idx]))
    for k in idx:
        ax.annotate(f"{energy[k]:.4f} eV",
                    xy=(energy[k], strength[k]),
                    xytext=(energy[k], ymax * 3),
                    ha="center", va="bottom", fontsize=8,
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="0.3"))


def plot_stick(energy: np.ndarray, strength: np.ndarray, outfile: Path,
               main_range: tuple[float, float] = (10.0, 210.0),
               zoom_range: tuple[float, float] = (15.9, 16.3)) -> None:
    """Two-panel stick spectrum vs photon energy: full range + doublet zoom."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharey=False)

    m = (energy >= main_range[0]) & (energy <= main_range[1])
    if not np.any(m):
        raise ValueError(f"No lines in main range {main_range} eV")
    ax1.vlines(energy[m], 1e-13, strength[m], colors="C0", linewidth=1.2)
    ax1.set_yscale("log")
    ax1.set_xlim(*main_range)
    ax1.set_ylim(bottom=1e-13)
    ax1.set_ylabel(r"Line luminosity (photons s$^{-1}$)")
    ax1.set_title("Ne VIII CRM stick spectrum - Te=125 eV, ne=1e10 cm^-3 "
                  "(bound-bound emission only)")
    ax1.grid(alpha=0.3, which="both")
    # The two strongest lines nearly overlap on the overview; label the top one.
    annotate_top_lines(ax1, energy[m], strength[m], top_n=1)

    z = (energy >= zoom_range[0]) & (energy <= zoom_range[1])
    if np.any(z):
        ax2.vlines(energy[z], 1e-13, strength[z], colors="C2", linewidth=2.0)
        ax2.set_yscale("log")
        ax2.set_xlim(*zoom_range)
        ax2.set_ylim(bottom=1e-13)
        annotate_top_lines(ax2, energy[z], strength[z])
    else:
        ax2.text(0.5, 0.5, f"No lines in {zoom_range} eV",
                 ha="center", va="center", transform=ax2.transAxes)
    ax2.set_xlabel(r"Photon energy $E$ (eV)")
    ax2.set_ylabel(r"photons s$^{-1}$")
    ax2.set_title(f"Zoom: {zoom_range[0]}-{zoom_range[1]} eV (2p -> 2s doublet)")
    ax2.grid(alpha=0.3, which="both")

    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"Wrote {outfile}")


def plot_gauss(energy: np.ndarray, strength: np.ndarray, outfile: Path,
               erange: tuple[float, float] = (15.9, 16.3),
               sigma: float = 0.01, step: float = 0.001) -> None:
    """Gaussian-instrument-broadened spectrum vs photon energy (eV)."""
    m = (energy >= erange[0]) & (energy <= erange[1])
    if not np.any(m):
        raise ValueError(f"No lines in requested Gaussian range {erange} eV; "
                         "try --gauss-range 60 210 or --euv-gauss")
    ee, ss = energy[m], strength[m]
    grid = np.arange(erange[0], erange[1] + step, step)
    conv = np.zeros_like(grid)
    norm = sigma * np.sqrt(2.0 * np.pi)
    for e, s in zip(ee, ss):
        conv += s * np.exp(-0.5 * ((grid - e) / sigma) ** 2) / norm

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(grid, conv, color="C1", lw=1.2)
    ax.set_xlim(*erange)
    ax.set_xlabel(r"Photon energy $E$ (eV)")
    ax.set_ylabel(r"photons s$^{-1}$ eV$^{-1}$")
    ax.set_title(f"Ne VIII Gaussian-instrument broadening (sigma={sigma} eV) - "
                 f"{erange[0]}-{erange[1]} eV")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outfile, dpi=150)
    plt.close(fig)
    print(f"Wrote {outfile} ({len(ee)} lines in band)")


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spfile", nargs="?", type=Path, default=here / "ref" / "Ne03a.sp",
                        help="SP table (default: ref/Ne03a.sp next to this script)")
    parser.add_argument("--outdir", type=Path, default=here, help="output directory")
    parser.add_argument("--main-range", nargs=2, type=float, default=(10.0, 210.0),
                        metavar=("LO", "HI"), help="stick-plot photon-energy range [eV]")
    parser.add_argument("--zoom-range", nargs=2, type=float, default=(15.9, 16.3),
                        metavar=("LO", "HI"), help="zoom panel photon-energy range [eV]")
    parser.add_argument("--gauss-range", nargs=2, type=float, default=(15.9, 16.3),
                        metavar=("LO", "HI"), help="Gaussian panel photon-energy range [eV]")
    parser.add_argument("--euv-gauss", action="store_true",
                        help="use 60-210 eV for the Gaussian panel instead")
    parser.add_argument("--sigma", type=float, default=0.01, help="Gaussian sigma [eV]")
    parser.add_argument("--step", type=float, default=0.001, help="energy grid step [eV]")
    args = parser.parse_args(argv)

    spfile = args.spfile.resolve()
    if not spfile.exists():
        parser.error(f"SP file not found: {spfile}")
    outdir = args.outdir.resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    try:
        energy, strength = parse_sp_table(spfile)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Photon-energy range: {energy.min():.5f} - {energy.max():.4f} eV; "
          f"strength {strength.min():.3g} - {strength.max():.3g} photons/s")

    gauss_range = (60.0, 210.0) if args.euv_gauss else tuple(args.gauss_range)
    try:
        plot_stick(energy, strength, outdir / "NeL_stick.png",
                   tuple(args.main_range), tuple(args.zoom_range))
        plot_gauss(energy, strength, outdir / "NeL_gauss.png",
                   gauss_range, args.sigma, args.step)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
