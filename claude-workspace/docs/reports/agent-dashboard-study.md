# Nghiên cứu dashboard agent STLab

Phạm vi: đọc mã nguồn đã clone, không cài/chạy npm/npx/pip. “Không thấy” chỉ áp dụng file đã rà.

## 1. Nguon su kien

- Claude hooks: Agent Monitor nhận SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStop, Notification, PreCompact; transcript bổ sung tool activity. SubagentStart không thấy trong docs đã xem. File community/hoangsonww-claude-code-agent-monitor/docs/HOOKS.md, server/index.js (hook routes/ensureSession), server/db.js.
- Claude JSONL: DevTools theo dõi ~/.claude/projects/**/*.jsonl; đọc type, content blocks tool_use/tool_result, uuid, parentUuid, timestamp, session, isSidechain và agent ID nếu có. File community/matt1398-claude-devtools/src/main/services/parsing/SessionParser.ts (parse), infrastructure/FileWatcher.ts, discovery/SubagentLocator.ts.
- Gán subagent: agent ID từ transcript/file agent; parent từ parentUuid, Task tool call/result và agentId. Không đoán theo model/tên. File community/matt1398-claude-devtools/src/main/services/discovery/SubagentResolver.ts; community/hoangsonww-claude-code-agent-monitor/server/__tests__/subagent-attribution.test.js, server/db.js.
- Codex: Toolhub đọc ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl và rate_limits gần nhất, không phải toàn bộ hoạt động. Kibitz có parser/watcher; Monitor ingest tăng dần có offset. File studio/toolhub/usage.py (_last_rate_limits, codex), community/kibitzsh-kibitz/src/core/parsers/codex.ts, src/core/watcher.ts, community/hoangsonww-claude-code-agent-monitor/server/lib/codex-ingest.js.
- OpenCode: delegate gọi executor, giữ log/kết quả. Parser phiên OpenCode local trong Toolhub/Kibitz không thấy. File tools/delegate/delegate.py (_opencode, run_task), community/kibitzsh-kibitz/src/core/parsers/claude.ts, community/getagentseal-codeburn/src/quota/index.ts.
- Delegate: state.json có PID/spec/state; run_dir có prompt/log/gate log; result.json chốt; handoff.md khi chưa PASS. File tools/delegate/delegate.py (run_states, run_task, write_handoff, take_lock), studio/toolhub/usage.py (org_board).

Ghép bằng source + session_id + agent_id + event_id/tool_use_id; parent lấy từ metadata/transcript. Lưu model Haiku riêng, không biến model thành vai trò. Stop không đảm bảo đủ event giữa phiên.

## 2. Luu tru

- Agent Monitor SQLite: sessions (id/status/transcript_path), agents (id/session_id/type/subagent_type/status/task/timestamps/parent_agent_id), events (id/session_id/agent_id/event_type/tool_name/summary/data/created_at), token_usage và index. File community/hoangsonww-claude-code-agent-monitor/server/db.js.
- Đề xuất SQLite local; bảng events chuẩn hóa, payload_json cho trường nguồn. JSONL gốc chỉ đọc/replay. Bảng sources (path/offset/last_read), tasks (delegate run/spec/verdict), approvals (ref/state/owner); namespace ID theo nguồn.
- Retention/dung lượng: TODO — chưa đo transcript/lưu lượng STLab, không đặt số ngày/MB. Ban đầu không tự xóa; sau đo chỉ retention bản sao index, không xóa transcript/run.
- Delegate giữ prompt/log/result tại %LOCALAPPDATA%/stlab-usage/delegate-runs; limits/stats/locks ở usage dir. File tools/delegate/delegate.py, studio/toolhub/usage.py.

## 3. Giao dien

- Toolhub Flask + HTML/JS thuần; /api/org và panel Nhân sự AI là điểm mở rộng. Thêm API events/runs/approvals; push chưa thấy.
- Polling cursor-based, batch nhỏ phù hợp máy yếu. SSE Flask khả thi một chiều; WebSocket không cần cho dashboard đọc trạng thái.
- Bố cục: trạng thái agent/session, bảng việc, queue Tuan, timeline, panel chi tiết. Nhóm theo phiên/cây parent-subagent; lọc nguồn/agent/dự án/event/thời gian/trạng thái.
- Chi tiết tool call ghép tool_use/result theo ID, hiện tool/input/output/thời gian/agent; mặc định thu gọn và ẩn prompt/code.
- HTML/JS thuần hỗ trợ bật/tắt khung, kéo thả pointer/CSS Grid, resize, lưu layout/filter JSON trong localStorage. Tham khảo community/matt1398-claude-devtools/src/renderer/components/chat/items/ExecutionTrace.tsx, SubagentItem.tsx; studio/toolhub/static/app.js; templates/overview.html.

