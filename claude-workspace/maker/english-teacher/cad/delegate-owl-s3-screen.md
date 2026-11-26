---
task: owl-s3-screen-enclosure
cwd: maker/english-teacher
allow:
  - "cad/build_owl_s3_screen.py"
  - "cad/out-s3-screen/**"
  - "cad/README.md"
  - "print/print-s3-screen.yaml"
  - "print/stl-s3-screen/**"
  - "print/plates-s3-screen/**"
gate: "\"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe\" -b --python-exit-code 1 -P cad\\gate_owl_s3_screen.py -- cad\\out-s3-screen"
timeout_min: 60
max_rounds: 2
executor: auto
read: ["tools/print", "tools/parts-library", "tools/model-study"]
---

# Mục tiêu
Vẽ lại vỏ Cú Bông S3: màn TFT 2,8" cảm ứng làm mắt (face-plate kem), 2 loa ở 2 sườn chếch trước 25°, 2 ampli, bụng trơn – để Tuan in thử.

# Đầu vào
- Đặc tả (số do Claude chốt): `cad/spec-owl-s3-screen.md` – ĐỌC KỸ, làm đúng từng mục.
- Gốc: `cad/build_owl_s3.py` (Blender 5.2 bpy), `cad/README.md` mục "Bản ESP32-S3" + "Bàn in thử v2", `print/print-s3.yaml`.
- Dáng: `design/design-spec.md` mục 10 + 10.9 (chỉ đọc).
- Gate: `cad/gate_owl_s3_screen.py` (KHÔNG sửa).

# Yêu cầu
- Chép build_owl_s3.py → cad/build_owl_s3_screen.py rồi sửa theo spec. Chạy:
  `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P cad\build_owl_s3_screen.py -- cad\out-s3-screen`
- Chép STL in sang print/stl-s3-screen, viết print/print-s3-screen.yaml, cắt lớp:
  `python ..\..\tools\print\scripts\slice.py print\print-s3-screen.yaml` → mọi bàn PASS không support.
- Chạy gate tới khi PASS. Bọc việc nặng (Blender, slice) bằng `python ..\..\tools\print\scripts\memjob.py` (giới hạn RAM, máy từng bị đứng).

# Không làm
- Không sửa build_owl_s3.py, gate_owl_s3*.py, out-s3/, print-s3*.yaml cũ, plates-s3*/ cũ, design/, firmware/, server/.
- Không tự chọn kích thước ngoài spec; thiếu số → để rộng + TODO trong README.
- Không commit.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự xem out-s3-screen/owl-preview.png + owl-exploded.png và .3mf từng bàn.
