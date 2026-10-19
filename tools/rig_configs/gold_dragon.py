"""Gold Dragon layout. Silver Dragon uses the same layout (recoloured)."""
from lib.paths import DRAGONS

def layout(dragon_id: str, name: str) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.75,
        leg_scale=0.6, leg_pull=(100, 95), ground=1265,
        body={
            "wing_far":  dict(src=(1205, 361), at=(447, 296), rot=-30),
            "tail_tip":  dict(src=(1395, 713), at=(951, 545)),
            "tail_mid":  dict(src=(1106, 853), at=(763, 807), fade=(1190, 1250)),
            "tail_base": dict(src=(828, 772), at=(608, 670), fade=(875, 935)),
            "torso":     dict(src=(428, 674), at=(169, 444), drop=[(160, 615, 228, 700)]),
            "jaw":       dict(src=(149, 468), at=(135, 433)),
            "head":      dict(src=(251, 239), at=(76, 130)),
            "wing_near": dict(src=(703, 304), at=(385, 270)),
        },
        joints={
            "torso": (430, 700),
            "head": (330, 480),
            "jaw": (265, 458),
            "wing_near": (410, 635),
            "wing_far": (470, 610),
            "tail_base": (635, 790),
            "tail_mid": (795, 860),
            "tail_tip": (1005, 925),
        },
        parents={"jaw": "head"},
        motion={"sleepTail": [0.1, 0.15, 0.2], "wingSpread": [0.1, -0.05], "foreArms": True,
                "armPose": [[-6, 4], [-30, -12]],
                "stance": [0, -80],
                "flyLegs": "dangle", "flyPitch": -0.12,
                "stride": 85},
        legs={
            "fore_near": dict(col=0, x=295, top=700, scale=0.75),
            "hind_near": dict(col=1, x=459),
            "fore_far":  dict(col=2, x=240, top=690, scale=0.75),
            "hind_far":  dict(col=3, x=481),
        },
    )


CONFIG = layout("rong_vang", "Rồng Vàng")
