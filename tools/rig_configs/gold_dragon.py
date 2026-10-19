"""Gold Dragon: feathered golden dragon that walks upright on its hind legs, arms swaying in front.

Silver Dragon is the same drawing recoloured (pieces at identical sheet positions), so both use this layout
through `layout(id, name)`.
"""
from lib.paths import DRAGONS

# parts/body.png: head (closed mouth), lower jaw, torso (neck tube + chest + hips, round sockets at the
# shoulders/hips), near wing, far wing, 3 tail slices joined by ring ends.
# parts/legs.png columns: near arm, near hind leg, far arm, far hind leg (3 pieces each).


def layout(dragon_id: str, name: str) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.75,
        # limb pieces end in ball joints: pull the next piece up over the ball (knee, ankle) so no gap shows
        leg_scale=0.6, leg_pull=(100, 95), ground=1265,   # legs tucked 60 px further up into the hips
        body={
            # far wing turned toward the head so the two wings read as a V (like the reference)
            "wing_far":  dict(src=(1205, 361), at=(447, 296), rot=-30),
            "tail_tip":  dict(src=(1395, 713), at=(951, 545)),
            # tail slices end in a ring; each slice is tucked deep under the one before and that one's
            # end ring fades out (fade, sheet x), so the tail reads as one piece
            "tail_mid":  dict(src=(1106, 853), at=(763, 807), fade=(1190, 1250)),
            "tail_base": dict(src=(828, 772), at=(608, 670), fade=(875, 935)),   # root sits on the hips
            # the round socket on the chest front pointed at nothing: cut away
            "torso":     dict(src=(428, 674), at=(169, 444), drop=[(160, 615, 228, 700)]),
            "jaw":       dict(src=(149, 468), at=(135, 433)),   # tucked under the snout, teeth just behind its tip
            "head":      dict(src=(251, 239), at=(76, 130)),    # mane drops over the open neck ring
            "wing_near": dict(src=(703, 304), at=(385, 270)),
        },
        joints={
            "torso": (430, 700),
            "head": (330, 480),        # top ring of the neck tube
            "jaw": (265, 458),         # hinge at the back of the jaw
            "wing_near": (410, 635),   # round socket on the shoulder (faces the viewer)
            "wing_far": (470, 610),    # far shoulder, a little behind and above
            "tail_base": (635, 790),   # ring end of each tail slice
            "tail_mid": (795, 860),
            "tail_tip": (1005, 925),
        },
        parents={"jaw": "head"},
        # stands upright: the arms ("fore" limbs) hang from the chest and sway; only the hind legs walk
        # armPose: the arms are held apart in a diagonal - near hand low, far hand a little higher and
        # further forward (like the reference) - so the two read as two arms, not one
        motion={"sleepTail": [0.1, 0.15, 0.2], "wingSpread": [0.1, -0.05], "foreArms": True,
                "armPose": [[-6, 4], [-30, -12]],
                "stance": [0, -80],   # standing: far foot a step ahead so both legs show
                "flyLegs": "dangle", "flyPitch": -0.12,
                "stride": 85},   # shorter steps: long strides bent the ankle far enough to open it   # flies head a little down
        legs={
            "fore_near": dict(col=0, x=295, top=700, scale=0.75),
            "hind_near": dict(col=1, x=459),
            "fore_far":  dict(col=2, x=240, top=690, scale=0.75),
            "hind_far":  dict(col=3, x=481),   # biped: both hips together under the pelvis
        },
    )


CONFIG = layout("rong_vang", "Rồng Vàng")
