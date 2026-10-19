"""Placeholder skill icons for dragons without skills/icons.png: the dragon's portrait on a round
framed badge, one tint per slot (passive grey-blue, basic green, skill blue, ultimate gold).

Usage: .venv/bin/python tools/skill_icons_from_portrait.py <dragon_id> ...
"""
import sys

from PIL import Image, ImageDraw, ImageFilter

from lib.paths import OUT

SIZE = 256
TINT = {"passive": (70, 90, 120), "basic": (40, 120, 70), "skill": (40, 90, 170), "ultimate": (190, 140, 30)}


def badge(portrait, rgb):
    img = Image.new("RGBA", (SIZE, SIZE))
    d = ImageDraw.Draw(img)
    d.ellipse([6, 6, SIZE - 6, SIZE - 6], fill=(*rgb, 255), outline=(255, 226, 140, 255), width=10)
    d.ellipse([22, 22, SIZE - 22, SIZE - 22], fill=tuple(min(255, c + 40) for c in rgb) + (255,))
    p = portrait.copy()
    p.thumbnail((SIZE - 60, SIZE - 60), Image.LANCZOS)
    shadow = Image.new("RGBA", img.size)
    shadow.paste((0, 0, 0, 120), ((SIZE - p.width) // 2 + 4, (SIZE - p.height) // 2 + 6), p.getchannel("A"))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(4)))
    img.alpha_composite(p, ((SIZE - p.width) // 2, (SIZE - p.height) // 2))
    return img


for did in sys.argv[1:]:
    portrait = Image.open(OUT / did / "portrait.png").convert("RGBA")
    dst = OUT / did / "skills"
    dst.mkdir(exist_ok=True)
    for slot, rgb in TINT.items():
        badge(portrait, rgb).save(dst / f"icon_{slot}.png", optimize=True)
    print(f"{did}: 4 placeholder icons")
