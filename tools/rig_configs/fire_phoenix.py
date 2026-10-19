"""Fire Phoenix layout. Ice Phoenix uses the same layout (recoloured)."""
from lib.paths import DRAGONS

def layout(dragon_id: str, name: str) -> dict:
    return dict(
        name=name,
        body_src=DRAGONS / dragon_id / "parts" / "body.png",
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.78,
        leg_scale=0.53, leg_pull=(70, 55), ground=1005,
        body={
            "wing_far":  dict(src=(1234, 321), at=(403, 330), rot=-30),
            "tail_tip":  dict(src=(1355, 763), at=(835, 520)),
            "tail_base": dict(src=(825, 752), at=(595, 615), rot=-8),
            "torso":     dict(src=(441, 762), at=(135, 583)),
            "head":      dict(src=(206, 455), at=(95, 318)),
            "wing_near": dict(src=(701, 281), at=(444, 275), rot=-20),
        },
        parents={"tail_tip": "tail_base"},
        joints={
            "torso": (440, 760),
            "head": (270, 625),
            "wing_near": (470, 610),
            "wing_far": (420, 580),
            "tail_base": (625, 715),
            "tail_tip": (865, 755),
        },
        motion={"wingSpread": [0.22, -0.05], "flyLegs": "dangle", "flyPitch": 0.2},
        legs={"fore_near": dict(col=0, x=190), "hind_near": dict(col=1, x=480),
              "fore_far": dict(col=2, x=235), "hind_far": dict(col=3, x=525)},
    )


CONFIG = layout("phuong_hoang_lua", "Phượng Hoàng Lửa")
