---
task: line-bot-build
cwd: maker/line-bot/freecad
allow:
  - "scripts/build_line_bot.py"
gate: "\"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P tests -t test_build"
timeout_min: 40
max_rounds: 3
executor: agy-sonnet
# ky_nang: [cad-script]
---

# Mục tiêu
Viết `scripts/build_line_bot.py`: script FreeCAD dựng TOÀN BỘ model xe line-bot (concept A – Khung tầng, học sinh lớp 6)
**từ `params.json`**. Đổi linh kiện = sửa params.json rồi chạy lại script; không có số kích thước linh kiện nào viết cứng
trong script (trừ các hằng bố trí ghi rõ dưới đây).

# Đầu vào
- `params.json` (Claude chốt – đọc kỹ `_ghi_chu`, mọi khóa). Đường dẫn lấy từ biến `LINEBOT_PARAMS`, mặc định
  `params.json` cạnh thư mục `scripts/`.
- Gate `tests/test_build.py` (Claude viết, KHÔNG sửa) – đặc tả chính xác tên Label và các kiểm.
- Thư viện dựng hình dùng chung: `../../../tools/robotics-cad/scripts/cad_lib.py` (`box`, `cyl`, `rrect`…) – nên dùng.
  Mẫu script cùng kiểu: `../../cyberbrick-car/freecad/scripts/build_car.py` (đọc để học cấu trúc, KHÔNG sửa).
- Chạy: `freecadcmd scripts/build_line_bot.py`. Ra file theo biến `LINEBOT_OUT`, mặc định `line_bot.FCStd` cạnh
  `scripts/`; nếu file đích đã có → chép bản cũ vào `backup/line_bot.<YYYYmmdd-HHMMSS>.FCStd` trước khi ghi đè.

# Bố trí (Claude chốt – đơn vị mm; hệ trục X tiến, Y trái, Z lên; gốc = trung điểm 2 trục bánh trên mặt sàn)
Ký hiệu: R = banh.d/2; trục bánh tại x = 0, z = R.
1. **Bánh** `Ref_Wheel_L/R`: trụ Ø banh.d dày banh.w, trục song song Y, mặt trong tại |y| = 61, ra ngoài tới |y| = 61 + banh.w.
2. **Motor** `Ref_N20_L/R`: khối n20.w (X) × n20.h (Z) × (n20.dai − n20.truc_dai + dai_encoder_them) (Y) + trục Ø truc_d dài
   truc_dai hướng ra ngoài. Mặt hộp số (gốc trục) tại |y| = 59, thân đi vào trong. Tâm trục tại (0, ±, R).
3. **Motor_mount_L/R** (in rời, bắt dưới Base_plate): khối ôm motor, hốc (n20.w + 2·khe) × (n20.h + 2·khe) để motor luồn từ
   phía trong; vách đầu phía mặt hộp số dày 2,5 có lỗ trục Ø(truc_d + 1,6) và 2 lỗ Ø m16_xuyen cách tâm trục
   ±vit_cach_tam theo X; mặt trên phẳng áp vào đáy Base_plate, có 2 lỗ M3 tự ren (Ø m3_tu_ren, sâu 8) để vít từ trên xuống.
   Thành quanh hốc ≥ 2,0.
4. **Base_plate**: tấm bo góc (bo_goc_r) dày tam_duoi_t, đáy tại z = R + n20.h/2 + khe + 2,0 (nắp gá motor 2,0); kích thước
   140 (X, từ −70 tới +70) × 120 (Y). Có 4 cột Ø cot_d cao cot_cao in liền hướng lên tại (±58, ±48), đỉnh cột có lỗ M3 tự ren
   sâu 8. Có lỗ M3 xuyên (Ø m3_xuyen) khớp mọi lỗ vít của Motor_mount, Caster_mount, Line_bracket, Sonar_bracket.
   Khe luồn dây 30 × 10 ở giữa. Khay pin: 2 gờ cao 6 dày 2 giữ `Ref_Battery` nằm trên tấm, tâm pin tại x = −12, y = 0 (chừa chỗ vít Caster_mount ở x = −55),
   + 2 khe dây dán 20 × 3 hai bên khay.
