---
task: esp32-s3-cam-cad-d
cwd: maker/esp32-s3-cam/freecad
allow:
  - "scripts/build_cam_d.py"
gate: "\"C:\\Program Files\\FreeCAD 1.1\\bin\\FreeCADCmd.exe\" --safe-mode -P tests -t test_build"
timeout_min: 40
max_rounds: 3
executor: codex
---

# Mục tiêu
Viết `scripts/build_cam_d.py`: script FreeCAD dựng vỏ camera **mẫu D (để bàn)** – Tuan đã duyệt dáng
(`../design/contact-sheet-D.png`, `../design/design-spec.md` mục D) – **từ `params.json`** (Claude chốt; không viết cứng số
kích thước linh kiện trong script, trừ các tọa độ bố trí ghi dưới đây, cũng phải tính từ params). Gate
`tests/test_build.py` (Claude viết, KHÔNG sửa) đặc tả tên Label và các kiểm.

# Đầu vào / đầu ra
- Params: biến `CAMD_PARAMS`, mặc định `params.json` cạnh `scripts/`. Thư viện dựng hình: `../../../tools/robotics-cad/scripts/cad_lib.py`
  (`box`, `cyl`, `rrect`…); mẫu cấu trúc `../../line-bot/freecad/scripts/build_line_bot.py` (đọc, KHÔNG sửa).
- Ra `cam_d.FCStd` (biến `CAMD_OUT`, mặc định cạnh `scripts/`); file đích có sẵn → chép sang `backup/cam_d.<YYYYmmdd-HHMMSS>.FCStd`.
- Xuất STL **đúng hướng in** (đặt mặt in xuống z = 0, x/y quanh gốc) vào thư mục `stl/` cạnh file FCStd:
  `body.stl`, `bezel.stl`, `u_frame.stl`, `base.stl`, `pin_cap.stl`, `coupon.stl`, `coupon_ring.stl`.
- Font chữ: params `mat_truoc.font` (`Part.makeWireString`); không có font → bỏ chữ, in cảnh báo, không lỗi.

# Hệ trục + ký hiệu (mm)
X phải, Y ra SAU (mặt trước camera nằm ở y nhỏ), Z lên, gốc = tâm đáy De. Viết tắt: T = than, M = mat_truoc, S = mach,
N = truc_nghieng, U = khung_u, D = de_xoay.
- zp (tâm trục nghiêng) = D.lom_sau… cụ thể: mặt trên đĩa zd = (D.de_cao − D.lom_sau) + D.dia_day; zp = zd + N.cao_tam_tren_dia.
  Với params hiện tại: đáy lõm z = 6, đĩa z 6…12, zp = 64.
- Thân: x ∈ ±T.w/2, z ∈ zp ± T.h/2, y ∈ [y0, y0 + T.d] với y0 = −(T.d + M.t)/2 + M.t (thân + mặt trước đối xứng quanh y = 0).
  Với params: mặt trước y −20…−17, thân y −17…+20, z 32…96.
- Mạch: mặt trước PCB y_pcb = y0 + 0,5 + S.cam_cao_tren_pcb (= −10,5); khối mạch y ∈ [y_pcb, y_pcb + S.stack_t];
  x ∈ ±S.pcb_w/2; z ∈ zp ± S.pcb_h/2. Tâm ống kính: x = 0, z_lens = zp + S.pcb_h/2 − S.ong_kinh_cach_canh_tren (= 74,85).

# Chi tiết in (Label → nội dung)
1. **Body** (trắng): khối T.w × T.d × T.h bo R T.r_goc các cạnh song song Y, rỗng thành T.thanh, **hở mặt trước** (y0), kín mặt sau.
   - 4 trụ vít M2.5 Ø M.tru_vit_d tại (±(T.w/2 − M.vit_cach_canh), z = zp ± (T.h/2 − M.vit_cach_canh)), từ y0 vào trong M.tru_vit_sau,
     lỗ tự ren Ø M.vit_m25_tu_ren hết chiều sâu trụ; trụ liền thành.
   - Dẫn hướng mạch (khe S.khe_moi_ben mỗi phía): mỗi bên 2 khối gân đặc từ mặt trong thành bên tới |x| = S.pcb_w/2 + khe,
     z ∈ [zp + 6, zp + 18] và [zp − 18, zp − 6] (tránh trụ trục nghiêng), y từ y_pcb tới y_pcb + S.stack_t;
     2 chặn sau: gân từ thành sau tới y = y_pcb + S.stack_t + khe, rộng 3, tại x = ±(S.pcb_w/2 − 4);
     2 đỡ dưới + 2 đỡ trên: cột 3 × 3 từ thành dưới/trên tới z = zp ∓ (S.pcb_h/2 + khe), tâm x = ±(S.pcb_w/2 − 2,5),
     y = y_pcb + S.stack_t − 2 (cổng USB ở giữa cạnh dưới – đỡ dưới nằm ngoài ô USB).
   - Trục nghiêng mỗi bên: trụ trong Ø N.tru_than_d dài N.tru_than_dai theo X, áp mặt trong thành bên, tâm (y = 0, z = zp);
     lỗ Ø N.m3_xuyen xuyên thành + trụ; hốc lục giác đai ốc cạnh-đối-cạnh N.dai_oc_s sâu N.dai_oc_sau từ mặt trong trụ, 1 cạnh
     phẳng nằm trên cùng (in được không support khi thân in nằm mặt sau).
   - Ô USB thành dưới (params `usb`): rộng x = usb.o_rong_x, sâu y = usb.o_sau_y, tâm x = 0, y = y_pcb + S.stack_t − usb.o_sau_y/2,
     bo góc usb.bo_mep.
   - Khe nhiệt (bắt buộc, xuyên thành): thành dưới 6 khe rộng khe_nhiet.rong (theo X) dài khe_nhiet.dai (theo Y), tâm x = ±(14, 17,5, 21),
     y từ y_pcb + 2 tới y_pcb + 2 + dai; thành trên 6 khe cùng cỡ tâm x = −10, −6, −2, 2, 6, 10, y từ y0 + 3 tới y0 + 3 + dai.
     Khe không được cắt vào trụ vít, cột đỡ, ô USB.
   - Không phần nào của Body giao khối mạch `Ref_Stack`.
