"""The Long Vương family (redesign 2026-10-26): wingless serpentine Eastern dragons on a cloud.
Việt Hải Long Vương (sea_dragon) and its four recoloured kin (east/west/north/south_sea_dragon) share
this layout; each passes its own fit (where its pieces sit), see the variant files."""
from lib.paths import DRAGONS

# parts/body.png: the head (no lower jaw, no neck), the lower jaw, and the whole body from the neck to
# the tail tip in ONE piece (no legs, no separate tail: the tail moves with the body).
# parts/legs.png: 4 columns (near fore, near hind, far fore, far hind) x thigh / shin / paw (pieces drawn
# touching are split at their narrowest row).
# ref.png: the whole dragon; layout px = ref.png px. A fit: the head matched onto ref.png, the body set
# under the back of the head and sized against it (as long as 2.3 head widths), the legs sized by their
# paws, legs and ground placed relative to the body. Then evened out against sea_dragon (head widths):
# the same fore and hind leg lengths (leg_scale, hind_scale) and the same clearance under the chest (ground).


def layout(dragon_id: str, name: str, fit: dict, key: str | None = None) -> dict:
    body = DRAGONS / dragon_id / "parts" / "body.png"
    # src: a point inside the piece on body.png; at: its top-left on ref.png
    piece = lambda n: dict(src_img=body, src=fit[n]["src"], img_scale=fit[n]["img_scale"], at=fit[n]["at"])
    legs = fit["legs"]
    hind = fit.get("hind_scale", 1.0)   # hind legs drawn shorter/longer than the fore ones on some sheets
    # a hind shin drawn in one piece with the paw: cut it at the ankle (low on the piece), not mid-shin
    split = {"split_band": fit["hind_split"]} if "hind_split" in fit else {}
    return dict(
        name=name,
        size=1.2,   # on-screen size vs the others (a long thin body: area alone makes it too small)
        **({"key": key} if key else {}),
        body_src=body,
        legs_src=DRAGONS / dragon_id / "parts" / "legs.png",
        far_shade=0.8, wing_far_shade=0.8,
        # big overlaps at knee and ankle keep the legs short and sturdy
        # pieces meet end to end (small overlap): the legs keep their drawn length and fold into a V instead
        leg_scale=fit["leg_scale"], leg_pull=(40, 25), ground=fit["ground"],
        # crouched like ref.png: the body sinks and the knees bend; legs set high up the body (raise),
        # fore paws a step forward, hind paws a step back
        # hips pulled down by the extra length (raise < 0) so they sit where they did: the knees bend into a V
        crouch={"drop": 50, "reach": {"fore": 70, "hind": 35}, "raise": {"fore": -35, "hind": -30}},
        # no faded joint edges: bent hard while walking, the faded rims showed as gaps (the caps cover the joints)
        joint_fade=0,
        body={"torso": piece("torso"), "head": piece("head"), "jaw": piece("jaw")},   # jaw: lower jaw + beard
        joints={
            "torso": fit["joints"]["torso"],
            "head": fit["joints"]["head"],   # back of the head, sitting on the end of the neck
            "jaw": fit["joints"]["jaw"],     # the hinge at the back of the jaw, under the cheek
        },
        parents={"jaw": "head"},
        # flies standing on a cloud (assets/dragons/sea_dragon/cloud.png, tools/slice_cloud.py) instead of wings
        # short, low steps: long or high ones fold the crouched legs shut
        # stance: far paws a step AHEAD of the near ones (rig px; the default puts them behind, right where
        # the near legs hide them) so all four legs show, standing and on the cloud
        motion={"sleepTail": [0, 0, 0], "rideCloud": True, "stride": 55, "liftScale": 0.45, "stance": [-45, -45]},
        # front legs under the chest, hind legs under the hips
        legs={"fore_near": dict(col=0, x=legs["fore_near"]), "hind_near": dict(col=1, x=legs["hind_near"], scale=hind, **split),
              "fore_far": dict(col=2, x=legs["fore_far"]), "hind_far": dict(col=3, x=legs["hind_far"], scale=hind, **split)},
    )


CONFIG = layout("sea_dragon", "Việt Hải Long Vương", dict(
    torso=dict(src=(1007, 540), img_scale=1.25, at=(476, 191)),
    head=dict(src=(288, 340), img_scale=1.0, at=(186, 17)),
    jaw=dict(src=(229, 695), img_scale=1.0, at=(292, 388)),
    joints=dict(torso=(860, 600), head=(545, 445), jaw=(495, 412)),
    legs=dict(fore_near=556, fore_far=511, hind_near=1166, hind_far=1121),
    leg_scale=0.626, hind_scale=0.929, ground=1067,
))
