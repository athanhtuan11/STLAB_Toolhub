---
task: claude-code-setup-audit
cwd: docs/reports
allow: ["claude-code-setup-audit.md"]
read: ["community/anthropics-claude-plugins-official", "custom", ".claude", "CLAUDE.md", "org", "tools/delegate",
       "tools/org", "community/links.tsv", "community/pins.tsv", "docs/model-routing.md", "harness-lab", "studio",
       "tools/robotics-cad", "maker"]
gate: 'python ../../tools/delegate/check_report.py claude-code-setup-audit.md "## 1. Phuong phap claude-automation-recommender" "## 2. Ho so codebase" "## 3. Hien trang 5 nhom" "## 4. De xuat theo skill" "## 5. Trung thua xung dot" "## 6. Ke hoach toi uu" --max-todo 4 --min-files 15'
ky_nang: [bao-cao]
timeout_min: 35
max_rounds: 3
---

# Mục tiêu
Viết `claude-code-setup-audit.md` (tiếng Việt có dấu, ≤ 260 dòng): áp ĐÚNG phương pháp của skill chính thức
`community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/SKILL.md`
(+ `references/*.md`) lên workspace STLab `claude-workspace/` để tối ưu cấu hình Claude Code. Chỉ ĐỌC, không sửa gì,
không cài/chạy. Repo gốc: `D:\04_Stlab\04_STLAB_Toolhub` (claude-workspace là thư mục con; `.claude/settings.json` gốc
nằm ở `../.claude/settings.json` – đọc nếu đọc được, không được thì ghi "không đọc được").

# Bối cảnh bắt buộc tôn trọng (đọc `CLAUDE.md`, `org/agents.yaml`, `org/policy.yaml`, `docs/model-routing.md`)
- Chỉ trả Claude Pro; còn lại free (Codex, OpenCode Zen, agy). Máy yếu, Windows, không model local.
- Phân quyền 3 tầng + sổ nhân sự `org/`; `tools/delegate/delegate.py` giao việc; agent Haiku `custom/agents/*.md`.
- Skill một nguồn: `custom/skills/` + `community/` liên kết qua `community/links.tsv`; không upload claude.ai.
- Nguồn cộng đồng: ưu tiên nhiều sao, phải còn cập nhật, đọc mã trước khi dùng.

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Phuong phap claude-automation-recommender`: các pha, tín hiệu codebase nó đọc, cách chọn top theo nhóm
  (MCP, skill, hook, subagent, plugin), quy tắc output – dẫn file.
- `## 2. Ho so codebase`: chạy Pha 1 của skill trên STLab (ngôn ngữ, framework, công cụ: FreeCAD/Blender/Flask/ESP32…,
  thư mục chính) – dẫn file thật.
- `## 3. Hien trang 5 nhom`: STLab đang có gì ở từng nhóm (hook trong `custom/hooks/` + settings, MCP, skill, subagent,
  plugin/lệnh `.claude/commands/`) – bảng, dẫn file.
- `## 4. De xuat theo skill`: theo đúng Decision Framework của skill, mỗi nhóm 1–3 đề xuất phù hợp bối cảnh (lý do +
  dẫn file nguồn của skill + dẫn file STLab liên quan). Không đề xuất dịch vụ trả phí/model local.
- `## 5. Trung thua xung dot`: chỗ trùng/thừa/lệch giữa CLAUDE.md, org/, custom/agents, settings, skills, commands
  (vd. quy tắc lặp nhiều nơi, agent không có trong sổ, lệnh cũ) – dẫn file.
- `## 6. Ke hoach toi uu`: ≤ 10 việc xếp theo giá trị/công sức (nhỏ/vừa/lớn), mỗi việc ghi ai làm theo sổ nhân sự
  (claude-main / codex / opencode / doc-writer …).

# Quy tắc
- Dẫn đường dẫn FILE cụ thể trong backtick, tương đối claude-workspace (gate: ≥ 15 file tồn tại, ≤ 4 TODO).
- Không thấy → "không thấy"; không đoán.
