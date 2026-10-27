---
task: study-ai-memory-ruflo
cwd: docs/reports
allow: ["agent-orchestration-ai-memory-ruflo.md"]
gate: 'python ../../tools/delegate/check_report.py agent-orchestration-ai-memory-ruflo.md "## 1. ai-memory" "## 2. ruflo" "## 3. So voi tools/delegate" "## 4. Rui ro an toan" "## 5. De xuat"'
timeout_min: 30
max_rounds: 2
executor: codex
---

# Mục tiêu
Viết `agent-orchestration-ai-memory-ruflo.md` (tiếng Việt có dấu, ≤ 250 dòng): nghiên cứu MÃ NGUỒN 2 repo đã clone
(chỉ ĐỌC, KHÔNG cài, KHÔNG chạy npx/npm/cargo/script của chúng) để STLab học cách điều phối nhiều agent.
- `../../community/akitaonrails-ai-memory/` (Rust, bộ nhớ chung cho agent lập trình)
- `../../community/ruvnet-ruflo/` (lớp điều phối quanh Claude Code/Codex; repo rất lớn → đọc README, package.json,
  điểm vào CLI, thư mục hooks/plugins/mods, phần tích hợp Claude Code/Codex; bỏ qua ví dụ/test/asset)
- Hệ hiện tại để so: `../../tools/delegate/delegate.py`, `../../tools/delegate/README.md`

# Mục bắt buộc (đúng tiêu đề)
`## 1. ai-memory`, `## 2. ruflo`: mỗi repo trả lời:
  a) Kiến trúc chính (thành phần, luồng dữ liệu). b) Bàn giao việc giữa Claude ↔ Codex/agent khác thế nào.
  c) Lưu trạng thái + chạy tiếp sau khi tiến trình chết/mất điện. d) Chống chạy trùng/đụng nhau giữa nhiều phiên.
  e) Định tuyến theo hạn mức/429. f) Định dạng bộ nhớ. g) Cài đặt cần gì (Node/Rust, Windows có chạy không),
  gửi dữ liệu ra mạng không, cài hook/quyền gì vào Claude Code.
`## 3. So voi tools/delegate`: bảng so a–g với delegate.py.
`## 4. Rui ro an toan`: hook, quyền, mạng, telemetry, lệnh tự chạy – dẫn file cụ thể.
`## 5. De xuat`: ≤ 8 ý có thể học cho delegate.py, mỗi ý: cái gì, dẫn file nguồn, công sức ước (nhỏ/vừa/lớn).
  Không đề xuất cài nguyên khối. Máy STLab yếu, chỉ trả Claude Pro, không model local.

# Quy tắc dẫn nguồn
- Mọi khẳng định quan trọng phải dẫn đường dẫn trong backtick, viết TƯƠNG ĐỐI theo claude-workspace, ví dụ
  `community/ruvnet-ruflo/README.md`, `tools/delegate/delegate.py` (gate kiểm mọi đường dẫn có tồn tại; ≥ 10 đường dẫn).
- Không biết/không thấy trong mã → ghi `TODO` hoặc "không thấy", KHÔNG đoán. Không chép số sao/ngày từ trí nhớ.
