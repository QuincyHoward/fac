#!/usr/bin/env python3
"""Create a labeled contact sheet from a figure manifest for visual review."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--thumb-width", type=int, default=420)
    parser.add_argument("--thumb-height", type=int, default=260)
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    cell_w = args.thumb_width + 30
    cell_h = args.thumb_height + 50
    cols = 2
    rows = (len(manifest) + cols - 1) // cols
    sheet = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    draw = ImageDraw.Draw(sheet)

    for i, item in enumerate(manifest):
        image = Image.open(item["path"]).convert("RGB")
        image.thumbnail((args.thumb_width, args.thumb_height))
        x = (i % cols) * cell_w + 15
        y = (i // cols) * cell_h + 28
        sheet.paste(image, (x, y))
        draw.text((x, y - 20), item["id"], fill="black")

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print("saved %s %s" % (args.output, sheet.size))


if __name__ == "__main__":
    main()
