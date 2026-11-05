# esp32-s3-cam – camera AI ESP32-S3 + OV3660

Dự án Tuan bắt đầu 2026-11-03. Mạch **ESP32-S3-CAM N16R8** (16 MB flash, 8 MB PSRAM octal, dạng giống ESP32-CAM, khe FPC 24 chân)
+ camera **WS-OV3660-8225N-40027** (OV3660 3 MP; ý nghĩa hậu tố 8225N/40027: TODO – chưa có nguồn).

## Mục tiêu (Tuan chọn cả 4)
1. Nhận diện AI trên chip (ESP-WHO / ESP-DL, TFLite Micro person detection, Edge Impulse).
2. Bài học STEAM / bộ kit bán (vỏ in 3D + firmware mẫu + giáo án).
3. Mắt robot (stream cho line-bot / tay máy CyberBrick).
4. Camera giám sát / smart home (ESPHome + Home Assistant).

## Đã biết (có nguồn – xem docs/research-notes/esp32-s3-cam-hardware.md)
- Không có sơ đồ chân chung cho "ESP32-S3-CAM N16R8": tùy hãng mạch. Bộ chân Freenove/GOOUUU: XCLK 15, SIOD 4, SIOC 5,
  D0–D7 = 11, 9, 8, 10, 12, 18, 17, 16, VSYNC 6, HREF 7, PCLK 13, PWDN/RESET −1 (chưa chắc cho mạch của Tuan).
- `espressif/esp32-camera` hỗ trợ OV3660 tới 2048 × 1536 (JPEG); cần PSRAM; ESP32-S3 2 MP chỉ ổn cho ảnh tĩnh JPEG.
- OV3660 cần nguồn 2,8 V (analog) + 1,5 V (lõi) – module camera tự có LDO (kiểm trên module).
- Dòng tiêu thụ khi stream, IC ổn áp trên mạch: TODO (đo/đọc mạch thật).

## An toàn
- Cấp nguồn USB-C 5 V. Camera + ESP32-S3 nóng khi stream lâu – không bọc kín vỏ không lỗ thoát nhiệt.
- Pin Li-ion 18650 (nếu dùng): chỉ cell có mạch bảo vệ + mạch tăng áp/sạc đúng dòng; chưa thiết kế phần pin.
- Cắm/rút cáp FPC camera khi đã rút nguồn; cáp FPC dễ gãy.

## Firmware
- `firmware/probe/` (ESP-IDF 5.5.4): dò chip/PSRAM/flash, thử bộ chân camera, đọc PID cảm biến, phát Wi-Fi AP
  `STLAB-CAM-xxxx` (mật khẩu in ra cổng serial, sinh từ MAC – không lưu trong mã) + trang xem hình.
  Build: `powershell -ExecutionPolicy Bypass -File build.ps1`; nạp + xem log: `flash.bat COMx`.
- Wi-Fi nhà (`main/wifi_nha.c`, chế độ AP+STA): `python wifi-setup.py --port COM6` tự lấy SSID + mật khẩu từ Windows, gửi qua
  UART, mạch lưu NVS → xem tại `http://stlab-cam.local`. Mật khẩu không nằm trong mã/file/log. Chỉ Wi-Fi 2,4 GHz.

## Kết quả dò phần cứng (2026-11-03, mạch thật của Tuan)
- Chip ESP32-S3R8 QFN56 rev v0.2 (hàn thẳng, không module), thạch anh 40 MHz; PSRAM 8 MB octal trong chip (AP gen 3,
  3 V, 80 MHz); flash 16 MB Boya (0x68/0x4018), DIO/QIO, 3,3 V; MAC 98:A3:16:EC:54:68.
- Nạp/log: cổng **mini USB → CH340 → UART0 (COM6)**, tự reset bằng RTS. USB native (GPIO19/20) có đi dây (demo xưởng chạy
  TinyUSB 303A:4001) – cổng nào: TODO. Đèn đỏ = nguồn; đèn xanh = **WS2812** (demo xưởng `led_strip`; chân: TODO).
