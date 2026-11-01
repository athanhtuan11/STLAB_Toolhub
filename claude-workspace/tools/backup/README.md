# backup – sao lưu file FreeCAD

File `.FCStd` trong `maker/` bị gitignore, chỉ có trên máy. `backup_fcstd.py` chép chúng ra **G:** (HDD USB) và
**OneDrive** (Tuan chọn 2026-11-01), so sánh bằng SHA-256, chỉ chép file đã đổi.

## Cấu hình – `backup.json`
- `source_root`: gốc tính từ thư mục script (`../..` = claude-workspace); `include`: glob tính từ gốc.
- `destinations`: thư mục đích, cho phép `%USERPROFILE%`. Đích mất (rút ổ USB) → bỏ qua, không tự tạo ổ.
- `keep_versions`: số bản cũ giữ cho mỗi file (mặc định 7).
- Biến môi trường: `STLAB_BACKUP_CONFIG` (file cấu hình khác), `STLAB_BACKUP_STATE` (chỗ ghi `last.json`,
  mặc định `%LOCALAPPDATA%\stlab-backup`).

## Cấu trúc đích
- `<đích>/current/<đường dẫn>`: bản mới nhất.
- `<đích>/versions/<thư mục>/<tên>.<YYYYmmdd-HHMMSS>.FCStd`: bản cũ. File nguồn bị xóa thì bản sao lưu vẫn giữ.

## Khôi phục một file
Đóng FreeCAD, chép file từ `current/` (hoặc bản cũ trong `versions/`, bỏ phần ngày trong tên) về đúng chỗ trong `maker/`.

## Lịch chạy
- Đăng ký: `powershell -ExecutionPolicy Bypass -File tools\backup\register-tasks.ps1`
  → `STLab-Backup-FCStd` (21:00 hằng ngày) + `STLab-Community-Check` (Chủ nhật 09:00, chỉ kiểm, không apply).
- Gỡ: thêm `-Unregister`. Chạy tay: `python tools\backup\backup_fcstd.py`.

Kiểm: `python tools/backup/tests/test_backup.py` (chỉ dùng thư mục tạm).
