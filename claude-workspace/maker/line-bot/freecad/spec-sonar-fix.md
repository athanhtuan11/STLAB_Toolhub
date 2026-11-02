---
task: line-bot-sonar-fix
cwd: maker/line-bot/freecad
allow:
  - "scripts/build_line_bot.py"
gate: "\"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P tests -t test_build"
timeout_min: 30
max_rounds: 3
executor: auto
---

# Mục tiêu
Sửa mục 8 (SONAR_BRACKET + REF_SONAR) và các lỗ vít sonar trên Base_plate trong `scripts/build_line_bot.py`:
HC-SR04 đang dựng sai chiều (cạnh dài 45 mm nằm theo X) → `Ref_Sonar` chồng `Ref_Battery` 1125 mm³.

# Đúng (Claude chốt – mm; X tiến, Y trái, Z lên)
- `sr04.bbox = [dai, cao, sau] = [45, 20, 15]` → **dài theo Y, cao theo Z, sâu theo X**, mặt phát hướng +X.
- `Ref_Sonar`: hộp X từ `vach_x − bbox[2]` tới `vach_x` (vach_x = 70 − BRACKET_T, giữ BRACKET_T = 3), Y ±bbox[0]/2,
  tâm Z = mặt trên Base_plate + 15 (giữ như cũ), cao bbox[1].
- `Sonar_bracket`: vách đứng rộng Y = bbox[0] + 4, cao từ mặt Base_plate tới đỉnh sonar + 1; đế ngang giữ SB_DE_X = 10,
  cùng bề rộng Y với vách. 2 lỗ mắt Ø(mat_d + 0,4) trục X, tâm tại y = ±mat_cach/2, z = tâm sonar (giữ như cũ).
- Lỗ M3 bắt đế: giữ 2 lỗ tại y = ±mat_cach/2, x = vach_x − SB_DE_X/2, trên cả Sonar_bracket và Base_plate (phải trùng).
- Sửa luôn comment sai "X=45 (chieu truoc-sau)" trong mục 8.

# Không làm
- Không sửa `params.json`, `tests/`, `print/`, các mục khác của script; không mở FreeCAD GUI.
- Thấy va chạm không tránh được với số trên → `ESCALATE: <số nào, vì sao>`, không tự đổi số.

# Tiêu chí PASS
- Gate exit 0 (gồm test_10_sonar_dung_ngang mới và 9 test cũ). Script vẫn in dòng `LINEBOT OK ...`.
