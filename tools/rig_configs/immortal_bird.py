"""Bất Tử Điểu (2026-11-01): an immortal fire bird in yellow, orange and blue feathers, a long tail of three
flowing eye-spot plumes. Walks on two taloned legs, flies.

ref.png: the whole bird, facing left; layout px = ref.png px. parts/body.png: an old head with the far wing
as a crest (unused), near wing (middle), far wing (right), body: neck + torso + a tail (only the torso is
used). parts/head.png: the head alone. parts/legs.png: near and far leg, whole. parts/tail.png: the tail
base (left) and three long plumes A (top), B (middle), C (bottom, the longest), each drawn pointing right.
"""
from lib.paths import DRAGONS

P = DRAGONS / "immortal_bird" / "parts"
TAIL = P / "tail.png"
# the three plumes grow from the end of the tail base, fanned (fan_k: they sway each on its own beat)
ROOT = (750, 640)
plume = lambda src, at, rot: dict(src_img=TAIL, src=src, img_scale=0.56, at=at, rot=rot)

CONFIG = dict(
    name="Bất Tử Điểu",
    size=0.8,
    tail_glow={"width": 0.6},   # the tail plumes softly lit
    wing_glow={"width": 1.7},   # a thick golden light on the wing rims, lit by the wing beat
    body_aura={"color": (255, 165, 40)},   # 2026-11-20: the whole body glows like embers
    key="tight",   # pink-purple feathers: magenta keying would eat them
    body_src=P / "body.png",
    legs_src=P / "legs.png",
    joint_fade=0.05, split_overlap=6,   # each leg split at its narrowest rows: thigh / shin / talons, bending at the knee
    far_shade=0.82, wing_far_shade=0.85,
    leg_scale=1.0, leg_pull=0, ground=935,
    body={
        "fan_1": plume((973, 770), (ROOT[0] - 50, ROOT[1] - 60), 48),    # C: the longest, sweeping down
        "fan_2": plume((1083, 425), (ROOT[0] - 30, ROOT[1] - 75), 22),    # B
        "fan_3": plume((976, 169), (ROOT[0] - 20, ROOT[1] - 80), -4),   # A: rising
        "wing_far":  dict(src=(1223, 304), at=(650, 120), img_scale=0.95),
        "tail_base": dict(src_img=TAIL, src=(224, 490), img_scale=0.72, at=(515, 572), rot=-12),
        "torso":     dict(src=(825, 749), at=(319, 416), keep=[(270, 530, 678, 880)], fade=(640, 678), rot=-8),   # (x < 678: a speck of the old tail at its edge)
        "head":      dict(src_img=P / "head.png", img_scale=0.39, at=(263, 279)),   # (smaller, about the neck)
        "wing_near": dict(src=(732, 307), at=(560, 60), img_scale=1.0, rot=6),
    },
    joints={
        "torso": (500, 680),
        "head": (445, 585),          # on the neck
        "tail_base": (530, 655),     # the rump
        "fan_1": ROOT, "fan_2": ROOT, "fan_3": ROOT,
        "wing_near": (610, 560),     # the wing roots on the back
        "wing_far": (660, 540),
    },
    parents={"fan_1": "tail_base", "fan_2": "tail_base", "fan_3": "tail_base"},
    motion={"fan": [0.45, 0.15, -0.2], "fanWave": 0.08,   # the plumes float gently
            "flyLegs": "tuck", "tuck": [-10, 1.0],   # in flight the legs fold up in a V, talons under the belly
            "wingSpread": [0.1, -0.05],
            "sleepTail": [0, 0, 0], "stance": [0, 0], "stride": 70, "flyPitch": 0.15,
            "alwaysFly": True, "idleHover": 80},   # always in the air: flies about and rests hovering
    legs={"hind_near": dict(pick=(439, 531), scale=0.42, x=470), "hind_far": dict(pick=(1132, 568), scale=0.4, x=437)},
    # wings as Hắc Long's: the far one fans up behind the head, the near one sweeps back over the back from
    # the shoulders (on the ground only)
    wing_rest={"wing_far": (-250, 20, -18, 0.9), "wing_near": (-110, 70, 8, 0.95)},
    # in flight the wings beat from the shoulders, not from where they are drawn (behind the back)
    wing_fly={"wing_far": (-120, 95), "wing_near": (-100, 50)},
)
