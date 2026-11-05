# Spec: chuyển vỏ camera mẫu D từ FreeCAD sang SolidCraft (Claude, 2026-11-05)

Tuan quyết định: dự án esp32-s3-cam dùng **SolidCraft 0.30.1** (`C:\Program Files\SolidCraft\solidcraft-cli.exe`) thay FreeCAD.

## Việc
Viết `solidcraft/build_cam_d.py` (Python thường, không import FreeCAD):
1. Đọc `solidcraft/params.json` (cùng thư mục). Không viết số cứng của mạch/vỏ – mọi số lấy từ params (hằng hình học nhỏ
   có sẵn trong bản FreeCAD như 0,5 / 1,5 / -21, -17.5 … được giữ nguyên).
2. Sinh script SolidCraft `cam_d.json` (`{"commands":[{"command","params"}]}`) dựng **đúng hình học** của
   `../freecad/scripts/build_cam_d.py` (bản FreeCAD = chuẩn): body `Body, Bezel, U_frame, Base, Pin_cap, Coupon,
   Coupon_ring` + body tham chiếu `Ref_Stack, Ref_Cam` (hộp, như FreeCAD). Bỏ Ref_Screw_L/R.
3. Chạy `solidcraft-cli run cam_d.json --save cam_d.sc` (thư mục ra = biến môi trường `CAMD_OUT`, mặc định thư mục
   `solidcraft/`), rồi xuất 7 STL theo hướng in vào `<out>/stl/<label viết thường>.stl`:
   body nằm mặt sau xuống (xoay X −90°), bezel mặt trước xuống (xoay X +90°), còn lại giữ nguyên; tịnh tiến zmin = 0.
   Cách xuất: tùy chọn – vd. script thứ 2 chạy `--in cam_d.sc` với `solid.move` (xoay) + `file.export_stl`
   `{path, bodies:[...], quality: fine}` rồi không lưu, hoặc xoay STL bằng numpy. Ref_* không xuất STL.
4. Exit ≠ 0 nếu bước nào lỗi; in `CAMD OK` khi xong.

## Mẫu đã chạy được (Claude thử, `solidcraft/probe/`)
- `gen_coupon.py`: Coupon + Coupon_ring đầy đủ (lục giác = `sketch.polygon.inscribed` + `solid.extrude` cut; chữ số
  = `sketch.text` font arialbd.ttf + extrude cut) – thể tích 9 548,5 vs FreeCAD 9 554,2 mm³. Chữ số bản FreeCAD đặt
  **tâm** chữ tại (x, yy) – sửa cho khớp.
- `gen_hard.py`: Bezel đầy đủ (10 188,4 vs 10 191,8), đế tiện xoay (`solid.revolve` quanh Z, chưa cắt lõm/chốt/lỗ),
  tay U có bo R3 (`solid.fillet` chọn cạnh bằng điểm trên cạnh).
- Mặt phẳng phác thảo XZ tùy ý: `{"origin":[0,y,0],"x_dir":[1,0,0],"y_dir":[0,0,1]}` → pháp tuyến −Y.
- Hình hộp bo góc (rrect của cad_lib) = `sketch.rectangle.rounded` + `solid.extrude`. Lỗ = `solid.cylinder`
  `operation: cut, targets:[body]`, trục `axis` X/Y/Z hoặc vector.

## Lỗi nhân đã biết (truck)
- Cắt lỗ côn (countersink) **trùng trục + trùng bán kính** với lỗ trụ → `boolean Cut: no result`. Né: côn có
  `top_radius = r_lo - 0.3`, `height` cộng 0,3 (cùng góc 45°), cắt côn trước rồi lỗ trụ sau. Áp dụng cho lỗ khóa đế
  (`lo_khoa_dau_d` → `lo_khoa_d`) và bezel.
- Lỗi tương tự với mặt trùng nhau khác: kéo dài dụng cụ cắt 0,1 mm ra ngoài (như FreeCAD đã làm) hoặc lệch nhỏ ≤ 0,05 mm,
  ghi chú lý do trong code.
- Bo R2 của đế: dùng cung thật (`sketch.arc.center_point`), không cần xấp xỉ 8 đoạn như FreeCAD.

## Gate (KHÔNG sửa)
`python tests/test_build.py` (chạy từ `solidcraft/`) – thể tích ±1 %, hộp bao ±0,05 mm so với FreeCAD, 1 shell kín,
STL đúng hướng in, không số cứng. PASS hết mới báo xong.

## Không làm
Không sửa `params.json`, `tests/`, thư mục `../freecad/`, file dự án khác. Không vẽ support. Không thêm chi tiết mới.
