"""Fire Phoenix: golden fire phoenix-dragon, walks on 4 legs and flies like the Black Dragon.
Ice Phoenix is the same sheets recoloured (pieces at the same positions) - shares this layout
through `layout(id, name)`.

parts/body.png: head (short crest), torso, near wing, far wing, 3 tail slices; parts/legs.png: 4
columns x 3 pieces. The body pieces keep their sheet layout with the ~40 px gaps closed; the wings
are moved from the top of the sheet onto the back.
"""
from lib.paths import DRAGONS


def layout(dragon_id: str, name: str) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.78,
        leg_scale=0.53, leg_pull=(70, 55), ground=1005,   # legs a bit bigger (they read thin under the feathered body)
        body={
            "wing_far":  dict(src=(1234, 321), at=(403, 330), rot=-30),   # raised and turned up, like Hắc Long
            # short tail like the reference: the base slice turned up, then the curled tip (mid slice left out)
            "tail_tip":  dict(src=(1355, 763), at=(835, 520)),   # its feathered end sits on the end of the base
            "tail_base": dict(src=(825, 752), at=(595, 615), rot=-8),
            "torso":     dict(src=(441, 762), at=(135, 583)),
            "head":      dict(src=(206, 455), at=(95, 318)),   # neck pressed 25 px into the chest (it stood off the body)
            "wing_near": dict(src=(701, 281), at=(444, 275), rot=-20),
        },
        parents={"tail_tip": "tail_base"},
        joints={
            "torso": (440, 760),
            "head": (270, 625),        # base of the neck, on the chest
            "wing_near": (470, 610),   # root ball on the shoulder
            "wing_far": (420, 580),
            "tail_base": (625, 715),
            "tail_tip": (865, 755),
        },
        # moves like Hắc Long: wings spread in a V on the ground, legs hang stretched out in flight
        motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2},
        legs={"fore_near": dict(col=0, x=190), "hind_near": dict(col=1, x=480),
              "fore_far": dict(col=2, x=235), "hind_far": dict(col=3, x=525)},
    )


CONFIG = layout("phuong_hoang_lua", "Phượng Hoàng Lửa")
