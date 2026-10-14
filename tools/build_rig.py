"""Cut a dragon's ChatGPT body-part sheets into rig pieces and write public/dragons/<id>/rig.json.

Sources (flat magenta background, every piece a separate island), per dragon in
assets/dragons/<id>/parts/:
  body.png  head(+neck), torso, near/far wing, 3 tail pieces (+ optional jaw)
  legs.png  4 legs (near fore, near hind, far fore, far hind) x 3 pieces each
Layouts live in tools/rig_configs/.

Each piece is cut along its own outline (connected component), placed into a standing "rest pose"
in rig space, and gets a joint (pivot) where it rotates. The game does the forward kinematics,
leg IK, breathing, tail sway and wing flap (public/rig.js).

Rig space: x to the right, y down, origin on the ground under the middle of the body; the dragon
faces left. Exported images are at EXPORT_SCALE of rig space so they stay sharp when the game
draws the rig at half size.

Usage: .venv/bin/python tools/build_rig.py [dragon_id ...] [--debug out_dir]   (default: all dragons)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("/Users/mypc/cinemark-workspace/dragon-island")
sys.path.insert(0, str(ROOT))

from lib.image import key_distance, key_magenta, components, cut, shade
from lib.paths import ROOT
from rig_configs import CONFIGS, LEG_SIDES

SEGMENTS = ("upper", "lower", "paw")

OUT_ROOT = ROOT / "frontend" / "public" / "dragons"
OUT = None   # set per dragon in main()

# Draw order, back to front (bones a species does not have are skipped).
ORDER = ["wing_far", "fore_far_upper", "fore_far_lower", "fore_far_paw", "hind_far_upper",
         "hind_far_lower", "hind_far_paw", "tail_fan", "tail_tip", "tail_mid", "tail_base", "torso",
         "hind_near_upper", "hind_near_lower", "hind_near_paw", "fore_near_upper", "fore_near_lower",
         "fore_near_paw", "jaw", "head", "wing_near"]
BODY_PARENT = {"head": "torso", "wing_near": "torso", "wing_far": "torso", "tail_base": "torso", "tail_fan": "tail_tip",
               "tail_mid": "tail_base", "tail_tip": "tail_mid"}

# Joint caps: a disc cut from the assembled rest pose around a joint, drawn behind the two pieces
# and turned by their mean angle, so bending never opens a gap. (parent piece, child piece, radius
# as a share of the limb width at the joint)
CAPS = [(f"{leg}_{a}", f"{leg}_{b}", r) for leg in LEG_SIDES for a, b, r in (("upper", "lower", 0.6), ("lower", "paw", 0.8))] + \
       [("torso", f"{leg}_upper", 0.6) for leg in LEG_SIDES] + \
       [("torso", "tail_base", 0.5), ("tail_base", "tail_mid", 0.5), ("tail_mid", "tail_tip", 0.5), ("tail_tip", "tail_fan", 0.5), ("torso", "head", 0.4)]

TARGET_HEIGHT = 416   # exported rig height in px (game draws it at 0.5 -> ~208 px like the sprites)


def align_replacement(old, at, path, keep=0.6):
    """Fit a redrawn piece onto the original one: find the scale and offset at which the lower `keep`
    share of both silhouettes (the part that was not redrawn) overlaps best. Returns (img, at)."""
    new = key_magenta(Image.open(path))
    (bbox, mask), = sorted(components(new), key=lambda c: -c[0][2] * c[0][3])[:1]
    new, _ = cut(new, bbox, mask)
    h = 0.5   # search at half resolution
    old_a = np.asarray(old.getchannel("A").resize((round(old.width * h), round(old.height * h)))) > 128
    top = int(old_a.shape[0] * (1 - keep))
    target = old_a[top:]
    ys, xs = np.nonzero(target)
    best = (-1.0, 1.0, 0, 0)
    for s in np.arange(0.6, 1.6, 0.01):
        k = old.height * s / new.height            # new px -> old px, guessed from the heights
        img = new.getchannel("A").resize((max(1, round(new.width * k * h)), max(1, round(new.height * k * h))))
        a = np.asarray(img) > 128
        # align bottoms, then search a small window of shifts
        for dy in range(-12, 13, 2):
            for dx in range(-30, 31, 2):
                canvas = np.zeros_like(old_a)
                y0 = old_a.shape[0] - a.shape[0] + dy
                x0 = dx + (old_a.shape[1] - a.shape[1]) // 2
                sy0, sx0 = max(0, -y0), max(0, -x0)
                cy0, cx0 = max(0, y0), max(0, x0)
                hh = min(a.shape[0] - sy0, canvas.shape[0] - cy0)
                ww = min(a.shape[1] - sx0, canvas.shape[1] - cx0)
                if hh <= 0 or ww <= 0:
                    continue
                canvas[cy0:cy0 + hh, cx0:cx0 + ww] = a[sy0:sy0 + hh, sx0:sx0 + ww]
                part = canvas[top:]
                score = (part & target).sum() / max(1, (part | target).sum())
                if score > best[0]:
                    best = (score, k, x0 / h, y0 / h)
    score, k, x0, y0 = best
    print(f"  replaced piece {path.name}: overlap {score:.2f}, scale {k:.3f}")
    img = new.resize((round(new.width * k), round(new.height * k)), Image.LANCZOS)
    return img, (at[0] + x0, at[1] + y0)


def split_tallest(col, which="tallest"):
    """[(bbox, mask)] of a leg where two pieces touch: cut one (the tallest, or the "last" = lowest) at its
    narrowest row (searched in the middle 30-75% of its height) into two pieces, keeping top-to-bottom order."""
    i = len(col) - 1 if which == "last" else max(range(len(col)), key=lambda k: col[k][0][3])
    (x, y, w, h), mask = col[i]
    rows = (mask[y:y + h, x:x + w] > 0).sum(axis=1)
    lo, hi = int(h * 0.3), int(h * 0.75)
    cut_at = lo + int(np.argmin(rows[lo:hi]))
    top, bot = mask.copy(), mask.copy()
    top[y + cut_at:] = 0
    bot[:y + cut_at] = 0
    def box(m):
        ys, xs = np.nonzero(m)
        return (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
    parts = [(box(top), top), (box(bot), bot)]
    return sorted(col[:i] + parts + col[i + 1:], key=lambda c: c[0][1])


def turn_point(pt, centre, deg):
    a = np.radians(deg)
    dx, dy = pt[0] - centre[0], pt[1] - centre[1]
    return (centre[0] + dx * np.cos(a) - dy * np.sin(a), centre[1] + dx * np.sin(a) + dy * np.cos(a))


def rotate_about(img, at, centre, deg):
    """Turn a piece placed at `at` (layout top-left) about layout point `centre`; returns (img, at)."""
    pad = int(np.hypot(*img.size)) // 2 + 4
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    big.paste(img, (pad, pad))
    c = (centre[0] - at[0] + pad, centre[1] - at[1] + pad)
    big = big.rotate(-deg, center=c, resample=Image.BICUBIC)   # PIL turns counter-clockwise
    box = big.getchannel("A").getbbox()
    return big.crop(box), (at[0] - pad + box[0], at[1] - pad + box[1])


def solid_x(img, y0, y1):
    """Mean x of solid pixels in rows y0..y1 of a piece."""
    a = np.asarray(img)[..., 3][max(0, int(y0)):int(y1)] > 128
    xs = np.nonzero(a)[1]
    return float(xs.mean()) if len(xs) else img.width / 2


def build(cfg):
    key = key_distance if cfg.get("key") == "distance" else key_magenta
    body_img = key(Image.open(cfg["body_src"]))
    legs_img = key(Image.open(cfg["legs_src"]))
    if "legs_crop" in cfg:   # the legs sheet also holds other pieces: keep only the leg area
        x0, y0, x1, y1 = cfg["legs_crop"]
        clean = Image.new("RGBA", legs_img.size)
        clean.paste(legs_img.crop((x0, y0, x1, y1)), (x0, y0))
        legs_img = clean
    GROUND, LEG_SCALE, LEG_PULL = cfg["ground"], cfg["leg_scale"], cfg["leg_pull"]
    parents = {**BODY_PARENT, **cfg.get("parents", {})}
    pieces = {}   # name -> dict(img, at (layout top-left), scale (layout px per image px), joint, parent)

    body_parts = components(body_img)
    for name, spec in cfg["body"].items():
        if name in cfg.get("skip", ()):
            continue
        sx, sy = spec["src"]
        bbox, mask = min(body_parts, key=lambda c: (c[0][0] + c[0][2] / 2 - sx) ** 2 + (c[0][1] + c[0][3] / 2 - sy) ** 2)
        shift = (0, 0)
        if "keep" in spec or "drop" in spec:   # carve one drawn piece into several bones (sheet rects)
            full = bbox
            mask = mask.copy()
            if "keep" in spec:
                inside = np.zeros_like(mask)
                for x0, y0, x1, y1 in spec["keep"]:
                    inside[y0:y1, x0:x1] = 1
                mask *= inside
            for x0, y0, x1, y1 in spec.get("drop", ()):
                mask[y0:y1, x0:x1] = 0
            ys, xs = np.nonzero(mask)
            bbox = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
            shift = (bbox[0] - full[0], bbox[1] - full[1])   # `at` is given for the whole drawn piece
        img, (ox, oy) = cut(body_img, bbox, mask)
        if "fade" in spec:   # sheet x range over which the piece fades out (its cut end melts into the next)
            a = np.asarray(img).astype(np.float32)
            x0, x1 = spec["fade"]
            xs = bbox[0] - ox + np.arange(a.shape[1])
            a[..., 3] *= np.clip((x1 - xs) / (x1 - x0), 0, 1)[None, :] if x1 > x0 else np.clip((xs - x1) / (x0 - x1), 0, 1)[None, :]
            img = Image.fromarray(a.astype(np.uint8), "RGBA")
        if name == "wing_far":
            img = shade(img, cfg["wing_far_shade"])
        at = (spec["at"][0] + shift[0] - ox, spec["at"][1] + shift[1] - oy)
        if name in cfg.get("replace", {}):
            img, at = align_replacement(img, at, cfg["replace"][name])
        joint = cfg["joints"][name]
        if spec.get("rot"):   # rest-pose turn about the joint (degrees, + = clockwise on screen)
            img, at = rotate_about(img, at, joint, spec["rot"])
        pieces[name] = dict(img=img, at=at, scale=1.0, joint=joint, parent=parents.get(name))
    for name, spec in cfg.get("place", {}).items():
        img = key_magenta(Image.open(spec["src"]))
        (bbox, mask), = sorted(components(img), key=lambda c: -c[0][2] * c[0][3])[:1]
        img, (ox, oy) = cut(img, bbox, mask)
        k = spec["height"] * pieces[spec["height_of"]]["img"].height / img.height
        rx, ry = (spec["root"][0] - bbox[0] + ox) * k, (spec["root"][1] - bbox[1] + oy) * k
        img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        if name == "wing_far":
            img = shade(img, cfg["wing_far_shade"])
        joint = cfg["joints"][name]
        at = (joint[0] - rx, joint[1] - ry)
        if spec.get("rot"):   # rest-pose turn about the root (degrees, + = clockwise on screen)
            img, at = rotate_about(img, at, joint, spec["rot"])
        pieces[name] = dict(img=img, at=at, scale=1.0, joint=joint, parent=parents.get(name))
    # a child bone that hangs off a turned piece turns with it
    for name, spec in cfg["body"].items():
        if name not in pieces:
            continue
        par = parents.get(name)
        prot = par and cfg["body"].get(par, {}).get("rot")
        if prot and not spec.get("rot"):
            p, pj = pieces[name], pieces[par]["joint"]
            p["img"], p["at"] = rotate_about(p["img"], p["at"], pj, prot)
            p["joint"] = turn_point(p["joint"], pj, prot)

    # scale: shrink/grow a body piece (and the pieces hanging off it, e.g. the jaw) about its joint
    for name, spec in cfg["body"].items():
        if name not in pieces or not spec.get("scale"):
            continue
        k, (jx, jy) = spec["scale"], pieces[name]["joint"]
        family = [name] + [n for n in pieces if parents.get(n) == name]
        for n in family:
            p = pieces[n]
            p["img"] = p["img"].resize((round(p["img"].width * k), round(p["img"].height * k)), Image.LANCZOS)
            p["at"] = (jx + (p["at"][0] - jx) * k, jy + (p["at"][1] - jy) * k)
            if n != name:
                p["joint"] = (jx + (p["joint"][0] - jx) * k, jy + (p["joint"][1] - jy) * k)

    leg_parts = components(legs_img)
    col_w = legs_img.width / 4
    for leg, spec in cfg["legs"].items():
        col = sorted([c for c in leg_parts if int((c[0][0] + c[0][2] / 2) // col_w) == spec["col"]], key=lambda c: c[0][1])
        if len(col) == 2:   # two pieces drawn touching: split the taller one at its narrowest row
            col = split_tallest(col, cfg.get("leg_split", "tallest"))
        assert len(col) == 3, f"{leg}: expected 3 pieces, got {len(col)}"
        left = min(c[0][0] for c in col)
        cuts = [cut(legs_img, b, m) for b, m in col]
        names = [f"{leg}_{seg}" for seg in SEGMENTS]
        # keep the pieces where ChatGPT drew them relative to each other, minus the pull-apart gap;
        # bounding boxes are no good for stacking (the hind shin has a long blade hanging down)
        src_top = col[0][0][1]
        # leg_pull: one gap for both joints, or (knee, ankle)
        pulls = LEG_PULL if isinstance(LEG_PULL, (tuple, list)) else (LEG_PULL, LEG_PULL)
        shift = [0, pulls[0], pulls[0] + pulls[1]]
        rel = [(b[0] - left, b[1] - src_top - shift[k]) for k, (b, _) in enumerate(col)]
        bottom = max(r[1] + b[3] for r, (b, _) in zip(rel, col))
        top = GROUND - bottom * LEG_SCALE          # paw stands on the ground
        for k, ((bbox, _), (img, (ox, oy)), (rx, ry)) in enumerate(zip(col, cuts, rel)):
            if LEG_SIDES[leg]:
                img = shade(img, cfg["far_shade"])
            x, y = spec["x"] + rx * LEG_SCALE, top + ry * LEG_SCALE
            pieces[names[k]] = dict(img=img, at=(x - ox * LEG_SCALE, y - oy * LEG_SCALE), scale=LEG_SCALE,
                                    parent=names[k - 1] if k else spec.get("parent", "torso"), bbox=bbox, box_at=(x, y))
        up, lo, paw = (pieces[n] for n in names)

        def solid_centre(p, row):
            """Layout point on the solid middle of piece p at `row` source px below its bbox top."""
            s = p["scale"]
            oy = (p["box_at"][1] - p["at"][1]) / s
            cx = solid_x(p["img"], oy + row - 6, oy + row + 6)
            return (p["at"][0] + cx * s, p["box_at"][1] + row * s)
        up["joint"] = solid_centre(up, 0.30 * up["bbox"][3])     # hip / shoulder, tucked under the torso
        lo["joint"] = solid_centre(lo, 14)                       # knee / elbow: top of the lower piece
        paw["joint"] = solid_centre(paw, 14)                     # ankle / wrist: top of the paw
        paw["toe"] = (paw["box_at"][0], GROUND)     # front of the paw on the ground (for the IK target)
    return pieces


def compose(rig, names, pad=40):
    """The named pieces in their rest pose on one canvas; returns (image, rig x/y of its top-left)."""
    bones = {b["name"]: b for b in rig["bones"]}
    placed = []
    for n in names:
        b = bones[n]
        img = Image.open(OUT / f"{n}.png")
        placed.append((img, b["joint"][0] - b["origin"][0] * img.width, b["joint"][1] - b["origin"][1] * img.height))
    x0 = min(x for _, x, _ in placed) - pad
    y0 = min(y for _, _, y in placed) - pad
    x1 = max(x + i.width for i, x, _ in placed) + pad
    y1 = max(y + i.height for i, _, y in placed) + pad
    canvas = Image.new("RGBA", (int(x1 - x0) + 1, int(y1 - y0) + 1))
    for img, x, y in placed:
        canvas.alpha_composite(img, (round(x - x0), round(y - y0)))
    return canvas, (x0, y0)


def add_caps(rig):
    """Write cap_<child>.png for every CAPS joint and insert it into the draw order just behind the
    first of its two pieces."""
    bones = rig["bones"]
    order = [b["name"] for b in bones]
    names = set(order)
    for parent, child, share in CAPS:
        if parent not in names or child not in names:   # e.g. two-legged species
            continue
        canvas, (x0, y0) = compose(rig, [parent, child])
        jx, jy = next(b["joint"] for b in bones if b["name"] == child)
        cx, cy = jx - x0, jy - y0
        alpha = np.asarray(canvas)[..., 3] > 128
        # limb width at the joint: solid run through the joint, across the limb
        row = alpha[int(cy)]
        xs = np.nonzero(row)[0]
        run = xs[np.abs(xs - cx) < 60]
        col = alpha[:, int(cx)]
        ys = np.nonzero(col)[0]
        run_v = ys[np.abs(ys - cy) < 60]
        width = min(np.ptp(run) if len(run) else 20, np.ptp(run_v) if len(run_v) else 20)
        r = max(6, share * width)
        size = int(2 * r) + 4
        disc = Image.new("L", canvas.size)
        ImageDraw.Draw(disc).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        disc = disc.filter(ImageFilter.GaussianBlur(1.2))
        cap = Image.new("RGBA", canvas.size)
        cap.paste(canvas, (0, 0), Image.fromarray(np.minimum(np.asarray(disc), np.asarray(canvas)[..., 3]).astype(np.uint8)))
        cap = cap.crop((int(cx - size / 2), int(cy - size / 2), int(cx - size / 2) + size, int(cy - size / 2) + size))
        name = f"cap_{child}"
        cap.save(OUT / f"{name}.png", optimize=True)
        entry = {"name": name, "parent": None, "joint": [jx, jy], "origin": [0.5, 0.5], "cap": [parent, child]}
        at = min(order.index(parent), order.index(child))
        bones.insert(at, entry)
        order.insert(at, name)


def split_crest(rig, spec):
    """Cut the top of head.png into crest.png (drawn behind the head, parented to it). The crest keeps
    a 12 px overlap below the cut, which the head covers, so bending it never opens a gap."""
    head = next(b for b in rig["bones"] if b["name"] == "head")
    img = Image.open(OUT / "head.png").convert("RGBA")
    w, h = img.size
    cut_at = int(spec["cut"] * h)
    rows = np.arange(h)[:, None]
    arr = np.asarray(img).astype(np.float32)
    crest, rest = arr.copy(), arr.copy()
    crest[..., 3] *= np.clip((cut_at + 12 - rows) / 6, 0, 1)        # crest: everything above cut (+overlap)
    rest[..., 3] *= np.clip((rows - cut_at + 3) / 6, 0, 1)          # head: everything below the cut
    if spec.get("drop"):
        # no crest bone: the head simply ends at the cut, with a soft edge
        rest[..., 3] = arr[..., 3] * np.clip((rows - cut_at + 6) / 10, 0, 1)
        Image.fromarray(rest.astype(np.uint8), "RGBA").save(OUT / "head.png", optimize=True)
        (OUT / "crest.png").unlink(missing_ok=True)
        return
    Image.fromarray(rest.astype(np.uint8), "RGBA").save(OUT / "head.png", optimize=True)
    crest_img = Image.fromarray(crest.astype(np.uint8), "RGBA")
    crest_img.save(OUT / "crest.png", optimize=True)
    # rig position of the crest pivot: head image top-left + pivot share
    x0 = head["joint"][0] - head["origin"][0] * w
    y0 = head["joint"][1] - head["origin"][1] * h
    px, py = spec["pivot"]
    entry = {"name": "crest", "parent": "head", "joint": [round(x0 + px * w, 2), round(y0 + py * h, 2)],
             "origin": [px, py]}
    rig["bones"].insert(rig["bones"].index(head), entry)   # behind the head


def portrait(rig):
    """The assembled rest pose as one image (dragon info panel)."""
    img, _ = compose(rig, [b["name"] for b in rig["bones"]], pad=6)
    img.crop(img.getchannel("A").getbbox()).save(OUT / "portrait.png", optimize=True)


def export(cfg, pieces, debug=None):
    GROUND = cfg["ground"]
    # rig space: origin on the ground under the torso joint, scaled to TARGET_HEIGHT
    top = min(p["at"][1] for p in pieces.values())
    k = TARGET_HEIGHT / (GROUND - top)
    ox = pieces["torso"]["joint"][0]
    order = [n for n in ORDER if n in pieces]
    to_rig = lambda x, y: (round((x - ox) * k, 2), round((y - GROUND) * k, 2))

    OUT.mkdir(parents=True, exist_ok=True)
    rig = {"name": cfg["name"], "height": TARGET_HEIGHT, "motion": cfg.get("motion", {}), "bones": []}
    for name in order:
        p = pieces[name]
        s = p["scale"] * k                           # image px -> rig px
        img = p["img"].resize((max(1, round(p["img"].width * s)), max(1, round(p["img"].height * s))), Image.LANCZOS)
        img.save(OUT / f"{name}.png", optimize=True)
        jx, jy = p["joint"]
        rig["bones"].append({
            "name": name, "parent": p["parent"], "joint": to_rig(jx, jy),
            # pivot inside the exported image, as a 0..1 origin
            "origin": [round((jx - p["at"][0]) * k / img.width, 4), round((jy - p["at"][1]) * k / img.height, 4)],
            **({"toe": to_rig(*p["toe"])} if "toe" in p else {}),
        })
    if "crest" in cfg:
        split_crest(rig, cfg["crest"])
    add_caps(rig)
    (OUT / "rig.json").write_text(json.dumps(rig, indent=1))
    portrait(rig)
    print(f"wrote {len(order)} pieces + rig.json to {OUT.relative_to(ROOT)}  (scale {k:.3f})")

    if debug:
        W = int((max(p["at"][0] + p["img"].width * p["scale"] for p in pieces.values()) - min(p["at"][0] for p in pieces.values())) * k) + 80
        canvas = Image.new("RGBA", (W, TARGET_HEIGHT + 40), (126, 190, 90, 255))
        d = ImageDraw.Draw(canvas)
        cx, cy = 40 + (ox - min(p["at"][0] for p in pieces.values())) * k, 20 + TARGET_HEIGHT
        for b in rig["bones"]:
            img = Image.open(OUT / f"{b['name']}.png")
            jx, jy = cx + b["joint"][0], cy + b["joint"][1]
            canvas.alpha_composite(img, (round(jx - b["origin"][0] * img.width), round(jy - b["origin"][1] * img.height)))
        d = ImageDraw.Draw(canvas)
        for b in rig["bones"]:
            jx, jy = cx + b["joint"][0], cy + b["joint"][1]
            d.ellipse([jx - 3, jy - 3, jx + 3, jy + 3], fill=(255, 0, 0))
            if b.get("parent"):
                pj = next(x for x in rig["bones"] if x["name"] == b["parent"])["joint"]
                d.line([(cx + pj[0], cy + pj[1]), (jx, jy)], fill=(255, 255, 0), width=1)
        d.line([(0, cy), (W, cy)], fill=(255, 0, 0))
        canvas.save(debug)


if __name__ == "__main__":
    args = sys.argv[1:]
    dbg = None
    if "--debug" in args:
        i = args.index("--debug"); dbg = Path(args[i + 1]); del args[i:i + 2]
    for dragon_id in args or list(CONFIGS):
        OUT = OUT_ROOT / dragon_id
        export(CONFIGS[dragon_id], build(CONFIGS[dragon_id]), dbg / f"{dragon_id}.png" if dbg else None)
