"""The ground decal under the battlefield statues: assets/battle/tower_ground.png (a soft-edged patch on magenta) ->
frontend/public/battle/tower_ground.png. Its edge fades into the magenta, so the alpha comes from how magenta a pixel
is not: only clear dirt is kept, fading out from the inside, so no pink halo and the edge melts into any ground.

Usage: .venv/bin/python tools/slice_ground_decal.py
"""
import cv2
import numpy as np
from PIL import Image

from lib.paths import ASSETS, PUBLIC

a = np.asarray(Image.open(ASSETS / "battle" / "tower_ground.png").convert("RGB")).astype(np.float32)
m = np.minimum(a[..., 0], a[..., 2]) - a[..., 1]   # ~255 on the background, below 0 on the dirt
# keep only what is clearly dirt, and fade it out from the inside: the pink mix at its rim never shows
dirt = (m < -8).astype(np.uint8)
dirt = cv2.morphologyEx(dirt, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(dirt)
dirt = (lab == 1 + int(np.argmax(st[1:, 4]))).astype(np.uint8)
inside = cv2.distanceTransform(dirt, cv2.DIST_L2, 5)
alpha = np.clip(inside / 70, 0, 1) ** 1.3
out = Image.fromarray(np.dstack([a, alpha * 255]).astype(np.uint8), "RGBA")
box = out.getchannel("A").point(lambda v: 255 if v > 30 else 0).getbbox()
print("box", box)
out.crop(box).save(PUBLIC / "battle" / "tower_ground.png", optimize=True)
