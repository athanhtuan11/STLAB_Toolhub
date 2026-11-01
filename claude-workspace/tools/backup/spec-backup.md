---
task: backup-fcstd
cwd: tools/backup
allow:
  - "backup_fcstd.py"
  - "backup.json"
  - "register-tasks.ps1"
  - "README.md"
gate: "python tests/test_backup.py"
timeout_min: 20
max_rounds: 2
executor: auto
---

# Mục tiêu
Sao lưu mọi file `.FCStd` của `claude-workspace/maker/` (chỉ có trên máy, bị gitignore) ra ổ G: (HDD USB) và OneDrive,
giữ vài bản cũ. Chạy hằng ngày bằng Task Scheduler (Tuan duyệt 2026-11-01).

# Đầu vào
- Gate `tests/test_backup.py` (Claude viết, KHÔNG sửa) – đọc kỹ, nó là đặc tả chính xác.

# Yêu cầu
- `backup_fcstd.py`: chỉ stdlib Python 3.11+. Đọc cấu hình JSON từ biến `STLAB_BACKUP_CONFIG`, mặc định `backup.json`
  cạnh script. Khóa: `source_root` (tương đối theo thư mục script hoặc tuyệt đối; giá trị trong `backup.json` = `../..`
  tức claude-workspace), `include` (glob kiểu `Path.glob`, tương đối theo `source_root`), `destinations` (danh sách,
  cho phép biến môi trường kiểu `%USERPROFILE%` – dùng `os.path.expandvars`), `keep_versions` (số nguyên).
- `backup.json` mặc định: `include: ["maker/**/*.FCStd"]`, `destinations: ["G:/stlab-backup/fcstd",
  "%USERPROFILE%/OneDrive/stlab-backup/fcstd"]`, `keep_versions: 7`.
- Mỗi đích: coi là **có** nếu thư mục đích đã tồn tại HOẶC thư mục cha của nó tồn tại (khi đó tạo thư mục đích).
  Ngược lại status `missing`, bỏ qua, KHÔNG tạo thư mục nào.
- Cấu trúc đích: `<dest>/current/<relpath>` (bản mới nhất), `<dest>/versions/<reldir>/<stem>.<YYYYmmdd-HHMMSS>.FCStd`.
- So sánh bằng sha256 (không chỉ kích thước/mtime). File đổi: chuyển bản `current` cũ vào `versions/` rồi chép bản mới.
  Chép qua file tạm cùng thư mục rồi `os.replace`; kiểm sha256 sau khi chép; lỗi → status `error` cho đích đó.
- Giữ tối đa `keep_versions` bản cũ mỗi file (xóa bản cũ nhất). File nguồn bị xóa: **không** xóa gì ở đích.
- In một dòng JSON cuối: `{"time", "copied", "unchanged", "versions_pruned", "destinations": [{"path", "status"
  (ok|missing|error), "copied", "error"?}]}`. `copied`/`unchanged` đếm theo file nguồn (đổi ở ít nhất một đích = copied).
- Ghi cùng JSON vào `<STLAB_BACKUP_STATE>/last.json`, mặc định `%LOCALAPPDATA%/stlab-backup/last.json`.
- Exit 0 nếu ít nhất một đích `ok`, ngược lại exit 1.
- `register-tasks.ps1` (PowerShell 5.1, ASCII, idempotent – chạy lại thì cập nhật, `-Force`): đăng ký 2 tác vụ cho user
  hiện tại, chỉ khi đăng nhập, `StartWhenAvailable`, không cần quyền admin:
  - `STLab-Backup-FCStd`: hằng ngày 21:00, chạy `python.exe backup_fcstd.py` (đường dẫn python lấy từ `(Get-Command
    python).Source` lúc đăng ký), thư mục làm việc = thư mục script.
  - `STLab-Community-Check`: Chủ nhật 09:00, chạy `bash.exe community/update-community.sh check` (bash của Git for
    Windows: `C:\Program Files\Git\bin\bash.exe`), thư mục làm việc = claude-workspace.
  Tham số `-Unregister` gỡ cả hai. Script KHÔNG tự chạy khi import; in tên tác vụ + lần chạy tới.
- `README.md` ngắn (tiếng Việt): làm gì, cấu hình, khôi phục 1 file (chép từ `current/` hoặc `versions/`), đăng ký/gỡ lịch.

# Không làm
- Không chạy `register-tasks.ps1`, không chạy backup thật (Claude làm sau khi duyệt).
- Không sửa `tests/`, không đụng file ngoài `tools/backup/`.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự đọc lại `register-tasks.ps1` trước khi chạy.
