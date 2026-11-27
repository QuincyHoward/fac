"""Streaming readers for FAC ASCII tables used by the FeL opacity example.

Only the fields needed for opacity synthesis are retained. The large ``.sp``
files are scanned line by line; population blocks are extracted without loading
the whole file into memory.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterator, List, Optional, TextIO

MAXNUSR = 10000


class LineReader(object):
    def __init__(self, handle: TextIO):
        self._handle = handle
        self._buffer = None  # type: Optional[str]

    def next_nonempty(self) -> Optional[str]:
        while True:
            if self._buffer is not None:
                line = self._buffer
                self._buffer = None
            else:
                line = self._handle.readline()
            if not line:
                return None
            line = line.rstrip("\r\n")
            if line.strip():
                return line

    def pushback(self, line: str) -> None:
        self._buffer = line


def _key_value(line: str):
    if "=" not in line:
        return None, None
    key, value = line.split("=", 1)
    key = key.strip().split()[0] if key.strip() else ""
    return key, value.strip()


def _parse_block_header(reader: LineReader, first_line: str) -> Dict[str, Any]:
    values = {}  # type: Dict[str, Any]
    line = first_line
    while True:
        key, raw = _key_value(line)
        if key is None:
            raise ValueError("unexpected RR header line: %s" % line)
        value = int(float(raw))
        values[key] = value
        if key in ("NTEGRID", "NEGRID", "NUSR"):
            numbers = []  # type: List[float]
            for _ in range(value):
                nxt = reader.next_nonempty()
                if nxt is None:
                    raise ValueError("truncated numeric list for %s" % key)
                numbers.append(float(nxt.split()[0]))
            values[key + "_VALUES"] = numbers
            if key == "NUSR":
                break
        line = reader.next_nonempty()
        if line is None:
            raise ValueError("truncated RR block")
    return values


def iter_rr(path: str) -> Iterator[Dict[str, Any]]:
    """Yield RR/PI blocks from an ASCII ``*a.rr`` table."""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        reader = LineReader(handle)
        first = None  # type: Optional[str]
        while True:
            line = reader.next_nonempty()
            if line is None:
                return
            key, _ = _key_value(line)
            if key == "NELE":
                first = line
                break
        while first is not None:
            header = _parse_block_header(reader, first)
            nusr = int(header.get("NUSR", 0))
            if nusr <= 0 or nusr > MAXNUSR:
                raise ValueError("invalid NUSR in %s: %d" % (path, nusr))
            energy = header.get("NUSR_VALUES", header.get("NEGRID_VALUES", []))
            for _ in range(int(header.get("NTRANS", 0))):
                head = reader.next_nonempty()
                params_line = reader.next_nonempty()
                if head is None or params_line is None:
                    raise ValueError("truncated RR transition in %s" % path)
                head_parts = head.split()
                pi = []  # type: List[float]
                rr = []  # type: List[float]
                for _ in range(nusr):
                    row = reader.next_nonempty()
                    if row is None:
                        raise ValueError("truncated RR energy rows in %s" % path)
                    parts = row.split()
                    rr.append(float(parts[1]))
                    pi.append(float(parts[2]))
                yield {
                    "nele": int(header.get("NELE", -1)),
                    "ntrans": int(header.get("NTRANS", 0)),
                    "bound_index": int(head_parts[0]),
                    "bound_2J": int(head_parts[1]),
                    "free_index": int(head_parts[2]),
                    "free_2J": int(head_parts[3]),
                    "delta_e": float(head_parts[4]),
                    "delta_l": int(head_parts[5]),
                    "parameters": [float(v) for v in params_line.split()],
                    "energy_ev": list(energy),
                    "rr_crosssection": rr,
                    "pi_crosssection": pi,
                }
            nxt = reader.next_nonempty()
            if nxt is None:
                return
            key, _ = _key_value(nxt)
            first = nxt if key == "NELE" else None


def _is_data_line(parts: List[str]) -> bool:
    if len(parts) < 6:
        return False
    if not parts[0].lstrip("-").isdigit():
        return False
    if not parts[1].lstrip("-").isdigit():
        return False
    return True


def iter_sp_populations(path: str, min_population: float = 0.0) -> Iterator[Dict[str, Any]]:
    """Yield ``TYPE=0000000`` population rows from an ASCII ``*.sp`` table."""
    current = {}  # type: Dict[str, Any]
    seen = 0
    last_nele = -1
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            if "=" in line:
                key, raw = _key_value(line)
                if key == "NELE":
                    last_nele = int(float(raw))
                if key == "NTRANS":
                    current = {"ntrans": int(float(raw)), "nele": last_nele}
                    seen = 0
                elif current:
                    if key == "TYPE":
                        current["type"] = raw
                    elif key == "IBLK":
                        current["iblk"] = int(float(raw))
                continue
            parts = line.split()
            if not _is_data_line(parts):
                continue
            ntrans = int(current.get("ntrans", 0))
            if seen >= ntrans or current.get("type") != "0000000":
                continue
            population = float(parts[3])
            seen += 1
            if population < min_population:
                continue
            yield {
                "nele": int(current.get("nele", -1)),
                "iblk": int(current.get("iblk", -1)),
                "block": int(parts[0]),
                "level": int(parts[1]),
                "energy_ev": float(parts[2]),
                "population": population,
                "deg": float(parts[4]),
                "total_rate": float(parts[5]),
            }


def iter_tr_transitions(path: str, min_gf: float = 0.0) -> Iterator[Dict[str, Any]]:
    """Yield bound-bound transitions from an ASCII ``*a.tr`` table."""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        reader = LineReader(handle)
        first = None  # type: Optional[str]
        while True:
            line = reader.next_nonempty()
            if line is None:
                return
            key, _ = _key_value(line)
            if key == "NELE":
                first = line
                break
        while first is not None:
            values = {}  # type: Dict[str, Any]
            line = first
            while True:
                key, raw = _key_value(line)
                if key is None:
                    break
                if key == "NELE":
                    values["nele"] = int(float(raw))
                elif key == "NTRANS":
                    values["ntrans"] = int(float(raw))
                line = reader.next_nonempty()
                if line is None:
                    return
            for _ in range(int(values.get("ntrans", 0))):
                parts = line.split()
                if len(parts) >= 8:
                    uta = len(parts) == 10
                    gf = float(parts[6] if uta else parts[5])
                    if gf < min_gf:
                        continue
                    yield {
                        "nele": int(values.get("nele", -1)),
                        "upper_index": int(parts[0]),
                        "upper_2J": int(parts[1]),
                        "lower_index": int(parts[2]),
                        "lower_2J": int(parts[3]),
                        "delta_e": float(parts[4]),
                        "gf": gf,
                        "rate": float(parts[7] if uta else parts[6]),
                    }
                line = reader.next_nonempty()
                if line is None:
                    return
            nxt = reader.next_nonempty()
            if nxt is None:
                return
            key, _ = _key_value(nxt)
            first = nxt if key == "NELE" else None


def en_block_offsets(path: str) -> List[int]:
    """Return cumulative level offsets for each block of an ASCII ``*.en`` file."""
    offsets = [0]
    total = 0
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "NLEV" and parts[1] == "=":
                count = int(float(parts[2]))
                total += count
                offsets.append(total)
    return offsets


def en_level_map(path: str, decimals: int = 3) -> Dict[tuple, int]:
    """Map (energy_eV, 2J+1) to the global ILEV used by DB_RR ASCII files."""
    mapping = {}  # type: Dict[tuple, int]
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) < 7:
                continue
            if not parts[0].isdigit() or not parts[1].lstrip("-").isdigit():
                continue
            try:
                energy = float(parts[2])
                two_j = int(float(parts[5]))
            except ValueError:
                continue
            key = (round(energy, decimals), two_j + 1)
            if key not in mapping:
                mapping[key] = int(parts[0])
    return mapping


def interp_sorted(xs: List[float], ys: List[float], x: float) -> float:
    """Piecewise linear interpolation in log-log space; inputs must be sorted."""
    if not xs:
        return 0.0
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            lx = math.log(x)
            ratio = (lx - math.log(xs[i])) / (math.log(xs[i + 1]) - math.log(xs[i]))
            return math.exp(math.log(ys[i]) + ratio * (math.log(ys[i + 1]) - math.log(ys[i])))
    return ys[-1]


def interp_loglog(x_grid: List[float], y_grid: List[float], x: float) -> float:
    """Piecewise linear interpolation in log-log space with boundary clamping."""
    pairs = [(a, b) for a, b in zip(x_grid, y_grid) if a > 0 and b > 0]
    if not pairs:
        return 0.0
    pairs.sort(key=lambda item: item[0])
    return interp_sorted([item[0] for item in pairs], [item[1] for item in pairs], x)
