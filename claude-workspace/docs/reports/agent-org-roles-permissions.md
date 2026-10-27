# Khảo sát tổ chức agent và quyền

Phạm vi: ghi nhận cấu hình có trong STLab và hai bộ nguồn cộng đồng; đây là khảo sát so sánh, không phải thiết kế hệ thống mới. Các giá trị không thấy trong nguồn được đánh dấu `TODO`.

## 1. Hien trang STLab

| Vai trò hiện có | Model | Tool được khai báo/dùng | Quyền ghi và chặn |
|---|---|---|---|
| Claude phiên chính, tổng giám đốc (theo mô hình vai trò ghi trong tài liệu) | Claude Opus; model cấu hình phiên hiện hành: TODO | Công cụ phiên Claude; danh sách đầy đủ: TODO | Quyết định, viết spec/gate và duyệt. Quyền hệ thống chi tiết: TODO. Nguồn: `CLAUDE.md`, `docs/model-routing.md`. |
| `check-runner`, quản lý chạy kiểm tra | `haiku` | `Bash, Read, Grep, Glob` | Chỉ chạy kiểm tra và báo tóm tắt; cấm sửa/lưu/xóa `.FCStd`, `.yaml`, `.py`, `.md`; không commit. Nguồn: `custom/agents/check-runner.md`. |
| `doc-writer`, quản lý tài liệu | `haiku` | `Read, Write, Edit, Glob, Grep, Bash`, deliberation `ask-gemini` | Ghi tài liệu được giao; cấm tự thêm số liệu kỹ thuật, cấm gửi dữ liệu phụ huynh, `.env`, key/mật khẩu, ảnh có người cho Gemini. Nguồn: `custom/agents/doc-writer.md`. |
| `git-scribe`, quản lý git | `haiku` | `Bash, Read, Grep` | Có thể commit/push nếu phiên chính giao rõ và kiểm tra đạt; chỉ add file trong phạm vi; cấm add `community/`, `.venv/`, báo cáo phụ huynh, `.env`/key. Nguồn: `custom/agents/git-scribe.md`. |
| Executor free `codex` qua delegate | Codex CLI; phiên bản và hạn mức hiện tại: TODO | `codex exec --sandbox workspace-write ...` | Làm trong `cwd`, chỉ file `allow`; không được đụng file cấm, không commit/push/reset/checkout; delegate kiểm tra file đổi và gate. Nguồn: `tools/delegate/delegate.py`, `tools/delegate/README.md`. |
| Executor free OpenCode Zen | `opencode/deepseek-v4.1-flash-free` | `opencode run` | `opencode.json` từ chối ghi ngoài thư mục làm việc, `.FCStd`, `print.yaml`, `community/`, `.env`, `parent-reports`; từ chối lệnh git nguy hiểm và xóa đệ quy. Tài liệu nói Windows không có sandbox hệ điều hành. Nguồn: `tools/delegate/opencode.json`, `tools/delegate/README.md`. |
| Executor dự phòng agy | `gemini-3.8-flash-high` trong delegate | Antigravity CLI (`agy`) | Được gọi với `--sandbox`, nhưng tài liệu nêu Windows không có sandbox hệ điều hành và `--sandbox` chỉ chặn lệnh terminal; hạn chế bổ sung và chỉ gửi bản sao. Nguồn: `tools/delegate/delegate.py`, `docs/model-routing.md`. |
| Tư vấn `ask-gpt`, `ask-gemini` | Codex/Gemini; model cụ thể tùy cấu hình | MCP deliberation | Đường deliberation chỉ đọc; không bật `allowImplement`; hạn chế gọi công cụ ghi được nêu trong `docs/model-routing.md`. Nguồn: `docs/model-routing.md`, `CLAUDE.md`. |

Delegate chạy executor theo thứ tự Codex → OpenCode → agy; `executor: auto` và giới hạn quota quyết định chuyển lượt. Cooldown Codex/OpenCode/agy trong mã chỉ là ước lượng, tài liệu đánh dấu TODO. Nguồn: `tools/delegate/delegate.py`, `tools/delegate/README.md`.

## 2. Claude Code subagent

Trong các file agent thật của STLab thấy frontmatter YAML có `name`, `description`, `tools`, `model`; ví dụ `custom/agents/check-runner.md`, `custom/agents/doc-writer.md`, `custom/agents/git-scribe.md`. Ví dụ model đều là `haiku`; danh sách tool khác nhau theo nhiệm vụ.

