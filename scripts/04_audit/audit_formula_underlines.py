#!/usr/bin/env python3
"""Audit README formula underline syntax.

Rules:
- unsourced formulas must be written as \\underline{$...$};
- HTML <u>...</u> is forbidden;
- explanatory \\underline{\\text{...}} notes are forbidden.
Inline code is ignored so skill rule documents can quote forbidden syntax.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INLINE_CODE = re.compile(r"`[^`]*`")
UNDERLINE = re.compile(r"\\underline\{")
VALID_UNDERLINE = re.compile(r"\\underline\{\$[^$\n]+\$\}")


def strip_code(text: str) -> str:
    return INLINE_CODE.sub("", text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Project root.")
    args = parser.parse_args(argv)

    base = Path(args.root).resolve()
    issues: list[str] = []
    count = 0

    for path in sorted(base.rglob("*.md")):
        rel = path.relative_to(base)
        if ".codebuddy" in rel.parts and "plans" in rel.parts:
            continue
        text = strip_code(path.read_text(encoding="utf-8", errors="replace"))
        if "<u>" in text or "</u>" in text:
            issues.append(f"{rel}: HTML <u> residue")
        if "\\underline{\\text{" in text:
            issues.append(f"{rel}: explanatory underline note residue")
        starts = list(UNDERLINE.finditer(text))
        valid = VALID_UNDERLINE.findall(text)
        count += len(starts)
        if len(starts) != len(valid):
            issues.append(f"{rel}: {len(starts) - len(valid)} malformed underline formula")

    print(f"underline formulas: {count}")
    print("issues:")
    print("\n".join(issues) if issues else "  none")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
