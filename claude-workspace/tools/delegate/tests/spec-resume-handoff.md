---
task: delegate-resume-handoff
cwd: tools/delegate
allow: ["delegate.py"]
gate: "python tests/test_delegate.py"
timeout_min: 15
max_rounds: 2
executor: opencode
---

# Mục tiêu
Thêm 3 cải tiến vào `delegate.py` (Claude đã duyệt, xem `../../docs/reports/agent-orchestration-ai-memory-ruflo.md` mục 6).
Giữ nguyên phong cách: chú thích tiếng Việt không dấu, gọn, không thêm thư viện ngoài (stdlib + yaml).

# Yêu cầu
1. `run_states()`: run không có `result.json` mà không có/thiếu pid trong `state.json` → tìm trong các file
   `USAGE/locks/*.json` khóa có `run_dir` trùng run đó; pid khóa còn sống (`pid_alive`) → `running`, ngược lại `interrupted`.
2. Hàm `build_resume(run_dir) -> (spec_path, context)`:
   - `run_dir` có thể là đường dẫn đầy đủ hoặc tên thư mục trong `USAGE/delegate-runs/`.
   - Không tồn tại → `ValueError`; đã có `result.json` → `ValueError` ("run da xong"); `state.json` thiếu `spec` → `ValueError`.
   - `context`: đuôi (~40 dòng) log executor vòng cuối (`<executor>-N.log`, N lớn nhất) + đuôi `gate-N.log` nếu có,
     có tiêu đề rõ "Lần chạy trước bị cắt ngang".
   - CLI `--resume <run>`: lỗi → in lỗi, exit 1. Hợp lệ → chạy lại spec như bình thường (khóa, run_dir MỚI), prompt vòng 1
     thêm `context` vào cuối; `result.json` có thêm `resumed_from` = tên run cũ.
3. Hàm `write_handoff(run_dir, result)`: ghi `run_dir/handoff.md` (tiếng Việt) gồm task, verdict, từng vòng (executor,
   số giây, `last_line`, `gate_exit`, `gate_tail`), `changed`, `forbidden_touched`, `outside_allow`, và 1 dòng
   "Bước tiếp: `python tools/delegate/delegate.py --resume <ten run>` hoặc Claude sửa spec". `run_task` gọi hàm này khi
   verdict khác PASS (trước khi in JSON cuối), và đưa đường dẫn handoff vào `result["handoff"]`.
- `--status` hiện có vẫn chạy; thêm vào header đầu file 1–2 dòng mô tả `--resume`, `handoff.md`.

# Không làm
- Không sửa `tests/`, `selftest/`, `opencode.json`, `README.md`. Không đổi thứ tự executor, regex 429, FORBIDDEN.
