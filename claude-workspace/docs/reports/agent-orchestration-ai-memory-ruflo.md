# Nghiên cứu điều phối agent: ai-memory và Ruflo

Phạm vi: đọc mã nguồn đã clone; không cài đặt hay chạy lệnh của hai dự án. Nhận xét tính năng dựa trên tệp dẫn nguồn, không coi số liệu quảng bá trong README là kết quả kiểm chứng.

## 1. ai-memory

- **a) Kiến trúc và luồng:** binary Rust chia crate core/store/wiki/hooks/MCP/CLI/workstream; hook gửi quan sát đã làm sạch vào server, writer ghi SQLite và wiki Markdown; MCP/CLI truy vấn, SessionEnd tạo trang phiên và handoff. Wiki Markdown là nguồn chuẩn, SQLite là chỉ mục/trạng thái dẫn xuất: `community/akitaonrails-ai-memory/Cargo.toml`, `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`.
- **b) Bàn giao:** hook SessionEnd tạo handoff có kiểu; agent sau lấy brief giới hạn rồi tìm kiếm thêm. Handoff có owner và được claim một lần theo mô tả dự án; có adapter chạy Codex/Claude cùng workstream: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`, `community/akitaonrails-ai-memory/crates/ai-memory-core/src/handoff.rs`, `community/akitaonrails-ai-memory/crates/ai-memory-workstream/src/lib.rs`.
- **c) Tiếp tục sau chết tiến trình:** quan sát có spool cục bộ và khóa idempotency; replay sự kiện chưa hoàn tất phục hồi hiệu ứng. Session thiếu SessionEnd có thể kết thúc theo tick idle nếu cấu hình. Không thấy phục hồi nguyên tiến trình/model call dở dang; tiếp tục dựa vào trang/handoff và transcript harness: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`, `community/akitaonrails-ai-memory/crates/ai-memory-hooks/src/capture_policy.rs`.
- **d) Chống trùng/đụng:** idempotency key theo project/sự kiện, khóa gate cho replay chồng lấn; handoff claim có chủ sở hữu và transaction. Đây là chống trùng dữ liệu/claim, không thấy khóa độc quyền một thư mục làm việc cho mọi phiên: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`, `community/akitaonrails-ai-memory/crates/ai-memory-store/tests/suite/handoff_ownership.rs`.
- **e) Hạn mức/429:** hook không chặn luồng làm việc; server trả 429 khi quá tải. Spool drain dừng thử endpoint đang nghẽn, không tính lần đó là lỗi retry; không thấy tự chuyển sang model/provider khác: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`.
- **f) Bộ nhớ:** wiki git-backed bằng Markdown/frontmatter; SQLite FTS/entity/link và embedding tùy chọn làm chỉ mục. Handoff là bản ghi có kiểu trong store, không phải văn bản tự do đơn thuần: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`, `community/akitaonrails-ai-memory/crates/ai-memory-core/src/handoff.rs`, `community/akitaonrails-ai-memory/crates/ai-memory-wiki/src/wiki.rs`.
- **g) Cài đặt, mạng, quyền:** Rust 1.95+; README nêu Linux/macOS, WSL2 hỗ trợ và Windows native thử nghiệm. Cần build/cài binary để vận hành; hook/MCP gửi sự kiện tới server cấu hình, LLM/embedding chỉ khi bật provider. Setup có thể gắn MCP, hook và Agent Skills vào agent; cần xem plan và quyền cấu hình trước khi áp dụng. Không thấy bằng chứng telemetry bắt buộc trong các tệp đã đọc: `community/akitaonrails-ai-memory/Cargo.toml`, `community/akitaonrails-ai-memory/README.md`, `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`.

## 2. ruflo

- **a) Kiến trúc và luồng:** gói Node CLI lớp ngoài chuyển tiếp tới CLI v3; CLI, MCP, plugins/hooks, agent/swarm, memory và provider adapters. Luồng tổng quát prompt/hook → định tuyến/task/swarm → agent/provider → memory. README có tuyên bố quy mô và khả năng rộng; chưa xác nhận mọi tính năng quảng bá trong mã: `community/ruvnet-ruflo/package.json`, `community/ruvnet-ruflo/bin/cli.js`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/index.ts`, `community/ruvnet-ruflo/README.md`.
- **b) Bàn giao Claude ↔ Codex:** plugin Claude khai báo hook, MCP và agent; workspace có adapter Codex riêng, gói CLI cũng chứa tích hợp Codex. Có thể trao task qua workflow/swarm và chia sẻ memory. Không thấy giao thức handoff claim-once thống nhất trực tiếp Claude↔Codex trong các điểm vào đã khảo sát: `community/ruvnet-ruflo/plugins/ruflo-core/hooks/hooks.json`, `community/ruvnet-ruflo/v3/@claude-flow/codex/package.json`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/commands/task.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/commands/memory.ts`.
- **c) Trạng thái sau crash:** có lớp memory, claims và task command; claim service có lưu/đọc trạng thái. README mô tả swarm/daemon, nhưng tính tiếp tục chính xác theo từng trạng thái task cần đối chiếu cấu hình runtime; không khẳng định mọi task tự resume sau mất điện: `community/ruvnet-ruflo/v3/@claude-flow/cli/src/services/claims-store.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/services/claim-service.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/commands/task.ts`.
- **d) Chống chạy trùng:** có dịch vụ claims và thao tác phối hợp; claims không đồng nghĩa khóa workspace/file ở mọi workflow. Cần cấu hình phạm vi/TTL trong runtime: `community/ruvnet-ruflo/v3/@claude-flow/cli/src/services/claims-store.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/commands/claims.ts`.
- **e) Hạn mức/429:** có retry, rate limiter và bộ phân loại lỗi nhà cung cấp; phân biệt rate limit với quota ở mã lỗi. Không thấy bằng chứng mọi workflow task tự chuyển executor Claude Pro sang nguồn khác; model/API key phụ thuộc provider được cấu hình: `community/ruvnet-ruflo/v3/@claude-flow/cli/src/production/rate-limiter.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/production/retry.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/funnel/credit-errors.ts`.
- **f) Bộ nhớ:** README mô tả AgentDB/vector memory; CLI có dịch vụ memory, SQLite và các thành phần truy hồi. Định dạng cụ thể thay đổi theo backend; không thấy một định dạng Markdown duy nhất làm nguồn chuẩn cho toàn Ruflo: `community/ruvnet-ruflo/README.md`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/commands/memory.ts`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/memory/shared-sqlite.ts`.
- **g) Cài đặt, mạng, quyền:** Node >=20 theo package gốc; CLI Codex yêu cầu Node >=18 (điều kiện workspace chưa giải quyết ở đây); tích hợp qua npm/npx/MCP. Plugin hooks chạy lệnh cục bộ và shim có fallback `npx --prefer-offline`, do đó có thể truy cập mạng khi thiếu CLI cục bộ; provider, MCP và cập nhật cũng có thể gửi dữ liệu ra ngoài tùy cấu hình. Native Windows: plugin core dùng bootstrap Node, nhưng package plugin cũ khai báo hook POSIX-only và lỗi đã biết. Hooks có PreToolUse/PreCommand, ghi telemetry best-effort và một hook PermissionRequest auto-allow tool MCP; đây là quyền đáng xem xét kỹ: `community/ruvnet-ruflo/package.json`, `community/ruvnet-ruflo/v3/@claude-flow/codex/package.json`, `community/ruvnet-ruflo/plugins/ruflo-core/hooks/hooks.json`, `community/ruvnet-ruflo/plugin/hooks/hooks.json`, `community/ruvnet-ruflo/plugin/scripts/ruflo-hook.cjs`.

## 3. So voi tools/delegate

| Tiêu chí | ai-memory | Ruflo | `tools/delegate` hiện tại |
|---|---|---|---|
| a) Kiến trúc | Server + hook/MCP + wiki/store | CLI/MCP/plugin + swarm/provider | Python đọc spec, chọn executor, chạy gate: `tools/delegate/delegate.py` |
| b) Bàn giao | Handoff claim-once, brief + search | Task/swarm/plugins; nhiều thành phần, giao thức qua Claude-Codex cần xác minh | Claude viết spec, Codex/OpenCode/agy thi hành, JSON kết quả: `tools/delegate/README.md`, `tools/delegate/delegate.py` |
| c) Chạy tiếp | Spool/idempotency, trang phiên; không phục hồi model call | Claims/task/memory; resume toàn task chưa chứng minh mặc định | Log/state/result theo run; status tìm tiến trình chết nhưng tự resume chưa thấy: `tools/delegate/delegate.py` |
| d) Trùng/va chạm | Idempotency + handoff ownership; không workspace lock chung | Claims; không mặc định khóa file/workspace toàn cục | Một lock mỗi cwd, PID chết mở khóa: `tools/delegate/delegate.py` |
| e) 429 | Dừng/retry spool endpoint; không đổi provider | Có retry/rate limiter ở một số lớp | So khớp 429/quota, đánh dấu cooldown rồi chọn executor kế tiếp: `tools/delegate/delegate.py` |
| f) Bộ nhớ | Markdown chuẩn + SQLite dẫn xuất | Backend memory đa dạng, gồm SQLite/vector | Không có bộ nhớ agent chung; spec/log/result JSON: `tools/delegate/README.md`, `tools/delegate/delegate.py` |
| g) Cài đặt/mạng/quyền | Rust, server/hook; LLM tùy chọn | Node và plugin/MCP; hook có quyền, mạng tùy cấu hình | Python, yaml và executor ngoài; truyền prompt tới executor đã chọn; cwd/allow/forbidden được kiểm tra: `tools/delegate/delegate.py`, `tools/delegate/opencode.json` |

## 4. Rui ro an toan

- **Nặng nhất (Claude kiểm lại 2026-10-27):** hook PreToolUse của Ruflo core trả `{"permission":"allow"}` cho Bash/Write/Edit (với Codex: exit 0 = cho phép vô điều kiện), luôn exit 0 kể cả khi lỗi, fallback `npx --prefer-offline`, telemetry chạy ở mọi nhánh → cài vào sẽ **bỏ qua bước duyệt quyền** của Claude Code: `community/ruvnet-ruflo/plugins/ruflo-core/hooks/hooks.json` (dòng `description`), `community/ruvnet-ruflo/plugins/ruflo-core/scripts/ruflo-hook.cjs`.
- Plugin cũ gọi shell `jq`, `xargs`, shim `.sh`; JSON tự cảnh báo chỉ POSIX và Windows native hỏng. Shim cũ có fallback `npx`; cài hoặc gọi khi chưa có binary có thể truy cập registry: `community/ruvnet-ruflo/plugin/hooks/hooks.json`, `community/ruvnet-ruflo/plugin/scripts/ruflo-hook.cjs`.
- Telemetry/metrics được gọi từ hook sau lệnh; hook lẫn CLI có thể kết nối provider, MCP hay registry tùy chức năng. Không thể kết luận dữ liệu nào rời máy trong cấu hình cụ thể nếu chưa kiểm toàn cấu hình: `community/ruvnet-ruflo/plugins/ruflo-core/hooks/hooks.json`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/index.ts`.
- Ruflo có nhiều script npm và plugin có thể chạy mã khi cài; nghiên cứu này không chạy chúng. Kiểm tra các scripts trong package manifest trước khi cân nhắc dùng: `community/ruvnet-ruflo/package.json`.
- ai-memory hook gửi JSON sự kiện lên server và có thể ghi nhận prompt/tool; privacy boundary làm sạch trước lưu. Bật provider LLM/embedding phát sinh gửi nội dung tới dịch vụ đã cấu hình: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`.
- `delegate.py` cũng chạy subprocess executor/gate với prompt, có thể gửi nội dung ngoài máy tùy executor; `opencode.json` giới hạn một phần thao tác file nhưng không phải sandbox OS trên Windows: `tools/delegate/delegate.py`, `tools/delegate/opencode.json`, `tools/delegate/README.md`.

## 5. De xuat

1. Thêm handoff JSON có task, owner, trạng thái, đầu ra và claim một lần; nguồn: `community/akitaonrails-ai-memory/crates/ai-memory-core/src/handoff.rs`; công sức: vừa.
2. Lưu trạng thái run có thể đọc lại và chỉ tiếp tục run thiếu result sau kiểm tra người dùng; nguồn: `tools/delegate/delegate.py`, `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`; công sức: vừa.
3. Thêm idempotency key cho sự kiện/result để retry không nhân đôi; nguồn: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`; công sức: vừa.
4. Giữ wiki Markdown nhỏ làm bộ nhớ dùng chung, có SQLite là tùy chọn sau này; nguồn: `community/akitaonrails-ai-memory/docs/ARCHITECTURE.md`; công sức: vừa.
5. Tách nhận diện 429/quota, trạng thái cooldown và thử executor kế tiếp thành module có cấu hình; nguồn: `tools/delegate/delegate.py`, `community/ruvnet-ruflo/v3/@claude-flow/cli/src/funnel/credit-errors.ts`; công sức: nhỏ.
6. Giữ hook tối thiểu, opt-in, không auto-allow lệnh ghi/chạy; nguồn: `community/ruvnet-ruflo/plugins/ruflo-core/hooks/hooks.json`; công sức: nhỏ.
7. Ghi rõ trong result executor nào chạy, file nào đổi, gate nào đạt và lý do retry; nguồn: `tools/delegate/delegate.py`; công sức: nhỏ.

