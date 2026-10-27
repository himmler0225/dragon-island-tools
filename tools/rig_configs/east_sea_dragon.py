"""Đông Hải Long Vương: Việt Hải Long Vương's family, red. Same layout (sea_dragon.layout).
parts/body.png was redrawn on Việt Hải's body.png (same pieces at the same spots), so it uses Việt Hải's
fit; only the legs (its own legs.png) are sized for it. parts/body_old.png: the first sheet."""
from .sea_dragon import layout

CONFIG = layout("east_sea_dragon", "Đông Hải Long Vương", dict(
    torso=dict(src=(1009, 542), img_scale=1.25, at=(475, 199)),
    head=dict(src=(288, 342), img_scale=1.0, at=(187, 14)),
    jaw=dict(src=(229, 695), img_scale=1.0, at=(293, 385)),
    joints=dict(torso=(860, 600), head=(546, 442), jaw=(496, 409)),
    legs=dict(fore_near=556, fore_far=511, hind_near=1166, hind_far=1121),
    leg_scale=0.645, hind_scale=0.905, ground=1132,
))