- **Camera: bộ chân FREENOVE_GOOUUU đúng**, XCLK 20 MHz, OV3660 PID 0x3660 @ I2C 0x3C. SVGA JPEG ~19 KB/khung, 35 ms/khung.
- Chân đã chiếm: camera (4,5,6,7,8,9,10,11,12,13,15,16,17,18), PSRAM octal (35–37), UART0 (43/44), USB (19/20).
  Chân trống cho robot: TODO – đối chiếu header thật (ảnh mạch).
- Nhiệt chip lúc nghỉ 41–42 °C. Cảnh báo `NO-SOI` lúc Wi-Fi khởi động (vài khung hỏng) – theo dõi khi stream.
- Lưu ý build: esp32-camera mặc định driver I2C mới; probe quét I2C bằng driver cũ → đặt
  `CONFIG_SCCB_HARDWARE_I2C_DRIVER_LEGACY=y` (IDF 5.5 cấm trộn 2 driver → abort khởi động).

## Trạng thái
- 2026-11-05: **Vỏ in được 1 bàn, không support**: `solidcraft/plates/p2-enclosure/p2-enclosure.3mf` PASS (216 ph, 97,6 g). Sửa: vòng trang trí lõm
  Ø26 → rãnh rộng 1 (hết floating cantilever bezel); ray đỡ mạch + 4 chân góc kéo tới thành sau (hết support thân). Coupon
  `P1_Coupon.3mf` PASS. ASSEMBLY.md 8 bước + ảnh `solidcraft/render_assembly.py`. TODO: cổng USB đế nạp ở cạnh dưới?; đo nhiệt có vỏ.
- 2026-11-05: **Build nhanh** (spec-speed.md): mỗi chi tiết 1 script SolidCraft, cache theo sha256 lệnh, chạy song song, ghép
  `cam_d.sc` bằng insert_design. Build sạch 40 s (trước ~3 ph), không đổi 0,1 s, đổi 1 thông số bezel ~20 s; gate 9/9 dùng
  build-report.json (2 s). Lỗ ống kính chốt 15,0 mm.
- 2026-11-05: **Ống kính đo thật:** khay thẻ nhớ → đỉnh đế ống kính 8,5 mm; ống kính xoay chỉnh nét Ø14, khay thẻ → đầu ống kính
  20–22 mm. Tuan chọn **ống kính nhô ra ngoài vỏ** (~10 mm, chỉnh nét từ ngoài): mạch lùi 2,5 mm, đế ống kính cách mặt trong bezel
  0,5 mm, ống kính chui lỗ 14,6 (0,3/bên). Gate 7/7 PASS (thêm test ống kính chui lỗ). Tâm ống kính cách mép trên 9,4 = tâm khay thẻ TF (camera dán lên khay thẻ – Tuan xác nhận).
- 2026-11-05: **Lỗ ống kính sửa 8,3 → 14,6 mm** (Tuan: ống kính OV3660 ~14 mm; 8,3 là vỏ ESP32-CAM OV2640 – sai). Coupon thử
  14,2/14,6/15,0. **Bảng khe lắp (nhựa PETG co ngót – luôn có khe):** mạch 27 × 40 → hốc 27,6 × 40,6 (0,3/bên); khối cao 18
  → gờ sau +0,3; ống kính 14 → 14,6 (0,3/bên); M3 xuyên 3,4; đai ốc M3 s 5,5 → 5,8; M2.5 tự ren 2,2 / xuyên 2,8; chốt xoay
  Ø8 / lỗ 8,4 (0,2/bên theo tipflow – thử Coupon, lỏng chặt chọn lại); tay U – thân 0,6; nắp chốt khe dọc 0,2.
  **TODO đo:** ống kính cao bao nhiêu mm trên mặt mạch (quyết định khoảng mạch – bezel, hiện ước 6).
