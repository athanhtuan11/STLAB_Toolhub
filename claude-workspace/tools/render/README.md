# Render Blender

Lệnh:

```text
python tools/render/render.py model.FCStd --cmf cmf.json --out render
```

CMF là JSON gồm `rules` (mảng `names`, màu `#RRGGBB`, `finish` là `matte`, `satin` hoặc `gloss`), `default` và `background`. Quy tắc khớp đầu tiên được áp dụng.

Views: `iso`, `front`, `top`, `side34`. Dùng `eevee` để xem nhanh; dùng `--engine cycles --samples 128` cho ảnh chốt. Kích thước mặc định `1600x1200`.
