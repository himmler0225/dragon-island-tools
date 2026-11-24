"""Split a whole head drawn with its mouth closed into the head and its lower jaw, by the jaw's colour.

Usage: .venv/bin/python tools/split_head_jaw.py <dragon_id> <hue_lo> <hue_hi> [--no-mouth] [--up N]
  reads  assets/dragons/<id>/parts/head.png (one head on magenta; the lower jaw is the only part in that
         OpenCV hue range, 0-179, e.g. 35 85 for green)
  writes parts/head_upper.png: the head without the jaw (its snout keeps its own outline)
         parts/head_jaw.png:   the jaw (with its outline) over a dark mouth interior that reaches up under
                               the snout, so an opened jaw shows a mouth, not the background
                               (--no-mouth: the jaw alone, for a mouth that only opens a little)
Both are cut from the same image, so they fit exactly; place them with the same scale and offset.
"""
import sys

import cv2
import numpy as np
from PIL import Image

from lib.image import key_distance
from lib.paths import DRAGONS

OUTLINE = 9        # px of outline around the jaw colour that belongs to the jaw
MOUTH_UP = 60      # px the mouth interior reaches above the jaw (hidden under the snout at rest); --up N to change
MOUTH_RGB = (58, 18, 64)

did, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
NO_MOUTH = '--no-mouth' in sys.argv
if '--up' in sys.argv:
    MOUTH_UP = int(sys.argv[sys.argv.index('--up') + 1])
P = DRAGONS / did / "parts"
img = key_distance(Image.open(P / "head.png"), 50, 130)
a = np.asarray(img).copy()
solid = a[..., 3] > 0
hsv = cv2.cvtColor(np.ascontiguousarray(a[..., :3]), cv2.COLOR_RGB2HSV)
colour = ((hsv[..., 0] >= lo) & (hsv[..., 0] <= hi) & (hsv[..., 1] > 90) & (hsv[..., 2] > 60) & solid).astype(np.uint8)
n, lab, st, _ = cv2.connectedComponentsWithStats(colour)
big = st[1:, 4].max()
keep = [i for i in range(1, n) if st[i, 4] > max(400, 0.1 * big)]   # the jaw's segments, not specks or small marks of that colour
colour = np.isin(lab, keep).astype(np.uint8)
colour = cv2.morphologyEx(colour, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))   # the dark lines between segments
jaw = cv2.dilate(colour, np.ones((2 * OUTLINE + 1,) * 2, np.uint8)) & solid
# the head keeps, of the jaw's outline, only the line along the snout (next to the head's own skin);
# the rest of that outline (under the jaw) goes with the jaw
core = solid & ~jaw.astype(bool)
# (opened: the thin soft edge just outside the jaw's outline is not head skin)
core = cv2.morphologyEx(core.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8)).astype(bool)
near = cv2.dilate(core.astype(np.uint8), np.ones((2 * OUTLINE + 7,) * 2, np.uint8)).astype(bool)
head = (solid & ~jaw.astype(bool) & near) | (solid & jaw.astype(bool) & ~colour.astype(bool) & near)

upper = a.copy(); upper[~head, 3] = 0
# the mouth: the jaw's shape pulled up under the snout, dark, behind the jaw
mouth = np.zeros_like(colour)
for dy in range(0, MOUTH_UP + 1, 4):
    mouth |= np.roll(colour, -dy, axis=0)
mouth = cv2.erode(mouth, np.ones((5, 5), np.uint8)).astype(bool) & solid
lower = np.zeros_like(a)
if not NO_MOUTH:
    lower[mouth, :3] = MOUTH_RGB; lower[mouth, 3] = 255
lower[jaw.astype(bool)] = a[jaw.astype(bool)]
for arr, name in ((upper, "head_upper.png"), (lower, "head_jaw.png")):
    # on magenta, like every source sheet (build_rig keys the background out)
    out = Image.new("RGBA", img.size, (255, 0, 255, 255))
    out.alpha_composite(Image.fromarray(arr))
    out.convert("RGB").save(P / name)
print(did, "head_upper.png + head_jaw.png", int(colour.sum()), "jaw px")
