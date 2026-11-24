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
       .venv/bin/python tools/build_rig.py [dragon_id ...] --portrait   (only redraw portrait.png)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from lib.image import key_distance, key_magenta, components, cut, shade
from lib.paths import ROOT
from lib.rig_ops import align_replacement, feather, rotate_about, split_tallest, solid_x, turn_point, rotate_about as _ra2, turn_point as _tp2
from rig_configs import CONFIGS, LEG_SIDES
from rig_jaw import POINTS as JAW_POINTS, add_jaw
from lib.paths import DRAGONS, OUT as OUT_ROOT

SEGMENTS = ("upper", "lower", "paw")

OUT = None   # set per dragon in main()

# Draw order, back to front (bones a species does not have are skipped).
# fan_1..15: a peacock's tail feathers (back layer first), behind everything; they fan open
FANS = [f"fan_{k}" for k in range(1, 16)]
ORDER = [*FANS, "wing_far", "fore_far_upper", "fore_far_lower", "fore_far_paw", "hind_far_upper",
         "hind_far_lower", "hind_far_paw", "tail_fan", "tail_tip", "tail_mid", "tail_base", "cannon_far", "cannon_near", "torso",
         "hind_near_upper", "hind_near_lower", "hind_near_paw", "fore_near_upper", "fore_near_lower",
         "fore_near_paw", "jaw", "head", "head_attack", "wing_near", "orb"]   # head_attack: a strike version of the head, over it
BODY_PARENT = {**{f: "torso" for f in FANS}, "head": "torso", "wing_near": "torso", "wing_far": "torso", "tail_base": "torso", "tail_fan": "tail_tip",
               "tail_mid": "tail_base", "tail_tip": "tail_mid", "orb": "tail_tip",
               "cannon_far": "torso", "cannon_near": "torso"}   # cannons: hidden in the shell, they rise on a strike (Rồng Rùa)   # orb: a charm floating over the tail tip (Nguyệt Long's moon)

# Joint caps: a disc cut from the assembled rest pose around a joint, drawn behind the two pieces
# and turned by their mean angle, so bending never opens a gap. (parent piece, child piece, radius
# as a share of the limb width at the joint)
CAPS = [(f"{leg}_{a}", f"{leg}_{b}", r) for leg in LEG_SIDES for a, b, r in (("upper", "lower", 1.0), ("lower", "paw", 1.0))] + \
       [("torso", f"{leg}_upper", 0.6) for leg in LEG_SIDES] + \
       [("torso", "tail_base", 0.5), ("tail_base", "tail_mid", 0.5), ("tail_mid", "tail_tip", 0.5), ("tail_tip", "tail_fan", 0.5), ("torso", "head", 0.4)]

# a leg piece's dark outline at a cut end, source px: at least [0], or [1] x the piece height (joint_fade)
JOINT_RIM = (6, 0.03)
TARGET_HEIGHT = 416   # rig height of the debug canvas only
# every dragon is scaled so its body (all pieces except wings, caps and crest) covers the same area,
# sqrt(area) = TARGET_BODY rig px: scaling by total height made winged/antlered dragons small and the
# long wingless ones big. cfg["size"] scales one species on purpose (e.g. a boss).
TARGET_BODY = 290



