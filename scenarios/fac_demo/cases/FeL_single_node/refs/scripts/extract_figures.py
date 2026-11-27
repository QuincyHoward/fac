#!/usr/bin/env python3
"""Render PDF pages and crop candidate literature figures with PyMuPDF."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import pymupdf as fitz
from PIL import Image, ImageStat

CAPTION_RE = re.compile(r"^(FIG\.|Figure)\s*[0-9]+", re.IGNORECASE)


def discover(pdf_dir: Path, output: Path):
    candidates = []
    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        doc = fitz.open(str(pdf_path))
        for page_index, page in enumerate(doc):
            for line in page.get_text().splitlines():
                text = line.strip()
                if CAPTION_RE.match(text):
                    candidates.append({
                        "pdf": pdf_path.name,
                        "page": page_index + 1,
                        "caption": text[:240],
                    })
        doc.close()
    with open(str(output), "w", encoding="utf-8") as handle:
        json.dump(candidates, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print("candidates=%d -> %s" % (len(candidates), output))


def locate_caption(page, caption):
    needle = caption.strip()
    rects = page.search_for(needle)
    if not rects and len(needle) > 40:
        rects = page.search_for(needle[:40])
    return rects[0] if rects else None


def crop_rect(page, spec, caption_rect):
    if spec.get("crop_box"):
        return fitz.Rect(spec["crop_box"])
    if caption_rect is None:
        return fitz.Rect(40, 40, page.rect.width - 40, page.rect.height - 40)
    top = max(30.0, spec.get("top_margin_pt", 36.0))
    bottom = max(top + 20.0, caption_rect.y0 - float(spec.get("caption_gap_pt", 6.0)))
    left = float(spec.get("left_margin_pt", 40.0))
    right = page.rect.width - float(spec.get("right_margin_pt", 40.0))
    return fitz.Rect(left, top, right, bottom)


def extract(spec_path: Path, pdf_dir: Path, out_dir: Path, dpi: int):
    with open(str(spec_path), "r", encoding="utf-8") as handle:
        specs = json.load(handle)
    crops = out_dir / "crops"
    raw_pages = out_dir / "raw_pages"
    crops.mkdir(parents=True, exist_ok=True)
    raw_pages.mkdir(parents=True, exist_ok=True)

    manifest = []
    for spec in specs:
        pdf_path = pdf_dir / spec["pdf"]
        if not pdf_path.exists():
            manifest.append({"id": spec["id"], "ok": False, "error": "missing pdf", "pdf": str(pdf_path)})
            continue
        doc = fitz.open(str(pdf_path))
        page_number = int(spec["page"])
        if page_number < 1 or page_number > doc.page_count:
            manifest.append({"id": spec["id"], "ok": False, "error": "bad page", "page": page_number})
            doc.close()
            continue
        page = doc[page_number - 1]
        caption_rect = locate_caption(page, spec.get("caption", ""))
        rect = crop_rect(page, spec, caption_rect)
        matrix = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
        out_path = crops / ("%s.png" % spec["id"])
        pix.save(str(out_path))

        with Image.open(str(out_path)) as image:
            stat = ImageStat.Stat(image.convert("L"))
            nonblank = stat.stddev[0] > 2.0
        manifest.append({
            "id": spec["id"],
            "ok": nonblank,
            "pdf": spec["pdf"],
            "page": page_number,
            "figure": spec.get("figure", ""),
            "caption": spec.get("caption", ""),
            "crop_box_pt": [rect.x0, rect.y0, rect.x1, rect.y1],
            "caption_found": caption_rect is not None,
            "path": str(out_path),
            "bytes": out_path.stat().st_size,
            "fac_counterpart": spec.get("fac_counterpart", ""),
            "comparison_mode": spec.get("comparison_mode", "side_by_side"),
            "notes": spec.get("notes", ""),
        })
        doc.close()
        print("%s: %s (%d bytes)" % (spec["id"], "OK" if nonblank else "BLANK", out_path.stat().st_size))

    with open(str(out_dir / "figure_manifest.json"), "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return 0 if all(item.get("ok") for item in manifest) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--discover-captions")
    parser.add_argument("--spec")
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args(argv)

    pdf_dir = Path(args.pdf_dir).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.discover_captions:
        return discover(pdf_dir, Path(args.discover_captions).resolve())
    if not args.spec:
        parser.error("--spec is required unless --discover-captions is given")
    return extract(Path(args.spec).resolve(), pdf_dir, out_dir, args.dpi)


if __name__ == "__main__":
    raise SystemExit(main())