## 4. Dieu phoi viec va duyet

- Squadra đăng ký identity/session/role, gửi task/handoff; người nhận ACK, bắt đầu, chứng minh, giao kết quả. Giao hàng không thay ACK. File community/dagoste-squadra/references/start.md, references/work.md, scripts/squadra.py.
- TaskTrooper có board/cột, assignee/subscriber, reviewer bắt buộc Code Review và Human UAT; backend Postgres lớn hơn nhu cầu Toolhub. File community/makifbaysal-tasktrooper/docs/board-and-columns.md, role-agents.md, tasks.md.
- STLab có org/agents.yaml; delegate chọn executor, khóa cwd, lưu state/log/result/handoff và DONE/BLOCKED/ESCALATE. usage.py.org_board tổng hợp run; /api/org hiện hữu. custom/hooks/guard_paths.py chặn ghi tại PreToolUse; usage_alert.py cảnh báo.
- Queue người gom ESCALATE, BLOCKED, handoff chưa đọc, câu hỏi Tuan, quyền ghi bị chặn; lưu run ID/lý do/file ref/pending-acknowledged-resolved. Chỉ Tuan/coordinator resolve; sent không phải ACK.
- Phân biệt org role, executor/agent ID, model, session ID; không suy ra vai trò từ model Haiku.

## 5. Han muc va chi phi

- studio/toolhub/usage.py tìm rate_limits mới nhất trong tối đa 10 file Codex JSONL theo mtime; quota payload, không phải tổng token.
- Claude Pro hiện do statusline ghi %LOCALAPPDATA%/stlab-usage/claude.json; usage.py.claude đọc file này. Comment nói chỉ khi chạy claude terminal; panel VS Code không gọi statusline. Toolhub chưa lấy quota độc lập statusline.
- CodeBurn quota adapters Claude/Codex/OpenCode đọc credential local, truy vấn provider và giải mã quota. File community/getagentseal-codeburn/src/quota/claude.ts, codex.ts, index.ts, index.ts. Ghi nguồn/thời điểm/lỗi.
- CodeBurn có cơ chế quota Claude không cần statusline; chưa chứng minh tích hợp STLab hoặc mọi Pro ổn định. Cần rà credential/mạng trước khi sao chép.
- OpenCode Zen: adapter opencode có, nhưng chưa thấy bằng chứng quota Zen account truy vấn ổn định. Nếu thiếu ghi “không thấy”, không suy từ token cost. Chi phí API-equivalent không phải hóa đơn. File community/getagentseal-codeburn/src/usage-aggregator.ts, quota/types.ts, docs/plans-and-quota.md.

## 6. An toan

- Hook local đọc JSON stdin. custom/hooks/guard_paths.py đăng ký PreToolUse cho ghi và áp rules; usage_alert.py đọc event, cấu hình ~/.claude/settings.json. Không làm yếu guard.
- Transcript có prompt/path/tool input-output/mã. Lưu local, quyền user, loopback, ẩn payload mặc định. Không telemetry; Agent Monitor có webhook/remote, CodeBurn quota có truy vấn mạng.
- SQLite trong user data; Flask bind ngoài loopback cần auth. Không ghi secret summary/log/URL. Tách quyền đọc và approve/resolve; mặc định chỉ đọc.
- Chỉ đọc có chủ đích ~/.claude/projects, ~/.codex/sessions, delegate log và org/agents.yaml. Tham khảo community/hoangsonww-claude-code-agent-monitor/docs/data-security.md, server/__tests__/transcript-sender.test.js; community/getagentseal-codeburn/src/quota/security.ts.

## 7. Ap dung cho STLab

