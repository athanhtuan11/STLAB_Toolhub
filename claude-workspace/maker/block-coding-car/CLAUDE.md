# block-coding-car – xe ESP32-S3 lập trình kéo thả kiểu ScratchJr cho bé lớp 1

Tuan bắt đầu 2026-11-16. Bé (lớp 1, 6–7 tuổi) kéo thả khối lệnh bằng hình trên máy tính → bấm Chạy → **xe thật** chạy trên thảm ô.
Thiết kế mới của STLab – tham khảo cách học của ScratchJr (khối icon ngang), KHÔNG chép giao diện/nhân vật/icon của ScratchJr.
Kế hoạch đã duyệt: `C:\Users\hoang\.claude\plans\l-n-d-n-robotics-fizzy-pearl.md` (tóm tắt ở README).

## Đã chốt (2026-11-16)
- Bo **ESP32-S3 N16R8 DevKit**; **2 × 28BYJ-48 5 V + ULN2003**; pin **4 × AA NiMH** hộp khóa vít (không Li-ion).
- Kết nối **Wi-Fi lab**, xe tự phục vụ app web (`robot-<màu>.local`, websocket `/ws`), không cài phần mềm.
- Dùng chung thông số thân xe/thảm ô 150 mm với `maker/card-coding-robot/` (Cú con – tạm dừng).
- Firmware ESP-IDF (chuẩn repo). App HTML/JS thuần nhúng flash. Chương trình = JSON danh sách khối, xe thông dịch.

## Bước 0 – Giao diện – `design/` (làm TRƯỚC)
- `brief.md` → 3 dáng xe (`concepts/`) + 3 bố cục app (`ui-mockups/`) + `cmf.png` → `contact-sheet.png` → Tuan chọn bằng ảnh.
- Chưa chọn thì chưa làm cơ khí/firmware/app thật.

## Cấu trúc
`design/` · `app/` (web kéo thả + mô phỏng) · `firmware/` (ESP-IDF) · `hardware/` (wiring.yaml, BOM) · `solidcraft/` · `print/` · `lessons/` · `docs/`.

## An toàn
- Trẻ 6–7: không chi tiết rời nhỏ, vít không lộ, bánh giấu, hộp pin mở bằng tua vít, NiMH. Firmware nhả cuộn stepper khi đứng yên.
- Nguồn: LDO DevKitC-1 v1.1 (SGM2212) tối đa 5,5 V, chân 5V nối thẳng LDO → **bắt buộc buck-boost 5 V**, không cấp pin thẳng. Không cắm USB khi pin bật (`hardware/BOM.md`).

## Trạng thái
- 2026-11-16: bước 0 xong – Tuan chọn **dáng A Xe hộp mặt cười + app U1**, bộ khối rút gọn, nút Dừng luôn đỏ. Giai đoạn 1 xong (giấy): `hardware/BOM.md`, `hardware/wiring.yaml` (render Toolhub OK), parts-library + 28BYJ-48/ULN2003. Tiếp: Tuan mua linh kiện; giai đoạn 2 firmware + 3 app làm song song được.
- 2026-11-16: GĐ2 firmware v0.1 + GĐ3 app v0.1 PASS (chưa thử mạch). **Đổi ngữ nghĩa khối → sửa `protocol/PROTOCOL.md` + `make_golden.py` trước**, rồi chạy lại 2 gate: `firmware/car`: `..\.venv-host\Scripts\python.exe -m pytest -q tests` + `build.ps1`; `app`: `node --test "tests/*.test.mjs"`. Tiếp: Tuan duyệt ảnh app, mua linh kiện → nạp USB lần đầu, hiệu chỉnh `cal`; GĐ4 CAD.
- 2026-11-16: GĐ4 CAD v1 PASS – `solidcraft/build_car.py` + `params.json` (nguồn số), gate `solidcraft/tests/test_build.py` (`--no-slice` khi lặp). Đổi hình học bánh/vết → tính lại `steps_90` trong PROTOCOL + firmware. Chờ Tuan in thử bàn p1–p6 + đo hàng thật (hộp 4×AA, MX, O-ring, loa, ULN2003).
