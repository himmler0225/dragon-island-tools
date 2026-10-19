"""Island props on magenta -> frontend/public/props/ (trimmed, resized).

  assets/props/lamp.png   lamp post with a hanging lantern (Island.createLamps)
  assets/props/grass.png  6 frames of a grass tuft being stepped on (upright -> flat -> springing back),
                          side by side: written as grass_1..6.png, all on one canvas (bottom-aligned)

Prints each prop's size and, for the lamp, where the lantern sits (share of width/height) so the
glow can be placed on it.
Usage: .venv/bin/python tools/slice_props.py
"""
import numpy as np
from PIL import Image

from lib.image import components, key_magenta
from lib.paths import ASSETS, PUBLIC

PROPS = {"lamp": dict(height=300, lantern=(855, 660))}   # lantern centre in source px


def main():
    out = PUBLIC / "props"
    out.mkdir(parents=True, exist_ok=True)
    for name, spec in PROPS.items():
        img = key_magenta(Image.open(ASSETS / "props" / f"{name}.png"))
        ys, xs = np.nonzero(np.asarray(img)[..., 3] > 12)
        box = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
        img = img.crop(box)
        k = spec["height"] / img.height
        img = img.resize((round(img.width * k), spec["height"]), Image.LANCZOS)
        img.save(out / f"{name}.png", optimize=True)
        lx, ly = spec["lantern"]
        print(f"{name}: {img.size}, lantern at ({(lx - box[0]) / (box[2] - box[0]):.3f}, {(ly - box[1]) / (box[3] - box[1]):.3f})")


def grass():
    """Animation frames on a shared canvas: each frame bottom-centred, so they swap in place."""
    out = PUBLIC / "props"
    img = key_magenta(Image.open(ASSETS / "props" / "grass.png"))
    parts = sorted(components(img), key=lambda c: c[0][0])
    w = max(b[2] for b, _ in parts) + 8
    h = max(b[3] for b, _ in parts) + 8
    k = 140 / w   # frames 140 px wide
    for n, (b, m) in enumerate(parts):
        piece = Image.fromarray((np.asarray(img) * (m[..., None] > 0)).astype(np.uint8), "RGBA").crop((b[0], b[1], b[0] + b[2], b[1] + b[3]))
        canvas = Image.new("RGBA", (w, h))
        canvas.alpha_composite(piece, ((w - b[2]) // 2, h - b[3] - 4))
        canvas.resize((round(w * k), round(h * k)), Image.LANCZOS).save(out / f"grass_{n + 1}.png", optimize=True)
    print(f"grass: {len(parts)} frames {round(w * k)}x{round(h * k)}")


if __name__ == "__main__":
    grass()
    main()