Đề xuất phù hợp với máy yếu và chỉ có Claude Pro: không cần vector DB, swarm daemon hay model local; ưu tiên file văn bản, một executor tại một thời điểm và gate hiện có.

## 6. Kết luận của Claude (tổng giám đốc) – chờ Tuan duyệt

- **Ruflo: KHÔNG cài.** Hook tự cho phép mọi lệnh ghi/chạy (mục 4) trái nguyên tắc duyệt quyền; nặng (Node, swarm,
  daemon), không hợp máy yếu. Chỉ giữ clone để đọc.
- **ai-memory: không cài** (cần server Rust, Windows native còn thử nghiệm), nhưng **học ý**: handoff có chủ sở hữu, claim
  một lần; spool + idempotency khi mất điện.
- Bộ nhớ chung: STLab đã có memory Claude + CLAUDE.md + `docs/` → không thêm wiki/SQLite (đề xuất 4 bỏ).
- **Nên làm (nhỏ, giá trị cao)** cho `tools/delegate/delegate.py`:
  1. `--resume <run>`: chạy lại run bị cắt ngang từ `state.json` (spec đã lưu), kèm log vòng trước làm ngữ cảnh – đúng sự
     cố cúp điện 2026-10-27 (đề xuất 2).
  2. `--status` xét cả file khóa: run cũ thiếu `state.json` nhưng tiến trình còn sống không bị báo nhầm "interrupted"
     (lỗi gặp thật 2026-10-27).
  3. `handoff.md` trong run_dir khi FAIL/BLOCKED: đã thử gì, gate lỗi gì, file đã đổi → executor/phiên sau đọc tiếp
     thay vì làm lại (ý từ đề xuất 1, bản file văn bản, không claim/DB).
- Đề xuất 3, 5, 6, 7: phần lớn `delegate.py` đã có (khóa cwd, cooldown 429, result.json) → không làm thêm.
