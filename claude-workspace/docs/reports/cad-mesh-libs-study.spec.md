---
task: study-cad-mesh-libs
cwd: docs/reports
allow: ["cad-mesh-libs-study.md"]
read: ["community/mikedh-trimesh", "community/cadquery-cadquery", "community/gumyr-build123d",
       "community/pan-chera-multi-agent-cad", "community/orcaslicer-orcaslicer", "tools/model-study",
       "tools/robotics-cad/scripts", "tools/cad-delegation", "tools/delegate"]
gate: 'python ../../tools/delegate/check_report.py cad-mesh-libs-study.md "## 1. trimesh" "## 2. CadQuery va build123d" "## 3. Multi-Agent-CAD" "## 4. OrcaSlicer 3MF" "## 5. OrcaSlicer support" "## 6. Ap dung cho STLab" --max-todo 4 --min-files 18'
timeout_min: 35
max_rounds: 2
executor: codex
---

# Mục tiêu
Viết `cad-mesh-libs-study.md` (tiếng Việt có dấu, ≤ 260 dòng): đọc MÃ NGUỒN 5 repo đã clone (chỉ ĐỌC, không cài/chạy)
để STLab hiểu cách đọc file STL/STEP/3MF và kiểm in 3D, rồi so với công cụ STLab đang có.

Repo (tương đối claude-workspace): `community/mikedh-trimesh/`, `community/cadquery-cadquery/`, `community/gumyr-build123d/`,
`community/pan-chera-multi-agent-cad/`, `community/orcaslicer-orcaslicer/` (chỉ có `src/libslic3r/Format/` và `src/libslic3r/Support/`).
Công cụ STLab để so: `tools/model-study/study_3mf.py`, `tools/model-study/measure_holes.py`,
`tools/robotics-cad/scripts/printability.py`, `tools/cad-delegation/gate.py`, `tools/delegate/delegate.py`.

# Mục bắt buộc (đúng tiêu đề)
- `## 1. trimesh`: hàm nào đọc STL/3MF (có đọc 3MF nhiều plate/Bambu không), kiểm kín, cắt lát (section), đo thể tích,
  tìm mặt phẳng/trụ, ray; phụ thuộc bắt buộc vs tùy chọn. Dẫn file module cụ thể.
- `## 2. CadQuery va build123d`: cách đọc STEP và duyệt mặt (face) → lấy loại mặt trụ, bán kính, trục, tâm (tên hàm/lớp
  cụ thể); nền OCCT/OCP. Ghi rõ đó cũng là OCCT mà FreeCAD dùng (nếu thấy bằng chứng) – không suy đoán API FreeCAD.
- `## 3. Multi-Agent-CAD`: vai trò từng agent, vòng kiểm/sửa, cách kiểm hình học, model/nhà cung cấp dùng; so với
  `tools/delegate/delegate.py` + `tools/cad-delegation/gate.py`.
- `## 4. OrcaSlicer 3MF`: `bbs_3mf.cpp`/`3mf.cpp` đọc gì: object/component/transform, `model_settings.config`, plate,
  tên, cut info, thông số in theo object; liệt kê những gì `tools/model-study/study_3mf.py` CHƯA đọc.
- `## 5. OrcaSlicer support`: tiêu chí dò vùng cần support (góc overhang, ngưỡng, cầu/bridge, đảo nhỏ) – tên tham số,
  dẫn file; so với `tools/robotics-cad/scripts/printability.py`.
- `## 6. Ap dung cho STLab`: ≤ 8 đề xuất cụ thể (cái gì, dẫn file nguồn, công sức nhỏ/vừa/lớn, rủi ro license:
  OrcaSlicer AGPL-3.0 chỉ học ý tưởng, không chép mã). Máy STLab yếu, Windows, đã có FreeCAD 1.1 + Python 3.13.

# Quy tắc
- Mọi khẳng định quan trọng dẫn đường dẫn trong backtick, TƯƠNG ĐỐI claude-workspace (gate kiểm tồn tại, ≥ 10).
- Không thấy → "không thấy"/`TODO`; không đoán số liệu, không chép từ trí nhớ.
