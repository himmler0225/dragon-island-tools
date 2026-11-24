"""Statue break effect (assets/battle/tower_break.png: 8 frames, 4x2, a rubble pile cracking, bursting, flying apart
and settling in dust, on magenta) -> frontend/public/battle/tower_break.png, the same 4x2 grid, transparent.

The magenta is unmixed rather than keyed: the dust clouds are half see-through and were drawn tinted by it, so each
pixel's magenta share (how far red and blue stand above green) becomes transparency and is taken out of its colour;
the dust, drawn pink too, is turned sandy.

Usage: .venv/bin/python tools/slice_tower_break.py
"""
import numpy as np
from PIL import Image

from lib.paths import ASSETS, PUBLIC

SRC = ASSETS / "battle" / "tower_break.png"
DST = PUBLIC / "battle" / "tower_break.png"


def unmix_magenta(img):
    c = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    m = np.clip(np.minimum(r, b) - g, 0, 1)   # magenta share
    m = np.clip((m - 0.04) / 0.92, 0, 1)      # paper noise: a little magenta is still opaque
    a = 1 - m
    M = np.array([1.0, 0.0, 1.0])
    f = (c - m[..., None] * M) / np.maximum(a, 1e-3)[..., None]
    f = np.clip(f, 0, 1)
    # the dust was drawn pink as well: what is still pinkish (red and blue over green) turns sandy, same brightness
    r2, g2, b2 = f[..., 0], f[..., 1], f[..., 2]
    pink = np.clip((r2 - g2 - 0.04) / 0.12, 0, 1) * np.clip((b2 - g2 + 0.06) / 0.08, 0, 1)   # red over green, blue not under it (not orange)
    lum = f @ np.array([0.3, 0.55, 0.15])
    sand = np.clip(lum[..., None] * np.array([1.12, 1.0, 0.8]) / 0.95, 0, 1)
    f = f * (1 - pink[..., None]) + sand * pink[..., None]
    out = np.dstack([f, a])
    out[a < 0.03] = 0
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


if __name__ == "__main__":
    out = unmix_magenta(Image.open(SRC))
    out.save(DST)
    print(DST, out.size)
