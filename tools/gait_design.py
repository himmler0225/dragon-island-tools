"""Design a proper four-legged walk for the dragon and export:

  assets/dragons/hac_long/templates/gait_preview.gif          - the gait animated (stick legs on the real torso), to review
  assets/dragons/hac_long/templates/template_walk_gait_4x2.png - 8 key poses for ChatGPT to paint legs on (same torso in every cell)

Gait: lateral-sequence walk, the 4-beat walk of dogs/horses/big cats. Feet hit the ground in the
order left-hind -> left-fore -> right-hind -> right-fore, a quarter cycle apart. Each foot is on the
ground for 5/8 of the cycle (stance: it slides back under the body at walking speed) and in the air
for 3/8 (swing: lifts and reaches forward). Joints come from 2-bone IK: elbows bend back, stifles
(knees of the hind legs) bend forward, as on a real quadruped.

The dragon faces left, so its LEFT side faces the viewer: left legs = near legs (drawn in front of
the body, red in the template), right legs = far legs (behind the body, darker, blue in the template).

Coordinates are walk_v3 cell pixels (384x512 cell). Usage: .venv/bin/python tools/gait_design.py
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
from slice_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "assets" / "dragons" / "hac_long" / "templates"
TORSO_SRC = ROOT / "assets" / "dragons" / "hac_long" / "animations" / "walk_v3.png"   # torso donor: legs get erased, so any walk cell works

CELL = (384, 512)
GROUND = 471          # feet line
BELLY = 432           # torso is kept above this line; legs are drawn below it
DUTY = 0.625          # share of the cycle a foot is on the ground
STRIDE = 56           # how far a planted foot slides back during stance (px)
LEGS = {
    # name: root joint, (upper, lower) bone lengths, foot offset from root x, lift height,
    #       phase offset, bend (+1 = joint points back/right, -1 = forward/left), near side?
    "left_hind":  dict(root=(238, 414), bones=(25, 23), foot_dx=8,  lift=14, phase=0.00, bend=-1, near=True),
    "left_fore":  dict(root=(128, 412), bones=(27, 25), foot_dx=-6, lift=17, phase=0.25, bend=+1, near=True),
    "right_hind": dict(root=(226, 412), bones=(25, 23), foot_dx=8,  lift=14, phase=0.50, bend=-1, near=False),
    "right_fore": dict(root=(146, 410), bones=(27, 25), foot_dx=-6, lift=17, phase=0.75, bend=+1, near=False),
}
HIND_PASTERN = (7, -16)   # hock sits this far from the paw (metatarsus slants back)
FORE_PASTERN = (-2, -11)  # wrist sits this far from the paw


def foot(leg, t):
    """Paw position at cycle time t (0..1). Stance: slide back along the ground at constant speed.
    Swing: lift on a sine arc and reach forward with ease-in-out."""
    x0 = leg["root"][0] + leg["foot_dx"]
    phi = (t - leg["phase"]) % 1.0
    if phi < DUTY:
        u = phi / DUTY
        return x0 - STRIDE / 2 + STRIDE * u, GROUND
    u = (phi - DUTY) / (1 - DUTY)
    ease = u * u * (3 - 2 * u)
    return x0 + STRIDE / 2 - STRIDE * ease, GROUND - leg["lift"] * math.sin(math.pi * u)


def ik(root, target, bones, bend):
    """Middle joint of a 2-bone chain from root to target; bend picks the side the joint points to."""
    (rx, ry), (tx, ty), (a, b) = root, target, bones
    d = min(math.hypot(tx - rx, ty - ry), a + b - 0.01)
    base = math.atan2(ty - ry, tx - rx)
    off = math.acos(max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * d))))
    cands = [(rx + a * math.cos(base + s * off), ry + a * math.sin(base + s * off)) for s in (1, -1)]
    return max(cands, key=lambda p: bend * p[0])


def leg_points(name, t, body_dy=0.0):
    leg = LEGS[name]
    px, py = foot(leg, t)
    root = (leg["root"][0], leg["root"][1] + body_dy)
    hind = "hind" in name
    dx, dy = HIND_PASTERN if hind else FORE_PASTERN
    lower = (px + dx, py + dy)                       # hock (hind) / wrist (fore)
    mid = ik(root, lower, leg["bones"], leg["bend"])  # stifle (hind) / elbow (fore)
    return [root, mid, lower, (px, py)]


def body_bob(t):
    """Torso dips slightly twice per cycle, when two feet share the weight."""
    return 1.5 * math.cos(4 * math.pi * t)


def torso():
    """walk_v3 cell 1 with everything below the belly removed (the legs get redrawn)."""
    cell = key_magenta(Image.open(TORSO_SRC)).crop((0, 0, *CELL))
    arr = np.asarray(cell).copy()
    fade = np.clip((np.arange(CELL[1]) - (BELLY - 4)) / 8, 0, 1)[:, None]   # soft cut, 8 px
    arr[..., 3] = (arr[..., 3] * (1 - fade)).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def draw_leg(d, pts, color, width):
    d.line(pts, fill=color, width=width, joint="curve")
    for x, y in pts:
        r = width * 0.6
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    px, py = pts[-1]
    d.line([(px - 13, py), (px + 4, py)], fill=color, width=width)   # paw, toes point forward (left)


def pose(t, body, near_color, far_color, width, bob=True):
    """One frame: far legs, torso, near legs, on a transparent cell."""
    dy = body_bob(t) if bob else 0.0
    img = Image.new("RGBA", CELL)
    d = ImageDraw.Draw(img)
    for name, leg in LEGS.items():
        if not leg["near"]:
            draw_leg(d, leg_points(name, t, dy), far_color, width)
    img.alpha_composite(body, (0, int(round(dy))))
    d = ImageDraw.Draw(img)
    for name, leg in LEGS.items():
        if leg["near"]:
            draw_leg(d, leg_points(name, t, dy), near_color, width)
    return img


def main():
    REF.mkdir(parents=True, exist_ok=True)
    body = torso()

    # 1) preview GIF: 32 frames over a 2 s cycle, dragon-coloured legs, on grass green
    frames = []
    for k in range(32):
        f = Image.new("RGBA", CELL, (126, 190, 90, 255))
        ImageDraw.Draw(f).line([(0, GROUND + 1), (CELL[0], GROUND + 1)], fill=(96, 150, 70), width=2)
        f.alpha_composite(pose(k / 32, body, (22, 58, 92, 255), (10, 28, 48, 255), 9))
        frames.append(f.crop((20, 180, 364, 500)).convert("P", palette=Image.ADAPTIVE))
    frames[0].save(REF / "gait_preview.gif", save_all=True, append_images=frames[1:], duration=62, loop=0)

    # 2) ChatGPT template: 8 key poses, same torso (no bob, so the body is identical in every cell),
    #    near legs red, far legs blue, magenta background, faint ground line and cell borders
    sheet = Image.new("RGBA", (CELL[0] * 4, CELL[1] * 2), (255, 0, 255, 255))
    for k in range(8):
        cx, cy = (k % 4) * CELL[0], (k // 4) * CELL[1]
        sheet.alpha_composite(pose(k / 8, body, (255, 30, 30, 255), (40, 90, 255, 255), 8, bob=False), (cx, cy))
    d = ImageDraw.Draw(sheet)
    for x in (384, 768, 1152):
        d.line([(x, 0), (x, 1024)], fill=(200, 0, 200), width=2)
    d.line([(0, 512), (1536, 512)], fill=(200, 0, 200), width=2)
    for k in range(8):
        cx, cy = (k % 4) * CELL[0], (k // 4) * CELL[1]
        d.line([(cx + 20, cy + GROUND + 1), (cx + 364, cy + GROUND + 1)], fill=(225, 0, 225), width=1)
    sheet.convert("RGB").save(REF / "template_walk_gait_4x2.png")
    print("wrote", (REF / "gait_preview.gif").relative_to(ROOT), "and", (REF / "template_walk_gait_4x2.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
