---
task: model-study-measure-features
cwd: tools/model-study
allow: ["measure_features.py"]
read: ["test_features.py", "measure_holes.py", "study_3mf.py", "pyproject.toml"]
gate: '.venv\Scripts\python.exe test_features.py && .venv\Scripts\python.exe test_holes.py'
executor: auto
timeout_min: 40
max_rounds: 3
---

# Mục tiêu
Tuan (2026-10-30): reverse engineering model in 3D đã chạy được (MakerWorld…) để rút **thông số chi tiết chính xác**
cho kho dữ liệu, để AI thiết kế sau này không sai lệch. `measure_holes.py` cũ chỉ đo lỗ theo trục x/y/z. Viết công cụ
mới `measure_features.py`: STL → lỗ/boss/cung trụ theo **trục bất kỳ** + lỗ bậc, có sai số và độ tin cậy.
Hành vi đúng = `test_features.py` (KHÔNG sửa test). `test_holes.py` cũ vẫn PASS (không sửa `measure_holes.py`).

# Môi trường
- Chạy bằng `.venv\Scripts\python.exe` (uv, `pyproject.toml` đã có: numpy, trimesh, pyransac3d, manifold3d, scipy).
  KHÔNG cài thêm gói, không sửa `pyproject.toml`/`uv.lock`.

# Yêu cầu – `measure_features.py`
## API
- `measure_mesh(mesh: trimesh.Trimesh) -> dict`:
  `{"units": "mm", "n_faces": int, "features": [...], "groups": [...]}`.
- Mỗi feature: `id` (int, duy nhất), `type` ∈ `hole | boss | arc`, `d_mm`, `axis` (vector đơn vị 3 số),
  `center` (điểm trên trục, giữa chiều dài, 3 số), `length_mm` (chiều dài phần mặt trụ dọc trục), `coverage_deg` (góc
  bao của mặt trụ quanh trục, 0–360), `rms_mm` (sai số khớp), `confidence` (0–1), `n_faces`. Riêng `hole`: `through`
  (bool). Làm tròn 3–4 chữ số.
- Group lỗ bậc: `{"type": "counterbore", "members": [id_lo_nho, id_lo_lon], "depth_mm": chiều dài lỗ lớn,
  "axis": ..}` khi 2 lỗ đồng trục (lệch trục ≤ 0,05 mm, góc ≤ 1°), nối nhau bằng mặt vành khuyên phẳng.

## Thuật toán (gợi ý, kết quả mới là chuẩn)
1. Phân vùng mặt: gộp tam giác kề nhau thành vùng trơn (góc nhị diện nhỏ, vd < 20–30°; dùng
   `mesh.face_adjacency`, `face_adjacency_angles`). Vùng phẳng (pháp tuyến gần như không đổi) → mặt phẳng, bỏ qua.
2. Vùng cong → khớp trụ: trục = hướng vuông góc với mọi pháp tuyến (vector riêng nhỏ nhất của ma trận hiệp phương
   sai pháp tuyến); chiếu **đỉnh** của vùng lên mặt phẳng vuông góc trục, khớp đường tròn bình phương tối thiểu →
   tâm, bán kính, `rms_mm`. Có thể dùng `pyransac3d` nếu thấy tốt hơn. Bỏ vùng có rms > 2 % bán kính hoặc không phải trụ.
   Gộp các vùng cùng trục + cùng bán kính (lệch ≤ 0,02 mm) thành 1 feature (mặt trụ hay bị chia thành nhiều vùng).
3. `type`: pháp tuyến hướng VÀO trục → `hole`; hướng RA → `boss`. `coverage_deg` < 300 → `arc` (khuyết, bo góc, rãnh),
   không tính là lỗ/boss.
4. `length_mm` = khoảng chiếu đỉnh lên trục (max − min). `through` (lỗ): KHÔNG có mặt phẳng vuông góc trục chặn ở
   đầu nào (đầu bị chặn = có mặt phẳng ⟂ trục, kề mép vùng trụ, nằm phía trong bán kính – đáy tròn đặc hoặc vành khuyên
   của lỗ bậc đều tính là chặn). Lỗ nhỏ của lỗ bậc thông xuống lỗ lớn → coi là mở.
5. `confidence`: giảm theo rms/bán kính, coverage thấp, ít mặt (< 12). Lỗ trụ sạch ≥ 0,9.
6. Đường kính theo **đỉnh** lưới (đỉnh nằm trên đường tròn thật của CAD) – lưới thô 24 cạnh vẫn phải sai ≤ 0,08 mm.

## CLI
- `python measure_features.py <file.stl|.3mf ...> --json out.json`: 1 file → JSON object (thêm `"file"`: đường dẫn);
  nhiều file → JSON list. `.3mf` nạp bằng `trimesh.load(..., force="mesh")`. File không có/không đọc được → in lỗi
  stderr, exit 1. Ghi JSON UTF-8, `ensure_ascii=False`, indent 1.
- Mã + chú thích: ASCII không dấu như các script cùng thư mục.

# Không làm
- Không sửa test, `measure_holes.py`, `study_3mf.py`, `pyproject.toml`.
- Không nhận dạng ren, lục giác đai ốc, snap-fit ở bản này (để bản sau).

# Tiêu chí PASS
- Gate exit 0 (2 lần đo < 60 s).
- Claude tự chạy thêm trên chi tiết thật của tay máy tipflow (community/) và xem kết quả.
