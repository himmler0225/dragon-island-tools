"""Cut the Icy Blue Dragon sheet into per-animation strips with uniform frame size.

The source sheet has no fixed grid: frame sizes differ per row, and rows 4-6 overlap
(skill vortex, effects). Rows 1-3 are detected from alpha gaps; rows 4-6 use hand-picked
boxes. Every frame of an animation is aligned on the dragon's feet so it does not jitter.

The idle/walk frames were not drawn on a consistent scale (walk frame 0 is ~12% larger) and
the body drifts a few pixels between frames, so those cycles are also registered: each frame
is scaled/shifted so its upper body matches a reference frame. The walk frames are then
re-ordered so the legs change as little as possible between neighbours.

Usage: .venv/bin/python tools/slice_sheet.py   (writes frontend/public/sprites/*.png + manifest.json; icons: tools/slice_hud_icons.py)
"""
import itertools
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path("/Users/mypc/cinemark-workspace/dragon-island")
sys.path.insert(0, str(ROOT))

from lib.image import key_magenta

HAC_LONG = ROOT / "assets" / "dragons" / "hac_long"
SRC = HAC_LONG / "sheet" / "sprite_sheet.png"
WALK_SRC = HAC_LONG / "animations" / "walk_v4.png"
WALK_STRIDE = 56
WALK_ANCHOR = (190, 471)
STAND_FROM = {"fore": 8, "hind": 2, "cut": 190, "feather": 16}
FLY_SRC = HAC_LONG / "animations" / "fly_v1.png"
GRID_CELL = (384, 512)
OUT = ROOT / "frontend" / "public" / "sprites"

ALPHA_SOLID = 100
ALPHA_HAZE = 8
PAD = 6

ROW4 = [(25, 625, 310, 866), (310, 625, 578, 866), (575, 625, 742, 866),
        (745, 625, 1092, 866), (1090, 625, 1368, 866)]
ROW5 = [(20, 862, 255, 1016), (268, 860, 515, 1012), (520, 862, 795, 1010),
        (818, 862, 1092, 1012), (1090, 862, 1292, 1016)]
ROW6 = [(12, 1018, 250, 1142), (250, 1018, 386, 1142), (386, 1018, 532, 1142),
        (535, 1018, 682, 1142), (682, 1004, 832, 1142), (832, 1006, 1062, 1142),
        (1062, 1022, 1252, 1142), (1252, 990, 1366, 1142)]
AUTO_ROWS = [(24, 236), (247, 407), (426, 617)]


def animations(rows):
    r1, r2, r3 = rows
    feet = {"align": True}
    walk_cells = [(c * GRID_CELL[0], r * GRID_CELL[1], (c + 1) * GRID_CELL[0], (r + 1) * GRID_CELL[1])
                  for r in range(2) for c in range(4)]
    return {
        "idle_sheet": (r1, 8, True, {**feet, "register": True}),
        "walk":    (walk_cells, 4, True, {"source": "walk", "match": "idle_sheet", "inbetween": 3,
                                          "stride": WALK_STRIDE, "anchor": WALK_ANCHOR}),
        "idle":    ([(0, 0, *GRID_CELL)], 1, True, {"source": "stand", "anchor": WALK_ANCHOR, "scale_as": "walk"}),
        "fly":     (walk_cells, 9, True, {"source": "fly", "mane_anchor": "walk"}),
        "attack":  (r3, 9, False, feet),
        "skill":   (ROW4[1:], 5, False, {**feet, "mirror": True}),
        "stance":  ([ROW4[0]], 1, False, {**feet, "mirror": True}),
        "stunned": (ROW5[0:2], 3, True, feet),
        "sleep":   (ROW5[2:4], 1.5, True, feet),
        "wake":    ([ROW5[4]], 1, False, feet),
        **{f"fx_{i}": ([b], 1, False, {}) for i, b in enumerate(ROW6)},
    }


