---
task: model-study-3mf
cwd: tools/model-study
allow: ["study_3mf.py", "_out/**", "_out/*"]
gate: "python test_study.py"
timeout_min: 20
max_rounds: 2
executor: auto
---

# Mục tiêu
Viết `study_3mf.py`: tách 1 file `.3mf` (Bambu Studio) tải từ cộng đồng thành từng chi tiết để Claude nghiên cứu.
Lệnh: `python study_3mf.py <file.3mf | thư mục chứa *.stl> <thư mục ra>`.
Chỉ dùng thư viện chuẩn + numpy + matplotlib (KHÔNG cài thêm gói). Mẫu thử: `_sample/arm.3mf` (33 build item, 3 plate).

# Định dạng 3MF (Bambu)
- `3D/3dmodel.model`: `<resources><object id><components><component p:path="/3D/Objects/object_N.model" objectid transform>`
  và `<build><item objectid transform>`. Lưới thật nằm trong `3D/Objects/object_N.model` (`<mesh><vertices><v x y z>`,
  `<triangles><triangle v1 v2 v3>`), có thể có nhiều object/component lồng nhau → đệ quy.
- Ma trận 3MF: 12 số `m00 m01 m02 m10 m11 m12 m20 m21 m22 m30 m31 m32`, điểm hàng: p' = [x y z 1] · M (cột cuối 0 0 0 1).
  Áp transform component rồi transform build item.
- Tên: `Metadata/model_settings.config` `<object id=..><metadata key="name" value=..>`.
- Plate: cùng file, `<plate>` chứa `<metadata key="plater_id" value=N>` và các `<model_instance>` có
  `<metadata key="object_id" value=..>`.
- Namespace XML: xử lý bằng cách bỏ tiền tố namespace khi so tên thẻ/thuộc tính.

# Yêu cầu đầu ra (trong thư mục ra)
1. `parts/NN-<ten-sach>.stl`: STL **nhị phân**, mỗi build item 1 file, toạ độ = đã áp mọi transform rồi **dời sao cho
   z_min = 0 và tâm bbox XY = 0** (giữ nguyên hướng in của tác giả). `ten-sach`: tên object, bỏ ký tự lạ, kebab-case.
2. `parts.csv` (utf-8) cột: `idx,name,plate,file,triangles,size_x,size_y,size_z,z_min,volume_mm3,watertight`
   (`file` tương đối với thư mục ra; size mm, 2 số lẻ; volume = |tổng tích hỗn hợp/6|; watertight = mọi cạnh dùng đúng 2 lần).
3. `contact-sheet.png`: lưới ảnh, mỗi ô 1 chi tiết render iso (matplotlib `Poly3DCollection`, đổ bóng theo pháp tuyến,
   lưới > 20k tam giác thì lấy mẫu con để vẽ nhanh), tiêu đề ô: `NN tên  sx×sy×sz mm  P<plate>`. Tỉ lệ trục bằng nhau.
4. `summary.md`: bảng Markdown từ parts.csv + tổng số chi tiết, tổng thể tích (mm³) mỗi plate.
- Đầu vào là thư mục `*.stl` (ASCII hoặc nhị phân): làm như trên, plate = 0.
- Chạy toàn bộ mẫu < 3 phút.

# Không làm
- Không sửa `test_study.py`, `_sample/`. Không cài gói pip.
