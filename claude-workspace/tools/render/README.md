# Render Blender

Render ảnh duyệt kiểu studio (vật liệu nhựa PETG) từ model FreeCAD bằng Blender 5.2.
Dùng cho bước 0 "Giao diện" của dự án maker: một lệnh ra bộ ảnh PNG + file scene JSON.

## Lệnh

```text
python tools/render/render.py <model.FCStd> --cmf <cmf.json> --out <dir> \
    [--views iso,front,top,side34] [--samples 64] [--size 1600x1200] \
    [--name <tiền tố>] [--engine eevee|cycles]
```

- Kết quả: `<dir>/<name>-<view>.png` và `<dir>/<name>-scene.json`; dòng cuối in `RENDER OK <n ảnh>`.
- `--name` mặc định là tên file model. Đường dẫn `model`, `--cmf`, `--out` tính theo thư mục đang chạy lệnh.
- `--engine eevee` (mặc định) để xem nhanh; `--engine cycles --samples 128` cho ảnh chốt (bật denoise).
- `--size` mặc định `1600x1200`; `--samples` chỉ dùng cho cycles.

## cmf.json

Do product-designer viết. Quy tắc **đầu tiên khớp** được áp dụng; không khớp thì dùng `default`.
`names` so khớp kiểu `fnmatch` trên Label của object trong FreeCAD.

```json
{
  "rules": [
    {"names": ["Base_*"], "color": "#1E5A45", "finish": "matte"},
    {"names": ["Ref_*"], "color": "#2A2E33", "finish": "satin"}
  ],
  "default": {"color": "#D9DDD9", "finish": "satin"},
  "background": "#ECF1EF"
}
```

- `color`: `#RRGGBB` (sRGB).
- `finish`: `matte` (roughness 0.65, specular 0.3), `satin` (0.45) hoặc `gloss` (0.25).
- `background`: màu phông, mặc định `#ECF1EF` (màu "sương" của `studio/design/tokens.json`).

## Các view

| View | Camera |
| --- | --- |
| `iso` | phối cảnh 50 mm, az −45°, el 30° |
| `front` | trực giao, nhìn theo +Y (thấy mặt hông XZ) |
| `top` | trực giao, từ trên xuống |
| `side34` | phối cảnh 85 mm, az −30°, el 15° |

Camera tự khung theo hộp bao toàn cảnh (lề 12 %), nên mọi model cùng tỉ lệ khung.
Phông cong liền (cyclorama) màu `background`, 3 đèn area (key trên-trái, fill phải yếu, rim sau),
View Transform AgX, look Medium High Contrast.

## Mẹo

- Dựng nhanh để kiểm bố cục: `--views iso,front --samples 16 --size 800x600` (vài giây/view).
- Ảnh chốt: `--engine cycles --samples 128` (chậm hơn, khử nhiễu tốt hơn).
- Chỉ render lại một view: `--views iso`.
- Object có Label bắt đầu bằng `_` hoặc đang ẩn trong FreeCAD sẽ bị bỏ qua.
- Không sửa/lưu file `.FCStd`: công cụ chỉ đọc model.