def auto_row(alpha, y0, y1):
    w = alpha.width
    px = alpha.load()
    occ = [any(px[x, y] > ALPHA_SOLID for y in range(y0, y1)) for x in range(w)]
    spans, start = [], None
    for x, on in enumerate(occ + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            if x - start > 15:
                spans.append([start, x])
            start = None
    boxes = []
    for i, (a, b) in enumerate(spans):
        left = a - PAD if i == 0 else max(a - PAD, (spans[i - 1][1] + a) // 2)
        right = b + PAD if i == len(spans) - 1 else min(b + PAD, (b + spans[i + 1][0]) // 2)
        boxes.append((max(0, left), max(0, y0 - PAD), min(w, right), min(alpha.height, y1 + PAD)))
    return boxes


def foot_anchor(frame):
    px = frame.load()
    xs, bottom = [], 0
    for y in range(frame.height):
        for x in range(frame.width):
            r, g, b, a = px[x, y]
            if a > 200 and (r + g + b) / 3 < 120:
                xs.append(x)
                bottom = max(bottom, y)
    if not xs:
        return frame.width / 2, frame.height
    return sum(xs) / len(xs), bottom


LEGS = 0.32


def place(img, ax, ay, s, size, at, resample=Image.BICUBIC):
    data = (1 / s, 0, ax - at[0] / s, 0, 1 / s, ay - at[1] / s)
    return img.transform(size, Image.AFFINE, data, resample)


def silhouette(img, ax, ay, s, size, at):
    return np.asarray(place(img.getchannel("A"), ax, ay, s, size, at, Image.NEAREST)) > 128


def iou(a, b):
    union = (a | b).sum()
    return (a & b).sum() / union if union else 0.0


def register(frames):
    h = 0.5
    areas = [(np.asarray(f.getchannel("A")) > 128).sum() for f, _, _ in frames]
    ref_i = int(np.argsort(areas)[len(areas) // 2])
    ref, rax, ray = frames[ref_i]
    size = (int(ref.width * 1.6 * h), int(ref.height * 1.6 * h))
    at = (size[0] / 2, size[1] * 0.85)
    ref_mask = silhouette(ref, rax, ray, h, size, at)
    upper = slice(0, int(at[1] - LEGS * ref.height * h))
    result = []
    for k, (f, ax, ay) in enumerate(frames):
        if k == ref_i:
            result.append((1.0, 0.0, 0.0))
            continue
        best = (-1, 1.0, 0, 0)
        for s in np.arange(0.84, 1.101, 0.01):
            m = silhouette(f, ax, ay, s * h, size, at)
            for dy in range(-8, 9):
                rolled_y = np.roll(m, dy, 0)
                for dx in range(-8, 9):
                    score = iou(np.roll(rolled_y, dx, 1)[upper], ref_mask[upper])
                    if score > best[0]:
                        best = (score, s, dx, dy)
        _, s, dx, dy = best
        result.append((float(s), dx / h, dy / h))
    return result


def leg_order(frames):
    size = (int(max(f.width for f, *_ in frames) * 1.4), int(max(f.height for f, *_ in frames) * 1.2))
    at = (size[0] / 2, size[1] * 0.9)
    ref_h = float(np.median([f.height for f, *_ in frames]))
    leg_slice = slice(int(at[1] - LEGS * ref_h), size[1])
    masks = [silhouette(f, ax, ay, s, size, at)[leg_slice] for f, ax, ay, s in frames]
    n = len(frames)
    dist = [[1 - iou(masks[i], masks[j]) for j in range(n)] for i in range(n)]
    best = min(((0,) + p for p in itertools.permutations(range(1, n))),
               key=lambda order: sum(dist[order[i]][order[(i + 1) % n]] for i in range(n)))
    return list(best)


def mane(img):
    a = np.asarray(img).astype(np.int16)
    m = (a[..., :3].min(axis=2) > 190) & (a[..., 3] > 200)
    cols = np.nonzero((a[..., 3] > 128).any(axis=0))[0]
    m[:, int(cols[0] + 0.45 * (cols[-1] - cols[0])):] = False
    ys, xs = np.nonzero(m)
    return float(xs.mean()), float(ys.mean()), int(m.sum())


def body_height(frames):
    def height(f):
        rows = np.where((np.asarray(f.getchannel("A")) > 128).any(axis=1))[0]
        return rows[-1] - rows[0] + 1
    return float(np.median([height(f) for f, *_ in frames]))


def inbetween(a, b, t=0.5):
    pa, pb = (np.asarray(x.convert("RGBa")).astype(np.float32) for x in (a, b))
    gray = [cv2.cvtColor((p[..., :3] + 128 * (1 - p[..., 3:] / 255)).astype(np.uint8), cv2.COLOR_RGB2GRAY) for p in (pa, pb)]
    args = dict(pyr_scale=0.5, levels=4, winsize=21, iterations=5, poly_n=7, poly_sigma=1.5, flags=0)
    f_ab = cv2.calcOpticalFlowFarneback(gray[0], gray[1], None, **args)
    f_ba = cv2.calcOpticalFlowFarneback(gray[1], gray[0], None, **args)
    h, w = gray[0].shape
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    warp = lambda img, f, k: cv2.remap(img, gx - k * f[..., 0], gy - k * f[..., 1], cv2.INTER_LINEAR, borderValue=0)
    wa, wb = warp(pa, f_ab, t), warp(pb, f_ba, 1 - t)
    near_b = t >= 0.5
    disagree = np.abs(wa[..., 3] - wb[..., 3]) / 255
    agree = 1 - np.clip((disagree - 0.15) / 0.35, 0, 1)
    w_b = cv2.GaussianBlur(t * agree + (1.0 if near_b else 0.0) * (1 - agree), (0, 0), 2)[..., None]
    mid = (1 - w_b) * wa + w_b * wb
    mid[(wb if near_b else wa)[..., 3] < 24] = 0
    return Image.fromarray(mid.clip(0, 255).astype(np.uint8), "RGBa").convert("RGBA")


def stand_pose(walk_src, spec):
    def cell(k):
        x0, y0 = ((k - 1) % 4) * GRID_CELL[0], ((k - 1) // 4) * GRID_CELL[1]
        return np.asarray(walk_src.crop((x0, y0, x0 + GRID_CELL[0], y0 + GRID_CELL[1]))).astype(np.float32)
    w = np.clip((np.arange(GRID_CELL[0]) - (spec["cut"] - spec["feather"] / 2)) / spec["feather"], 0, 1)[None, :, None]
    mixed = cell(spec["fore"]) * (1 - w) + cell(spec["hind"]) * w
    return Image.fromarray(mixed.clip(0, 255).astype(np.uint8), "RGBA")


def drop_haze(img):
    r, g, b, a = img.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: 0 if v <= ALPHA_HAZE else v)))


def steady_torso(frames, leg_frac=LEGS):
    centres = []
    for f, ax, ay, s in frames:
        solid = np.asarray(f.getchannel("A")) > 128
        rows = np.nonzero(solid.any(axis=1))[0]
        cut_at = int(rows[-1] - leg_frac * (rows[-1] - rows[0]))
        ys, xs = np.nonzero(solid[:cut_at])
        centres.append(((xs.mean() - ax) * s, (ys.mean() - ay) * s))
    mx, my = np.mean([c[0] for c in centres]), np.mean([c[1] for c in centres])
    return [(f, ax + (cx - mx) / s, ay + 0.5 * (cy - my) / s, s) for (f, ax, ay, s), (cx, cy) in zip(frames, centres)]


def main():
    sheet = drop_haze(Image.open(SRC).convert("RGBA"))
    OUT.mkdir(parents=True, exist_ok=True)
    a = sheet.getchannel("A")

    rows = [auto_row(a, y0, y1) for y0, y1 in AUTO_ROWS]
    walk_src = key_magenta(Image.open(WALK_SRC))
    sources = {"sheet": sheet, "walk": walk_src, "stand": stand_pose(walk_src, STAND_FROM),
               "fly": key_magenta(Image.open(FLY_SRC))}
    manifest, done = {}, {}

    for name, (boxes, fps, loop, opts) in animations(rows).items():
        frames = []
        for k, box in enumerate(boxes):
            src = sources[opts.get("source", "sheet")]
            cell_origin = box[:2]
            if "source" in opts:
                box = (box[0] + 4, box[1] + 4, box[2] - 4, box[3] - 4)
            crop = src.crop(box)
            bbox = crop.getchannel("A").getbbox() or (0, 0, crop.width, crop.height)
            crop = crop.crop(bbox)
            if opts.get("mirror"):
                crop = crop.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if "anchor" in opts:
                ax = opts["anchor"][0] + cell_origin[0] - box[0] - bbox[0]
                ay = opts["anchor"][1] + cell_origin[1] - box[1] - bbox[1]
            elif opts.get("align"):
                ax, ay = foot_anchor(crop)
            else:
                ax, ay = crop.width / 2, crop.height / 2
            frames.append((crop, ax, ay))

        fit = register(frames) if opts.get("register") else [(1.0, 0.0, 0.0)] * len(frames)
        base = body_height(done[opts["match"]]) / body_height(frames) if "match" in opts else 1.0
        if "scale_as" in opts:
            base = done[opts["scale_as"]][0][3]
        frames = [(f, ax - dx / s, ay - dy / s, s * base) for (f, ax, ay), (s, dx, dy) in zip(frames, fit)]
        if "mane_anchor" in opts:
            rf, rax, ray, rs = done[opts["mane_anchor"]][0]
            rmx, rmy, rcount = mane(rf)
            s = rs * (rcount / float(np.median([mane(f)[2] for f, *_ in frames]))) ** 0.5
            aligned = []
            for f, *_ in frames:
                mx, my, _ = mane(f)
                aligned.append((f, mx + (rax - rmx) * rs / s, my + (ray - rmy) * rs / s, s))
            frames = aligned
        order = leg_order(frames) if opts.get("reorder") else list(range(len(frames)))
        frames = [frames[k] for k in order]
        if opts.get("steady"):
            frames = steady_torso(frames)
        done[name] = frames

        left = max(ax * s for _, ax, _, s in frames)
        right = max((f.width - ax) * s for f, ax, _, s in frames)
        top = max(ay * s for _, _, ay, s in frames)
        down = max((f.height - ay) * s for f, _, ay, s in frames)
        fw, fh = int(left + right + 0.999), int(top + down + 0.999)

        cells_list = [place(f.convert("RGBa"), ax, ay, s, (fw, fh), (left, top)).convert("RGBA") for f, ax, ay, s in frames]
        if opts.get("inbetween"):
            n = opts["inbetween"]
            cells_list = [c for k, a in enumerate(cells_list)
                     for c in [a] + [inbetween(a, cells_list[(k + 1) % len(cells_list)], i / (n + 1)) for i in range(1, n + 1)]]
            fps *= n + 1
        strip = Image.new("RGBA", (fw * len(cells_list), fh))
        for i, cell in enumerate(cells_list):
            strip.alpha_composite(cell, (i * fw, 0))
        strip.save(OUT / f"{name}.png", optimize=True)

        manifest[name] = {
            "file": f"{name}.png", "frameWidth": fw, "frameHeight": fh,
            "frames": len(cells_list), "fps": fps, "loop": loop,
            "originX": round(left / fw, 4), "originY": round(top / fh, 4),
            "source": [list(boxes[k]) for k in order],
            **({"stride": round(opts["stride"] * frames[0][3], 1)} if "stride" in opts else {}),
            **({"fit": [[round(s, 3), round(dx, 1), round(dy, 1)] for s, dx, dy in (fit[k] for k in order)]}
               if opts.get("register") else {}),
        }
        print(f"{name:10s} {len(cells_list)} frames  {fw}x{fh}  order={order}"
              + (f"  scale={[round(fit[k][0], 2) for k in order]}" if opts.get("register") else "")
              + (f"  match={base:.3f}" if "match" in opts else ""))

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"sprites  {len(manifest)} animations -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
