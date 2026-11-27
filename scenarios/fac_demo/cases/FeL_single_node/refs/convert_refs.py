from pathlib import Path
import os
import pymupdf

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "pdfs"
MD_DIR = ROOT / "mds"
MD_DIR.mkdir(exist_ok=True)

MAPPING = {
    "2308.14880.pdf": (
        "Zhao2024a_R-Matrix calculations for opacities IV Convergence completeness "
        "and comparison of relativistic R-matrix and distorted wave calculations "
        "for Fe XVII and Fe XVIII.pdf"
    ),
    "2607.21238.pdf": (
        "Zhou2026a_Plasma screening and configuration interaction effects induced "
        "large enhancement on L-shell photoionization cross sections and opacity.pdf"
    ),
    "a-higher-than-predicted-measurement-of-iron-opacity-at-solar-4vx7wp39j8.pdf": (
        "Bailey2015a_A higher-than-predicted measurement of iron opacity at solar "
        "interior temperatures.pdf"
    ),
    "jin2009.pdf": (
        "Jin2009a_Radiative opacity of iron studied using a detailed level "
        "accounting model.pdf"
    ),
    "PhysRevLett.122.235001-accepted.pdf": (
        "Nagayama2019a_Systematic study of L-shell opacity at stellar interior "
        "temperatures.pdf"
    ),
    "zhang2012.pdf": (
        "Zhang2012a_L- and M-shell absorption measurements of radiatively heated "
        "Fe plasma.pdf"
    ),
}


def long_path(path):
    return "\\\\?\\" + str(path.resolve())


for old, new in MAPPING.items():
    src = PDF_DIR / old
    dst = PDF_DIR / new
    if src.exists():
        os.rename(long_path(src), long_path(dst))
        print("renamed: %s" % new)
    elif dst.exists():
        print("already renamed: %s" % new)
    else:
        print("MISSING: %s" % old)

for pdf in sorted(PDF_DIR.glob("*.pdf")):
    doc = pymupdf.open(long_path(pdf))
    parts = [
        "# %s" % pdf.stem,
        "",
        "- Source: `%s`" % pdf.name,
        "- Pages: %d" % len(doc),
        "",
    ]
    for number, page in enumerate(doc, 1):
        parts.extend(["## Page %d" % number, "", page.get_text("text"), ""])
    out = MD_DIR / (pdf.stem + ".md")
    with open(long_path(out), "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts))
    print("converted: %s (%d pages)" % (out.name, len(doc)))
