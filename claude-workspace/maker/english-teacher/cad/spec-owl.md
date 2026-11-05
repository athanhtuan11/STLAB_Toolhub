# spec-owl – CAD vỏ "Cú Bông" bản 1 (ESP32-A1S Audio Kit), Blender bpy

> **Đổi 2026-11-05 (Tuan): 2 loa trái + phải** Ø52 × 26 ở 2 bên sườn dưới cánh, lưới trên vỏ sườn; tấm bụng không còn lưới loa.
> params `speakers` = 2 mục {center, axis}; gate_owl.py đã cập nhật.

cwd: `maker/english-teacher/cad`
allow: `build_owl.py`, `out/**`, `README.md`
Không sửa: `gate_owl.py`. Không tạo/sửa `print.yaml` (Tuan duyệt sau).
gate: `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl.py -- out && "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl.py -- out`

## Đầu vào
- Dáng đã duyệt: `../design/design-spec.md` mục 2 + mục 4A, ảnh `../design/concepts/a-cu-bong-*.png`, mô hình hình khối trong `../design/make_concepts.py`
  (dùng lại hàm dựng dáng ngoài nếu được – chỉ là dáng, phải làm thành khối in được).
- Linh kiện (`../CLAUDE.md`): bo Audio Kit **82 × 73 mm** (datasheet; độ dày/chiều cao linh kiện không có nguồn → khối giữ chỗ **82 × 73 × 25**),
  loa **Ø52 × 26 mm** (Tuan đo), cổng USB của bo: vị trí không có nguồn → **khe cáp rộng 40 × 12 mm ở chân lưng** (đủ cho cả 2 cổng micro-USB dù lệch).
- Khe lắp (PETG, bảng dự án esp32-s3-cam đã dùng): khe 0,3 mm/bên cho hốc linh kiện; M3 xuyên **3,4**; đai ốc M3 lục giác **5,8** (dẹt 2,4 → hốc sâu 2,8);
  khe trượt rãnh–gờ 0,2/bên. fit-library chưa có mục M3 → ghi chú "chưa in thử" trong README.

## Chi tiết (STL đặt sẵn hướng in, mặt lớn xuống z = 0, đơn vị mm)
| File | Màu | Ghi chú |
|---|---|---|
| `shell-front.stl` | mơ | nửa trước thân (tai, cánh liền), lỗ bụng nhận tấm bụng, 2 lỗ mắt, lỗ mỏ; in **mặt ráp xuống bàn** |
| `shell-back.stl` | mơ | nửa sau; 5 khe nhiệt 2 × 18; khe cáp USB 40 × 12 ở chân; **ray đứng giữ bo** (rãnh rộng 2,4 cho PCB, khe 0,3/bên theo 82 × 73); lỗ nút Ø50,8 trên đỉnh nằm trên đường ráp hoặc trọn ở nửa sau; 3 lỗ micro Ø2 ở trán (cách tâm loa ≥ 60) |
| `belly.stl` | kem | tấm bụng ~94 × 88, lưới loa Ø56 lỗ Ø2,8 bước 5,6 (lỗ cách mép ≥ 3), hốc loa Ø52,6 sâu đủ, 3–4 vấu ép giữ vành loa; lắp từ trong, bắt 2 vít M3 hoặc gờ khóa |
| `beak.stl` | bơ | mỏ, cài từ trong (gờ + khe 0,2/bên), không thể rút ra từ ngoài |
| `button-cap.stl` | bơ | nắp nút Ø50 × 12 có vành giữ trong (không rơi ra ngoài), hành trình ~2 mm, chân ép công tắc tactile 6 × 6 (đế công tắc trên giá trong nửa sau) |
| `eye-diffuser.stl` | trắng tự nhiên | 1 file in 2 cái: cửa sổ Ø34 dày **0,8** + vành giữ lắp từ trong; sau nó là chỗ gắn LED RGB (WS2812 5 mm hoặc module tròn – giá đỡ rộng) |
| `owl-assembled.stl` | – | toàn bộ ở vị trí lắp (gate dùng để kiểm kích thước + va chạm) |

Ghép 2 nửa: gờ–rãnh dọc toàn đường ráp (khe 0,2/bên) + **4 vít M3 từ đáy** (lỗ lõm Ø9 sâu 6 dưới miếng cao su Ø16, xuyên 3,4 ở nửa này, hốc đai ốc 5,8 ở nửa kia
hoặc trụ ở nửa sau) – vít/đai ốc không lộ khi đã dán cao su. Cạnh ngoài bo R ≥ 3 (vùng cầm ≥ 8), không chi tiết nhô < Ø20, không khe ngoài > 4 mm
(trừ khe cáp ở chân lưng, sát mặt bàn). Thành 2,4. In không support: mặt nghiêng ≥ 45°, cầu ≤ 15 mm; ghi vùng nào còn nghi ngờ vào README.

## out/owl-params.json (gate đọc – đúng tên khóa)
`wall 2.4, speaker_pocket_d 52.6, grille_hole_d 2.8, mic_hole_d 2.0, m3_clear_d 3.4, m3_nut_s 5.8, button_cap_d 50.0, button_hole_d 50.8,
diffuser_t 0.8, vent_w 2.0, speaker_center [x,y,z], pcb_center [x,y,z], pcb_box [dx,dy,dz]` – toạ độ trong hệ lắp ráp của `owl-assembled.stl`
(loa quay mặt ra trước theo −Y; pcb_box là 82/73/25 theo trục thực tế đặt bo, bo dựng đứng sau loa). Kèm mọi số khác đặt ở đầu `build_owl.py`.

## Ảnh duyệt
`out/owl-preview.png` (Eevee/Cycles thấp, 1600 × 1200: 3/4 trước + lưng thấy khe cáp) và `out/owl-exploded.png` (tách rời thấy loa, bo giữ chỗ, nút, mắt).
Màu theo design-spec. Tự xem ảnh, sửa nếu sai dáng so với concept.

## Không làm
Không print.yaml/cắt lớp/3mf (sáng mai cùng Tuan), không support vẽ vào STL, không đổi kích thước dáng ngoài quá ±6 mm so với 142 × 116 × 175.
