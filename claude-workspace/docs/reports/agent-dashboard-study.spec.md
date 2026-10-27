---
task: study-agent-dashboard
cwd: docs/reports
allow: ["agent-dashboard-study.md"]
read: ["community/matt1398-claude-devtools", "community/hoangsonww-claude-code-agent-monitor", "community/kibitzsh-kibitz",
       "community/getagentseal-codeburn", "community/dagoste-squadra", "community/makifbaysal-tasktrooper",
       "studio/toolhub", "tools/delegate", "org", "custom/hooks"]
gate: 'python ../../tools/delegate/check_report.py agent-dashboard-study.md "## 1. Nguon su kien" "## 2. Luu tru" "## 3. Giao dien" "## 4. Dieu phoi viec va duyet" "## 5. Han muc va chi phi" "## 6. An toan" "## 7. Ap dung cho STLab" --max-todo 4 --min-files 25'
ky_nang: [bao-cao]
timeout_min: 40
max_rounds: 3
---

# Mục tiêu
Viết `agent-dashboard-study.md` (tiếng Việt có dấu, ≤ 280 dòng): đọc MÃ NGUỒN 6 repo đã clone (chỉ ĐỌC, không cài/chạy
npm/npx/pip) để STLab làm Toolhub hiển thị **mọi việc hệ thống agent đang làm** (Tuan: "mở trang web lên thấy được tất
cả mình làm", giao diện tùy biến). Hệ hiện có để so: `studio/toolhub/usage.py` (ô Nhân sự AI, `/api/org`),
`tools/delegate/delegate.py` (run_dir, result.json, agent-stats.json, executors.json, khóa), `org/agents.yaml`,
`custom/hooks/` (usage_alert.py, guard_paths.py). Toolhub = Flask + HTML/JS thuần, máy Windows yếu.

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Nguon su kien`: mỗi repo lấy dữ liệu từ đâu: hook Claude Code nào (PreToolUse/PostToolUse/SubagentStart/
  SubagentStop/Stop/Notification/UserPromptSubmit…), file phiên `~/.claude/projects/**/*.jsonl` (trường nào: type,
  tool_use, isSidechain, agent/subagent id…), phiên Codex `~/.codex/sessions`, OpenCode; cách gán sự kiện cho TỪNG
  subagent/agent. Dẫn file + tên hàm.
- `## 2. Luu tru`: SQLite/JSONL/bộ nhớ, schema bảng sự kiện, giữ bao lâu, dung lượng.
- `## 3. Giao dien`: cập nhật trực tiếp (SSE/WebSocket/polling), bố cục, **tùy biến** (bật/tắt khung, kéo thả, lưu
  bố cục, bộ lọc), dòng thời gian, xem chi tiết 1 lệnh gọi công cụ. Cái nào làm được bằng HTML/JS thuần.
- `## 4. Dieu phoi viec va duyet`: squadra/tasktrooper: bảng việc, giao/nhận/xác nhận (ack), hàng chờ duyệt của người,
  vai trò agent – so với `tools/delegate/` + `org/` (spec, ESCALATE, handoff.md).
- `## 5. Han muc va chi phi`: codeburn đọc token/chi phí Claude Code, Codex, OpenCode cục bộ thế nào (file nào, trường
  nào) – đặc biệt có lấy được hạn mức Claude Pro KHÔNG cần statusline, và hạn mức OpenCode Zen không.
- `## 6. An toan`: hook cài vào đâu, gửi mạng/telemetry, đọc dữ liệu nhạy cảm (prompt, mã), quyền.
- `## 7. Ap dung cho STLab`: ≤ 10 đề xuất cụ thể (cái gì, dẫn file nguồn, công sức nhỏ/vừa/lớn), ưu tiên: nhật ký sự
  kiện chung (Claude chính + subagent Haiku + executor delegate), hàng chờ duyệt (ESCALATE, hỏi Tuan), bảng việc,
  dòng thời gian, khung tùy biến. Không đề xuất dịch vụ trả phí/model local/framework nặng.

# Quy tắc
- Dẫn đường dẫn FILE cụ thể trong backtick, tương đối claude-workspace (gate: ≥ 25 file tồn tại, ≤ 4 TODO).
- Không thấy → "không thấy"; không đoán, không chép số sao/ngày từ trí nhớ.
