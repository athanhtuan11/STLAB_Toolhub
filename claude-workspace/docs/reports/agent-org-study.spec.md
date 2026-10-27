---
task: study-agent-org
cwd: docs/reports
allow: ["agent-org-roles-permissions.md"]
gate: 'python ../../tools/delegate/check_report.py agent-org-roles-permissions.md "## 1. Hien trang STLab" "## 2. Claude Code subagent" "## 3. knowledge-work-plugins" "## 4. VoltAgent subagents" "## 5. Codex va OpenCode" "## 6. Bang thuoc tinh"'
timeout_min: 30
max_rounds: 2
executor: codex
---

# Mục tiêu
Viết `agent-org-roles-permissions.md` (tiếng Việt có dấu, ≤ 220 dòng): KHẢO SÁT bằng chứng để Claude thiết kế
"sơ đồ tổ chức" agent cho STLab: Claude = tổng giám đốc, agent Haiku = quản lý, executor free = nhân viên; sau này sẽ
thêm nhiều agent nữa. Chỉ ĐỌC file, không cài/chạy gì. KHÔNG tự thiết kế hệ STLab – chỉ thu thập và so sánh.

# Nguồn (đường dẫn tương đối claude-workspace; đọc từ ../../)
- Hiện trạng: `custom/agents/*.md`, `tools/delegate/delegate.py`, `tools/delegate/opencode.json`,
  `tools/delegate/README.md`, `CLAUDE.md` (mục "Phân việc theo model"), `docs/model-routing.md`.
- `community/anthropics-knowledge-work-plugins/` (README + 2–3 plugin tiêu biểu: cách khai báo agent/skill/lệnh/connector theo vai trò).
- `community/voltagent-subagents/` (README, CLAUDE.md, 2–3 file agent trong `categories/`: frontmatter tools/model).
- Claude Code subagent: các trường frontmatter thấy trong các file trên (name, description, tools, model, …).

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Hien trang STLab`: liệt kê từng agent/executor đang có: vai trò, model, tool được dùng, quyền ghi, chặn gì.
- `## 2. Claude Code subagent`: các trường cấu hình quyền/model/tool thấy được trong file thật; giới hạn.
- `## 3. knowledge-work-plugins`: plugin tổ chức theo vai trò thế nào (cấu trúc thư mục, manifest, agent/skill/connector).
- `## 4. VoltAgent subagents`: cách phân loại agent theo nhóm, cách giới hạn tool theo vai trò.
- `## 5. Codex va OpenCode`: cơ chế quyền/sandbox thấy trong cấu hình STLab (`opencode.json`, lệnh codex trong delegate.py).
- `## 6. Bang thuoc tinh`: bảng các THUỘC TÍNH mà một "hồ sơ nhân sự" agent nên có, mỗi thuộc tính: ý nghĩa, ví dụ
  giá trị đang dùng ở STLab hoặc nguồn cộng đồng, dẫn file. (vd: vai trò, cấp, model, chi phí/hạn mức, tool được dùng,
  đường ghi được, cấm, mạng, dữ liệu được xem, ai duyệt kết quả, gate, thoát khi lỗi.)

# Quy tắc
- Mọi khẳng định quan trọng dẫn đường dẫn trong backtick, TƯƠNG ĐỐI theo claude-workspace (gate kiểm tồn tại, ≥ 10).
- Không thấy → "không thấy"/`TODO`; không đoán, không chép số liệu từ trí nhớ.
