# Ảnh sản phẩm chân thực – esp32-s3-cam mẫu D (cho reel 30 s dọc)

7 ảnh 1188×2112 (9:16 rộng hơn 10 %; cắt giữa 1080×1920 vẫn chừa trên ≥160 px, dưới ≥420 px cho chữ). Dựng bằng Blender 5.2 Cycles
(GPU GTX 1660 Super, OPTIX), KHÔNG dùng AI tạo ảnh.

| Ảnh | Nội dung | Thời gian render (160–200 mẫu, full) |
|---|---|---|
| k01-macro-lens.png | macro ống kính, DOF nông, vệt sáng trên kính | 86 s |
| k02-desk-hero.png | 3/4 trước, bàn gỗ, nắng cửa sổ | 63 s |
| k03a-exploded.png | tách rời theo trục lắp (đế, khung U+đĩa, nắp chốt, hộp, mạch, mặt trước) | 58 s |
| k03b-assembled.png | cùng góc máy, đã lắp | 51 s |
| k04-shelf-room.png | trên kệ nhìn ra phòng học | 78 s |
| k05-tilt-pan.png | ngang tầm, nghiêng 20° + xoay 30° | 57 s |
| k06-low-hero.png | góc thấp, cảnh kết | 55 s |

Hậu kỳ (compositor, ~3 s/ảnh): glare nhẹ, màu ấm, vignette, sharpen nhẹ, hạt phim. `raw/` = bản thô (EXR 16-bit + PNG AgX, chưa hậu kỳ).

## Chạy lại
`python render_stills.py all` | `render k02 [--samples N --scale 0.5]` | `post` (chỉ hậu kỳ lại từ raw) | `sheet` | `cad`.
Đổi màu nhựa: các biến `COL_*` đầu `render_stills.py` (TODO: Tuan chưa báo màu cuộn; tạm theo concept D).

## Hình học
Mesh ở vị trí lắp xuất từ `solidcraft/cam_d.sc` bằng `solidcraft-cli file.export_stl` → `assets/cad/*.stl` (Body, Bezel, U_frame, Base,
Pin_cap, Ref_Stack = hộp mạch 27×40×18 xanh, Ref_Cam = ống kính Ø14). Không thêm/bớt chi tiết. Phần thêm CHỈ ở shader: mặt kính
ống kính (inset + lõm 0,6 mm trong mesh để có vòng kim loại đen + kính). Pan quanh Z gốc; tilt quanh trục X qua z = 64 mm.

## Nguồn / license (CC0)
- HDRI `kloofendal_misty_morning_puresky_2k` – Greg Zaal, Poly Haven, CC0 (https://polyhaven.com/a/kloofendal_misty_morning_puresky).
- Texture gỗ `wood_table_001` 2k (diff, rough, nor_gl) – Dimitrios Savva (ảnh) / Rico Cilliers (xử lý), Poly Haven, CC0.
- Vật phụ (sách, cốc, bút chì, ghế, bàn, cửa sổ) dựng procedural trong script, không chữ/thương hiệu.
