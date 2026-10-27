"""Nam Hải Long Vương: Việt Hải Long Vương's family, yellow. Same layout (sea_dragon.layout), its own fit."""
from .sea_dragon import layout

# head (and jaw) set 60 px lower than its fit: it sat high above the neck

CONFIG = layout("south_sea_dragon", "Nam Hải Long Vương", dict(
    torso=dict(src=(1010, 513), img_scale=1.214, at=(488, 94)),
    head=dict(src=(283, 361), img_scale=1.04, at=(181, 135)),
    jaw=dict(src=(253, 753), img_scale=1.04, at=(291, 466)),
    joints=dict(torso=(883, 591), head=(540, 575), jaw=(528, 505)),
    legs=dict(fore_near=570, fore_far=524, hind_near=1195, hind_far=1149),
    leg_scale=0.642, hind_scale=0.922, ground=1197,
))
