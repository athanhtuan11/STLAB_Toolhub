---
task: org-gen-table
cwd: tools/org
allow: ["gen_table.py"]
read: ["org", "CLAUDE.md"]
gate: "python tests/test_gen_table.py && python tests/test_check_org.py"
timeout_min: 15
max_rounds: 2
executor: codex
---

# Mục tiêu
Bước 4 sổ nhân sự: `gen_table.py` sinh bảng phân việc trong CLAUDE.md từ `org/agents.yaml`, để bảng luôn khớp sổ.
Stdlib + yaml. Đọc `tests/test_gen_table.py` để biết đúng hành vi.

# Yêu cầu
- `python gen_table.py [--org <dir>] [--claude <file>] (--check | --write)`; mặc định `--org` = `../../org`,
  `--claude` = `../../CLAUDE.md` (tính từ file script).
- Bảng Markdown nằm giữa `<!-- org-table:start -->` và `<!-- org-table:end -->` (thay toàn bộ phần giữa, giữ nguyên
  phần ngoài, ghi UTF-8 không BOM, giữ kiểu xuống dòng của file).
- Cột: `Tầng | Chức danh | Agent | Model | Chi phí | Kỹ năng | Báo cáo cho | Trạng thái`. Tầng hiển thị:
  0 → "0 – Giám đốc", 1 → "1 – Quản lý", 2 → "2 – Nhân viên", "tu-van" → "Tư vấn". Agent ghi `` `id` ``.
  Kỹ năng nối bằng ", ". Thứ tự: theo tầng (0, 1, 2, tư vấn) rồi theo thứ tự trong sổ.
- `--check`: bảng hiện tại khớp → exit 0, khác → in "LECH" exit 1; thiếu marker → exit 2. `--write` idempotent.
- Dòng ngay sau bảng (vẫn trong marker): `_Sinh tự động từ org/agents.yaml bằng tools/org/gen_table.py – không sửa tay._`

# Không làm
- Không sửa `tests/`, `org/`, `CLAUDE.md`, `check_org.py`.
