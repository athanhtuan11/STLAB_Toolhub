---
task: ops-events
cwd: tools
allow: ["org/events.py", "delegate/delegate.py"]
read: ["custom/hooks", "docs/reports/ops-center-design.md", "org"]
gate: 'python org\tests\test_events.py && python delegate\tests\test_delegate.py && python delegate\tests\test_registry.py && python delegate\tests\test_stats.py'
ky_nang: [code]
timeout_min: 30
max_rounds: 3
---

# Mục tiêu
Bước 1 Trung tâm điều hành (Tuan đã duyệt `docs/reports/ops-center-design.md`): kho sự kiện + hàng chờ duyệt, và
`delegate.py` ghi sự kiện. Đọc `org/tests/test_events.py` để biết đúng hành vi. Stdlib (sqlite3) + yaml.
Hook `custom/hooks/event_log.py` nằm NGOÀI cwd: viết nội dung nó vào `org/event_log_hook.py` (trong allow? KHÔNG –
xem dưới) – thay vào đó **chỉ viết `org/events.py` có hàm `hook_main()`**; Claude sẽ tạo file hook mỏng gọi hàm đó.

# `org/events.py` (thư viện + CLI)
- DB: `%LOCALAPPDATA%/stlab-usage/events.db` – đọc biến môi trường MỖI lần gọi (không đóng băng lúc import). WAL,
  `timeout=5`. Bảng `events(id INTEGER PK, ts REAL, source, kind, title, agent, session, parent, ref, data TEXT JSON)`,
  `approvals(id INTEGER PK, ts REAL, source, question, ref, options TEXT JSON, state, by, note, resolved_ts)`.
- `emit(source, kind, title, agent=None, session=None, parent=None, ref=None, data=None) -> int|None`: KHÔNG BAO GIỜ
  raise (mọi lỗi → None). Cắt title ≤ 200 ký tự.
- `recent(limit=100, after_id=None, agent=None, source=None, kind=None) -> list[dict]` mới nhất trước; `data` đã parse.
- `add_approval(question, source, ref=None, options=None) -> int` (state "cho") + emit kind "approval_add";
  `list_approvals(state=None)`; `resolve(id, state, by, note=None) -> bool` (state "da-duyet"|"tu-choi") + emit
  "approval_resolved"; id không có → False.
- CLI (in JSON UTF-8): `approvals add <question> [--source S] [--ref R] [--options A,B]` → {"id"};
  `approvals list [--state S]`; `approvals resolve <id> --state S [--by tuan] [--note N]` → {"ok"}; `tail [--limit N]`.
- `hook_main()`: đọc JSON hook Claude Code từ stdin (rác → im lặng, exit 0) và `emit(source="hook", ...)`:
  SessionStart → kind "session_start"; UserPromptSubmit → "prompt", title "Tuan gửi yêu cầu" (TUYỆT ĐỐI không lưu
  nội dung prompt); PostToolUse → "tool", title "<tool_name> <basename(file_path|notebook_path)>" (Bash/khác: chỉ tên
  công cụ; KHÔNG lưu command/old_string/content); SubagentStop → "subagent_stop", agent = `agent_type` (hoặc
  `subagent_type`/`agent_name`), title "<agent> xong"; Stop → "stop"; Notification → "notification" (title ≤ 80 ký tự
  của message); khác → bỏ qua. `agent` mặc định "claude-main" nếu input không có agent_type/agent_id; `session` = session_id.
  `if __name__ == "__main__"` chỉ cho CLI; hook gọi `hook_main()` qua file mỏng.

# `delegate/delegate.py`
- Import `events` từ `../org/events.py` (sys.path theo HERE); nếu import lỗi → chạy bình thường không ghi (không hỏng delegate).
- Ghi: "run_start" (title "<executor đầu> nhận <task>", ref run_dir), mỗi vòng "round" (verdict gate), "run_end"
  (title "<task> <verdict>", data {verdict, rounds, seconds}); ESCALATE → `add_approval(question="<executor>: <lý do>",
  source="delegate", ref=<tên run>)`.

# Không làm
- Không sửa tests/, custom/, org/*.yaml, studio/.
- Ghi file: mã + chú thích ASCII (không dấu, như phần còn lại của delegate.py) ghi cách nào cũng được; chuỗi tiếng
  Việt có dấu trong mã (vd "Tuan gửi yêu cầu") viết dạng `\uXXXX` trong source Python (vd "Tuan gửi yêu cầu").
