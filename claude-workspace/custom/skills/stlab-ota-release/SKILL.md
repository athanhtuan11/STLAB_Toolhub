---
name: stlab-ota-release
description: Phat hanh firmware ESP32 qua OTA cho thiet bi cua khach STLab (hien tai maker/pump-control, RainMaker) bang firmware/release.ps1. Dung ngay sau khi sua firmware xong va build/test PASS, khi Tuan noi "phat hanh", "cap nhat cho khach", "day ban moi". KHONG bao Tuan nap USB.
---

# Phát hành firmware OTA (Tuan chốt 2026-10-29)

Áp dụng: `maker/pump-control/firmware` (ESP32-D + RainMaker). Dự án khác có `firmware/release.ps1` cùng kiểu thì dùng
y như vậy.

## An toàn trước khi phát hành
- Thiết bị điều khiển **máy bơm 220 V / 2 HP** của khách: bản mới phải giữ nguyên logic an toàn đã chốt
  (vd `PUMP_MIN_OFF_S` = 5 s chống bật/tắt liên tục). Đổi hành vi bật/tắt → nêu rủi ro cho Tuan trước.
- Build `idf.py build` PASS trước. Firmware không chứa mật khẩu/khóa (repo releases là PUBLIC).

## Các bước
1. Commit mã nguồn firmware trước (qua `git-scribe`).
2. Chạy (Claude tự chạy, không bảo Tuan):
   `powershell -ExecutionPolicy Bypass -File maker/pump-control/firmware/release.ps1 -Version x.y.z -Notes "..."`
   - `x.y.z` phải **lớn hơn** bản cũ; KHÔNG tự sửa `PROJECT_VER` trước (script tự ghi, từ chối nếu không lớn hơn).
   - `Notes` ≤ 80 ký tự, không dấu (hiện ở ô "Ban moi" trên app).
   - Script: ghi `PROJECT_VER` → build → chép `.bin` + `manifest.json` vào `releases/` → commit + push.
3. Báo Tuan: bản x.y.z đã đăng; thiết bị thấy bản mới trong ≤ 6 giờ hoặc sau khởi động lại → khách bấm "Cap nhat".
   Bản lỗi không lên được cloud → sau 90 s tự quay về bản cũ.
4. Cập nhật memory `pump-control` (phiên bản hiện tại + thay đổi).

## Không làm
- Không bảo nạp USB. `flash.ps1` chỉ cho ESP32 mới hoặc cứu khi OTA hỏng.
- Không đăng bản chưa build/test.
