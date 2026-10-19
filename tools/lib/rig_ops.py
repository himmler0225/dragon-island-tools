"""Image-processing helpers for the dragon rig builder: rotation, feather, alignment, splitting."""
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter


def turn_point(pt, centre, deg):
    """Rotate layout point `pt` around `centre` by `deg` degrees."""
    a = np.radians(deg)
    dx, dy = pt[0] - centre[0], pt[1] - centre[1]
    return (centre[0] + dx * np.cos(a) - dy * np.sin(a), centre[1] + dx * np.sin(a) + dy * np.cos(a))


def rotate_about(img, at, centre, deg):
    """Turn a piece placed at `at` (layout top-left) about layout point `centre`; returns (img, at)."""
    pad = int(np.hypot(*img.size)) // 2 + 4
    big = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad))
    big.paste(img, (pad, pad))
    c = (centre[0] - at[0] + pad, centre[1] - at[1] + pad)
    big = big.rotate(-deg, center=c, resample=Image.BICUBIC)   # PIL counter-clockwise
    box = big.getchannel("A").getbbox()
    return big.crop(box), (at[0] - pad + box[0], at[1] - pad + box[1])


def solid_x(img, y0, y1):
    """Mean x of solid pixels in rows y0..y1 of a piece."""
    a = np.asarray(img)[..., 3][max(0, int(y0)):int(y1)] > 128
    xs = np.nonzero(a)[1]
    return float(xs.mean()) if len(xs) else img.width / 2


def split_tallest(col, which="tallest"):
    """Split one leg piece at its narrowest row (middle 30-75% of height) into two pieces."""
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


def feather(img, at, x, y=-1e9, px=14):
    """Soften the outline where a piece lies over the next one.

    Within `px` of the edge, and only right of layout x `x` / below layout y `y`,
    the alpha ramps to 0 so the dark outline melts into the piece below.
    """
    a = np.asarray(img).astype(np.float32)
    solid = (a[..., 3] > 128).astype(np.uint8)
    dist = cv2.distanceTransform(solid, cv2.DIST_L2, 5)
    ramp = np.clip(dist / px, 0, 1)
    xs = at[0] + np.arange(a.shape[1])[None, :]
    ys = at[1] + np.arange(a.shape[0])[:, None]
    w = np.clip((xs - x) / 30, 0, 1) * np.clip((ys - y) / 30, 0, 1)
    a[..., 3] *= 1 - w * (1 - ramp)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def align_replacement(old, at, path, keep=0.6):
    """Fit a redrawn piece onto the original: find scale and offset for best silhouette overlap.

    Returns (img, at) where the lower `keep` share of both silhouettes overlap best.
    """
    from lib.image import components, cut, key_magenta
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
        k = old.height * s / new.height
        img = new.getchannel("A").resize((
            max(1, round(new.width * k * h)), max(1, round(new.height * k * h))))
        a = np.asarray(img) > 128
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
