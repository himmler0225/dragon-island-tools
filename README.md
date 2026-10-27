# Dragon Island Tools

Pipeline ảnh (Python) cho game [Dragon Island](../dragon-island): đọc ảnh gốc trong `assets/`, cắt/ráp rig rồi ghi vào `frontend/public/` của repo game.

| Thư mục | Nội dung |
|---|---|
| `assets/` | Ảnh gốc: `dragons/<id>/` (ref.png, parts/, skills/), `island/`, `buildings/`, `ui/`, `battle/`, `eggs/`, `status/`… |
| `tools/` | Script cắt ảnh + dựng rig (xem [tools/README.md](tools/README.md)) |

## Cài đặt
```bash
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
```
Phiên bản thư viện được ghim cố định: Pillow/OpenCV khác phiên bản cho ra pixel khác → `frontend/public` sẽ bị diff.

## Output
Mặc định ghi vào repo game checkout cạnh repo này: `../dragon-island/frontend/public`.
Đổi chỗ khác bằng biến môi trường:
```bash
DRAGON_ISLAND_PUBLIC=/path/to/dragon-island/frontend/public .venv/bin/python tools/build_rig.py
```

## Chạy pipeline
```bash
.venv/bin/python tools/build_rig.py            # tất cả rồng
.venv/bin/python tools/build_rig.py black_dragon   # một rồng
.venv/bin/python tools/slice_skills.py
.venv/bin/python tools/slice_cloud.py sea_dragon
.venv/bin/python tools/slice_world.py
.venv/bin/python tools/slice_ui.py
.venv/bin/python tools/slice_hud_icons.py
git -C ../dragon-island status --porcelain frontend/public   # chạy lại không đổi art thì phải trống
```

Các bước thêm rồng mới / tham số chỉnh rig: xem `docs/ADDING_A_DRAGON.md` và `docs/COMMON_TWEAKS.md` trong repo game.
