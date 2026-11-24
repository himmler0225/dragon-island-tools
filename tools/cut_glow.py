"""Cut a glowing piece (an orb with a soft halo) off magenta into an RGBA png, keeping the halo.

Usage: .venv/bin/python tools/cut_glow.py <src.png> <x0> <y0> <x1> <y1> <out.png>
The solid core (the largest non-magenta island, holes filled) is opaque; around it, a pixel's alpha is
how far it is from magenta (pink halo over magenta -> half transparent pink), its colour un-mixed from
the magenta behind it. key_magenta / key_distance would eat the halo and turn pink-purple spots grey.
"""
import sys

import cv2
import numpy as np
from PIL import Image

src, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)[y0:y1, x0:x1]
M = np.array([255, 0, 255], np.float32)
alpha = np.clip(a[..., 1] / 200, 0, 1)   # magenta has no green; the halo and the moon do
solid = (alpha > 0.6).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(solid)
core = (lab == 1 + np.argmax(st[1:, 4])).astype(np.uint8)
cs, _ = cv2.findContours(core, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(core, cs, -1, 1, -1)   # fill the spots inside it
core = cv2.erode(core, np.ones((5, 5), np.uint8)).astype(bool)
alpha[core] = 1
rgb = (a - (1 - alpha[..., None]) * M) / np.maximum(alpha[..., None], 1e-3)
rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
rgba[alpha < 0.03] = 0
Image.fromarray(rgba, "RGBA").save(out)
print(out, rgba.shape)
