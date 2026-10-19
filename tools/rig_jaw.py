"""Give a built rig a working mouth from a redrawn head sheet (parts/jaw.png, on magenta):

  3 pieces side by side: the UPPER HEAD (lower jaw removed), the LOWER JAW (closed) and the MOUTH
  interior (throat + tongue, drawn open ~35 deg), each with the hinge at its back (right) end.

Works on the exported pieces (rig px), after build_rig's export:
  1. the upper head is fitted onto the exported head by its face (the top of the silhouette: the
     neck of the old head may be longer than the redrawn one and is kept);
  2. the old closed jaw is what the upper head no longer covers around the mouth: the jaw piece is
     fitted into that gap (its closed position);
  3. head.png becomes the upper head + whatever of the old head it does not cover (the neck), minus
     the old jaw; jaw.png and mouth.png are new bones parented to the head, hinged at the jaw's
     back end. The rig opens the jaw (A.jaw) and swings the mouth with it (DragonRig).
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from lib.image import components, cut, key_distance

FACE = 0.6      # the fit only looks at the top 60% of the old head (face + crest), not the neck
PAD = 60
MOUTH_OPEN = 0.6   # rad the mouth interior is drawn open (DragonRig MOUTH_OPEN)


def key_soft(img):
    """key_distance (the throat and tongue are red-purple: key_magenta read them as background and
    turned them green), despilling only the soft edge so no pink fringe is left."""
    out = np.asarray(key_distance(img, 50, 130)).astype(np.float32)
    a = out[..., 3:] / 255
    spill = np.clip(np.minimum(out[..., 0], out[..., 2]) - out[..., 1], 0, None)[..., None] * (1 - a)
    out[..., [0, 2]] -= spill[..., [0, 0]]
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")


def pieces(sheet_path):
    """(upper head, jaw, mouth) as RGBA images, from the largest 3 parts of the sheet."""
    sheet = key_soft(Image.open(sheet_path))
    parts = sorted(components(sheet, min_area=800), key=lambda c: -c[0][2] * c[0][3])[:3]
    head = parts[0]
    jaw, mouth = sorted(parts[1:], key=lambda c: c[0][0])   # left to right
    return [cut(sheet, bbox, mask, pad=0)[0] for bbox, mask in (head, jaw, mouth)]


# per species, in px of the sheet's pieces (each cropped to its own box): (front tip, hinge).
# head: under the tip of the upper jaw/beak, and the corner of the mouth; jaw: its front tip and the
# centre of its hinge; mouth: the front tip of its top edge (the roof) and its back corner
POINTS = {
    "hac_long": dict(head=((44, 469), (272, 413)), jaw=((5, 97), (288, 25)), mouth=((13, 50), (303, 15))),
    "than_long": dict(head=((25, 612), (362, 532)), jaw=((4, 195), (361, 42)), mouth=((56, 18), (396, 48))),
    "phuong_hoang_lua": dict(head=((60, 430), (250, 395)), jaw=((3, 85), (293, 20)), mouth=((48, 45), (353, 68))),
    "phuong_hoang_bang": dict(head=((60, 428), (250, 390)), jaw=((6, 85), (293, 30)), mouth=((38, 52), (378, 75))),
}


def fit_two(img, p_tip, p_hinge, q_tip, q_hinge):
    """Scale + turn `img` so its points p_tip, p_hinge land on q_tip, q_hinge (canvas px).
    Returns (image, integer top-left, hinge in canvas px)."""
    p = np.subtract(p_hinge, p_tip); q = np.subtract(q_hinge, q_tip)
    s = np.hypot(*q) / np.hypot(*p)
    ang = np.arctan2(q[1], q[0]) - np.arctan2(p[1], p[0])
    img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)
    hx, hy = p_hinge[0] * s, p_hinge[1] * s
    R = int(np.hypot(img.width, img.height)) + 2
    big = Image.new("RGBA", (2 * R, 2 * R))
    ox, oy = round(R - hx), round(R - hy)
    big.alpha_composite(img, (ox, oy))
    big = big.rotate(-np.degrees(ang), center=(ox + hx, oy + hy), resample=Image.BICUBIC)
    bbox = big.getchannel("A").getbbox()
    big = big.crop(bbox)
    hinge_in = (ox + hx - bbox[0], oy + hy - bbox[1])
    tl = (round(q_hinge[0] - hinge_in[0]), round(q_hinge[1] - hinge_in[1]))
    return big, tl, (tl[0] + hinge_in[0], tl[1] + hinge_in[1])


def clip_wedge(img, tl, q_tip, q_hinge, reach=0.92):
    """Keep only the inside of the open mouth: the wedge between the roof (hinge -> tip) and the
    floor opened MOUTH_OPEN rad, a little shorter than the jaw. The tongue that hung out of the
    front is cut away (not wanted)."""
    hx, hy = q_hinge[0] - tl[0], q_hinge[1] - tl[1]
    vx, vy = (q_tip[0] - q_hinge[0]) * reach, (q_tip[1] - q_hinge[1]) * reach
    c, s_ = np.cos(-MOUTH_OPEN), np.sin(-MOUTH_OPEN)
    fx, fy = vx * c - vy * s_, vx * s_ + vy * c          # roof turned down by the opening (front end goes down)
    pts = [(hx + 6, hy - 4), (hx + vx, hy + vy - 4)]
    pts += [(hx + vx * (1 - t) + fx * t, hy + vy * (1 - t) + fy * t) for t in np.linspace(0, 1, 8)]   # front, rounded
    pts += [(hx + fx, hy + fy + 4), (hx + 6, hy + 4)]
    m = Image.new("L", img.size)
    ImageDraw.Draw(m).polygon([(float(x), float(y)) for x, y in pts], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1))
    out = img.copy()
    out.putalpha(Image.fromarray(np.minimum(np.asarray(img.getchannel("A")), np.asarray(m))))
    return out


def alpha(img):
    return (np.asarray(img.getchannel("A")) > 128).astype(np.float32)


def best_fit(target, weight, tmpl):
    """Offset of `tmpl` (mask) on `target` maximizing IoU over the `weight` region (1 = counts)."""
    t = target * weight
    inter = cv2.matchTemplate(t, tmpl, cv2.TM_CCORR)
    in_region = cv2.matchTemplate(weight, tmpl, cv2.TM_CCORR)
    iou = inter / np.maximum(1, t.sum() + in_region - inter)
    _, score, _, (x, y) = cv2.minMaxLoc(iou)
    return score, x, y


def add_jaw(rig, out, sheet_path, did):
    head_b = next(b for b in rig["bones"] if b["name"] == "head")
    old = Image.open(out / "head.png").convert("RGBA")
    up, jaw, mouth = pieces(sheet_path)

    # canvas: the old head with room around it, in rig px
    W, H = old.width + 2 * PAD, old.height + 2 * PAD
    canvas_old = Image.new("RGBA", (W, H)); canvas_old.alpha_composite(old, (PAD, PAD))
    old_m = alpha(canvas_old)
    ys, _ = np.nonzero(old_m)
    face = np.zeros_like(old_m); face[: int(ys.min() + (ys.max() - ys.min()) * FACE)] = 1

    # 1. upper head onto the face
    best = (-1, 0, 0, 1.0)
    base = old.width / up.width
    for s in np.arange(0.7, 1.4, 0.01):
        k = base * s
        m = alpha(up.resize((max(1, round(up.width * k)), max(1, round(up.height * k)))))
        if m.shape[0] >= H or m.shape[1] >= W:
            continue
        score, x, y = best_fit(old_m, face, m)
        if score > best[0]:
            best = (score, x, y, k)
    score, hx, hy, k = best
    up_r = up.resize((round(up.width * k), round(up.height * k)), Image.LANCZOS)
    up_m = np.zeros_like(old_m); up_m[hy:hy + up_r.height, hx:hx + up_r.width] = alpha(up_r)
    print(f"  jaw: upper head fit {score:.2f} at scale {k:.3f}")

    # 2. jaw and mouth: each mapped by two points (front tip, hinge) onto the upper head (in the
    #    sheet's upper-head px, then by the head's fit into canvas px)
    P = POINTS[did]
    to_canvas = lambda pt: (hx + pt[0] * k, hy + pt[1] * k)
    q_tip, q_hinge = to_canvas(P["head"][0]), to_canvas(P["head"][1])
    jaw_r, (jx, jy), hinge = fit_two(jaw, *P["jaw"], q_tip, q_hinge)
    mouth_r, (mx, my), _ = fit_two(mouth, *P["mouth"], q_tip, q_hinge)
    mouth_r = clip_wedge(mouth_r, (mx, my), q_tip, q_hinge)
    jaw_m = np.zeros_like(old_m)
    a = alpha(jaw_r)
    y0, x0 = max(0, jy), max(0, jx)
    jaw_m[y0:jy + a.shape[0], x0:jx + a.shape[1]] = a[y0 - jy:, x0 - jx:][: H - y0, : W - x0]

    # 3. new head = upper head over the old pieces it leaves (the neck), without the old jaw and
    #    without thin slivers of the old outline
    keep = old_m * (1 - cv2.dilate(up_m, np.ones((3, 3), np.uint8))) * (1 - cv2.dilate(jaw_m, np.ones((9, 9), np.uint8)))
    keep = cv2.morphologyEx(keep, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(keep.astype(np.uint8))
    big = np.isin(lab, [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 0.04 * old_m.sum()])
    arr = np.asarray(canvas_old).copy()
    arr[..., 3] = np.where(big, arr[..., 3], 0)
    new_head = Image.fromarray(arr)
    new_head.alpha_composite(up_r, (hx, hy))

    # canvas px -> rig px: the old head's top-left sits at joint - origin * size
    ox = head_b["joint"][0] - head_b["origin"][0] * old.width - PAD
    oy = head_b["joint"][1] - head_b["origin"][1] * old.height - PAD
    hinge_rig = [round(ox + hinge[0], 2), round(oy + hinge[1], 2)]

    def save(name, img, at):
        bbox = img.getchannel("A").getbbox()
        img = img.crop(bbox); at = (at[0] + bbox[0], at[1] + bbox[1])
        img.save(out / f"{name}.png", optimize=True)
        return [round((hinge[0] - at[0]) / img.width, 4), round((hinge[1] - at[1]) / img.height, 4)], img, at

    # head keeps its joint; only the image (and origin) change
    _, img, at = save("head", new_head, (0, 0))
    head_b["origin"] = [round((head_b["joint"][0] - ox - at[0]) / img.width, 4), round((head_b["joint"][1] - oy - at[1]) / img.height, 4)]
    jaw_origin, *_ = save("jaw", jaw_r, (jx, jy))
    mouth_origin, *_ = save("mouth", mouth_r, (mx, my))

    bones = [b for b in rig["bones"] if b["name"] not in ("jaw", "mouth")]
    i = next(i for i, b in enumerate(bones) if b["name"] == "head")
    bones[i:i] = [{"name": "mouth", "parent": "head", "joint": hinge_rig, "origin": mouth_origin},
                  {"name": "jaw", "parent": "head", "joint": hinge_rig, "origin": jaw_origin}]
    rig["bones"] = bones


if __name__ == "__main__":
    # preview: python tools/rig_jaw.py <id>  -> /tmp/di/jaw_<id>.png (closed + open), no rig changes
    import json, sys, shutil, tempfile
    from pathlib import Path
    from lib.paths import DRAGONS, OUT as OUT_ROOT
    for did in sys.argv[1:]:
        src = Path("/tmp/di/dragons_backup") / did   # the build before the jaw was added
        tmp = Path(tempfile.mkdtemp())
        shutil.copy(src / "head.png", tmp / "head.png")
        rig = json.loads((src / "rig.json").read_text())
        add_jaw(rig, tmp, DRAGONS / did / "parts" / "jaw.png", did)
        B = {b["name"]: b for b in rig["bones"]}
        canvas = Image.new("RGBA", (900, 400), (126, 190, 90, 255))
        for col, ang in enumerate((0, -0.6)):
            cx = 220 + col * 450 - B["head"]["joint"][0]; cy = 300 - B["head"]["joint"][1]
            for name, rot in (("mouth", ang + 0.6), ("jaw", ang), ("head", 0)):
                img = Image.open(tmp / f"{name}.png"); b = B[name]
                px, py = b["origin"][0] * img.width, b["origin"][1] * img.height
                big = Image.new("RGBA", (img.width * 3, img.height * 3)); big.alpha_composite(img, (img.width, img.height))
                big = big.rotate(-np.degrees(rot), center=(img.width + px, img.height + py), resample=Image.BICUBIC)
                if name == "mouth" and ang == 0:
                    continue
                canvas.alpha_composite(big, (round(cx + b["joint"][0] - img.width - px), round(cy + b["joint"][1] - img.height - py)))
        canvas.resize((canvas.width * 2, canvas.height * 2), Image.LANCZOS).save(f"/tmp/di/jaw_{did}.png")
        print("preview", did)
