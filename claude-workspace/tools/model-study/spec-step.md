---
task: model-study-step
cwd: tools/model-study
allow: ["measure_step.py", "_out/**", "_out/*"]
gate: "python test_step.py"
timeout_min: 20
max_rounds: 2
executor: auto
---

# Mục tiêu
Viết `measure_step.py`: đo lỗ/chốt/cung CHÍNH XÁC từ mặt trụ của file STEP (model cộng đồng) để Claude học dung sai
lắp ghép. Chạy bằng FreeCAD (đã có OCCT): `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" measure_step.py <file.step> <thư mục ra>`.
Lấy tham số: `[a for a in sys.argv[1:] if not a.endswith(".py")]` (freecadcmd tự thêm tham số). Chỉ dùng FreeCAD
(`Part`) + stdlib. Mẫu thử: `make_step_fixture.py` (đọc chú thích đầu file để biết đáp án).

# Cách làm (đã thử thật: `Part.read()` → `face.Surface` là `Part.Cylinder` có `Radius`, `Axis`, `Center`)
1. `shape = Part.read(path)`; duyệt từng `solid` (`part` = chỉ số solid, từ 1); trong solid duyệt `Faces` có
   `isinstance(face.Surface, Part.Cylinder)`.
2. Chuẩn hóa trục: vector đơn vị, đổi dấu để thành phần có trị tuyệt đối lớn nhất dương. `axis` = "x"/"y"/"z" nếu song
   song trục toạ độ (sai lệch < 0,5°), ngược lại ghi "a,b,c" (3 số lẻ).
3. GỘP các mặt trụ cùng solid, cùng bán kính (±0,001 mm), cùng trục (song song, đường trục cách nhau < 0,001 mm)
   VÀ khoảng theo trục chồng/chạm nhau → 1 đặc trưng (`faces` = số mặt đã gộp). Lỗ bị OCCT tách 2 nửa phải ra 1 dòng.
4. `sweep_deg`: tổng góc quét (từ `face.ParameterRange` u, đơn vị rad → độ, gộp không cộng trùng), tối đa 360.
5. `length`: khoảng chiếu các đỉnh/cạnh của các mặt lên trục (max − min). Tâm (`cx,cy,cz`) = điểm trên đường trục tại
   GIỮA khoảng đó.
6. `kind`: sweep < 300° → `arc`; ngược lại `hole` nếu pháp tuyến mặt (tại điểm giữa tham số) hướng VỀ trục (vật liệu
   bao quanh), `pin` nếu hướng RA xa trục. Lưu ý `face.Orientation` ("Reversed") có thể đảo pháp tuyến – dùng
   `face.normalAt(u, v)` (đã tính hướng mặt).
7. Ghi `step_features.csv` (utf-8) cột `idx,part,kind,diameter,axis,cx,cy,cz,length,sweep_deg,faces`
   (diameter/toạ độ/length 3 số lẻ mm, sweep 1 số lẻ) và `step_features.md`: bảng theo part + mục `## Thong ke duong
   kinh` (đường kính hole/pin lặp lại, gom ±0,005, số lần).

# Không làm
- Không sửa `test_step.py`, `make_step_fixture.py`, các file khác trong `tools/model-study/` (thuộc phiên khác).
