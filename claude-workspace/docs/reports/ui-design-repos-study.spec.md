---
task: study-ui-design-repos
cwd: docs/reports
allow: ["ui-design-repos-study.md"]
read: ["community/nextlevelbuilder-ui-ux-pro-max-skill", "community/voltagent-awesome-design-md",
       "community/nexu-io-open-design", "community/leonxlnx-taste-skill", "community/pbakaus-impeccable",
       "community/davidhdev-react-bits", "community/emilkowalski-skills", "community/nutlope-hallmark",
       "community/google-labs-code-design-md", "community/greensock-gsap-skills", "community/oso95-scroll-world",
       "community/davidhdev-canvas-ui", "studio"]
gate: 'python ../../tools/delegate/check_report.py ui-design-repos-study.md "## 1. Tong quan 12 repo" "## 2. DESIGN.md" "## 3. Kiem giao dien" "## 4. Hieu ung va component" "## 5. An toan" "## 6. Ap dung cho Toolhub" --max-todo 4 --min-files 20'
timeout_min: 35
max_rounds: 2
executor: codex
---

# Mục tiêu
Viết `ui-design-repos-study.md` (tiếng Việt có dấu, ≤ 240 dòng): đọc MÃ/tài liệu 12 repo thiết kế UI đã clone (chỉ
ĐỌC, không cài/chạy npx/npm/pip) để STLab nâng giao diện **STLAB Toolhub** (`studio/`, Flask) và hệ thiết kế
`studio/design/DESIGN.md` + `studio/design/tokens.json`. Máy yếu, Windows; Toolhub là Flask + HTML, không phải React.

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Tong quan 12 repo`: bảng: repo, loại (skill cho agent / bộ DESIGN.md / thư viện component / app), cần
  framework gì (React? Node?), dùng được với Flask+HTML không, file chính dẫn chứng.
- `## 2. DESIGN.md`: so định dạng `community/google-labs-code-design-md` + các mẫu trong
  `community/voltagent-awesome-design-md` với `studio/design/DESIGN.md` hiện có: thiếu mục nào, token nào.
- `## 3. Kiem giao dien`: quy tắc/lệnh phát hiện giao diện rập khuôn ("AI slop") của impeccable, taste-skill,
  hallmark, ui-ux-pro-max: tiêu chí cụ thể (tên quy tắc, dẫn file) áp được cho Toolhub.
- `## 4. Hieu ung va component`: react-bits, canvas-ui, gsap-skills, scroll-world, emilkowalski/skills: cái nào
  dùng được không cần React (CSS/vanilla JS), cái nào chỉ React; license (react-bits/canvas-ui MIT + Commons Clause).
- `## 5. An toan`: skill/agent nào có hook, script tự chạy, gọi mạng, cài gói – dẫn file. open-design: chạy gì.
- `## 6. Ap dung cho Toolhub`: ≤ 8 đề xuất (cái gì, dẫn file nguồn, công sức nhỏ/vừa/lớn); ưu tiên thứ làm bằng
  HTML/CSS thuần + DESIGN.md, không thêm build React.

# Quy tắc
- Dẫn đường dẫn FILE cụ thể trong backtick, tương đối claude-workspace (gate: ≥ 20 file tồn tại, ≤ 4 TODO).
- Không thấy → "không thấy"; không đoán, không chép số sao/ngày từ trí nhớ.
