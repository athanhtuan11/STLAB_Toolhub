# Báo cáo kiểm toán Claude Code cho STLab

Phạm vi chỉ đọc; không cài, chạy hoặc sửa cấu hình. Đường dẫn tương đối với claude-workspace.

## 1. Phuong phap claude-automation-recommender

Nguồn: `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/SKILL.md`.

- **Pha 1 – phân tích:** nhận diện ngôn ngữ/framework từ manifests/imports; cấu hình Claude từ .claude/ và CLAUDE.md; cấu trúc, kiểm thử, CI, database, API ngoài, tài liệu. Dấu hiệu định hướng MCP, skill, hook, subagent, plugin.
- **Pha 2 – đề xuất:** MCP cho tích hợp ngoài/tài liệu/trình duyệt/nhóm; skill cho quy trình lặp và tài liệu; hook cho tự động hóa, bảo vệ, kiểm tra; subagent cho chuyên môn/đánh giá; plugin cho gói năng lực. Tham chiếu `references/mcp-servers.md`, `references/skills-reference.md`, `references/hooks-patterns.md`, `references/subagent-templates.md`, `references/plugins-reference.md`.
- **Ưu tiên:** chọn 1–2 lựa chọn nổi bật mỗi loại theo tín hiệu thực tế, bỏ loại không phù hợp. Báo cáo này cho 1–3 theo đề bài. Không đề xuất dịch vụ trả phí/model local.
- **Pha 3 – báo cáo:** nêu hồ sơ, lý do cụ thể, nơi cấu hình/cách gọi và file dẫn chứng; chỉ phân tích, không cài/tạo; mời yêu cầu gợi ý thêm.

## 2. Ho so codebase

- **Ngôn ngữ:** Python ở Toolhub/CAD/delegate; C/C++ ở firmware ESP-IDF; JavaScript/CSS ở giao diện. Dẫn chứng: `studio/pyproject.toml`, `studio/toolhub/views.py`, `studio/toolhub/static/app.js`, `maker/pump-control/firmware/main/app_main.c`.
- **Framework/công cụ:** Flask trong `studio/pyproject.toml`; FreeCAD trong `tools/robotics-cad/CLAUDE.md`, `studio/freecad/`; Blender trong `studio/bat/open-blender.bat`; ESP-IDF trong `maker/pump-control/firmware/CMakeLists.txt`. Delegate và CAD: `tools/delegate/delegate.py`, `tools/robotics-cad/scripts/prepare-print.py`.
- **Kiểm thử:** `studio/tests/test_org_board.py`, `tools/robotics-cad/tests/test_cad_lib.py`, `maker/pushrod-arm/freecad/tests/test_pushrod_arm.py`; chưa xác định cấu hình pytest/Ruff cụ thể, cần đọc thêm trước khi gắn hook.
- **Cấu trúc:** quy tắc `CLAUDE.md`; ứng dụng `studio/`; dự án CAD/firmware `maker/`; công cụ `tools/robotics-cad/`; quản trị `org/`; skill/hook `custom/`; nguồn ghim `community/`; báo cáo `docs/`.
- **Tín hiệu ngoài:** không thấy bằng chứng khảo sát về React/Vue, database, CI GitHub, Linear, AWS, Stripe, Sentry. Không đủ căn cứ MCP tương ứng. Tích hợp FreeCAD/Blender có trong `community/links.tsv`.
- Có `CLAUDE.md`, `org/agents.yaml`, `org/policy.yaml`, `custom/agents/`, `custom/skills/`, `custom/hooks/`, `.claude/commands/`. Không thấy `.claude/settings.json` tại gốc workspace đã kiểm tra; không xác nhận cấu hình đang nạp.


Tệp nguồn bổ sung đã đối chiếu: `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/SKILL.md`, `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/mcp-servers.md`, `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/skills-reference.md`, `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/hooks-patterns.md`, `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/subagent-templates.md`, `community/anthropics-claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/plugins-reference.md`, `tools/robotics-cad/scripts/check.py`, `tools/robotics-cad/tests/test_cad_lib.py`, `tools/robotics-cad/scripts/prepare-print.py`, `tools/delegate/README.md`, `tools/delegate/delegate.py`, `docs/model-routing.md`, `docs/COMMUNITY.md`.

## 3. Hien trang 5 nhom