Các nguồn mẫu VoltAgent cũng có `name`, `description`, `tools`, `model`: ví dụ `community/voltagent-subagents/categories/01-core-development/api-designer.md` dùng `sonnet`, `auth-integration-engineer.md` dùng `sonnet`, còn `community/voltagent-subagents/categories/04-quality-security/code-reviewer.md` dùng `inherit`.

Giới hạn quan sát được: frontmatter liệt kê tool được phép theo agent; `description` nêu tình huống gọi. Các file đã xem không thể hiện mức quota, giới hạn mạng, thư mục sandbox, chủ thể duyệt hay gate thực thi thống nhất. Không suy ra các trường này từ frontmatter; chi tiết khác: `TODO`. Nguồn: ba file `custom/agents/*.md` và ba ví dụ VoltAgent ở trên.

## 3. knowledge-work-plugins

Nguồn tổ chức theo chức năng công việc: mỗi thư mục plugin là một vai trò/miền như `engineering/`, `finance/`, `sales/`; danh sách vai trò và connector được mô tả trong `community/anthropics-knowledge-work-plugins/README.md`.

README mô tả cấu trúc thành phần phổ biến: `.claude-plugin/plugin.json` là manifest, `.mcp.json` khai báo kết nối công cụ, `commands/` chứa slash command được gọi rõ ràng, `skills/` chứa tri thức và quy trình tự áp dụng khi phù hợp. Nguồn: `community/anthropics-knowledge-work-plugins/README.md`.

Ví dụ plugin Engineering có manifest `name`, `version`, `description`, `author` tại `community/anthropics-knowledge-work-plugins/engineering/.claude-plugin/plugin.json`; `.mcp.json` khai báo máy chủ Slack, Linear, Asana, Atlassian, Notion, GitHub, PagerDuty và Datadog cùng cấu hình kết nối tại `community/anthropics-knowledge-work-plugins/engineering/.mcp.json`. Kết nối Gmail/Calendar có URL rỗng trong file đó, nên không khẳng định chúng đang hoạt động.

README gốc nói plugin gom skills, connectors, slash commands và sub-agents theo vai trò; cấu trúc thư mục minh họa không liệt kê thư mục agent. Plugin Engineering được xem có `skills/` và tài liệu connector, nhưng agent cụ thể trong plugin này: không thấy trong cấu trúc README đã xem. Nguồn: `community/anthropics-knowledge-work-plugins/README.md`, `community/anthropics-knowledge-work-plugins/engineering/README.md`.

## 4. VoltAgent subagents

README mô tả bộ sưu tập agent phân loại vào 10 nhóm; đường dẫn `categories/` cho thấy nhóm như `01-core-development`, `02-language-specialists`, `04-quality-security`, `09-meta-orchestration`, `10-research-analysis`. Mỗi agent là file Markdown có frontmatter và nội dung nhiệm vụ. Nguồn: `community/voltagent-subagents/README.md`, `community/voltagent-subagents/categories/`.

Giới hạn tool theo vai trò được thể hiện trong trường `tools`: hai agent phát triển đã xem khai báo `Read, Write, Edit, Bash, Glob, Grep`, tại `community/voltagent-subagents/categories/01-core-development/api-designer.md` và `auth-integration-engineer.md`. Agent đánh giá mã trong nhóm chất lượng cũng khai báo cùng bộ tool tại `community/voltagent-subagents/categories/04-quality-security/code-reviewer.md`. Nghĩa vụ chuyên môn nằm tiếp trong phần chỉ dẫn của từng file.

Trong ba mẫu này, `model` có giá trị cụ thể `sonnet` hoặc giá trị kế thừa `inherit`. Chỉ từ các file mẫu không thấy sandbox, allowlist đường dẫn, mạng hay hạn mức quota: `TODO`. README hướng dẫn cài file vào `~/.claude/agents/` hoặc `.claude/agents/`; đây là hướng dẫn của repo cộng đồng, không phải thao tác đã thực hiện. Nguồn: `community/voltagent-subagents/README.md`.

## 5. Codex va OpenCode

`tools/delegate/delegate.py` gọi Codex bằng `exec --sandbox workspace-write --skip-git-repo-check -c features.prefer_mxc=true -`; vì vậy cấu hình lệnh quan sát được đặt sandbox ở chế độ `workspace-write`. Tài liệu không nêu trong các file đã khảo sát cơ chế quyền chi tiết hơn của Codex: `TODO`.

`tools/delegate/opencode.json` đặt `external_directory: deny`, `webfetch: deny`; quy tắc `edit` mặc định allow nhưng deny cho các mẫu file/thư mục cấm, còn `bash` mặc định allow và deny một số lệnh git/xóa. `tools/delegate/README.md` lưu ý OpenCode trên Windows không có sandbox hệ điều hành; chính sách JSON là lớp hạn chế cấu hình ứng dụng, không phải sandbox hệ điều hành.