1. Nhật ký chung (vừa): SQLite cho Claude chính/subagent/delegate rồi Codex; lưu source/session/agent/parent/tool/event/time/payload ref. Học community/hoangsonww-claude-code-agent-monitor/server/db.js.
2. Ingest JSONL (vừa): giữ offset, ghép tool call/result ID; xem community/hoangsonww-claude-code-agent-monitor/server/lib/codex-ingest.js, community/matt1398-claude-devtools/src/main/services/infrastructure/FileWatcher.ts. OpenCode schema local: không thấy.
3. Hook Claude (vừa): mốc prompt/tool/stop/subagent và transcript ref, giữ guard. File community/hoangsonww-claude-code-agent-monitor/docs/HOOKS.md, custom/hooks/guard_paths.py.
4. Cây agent (vừa): ID/session, parent từ transcript/Task, role từ org, model riêng. File community/matt1398-claude-devtools/src/main/services/discovery/SubagentResolver.ts.
5. Queue Tuan (nhỏ): đọc ESCALATE/BLOCKED/handoff từ result.json/handoff.md; chỉ người resolve. tools/delegate/delegate.py (write_handoff), studio/toolhub/usage.py (org_board).
6. Bảng việc (nhỏ): dùng state/run_dir/lock/result, lọc queue và link log/handoff; không dựng scheduler. ACK tham khảo community/dagoste-squadra/references/work.md.
7. Timeline (vừa): session, nhánh subagent, filter, tool detail. File community/matt1398-claude-devtools/src/renderer/components/chat/items/ExecutionTrace.tsx.
8. Khung tùy biến (nhỏ): HTML/JS, CSS Grid, kéo thả/toggle/resize/localStorage. Sửa studio/toolhub/templates/overview.html, studio/toolhub/static/app.js.
9. API/polling (nhỏ): endpoint cursor-based, poll nhẹ; SSE cân nhắc sau đo; giữ /api/org. File studio/toolhub/usage.py.
10. Usage/quota (vừa): tiếp tục Codex rate_limits; Claude phụ thuộc claude.json/statusline. Rà adapter CodeBurn và quyền mạng; OpenCode Zen chưa xác định. File community/getagentseal-codeburn/src/quota/claude.ts, index.ts.

Thứ tự: event store/ingest → queue hỏi Tuan → bảng việc/timeline → tùy biến → quota. Không cần dịch vụ trả phí, model local hoặc framework nặng.


### Danh muc file nguon da doi chieu

- `community/matt1398-claude-devtools/src/main/services/parsing/SessionParser.ts`
- `community/matt1398-claude-devtools/src/main/services/infrastructure/FileWatcher.ts`
- `community/matt1398-claude-devtools/src/main/services/discovery/SubagentLocator.ts`
- `community/matt1398-claude-devtools/src/main/services/discovery/SubagentResolver.ts`
- `community/matt1398-claude-devtools/src/main/types/domain.ts`
- `community/matt1398-claude-devtools/src/renderer/components/chat/items/ExecutionTrace.tsx`
- `community/matt1398-claude-devtools/src/renderer/components/chat/items/SubagentItem.tsx`
- `community/hoangsonww-claude-code-agent-monitor/docs/HOOKS.md`
- `community/hoangsonww-claude-code-agent-monitor/docs/DATABASE.md`
- `community/hoangsonww-claude-code-agent-monitor/server/index.js`
- `community/hoangsonww-claude-code-agent-monitor/server/db.js`
- `community/hoangsonww-claude-code-agent-monitor/server/lib/codex-ingest.js`
- `community/hoangsonww-claude-code-agent-monitor/server/__tests__/subagent-attribution.test.js`
- `community/hoangsonww-claude-code-agent-monitor/server/__tests__/transcript-sender.test.js`
- `community/kibitzsh-kibitz/src/core/parsers/codex.ts`
- `community/kibitzsh-kibitz/src/core/parsers/claude.ts`
- `community/kibitzsh-kibitz/src/core/watcher.ts`
- `community/getagentseal-codeburn/src/quota/claude.ts`
- `community/getagentseal-codeburn/src/quota/codex.ts`
- `community/getagentseal-codeburn/src/quota/index.ts`
- `community/getagentseal-codeburn/src/quota/security.ts`
- `community/getagentseal-codeburn/src/quota/types.ts`
- `community/getagentseal-codeburn/src/usage-aggregator.ts`
- `community/getagentseal-codeburn/docs/plans-and-quota.md`
- `community/dagoste-squadra/references/start.md`
- `community/dagoste-squadra/references/work.md`
- `community/dagoste-squadra/scripts/squadra.py`
- `community/makifbaysal-tasktrooper/docs/board-and-columns.md`
- `community/makifbaysal-tasktrooper/docs/role-agents.md`
- `community/makifbaysal-tasktrooper/docs/tasks.md`
- `studio/toolhub/usage.py`
- `studio/toolhub/static/app.js`
- `studio/toolhub/templates/overview.html`
- `tools/delegate/delegate.py`
- `org/agents.yaml`
- `custom/hooks/guard_paths.py`
- `custom/hooks/usage_alert.py`
