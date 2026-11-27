"""Streaming parsers for the full-physics FeL opacity scene."""

from __future__ import annotations

import math
from typing import Dict, Iterator, List, Optional, TextIO, Tuple


class LineReader(object):
    def __init__(self, handle: TextIO):
        self._handle = handle
        self._buffer = None  # type: Optional[str]

    def next_nonempty(self) -> Optional[str]:
        while True:
            line = self._buffer if self._buffer is not None else self._handle.readline()
            self._buffer = None
            if not line:
                return None
            line = line.rstrip("\r\n")
            if line.strip():
                return line


def interp_sorted(xs: List[float], ys: List[float], x: float) -> float:
    if not xs:
        return 0.0
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            ratio = (math.log(x) - math.log(xs[i])) / (math.log(xs[i + 1]) - math.log(xs[i]))
            return math.exp(math.log(ys[i]) + ratio * (math.log(ys[i + 1]) - math.log(ys[i])))
    return ys[-1]


def iter_rr(path) -> Iterator[Dict]:
    """Yield RR/PI blocks from an ASCII *a.rr table (self-contained copy)."""
    with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
        reader = LineReader(handle)
        first = None
        while True:
            line = reader.next_nonempty()
            if line is None:
                return
            if "=" in line and line.split("=", 1)[0].strip().startswith("NELE"):
                first = line
                break
        while first is not None:
            values = {}  # type: Dict
            line = first
            while True:
                key, raw = _kv(line)
                if key is None:
                    raise ValueError("bad RR header: %s" % line)
                value = int(float(raw))
                values[key] = value
                if key in ("NTEGRID", "NEGRID", "NUSR"):
                    nums = []
                    for _ in range(value):
                        nxt = reader.next_nonempty()
                        nums.append(float(nxt.split()[0]))
                    values[key + "_VALUES"] = nums
                    if key == "NUSR":
                        break
                line = reader.next_nonempty()
            nusr = int(values.get("NUSR", 0))
            energy = values.get("NUSR_VALUES", values.get("NEGRID_VALUES", []))
            for _ in range(int(values.get("NTRANS", 0))):
                head = reader.next_nonempty().split()
                reader.next_nonempty()
                rr, pi = [], []
                for _ in range(nusr):
                    parts = reader.next_nonempty().split()
                    rr.append(float(parts[1]))
                    pi.append(float(parts[2]))
                yield {
                    "nele": int(values.get("NELE", -1)),
                    "bound_index": int(head[0]),
                    "delta_e": float(head[4]),
                    "energy_ev": list(energy),
                    "rr_crosssection": rr,
                    "pi_crosssection": pi,
                }
            nxt = reader.next_nonempty()
            if nxt is None:
                return
            first = nxt if "=" in nxt and nxt.split("=", 1)[0].strip().startswith("NELE") else None


def _kv(line: str):
    if "=" not in line:
        return None, None
    key, value = line.split("=", 1)
    return key.strip().split()[0] if key.strip() else "", value.strip()


def _is_data(parts: List[str]) -> bool:
    return len(parts) >= 8 and parts[0].lstrip("-").isdigit() and parts[1].lstrip("-").isdigit()


def iter_sp_populations_full(path, min_population=0.0, expected_nele=None) -> Iterator[Dict]:
    current = {}  # type: Dict
    seen = 0
    last_nele = -1
    with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            if "=" in line:
                key, raw = _kv(line)
                if key == "NELE":
                    last_nele = int(float(raw))
                elif key == "NTRANS":
                    current = {"ntrans": int(float(raw)), "nele": last_nele}
                    seen = 0
                elif current:
                    if key == "TYPE":
                        current["type"] = raw
                    elif key == "IBLK":
                        current["iblk"] = int(float(raw))
                continue
            parts = line.split()
            if not _is_data(parts) or current.get("type") != "0000000":
                continue
            if seen >= int(current.get("ntrans", 0)):
                continue
            seen += 1
            nele = int(current.get("nele", -1))
            if expected_nele is not None and nele != expected_nele:
                continue
            population = float(parts[3])
            if population < min_population:
                continue
            yield {
                "nele": nele,
                "global_level": int(parts[0]),
                "block_level": int(parts[1]),
                "iblk": int(current.get("iblk", -1)),
                "energy_ev": float(parts[2]),
                "population": population,
                "deg": float(parts[4]),
                "total_rate": float(parts[5]),
                "wimp": float(parts[6]) if len(parts) > 6 else 0.0,
                "wstk": float(parts[7]) if len(parts) > 7 else 0.0,
            }


