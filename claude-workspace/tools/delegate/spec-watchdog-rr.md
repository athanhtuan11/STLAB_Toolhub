---
task: delegate-watchdog-roundrobin
cwd: tools/delegate
allow:
  - "delegate.py"
  - "README.md"
gate: 'python tests/test_watchdog_rr.py && python tests/test_stats.py && python tests/test_registry.py && python tests/test_delegate.py'
timeout_min: 30
max_rounds: 3
executor: copilot
---

# Mục tiêu
Cải tiến `delegate.py` (Tuan duyệt 2026-11-03): (1) **phát hiện treo** – OpenCode treo 20 phút không làm gì mà delegate vẫn
chờ tới hết timeout; (2) **chia việc xoay vòng** – Kilo gần như không được giao; (3) gate/executor **không kế thừa biến MSYS**
khi delegate được gọi từ Git Bash (ESP-IDF từ chối chạy → build không chạy → gate PASS giả).
Gate `tests/test_watchdog_rr.py` do Claude viết – **KHÔNG sửa tests/**. Giữ mọi hành vi cũ (các test cũ phải PASS).

# Yêu cầu
1. `recent_counts(days=7, root=None)`: đếm số vòng mỗi executor trong `root` (mặc định thư mục delegate-runs đang dùng,
   xem `run_roots()`), chỉ tính thư mục run có tiền tố ngày `YYYYMMDD-` trong `days` ngày gần nhất; mỗi file `<executor>-<n>.log`
   = 1 vòng. Trả dict.
2. `order_fair(queue, counts)`: sắp xếp ổn định theo số vòng tăng dần (thiếu = 0), bằng nhau giữ thứ tự gốc. Dùng khi
   `executor: auto` hoặc `ky_nang` (sau khi lọc mức dữ liệu, trước hạn mức); executor chỉ định thì giữ nguyên.
3. `run_proc_watch(argv, cwd, stdin, timeout_s, stall_s, watch_dir, env=None)` thay `run_proc` khi chạy **executor** (gate vẫn
   `run_proc`): `subprocess.Popen` (stdout+stderr gộp, đọc bằng luồng riêng không chặn), kiểm mỗi ≤ 2 s; "có tiến triển" = output
   mới HOẶC có file trong `watch_dir` (đệ quy, bỏ `.git`, `build`, `managed_components`, `node_modules`, `.delegate-tmp`) có
   mtime mới hơn lần tiến triển trước. Không tiến triển quá `stall_s` → dừng **cả cây tiến trình** (Windows: `taskkill /T /F /PID`;
   khác: kill process group), trả `(out + "\n[delegate] STALL <stall_s> s", -2, secs)`. Quá `timeout_s` → như cũ
   `(out + "\n[delegate] TIMEOUT ...", -1, secs)`. Trả `(out, returncode, secs)` khi xong.
4. Ngưỡng treo `STALL_MIN = float(os.environ.get("DELEGATE_STALL_MIN", "6"))` phút.
5. Trong `main`: khi executor trả -2 (STALL): `mark_limited(name, "stall <x> phut", until=now + 30 phut)`, ghi vào kết quả vòng
   `"stalled": true`, rồi **chuyển executor kế tiếp** theo thứ tự `org["order"]` (kể cả khi spec chỉ định executor – thêm các
   executor còn lại phía sau, bỏ người đang bị giới hạn). Thống kê `tally` đếm thêm `stalled`.
6. `clean_env(env=None)`: bản sao `os.environ` (hoặc env truyền vào) bỏ `MSYSTEM, MSYSTEM_PREFIX, MSYSTEM_CHOST, MINGW_PREFIX,
   MSYS, CHERE_INVOKING`. Dùng cho mọi lần chạy gate và executor.
7. `--status` in thêm `recent_7d` (kết quả `recent_counts`). README: thêm mục ngắn (tiếng Việt có dấu) về treo + xoay vòng.

# Không làm
- Không sửa `tests/`, `org/`, adapter executor. Không đổi định dạng spec.

# Tiêu chí PASS
- Gate exit 0.
