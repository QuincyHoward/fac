#!/usr/bin/env python3
"""Compose literature crops and FAC counterparts into side-by-side figures."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


def compose(pair, scene_dir, out_dir, height=520):
    lit = Image.open(pair["path"]).convert("RGB")
    fac_path = (scene_dir / pair["fac_counterpart"]).resolve()
    if not fac_path.exists():
        return None
    fac = Image.open(str(fac_path)).convert("RGB")

    def resize(image):
        ratio = height / image.height
        return image.resize((max(1, int(image.width * ratio)), height), Image.Resampling.LANCZOS)

    lit = resize(lit)
    fac = resize(fac)
    pad = 18
    label_h = 34
    width = lit.width + fac.width + pad * 3
    canvas = Image.new("RGB", (width, height + label_h + pad * 2), "white")
    draw = ImageDraw.Draw(canvas)
    canvas.paste(lit, (pad, label_h + pad))
    canvas.paste(fac, (lit.width + pad * 2, label_h + pad))
    draw.text((pad, 8), "Literature: %s" % pair["figure"], fill="#244B7A")
    draw.text((lit.width + pad * 2, 8), "FAC counterpart", fill="#244B7A")
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / ("%s.png" % pair["id"])
    canvas.save(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--scene-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--height", type=int, default=520)
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    pairs = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir = Path(args.output_dir).resolve()
    scene_dir = Path(args.scene_dir).resolve()

    ok = True
    for pair in pairs:
        output = compose(pair, scene_dir, out_dir, args.height)
        pair["side_by_side"] = str(output) if output else ""
        pair["side_by_side_ok"] = output is not None
        if output is None:
            ok = False
        print("%s: %s" % (pair["id"], "OK" if output else "MISSING FAC"))
    manifest_path.write_text(json.dumps(pairs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