def iter_sp_line_widths(path, min_strength=1.0e-12) -> Iterator[Dict]:
    """Yield line-block widths from verbose ASCII .sp tables.

    The key is returned as (upper, lower, rounded_energy). Both orderings are
    kept by callers when matching TR transitions.
    """
    current = {}  # type: Dict
    seen = 0
    last_nele = -1
    with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            if "=" in line:
                key, raw = _kv(line)
                if key == "NELE":
                    last_nele = int(float(raw))
                elif key == "NTRANS":
                    current = {"ntrans": int(float(raw)), "nele": last_nele}
                    seen = 0
                elif current:
                    if key == "TYPE":
                        current["type"] = raw
                    elif key == "IBLK":
                        current["iblk"] = int(float(raw))
                continue
            parts = line.split()
            if not _is_data(parts) or seen >= int(current.get("ntrans", 0)):
                continue
            if current.get("type") in (None, "0000000"):
                continue
            seen += 1
            if len(parts) >= 9:
                energy = float(parts[2])
                sdev = float(parts[3])
                strength = float(parts[4])
                rrate = float(parts[5])
                trate = float(parts[6])
                wimp = float(parts[7])
                wstk = float(parts[8])
            else:
                energy = float(parts[2])
                sdev = 0.0
                strength = float(parts[3])
                rrate = float(parts[4])
                trate = float(parts[5])
                wimp = float(parts[6])
                wstk = float(parts[7])
            if strength < min_strength:
                continue
            yield {
                "nele": int(current.get("nele", -1)),
                "upper": int(parts[0]),
                "lower": int(parts[1]),
                "energy_ev": energy,
                "sdev": sdev,
                "strength": strength,
                "rate": rrate,
                "total_rate": trate,
                "wimp": wimp,
                "wstk": wstk,
            }


def iter_tr_transitions_full(path, min_gf=0.0) -> Iterator[Dict]:
    with open(str(path), "r", encoding="utf-8", errors="replace") as handle:
        current = {}  # type: Dict
        for line in handle:
            if not line.strip():
                continue
            if "=" in line:
                key, raw = _kv(line)
                if key == "NELE":
                    current = {"nele": int(float(raw))}
                elif key == "NTRANS" and current:
                    current["ntrans"] = int(float(raw))
                continue
            parts = line.split()
            if len(parts) < 8 or not parts[0].lstrip("-").isdigit():
                continue
            uta = len(parts) == 10
            gf = float(parts[6] if uta else parts[5])
            if gf < min_gf:
                continue
            yield {
                "nele": int(current.get("nele", -1)),
                "upper_index": int(parts[0]),
                "upper_2J": int(parts[1]),
                "lower_index": int(parts[2]),
                "lower_2J": int(parts[3]),
                "delta_e": float(parts[4]),
                "gf": gf,
                "rate": float(parts[7] if uta else parts[6]),
                "sdev": float(parts[5]) if uta else 0.0,
                "multipole": float(parts[8] if uta else parts[7]),
            }


def load_csv(path) -> List[Dict]:
    import csv

    with open(str(path), "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def energy_grid(config: Dict) -> Tuple[List[float], List[float]]:
    grid = config["energy_grid"]
    lo, hi, step = float(grid["min"]), float(grid["max"]), float(grid["step"])
    count = int(round((hi - lo) / step)) + 1
    hc = 12398.419843320026
    pairs = sorted((hc / (lo + i * step), lo + i * step) for i in range(count))
    return [p[0] for p in pairs], [p[1] for p in pairs]
