"""Give a lower jaw drawn on its own a dark mouth interior: the jaw's shape pulled up behind it, so an opened jaw
shows a mouth, not the background behind the head. Writes <sheet stem>_jaw.png next to the sheet (on magenta).

Usage: .venv/bin/python tools/jaw_with_mouth.py <sheet.png> <x> <y> [up=80]
  x, y: a point inside the jaw on the sheet
"""
import sys

import cv2
import numpy as np
from PIL import Image

from lib.image import components, key_magenta

MOUTH_RGB = (58, 20, 34)

if __name__ == "__main__":
    src = sys.argv[1]
    x, y = int(sys.argv[2]), int(sys.argv[3])
    up = int(sys.argv[4]) if len(sys.argv) > 4 else 80
    img = key_magenta(Image.open(src))
    (bx, by, bw, bh), mask = min(components(img), key=lambda c: (c[0][0] + c[0][2] / 2 - x) ** 2 + (c[0][1] + c[0][3] / 2 - y) ** 2)
    a = np.asarray(img).copy()
    jaw = mask.astype(bool)
    mouth = np.zeros_like(jaw)
    for dy in range(0, up + 1, 4):
        mouth |= np.roll(jaw, -dy, axis=0)
    mouth = cv2.erode(mouth.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool)
    out = np.zeros_like(a)
    out[mouth, :3] = MOUTH_RGB
    out[mouth, 3] = 255
    out[jaw] = a[jaw]
    sheet = Image.new("RGBA", img.size, (255, 0, 255, 255))
    sheet.alpha_composite(Image.fromarray(out))
    dst = src.rsplit(".", 1)[0] + "_jaw.png"
    sheet.convert("RGB").save(dst)
    print(dst, "mouth up", up)