- 2026-11-05: **CAD chuyển hẳn sang SolidCraft 0.30.1** (Tuan quyết). Nguồn: `solidcraft/params.json` + `build_cam_d.py`
  (sinh `cam_d.json` → `cam_d.sc` mở bằng SolidCraft, xuất `stl/` hướng in, ~3 ph) + gate `python tests/test_build.py` 6/6 PASS
  (thể tích ±1 %, bao ±0,05 mm so bản FreeCAD). Cắt lớp: `tools/robotics-cad/scripts/slice.py solidcraft/print/print.yaml`.
  Né lỗi nhân truck: lỗ côn `top_radius` −0,3; trụ vít Body join d −0,1 (tiếp tuyến thành). FreeCAD cũ → `backup/20261105-freecad-cu/`.
  Coupon PASS (22 ph, 7,7 g); vỏ vẫn FAIL bezel floating cantilever (TODO), body 4 vùng support 12 × 6 mm ở z 12,5.
- 2026-11-05: **Tuan đo mạch thật 27 × 40 × 18 mm** (18 = cả đế nạp CH340, chưa tính camera) → params `pcb_h` 40,0, `stack_t` 18,0;
  ống kính Ø8,3 / cách cạnh 9,4 / cam ≤ 7,7 mm vẫn lấy từ ESP32_CAM_CASE.step. Build lại, gate 11/11 PASS, Coupon cắt lớp PASS
  (22 ph, 7,7 g; khung thử 27,6 × 40,6). Vỏ: bezel bị Bambu báo floating cantilever (TODO sửa), body cần tô support 4 vùng
  12 × 6 mm ở z 8,5. Chờ Tuan chọn cỡ Coupon → sửa params + bezel → in vỏ.
- 2026-11-03: **CAD mẫu D** `freecad/` (params.json + scripts/build_cam_d.py + gate tests/test_build.py 11/11 PASS):
  Body, Bezel, U_frame (liền đĩa xoay), Base, Pin_cap + Coupon/Coupon_ring; STL hướng in ở `freecad/scripts/stl/`.
  Số mạch lấy cộng đồng (chưa đo) → **in Coupon trước** (M3 3,3/3,4/3,5; đai ốc 5,6/5,8/6,0; ống kính 8,3/8,6/9,0; da đèn
  0,4/0,6; chốt Ø8 + vòng 8,4; khung thử mạch 27,6 × 41,1) → Tuan chọn cỡ → sửa params → in vỏ. Vít: 4 × M2.5 tự ren (mặt trước),
  2 × M3×12 + đai ốc (trục nghiêng), 1 × M2.5 (nắp chốt). Vị trí đèn trên mạch thật: TODO.
- 2026-11-03: **firmware chính `firmware/cam` v0.1.0** chạy trên mạch thật – test_cam.py PASS (xem + chụp cùng lúc, đóng tab
  đột ngột ×5 không kẹt, tối đa 2 người xem, /control đổi độ phân giải), chạy video 20 phút: 0 lỗi, 10 fps, nhiệt tăng
  65,8 → 69,8 °C rồi tự hạ 5 fps (về 66,8 °C). **Mạch trần đã gần 70 °C → vỏ bắt buộc khe đối lưu; đo lại khi lắp vỏ.**
  Ảnh nằm nghiêng 90° (camera xoay 90° so với mạch) – chốt chiều khi CAD. Dáng: 2 mẫu – để bàn (D, đế xoay) + treo tường
  (W), chung hộp + khung U, tilt vít M3 (design/). Thứ tự Tuan chốt: code → test → mới CAD (số mạch lấy cộng đồng).
- 2026-11-03: Wi-Fi nhà chạy trên mạch thật: vào `VIETTEL_Suong` (2,4 GHz) IP 192.168.1.127, RSSI −46…−58 dBm, reset tự vào lại
  ~6,5 s, mDNS `stlab-cam.local` OK, stream SVGA ~18 fps (~570 KB/s) qua mạng nhà. Tiếp: Tuan xem hình → nhiệt khi stream lâu
  → bước 0 dáng vỏ + UI web.
- 2026-11-03: firmware dò chạy trên mạch thật. Tiếp: Tuan xem hình qua AP → đo fps stream/nhiệt khi chạy lâu → bước 0 dáng
  vỏ + giao diện web → chọn thứ tự 4 hướng.
