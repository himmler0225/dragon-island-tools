# Tools

Python asset pipeline for the Dragon Island game.

## Structure

```
tools/
├── lib/               shared helpers used by all pipeline scripts
│   ├── paths.py       ROOT, ASSETS, PUBLIC, DRAGONS constants
│   ├── image.py       key_magenta, key_distance, components, cut, shade
│   └── __init__.py    re-exports for backwards compatibility
├── rig_configs/       one file per dragon species
│   ├── __init__.py    CONFIGS dict + LEG_SIDES (all species)
│   ├── hac_long.py
│   ├── rong_xuong.py
│   ├── tuan_long.py
│   ├── hai_long.py
│   └── ki_lan.py
├── legacy/            one-off or experimental scripts kept for reference
│   ├── slice_sheet.py
│   └── gait_design.py
├── build_rig.py       slice dragon body/legs sheets → public/dragons/<id>/
├── slice_skills.py    slice skill art → public/dragons/<id>/skills/
├── slice_cloud.py     slice riding cloud → public/dragons/<id>/cloud*.png
├── slice_world.py     slice islands + buildings + resource icons
├── slice_hud_icons.py extract HUD icons from the 4×4 sheet
└── slice_ui.py        logo + loading screen → public/ui/
```

## Quick reference

```bash
# All scripts run via the project venv from the repo root:
.venv/bin/python tools/build_rig.py            # all dragons
.venv/bin/python tools/build_rig.py hac_long   # one dragon
.venv/bin/python tools/slice_skills.py          # all dragons with skills/
.venv/bin/python tools/slice_cloud.py           # all dragons with cloud.png
.venv/bin/python tools/slice_world.py
.venv/bin/python tools/slice_hud_icons.py
.venv/bin/python tools/slice_ui.py

# After any run, verify public/ is clean:
git status --porcelain frontend/public
```

## Shared library

```python
from lib.paths import ROOT, ASSETS, PUBLIC, DRAGONS
from lib.image import key_magenta, key_distance, components, cut, shade
from lib import components, cut, key_distance, key_magenta, shade  # re-exported
```

`key_magenta` — remove flat `#FF00FF` background (dragon sheets).
`key_distance` — remove `#FF00FF` background by colour distance (preserves purples).
`components` — connected-component islands from an RGBA image.
`cut` — carve one island out of an image using its component bbox/mask.
`shade` — multiply brightness by a float factor.
