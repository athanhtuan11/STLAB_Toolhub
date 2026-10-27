---
task: org-check
cwd: tools/org
allow: ["check_org.py"]
gate: "python tests/test_check_org.py"
timeout_min: 15
max_rounds: 2
executor: opencode
---

# Mục tiêu
Viết `check_org.py`: kiểm sổ nhân sự agent `org/agents.yaml` + `org/policy.yaml` (claude-workspace/org/) có hợp lệ
và KHỚP với cấu hình thật. Chỉ ĐỌC, không sửa file nào. Stdlib + yaml.
Lệnh: `python check_org.py [--org <thư mục chứa agents.yaml, policy.yaml>]` (mặc định `../../org` tính từ file script).
Đọc kỹ chú thích đầu `org/agents.yaml` và `org/policy.yaml` (đọc qua đường dẫn mặc định, hoặc test truyền --org).
Đường dẫn workspace = 2 cấp trên thư mục script (claude-workspace/), KHÔNG phụ thuộc --org.

# Luật (mỗi lỗi in 1 dòng `<MÃ> <id>: <mô tả>`; có lỗi → exit 1; không lỗi → in tóm tắt số agent theo tầng, exit 0)
- `E-ID-TRUNG`: id trùng.
- `E-THIEU-TRUONG`: thiếu trường bắt buộc: id, chuc_danh, tang, bao_cao_cho, loai, model, chi_phi, ky_nang, mang,
  muc_du_lieu, nguoi_duyet, gate, khi_het_han_muc, trang_thai, tu_ngay. `cli-executor` bắt buộc thêm `cooldown_h`;
  `claude-subagent` bắt buộc thêm `tool`.
- `E-ENUM`: tang ∈ {0,1,2,"tu-van"}; loai ∈ {claude-session, claude-subagent, cli-executor, mcp-advisor};
  chi_phi ∈ {claude-quota, free, tra-phi}; mang ∈ {none, web-search, connector};
  muc_du_lieu ∈ policy.muc_du_lieu.thu_tu; trang_thai ∈ {thu-viec, chinh-thuc, nghi}; gate ∈ {bat-buoc, khong, tuy-viec}.
- `E-BAO-CAO`: bao_cao_cho phải là id có trong sổ, hoặc "tuan" (chỉ cho tang 0).
- `E-CAP`: cấp số (0 < 1 < 2) – người được báo cáo phải có tang số NHỎ hơn; "tu-van" chỉ báo cáo cho tang 0.
- `E-TRA-PHI`: chi_phi = tra-phi bị cấm.
- `E-TU-DUYET`: nguoi_duyet = chính id.
- `E-DU-LIEU`: agent `chi_phi: free` và loai cli-executor/mcp-advisor có muc_du_lieu cao hơn
  `policy.nha_cung_cap_ngoai_toi_da` (theo thứ tự `thu_tu`).
- `E-SUBAGENT`: loai claude-subagent → phải có `custom/agents/<id>.md`; frontmatter `model` bằng `model`, tập `tools`
  (tách dấu phẩy, bỏ khoảng trắng) bằng tập `tool`.
- `E-DELEGATE`: so với `tools/delegate/delegate.py` (import theo đường dẫn bằng importlib, KHÔNG chạy main):
  tập id cli-executor có trang_thai ≠ nghi phải bằng tập `ORDER`; `cooldown_h` bằng `COOLDOWN_H[id]`;
  `khi_het_han_muc` của executor thứ i phải là `ORDER[i+1]` (cuối cùng: null).
- `E-POLICY`: mọi mẫu trong `FORBIDDEN` của delegate.py phải có trong `policy.duong_cam`.
- `khi_het_han_muc` khác null phải là id có trong sổ (`E-BAO-CAO`).

# Không làm
- Không sửa `tests/`, `org/`, `tools/delegate/`. Không cài gói.
