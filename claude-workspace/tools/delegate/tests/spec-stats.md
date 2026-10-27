---
task: delegate-stats
cwd: tools/delegate
allow: ["delegate.py"]
gate: "python tests/test_stats.py && python tests/test_registry.py && python tests/test_delegate.py"
timeout_min: 20
max_rounds: 2
executor: opencode
---

# Mục tiêu
Bước 3 sổ nhân sự: `delegate.py` ghi thành tích từng executor để Claude/Tuan đánh giá "nhân viên" và (tùy chọn) ưu tiên
người làm tốt. Giữ phong cách file (chú thích tiếng Việt không dấu), stdlib + yaml. Đọc `tests/test_stats.py` để biết đúng định nghĩa.

# Yêu cầu
1. File `USAGE/agent-stats.json`: {executor: {rounds, gate_pass, pass_round1, limited, escalate, seconds}}.
   - `rounds`: số vòng KHÔNG bị `limited` của executor đó; `gate_pass`: vòng có `gate_exit == 0`;
     `pass_round1`: run mà vòng 1 do executor đó chạy và `gate_exit == 0`; `limited`: vòng có `limited` true;
     `escalate`: run có verdict `ESCALATE` mà vòng cuối do executor đó chạy; `seconds`: tổng giây các vòng không limited.
2. `update_stats(result)`: cộng dồn 1 run; `load_stats()`; `rebuild_stats()`: tính lại TỪ ĐẦU từ mọi
   `USAGE/delegate-runs/*/result.json` (idempotent). `run_task` gọi `update_stats(result)` ngay trước khi ghi result.json.
3. `rank_by_stats(queue, stats, min_rounds=3)`: executor có ≥ min_rounds vòng xếp theo `gate_pass/rounds` giảm dần,
   rồi tới người < min_rounds; bằng nhau giữ thứ tự gốc. Spec `uu_tien: thanh-tich` → áp dụng sau `pick_queue`
   (mặc định giữ chuỗi trong sổ).
4. CLI `--stats` in JSON {executor: {...các trường..., pass_rate}} (pass_rate = gate_pass/rounds, 0 nếu rounds = 0);
   `--stats --rebuild` chạy rebuild trước. Header đầu file thêm 1–2 dòng.

# Không làm
- Không sửa `tests/`, `org/`, `opencode.json`, `README.md`. Không đổi hành vi khác.