def build(cfg):
    key = key_distance if cfg.get("key") == "distance" else key_magenta
    if cfg.get("key") == "tight":   # pink art: only near-exact magenta is background
        key = lambda im: key_distance(im, 14, 45)
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
    sheets = {}   # other sheets pieces are carved from (spec["sheet"]): path -> (keyed image, islands)
    unders = []   # (target piece, image, layout top-left): pixels moved from one piece to behind another
    for name, spec in cfg["body"].items():
        if name in cfg.get("skip", ()):
            continue
        if "src_img" in spec:   # piece drawn on its own image (a redrawn part): largest island, resized
            # same keying as the sheets (cfg["key"]); rgba: the image is already cut out (soft glows kept)
            own = Image.open(spec["src_img"]).convert("RGBA") if spec.get("rgba") else key(Image.open(spec["src_img"]))
            parts_own = components(own)
            if "src" in spec:   # several pieces on that image: the one nearest src
                sx, sy = spec["src"]
                bbox, mask = min(parts_own, key=lambda c: (c[0][0] + c[0][2] / 2 - sx) ** 2 + (c[0][1] + c[0][3] / 2 - sy) ** 2)
            elif spec.get("whole"):   # every island on the image is the piece (a glow ring round a core)
                mask = np.max([m for _, m in parts_own], axis=0)
                ys, xs = np.nonzero(mask)
                bbox = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
            else:
                (bbox, mask), = sorted(parts_own, key=lambda c: -c[0][2] * c[0][3])[:1]
            img, (ox, oy) = cut(own, bbox, mask)
            k = spec.get("img_scale", 1.0)
            img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
            at = (spec["at"][0] - ox * k, spec["at"][1] - oy * k)
            if name == "wing_far":
                img = shade(img, cfg["wing_far_shade"])
            if spec.get("rot"):
                img, at = rotate_about(img, at, cfg["joints"][name], spec["rot"])
            if "feather" in spec:
                img = feather(img, at, **spec["feather"])
            if name in cfg.get("replace", {}):   # this image only places the piece: a redrawn one is fitted over it
                img, at = align_replacement(img, at, cfg["replace"][name])
            pieces[name] = dict(img=img, at=at, scale=1.0, joint=cfg["joints"][name], parent=parents.get(name))
            continue
        sheet_img, sheet_parts = body_img, body_parts
        if "sheet" in spec:   # carved from another sheet (a redrawn piece): keep / fade / drop in its px
            if spec["sheet"] not in sheets:
                own = key(Image.open(spec["sheet"]))
                sheets[spec["sheet"]] = (own, components(own))
            sheet_img, sheet_parts = sheets[spec["sheet"]]
        sx, sy = spec["src"]
        bbox, mask = min(sheet_parts, key=lambda c: (c[0][0] + c[0][2] / 2 - sx) ** 2 + (c[0][1] + c[0][3] / 2 - sy) ** 2)
        shift = (0, 0)
        if any(k in spec for k in ("keep", "drop", "drop_poly", "keep_poly")):   # carve one drawn piece into several bones (sheet rects)
            full = bbox
            mask = mask.copy()
            orig = mask.copy()
            if "keep" in spec:
                inside = np.zeros_like(mask)
                for x0, y0, x1, y1 in spec["keep"]:
                    inside[y0:y1, x0:x1] = 1
                mask *= inside
            for x0, y0, x1, y1 in spec.get("drop", ()):
                mask[y0:y1, x0:x1] = 0
            if "keep_poly" in spec:   # polygons in sheet px: keep only what is inside them
                inside = np.zeros(mask.shape, np.uint8)
                for poly in spec["keep_poly"]:
                    cv2.fillPoly(inside, [np.array(poly, np.int32)], 1)
                mask = mask * inside
            for poly in spec.get("drop_poly", ()):   # polygon in sheet px (e.g. a drawn-in lower jaw)
                hole = np.zeros(mask.shape, np.uint8)
                cv2.fillPoly(hole, [np.array(poly, np.int32)], 1)
                mask[hole > 0] = 0
            ys, xs = np.nonzero(mask)
            bbox = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
            shift = (bbox[0] - full[0], bbox[1] - full[1])   # `at` is given for the whole drawn piece
        src_im = sheet_img
        if "paint" in spec:   # [(polygon, rgb)]: recolour the light pixels inside (e.g. paint teeth over), outlines stay
            rgba = np.asarray(sheet_img).copy()
            for poly, rgb in spec["paint"]:
                area = np.zeros(rgba.shape[:2], np.uint8)
                cv2.fillPoly(area, [np.array(poly, np.int32)], 1)
                light = rgba[..., :3].astype(int).sum(axis=2) > 480
                rgba[(area > 0) & light, :3] = rgb
            src_im = Image.fromarray(rgba, "RGBA")
        if "fill_poly" in spec:   # holes left by carved-out pieces: inpaint them so the body continues underneath
            rgba = np.asarray(sheet_img).copy()
            hole = np.zeros(mask.shape, np.uint8)
            for poly in spec["fill_poly"]:
                cv2.fillPoly(hole, [np.array(poly, np.int32)], 1)
            known = (mask > 0) & (hole == 0)
            fill = ((hole > 0) & ~known).astype(np.uint8)
            rgb = rgba[..., :3].copy()
            # inpaint the hole plus a band around it, from the known body pixels only
            band = cv2.dilate(fill, np.ones((31, 31), np.uint8)).astype(bool) & ~known
            rgb[band] = 0
            rgb = cv2.inpaint(rgb, band.astype(np.uint8), 9, cv2.INPAINT_TELEA)
            rgba[..., :3] = np.where(known[..., None], rgba[..., :3], rgb)
            rgba[..., 3] = np.where(fill > 0, 255, rgba[..., 3])
            src_im = Image.fromarray(rgba, "RGBA")
            mask = np.maximum(mask, fill)
            ys, xs = np.nonzero(mask)
            bbox = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
            shift = (bbox[0] - full[0], bbox[1] - full[1])
        img, (ox, oy) = cut(src_im, bbox, mask)
        if "fade" in spec:   # sheet x range over which the piece fades out (its cut end melts into the next)
            a = np.asarray(img).astype(np.float32)
            x0, x1 = spec["fade"]
            xs = bbox[0] - ox + np.arange(a.shape[1])
            a[..., 3] *= np.clip((x1 - xs) / (x1 - x0), 0, 1)[None, :] if x1 > x0 else np.clip((xs - x1) / (x0 - x1), 0, 1)[None, :]
            img = Image.fromarray(a.astype(np.uint8), "RGBA")
        k = spec.get("img_scale", 1.0)   # sheet px -> layout px (the sheet drew it at another size)
        if k != 1.0:
            img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
        if name == "wing_far":
            img = shade(img, cfg["wing_far_shade"])
        at = (spec["at"][0] + (shift[0] - ox) * k, spec["at"][1] + (shift[1] - oy) * k)
        if name in cfg.get("replace", {}):
            img, at = align_replacement(img, at, cfg["replace"][name])
        joint = cfg["joints"][name]
        if spec.get("rot"):   # rest-pose turn about the joint (degrees, + = clockwise on screen)
            img, at = rotate_about(img, at, joint, spec["rot"])
        if "fade_y" in spec:   # layout y range over which the piece fades out downward (a neck melting into the chest)
            a = np.asarray(img).astype(np.float32)
            y0, y1 = spec["fade_y"]
            ys = at[1] + np.arange(a.shape[0])
            a[..., 3] *= np.clip((y1 - ys) / (y1 - y0), 0, 1)[:, None]
            img = Image.fromarray(a.astype(np.uint8), "RGBA")
        if "feather" in spec:
            img = feather(img, at, **spec["feather"])
        pieces[name] = dict(img=img, at=at, scale=1.0, joint=joint, parent=parents.get(name))
        if "under" in spec:   # (target, polygon in sheet px): that part of this piece goes behind target
            target, poly = spec["under"]   # (e.g. a mouth interior, which the head drawn over the jaw would hide it with)
            inside = np.zeros(orig.shape, np.uint8)
            cv2.fillPoly(inside, [np.array(poly, np.int32)], 1)
            m2 = orig * inside
            ys, xs = np.nonzero(m2)
            b2 = (int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))
            img2, (ox2, oy2) = cut(src_im, b2, m2)
            if k != 1.0:
                img2 = img2.resize((round(img2.width * k), round(img2.height * k)), Image.LANCZOS)
            unders.append((target, img2, (spec["at"][0] + (b2[0] - full[0] - ox2) * k, spec["at"][1] + (b2[1] - full[1] - oy2) * k)))
    for target, img2, at2 in unders:
        p = pieces[target]
        x0, y0 = min(p["at"][0], at2[0]), min(p["at"][1], at2[1])
        x1 = max(p["at"][0] + p["img"].width, at2[0] + img2.width)
        y1 = max(p["at"][1] + p["img"].height, at2[1] + img2.height)
        canvas = Image.new("RGBA", (int(np.ceil(x1 - x0)) + 1, int(np.ceil(y1 - y0)) + 1))
        canvas.alpha_composite(img2, (round(at2[0] - x0), round(at2[1] - y0)))
        canvas.alpha_composite(p["img"], (round(p["at"][0] - x0), round(p["at"][1] - y0)))
        p["img"], p["at"] = canvas, (x0, y0)
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
    # a bone that hangs off a turned piece (or off its children, e.g. a tail chain) turns with it
    for name, spec in cfg["body"].items():
        if name not in pieces:
            continue
        par = parents.get(name)
        while par and par in cfg["body"] and not cfg["body"][par].get("rot"):
            par = parents.get(par)
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
    ref_img = ref_parts = None
    for leg, spec in cfg["legs"].items():
        src_img = legs_img
        if "poly" in spec:
            # leg carved straight out of the reference drawing (polygon, reference px = layout px):
            # cut into 3 at its narrowest rows and left exactly where it is drawn
            if ref_img is None:
                ref_img = key(Image.open(cfg["leg_ref"]))
                ref_parts = components(ref_img)
            src_img = ref_img
            (bb, m), = sorted(ref_parts, key=lambda c: -c[0][2] * c[0][3])[:1]
            inside = np.zeros(m.shape, np.uint8)
            cv2.fillPoly(inside, [np.array(spec["poly"], np.int32)], 1)
            m = m * inside
            ys, xs = np.nonzero(m)
            col = [((int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)), m)]
        elif "pick" in spec:
            # one whole leg drawn as a single piece anywhere on the legs sheet: the island nearest `pick`
            px, py = spec["pick"]
            (bb, m) = min(leg_parts, key=lambda c: (c[0][0] + c[0][2] / 2 - px) ** 2 + (c[0][1] + c[0][3] / 2 - py) ** 2)
            col = [(bb, m)]
        else:
            col = sorted([c for c in leg_parts if int((c[0][0] + c[0][2] / 2) // col_w) == spec["col"]], key=lambda c: c[0][1])
        if cfg.get("rigid_legs") and len(col) == 1:
            # one solid leg (chibi): it swings from the hip as a whole; the lower/paw bones are
            # 2-px stubs at the bottom of the foot so the leg bookkeeping still has 3 bones
            (bx, by, bw, bh), m = col[0]
            stubs = []
            for k in range(2):
                sm = np.zeros_like(m)
                yy = by + bh - 4 + 2 * k
                sm[yy:yy + 2, bx + bw // 2:bx + bw // 2 + 2] = 1
                stubs.append(((bx + bw // 2, yy, 2, 2), sm))
            col = col + stubs
        while 0 < len(col) < 3:   # pieces drawn touching: split the tallest at its narrowest row
            col = split_tallest(col, cfg.get("leg_split", "tallest"), spec.get("split_band", (0.3, 0.75)),
                                cfg.get("split_overlap", 0))
        assert len(col) == 3, f"{leg}: expected 3 pieces, got {len(col)}"
        left = min(c[0][0] for c in col)
        cuts = [cut(src_img, b, m) for b, m in col]
        names = [f"{leg}_{seg}" for seg in SEGMENTS]
        # keep the pieces where ChatGPT drew them relative to each other, minus the pull-apart gap;
        # bounding boxes are no good for stacking (the hind shin has a long blade hanging down)
        src_top = col[0][0][1]
        # leg_pull: one gap for both joints, or (knee, ankle)
        pulls = LEG_PULL if isinstance(LEG_PULL, (tuple, list)) else (LEG_PULL, LEG_PULL)
        shift = [0, pulls[0], pulls[0] + pulls[1]]
        rel = [(b[0] - left, b[1] - src_top - shift[k]) for k, (b, _) in enumerate(col)]
        bottom = max(r[1] + b[3] for r, (b, _) in zip(rel, col))
        # per-limb options: scale (x leg_scale, e.g. short arms) and top (layout y of the limb's top:
        # the limb hangs from there instead of standing on the ground - arms of a biped)
        ls = LEG_SCALE * spec.get("scale", 1.0)
        top = spec["top"] if "top" in spec else GROUND - bottom * ls   # paw stands on the ground
        if "poly" in spec or "pick" in spec:   # whole/carved legs: feet on the ground, scale/dx/x per leg
            ls = spec.get("scale", 1.0)
            rel = [(b[0] - left, b[1] - src_top) for b, _ in col]
            bottom = max(r[1] + b[3] for r, (b, _) in zip(rel, col))
            width = max(r[0] + b[2] for r, (b, _) in zip(rel, col))
            top = spec["top"] if "top" in spec else GROUND - bottom * ls   # (an arm hangs from `top`)
            spec = {**spec, "x": spec["x"] if "x" in spec else left + spec.get("dx", 0) + (1 - ls) * width / 2}
        for k, ((bbox, _), (img, (ox, oy)), (rx, ry)) in enumerate(zip(col, cuts, rel)):
            if LEG_SIDES[leg]:
                img = shade(img, cfg["far_shade"])
            jf = cfg.get("joint_fade", 0.22)
            if jf and not cfg.get("rigid_legs"):
                # the cut ends lose their dark outline, so no line shows across a joint: a shin / paw's top
                # (over the piece above) is clear through the outline, then fades in; a thigh / shin's bottom
                # (under the piece below, but wider than it) drops its outline rim. Never more than the two
                # pieces overlap (source px, as stacked): what turns clear must lie over the solid piece above,
                # or the joint opens a gap
                a = np.asarray(img).astype(np.float32)
                rows = np.arange(a.shape[0]) - oy
                def over(j):
                    # overlap of piece j over j - 1: down from j's top to the bottom of j - 1's SOLID part under
                    # j's middle (not its bounding box: a shin's hanging blade or tuft is no cover)
                    (pi, (pox, poy)), (ci, (cox, coy)) = cuts[j - 1], cuts[j]
                    pa, ca = np.asarray(pi)[..., 3] > 128, np.asarray(ci)[..., 3] > 128
                    cx = np.nonzero(ca.any(axis=0))[0]
                    mid = cx[len(cx) // 4: 3 * len(cx) // 4 + 1] - cox + rel[j][0] - rel[j - 1][0] + pox
                    mid = mid[(mid >= 0) & (mid < pa.shape[1])]
                    ends = [np.nonzero(pa[:, x])[0].max() - poy for x in mid if pa[:, x].any()]
                    if not ends:
                        return 0.0
                    return rel[j - 1][1] + float(np.percentile(ends, 25)) - rel[j][1]
                def clear(j):   # (rim, band) of piece j's top
                    ov, h = over(j), col[j][0][3]
                    r = min(max(JOINT_RIM[0], JOINT_RIM[1] * h), 0.3 * ov)
                    return max(0.0, r), max(0.0, min(max(4.0, jf * h), 0.7 * ov - r))
                if cfg.get("legs_down"):
                    # drawn thigh over shin over paw: the upper piece's bottom end (over the next one) is clear
                    # through its outline, then fades in going up, so it melts into the piece under it - no line
                    # across the joint; the lower piece keeps its whole outline (its top is under the one above)
                    if k < len(col) - 1 and over(k + 1) > 0:
                        r, band = clear(k + 1)
                        if band > 0:
                            a[..., 3] *= np.clip((bbox[3] - rows - r) / band, 0, 1)[:, None] ** 0.7
                    # and the lower piece's top outline (its rim, under the piece above) goes too: where a bent joint
                    # shows a sliver of it past the upper piece, no dark line - only its colour
                    if k and over(k) > 0 and cfg.get("legs_down_rim", False):
                        rim = min(max(JOINT_RIM[0], JOINT_RIM[1] * bbox[3]), 0.4 * over(k))
                        a[..., 3] *= np.clip((rows - rim) / max(1.0, rim), 0, 1)[:, None]
                    img = Image.fromarray(a.astype(np.uint8), "RGBA")
                    a = None
                if a is not None and k and over(k) > 0:
                    r, band = clear(k)
                    if band > 0:
                        a[..., 3] *= np.clip((rows - r) / band, 0, 1)[:, None] ** 0.7
                if a is not None and k < len(col) - 1 and over(k + 1) > 0:
                    r2, b2 = clear(k + 1)
                    rim = min(max(JOINT_RIM[0], JOINT_RIM[1] * bbox[3]), over(k + 1) - r2 - b2)
                    if rim > 1:
                        a[..., 3] *= np.clip((bbox[3] - rows - rim) / rim, 0, 1)[:, None]
                if a is not None:
                    img = Image.fromarray(a.astype(np.uint8), "RGBA")
            if k == 0 and spec.get("fade_top"):
                # whole limb: its cut top (a pale oval) melts into the body instead of showing a hard line
                a = np.asarray(img).astype(np.float32)
                band = max(4.0, spec["fade_top"] * bbox[3])
                rows = np.arange(a.shape[0]) - oy
                a[..., 3] *= np.clip(rows / band, 0, 1)[:, None] ** 0.8
                img = Image.fromarray(a.astype(np.uint8), "RGBA")
            x, y = spec["x"] + rx * ls, top + ry * ls
            # nudge {segment: (dx, dy)}: move one piece of this leg (layout px), e.g. a paw drawn off its shin
            ndx, ndy = spec.get("nudge", {}).get(SEGMENTS[k], (0, 0))
            x, y = x + ndx, y + ndy
            # thicker legs: stretch each piece sideways about its middle (leg_widen; a leg's widen {segment: k} on top)
            fw = cfg.get("leg_widen", 1.0) * spec.get("widen", {}).get(SEGMENTS[k], 1.0)
            if fw != 1.0:
                img = img.resize((round(img.width * fw), img.height), Image.LANCZOS)
                x -= (fw - 1) * bbox[2] * ls / 2
                ox *= fw
            pieces[names[k]] = dict(img=img, at=(x - ox * ls, y - oy * ls), scale=ls,
                                    parent=names[k - 1] if k else spec.get("parent", "torso"), bbox=bbox, box_at=(x, y))
        up, lo, paw = (pieces[n] for n in names)

        def solid_centre(p, row):
            """Layout point on the solid middle of piece p at `row` source px below its bbox top."""
            s = p["scale"]
            oy = (p["box_at"][1] - p["at"][1]) / s
            cx = solid_x(p["img"], oy + row - 6, oy + row + 6)
            return (p["at"][0] + cx * s, p["box_at"][1] + row * s)
        up["joint"] = solid_centre(up, 0.30 * up["bbox"][3])     # hip / shoulder, tucked under the torso
        if cfg.get("rigid_legs") and ("poly" in spec or "pick" in spec):
            up["joint"] = solid_centre(up, 0.15 * up["bbox"][3])   # hip near the top of the solid leg
            lo["joint"] = (lo["box_at"][0], lo["box_at"][1] - 6)
            paw["joint"] = (paw["box_at"][0], paw["box_at"][1])
        else:
            lo["joint"] = solid_centre(lo, 14)                       # knee / elbow: top of the lower piece
            paw["joint"] = solid_centre(paw, 14)                     # ankle / wrist: top of the paw
        paw["toe"] = (paw["box_at"][0], GROUND)     # front of the paw on the ground (for the IK target)
        if cfg.get("ball_joints"):
            # legs drawn with round joint balls (a bird's): the knee / ankle turns about the centre of the
            # child piece's ball. ball_pairs (the phoenixes): each piece ends in a ball at the bottom AND starts
            # with one at the top - the lower piece (and the ones under it) moves so its top
            # ball lands exactly on the bottom ball of the piece above (one round joint), it turns about that
            # centre, and the whole leg goes back down onto the ground
            def ball(piece, top):
                # the ball capping the piece's end, ball_pairs = its radius in image px: its centre is that far
                # in from the end, in line with the middle of the cap's first rows (the piece widens right behind
                # the ball, so a thickness search would land in the feathers)
                a = np.asarray(piece["img"])[..., 3] > 128
                rows = np.nonzero(a.any(axis=1))[0]
                end, sign = (rows[0], 1) if top else (rows[-1], -1)
                r = cfg["ball_pairs"]
                xs = np.nonzero(a[end + sign * round(r * 0.4)])[0]
                s = piece["scale"]
                return (piece["at"][0] + xs.mean() * s, piece["at"][1] + (end + sign * r) * s)
            if not cfg.get("ball_pairs"):   # one ball per joint, on top of the lower piece: turn about it
                for q in (lo, paw):
                    a = (np.asarray(q["img"])[..., 3] > 128).astype(np.uint8)
                    d = cv2.distanceTransform(a, cv2.DIST_L2, 5)
                    sq = q["scale"]
                    jx, jy = (q["joint"][0] - q["at"][0]) / sq, (q["joint"][1] - q["at"][1]) / sq
                    yy, xx = np.mgrid[:d.shape[0], :d.shape[1]]
                    d[(xx - jx) ** 2 + (yy - jy) ** 2 > (cfg["ball_joints"] / sq) ** 2] = 0
                    by, bx = np.unravel_index(d.argmax(), d.shape)
                    q["joint"] = (q["at"][0] + bx * sq, q["at"][1] + by * sq)
            drop = 0.0
            for par, ch, rest in ((up, lo, (lo, paw)), (lo, paw, (paw,))) if cfg.get("ball_pairs") else ():
                pb, cb = ball(par, top=False), ball(ch, top=True)
                dx, dy = pb[0] - cb[0], pb[1] - cb[1]
                for q in rest:
                    _shift(q, dx, dy)
                ch["joint"] = pb
                drop -= dy
            for q in (up, lo, paw):
                _shift(q, 0, drop)
    if "crouch" in cfg:
        crouch(pieces, cfg)
    if cfg.get("joint_heal"):
        heal_joints(pieces, cfg)
    # wing_fit {wing: (dx, dy, deg, scale[, flip])}: matched onto ref.png by tools/fit_wings.py - the wing
    # is mirrored about its root (flip: a far wing seen fanning the other way), scaled and turned about
    # its root, then moved (root and all) by (dx, dy) layout px
    for name, (dx, dy, deg, sc, *flip) in cfg.get("wing_fit", {}).items():
        w = pieces[name]
        j = w["joint"]
        if flip and flip[0]:
            w["img"] = w["img"].transpose(Image.FLIP_LEFT_RIGHT)
            w["at"] = (2 * j[0] - w["at"][0] - w["img"].width * w["scale"], w["at"][1])
        w["at"] = (j[0] + (w["at"][0] - j[0]) * sc, j[1] + (w["at"][1] - j[1]) * sc)
        w["scale"] *= sc
        if deg:
            _turn(w, j, deg)
        _shift(w, dx, dy)
    return pieces


def heal_joints(pieces, cfg):
    """joint_heal = px: at each knee and ankle (in the pose as built) the dark outline of the upper piece where it lies
    over the lower one, and of the lower piece where the upper one covers it (a bent joint shows a sliver of it), is
    painted over with the colour beside it (inpainted): the leg reads as one piece, no line across a joint. px: how far
    past the overlap it reaches. The shapes stay; only dark outline pixels change colour."""
    grow = int(cfg["joint_heal"])
    k_dark = cfg.get("joint_heal_dark", 0.78)

    def heal(piece, where):
        a = np.asarray(piece["img"]).copy()
        rgb = np.ascontiguousarray(a[..., :3])
        lum = rgb.astype(np.float32) @ np.array([0.3, 0.59, 0.11], np.float32)
        solid = a[..., 3] > 60
        if not solid.any():
            return
        line = (where & (lum < k_dark * float(np.median(lum[solid]))) & (a[..., 3] > 0)).astype(np.uint8)
        if line.any():
            # the see-through pixels round them are filled too (their colour is black: it would bleed back into the
            # outline), so the colour comes only from the skin inside; the alpha stays as it was
            fill = line | (where & (a[..., 3] < 255)).astype(np.uint8)
            healed = cv2.inpaint(rgb, fill, 5, cv2.INPAINT_TELEA)
            a[..., :3] = np.where(fill[..., None] > 0, healed, rgb)
            piece["img"] = Image.fromarray(a, "RGBA")

    def cover(over, under):
        """`over`'s solid pixels, in `under`'s image px."""
        k = over["scale"] / under["scale"]
        m = over["img"].getchannel("A").resize((max(1, round(over["img"].width * k)), max(1, round(over["img"].height * k))))
        canvas = Image.new("L", under["img"].size)
        canvas.paste(m, (round((over["at"][0] - under["at"][0]) / under["scale"]), round((over["at"][1] - under["at"][1]) / under["scale"])))
        return np.asarray(canvas) > 128

    near = np.ones((2 * grow + 1, 2 * grow + 1), np.uint8)
    legs = [n.removesuffix("_upper") for n in pieces if n.endswith("_upper")]
    for leg in legs:
        for top, low in (("upper", "lower"), ("lower", "paw")):
            p, c = pieces.get(f"{leg}_{top}"), pieces.get(f"{leg}_{low}")
            if not p or not c:
                continue
            under_p = cv2.dilate(cover(c, p).astype(np.uint8), near) > 0     # where the lower piece lies under the upper
            over_c = cv2.dilate(cover(p, c).astype(np.uint8), near) > 0      # where the upper piece covers the lower
            heal(p, under_p)
            heal(c, over_c)


def _turn(piece, centre, deg):
    """rotate_about for a piece whose image is at `scale` layout px per image px."""
    s = piece["scale"]
    img, at = piece["img"], piece["at"]
    pad = int(np.hypot(*img.size)) // 2 + 4
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    big.paste(img, (pad, pad))
    c = ((centre[0] - at[0]) / s + pad, (centre[1] - at[1]) / s + pad)
    big = big.rotate(-deg, center=c, resample=Image.BICUBIC)   # PIL turns counter-clockwise
    box = big.getchannel("A").getbbox()
    piece["img"] = big.crop(box)
    piece["at"] = (at[0] + (box[0] - pad) * s, at[1] + (box[1] - pad) * s)


def _shift(piece, dx, dy):
    piece["at"] = (piece["at"][0] + dx, piece["at"][1] + dy)
    for key in ("joint", "box_at", "toe"):
        if key in piece:
            piece[key] = (piece[key][0] + dx, piece[key][1] + dy)


def crouch(pieces, cfg):
    """Rest pose with bent legs (cfg["crouch"]): the whole body sinks `drop` layout px while every paw
    stays on the ground (pushed `reach` px: fore paws forward, hind paws back); each leg's thigh and
    shin turn to meet it (two-bone IK; the knee bends the way the game bends it: a front leg's elbow
    points back, a hind leg's knee forward, unless motion.hindKnee is "back"). `raise` sets a leg kind's
    hip higher up the body (its paw still on the ground). Baked into the
    images, so the dragon also stands like this where the game does not solve the legs (on its cloud)."""
    spec = cfg["crouch"]
    drop, reach, lift = spec["drop"], spec.get("reach", {}), spec.get("raise", {})
    legs = [n.removesuffix("_upper") for n in pieces if n.endswith("_upper")]
    for name, p in pieces.items():
        if not any(name.startswith(leg) for leg in legs):
            _shift(p, 0, drop)   # body, head, jaw: down
    d = lambda a, b: np.arctan2(b[1] - a[1], b[0] - a[0])
    for leg in legs:
        up, lo, paw = (pieces[f"{leg}_{seg}"] for seg in SEGMENTS)
        _shift(up, 0, drop - lift.get(leg.split("_")[0], 0))   # the hip goes down with the body
        S, K, P = (np.array(x["joint"], float) for x in (up, lo, paw))
        K = K + (0, drop - lift.get(leg.split("_")[0], 0))   # the knee if the leg just moved with the hip
        dx = reach.get(leg.split("_")[0], 0) * (-1 if leg.startswith("fore") else 1)
        T = P + (dx, 0)                        # paw: stays on the ground
        l1 = np.linalg.norm(K - S)                                     # thigh
        l2 = np.linalg.norm(np.array(paw["joint"]) - np.array(lo["joint"]))   # shin
        v = T - S
        dist = min(np.linalg.norm(v), l1 + l2 - 0.5)
        base = np.arctan2(v[1], v[0])
        off = np.arccos(np.clip((l1 ** 2 + dist ** 2 - l2 ** 2) / (2 * l1 * dist), -1, 1))
        back = leg.startswith("fore") or cfg.get("motion", {}).get("hindKnee") == "back"
        K2 = max((S + l1 * np.array([np.cos(a), np.sin(a)]) for a in (base + off, base - off)),
                 key=lambda k: k[0] if back else -k[0])
        T = S + v / np.linalg.norm(v) * dist
        a_up = np.degrees(d(S, K2) - d(S, K))
        a_lo = np.degrees(d(K2, T) - d(np.array(lo["joint"]), np.array(paw["joint"])))
        _turn(up, tuple(S), a_up)
        _shift(lo, *(K2 - np.array(lo["joint"])))
        _turn(lo, tuple(K2), a_lo)
        lo["joint"] = tuple(K2)
        _shift(paw, *(T - np.array(paw["joint"])))
        paw["joint"] = tuple(T)
        paw["toe"] = (paw["toe"][0], cfg["ground"])


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


def add_caps(rig, skip=()):
    """Write cap_<child>.png for every CAPS joint and insert it into the draw order just behind the
    first of its two pieces."""
    bones = rig["bones"]
    order = [b["name"] for b in bones]
    names = set(order)
    for parent, child, share in CAPS:
        if parent not in names or child not in names or child in skip:   # e.g. two-legged species
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


def add_wing_glow(rig, spec, names=("wing_near", "wing_far")):
    """wing_near_glow / wing_far_glow (cfg["wing_glow"]): a golden light along the rim of each wing, drawn just
    over it with additive blending; pose.ts moves it with the wing and lights it on the wing beat. spec: True, or
    {"color": (r, g, b), "width": k} (another colour; k x as thick)."""
    spec = spec if isinstance(spec, dict) else {}
    width = spec.get("width", 1.0)
    PAD = round(34 * width)
    bones = rig["bones"]
    for name in names:
        b = next((x for x in bones if x["name"] == name), None)
        if not b:
            continue
        img = Image.open(OUT / f"{name}.png").convert("RGBA")
        a = np.zeros((img.height + 2 * PAD, img.width + 2 * PAD), np.uint8)
        a[PAD:PAD + img.height, PAD:PAD + img.width] = (np.asarray(img)[..., 3] > 128) * 255
        inside = cv2.distanceTransform(a, cv2.DIST_L2, 5)
        rim = np.clip(1.2 - inside / (12 * width), 0, 1) * (a > 0)               # a band inside the outline
        halo = cv2.GaussianBlur((a > 0).astype(np.float32), (0, 0), 14 * width) * (a == 0)   # a soft glow outside it
        alpha = np.clip(rim + 2.2 * halo, 0, 1)
        out = np.zeros((*a.shape, 4), np.uint8)
        out[..., :3] = spec.get("color", (255, 190, 50))
        out[..., 3] = (alpha * 255).astype(np.uint8)
        glow = f"{name}_glow"
        Image.fromarray(out, "RGBA").save(OUT / f"{glow}.png", optimize=True)
        entry = {"name": glow, "parent": None, "joint": b["joint"],
                 "origin": [round((b["origin"][0] * img.width + PAD) / a.shape[1], 4), round((b["origin"][1] * img.height + PAD) / a.shape[0], 4)]}
        bones.insert(bones.index(b) + 1, entry)


def add_body_aura(rig, spec):
    """<bone>_aura for every piece (cfg["body_aura"], 2026-11-20): a soft halo just OUTSIDE each piece's outline, in
    one colour; the game draws all of them behind the whole dragon with additive blending (so the halos only show
    round the silhouette, never over the art), each following its piece, and lets them breathe slowly.
    spec: {"color": (r, g, b), "width": k (x as wide)}."""
    width = spec.get("width", 1.0)
    PAD = round(40 * width)
    bones = rig["bones"]
    for b in list(bones):
        name = b["name"]
        if name.startswith("cap_") or name.endswith(("_glow", "_aura")):
            continue
        img = Image.open(OUT / f"{name}.png").convert("RGBA")
        a = np.zeros((img.height + 2 * PAD, img.width + 2 * PAD), np.uint8)
        a[PAD:PAD + img.height, PAD:PAD + img.width] = (np.asarray(img)[..., 3] > 128) * 255
        halo = cv2.GaussianBlur((a > 0).astype(np.float32), (0, 0), 13 * width) * (a == 0)
        alpha = np.clip(2.4 * halo, 0, 1)
        out = np.zeros((*a.shape, 4), np.uint8)
        out[..., :3] = spec.get("color", (255, 200, 80))
        out[..., 3] = (alpha * 255).astype(np.uint8)
        Image.fromarray(out, "RGBA").save(OUT / f"{name}_aura.png", optimize=True)
        bones.append({"name": f"{name}_aura", "parent": None, "joint": b["joint"],
                      "origin": [round((b["origin"][0] * img.width + PAD) / a.shape[1], 4),
                                 round((b["origin"][1] * img.height + PAD) / a.shape[0], 4)]})


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


def far_leg_poses(rig):
    """{bone: (rotation rad, new joint)} for the far legs in the game's idle stance (pose.ts): the paw
    is pushed by `stance` / `armPose` and the leg follows with the same two-bone IK as ik.ts, so the
    far leg no longer hides exactly behind the near one."""
    bones = {b["name"]: b for b in rig["bones"]}
    motion = rig.get("motion", {})
    stance = motion.get("stance", [48, 40])
    poses = {}
    for i, kind in enumerate(("fore", "hind")):
        leg = f"{kind}_far"
        if not all(f"{leg}_{seg}" in bones for seg in SEGMENTS):
            continue
        if kind == "fore" and motion.get("foreArms"):   # arms hang at armPose instead of standing
            dx, dy = motion.get("armPose", [[0, 0], [0, 0]])[1]
        else:
            dx, dy = stance[i], 0
        if not (dx or dy):
            continue
        S, K, P = (np.array(bones[f"{leg}_{seg}"]["joint"], float) for seg in SEGMENTS)
        l1, l2 = np.linalg.norm(K - S), np.linalg.norm(P - K)
        v = P + (dx, dy) - S
        d = min(np.linalg.norm(v), l1 + l2 - 0.01)   # out of reach: stretch towards it
        v = v / np.linalg.norm(v) * d
        base = np.arctan2(v[1], v[0])
        off = np.arccos(np.clip((l1 ** 2 + d * d - l2 ** 2) / (2 * l1 * d), -1, 1))
        # bend the knee the way the art draws it: the solution nearest the rest knee
        K2 = min((S + l1 * np.array([np.cos(a), np.sin(a)]) for a in (base + off, base - off)),
                 key=lambda k: np.linalg.norm(k - K))
        T = S + v
        dir_ = lambda a, b: np.arctan2(b[1] - a[1], b[0] - a[0])
        r1, r2 = dir_(S, K2) - dir_(S, K), dir_(K2, T) - dir_(K, P)
        poses[f"{leg}_upper"] = (r1, S)
        poses[f"{leg}_lower"] = (r2, K2)
        poses[f"{leg}_paw"] = (0.0, T)   # the paw stays level, as in the idle pose
    # joint caps sit on the child joint, turned halfway between their two pieces (pose.ts)
    for b in rig["bones"]:
        if "cap" in b and any(n in poses for n in b["cap"]):
            (ra, _), (rb, pos) = (poses.get(n, (0.0, np.array(bones[n]["joint"], float))) for n in b["cap"])
            poses[b["name"]] = ((ra + rb) / 2, pos)
    return poses


def portrait(rig):
    """The assembled idle pose as one image (dragon info panel)."""
    # (the mouth interior is drawn open: it only shows when the jaw opens)
    names = [b["name"] for b in rig["bones"] if b["name"] != "mouth" and not b["name"].endswith("_glow") and not b["name"].startswith("cannon")]   # (cannons: hidden at rest)
    bones = {b["name"]: b for b in rig["bones"]}
    poses = far_leg_poses(rig)
    placed = []
    for n in names:
        img = Image.open(OUT / f"{n}.png").convert("RGBA")
        b = bones[n]
        placed.append((n, img, b["joint"][0] - b["origin"][0] * img.width, b["joint"][1] - b["origin"][1] * img.height))
    # generous margin: a posed leg can swing past the rest-pose bounds (cropped away below)
    pad = 6 + (150 if poses else 0)
    x0 = min(x for _, _, x, _ in placed) - pad
    y0 = min(y for _, _, _, y in placed) - pad
    x1 = max(x + i.width for _, i, x, _ in placed) + pad
    y1 = max(y + i.height for _, i, _, y in placed) + pad
    size = (int(x1 - x0) + 1, int(y1 - y0) + 1)
    canvas = Image.new("RGBA", size)
    # wings where they rest on the ground (motion.wingRest, as pose.ts sets them): moved, turned, scaled about
    # the root (a canvas wide enough for a wing moved past the rest-pose bounds)
    rest = rig.get("motion", {}).get("wingRest", {})
    if rest:
        grow = int(max(abs(v) for r in rest.values() for v in r[:2]) * 2 + 200)
        x0, y0 = x0 - grow, y0 - grow
        size = (size[0] + 2 * grow, size[1] + 2 * grow)
        canvas = Image.new("RGBA", size)
    for n, img, x, y in placed:
        if n in rest:
            dx, dy, rot, sc = rest[n]
            jx, jy = bones[n]["joint"]
            w = img.resize((max(1, round(img.width * sc)), max(1, round(img.height * sc))), Image.LANCZOS)
            layer = Image.new("RGBA", size)
            layer.alpha_composite(w, (round(jx - x0 - (jx - x) * sc), round(jy - y0 - (jy - y) * sc)))
            canvas.alpha_composite(layer.rotate(-np.degrees(rot), Image.BICUBIC, center=(jx - x0, jy - y0), translate=(dx, dy)))
            continue
        if n not in poses:
            canvas.alpha_composite(img, (round(x - x0), round(y - y0)))
            continue
        rot, (nx, ny) = poses[n]
        jx, jy = bones[n]["joint"]
        layer = Image.new("RGBA", size)
        layer.alpha_composite(img, (round(x - x0), round(y - y0)))
        # rig rotations turn clockwise on screen (y down); PIL turns counter-clockwise
        canvas.alpha_composite(layer.rotate(-np.degrees(rot), Image.BICUBIC, center=(jx - x0, jy - y0),
                                            translate=(nx - jx, ny - jy)))
    canvas.crop(canvas.getchannel("A").getbbox()).save(OUT / "portrait.png", optimize=True)


def export(cfg, pieces, debug=None):
    GROUND = cfg["ground"]
    # rig space: origin on the ground under the torso joint, scaled to TARGET_HEIGHT
    top = min(p["at"][1] for p in pieces.values())
    body = sum(float((np.asarray(p["img"])[..., 3] > 128).sum()) * p["scale"] ** 2
               for n, p in pieces.items() if not n.startswith(("wing", "crest", "fan", "orb", "cannon")))
    k = TARGET_BODY / body ** 0.5 * cfg.get("size", 1.0)
    ox = pieces["torso"]["joint"][0]
    order = [n for n in ORDER if n in pieces]
    for name in reversed(cfg.get("behind", ())):   # bones drawn behind everything (e.g. a bird's legs under its body)
        if name in order:
            order.remove(name); order.insert(0, name)
    for name in cfg.get("front", ()):   # bones drawn on top of everything else (e.g. a leg over a long neck)
        if name in order:
            order.remove(name); order.append(name)
    if cfg.get("legs_down"):   # each leg drawn thigh over shin over paw: a piece's round end wraps the top of the next
        for leg in cfg.get("legs", {}):
            seg = [f"{leg}_{g}" for g in SEGMENTS]
            at = [order.index(n) for n in seg if n in order]
            for i, n in zip(sorted(at), reversed([n for n in seg if n in order])):
                order[i] = n
    to_rig = lambda x, y: (round((x - ox) * k, 2), round((y - GROUND) * k, 2))

    OUT.mkdir(parents=True, exist_ok=True)
    rig = {"name": cfg["name"], "height": round((GROUND - top) * k), "motion": dict(cfg.get("motion", {})), "bones": []}
    if "wing_rest" in cfg:
        # wing_rest {wing: (dx, dy, deg, scale)}: like wing_fit, but only on the ground - in flight the wing
        # beats from where it is drawn. Exported for pose.ts in rig px and radians.
        rig["motion"]["wingRest"] = {n: [round(dx * k, 2), round(dy * k, 2), round(np.radians(deg), 4), sc]
                                     for n, (dx, dy, deg, sc) in cfg["wing_rest"].items()}
    if "cannon_drop" in cfg:   # how far (layout px) the cannons sink into the shell when not firing
        rig["motion"]["cannonDrop"] = round(cfg["cannon_drop"] * k, 2)
    if "wing_fly" in cfg:   # wing_fly {wing: (dx, dy)}: moves the wing in flight only (layout px -> rig px)
        rig["motion"]["wingFly"] = {n: [round(dx * k, 2), round(dy * k, 2)] for n, (dx, dy) in cfg["wing_fly"].items()}
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
    jaw_sheet = DRAGONS / OUT.name / "parts" / "jaw.png"
    if OUT.name in JAW_POINTS and jaw_sheet.exists():   # a redrawn head with a separate jaw: the mouth opens
        add_jaw(rig, OUT, jaw_sheet, OUT.name)
    rigid = [f"{leg}_{seg}" for leg in cfg.get("legs", {}) for seg in SEGMENTS] if cfg.get("rigid_legs") else []
    if cfg.get("ball_joints"):   # the drawn balls are the joints: no caps over them
        rigid += [f"{leg}_{seg}" for leg in cfg.get("legs", {}) for seg in ("lower", "paw")]
    add_caps(rig, rigid + list(cfg.get("no_caps", ())))   # no_caps: child pieces whose joint gets no cap
    if cfg.get("tail_glow"):   # the same rim light on the tail; pose.ts keeps it softly lit
        add_wing_glow(rig, cfg["tail_glow"], ("tail_base", *FANS))
    if cfg.get("wing_glow"):
        add_wing_glow(rig, cfg["wing_glow"])
        if isinstance(cfg["wing_glow"], dict) and "color" in cfg["wing_glow"]:   # its falling motes too (DragonRig)
            r, g, b = cfg["wing_glow"]["color"]
            rig["motion"]["glowColor"] = (r << 16) | (g << 8) | b
    if cfg.get("body_aura"):   # a halo round the whole body (all pieces), breathing
        add_body_aura(rig, cfg["body_aura"])
    (OUT / "rig.json").write_text(json.dumps(rig, indent=1))
    portrait(rig)
    print(f"wrote {len(order)} pieces + rig.json to {OUT}  (scale {k:.3f})")

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
    only_portrait = "--portrait" in args
    if only_portrait:
        args.remove("--portrait")
    for dragon_id in args or list(CONFIGS):
        OUT = OUT_ROOT / dragon_id
        if only_portrait:   # redraw portrait.png from the exported pieces + rig.json, nothing else
            portrait(json.loads((OUT / "rig.json").read_text()))
            continue
        export(CONFIGS[dragon_id], build(CONFIGS[dragon_id]), dbg / f"{dragon_id}.png" if dbg else None)