5. **Top_plate**: tấm bo góc dày tam_tren_t, đáy tại đỉnh cột; 140 × 120; 4 lỗ M3 xuyên trùng cột; khe dây 30 × 10.
   Trên mặt có 4 cột đỡ Mega Ø6 cao 5 tại 4 lỗ `mega.lo_dung`, lỗ Ø m3_tu_ren sâu 7 (không xuyên tấm là được).
   **`Ref_Mega`**: hộp mega.bbox, đáy tại đỉnh cột đỡ (nằm trên Top_plate), tâm hộp bao tại (0, 0) theo XY; tọa độ lỗ =
   góc hộp bao (XMin, YMin) + mega.lo[i] – phải trùng tâm cột đỡ.
6. **Caster_mount + `Ref_Ball`**: bi cầu Ø bi_do.d_bi tại x = −55, y = 0, đáy bi chạm z = 0. Caster_mount in rời bắt dưới
   Base_plate (2 vít M3 từ trên): trụ từ đáy Base_plate xuống, hốc cầu Ø(d_bi + 0,4) ôm bi, miệng dưới hẹp Ø(0,85·d_bi)
   (bi ép vào). Chiều cao trụ TỰ TÍNH từ R để bi chạm sàn (khi đổi banh.d vẫn đúng – gate kiểm).
7. **Line_bracket + `Ref_Line_array`**: mảng = hộp line.pcb, mặt dưới cách sàn line.cao_san, tâm tại x = line.truoc_truc,
   y = 0, cạnh dài theo Y. Line_bracket in rời: chữ L bắt dưới Base_plate (2 vít M3 từ trên), chân xuống ôm mảng; 2 lỗ M3
   xuyên dạng **rãnh dọc dài 6** để chỉnh cao ±3 (Pololu: tối ưu 3 mm, tối đa 6). Không che 8 mắt cảm biến (vùng
   so_mat × buoc ở giữa mặt dưới mảng phải trống).
8. **Sonar_bracket + `Ref_Sonar`**: HC-SR04 dựng đứng ở mũi, mặt phát hướng +X, tâm cao hơn mặt Base_plate 15; bracket
   vách đứng có 2 lỗ Ø(mat_d + 0,4) cách nhau mat_cach, đế bắt lên Base_plate (2 vít M3 từ dưới lên hoặc từ trên – tự chọn,
   có lỗ tương ứng). Không vượt bao X.
9. **`Ref_Driver`**: hộp driver.bbox nằm trên Base_plate phía trước khay pin, không chạm cột.
10. Ref_* là khối tham chiếu (không in). Đặt màu: chi tiết in xanh `#3a8fd9`, Mega xanh lá, bánh đen, cảm biến đỏ/tím.
11. Cuối script: `doc.recompute()`, lưu; in 1 dòng `LINEBOT OK <số chi tiết in> <bao X×Y×Z>`.

# Yêu cầu chung
- Mọi chi tiết in: 1 solid hợp lệ, in phẳng được không support (Base_plate cột hướng lên; các gá in theo mặt áp tấm).
- Không chi tiết in nào chồng Ref_* hay chồng nhau (gate test_07; tiếp xúc mặt cho phép).
- Dùng `cad_lib`; boolean lớn thì gộp dụng cụ cắt rồi `cut` một lần.

# Không làm
- Không sửa `params.json`, `tests/`, `print/`, file `.FCStd` khác; không mở FreeCAD GUI.
- Không tự đổi số trong "Bố trí"/params – thấy mâu thuẫn (vd. va chạm không tránh được) → `ESCALATE: <số nào, vì sao>`.

# Tiêu chí PASS
- Gate exit 0. Claude tự chạy check.py + xem ảnh render trước khi đưa Tuan.