Ở tầng delegate, `cwd`, `allow`, `gate`, timeout, số vòng và executor được đọc từ spec; cấm ghi ngoài allow được kiểm sau chạy và file cấm được theo dõi. Tài liệu tuyên bố gate phải PASS trước khi nhận kết quả, và thay đổi không được tự hoàn tác. Nguồn: `tools/delegate/README.md`, `tools/delegate/delegate.py`.

## 6. Bang thuoc tinh

Bảng dưới đây tổng hợp các thuộc tính thấy cần ghi nhận khi mô tả một hồ sơ agent; đây là phép đối chiếu nguồn, không xác lập cấu hình mới. `TODO` nghĩa là giá trị cụ thể chưa thấy.

| Thuộc tính | Ý nghĩa | Ví dụ có trong nguồn | Dẫn file |
|---|---|---|---|
| Vai trò/nhiệm vụ | Công việc và phạm vi đầu ra | Chạy kiểm tra; viết tài liệu; git; nhóm Engineering | `custom/agents/check-runner.md`, `custom/agents/doc-writer.md`, `community/anthropics-knowledge-work-plugins/engineering/README.md` |
| Cấp/báo cáo cho ai | Vị trí trong luồng giao việc | Claude tổng giám đốc, Haiku quản lý, executor nhân viên | `tools/delegate/README.md`, `docs/model-routing.md` |
| Model | Model được chọn hoặc kế thừa | `haiku`, `sonnet`, `inherit`, `opencode/deepseek-v4.1-flash-free` | `custom/agents/check-runner.md`, `community/voltagent-subagents/categories/01-core-development/api-designer.md`, `community/voltagent-subagents/categories/04-quality-security/code-reviewer.md`, `tools/delegate/delegate.py` |
| Chi phí/hạn mức | Nguồn quota và thời điểm giới hạn | Claude Pro; cooldown mã có chú thích chưa xác nhận; hạn mức Zen TODO | `docs/model-routing.md`, `tools/delegate/delegate.py`, `tools/delegate/README.md` |
| Tool được dùng | Công cụ agent được khai báo hoặc lệnh gọi | `Read, Write, Edit, Bash, Glob, Grep`; `codex exec` | `custom/agents/doc-writer.md`, `community/voltagent-subagents/categories/01-core-development/api-designer.md`, `tools/delegate/delegate.py` |
| Đường ghi được | Vị trí tạo/sửa được cho phép | `cwd` và glob `allow` trong spec; OpenCode cấm external directory | `tools/delegate/README.md`, `tools/delegate/opencode.json` |
| Cấm | File, lệnh hoặc dữ liệu không được chạm | `.FCStd`, `print.yaml`, `community/`, `.env`; lệnh commit/push/reset/checkout | `tools/delegate/delegate.py`, `tools/delegate/opencode.json`, `tools/delegate/README.md` |
| Mạng/kết nối | Khả năng gọi mạng hoặc connector | OpenCode `webfetch: deny`; plugin Engineering liệt kê MCP Slack/Linear… | `tools/delegate/opencode.json`, `community/anthropics-knowledge-work-plugins/engineering/.mcp.json` |
| Dữ liệu được xem/gửi | Ranh giới dữ liệu đầu vào và chuyển ra ngoài | agy chỉ nhận bản sao; loại trừ dữ liệu phụ huynh và secrets | `docs/model-routing.md`, `custom/agents/doc-writer.md`, `tools/delegate/delegate.py` |
| Người duyệt | Chủ thể quyết định nhận kết quả | Phiên Claude chính duyệt; executor không tự chọn thông số | `tools/delegate/README.md`, `docs/model-routing.md` |
| Gate | Điều kiện xác nhận đầu ra | `gate` trong spec; exit 0 là PASS | `tools/delegate/README.md` |
| Thoát khi lỗi | Handoff, retry/chuyển model và báo lỗi | 429/quota làm chuyển executor; `handoff.md` nếu chưa PASS | `tools/delegate/delegate.py`, `tools/delegate/README.md` |
| Lịch sử/kiểm toán | Dấu vết chạy và thay đổi | `result.json`, log lượt chạy, `git status` sau chạy | `tools/delegate/README.md`, `tools/delegate/delegate.py` |
| Manifest/phiên bản | Nhận diện gói và cấu hình kết nối | Engineering `name`, `version`; MCP servers | `community/anthropics-knowledge-work-plugins/engineering/.claude-plugin/plugin.json`, `community/anthropics-knowledge-work-plugins/engineering/.mcp.json` |

