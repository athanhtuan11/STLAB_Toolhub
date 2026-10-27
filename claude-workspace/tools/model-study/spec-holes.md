---
task: model-study-holes
cwd: tools/model-study
allow: ["measure_holes.py", "_out/**", "_out/*"]
gate: "python test_holes.py"
timeout_min: 25
max_rounds: 2
executor: auto
---

# Mục tiêu
Viết `measure_holes.py`: đo lỗ tròn và trục/chốt tròn trong STL (cộng đồng) để Claude học dung sai lắp ghép.
- `python measure_holes.py <file.stl> --json <out.json>` → `{"file": ..., "features": [...]}`
- `python measure_holes.py <thư mục *.stl> --csv <out.csv>` → mọi file trong thư mục, 1 dòng/feature.
- Đọc STL nhị phân và ASCII. Chỉ thư viện chuẩn + numpy. Không cài gói pip.

# Thuật toán (bắt buộc theo)
1. Với từng trục `x`, `y`, `z`: cắt lưới bằng các mặt phẳng vuông góc trục, bước 0,25 mm, lệch nửa bước khỏi biên
   (tránh cắt trúng đỉnh/mặt phẳng). Giao tam giác–mặt phẳng → đoạn thẳng → nối thành vòng kín (khớp đầu mút, làm tròn
   1e-5 mm).
2. Vòng được coi là **tròn** khi: ≥ 16 đoạn; fit đường tròn bình phương tối thiểu (Kasa) trên đỉnh vòng; mọi đỉnh
   **và trung điểm mọi đoạn** cách tâm lệch khỏi r không quá max(0,03 mm, 1 % r); 0,4 ≤ d ≤ 60 mm.
3. Phân loại bằng chẵn–lẻ (ray casting) trên **toàn bộ** vòng của lát đó, thử điểm cách đường tròn ±min(0,1 mm; 0,2 r)
   theo 8 hướng: bên ngoài là vật liệu, bên trong rỗng → `hole`; bên trong vật liệu, bên ngoài rỗng → `boss`;
   lẫn lộn → bỏ.
4. Gộp các lát liên tiếp cùng trục, cùng loại, tâm lệch ≤ 0,1 mm, d lệch ≤ 0,05 mm thành 1 feature. Bỏ feature chỉ
   có 1 lát.
5. Feature: `type` (hole|boss), `axis` (x|y|z), `d_mm` (trung bình các lát, 3 số lẻ), `center` [a, b] = toạ độ 2 trục
   còn lại theo thứ tự (x → [y, z]; y → [x, z]; z → [x, y]), `from_mm`, `to_mm` = toạ độ lát đầu/cuối ± nửa bước,
   `length_mm`, `n_slices`, `max_dev_mm` (độ lệch tròn lớn nhất).
- CSV cột: `file,type,axis,d_mm,center_a,center_b,from_mm,to_mm,length_mm,n_slices,max_dev_mm` (utf-8, file = tên file).
- Batch 33 chi tiết `_out/arm/parts` (lưới tới 171k tam giác) < 240 s: vector hoá phần cắt bằng numpy (lọc tam giác
  theo khoảng toạ độ trước mỗi lát).

# Không làm
- Không sửa `test_holes.py`, `test_study.py`, `test_render.py`, `_sample/`, `_out/arm/parts/`.
- Không tự đổi ngưỡng ở trên. Thiếu thông tin thì ghi `TODO` và dừng.

# Tiêu chí PASS
`python test_holes.py` exit 0.
