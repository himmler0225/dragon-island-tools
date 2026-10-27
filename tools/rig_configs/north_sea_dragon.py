"""Bắc Hải Long Vương: Việt Hải Long Vương's family, ice blue. Same layout (sea_dragon.layout).
parts/body.png was redrawn after Việt Hải's body.png: each piece is put on Việt Hải's spot (same top-left,
scaled to the same width), with its joints; the head and jaw then 40 px lower, 20 px back onto the neck. parts/body_old.png: the first sheet."""
from .sea_dragon import layout

CONFIG = layout("north_sea_dragon", "Bắc Hải Long Vương", dict(
    torso=dict(src=(1016, 523), img_scale=1.227, at=(476, 191)),
    head=dict(src=(287, 379), img_scale=0.987, at=(186, 72)),
    jaw=dict(src=(231, 760), img_scale=0.844, at=(292, 443)),
    joints=dict(torso=(860, 600), head=(545, 500), jaw=(495, 467)),
    legs=dict(fore_near=556, fore_far=511, hind_near=1166, hind_far=1121),
    leg_scale=0.597, hind_scale=0.895, ground=1138,
))
