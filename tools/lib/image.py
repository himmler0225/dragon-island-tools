"""Shared image processing helpers (OpenCV + Pillow)."""
from __future__ import annotations

import numpy as np
from PIL import Image


def key_magenta(img: Image.Image) -> Image.Image:
    """Flat #FF00FF background -> transparency. 'Magenta-ness' = min(R, B) - G is ~250 on the
    background and grid lines and <= 0 on the dragon; edges get partial alpha and are despilled
    (the pink fringe is pulled back to grey) so they blend into any background."""
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    m = np.minimum(r, b) - g
    alpha = 1 - np.clip((m - 30) / 80, 0, 1)
    spill = np.clip(m, 0, None)
    out = np.dstack([r - spill, g, b - spill, alpha * 255]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def key_distance(img: Image.Image, near: int = 40, far: int = 110) -> Image.Image:
    """Background removal by colour distance to pure magenta. Gentler than key_magenta: purples and
    violets (which key_magenta reads as background) stay opaque."""
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    d = np.max(np.abs(arr - np.array([255, 0, 255], np.float32)), axis=2)
    alpha = np.clip((d - near) / (far - near), 0, 1)
    return Image.fromarray(np.dstack([arr, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def components(img: Image.Image, min_area: int = 3000):
    """[(bbox, mask)] for every opaque island bigger than `min_area` px.

    bbox: (x, y, w, h) in image pixels
    mask: uint8 (0/1) same size as the cropped bbox
    """
    import cv2
    alpha = np.asarray(img)[..., 3]
    solid = cv2.morphologyEx((alpha > 60).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(solid)
    out = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if area < min_area:
            continue
        # keep the soft edge: grow the island mask a little and take the real alpha inside it
        mask = cv2.dilate((labels == i).astype(np.uint8), np.ones((7, 7), np.uint8))
        out.append(((x, y, w, h), mask))
    return out


def cut(img: Image.Image, bbox: tuple[int, int, int, int], mask: np.ndarray, pad: int = 4):
    """Cut a piece from `img` using its bounding box and mask, with `pad` px of padding.

    Returns (piece, offset): the cropped piece image and the offset of the bbox top-left
    inside the returned image.
    """
    x, y, w, h = bbox
    x0, y0 = max(0, x - pad), max(0, y - pad)
    x1, y1 = min(img.width, x + w + pad), min(img.height, y + h + pad)
    arr = np.asarray(img)[y0:y1, x0:x1].copy()
    arr[..., 3] = (arr[..., 3] * mask[y0:y1, x0:x1]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA"), (x - x0, y - y0)   # piece, offset of bbox inside it


def shade(img: Image.Image, k: float) -> Image.Image:
    """Brighten/darken an image by factor `k`."""
    from PIL import ImageEnhance
    return ImageEnhance.Brightness(img).enhance(k)
