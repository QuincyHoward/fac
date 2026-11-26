"""Optional plotting helper with delayed matplotlib import."""

from __future__ import annotations

from pathlib import Path


def plot_two_columns(path: Path, output: Path, xcol: int = 0, ycol: int = 1, label: str = "data") -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Plotting requires matplotlib; install requirements-dev.txt") from exc

    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) <= max(xcol, ycol):
            continue
        try:
            rows.append((float(parts[xcol]), float(parts[ycol])))
        except ValueError:
            continue
    if not rows:
        raise ValueError(f"No numeric two-column data found in {path}")

    x, y = zip(*rows)
    plt.figure(figsize=(7, 4))
    plt.plot(x, y, label=label)
    plt.xlabel("column " + str(xcol))
    plt.ylabel("column " + str(ycol))
    plt.legend()
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output)
    plt.close()
