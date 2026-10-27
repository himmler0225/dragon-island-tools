"""Khổng Tước (2026-10-27): a peacock on two legs, tail spread as on ref.png. The fan is the 5 drawn
feather sections reused in four layers (15 bones, back to front: pink, mixed, green, blue), each turned about
the rump; strikes open it wider still (motion.fan, pose.ts)."""
from lib.paths import DRAGONS

# parts/body.png: head (crest + beak, no neck), body with the neck, the yellow wing, then the 5 tail
# feathers left to right = outer (pink) to inner (blue), each drawn pointing up with its base at the bottom.
# parts/legs.png: 4 columns, the near leg in column 2 and the far leg in column 4 (thigh / shin / foot).
# ref.png: the whole peacock, tail spread; layout px = ref.png px (head and wing matched onto it).
BODY = DRAGONS / "peacock" / "parts" / "body.png"
RUMP = (700, 600)   # where every tail feather grows from

CONFIG = dict(
    name="Khổng Tước",
    key="tight",   # pink feathers: magenta / distance keying would eat them
    body_src=BODY,
    legs_src=DRAGONS / "peacock" / "parts" / "legs.png",
    far_shade=0.8, wing_far_shade=0.8,
    # short sturdy legs as on ref.png
    leg_scale=0.42, leg_pull=(60, 60), ground=945, leg_widen=1.7,
    body={
        "fan_1": dict(src_img=BODY, src=(708, 514), img_scale=0.72, at=(602, 49), rot=-16),   # pink
        "fan_2": dict(src_img=BODY, src=(708, 514), img_scale=0.72, at=(602, 49), rot=18),   # pink
        "fan_3": dict(src_img=BODY, src=(708, 514), img_scale=0.72, at=(602, 49), rot=52),   # pink
        "fan_4": dict(src_img=BODY, src=(708, 514), img_scale=0.72, at=(602, 49), rot=86),   # pink
        "fan_5": dict(src_img=BODY, src=(708, 514), img_scale=0.72, at=(602, 49), rot=120),   # pink
        "fan_6": dict(src_img=BODY, src=(917, 539), img_scale=0.72, at=(627, 85), rot=1),   # pinkgreen
        "fan_7": dict(src_img=BODY, src=(917, 539), img_scale=0.72, at=(627, 85), rot=35),   # pinkgreen
        "fan_8": dict(src_img=BODY, src=(917, 539), img_scale=0.72, at=(627, 85), rot=69),   # pinkgreen
        "fan_9": dict(src_img=BODY, src=(917, 539), img_scale=0.72, at=(627, 85), rot=103),   # pinkgreen
        "fan_10": dict(src_img=BODY, src=(1106, 565), img_scale=0.684, at=(640, 150), rot=12),   # green
        "fan_11": dict(src_img=BODY, src=(1106, 565), img_scale=0.684, at=(640, 150), rot=50),   # green
        "fan_12": dict(src_img=BODY, src=(1106, 565), img_scale=0.684, at=(640, 150), rot=88),   # green
        "fan_13": dict(src_img=BODY, src=(1438, 643), img_scale=0.612, at=(659, 296), rot=24),   # blue
        "fan_14": dict(src_img=BODY, src=(1438, 643), img_scale=0.612, at=(659, 296), rot=58),   # blue
        "fan_15": dict(src_img=BODY, src=(1438, 643), img_scale=0.612, at=(659, 296), rot=92),   # blue
        "torso": dict(src_img=BODY, src=(311, 626), img_scale=0.92, at=(240, 266)),
        "head":  dict(src_img=BODY, src=(166, 207), img_scale=0.94, at=(205, 114)),
        "wing_near": dict(src_img=BODY, src=(419, 440), img_scale=0.94, at=(452, 484)),
    },
    joints={
        **{f"fan_{k}": RUMP for k in range(1, 16)},
        "torso": (480, 560),
        "head": (330, 320),        # the top of the neck, under the back of the head
        "wing_near": (470, 520),   # the front of the folded wing
    },
    # a ground bird: never flies; fan = how far each feather turns (rad) when the tail opens wider than
    # drawn (strikes): away from the middle of the fan, so it spreads both ways
    motion={"noFly": True, "sleepTail": [0, 0, 0], "wingSpread": [0, 0], "stance": [0, -60],
            "fan": [-0.415, -0.208, 0.0, 0.208, 0.415, -0.312, -0.104, 0.104, 0.312, -0.244, -0.012, 0.22, -0.171, 0.037, 0.244]},
    # the legs come out from under the body: drawn behind it (the thighs are hidden by the belly)
    behind=[f"{leg}_{seg}" for leg in ("hind_far", "hind_near") for seg in ("upper", "lower", "paw")],
    legs={"hind_near": dict(col=1, x=430), "hind_far": dict(col=3, x=600)},
)
