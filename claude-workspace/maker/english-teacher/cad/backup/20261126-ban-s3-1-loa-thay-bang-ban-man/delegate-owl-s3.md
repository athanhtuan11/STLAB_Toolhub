---
task: owl-s3-enclosure
cwd: maker/english-teacher
allow:
  - "cad/build_owl_s3.py"
  - "cad/out-s3/**"
  - "cad/README.md"
  - "print/print-s3.yaml"
  - "print/stl-s3/**"
  - "print/plates-s3/**"
gate: "\"C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe\" -b --python-exit-code 1 -P cad\\gate_owl_s3.py -- cad\\out-s3"
timeout_min: 45
max_rounds: 2
executor: auto
read: ["tools/print", "tools/parts-library", "tools/model-study"]
---

# Mục tiêu
Vẽ lại vỏ Cú Bông cho bản ESP32-S3 (1 loa ở bụng, mic ở trán, bo S3, ampli MAX98357A, nút nói GPIO1) để Tuan in thử.

# Đầu vào
- Đặc tả đầy đủ (số liệu do Claude chốt): `cad/spec-owl-s3.md` – ĐỌC KỸ, làm đúng từng mục.
- Bản A1S làm gốc: `cad/build_owl.py` (Blender 5.2 bpy, 813 dòng), `cad/spec-owl.md`, `cad/spec-vol-back.md`, `print/print.yaml`.
- Gate: `cad/gate_owl_s3.py` (KHÔNG sửa).

# Yêu cầu
- Chép build_owl.py → cad/build_owl_s3.py rồi sửa theo spec-owl-s3.md. Chạy:
  `"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P cad\build_owl_s3.py -- cad\out-s3`
- Chép STL in từ cad/out-s3 sang print/stl-s3, viết print/print-s3.yaml (plates_dir: plates-s3, xếp theo màu như print.yaml),
  cắt lớp: `python ..\..\tools\print\scripts\slice.py print\print-s3.yaml` → mọi bàn PASS không support.
- Rồi chạy gate tới khi PASS.

# Không làm
- Không sửa build_owl.py, gate_owl.py, gate_owl_s3.py, out/, print/print.yaml, print/plates/, firmware/, server/.
- Không tự chọn kích thước ngoài spec; thiếu số → để rộng + TODO trong README.
- Không commit.

# Tiêu chí PASS
- Gate exit 0.
- Claude tự xem out-s3/owl-preview.png + owl-exploded.png và .3mf từng bàn.
