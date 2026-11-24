"""Gold Dragon layout. Silver Dragon uses the same layout (recoloured)."""
from lib.paths import DRAGONS

def layout(dragon_id: str, name: str, wing_root=(680, 953)) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.86,
        leg_scale=0.6, leg_pull=(100, 95), ground=1265,
        # the joint balls drawn at the bottom of each thigh / shin (arms too) ARE the joints: each lower piece's top end
        # sits on the centre of the ball above and turns about it, so a bent knee never opens a slit (2026-11-20)
        ball_joints=True, ball_pairs=36,
        # 2026-11-20: legs as Hồng Ngọc Long's: thigh over shin over paw, outlines as drawn, no joint caps
        legs_down=True, joint_fade=0,
        no_caps=tuple(f"{leg}_{seg}" for leg in ("hind_near", "hind_far") for seg in ("upper", "paw")),   # the knee keeps its cap
        # parts/wing_far.png (2026-11-09): the far wing drawn upright as Hắc Long's, its root ornament at the bottom
        place={"wing_far": dict(src=DRAGONS / dragon_id / "parts" / "wing_far.png", root=wing_root,
                                height_of="wing_near", height=1.0)},
        body={
            "wing_far":  dict(src=(1205, 361), at=(447, 296), rot=-30),
            "tail_tip":  dict(src=(1395, 713), at=(951, 545)),
            "tail_mid":  dict(src=(1106, 853), at=(763, 807), fade=(1190, 1250)),
            "tail_base": dict(src=(828, 772), at=(608, 670), fade=(875, 935)),
            "torso":     dict(src=(428, 674), at=(169, 444)),   # body.png (2026-11-10): no leg stump on the chest to cut away any more
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
                "stance": [0, 0],   # the far leg drawn a step ahead of the near one: both show, straight under the body
                "lean": 0.1,          # stooping a little forward over its legs
                "flyLegs": "dangle", "flyPitch": -0.12,
                "stride": 85},
        legs={
            "fore_near": dict(col=0, x=295, top=700, scale=0.75),
            "hind_near": dict(col=1, x=459),
            "fore_far":  dict(col=2, x=240, top=690, scale=0.75),
            "hind_far":  dict(col=3, x=402),
        },
    )


CONFIG = {**layout("gold_dragon", "Rồng Vàng"),
          # on the ground the far wing peeks up ahead of the near one, both a little smaller than drawn;
          # in flight both beat from where they are drawn (wing_rest, not wing_fit)
          "wing_rest": {"wing_far": (-60, -90, 0, 0.85), "wing_near": (20, -30, 8, 1.0)}}

# 2026-11-20: the far legs placed as Hắc Long's: each far paw a step ahead of its near twin and a little up (it stands
# behind the body), the same offsets as Hắc Long's (with the rig editor tweaks): the whole far leg moved (layout px)
CONFIG["legs"] = {**CONFIG["legs"],
                  "fore_far": {**CONFIG["legs"]["fore_far"], "nudge": {s: (23, -44) for s in ("upper", "lower", "paw")}},
                  "hind_far": {**CONFIG["legs"]["hind_far"], "nudge": {s: (11, -18) for s in ("upper", "lower", "paw")}}}
# (2026-11-20, later: a biped lifting its far hind leg as high as Hắc Long's reads as a step: only ~8 rig px up)
