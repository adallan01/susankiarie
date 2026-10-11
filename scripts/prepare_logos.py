#!/usr/bin/env python3
"""Trim supplied logo files, knock out their flat light backgrounds and save web-ready PNGs.
Usage: python3 scripts/prepare_logos.py <source-dir-or-files...>  (edit MAP below to match file names)"""
import sys, pathlib
from PIL import Image, ImageChops
OUT = pathlib.Path(__file__).resolve().parent.parent / "dist" / "assets" / "logos"
OUT.mkdir(parents=True, exist_ok=True)

def knockout(im, thresh=232, soft=18):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            m = min(r, g, b)
            spread = max(r, g, b) - m
            if m >= thresh and spread < 24:
                px[x, y] = (r, g, b, 0)
            elif m >= thresh - soft and spread < 24:
                k = (m - (thresh - soft)) / soft
                px[x, y] = (r, g, b, int(a * (1 - k)))
    return im

def trim(im, pad=6):
    bbox = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    im = im.crop(bbox)
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad))
    return canvas

def run(name, src, crop=None, thresh=232, height=160):
    im = Image.open(src)
    if crop:
        im = im.crop(crop)
    im = trim(knockout(im, thresh))
    if im.height > height:
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    im.save(OUT / f"{name}.png", optimize=True)
    print(name, im.size)

if __name__ == "__main__":
    U = pathlib.Path(sys.argv[1])
    MAP = [
        ("roam", "28601910-image.png", None, 232),
        ("gsk", "dcf63914-image.jpg", None, 232),
        ("mobiserve", "bb02d067-image.jpg", (100, 130, 500, 215), 222),
        ("adrian", "e90a3249-image.png", None, 232),
        ("ecoligo", "0debdd41-image.jpg", None, 232),
        ("sagemcom", "68e64da5-image.png", None, 232),
        ("applied-principles", "5715b550-image.jpg", None, 232),
        ("vodafone", "239dfe50-image.png", None, 232),
        ("power-wiz", "9758b3bc-image.png", None, 232),
    ]
    for name, f, crop, th in MAP:
        run(name, U / f, crop, th)
