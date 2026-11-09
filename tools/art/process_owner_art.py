#!/usr/bin/env python3
"""Prepare owner-supplied drawings for the web.

Offline, owner-controlled step. For each source drawing it:
  * flattens transparency onto paper white,
  * trims empty margins (keeps a padding band so nothing is cut),
  * caps the long edge at 1600 px,
  * writes WebP (primary) and PNG (fallback) with NO metadata
    (no EXIF, no device or location data survives),
  * prints a SHA-256 for each output so the asset manifest can record it.

Usage:
  python3 tools/art/process_owner_art.py <source-dir> apps/web/public/art/owner
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageChops

# source file name -> published slug (the manifest uses the slug)
SOURCES = {
    "canvas.png": "robo-beast-roar",
    "canvas_1.png": "yeti-showdown",
    "canvas_3.png": "wave-ride",
    "canvas_4.png": "stretch-punch-replay",
    "canvas_5.png": "stretch-punch",
}
PAPER = (250, 250, 250)
MAX_EDGE = 1600
PAD_RATIO = 0.04


def trim(im: Image.Image) -> Image.Image:
    bg = Image.new("RGB", im.size, PAPER)
    diff = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 18 else 0)
    box = diff.getbbox()
    if not box:
        return im
    pad = int(max(im.size) * PAD_RATIO)
    left, top, right, bottom = box
    box = (max(0, left - pad), max(0, top - pad), min(im.width, right + pad), min(im.height, bottom + pad))
    return im.crop(box)


def main(src_dir: str, out_dir: str) -> None:
    src, out = Path(src_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, slug in SOURCES.items():
        raw = Image.open(src / name).convert("RGBA")
        flat = Image.new("RGB", raw.size, PAPER)
        flat.paste(raw, mask=raw.split()[3])
        img = trim(flat)
        scale = min(1.0, MAX_EDGE / max(img.size))
        if scale < 1.0:
            img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        webp = out / f"{slug}.webp"
        png = out / f"{slug}.png"
        img.save(webp, "WEBP", quality=86, method=6)
        img.quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(png, "PNG", optimize=True)
        for f in (webp, png):
            digest = hashlib.sha256(f.read_bytes()).hexdigest()
            print(f"{f.name}\t{img.width}x{img.height}\t{f.stat().st_size}\tsha256:{digest}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