| Nhóm | Hiện trạng | Dẫn chứng |
|---|---|---|
| Hook | Có cảnh báo quota và chặn đường dẫn; settings workspace không thấy nên chưa kiểm chứng đăng ký. | `custom/hooks/usage_alert.py`; `custom/hooks/guard_paths.py`; `docs/model-routing.md`; `.claude/settings.json` không thấy |
| MCP | Tài liệu ghi deliberation Codex/Gemini chỉ đọc và MCP FreeCAD/Blender; cấu hình trực tiếp không thấy. | `docs/model-routing.md`; `community/links.tsv`; `studio/bat/check-mcp.bat` |
| Skill | Năm skill custom; liên kết cộng đồng tập trung, chia dùng chung/cấp dự án. | `custom/skills/robotics-cad/SKILL.md`; `custom/skills/bambu-a1/SKILL.md`; `custom/skills/video-ai/SKILL.md`; `custom/skills/steam-lesson-plan/SKILL.md`; `custom/skills/parent-report/SKILL.md`; `community/links.tsv` |
| Subagent | Ba agent Haiku trong sổ, có file tương ứng; agent cộng đồng liên kết theo dự án maker. | `org/agents.yaml`; `custom/agents/check-runner.md`; `custom/agents/doc-writer.md`; `custom/agents/git-scribe.md`; `community/links.tsv` |
| Plugin/lệnh | Bốn lệnh workspace; routing ghi deliberation và Codex plugin. Plugin manifest trong workspace không thấy. | `.claude/commands/lesson.md`; `.claude/commands/new-project.md`; `.claude/commands/print-result.md`; `.claude/commands/update-community.md`; `docs/model-routing.md` |

## 4. De xuat theo skill

### MCP
- **Duy trì deliberation chỉ đọc** cho tóm tắt/ý kiến hai; chỉ gửi tài liệu kỹ thuật/bản sao theo chính sách. Nguồn skill: `.../claude-automation-recommender/SKILL.md`, `.../references/mcp-servers.md`; STLab: `docs/model-routing.md`, `org/policy.yaml`.
- **Duy trì MCP FreeCAD/Blender**, công cụ chính đã liên kết; rà mã, cập nhật, license trước khi đổi nguồn. Nguồn: `.../references/mcp-servers.md`; STLab: `community/links.tsv`, `studio/bat/check-mcp.bat`, `tools/robotics-cad/CLAUDE.md`.
- **Không thêm GitHub/browser/database MCP** khi chưa thấy tín hiệu. Nguồn: `.../references/mcp-servers.md`; STLab: `studio/pyproject.toml`, `CLAUDE.md`.

### Skill
- **Giữ CAD/Bambu trong custom và qua links.tsv**, tránh bản sao. Nguồn: `.../references/skills-reference.md`; STLab: `custom/skills/robotics-cad/SKILL.md`, `custom/skills/bambu-a1/SKILL.md`, `community/links.tsv`.
- **Chỉ cân nhắc skill quy ước Claude-only** nếu rà soát thấy chưa có nguồn tương đương; tôn trọng một nguồn. Nguồn: `.../references/skills-reference.md`; STLab: `CLAUDE.md`, `org/policy.yaml`.
- **Giữ skill giáo dục đúng phạm vi dữ liệu**, không gửi parent-report ra ngoài. Nguồn: `.../references/skills-reference.md`; STLab: `custom/skills/steam-lesson-plan/SKILL.md`, `custom/skills/parent-report/SKILL.md`, `org/policy.yaml`.

### Hook
- **Ưu tiên guard_paths** bảo vệ đường cấm/vùng cần hỏi; xác minh settings trước khi sửa. Nguồn: `.../references/hooks-patterns.md`; STLab: `custom/hooks/guard_paths.py`, `org/policy.yaml`.
- **Giữ usage_alert nếu hữu ích**, routing phụ thuộc quota. Nguồn: `.../references/hooks-patterns.md`; STLab: `custom/hooks/usage_alert.py`, `docs/model-routing.md`.
- **Chỉ cân nhắc hook CAD nhẹ** khi đã định rõ lệnh/phạm vi, tránh file in được bảo vệ. Nguồn: `.../references/hooks-patterns.md`; STLab: `tools/robotics-cad/scripts/check.py`, `tools/robotics-cad/scripts/prepare-print.py`, `org/policy.yaml`.

### Subagent
- **Giữ ba vai trò trong sổ**: check-runner, doc-writer, git-scribe; không thêm bản thể ngoài đăng ký. Nguồn: `.../references/subagent-templates.md`; STLab: `org/agents.yaml`, `custom/agents/check-runner.md`, `custom/agents/doc-writer.md`, `custom/agents/git-scribe.md`.
- **Chỉ xem xét reviewer CAD/Python chỉ đọc** nếu check-runner chưa đáp ứng nhu cầu; agent mới cần Claude đề xuất, Tuan duyệt. Nguồn: `.../references/subagent-templates.md`; STLab: `org/agents.yaml`, `tools/robotics-cad/tests/test_cad_lib.py`.

### Plugin
- **Giữ deliberation và Codex theo routing**, không dùng provider trả phí/model local. Nguồn: `.../references/plugins-reference.md`; STLab: `docs/model-routing.md`, `org/policy.yaml`.
- **Không ưu tiên plugin frontend/code-review chung**: chưa thấy framework tương ứng; đã có delegate và agent. Nguồn: `.../references/plugins-reference.md`; STLab: `tools/delegate/README.md`, `org/agents.yaml`, `studio/toolhub/static/app.js`.

