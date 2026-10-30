---
task: usage-all-sources
cwd: .
allow: ["tools/delegate/delegate.py", "studio/toolhub/usage.py", "studio/toolhub/templates/overview.html"]
read: ["tools/delegate/tests/test_stats_time.py", "tools/delegate/tests/test_stats.py", "studio/tests/test_org_board.py", "org/agents.yaml"]
gate: 'python tools\delegate\tests\test_stats_time.py && python tools\delegate\tests\test_stats.py && python tools\delegate\tests\test_delegate.py && python tools\delegate\tests\test_registry.py && studio\.venv\Scripts\python.exe studio\tests\test_org_board.py && studio\.venv\Scripts\python.exe studio\tests\test_library_pages.py'
executor: auto
timeout_min: 30
max_rounds: 2
---

# Mục tiêu
Tuan (2026-10-30): "hạn mức theo nguồn chưa thấy cập nhật". Ô Nhân sự AI trên trang chính Toolhub phải hiện **đủ
mọi nguồn** trong sổ `org/agents.yaml`; nguồn nào không có số hạn mức thì vẫn hiện, ghi "Chưa có số hạn mức" kèm
**lần cuối chạy được** (lấy từ thống kê `delegate.py`). Hành vi đúng = các test trong gate (KHÔNG sửa test).
Lưu ý: `studio/toolhub/usage.py` đang có thay đổi chưa commit (hàm `_stale`, cờ `stale`) – GIỮ NGUYÊN, làm tiếp trên đó.

# Yêu cầu
## `tools/delegate/delegate.py`
- `tally(stats, result)`: lấy mốc từ `os.path.basename(result.get("run_dir") or "")` khớp `^(\d{8})-(\d{6})-`
  → chuỗi `"YYYY-MM-DDTHH:MM"`. Không khớp → không ghi mốc nào (không lỗi).
- Với mỗi vòng có `executor` (kể cả vòng `limited`): `last_run = max(cũ, mốc)`. Vòng `limited` → `last_limited = max`.
  Vòng `gate_exit == 0` → `last_pass = max`. So sánh chuỗi; chỉ thêm khóa khi có mốc (không đưa vào `STAT_FIELDS`,
  `new_stats()` giữ nguyên các số đếm). Các số đếm cũ không đổi. `rebuild_stats` tự đúng vì dùng chung `tally`.

## `studio/toolhub/usage.py` – `org_board()`
- 6 nguồn, thứ tự: `claude`, `codex`, `gemini`, `opencode`, `kilo`, `copilot`. Gán agent → nguồn:
  `chi_phi == "claude-quota"` → claude; id/model chứa `codex`/`gpt` → codex; id bắt đầu `agy` hoặc chứa `gemini` →
  gemini (gồm `agy-sonnet`); `opencode` → opencode; `kilo` → kilo; `copilot` → copilot. Mỗi agent đúng 1 nguồn.
- Tên hiển thị nguồn `gemini`: `"Antigravity (agy)"` (agy chạy cả Gemini lẫn Sonnet; thẻ hiện cả 2 thanh
  `gemini-weekly` + `3p-weekly` như hàm `gemini()` đang làm).
- Nguồn không có hàm đọc số (opencode, kilo, copilot): `bars: []`, `note: "Chưa có số hạn mức – xem lần cuối chạy"`
  (chữ "chưa có số" phải có), `plan` lần lượt `"Zen free"`, `"Kilo free"`, `"Copilot free"`.
- Mỗi nguồn thêm `last_run`: max `last_run` trong `agent-stats.json` của các agent thuộc nguồn, định dạng
  `"dd/mm HH:MM"`; không có → `""`. Thêm tương tự `last_limited` (cùng định dạng, `""` nếu không có).

## `studio/toolhub/templates/overview.html`
- Thẻ nguồn (`u-card`): nếu `p.last_run` → thêm dòng nhỏ `Lần cuối chạy: <last_run>`; nếu `p.last_limited` →
  `· chạm hạn mức <last_limited>`. Nguồn không có thanh thì vẫn hiện thẻ với `note`. Giữ style class sẵn có.

# Không làm
- Không sửa `org/`, `executors.json`, hàm `codex()/gemini()/claude()` đọc số, các test.
- Không gọi mạng/API để lấy hạn mức.

# Tiêu chí PASS
- Gate exit 0. Claude tự xem trang chính Toolhub.