2. **Bezel** (đen): tấm T.w × M.t × T.h bo R T.r_goc (cạnh // Y), y ∈ [y0 − M.t, y0], z như thân.
   - Lỗ ống kính Ø M.lo_ong_kinh_d xuyên tại (0, z_lens); lõm vòng trang trí mặt trước Ø M.vong_trang_tri_d sâu M.vong_trang_tri_sau.
   - 2 cửa sổ đèn Ø M.den_d tại x = ±M.den_cach_nhau/2, z = z_lens − M.den_duoi_ong_kinh: lỗ mù khoan từ MẶT SAU, chừa da
     M.den_da_mong ở mặt trước.
   - Chữ M.chu khắc sâu M.chu_sau mặt trước, cao M.chu_cao, căn giữa x, tâm chữ z = z_lens − M.den_duoi_ong_kinh − M.chu_duoi_den.
   - 4 lỗ Ø M.vit_m25_xuyen trùng trụ vít Body, côn chìm đầu vít mặt trước (Ø 5,0, góc 90°).
   - 4 cột chặn trước Ø 2,5 từ mặt sau tới y = y_pcb − khe tại (±(S.pcb_w/2 − 1,5), zp ± (S.pcb_h/2 − 1,5)) – chặn góc PCB.
3. **U_frame** (xanh, 1 khối): đĩa Ø D.dia_d dày D.dia_day, z ∈ [zd − D.dia_day, zd]; lỗ giữa Ø D.lo_dia_d; lốc mặt trên
   Ø D.loc_dia_d sâu D.loc_dia_sau. 2 tay: dày U.tay_day theo X, mặt trong |x| = T.w/2 + N.khe_tay_than, sâu U.tay_sau_y (y ∈ ±U.tay_sau_y/2),
   từ zd lên zd + U.tay_cao, đầu tay bo tròn R = U.tay_sau_y/2 quanh trục (y = 0, z = zp) nếu tay_cao cho phép, không thì bo R 3.
   Lỗ trục Ø N.m3_xuyen theo X tại (y = 0, z = zp), lốc đầu vít mặt ngoài Ø N.loc_dau_vit_d sâu N.loc_dau_vit_sau.
4. **Base** (xanh): trụ Ø D.de_d cao D.de_cao, z 0…de_cao, bo R 2 cạnh trên ngoài; lõm Ø D.lom_d sâu D.lom_sau ở mặt trên;
   chốt giữa Ø D.chot_d từ đáy lõm lên tới z = (zd − D.loc_dia_sau) + D.khe_doc; lỗ tự ren M2.5 Ø M.vit_m25_tu_ren dọc trục chốt sâu 8.
   2 lỗ vít tường Ø D.lo_khoa_d xuyên tại x = ±D.lo_khoa_cach/2, y = 0, côn chìm đầu Ø D.lo_khoa_dau_d ở đáy lõm (vít từ trên xuống).
   Mặt đáy PHẲNG (không lõm 3M – dán thẳng).
5. **Pin_cap**: đĩa Ø D.nap_chot_d dày D.nap_chot_day, lỗ Ø M.vit_m25_xuyen; lắp trên đỉnh chốt (z từ đỉnh chốt), nằm trong lốc đĩa,
   không giao U_frame.
6. **Coupon** (in trước để chọn số): tấm 70 × 34 × 4; trên đó: 3 lỗ M3 xuyên `coupon.m3_xuyen`; 3 hốc lục giác `coupon.dai_oc_s`
   sâu 2,6 (lỗ M3 3,4 ở giữa mỗi hốc); 3 lỗ ống kính `coupon.lo_ong_kinh`; 2 lỗ mù Ø 3,4 chừa da `coupon.den_da_mong` ở mặt đáy;
   1 chốt Ø 8,0 cao 6; khung thử khối mạch: viền trong (S.pcb_w + 2·khe) × (S.pcb_h + 2·khe), thành 1,2, cao 5 (đặt cạnh tấm, liền).
   Khắc số cỡ cạnh mỗi lỗ nếu có font (sâu 0,4). Tấm có thể dài hơn 70 nếu cần chỗ – gate chỉ kiểm có các lỗ.
7. **Coupon_ring**: vòng Ø 15 × 4, lỗ Ø D.lo_dia_d (thử khớp xoay với chốt Ø 8 của Coupon).

# Tham chiếu (không in, Label bắt đầu `Ref_`)
`Ref_Stack` (khối mạch), `Ref_Cam` (8,5 × 4,2 (y) × 8,5 tại ống kính, mặt trước cách mặt sau Bezel 0,5),
`Ref_Screw_L/R` (trụ Ø 3 dài 12 từ đáy lốc đầu vít vào trong).

# Không làm
Không vẽ support. Không sửa params.json, tests, cad_lib, file của dự án khác.