## 5. Trung thua xung dot

- **Quyền/routing lặp:** `CLAUDE.md`, `org/policy.yaml`, `docs/model-routing.md` cùng mô tả phân quyền, dữ liệu, chi phí. `CLAUDE.md` xác định `org/agents.yaml` + `org/policy.yaml` là nguồn chuẩn agent/chính sách; tránh sửa bản mô tả rời rạc lệch nhau.
- **Agent:** ba `custom/agents/*.md` khớp sổ; không thấy agent custom ngoài sổ trong nhóm này. Agent cộng đồng ở `community/links.tsv` là liên kết theo dự án, không phải nhân sự nội bộ.
- **Settings:** `docs/model-routing.md` mô tả hook/deny ở settings người dùng; `.claude/settings.json` workspace không thấy, chưa thể kết luận cấu hình đang chạy khớp tài liệu.
- **Skill:** `community/links.tsv` là registry; `CLAUDE.md` yêu cầu một nguồn và cấm tải lên claude.ai. Không tạo bản dự án trùng. `custom/skills/parent-report/SKILL.md` cần theo phân loại customer trong `org/policy.yaml`.
- **Lệnh:** bốn lệnh trong `.claude/commands/`; chưa có bằng chứng lệnh cũ/trùng. Không suy đoán nội dung chưa đọc.
- **Hook:** mã hook có trong workspace, mô tả matcher ở user settings nhưng thiếu settings workspace để đối chiếu; xác minh trước khi đăng ký mới, tránh chạy trùng.

## 6. Ke hoach toi uu

Đề xuất, chưa thực thi. Vai trò theo `org/agents.yaml`.

| # | Việc | Giá trị / công sức | Người làm |
|---|---|---|---|
| 1 | Claude kiểm tra settings người dùng, xác nhận guard_paths/usage_alert đăng ký đúng một lần. | Cao / nhỏ | claude-main |
| 2 | Đối chiếu CLAUDE.md và org/policy.yaml; Claude chốt nguồn/gate trước sửa. | Cao / vừa | claude-main; doc-writer soạn nháp |
| 3 | Kiểm kê link skill/agent trong community/links.tsv, ghi thiếu/hỏng; không đổi nguồn ngoài quy trình. | Cao / vừa | check-runner |
| 4 | Rà custom/skills tìm quy trình lặp chưa được hướng dẫn; chỉ đề xuất skill mới khi có bằng chứng. | Vừa / nhỏ | doc-writer |
| 5 | Đánh giá hook CAD nhẹ sau khi định rõ sự kiện, lệnh, phạm vi, file bảo vệ. | Vừa / vừa | claude-main thiết kế; codex theo spec/gate |
| 6 | Rà nguồn plugin/MCP ghim theo cập nhật, sao, mã, license trước thay đổi. | Vừa / vừa | codex khảo sát theo spec; claude-main duyệt |
| 7 | Rà lệnh workspace về trùng/lỗi thời khi có bằng chứng cụ thể. | Thấp / nhỏ | doc-writer |

## 7. Kết luận của Claude (tổng giám đốc) – 2026-10-27

- Theo khung quyết định của skill chính thức, cấu hình STLab **về cơ bản đúng**: không thêm MCP/plugin/subagent khi chưa
  có tín hiệu (đúng nguyên tắc "bỏ mục không liên quan" của skill).
- **Đã làm ngay (Tuan duyệt):** hook PreToolUse `custom/hooks/guard_paths.py` đăng ký ở `../.claude/settings.json`,
  đọc `org/policy.yaml` mục `hang_rao` (cấm: mã cộng đồng đã clone, `.FCStd`, `.env`; hỏi: `org/`, `print.yaml`, báo
  cáo phụ huynh). Thử thật: ghi vào `community/<repo>/` bị chặn.
- **Việc 1 đã xác minh:** `usage_alert.py` đăng ký đúng 1 lần ở `~/.claude/settings.json` (StopFailure `rate_limit` +
  Notification `quota_auto_resume_*`); `guard_paths.py` chỉ ở settings dự án → không chạy trùng.
- Giới hạn còn lại: hàng rào chỉ xét Edit/Write; lệnh Bash ghi file không bị xét (executor đã có kiểm riêng trong
  `tools/delegate/delegate.py`).
- Bài học kèm theo: Codex trên Windows ghi tiếng Việt qua đường ống PowerShell 5.1 → mất dấu (3 lần). `delegate.py` nay
  dặn ghi bằng công cụ sửa file hoặc Python lệnh thuần ASCII (`\uXXXX`), và kiểm mã hóa sau mỗi vòng (hỏng → giao lại).
