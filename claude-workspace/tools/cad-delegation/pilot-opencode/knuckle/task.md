---
task: pilot-opencode-knuckle
cwd: tools/cad-delegation/pilot-opencode/knuckle
allow: ["build_part.py", "part.step", "gate.json", "attempts.log", "*.stl"]
gate: '"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" ../../gate.py . && python ../../../delegate/json_ok.py gate.json passed'
timeout_min: 15
max_rounds: 2
executor: opencode
---

# Mục tiêu
Dựng chi tiết theo `spec.yaml` (mục "deliverable", "design", "print"); `context.FCStd` là chi tiết lân cận.

# Yêu cầu
1. Viết `build_part.py` (Python FreeCAD, module Part, tham số đặt tên ở đầu file), xuất `part.step` (1 solid) cùng thư mục.
   Chạy: `"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" build_part.py`
2. Chạy gate (lệnh ở trên), đọc `gate.json` (passed, checks, warnings). FAIL thì sửa `build_part.py` theo check FAIL, tối đa 8 vòng.
3. Mỗi lần chạy gate thêm 1 dòng vào `attempts.log`: "<số vòng> <summary> <tên check FAIL>".

# Không làm
- Không sửa `spec.yaml`, `context.FCStd`, `../../gate.py`. Không git.
