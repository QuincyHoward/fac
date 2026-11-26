#!/usr/bin/env python3
"""Plot a two-column spectrum file under plots/."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCEN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCEN))

from common.plotting import plot_two_columns  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("table", help="Two-column numeric table.")
    parser.add_argument("--output", default=str(SCEN / "fac_demo" / "plots" / "crm_spectrum.png"))
    args = parser.parse_args(argv)

    try:
        plot_two_columns(Path(args.table).resolve(), Path(args.output).resolve(), label="spectrum")
    except (RuntimeError, ValueError) as exc:
        print(exc)
        return 1
    print("Wrote:", args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