## 7. Thiết kế đề xuất (Claude, tổng giám đốc) – chờ Tuan duyệt

**Vấn đề:** thông tin "nhân sự" đang rải ở 5 nơi (frontmatter `custom/agents/*.md`, `ORDER`/`COOLDOWN_H`/`command()` trong
`delegate.py`, `opencode.json`, bảng CLAUDE.md, memory). Thêm agent mới phải sửa nhiều chỗ, dễ lệch; cộng đồng (mục 2–4)
cũng không có trường cho hạn mức, dữ liệu được xem, người duyệt, gate.

### 7.1 Sổ nhân sự: `org/agents.yaml` (một nguồn duy nhất)
Mỗi agent một hồ sơ:

| Trường | Ví dụ | Ghi chú |
|---|---|---|
| `id`, `chuc_danh` | `opencode-zen`, "Nhân viên lập trình" | |
| `tang` | 0 giám đốc · 1 quản lý · 2 nhân viên · `tu-van` | |
| `bao_cao_cho` | `claude-main` | ai giao việc + nhận kết quả |
| `loai` | `claude-session` · `claude-subagent` · `cli-executor` · `mcp-advisor` | quyết định cách gọi |
| `model`, `chi_phi` | `deepseek-v4.1-flash-free`, `free` | `claude-quota` / `free`; `tra-phi` = cấm (chỉ Claude Pro) |
| `ky_nang` | `[code, cad-script, test]` | dùng để định tuyến |
| `tool`, `ghi_duoc` | `[Read, Bash]`, theo `allow` của spec | |
| `mang` | `none` · `web-search` · `connector` | |
| `muc_du_lieu` | `public-tech` · `internal` · `customer` | **nhà cung cấp ngoài tối đa `internal`**; `parent-reports` không ai ngoài Claude |
| `nguoi_duyet`, `gate` | `claude-main`, `bat-buoc` | không agent nào tự duyệt việc của mình |
| `khi_het_han_muc`, `cooldown_h` | `agy`, `1` | thay `ORDER`/`COOLDOWN_H` cứng trong mã |
| `trang_thai`, `tu_ngay` | `thu-viec` · `chinh-thuc` · `nghi` | |

Quy tắc chung đặt ở `org/policy.yaml`: đường cấm (gộp `FORBIDDEN` + `opencode.json`), phân loại dữ liệu theo thư mục,
"chỉ tầng 0 quyết kích thước/an toàn", "chỉ `git-scribe` commit", "executor không được sửa `org/**`".

### 7.2 Luồng giao việc
Spec ghi `ky_nang: code` (không cần ghi tên executor) → `delegate.py` chọn agent `chinh-thuc` có kỹ năng đó, chưa hết hạn
mức, `muc_du_lieu` đủ cho thư mục `cwd`, ưu tiên `free` trước, rồi theo thành tích (7.4).

### 7.3 Tuyển nhân viên mới (onboarding)
Thêm hồ sơ `trang_thai: thu-viec` → chạy bài thử bắt buộc (selftest + 1 việc mẫu có gate, như pilot Knuckle_L) →
ghi kết quả vào hồ sơ → **Tuan duyệt** → `chinh-thuc`. Nghỉ việc: `nghi` (giữ hồ sơ để tra lịch sử).

### 7.4 Đánh giá thành tích
`delegate.py` cộng dồn mỗi agent: số việc, % PASS vòng 1, thời gian TB, số lần 429 →
`%LOCALAPPDATA%/stlab-usage/agent-stats.json`; dùng xếp thứ tự chọn và để Tuan xem.

### 7.5 Lộ trình (mỗi bước có gate, không đổi hành vi trước khi kiểm)
1. `org/agents.yaml` + `org/policy.yaml` + `check_org.py` (kiểm khớp với `custom/agents/*.md` và `delegate.py`) – nhỏ.
2. `delegate.py` đọc sổ thay `ORDER`/`COOLDOWN_H`/lệnh cứng; spec chấp nhận `ky_nang` – vừa.
3. Thống kê thành tích + định tuyến theo thành tích – nhỏ.
4. Mẫu "tuyển nhân viên" + bảng CLAUDE.md sinh từ sổ – nhỏ.

**Không làm:** daemon/swarm điều phối tự động, agent tự nâng quyền, agent tự sửa sổ nhân sự, cài Ruflo (xem
`docs/reports/agent-orchestration-ai-memory-ruflo.md` mục 4).
