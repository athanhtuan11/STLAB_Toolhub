---
task: esp32-s3-cam-firmware-cam-v0.2-ui
cwd: maker/esp32-s3-cam/firmware/cam
allow:
  - "main/*"
  - "README.md"
gate: 'powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_cam.py && python check_ui.py'
executor: coder
---

# Mục tiêu
Firmware cam v0.1.0 (đã PASS test_cam.py + soak 20 phút trên mạch thật) → **v0.2.0**: thay trang `/` tạm bằng giao diện
theo mockup Tuan đã thấy `../../design/ui/cam-ui.html` (sáng/tối, desktop + điện thoại), nối dữ liệu thật. Không đổi phần
camera/stream/watchdog/nhiệt đã chạy ổn (chỉ thêm biến `rotate` và đổi version). Gate `check_cam.py`, `check_ui.py`,
`test_cam.py`, `build.ps1` do Claude viết – KHÔNG sửa.

# Giao diện (main/index.html, 1 file, không tài nguyên ngoài, ≤ 40 KB, tiếng Việt có dấu)
- Lấy bố cục, màu, chữ, chế độ sáng/tối (prefers-color-scheme) từ mockup; bỏ hình minh họa SVG, thay bằng
  `<img id="video">` có `src = http://<location.hostname>:81/stream`.
- Bảng "Kết nối": Wi-Fi nhà (sta_ssid), tín hiệu (sta_rssi dBm + chữ Tốt/Khá/Yếu: ≥ −60 / −60…−75 / < −75), IP, tên truy cập
  stlab-cam.local; "Chip": nhiệt °C + thanh màu: < 60 xanh, 60–70 vàng, ≥ 70 đỏ (2 ngưỡng là hằng số JS đầu file, ghi
  `// TODO Tuan chốt ngưỡng`), dòng "Đang hạ fps do nóng" khi `nong` = true; tốc độ hình (fps_thuc / fps_cai), độ phân giải,
  số người xem. Cập nhật `/status` mỗi 2 s; mất kết nối → chấm trạng thái đỏ "Mất kết nối", tự thử lại.
- Nút: **Chụp ảnh** (hiện ảnh /capture trong khung xem trước nhỏ), **Tải ảnh** (tải file `stlab-cam-YYYYMMDD-HHMMSS.jpg`;
  nếu rotate ≠ 0 thì xoay bằng canvas trước khi tải), **Lật 180°** (gửi vflip + hmirror cùng giá trị), **Xoay 90°**
  (vòng 0 → 90 → 180 → 270), chọn **độ phân giải** (QVGA 6, VGA 10, SVGA 11, XGA 12, HD 13 – số enum framesize_t),
  thanh trượt **Sáng / Tương phản** (−2..2), **fps** (1–25). Mỗi thay đổi gọi `/control`, lỗi → thông báo nhỏ.
- Xoay 90°/270° hiển thị bằng CSS transform, khung video giữ tỉ lệ đúng (không tràn, không méo) trên cả điện thoại.
- Khi người xem thứ 3 (stream trả 503): hiện "Đã đủ 2 người xem – thử lại sau" thay vì ảnh vỡ; nút "Thử lại".
- Không ghi mật khẩu, không form nhập Wi-Fi (Wi-Fi cài bằng wifi-setup.py).

# Firmware
- `/control?var=rotate&val=0|90|180|270` → lưu NVS `cam_cfg` (chỉ lưu, không xoay ảnh trên chip); sai → 400.
  `/status` thêm `rotate`. Mặc định 0.
- version "0.2.0" (đổi cả chuỗi trong `/status`).
- Trang `/` gửi kèm `Content-Encoding: gzip` nếu nén lúc build (tùy chọn; nếu làm thì gate vẫn phải đọc được index.html gốc).

# Không làm
Không đổi task camera, stream, watchdog, ngưỡng nhiệt firmware, Wi-Fi. Không sửa gate/test/build.ps1.

# Tiêu chí PASS
Gate exit 0. Claude nạp + `python test_cam.py --host 192.168.1.127` PASS + mở trang trên máy tính, chụp ảnh màn hình duyệt.
