---
task: delegate-registry
cwd: tools/delegate
allow: ["delegate.py"]
read: ["org", "tools/org"]
gate: "python tests/test_registry.py && python tests/test_delegate.py && cd ../org && python tests/test_check_org.py && python check_org.py"
timeout_min: 20
max_rounds: 2
executor: codex
---

# Mục tiêu
Bước 2 sổ nhân sự (`docs/reports/agent-org-roles-permissions.md` mục 7.5): `delegate.py` đọc `org/agents.yaml` +
`org/policy.yaml` (claude-workspace/org/, CHỈ ĐỌC – cấm sửa) thay các hằng số cứng; spec được ghi `ky_nang` thay tên
executor. Giữ phong cách file (chú thích tiếng Việt không dấu, gọn), stdlib + yaml.

# Yêu cầu
1. `ADAPTERS`: dict id → hàm dựng lệnh (giữ nguyên lệnh hiện có của codex/opencode/agy trong `command()`; model lấy
   từ sổ, không hằng số `OPENCODE_MODEL`/`AGY_MODEL`). `command(name, prompt)` vẫn tồn tại, dùng ADAPTERS.
2. `load_org(org_dir=None) -> dict(order, cooldown, model, forbidden, agents, policy)`; mặc định `WS/org`.
   - Thiếu/hỏng file → `ValueError` (không dùng mặc định ngầm).
   - `order`: chuỗi executor `loai: cli-executor`, `trang_thai: chinh-thuc`, `chi_phi` ≠ `tra-phi`: bắt đầu từ executor
     không bị ai trỏ tới qua `khi_het_han_muc`, đi theo `khi_het_han_muc`; người `nghi`/`thu-viec` bị bỏ qua (nối tiếp
     theo `khi_het_han_muc` của họ). Executor chinh-thuc không có trong ADAPTERS → `ValueError`.
   - `cooldown`: id → `cooldown_h`; `model`: id → `model`; `forbidden`: `policy.duong_cam` (danh sách).
3. Hằng module tính từ sổ lúc import: `ORDER`, `COOLDOWN_H`, `FORBIDDEN` (`tools/org/check_org.py` import chúng).
   Bỏ các hằng cứng cũ. Import lỗi sổ → để lỗi nổi lên (không nuốt).
4. `pick_queue(meta, cwd_rel, org) -> list[id]`:
   - `meta["executor"]` là id cụ thể → `[id]` nếu có trong sổ (kể cả `thu-viec`) VÀ có trong ADAPTERS, ngược lại `ValueError`.
   - `meta["ky_nang"]` (chuỗi hoặc list) → các id trong `order` có ĐỦ mọi kỹ năng đó, giữ thứ tự `order`; rỗng → `ValueError`.
   - `executor: auto` (hoặc không có cả hai) → `order`.
   - Mức dữ liệu: lớp của `cwd_rel` = khóa dài nhất trong `policy.muc_du_lieu.thu_muc` là tiền tố của `cwd_rel`
     (mặc định `policy.muc_du_lieu.mac_dinh`); bỏ executor có `muc_du_lieu` thấp hơn (theo `thu_tu`); không còn ai → `ValueError`.
5. `main()`/`run_task`: dùng `pick_queue` thay `ORDER if choice == "auto" else [choice]`; lỗi `ValueError` → in `LOI: ...`
   ra stderr, exit 1. `parse_spec` chấp nhận `ky_nang` (không bắt buộc). Giữ nguyên `REFUSE_CWD`, khóa, resume,
   handoff, ESCALATE. `--status` liệt kê executor theo `ORDER` + những id trong sổ.
6. Header đầu file: thêm 1–2 dòng về `ky_nang` và nguồn `org/`.

# Không làm
- Không sửa `org/`, `tools/org/`, `tests/`, `opencode.json`, `README.md`.
