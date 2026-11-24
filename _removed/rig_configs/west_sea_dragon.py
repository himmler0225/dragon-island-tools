"""Tây Hải Long Vương: Việt Hải Long Vương's family, green; its pink belly needs distance keying. Same layout (sea_dragon.layout), its own fit."""
from .sea_dragon import layout

# its neck is drawn lower than the others': the head (and jaw) sit 80 px higher and 35 px back, right on the end of the neck

CONFIG = layout("west_sea_dragon", "Tây Hải Long Vương", dict(
    torso=dict(src=(958, 524), img_scale=1.092, at=(472, 48)),
    head=dict(src=(301, 293), img_scale=0.98, at=(218, 22)),
    jaw=dict(src=(226, 674), img_scale=0.98, at=(322, 386)),
    joints=dict(torso=(863, 509), head=(556, 437), jaw=(525, 451)),
    legs=dict(fore_near=553, fore_far=508, hind_near=1172, hind_far=1127),
    crouch={"drop": 22, "reach": {"fore": 26, "hind": 16}, "raise": {"fore": -8, "hind": -6}},   # its own stance: Việt Hải's deep crouch folded these legs into a Z
    leg_scale=0.562, hind_scale=0.944, ground=1025,
), key="distance")
