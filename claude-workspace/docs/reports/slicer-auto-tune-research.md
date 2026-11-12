# Tự chọn thông số slicer theo hình học (Bambu A1 0.4 + Bambu PETG Basic, Textured PEI)

Ngày: 2026-11-12. Phạm vi: báo cáo tham khảo, chưa viết code. Đơn vị: mm, °C, mm/s.

## 0. Nguồn đã đọc và độ tin cậy

| Nguồn | Cách đọc | Ghi chú |
|---|---|---|
| Profile hệ thống Bambu Studio 02.09.00.74 trên máy (`C:\Program Files\Bambu Studio\resources\profiles\BBL`) | Gộp chuỗi `inherits` của `0.20mm Standard @BBL A1` và `Bambu PETG Basic @BBL A1` | Đây là **giá trị thật** của A1. Khóa nào không có trong profile thì dùng mặc định trong PrintConfig. |
| `src/libslic3r/PrintConfig.cpp` BambuStudio master (tải 2026-11-12) | Đọc tên khóa, mặc định, min/max | https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/PrintConfig.cpp |
| `PrintConfig.cpp` OrcaSlicer main | Tên khóa, mặc định (brim ears, support) | https://github.com/OrcaSlicer/OrcaSlicer/blob/main/src/libslic3r/PrintConfig.cpp |
| Bản sparse OrcaSlicer cục bộ `community/orcaslicer-orcaslicer` | Chỉ có `src/libslic3r/Format` + `Support`, KHÔNG có PrintConfig, KHÔNG có profile BBL | Dùng để xác nhận 3MF lưu paint (mục 4.3) |
| Wiki OrcaSlicer (orcaslicer.com/wiki) | Đọc được | Liên kết ở từng mục |
| Wiki Bambu (wiki.bambulab.com) | **Không tải trực tiếp được** (HTTP 402); chỉ có tóm tắt từ kết quả tìm kiếm | Mọi mục ghi "(wiki Bambu, qua tìm kiếm)" cần Tuan mở trang xác nhận lại |
| Diễn đàn Bambu, blog bên thứ ba | Chỉ để tham khảo | Ghi rõ là không chính thức |

Lưu ý: nhiều mặc định "Bambu" dưới đây là **mặc định của profile A1**, không phải mặc định chương trình. Ví dụ `wall_generator` mặc định chương trình là `arachne`, nhưng profile A1 đặt `classic`.

## 1. Bảng khuyến nghị tóm tắt

Cột "A1 hiện tại" là giá trị trong `0.20mm Standard @BBL A1` (đã gộp). "Đề xuất" cho A1 + PETG Basic. Mức nguồn: **S** = có nguồn chính thức/mã nguồn; **P** = đề xuất cần in thử.

| Mục tiêu | Khóa (process JSON / project_settings.config) | A1 hiện tại | Đề xuất | Mức | Nguồn |
|---|---|---|---|---|---|
| Loại support | `support_type` | `tree(auto)` | Giữ `tree(auto)`; chi tiết nhiều mặt phẳng nằm ngang lớn thì `normal(auto)` | P | PrintConfig BS (enum); wiki Bambu support (qua tìm kiếm) |
| Kiểu tree | `support_style` | `default` | `default` (= tree hybrid theo wiki); `tree_slim` khi tiết kiệm nhựa, `tree_strong` khi chân cao mỏng | P | PrintConfig BS (enum: default/grid/snug/tree_slim/tree_strong/tree_hybrid/tree_organic) |
| Ngưỡng góc | `support_threshold_angle` | 30 | 30 giữ nguyên; bỏ ngưỡng 45° của repo khi gọi slicer (xem 3.1) | S/P | PrintConfig BS (mặc định 30, min 1, max 90) |
| Khe Z trên | `support_top_z_distance` | 0.2 | 0.2 (cùng nhựa); 0.25 thử nếu khó gỡ | P | PrintConfig BS (mặc định 0.2). Blog PrintPal/SlicerGuide nêu 0.25 cho PETG: không chính thức |
| Khe Z dưới | `support_bottom_z_distance` | 0.2 | 0.2 | S | PrintConfig BS |
| Lớp interface trên | `support_interface_top_layers` | 2 | 2 (1 khi cần dễ gỡ, 3 khi mặt dưới cần phẳng) | P | Wiki Orca (nhiều lớp = phẳng hơn nhưng khó gỡ) |
| Lớp interface dưới | `support_interface_bottom_layers` | 2 | 0 khi support chỉ trên chi tiết, 2 giữ nguyên nếu đứng trên chi tiết khác | P | PrintConfig BS (-1 = giống trên) |
| Khoảng cách interface | `support_interface_spacing` | 0.5 | 0.5 giữ (dễ gỡ); 0.1 nếu cần mặt đẹp; 0 = đặc | P | PrintConfig BS; diễn đàn Bambu (0.1) |
| Mẫu interface | `support_interface_pattern` | `auto` | `auto` (rectilinear); `concentric` cho mặt tròn nhỏ | P | Wiki Orca support advanced |
| Khe XY | `support_object_xy_distance` | 0.35 | 0.35; giảm 0.2 chỉ khi support chạm sát lỗ nhỏ | P | PrintConfig BS (mặc định 0.35, 0–10) |
| Chỉ support từ bàn | `support_on_build_plate_only` | 0 | **1** khi chi tiết có mặt trong đẹp (tránh sẹo trên mặt chi tiết) | P | PrintConfig BS |
| Support PLA cho PETG (interface) | `support_interface_filament` | 0 | Chưa khuyến nghị cho STLab (xem 2.1) | P/TODO | Wiki Bambu zh PLA Basic + PETG HF (qua tìm kiếm); sản phẩm Support for PLA/PETG |
| Brim kiểu | `brim_type` | không khai (= `auto_brim`) | `outer_only` (đã có trong slice.py) hoặc `brim_ears` (BS: tên hiển thị "Painted") | S/P | PrintConfig BS; wiki Orca brim |
| Brim rộng | `brim_width` | 5 | 5 cho chi tiết nhỏ/cao mảnh; 3 cho chân vừa; 0 cho chân lớn | P | Profile A1 (5); ngưỡng cần in thử |
| Khe brim | `brim_object_gap` | 0.1 | 0.1 (đã dễ gỡ); 0.15–0.2 khi mép chi tiết phải đẹp | P | PrintConfig BS (0–2); wiki Orca (khe lớn dễ gỡ hơn, bám yếu hơn) |
| Brim ears (chỉ Orca) | `brim_ears_max_angle`=125, `brim_ears_detection_length`=1 | n/a trong BS | Chỉ dùng nếu chuyển sang Orca | S | PrintConfig Orca |
| Seam | `seam_position` | `aligned` | `aligned`; `back` khi có mặt trước cần đẹp | S | Wiki Orca seam |
| Scarf seam | `seam_slope_type`, `scarf_angle_threshold`(155) | `none` | `external` cho chi tiết tròn trơn; in thử. **Sửa 2026-11-12**: profile A1 có `override_filament_scarf_seam_setting=0` nên scarf lấy theo filament (`filament_scarf_seam_type=none`); phải đặt thêm `override_filament_scarf_seam_setting=1` hoặc ghi đè khóa filament (mục 8.5) | P | PrintConfig BS; wiki Orca |
| Thứ tự tường | `wall_infill_order` (BS 02.09; tên cũ `wall_sequence`) | `inner wall/outer wall/infill` | Giữ; Orca khuyên inner-outer-inner cho seam đẹp | S/P | Profile A1; wiki Orca seam |
| Wall generator | `wall_generator` | `classic` | `classic` (hiện tại); `arachne` cho chi tiết vách mỏng 0.4–0.84 | P | PrintConfig BS (mặc định chương trình arachne); wiki Orca |
| Chỉ 1 tường trên | `only_one_wall_top` | 1 | 1 | S | Profile A1 |
| Ironing | `ironing_type` | `no ironing` | `top`/`topmost` chỉ cho mặt phẳng trên lớn, đẹp; rủi ro heat creep | P | Wiki Orca ironing; profile A1 (flow 10%, spacing 0.15) |
| Mẫu mặt trên | `top_surface_pattern` | `monotonicline` | `monotonicline` giữ; `concentric` cho mặt tròn | P | Profile A1; PrintConfig BS (enum) |
| Mẫu mặt đáy | `bottom_surface_pattern` | `monotonic` | giữ | S | Profile A1 |
| Layer height | `layer_height` + `adaptive_layer_height` | 0.2 / 0 | 0.2; 0.12–0.16 khi có mặt cong lớn; `adaptive_layer_height`=1 (cần in thử) | P | Profile A1 (có sẵn bộ 0.08–0.28) |
| Tránh vượt tường | `reduce_crossing_wall` | 0 | 1 cho chi tiết nhiều lỗ (giảm sợi tơ PETG); đổi lại thời gian lâu | P | PrintConfig BS (mặc định false) |
| Bù lỗ/contour | `xy_hole_compensation`, `xy_contour_compensation` | 0 / 0 | 0 (lắp ghép tính bằng khe thiết kế, theo quy tắc khe 0.2) | S | Profile A1; wiki Orca không cho số |
| Elephant foot | `elefant_foot_compensation` | 0.075 | 0.075 giữ; Orca ví dụ 0.25 nhưng đó là ví dụ, không phải khuyến nghị | S/P | Profile A1; wiki Orca precision |
| Cầu không support | `bridge_no_support` | 0 | giữ 0 | S | Profile A1 |
| Overhang tường | `detect_overhang_wall` | 1 | giữ 1 | S | Profile A1 |

## 2. Chi tiết theo nhóm

### 2.1 Support

Khóa chính xác (BambuStudio PrintConfig): `enable_support`, `support_type` (normal(auto) | tree(auto) | normal(manual) | tree(manual)), `support_style` (default | grid | snug | tree_slim | tree_strong | tree_hybrid | tree_organic), `support_threshold_angle` (int, 1–90, mặc định 30), `support_top_z_distance` (0.2), `support_bottom_z_distance` (0.2), `support_interface_top_layers` (enum mở, min 0), `support_interface_bottom_layers` (min -1 = giống trên), `support_interface_spacing` (0.5, 0 = đặc), `support_interface_pattern` (auto | rectilinear | concentric | rectilinear_interlaced | grid), `support_object_xy_distance` (0.35, 0–10), `support_on_build_plate_only` (false), `support_interface_filament` (int, 0 = dùng nhựa hiện tại), `top_z_overrides_xy_distance` (false; "chỉ nên bật với HybridTree"), `independent_support_layer_height` (true), `tree_support_branch_angle` (mặc định chương trình 40, profile A1 đặt 45), `tree_support_branch_diameter` (profile A1: 2), `support_remove_small_overhang` (true).

Giá trị trong profile A1 0.20 Standard (đọc từ máy): `enable_support=0`, `support_type=tree(auto)`, `support_style=default`, `support_threshold_angle=30`, top/bottom Z = 0.2/0.2, interface 2/2 lớp, spacing 0.5, pattern `auto`, XY 0.35, `support_base_pattern=default` (spacing 2.5), `support_speed=150`, `support_interface_speed=80`, `support_expansion=0`, `support_on_build_plate_only=0`, `support_filament=0`, `support_interface_filament=0`.

Đánh đổi:
- Khe Z lớn: dễ gỡ hơn nhưng mặt dưới chi tiết thô hơn; khe nhỏ: ngược lại (wiki Bambu, qua tìm kiếm). Wiki Bambu cũng nói khi interface bằng vật liệu support chuyên dụng thì Z có thể bằng 0; với interface cùng nhựa thì khoảng 0.2 và đừng đặt 0 (rất khó gỡ) (bản zh, qua tìm kiếm). Với PETG cùng nhựa, tránh Z = 0.
- Interface nhiều lớp / spacing 0: mặt phẳng hơn, tốn thời gian hơn, khó gỡ hơn (wiki Orca).
- Tree strong: nhánh nối chắc, đôi khi khó gỡ; slim: gộp mạnh, ít nhựa; hybrid: normal dưới mặt phẳng lớn + tree nơi khác (wiki Bambu, qua tìm kiếm).
- `support_on_build_plate_only=1`: không có sẹo trên mặt chi tiết, nhưng phần nhô ở giữa chi tiết sẽ không có support (cần sửa model hoặc đổi hướng). Hợp với quy tắc "sửa model để khỏi support".

Interface khác vật liệu (PLA làm interface cho PETG qua AMS):
- Có tồn tại cấu hình chính thức: Bambu có trang wiki bản zh cho cặp **Bambu PLA Basic + Bambu PETG HF** hỗ trợ cho nhau, nói PLA/PETG cho interface tốt hơn và dễ gỡ hơn (https://wiki.bambulab.com/zh/filament-acc/filament/pla-basic-and-petg-hf, qua tìm kiếm, không tải được trực tiếp). Bambu cũng bán "Support for PLA/PETG" (65102) dùng chọn ở "Support/Raft interface".
- Cặp **PETG Basic + PLA** KHÔNG được trang đó nêu đích danh. Diễn đàn có báo cáo PLA/PETG bám nhau yếu nên tách dễ, nhưng cũng có thread thất bại (https://forum.bambulab.com/t/cannot-print-petg-as-a-support-interface-with-pla/73640): in nhựa PETG làm interface cho PLA hỏng ở A1 mini, trong khi tài khoản khác thành công với preset mặc định. Kết luận: **hợp lệ về mặt phần mềm, hiệu quả với PETG Basic chưa có nguồn chính thức → TODO in thử**.
- Chi phí cho STLab: dùng AMS lite + prime tower/lượng nhựa xả đổi màu, đi ngược quy tắc "hạn chế AMS". Đề xuất: không bật mặc định, chỉ là tùy chọn "nâng cao" trong giao diện.

### 2.2 Brim

Khóa: `brim_type`, `brim_width` (0–100), `brim_object_gap` (0–2).
- BS `brim_type` enum: `auto_brim` (mặc định chương trình), `brim_ears` (nhãn "Painted" = chỉ vẽ trong Prepare), `outer_only`, `inner_only`, `outer_and_inner`, `no_brim`. **Bambu Studio KHÔNG có `brim_ears_max_angle`/`brim_ears_detection_length`; đó là của OrcaSlicer** (Orca: mặc định 125° và 1 mm; `brim_ears_outer_only`; thêm loại `painted`, `leading_edge_only`). Điểm tai brim vẽ tay lưu ở `Metadata/brim_ear_points.txt` trong 3MF (bbs_3mf.cpp).
- A1 hiện tại: `brim_width=5`, `brim_object_gap=0.1`, `brim_type` không khai → `auto_brim`.
- Wiki Orca: Auto tính chiều rộng theo hình học + nhựa (hệ số bám PETG = 2, trần 18 mm; nếu tính ra < 5 mm thì có thể bằng 0). Điều này phù hợp quan sát của Tuan 2026-10-23 "auto_brim để chi tiết nhỏ vẫn bong". `outer_only` dễ gỡ nhất; `inner_only` khó gỡ hơn nhưng giấu vết (https://www.orcaslicer.com/wiki/print_settings/others/others_settings_brim).
- Đánh đổi `brim_object_gap`: lớn → dễ gỡ, bám yếu; rất lớn có thể mất tiếp xúc. 0.1 mm của profile là điểm cân bằng sẵn có; đổi lên 0.15–0.2 chưa có số liệu → in thử.

### 2.3 Bề mặt

Giá trị A1: `seam_position=aligned`, `seam_slope_type=none` (scarf tắt), `scarf_angle_threshold=155`, `seam_slope_min_length=10`, `wall_loops=2`, `wall_generator=classic`, `wall_infill_order=inner wall/outer wall/infill`, `only_one_wall_top=1`, `top_shell_thickness=1.0`, `top_surface_pattern=monotonicline`, `bottom_surface_pattern=monotonic`, `ironing_type=no ironing` (`ironing_flow=10%`, `ironing_spacing=0.15`, `ironing_speed=30`), `resolution=0.012`, `reduce_crossing_wall=0`, `adaptive_layer_height=0`, `elefant_foot_compensation=0.075`, `xy_hole_compensation=0`, `xy_contour_compensation=0`, `detect_thin_wall=0`, `fuzzy_skin=none`.

Filament PETG Basic @A1: nozzle 245 °C (range 230–270), `textured_plate_temp` 70 °C, quạt 30–50%, `filament_flow_ratio` 0.94, `filament_max_volumetric_speed` 13 mm3/s, `filament_retraction_length` 0.4, `filament_bridge_speed` 25 mm/s (process `bridge_speed` 50), `temperature_vitrification` 55 °C, `overhang_fan_speed` 50, `filament_type` PETG.

Đánh đổi:
- Scarf seam: giấu seam tốt trên chi tiết đơn giản ít overhang, cần PA đã hiệu chuẩn, tắt khi hình có góc nhọn (conditional scarf: góc ≥ 155° mới áp dụng) (wiki Orca seam).
- Ironing: làm phẳng mặt trên, nhưng chậm, dễ heat creep; không có nguồn nói tốt hay xấu riêng cho PETG → P.
- Arachne vs classic: Arachne đổi độ rộng đường để bám vách mỏng; classic dự đoán được hơn (wiki Orca). Mặc định A1 là classic; chi tiết vách mỏng cần Arachne là đề xuất P.
- `xy_hole/contour_compensation` không có số khuyến nghị chính thức (wiki Orca chỉ dẫn tới hiệu chuẩn). Quy ước STLab hiện nay: bù bằng khe thiết kế 0.2 mm, giữ 0.
- Chất lượng cong: layer 0.12–0.16 và adaptive là đề xuất P (profile có sẵn các bộ 0.12/0.16 cho A1 để dựng sẵn).

## 3. Luật tự chọn theo hình học

Đầu vào lấy từ mesh (trimesh hoặc `printability.py` có sẵn). Ngưỡng "S" có nguồn, "P" là đề xuất cần in thử.

### 3.1 Support

| Luật | Điều kiện | Hành động | Mức |
|---|---|---|---|
| Phần nhô | Mặt có góc từ mặt bàn < 45° (hoặc ngưỡng slicer 30°) | Cờ "cần support" | 45° có trong `thresholds.yaml` (nguồn Bambu wiki 5.1 do repo ghi); 30° là mặc định `support_threshold_angle` (S). Dùng một ngưỡng thôi cho nhất quán: slicer dùng 30° nên cờ 45° sẽ báo nhiều hơn slicer sinh. |
| Cầu | Mái ngang hẹp ≤ 5 mm, kín ≤ 8 mm | Không support | P (đã có trong repo, đang là TAM) |
| Nhô lớn mà đáy phẳng | Mặt nhô ngược lớn (diện tích > ~100 mm²) tách biệt | `support_type=normal(auto)` + `support_style=default/grid` | P |
| Nhô nhỏ rải rác, sát mặt | Phần lớn là điểm/cạnh nhỏ | `tree(auto)` | P |
| Support chạm mặt đẹp | Chi tiết có mặt "trong" đẹp | `support_on_build_plate_only=1`; nếu vẫn cần nhô giữa chi tiết thì đề xuất xoay/sửa model | P |
| Quy tắc chủ | Luôn | KHÔNG sinh support trong STL; xuất cờ vùng cần để Tuan tô paint (xem 4.3) | Quy tắc Tuan |
| Dễ gỡ mặc định | Luôn | Z 0.2, interface 2, spacing 0.5, XY 0.35 (mặc định profile) | S (profile) |
| Mặt dưới cần phẳng | Mặt nhô là mặt trang trí | interface 3, spacing 0.1, `support_interface_pattern=concentric` | P |

### 3.2 Brim

Repo đã làm: chân < `brim_contact_max_mm2` = 120 mm² hoặc cao/ngang ≥ 2.5 → `outer_only`, `brim_width=5` (cả hai ngưỡng là TAM). Đề xuất bổ sung (đều P):
- Chân lớn (> 120 mm²), thấp, phẳng: `no_brim` để bàn không có vết.
- Chi tiết cao mảnh (aspect ≥ 2.5) hoặc chân < 40 mm²: `brim_width` 5–8 (cần in thử, không có số nguồn).
- Chi tiết có góc nhọn bị cong mép (warping): `brim_ears` chỉ có trong Orca; với BS phải vẽ tay.
- Mép chi tiết cần đẹp: `brim_object_gap` 0.15–0.2.

### 3.3 Bề mặt

| Luật | Điều kiện | Hành động | Mức |
|---|---|---|---|
| Mặt cong lớn | Nhiều facet nghiêng 10–60° liên tục, tổng > ~30% diện tích | `layer_height` 0.12–0.16 hoặc `adaptive_layer_height=1` | P |
| Mặt trên phẳng lớn | Đỉnh phẳng > ~400 mm² | `ironing_type=topmost` tùy chọn | P |
| Lỗ nhiều | ≥ 4 lỗ hoặc lỗ gần nhau | `reduce_crossing_wall=1` (giảm tơ PETG) | P |
| Vách mỏng | Có vùng tường mỏng giữa 0.42 và 0.84 mm (`thresholds.yaml` min_wall_mm = 0.84) | `wall_generator=arachne` | P |
| Lỗ lắp ghép | Có lỗ có tên linh kiện | Giữ bù 0; khe theo bảng khe của dự án | Quy ước STLab |
| Mặt trước/đẹp | Biết mặt chọn | `seam_position=back` hoặc aligned + scarf `external` nếu chi tiết tròn trơn (sửa 2026-11-12: kèm `override_filament_scarf_seam_setting=1`, xem 8.5) | P |
| Chi tiết nhỏ (< 20×20 mm) | Bbox nhỏ | Chậm lại vì layer time min; kiểm `slow_down_for_layer_cooling` | P/TODO |

## 4. CLI

### 4.1 Bambu Studio CLI

Nguồn: https://github.com/bambulab/BambuStudio/wiki/Command-Line-Usage

Cờ có trong wiki: `--debug <0–5>`, `--load-settings "machine.json;process.json"` (phải là cấu hình đầy đủ), `--load-filaments "f1.json;;f3.json"` (bỏ trống để giữ filament trong 3MF), `--outputdir`, `--arrange 0|1|auto`, `--orient`, `--scale`, `--export-3mf`, `--export-settings`, `--export-slicedata`, `--load-slicedata`, `--info`, `--slice <0=tất cả|n>`, `--uptodate`, `--pipe`, `--curr-bed-type "Cool Plate"` (xuất hiện trong ví dụ). Ưu tiên: dòng lệnh `--key=value` > file `--load-settings` > cài đặt trong 3MF.

Quan sát cục bộ: `bambu-studio.exe --help` trên Windows không in gì ra stdout (chương trình kiểu GUI) nên không thể liệt kê cờ từ máy; dựa vào wiki. `--min-save` và `--allow-newer-file` KHÔNG có trong wiki này; `slice.py` hiện không dùng.

Cách repo đang làm (`tools/print/scripts/slice.py`): gộp `inherits` của process, ghi đè khóa vào JSON đầy đủ rồi `--load-settings machine;process --load-filaments filament --arrange 1 --orient 0|1 --avoid-extrusion-cali-region --slice 0 --export-3mf`. Cách này ổn định hơn `--key=value` và đã chạy thật. TODO: chưa kiểm BS có nhận `--support-top-z-distance=0.25` kiểu hyphen như Orca hay không; hiện không cần.

### 4.2 OrcaSlicer CLI

Nguồn: https://www.orcaslicer.com/wiki/cli/cli_mode
- Ví dụ: `orca-slicer model.3mf --load-settings "process.json;printer.json" --load-filaments filament.json --arrange 1 --slice 0 --export-3mf output.3mf`.
- Ghi đè trực tiếp: mọi khóa có dạng `--layer-height=0.16` (gạch dưới → gạch ngang); khóa vector dùng dấu phẩy; lặp cờ vector sẽ NỐI THÊM, không thay; 43 khóa không đặt được từ CLI (nhận dạng preset, mạng, chỉ số extruder).
- Giá trị boolean dùng `=0/=1`.
- TODO: Orca và BS khác nhau về một số khóa (`brim_ears_*`, `wall_sequence` vs `wall_infill_order`); 3MF xuất từ Orca không hoàn toàn mở được bằng BS ở mọi trường hợp; chưa kiểm.

### 4.3 Giới hạn đã biết và paint

- Support/seam/brim-ear được tô (paint) lưu trong 3MF: thuộc tính tam giác `paint_supports`, `paint_seam`, `paint_fuzzy_skin`, `paint_color`, và `Metadata/brim_ear_points.txt` (đọc từ `src/libslic3r/Format/bbs_3mf.cpp` của bản Orca cục bộ; BS có cùng hậu duệ, TODO xác nhận trên file do BS 02.09 ghi). CLI không có cờ "tô"; muốn tự động tô thì phải **ghi trực tiếp** các thuộc tính này vào 3MF (định dạng mã hóa bit-stream theo facet, phức tạp) → để TODO, không làm ở giai đoạn 1.
- Thiết lập theo đối tượng (per-object override) nằm trong `Metadata/model_settings.config`; cấu hình cả dự án trong `Metadata/project_settings.config`.
- `--arrange 1` có thể xếp lại bàn; `--orient` chọn hướng giảm support nhưng không biết quy tắc "sửa model"; repo đã chọn `--orient 0` khi STL đã đúng hướng.
- Đồng thời nhiều tiến trình CLI chạy song song được (repo đã làm); bảng in lớn cần kiểm `outside`.

## 5. Dự án cộng đồng (GitHub API tra 2026-11-12)

| Dự án | Sao | License | Cập nhật | Dùng được? |
|---|---|---|---|---|
| OrcaSlicer/OrcaSlicer | 16431 | AGPL-3.0 | 2026-11-12 | CLI cho dịch vụ nội bộ; AGPL chỉ ràng buộc khi phân phối/dịch vụ mạng, STLab phi thương mại → ghi chú, không chặn |
| bambulab/BambuStudio | 5272 | AGPL-3.0 | 2026-11-10 | Đang dùng qua CLI |
| prusa3d/PrusaSlicer | 9481 | AGPL-3.0 | 2026-11-07 | Chỉ tham khảo thuật toán support |
| mikedh/trimesh | 3723 | MIT | 2026-11-09 | Dùng được để phân tích mesh (diện tích, góc, hướng) |
| ChristophSchranz/Tweaker-3 | 110 | GPL-3.0 | 2026-03-24 | Tự chọn hướng in (tối thiểu support). Dùng được làm tham khảo hoặc gọi tiến trình riêng; ít sao, cập nhật chậm. Chưa kiểm chất lượng thực. |
| AFKFelix/orca-slicer-api | 79 | AGPL-3.0 | 2026-10-29 | REST bọc Orca CLI: tham khảo kiến trúc, không cần dùng |
| mgomezdev/laminus | 0 | không | 2026-11-10 | Bỏ qua (0 sao, không license) |
| sameer/orient-stl | 12 | MIT | 2023-07-06 | Cũ, bỏ qua |

Tìm "AI slicer tự tối ưu thông số" trên GitHub: tôi không thấy dự án nhiều sao, dùng được và còn bảo trì; không bịa tên. Hướng thực tế là luật tay (mục 3) + hiệu chuẩn bằng in thử. Chính slicer cũng có `--orient` (Bambu) và Orca có auto orient trong giao diện (TODO kiểm).

## 6. Đề xuất kiến trúc cho Toolhub

Khuyến nghị: **mở rộng /quote bằng một tab/bước "Tối ưu in"**, KHÔNG làm trang mới. Lý do: /quote đã có kéo file, gọi `quote_slice.py` (dùng lại hàm của `slice.py`), kết quả ảnh `plate_1.png` và `quote.3mf`. Trang mới nhân đôi upload/hàng đợi. Đánh đổi: /quote đang hướng khách báo giá; giao diện tối ưu hướng người vận hành → cần cờ chế độ (vd `?mode=tune`) để ẩn giá.

Luồng:
1. **Tải file** (STL/3MF) → lưu tạm như /quote hiện nay.
2. **Phân tích hình học** (module mới `tools/print/scripts/geometry_profile.py`, dựa trên `printability.py` + trimesh): chân, aspect, góc nhô, cầu, mặt cong, lỗ, vách mỏng → JSON `features`.
3. **Đề xuất bộ thông số** (module luật `tune_rules.py`, bảng luật ở mục 3, mỗi khóa kèm lý do + mức nguồn S/P + link). Hiển thị dạng bảng "khóa | giá trị | lý do | S/P".
4. **Người dùng chỉnh**: sửa từng giá trị, chọn "mặc định hãng" (xóa ghi đè) hoặc "tối ưu". Hạn chế khóa nâng cao (interface PLA) sau nút "Nâng cao" và cảnh báo AMS.
5. **Cắt lớp + xem trước**: gọi `slice.cat` với process ghi đè, trả ảnh `plate_1.png`, thời gian, gam, cảnh báo; có thể cắt 2 phương án (hãng vs tối ưu) song song để so sánh ảnh cạnh nhau (theo quy tắc "duyệt bằng ảnh").
6. **Xuất .3mf** (đã có `quote.3mf`) kèm file JSON thông số đã chọn. Vùng cần support xuất thành ảnh/danh sách để Tuan tô trong Bambu Studio (tuân quy tắc KHÔNG vẽ support vào STL).

Điểm kỹ thuật:
- Đầu ra thông số = dict ghi đè process, đúng cơ chế `d.update(overrides)` ở `slice.py` → không cần sửa slicer.
- Lưu lịch sử "tối ưu có hiệu quả hay không" (in thật, kết quả gỡ support) để dần chuyển ngưỡng P thành S. Đây là cách thay cho "AI".
- Thử Orca CLI chỉ khi cần `brim_ears`; mặc định giữ Bambu Studio CLI.

## 7. TODO / cần in thử

1. Mở các trang wiki Bambu (support, brim, PLA Basic + PETG HF) để xác nhận số liệu; trong phiên này không tải được (HTTP 402), chỉ có qua tìm kiếm.
2. In thử: `support_top_z_distance` 0.2 vs 0.25 trên cùng chi tiết PETG Basic, đo độ dễ gỡ và độ nhám mặt dưới (A/B, 3 lần).
3. In thử `support_interface_spacing` 0.5 / 0.1 / 0 và interface 1 / 2 / 3 lớp.
4. In thử `support_on_build_plate_only=1` + sửa model, so với `tree(auto)` mặc định.
5. In thử cặp PETG Basic + interface PLA Basic (A1 + AMS lite): lượng nhựa xả, độ dễ gỡ, mặt dưới.
6. Brim: `brim_width` 3/5/8 và `brim_object_gap` 0.1/0.15/0.2 với chi tiết thật (chân < 120 mm²); đo có bong không, mép có đẹp không.
7. Thử scarf seam `external` + conditional trên chi tiết tròn trơn; thử `wall_generator=arachne` cho vách 0.5–0.8 mm.
8. Ironing `topmost` trên mặt phẳng lớn: có heat creep trên A1 không.
9. Kiểm Bambu Studio 02.09 có nhận ghi đè `--key=value`; kiểm tên khóa `wall_infill_order` vs `wall_sequence` trong 3MF do BS ghi.
10. Xác nhận bit-stream `paint_supports` trong 3MF BS để có thể tự động tô (giai đoạn sau).
11. Ngưỡng hình học mục 3 đều là đề xuất P cho tới khi in thử; không có nguồn chính thức cho các số 120 mm², 2.5, 400 mm², ≥ 4 lỗ.


## 8. Danh mục đầy đủ thông số ảnh hưởng tháo support, bề mặt, bám bàn

Ngày: 2026-11-12. Rà soát toàn bộ khóa chứ không chỉ khóa đã gợi ý. Đơn vị: mm, °C, %, mm/s, mm/s².

### 8.0 Phương pháp, độ tin cậy, phát hiện chính

Nguồn và cách rà:
- `PrintConfig.cpp` BambuStudio master (tải 2026-11-12) và tag `v02.09.01.70`: hai file **giống hệt từng byte** (524930 byte, 784 khóa) nên dùng được cho BS 02.09. https://github.com/bambulab/BambuStudio/blob/v02.09.01.70/src/libslic3r/PrintConfig.cpp . Phạm vi process/filament/machine lấy từ `s_Preset_*_options` trong `Preset.cpp` cùng tag.
- `PrintConfig.cpp` OrcaSlicer main, 993 khóa (https://github.com/OrcaSlicer/OrcaSlicer/blob/main/src/libslic3r/PrintConfig.cpp ; SoftFever/OrcaSlicer chuyển hướng về đây).
- Giá trị A1 thật: gộp `inherits` của `0.20mm Standard @BBL A1` (212 khóa), `Bambu PETG Basic @BBL A1` (146 khóa), `Bambu Lab A1 0.4 nozzle` (115 khóa), đọc từ `C:\Program Files\Bambu Studio\resources\profiles\BBL`.
- Kiểm chéo với `BambuStudio.dll` đã cài: toàn bộ khóa BS có chuỗi trong DLL; khóa Orca-only (không có ở BS) hầu hết KHÔNG có trong DLL, nghĩa là BS 02.09 bỏ qua hoặc báo lỗi nếu ghi vào profile. DLL chỉ còn vài chuỗi khóa cũ (`brim_ears`, `tree_support_brim_width`).
- Số khóa rà (lọc theo nhóm support/raft/brim/skirt/lớp đầu/ironing/seam/shell/overhang/bridge/làm mát/tốc độ/retraction/độ chính xác): 680 khóa trùng bộ lọc rộng, 229 khóa đủ liên quan được đưa vào bảng bên dưới.
- Wiki OrcaSlicer đọc trực tiếp được: https://www.orcaslicer.com/wiki/print_settings/support/support_settings_advanced , https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_bridging , https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_seam , https://www.orcaslicer.com/wiki/print_settings/quality/quality_settings_ironing , https://www.orcaslicer.com/wiki/material_settings/cooling/material_cooling , https://www.orcaslicer.com/wiki/print_settings/speed/speed_settings_overhang_speed . Wiki Bambu (`wiki.bambulab.com/en/...`) vẫn HTTP 402; chỉ có bản zh qua kết quả tìm kiếm (https://wiki.bambulab.com/zh/software/bambu-studio/support): PETG cùng nhựa không đặt khe Z = 0, khoảng 0.2; khe lớn dễ gỡ nhưng mặt dưới xấu hơn. Phần ghi "qua tìm kiếm" cần Tuan mở lại.

Cách đọc bảng: **Có ở** B = Bambu Studio, O = OrcaSlicer, B+O = cả hai. **Mã** = mặc định trong PrintConfig (thường khác profile). **A1** = giá trị thật trong profile đã gộp (`—` = khóa chỉ có ở Orca; `(mặc định mã)` = profile không khai nên lấy mặc định mã). **Phạm vi**: P = khóa process (ghi vào `overrides` của slice.py), F = khóa filament (ghi vào `filament_overrides`), M = khóa machine/printer. **Ảnh hưởng**: a = support dễ gỡ + mặt tiếp xúc, b = bám bàn/gỡ brim/mép, c = bề mặt (đỉnh, đáy, thành, nhô, cầu, seam, tơ PETG). S = có nguồn chính thức (mã, profile hãng, wiki), P = đề xuất cần in thử.

Tám phát hiện quan trọng mà vòng trước bỏ sót:
1. **BS 02.09 không có quạt riêng cho interface support** (`support_material_interface_fan_speed` chỉ Orca, nằm ở filament). Mẹo "quạt cao ở interface cho dễ gỡ" của Orca không dùng được với BS. `overhang_fan_speed` chỉ cho nhô/cầu, không cho interface.
2. **Scarf seam do FILAMENT điều khiển**: profile A1 có `override_filament_scarf_seam_setting=0`, còn `filament_scarf_seam_type=none` của PETG Basic. Chỉ ghi `seam_slope_type=external` vào process là KHÔNG đủ (đã sửa mục 1 và 3.3 bên trên, ghi "sửa 2026-11-12").
3. **Các khóa support bị bỏ sót nhưng có ở BS**: `support_object_first_layer_gap`, `support_bottom_interface_spacing`, `tree_support_tip_diameter` (mũi nhánh dày = sẹo + khó gỡ), `tree_support_branch_distance`, `tree_support_branch_diameter_angle`, `support_angle`, `support_expansion`, `support_critical_regions_only`, `support_base_pattern(_spacing)`, `top_z_overrides_xy_distance`.
4. **BS có support ironing** (`enable_support_ironing` + `support_ironing_*`, đã nằm trong profile A1), cần `support_interface_spacing=0`. Cho mặt tiếp xúc support đẹp hơn bằng interface đặc + ủi (P).
5. **Chống vân/bóng thành ngoài**: `cooling_slowdown_logic=consistent_surface`, `no_slow_down_for_cooling_on_outwalls`, `precise_outer_wall`, `seam_placement_away_from_overhangs` (đều chỉ có sẵn ở BS 02.09, không nằm trong profile PETG Basic).
6. **Nhiều thông số retraction/nhô/cầu nằm ở FILAMENT hoặc MACHINE, không ở process**: `retraction_length` 0.8 (machine) bị `filament_retraction_length` 0.4 ghi đè; `filament_wipe_distance` 1, `filament_z_hop_types` Spiral Lift, `filament_bridge_speed` 25 (process `bridge_speed` 50), `filament_overhang_*` chỉ hiệu lực khi `override_process_overhang_speed=1` (profile 0). Ghi đè ở process JSON sẽ không đổi gì với các khóa này.
7. **`filament_shrink`** (co ngót XY theo nhựa, 100% = tắt) có ở BS; `enable_circle_compensation` mô tả mã chỉ hỗ trợ PLA Basic/PLA CF/PET CF/PETG CF/PETG HF, KHÔNG PETG Basic.
8. **Khóa chỉ có ở Orca, BS 02.09 không nhận**: `brim_ears*`, `support_flow_ratio`, `support_interface_flow_ratio`, `internal_bridge_*` (speed/flow/density/fan), `bridge_density`, `thick_internal_bridges`, `elefant_foot_compensation_layers`, `wipe_on_loops`, `role_based_wipe_speed`, `overhang_reverse`, `tree_support_auto_brim`, `initial_layer_fan_speed`. Thêm: `independent_support_layer_height` vô hiệu khi có prime tower; `wall_infill_order` (02.09.00.74) đã đổi tên thành `wall_sequence` ở master.

TODO còn lại: tên khóa nhận bởi đúng bản 02.09.00.74 đang cài (mã nguồn tag `v02.09.00.74` không có trên GitHub, dùng `v02.09.01.70`); thứ tự ưu tiên `filament_bridge_speed` so với `bridge_speed`; ngữ nghĩa `enable_height_slowdown`; mọi số P in thử A/B.

### 8.1 Support (process; riêng quạt interface xem 8.7)

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `enable_support` | B+O | bool | false | 0 | P | a | Bật bằng cờ auto hoặc paint. Quy tắc Tuan: không vẽ support vào STL (S). |
| `support_type` | B+O | enum | NormalAuto | tree(auto) | P | a | `tree(auto)` giữ (S profile). Mặt nhô phẳng lớn: `normal(auto)` (P). |
| `support_style` | B+O | enum | Default | default | P | a | `tree_slim` gộp nhánh mạnh, ít nhựa; `tree_strong` chắc nhưng khó gỡ (S mô tả mã). easy: `tree_slim` (P). |
| `support_threshold_angle` | B+O | int (°) | 30 | 30 | P | a | 30 (S). Chỉ đổi khi in thử nhô 35-40 vẫn đẹp (P). |
| `support_critical_regions_only` | B+O | bool | false | (mặc định mã) | P | a | Chỉ support vùng nguy cấp (đuôi nhọn, công-xôn): ít sẹo, nhưng thiếu support ở mái ngang nhỏ. Không vào preset mặc định (P). |
| `support_remove_small_overhang` | B+O | bool | true | (mặc định mã) | P | a | Giữ `1` (mặc định mã, S): bỏ nhô nhỏ không cần support. |
| `support_on_build_plate_only` | B+O | bool | false | 0 | P | a | `1` khi mặt chi tiết đẹp: hết sẹo trên chi tiết, nhưng nhô giữa chi tiết không có support (S/P). |
| `top_z_overrides_xy_distance` | B | bool | false | (mặc định mã) | P | a | Chỉ BS. Ưu tiên khe Z hơn khe XY; mã khuyên chỉ bật với `tree_hybrid` (S). Giữ 0. |
| `support_top_z_distance` | B+O | float (mm) | 0.2 | 0.2 | P | a,c | Khe Z trên. 0.2 giữ (S profile). PETG cùng nhựa không đặt 0 (wiki Bambu zh, qua tìm kiếm). Lớn = dễ gỡ, mặt dưới thô; easy 0.25 (P). |
| `support_bottom_z_distance` | B+O | float (mm) | 0.2 | 0.2 | P | a,c | Khe Z dưới 0.2 (S); 0.25 nếu support đứng trên chi tiết và khó gỡ (P). |
| `support_object_xy_distance` | B+O | float (mm) | 0.35 | 0.35 | P | a | 0.35 (S profile). Tăng 0.4-0.5 để dễ gỡ ở thành đứng; giảm 0.2 cho lỗ nhỏ (P). |
| `support_object_first_layer_gap` | B+O | float (mm) | 0.2 | (mặc định mã) | P | a | BỎ SÓT: khe XY lớp đầu giữa chi tiết và support, mặc định mã 0.2; không có trong profile A1 (S mã). Tăng khi support dính chân chi tiết (P). |
| `independent_support_layer_height` | B+O | bool | true | (mặc định mã) | P | a | Cho khe Z độc lập lớp; vô hiệu khi có prime tower (S mô tả mã). Profile A1 `enable_prime_tower=1` nhưng một nhựa thì tháp không sinh (P). |
| `support_interface_top_layers` | B+O | int (layers) | 3 | 2 | P | a,c | Profile 2, mã 3. 0-1 lớp dễ gỡ nhất, mặt thô (S wiki Orca); 3 lớp mặt đẹp hơn nhưng khó gỡ. easy 1 (P), pretty 3 (P). |
| `support_interface_bottom_layers` | B+O | int (layers) | 0 | 2 | P | a | Profile 2; -1 = bằng lớp trên (S). Support chỉ chạm bàn: 0; support đứng trên chi tiết: 1-2 (P). |
| `support_interface_spacing` | B+O | float (mm) | 0.5 | 0.5 | P | a,c | 0.5 (S profile): thưa, dễ gỡ. 0 = đặc (và là điều kiện bật `enable_support_ironing`). 0.1-0.2 mặt đẹp hơn (P). |
| `support_bottom_interface_spacing` | B+O | float (mm) | 0.5 | (mặc định mã) | P | a | BỎ SÓT: khoảng cách interface dưới, mặc định mã 0.5, không có trong profile (S mã). Cho bằng khoảng cách trên (P). |
| `support_interface_pattern` | B+O | enum | Auto | auto | P | a,c | `auto` (S profile). `concentric` tróc nguyên mảng, không để đầu đường lộ trên mặt (S wiki Orca); `rectilinear_interlaced` cứng hơn (S). Mặt tròn nhỏ concentric, mặt dài `auto` (P). |
| `support_interface_loop_pattern` | B+O | bool | false | 0 | P | c | Phủ lớp tiếp xúc trên bằng vòng; mặc định 0 (S mã). Chưa có số liệu (P/TODO). |
| `support_interface_not_for_body` | B+O | bool | true | (mặc định mã) | P | a | Mặc định true: nếu có nhựa interface riêng thì thân support không dùng nhựa đó (S mã). Chỉ có nghĩa với `support_interface_filament`. |
| `support_interface_filament` | B+O | int | 0 | 0 | P | a | 0 = cùng nhựa. PLA làm interface cho PETG Basic chưa có nguồn chính thức và tốn AMS (xem 2.1). Không dùng mặc định (P/TODO). |
| `support_filament` | B+O | int | 0 | 0 | P | a | 0 (S profile). |
| `support_interface_speed` | B+O | float[] (mm/s) | 80 | 80 | P | a,c | Profile 80 mm/s (S). 40-50 mm/s cho mặt interface đẹp hơn (P). |
| `support_speed` | B+O | float[] (mm/s) | 80 | 150 | P | a | Profile 150 mm/s (S). |
| `support_line_width` | B+O | float (mm) | 0.4 | 0.42 | P | a | 0.42 mm (S profile). Tăng 0.45-0.5 làm support cứng, khó gỡ (P). |
| `support_base_pattern` | B+O | enum | Default | default | P | a | `default`; có `rectilinear`, `rectilinear-grid`, `honeycomb`, `lightning`, `hollow` (S mã). `lightning`/`hollow` ít nhựa, dễ gỡ (P/TODO). Chỉ cho support normal. |
| `support_base_pattern_spacing` | B+O | float (mm) | 2.5 | 2.5 | P | a | 2.5 mm (S profile). 3-4 mm nhanh và dễ gỡ nhưng interface dễ võng (P). |
| `support_angle` | B+O | float (°) | 0 | (mặc định mã) | P | a,c | Xoay mẫu support 0-359° (S mã). Chọn góc cắt chéo đường in mặt chi tiết cho vết mờ hơn (P). |
| `support_expansion` | B+O | float (mm) | 0 | 0 | P | a | Nở/co vùng support normal theo chiều ngang; âm giảm sẹo cạnh (S mã). Profile 0. -0.5 thử (P). |
| `enable_support_ironing` | B | bool | false | 0 | P | c | Chỉ BS (Orca: `support_ironing`). Ủi lớp interface cho mặt dưới phẳng; cần `support_interface_spacing=0` (S mô tả mã). Dùng trong pretty (P). |
| `support_ironing_flow` | B+O | % | 10 | 10% | P | c | 10% (S profile). |
| `support_ironing_spacing` | B+O | float (mm) | 0.1 | 0.15 | P | c | 0.15 mm (S profile); ≤ đường kính vòi (S wiki Orca ironing). |
| `support_ironing_speed` | B | float (mm/s) | 20 | 30 | P | c | 30 mm/s (S profile). |
| `support_ironing_pattern` | B+O | enum | Rectilinear | zig-zag | P | c | `zig-zag` (S profile). |
| `support_ironing_inset` | B | float (mm) | 0 | 0.0 | P | c | 0.0 (S profile). |
| `support_ironing_direction` | B | float (°) | 0 | 0 | P | c | 0° (S profile). |
| `support_flow_ratio` | O | float | 1 | — | P | a,c | CHỈ Orca. BS 02.09 không có. |
| `support_interface_flow_ratio` | O | float | 1 | — | P | a,c | CHỈ Orca; giảm 0.9-0.95 làm interface bám yếu, dễ gỡ (P). |
| `support_threshold_overlap` | O | mm|% (mm or %) | 50., true | — | P | a | CHỈ Orca. |
| `tree_support_branch_angle` | B+O | float (°) | 40. | 45 | P | a | 40 mã, 45 profile (S). |
| `tree_support_branch_distance` | B+O | float (mm) | 5. | (mặc định mã) | P | a,c | Khoảng cách nút nhánh, mã 5 mm (S). Tăng 6-7: ít điểm chạm, dễ gỡ, mặt dưới võng hơn (P). |
| `tree_support_branch_diameter` | B+O | float (mm) | 5. | 2 | P | a | 2 mm (S profile); mã 5. |
| `tree_support_branch_diameter_angle` | B+O | float (°) | 5. | (mặc định mã) | P | a | Mặc định mã 5°: nhánh dày dần về gốc cho chắc (S mô tả mã). |
| `tree_support_tip_diameter` | B+O | float (mm) | 0.8 | (mặc định mã) | P | a,c | BỎ SÓT: đường kính mũi nhánh, mã 0.8 mm, không có trong profile. Mũi dày bám chắc nhưng sẹo nặng, khó gỡ (S mô tả mã); easy 0.5-0.6 (P). |
| `tree_support_wall_count` | B+O | int | -1 | -1 | P | a | -1 tự động (S profile). 0 cho phép chỉ-infill khi đủ dày; 2 chắc hơn (S mã). |
| `support_max_bridge_length` | B+O | float | 15.0 | (mặc định mã) | — | a | Tree: cầu dài nhất không support, mặc định mã 15 mm (S). |
| `bridge_no_support` | B+O | bool | false | 0 | P | a | 0 (S profile). Bật 1 để bỏ support cho cầu ngắn (P). |
| `avoid_crossing_wall_includes_support` | B | bool | false | 0 | P | a | Chỉ BS: khi tránh vượt tường có tính support; profile 0 (S). |
| `tree_support_auto_brim` | O | bool | 1 | — | P | b | CHỈ Orca. BS 02.09 bỏ qua; `tree_support_brim_width` nằm trong danh sách khóa cũ của BS (S mã). |

### 8.2 Raft

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `raft_layers` | B+O | int (layers) | 0 | 0 | P | b | 0 (S profile). Raft cho chi tiết rất mảnh 2-3 lớp; mặt đáy thô (P). |
| `raft_contact_distance` | B+O | float (mm) | 0.1 | (mặc định mã) | P | b,c | Khe Z raft-vật thể, mặc định mã 0.1. PETG cùng nhựa nên 0.2 để gỡ (P). |
| `raft_expansion` | B+O | float (mm) | 1.5 | (mặc định mã) | P | b | 1.5 mm (mã). |
| `raft_first_layer_density` | B+O | % | 90 | (mặc định mã) | P | b | 90% (mã); thấp hơn dễ gỡ nhưng bám yếu (P). |
| `raft_first_layer_expansion` | B+O | float (mm) | -1 | (mặc định mã) | P | b | -1 = tự động (mã). |

### 8.3 Brim, skirt, lớp đầu, bám bàn

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `brim_type` | B+O | enum | AutoBrim | (mặc định mã) | P | b | BS: auto_brim (mặc định mã) / brim_ears (Painted) / outer_only / inner_only / outer_and_inner / no_brim (S). Dùng `outer_only`. |
| `brim_width` | B+O | float (mm) | 0. | 5 | P | b | 5 mm (S profile). Nhỏ/mảnh 5-8 (P). Chân lớn 0-3. |
| `brim_object_gap` | B+O | float (mm) | 0. | 0.1 | P | b,c | Profile 0.1. Khe lớn = dễ gỡ, bám yếu hơn (S mô tả mã). 0.15 cho easy (P). |
| `brim_ears` | O | bool | false | — | — | b | CHỈ Orca (DLL BS chỉ còn tên cũ). Dùng `brim_type=brim_ears` + vẽ tay trong BS (S). |
| `brim_ears_max_angle` | O | float | 125 | — | P | b | CHỈ Orca, 125° (S). |
| `brim_ears_detection_length` | O | float (mm) | 1 | — | P | b | CHỈ Orca, 1 mm (S). |
| `brim_flow_ratio` | O | float | 1 | — | P | b | CHỈ Orca. |
| `brim_use_efc_outline` | O | bool | false | — | P | b | CHỈ Orca; brim bám theo biên sau bù elefant foot (S mô tả mã). |
| `skirt_loops` | B+O | int | 1 | 0 | P | b | 0 (S profile). Skirt không ảnh hưởng bám. |
| `skirt_distance` | B+O | float (mm) | 2 | 2 | P | b | 2 mm (S profile). |
| `skirt_height` | B+O | int (layers) | 1 | 1 | P | b | 1 lớp (S profile). |
| `skirt_per_object` | B | bool | true | 1 | P | b | Chỉ BS (S mã). |
| `draft_shield` | B+O | enum | Disabled | disabled | P | c | `disabled` (S). Tường chắn gió cho chi tiết cao PETG ở A1 khung hở (P/TODO). |
| `initial_layer_print_height` | B+O | float (mm) | 0.2 | 0.2 | P | b | 0.2 mm (S profile). |
| `initial_layer_speed` | B+O | float[] (mm/s) | 30 | 50 | P | b,c | 50 mm/s (S profile). Chi tiết nhỏ/cao 30 mm/s (P). |
| `initial_layer_infill_speed` | B+O | float[] (mm/s) | 60.0 | 105 | P | b | 105 mm/s (S profile). |
| `initial_layer_line_width` | B+O | float (mm) | 0.4 | 0.5 | P | b | 0.5 mm (S profile): đường rộng bám tốt hơn. |
| `initial_layer_infill_line_width` | B | float (mm) | 0 | 0.5 | P | b | 0.5 mm (S profile). |
| `initial_layer_acceleration` | B+O | float[] | 300 | 500 | P | b | 500 mm/s² (S profile). |
| `initial_layer_travel_acceleration` | B+O | float[] | 500.0 | 6000 | P | b | 6000 mm/s² (S profile). |
| `initial_layer_flow_ratio` | B | float | 1 | (mặc định mã) | P | b,c | BỎ SÓT, chỉ BS: dòng nhựa lớp đầu, mã 1, không có trong profile. 1.02-1.05 nếu lớp đầu thiếu nhựa (P). |
| `only_one_wall_first_layer` | B+O | bool | false | (mặc định mã) | P | b | Mặc định mã false. 1 tường ở lớp đầu: bám nhanh trên chi tiết nhỏ (P). |
| `bottom_surface_pattern` | B+O | enum | Rectilinear | monotonic | P | b,c | `monotonic` (S profile). `bottom_surface_fill_order` chỉ Orca. |
| `bottom_surface_density` | B+O | % | 100 | 100 | P | b,c | 100% (S profile). Hạ dưới 100 làm vân mặt đáy nhưng bám yếu (S mô tả mã). |
| `bottom_shell_layers` | B+O | int | 3 | 3 | P | b,c | 3 (S profile). |
| `elefant_foot_compensation` | B+O | float (mm) | 0. | 0.075 | P | b,c | 0.075 mm (S profile): co lớp đầu chống chân voi. |
| `elefant_foot_min_width` | B+O | float | 0.2 | (mặc định mã) | — | b,c | Chỉ BS/Orca: bề rộng tối thiểu sau bù, mã 0.2; không có trong profile (S mã). |
| `elefant_foot_compensation_layers` | O | int (layers) | 1 | — | P | b,c | CHỈ Orca; BS không có. |
| `nozzle_temperature_initial_layer` | B+O | int[] | 200 | 245 | F | b | 245 °C (S profile PETG Basic). |
| `textured_plate_temp_initial_layer` | B+O | int[] | 45 | 70 | F | b | 70 °C (S profile). |
| `textured_plate_temp` | B+O | int[] | 45 | 70 | F | b | 70 °C (S profile). |
| `hot_plate_temp` | B+O | int[] | 45 | 70 | F | b | 70 °C (S profile). Không áp cho Textured PEI. |
| `close_fan_the_first_x_layers` | B+O | int[] (layers) | 1 | 3 | F | b | 3 lớp (S profile): tắt quạt 3 lớp đầu. |
| `first_x_layer_part_fan_speed` | B | int[] | 0 | (mặc định mã) | F | b | Chỉ BS; quạt part ở lớp đầu, mã 0 (S). |
| `temperature_vitrification` | B+O | int[] | 100 | 55 | F | b | 55 °C (S profile): nhiệt hóa mềm dùng kiểm tra bàn, không phải thông số in. |
| `filament_adhesiveness_category` | B+O | int[] | 0 | 300 | F | b | 300 (S profile). Nhóm bám dính khi in nhiều nhựa; tác dụng thực tế TODO. |

### 8.4 Bề mặt: đỉnh, đáy, thành, độ phân giải

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `layer_height` | B+O | float (mm) | 0.2 | 0.2 | P | c | 0.2 (S). Mặt cong 0.12-0.16 (P). |
| `adaptive_layer_height` | B+O | bool | 0 | 0 | P | c | 0 (S profile). Trong BS master khóa nằm ở danh sách cũ; DLL 02.09.00.74 vẫn có chuỗi (TODO kiểm hoạt động). |
| `top_shell_layers` | B+O | int | 4 | 5 | P | c | 5 (S profile). |
| `top_shell_thickness` | B+O | float (mm) | 0.6 | 1.0 | P | c | 1.0 mm (S profile). |
| `bottom_shell_thickness` | B+O | float (mm) | 0. | 0 | P | c | 0 = chỉ theo số lớp (S profile). |
| `top_surface_pattern` | B+O | enum | Rectilinear | monotonicline | P | c | `monotonicline` (S profile). `concentric` mặt tròn (P). |
| `top_surface_line_width` | B+O | float (mm) | 0.4 | 0.42 | P | c | 0.42 mm (S profile). |
| `top_surface_speed` | B+O | float[] (mm/s) | 100 | 200 | P | c | 200 mm/s (S profile). 100-120 mm/s cho đỉnh mịn (P). |
| `top_surface_acceleration` | B+O | float[] | 500 | 2000 | P | c | 2000 mm/s² (S profile); 1000-1500 thử (P). |
| `top_surface_density` | B+O | % | 100 | 100 | P | c | 100% (S). Thấp hơn làm vân trang trí (S mô tả mã). |
| `top_solid_infill_flow_ratio` | B+O | float[] | 1 | 1 | P | c | 1 (S profile). Giảm nhẹ 0.97-0.98 cho đỉnh nhẵn (S mô tả mã Orca; số P). |
| `infill_wall_overlap` | B+O | % | 15 | 15% | P | c | 15% (S profile). Orca có thêm `top_bottom_infill_wall_overlap`. |
| `only_one_wall_top` | O | bool | false | — | P | c | 1 (S profile). BS master đã đưa vào danh sách khóa cũ; DLL vẫn có chuỗi (S mã/TODO). |
| `ironing_type` | B+O | enum | NoIroning | no ironing | P | c | `no ironing` (S). `top`/`topmost`/`solid` (S mã). Ủi mặt phẳng lớn; chậm, rủi ro heat creep (S wiki Orca). |
| `ironing_flow` | B+O | % | 10 | 10% | P | c | 10% (S profile). |
| `ironing_spacing` | B+O | float (mm) | 0.1 | 0.15 | P | c | 0.15 mm (S profile); ≤ đường kính vòi (S wiki Orca). |
| `ironing_speed` | B+O | float (mm/s) | 20 | 30 | P | c | 30 mm/s (S profile). |
| `ironing_inset` | B+O | float (mm) | 0 | 0.21 | P | c | 0.21 mm (S profile); mã 0. |
| `ironing_pattern` | B+O | enum | Rectilinear | (mặc định mã) | P | c | Mặc định mã `rectilinear`; không có trong profile. |
| `ironing_direction` | B | float (°) | 45 | (mặc định mã) | P | c | Chỉ BS, 45° (S mã). Orca đổi thành `ironing_angle`. |
| `ironing_fan_speed` | B+O | int[] | -1 | (mặc định mã) | F | c | BỎ SÓT: khóa FILAMENT của BS, mã -1 = không đổi; hạ quạt khi ủi để tránh tắc (S mô tả mã). Không có trong profile PETG Basic (P). |
| `wall_loops` | B+O | int | 2 | 2 | P | c | 2 (S profile). |
| `wall_generator` | B+O | enum | Arachne | classic | P | c | `classic` (S profile). `arachne` vách mỏng (P). |
| `wall_infill_order` | B (02.09.00.74; master: `wall_sequence`) | enum | | inner wall/outer wall/in | P | c | BS 02.09.00.74 dùng khóa này; master đổi sang `wall_sequence` (S mã, handler dòng 8396). Profile `inner wall/outer wall/infill` (S). `inner-outer-inner wall` có ở master (TODO thử với 02.09.00.74). |
| `precise_outer_wall` | B+O | bool | false | (mặc định mã) | P | c | BỎ SÓT: chỉnh khoảng cách tường ngoài để kích thước chính xác, lớp đều (S mô tả mã). Mặc định false, không có trong profile. Bật cho chi tiết lắp ghép đẹp (P). |
| `outer_wall_speed` | B+O | float[] (mm/s) | 60 | 200 | P | c | 200 mm/s (S profile). 100-120 mm/s cho thành đẹp (P). |
| `inner_wall_speed` | B+O | float[] (mm/s) | 60 | 300 | P | c | 300 mm/s (S profile). |
| `outer_wall_acceleration` | B+O | float[] | 500 | 5000 | P | c | 5000 mm/s² (S profile). 2000-3000 giảm rung dội (P). |
| `inner_wall_acceleration` | B+O | float[] | 0 | 0 | P | c | 0 = theo mặc định (S profile). |
| `default_acceleration` | B+O | float[] | 500.0 | 6000 | P | c | 6000 mm/s² (S profile). |
| `outer_wall_line_width` | B+O | float (mm) | 0 | 0.42 | P | c | 0.42 mm (S profile). |
| `inner_wall_line_width` | B+O | float (mm) | 0.4 | 0.45 | P | c | 0.45 mm (S profile). |
| `line_width` | B+O | float (mm) | 0.4 | 0.42 | P | c | 0.42 mm (S profile). |
| `resolution` | B+O | float (mm) | 0.01 | 0.012 | P | c | 0.012 mm (S profile). |
| `enable_arc_fitting` | B+O | bool | 0 | 1 | P | c | 1 (S profile): G2/G3. |
| `xy_hole_compensation` | B+O | float (mm) | 0 | 0 | P | c | 0 (S profile); quy tắc STLab bù bằng khe thiết kế. |
| `xy_contour_compensation` | B+O | float (mm) | 0 | 0 | P | c | 0 (S profile). |
| `enable_circle_compensation` | B | bool | false | 0 | P | c | Chỉ BS: bù lỗ/trụ tròn Ø<50 mm; mô tả mã chỉ hỗ trợ PLA Basic, PLA CF, PET CF, PETG CF, PETG HF, không nêu PETG Basic (S). Giữ 0. |
| `circle_compensation_manual_offset` | B | float (mm) | 0.0 | 0 | P | c | Chặt/lỏng lắp ghép, chỉ có tác dụng khi bật bù tròn (S mã). 0. |
| `filament_shrink` | B+O | %[] (%) | 100 | 100% | F | c | BỎ SÓT, chỉ BS, khóa FILAMENT: co ngót XY, 100% = tắt (S mã; profile 100%). PETG ~99.5% thử, cần đo (P/TODO). |
| `detect_thin_wall` | B+O | bool | false | 0 | P | c | 0 (S profile); 1 in vách mỏng 1 đường (P). |
| `ensure_vertical_shell_thickness` | B+O | enum | (EnsureVerticalThickne | (mặc định mã) | P | c | Có trong mã; không khai ở profile (TODO). |
| `fuzzy_skin` | B+O | enum | None | none | P | c | `none` (S profile). Giấu vân và tơ nhưng mặt nhám (P). |
| `gap_infill_speed` | B+O | float[] (mm/s) | 30 | 250 | P | c | 250 mm/s (S profile). |
| `internal_solid_infill_speed` | B+O | float[] (mm/s) | 100 | 250 | P | c | 250 mm/s (S profile). |
| `top_surface_expansion` | O | float (mm) | 0 | — | P | c | CHỈ Orca. |
| `slowdown_for_curled_perimeters` | O | bool[] | false | — | P | c | CHỈ Orca. |
| `small_perimeter_speed` | B+O | mm|%[] (mm/s|%) | (50, true) | 50% | P | c | 50% (S profile); mm/s hoặc %. |
| `small_perimeter_threshold` | B+O | float[] (mm) | 0 | 0 | P | c | 0 mm (S profile). Chi tiết có lỗ nhỏ 6-8 mm làm chậm tường nhỏ (P). |
| `enable_height_slowdown` | B | bool[] | false | 0 | P | c | Chỉ BS: chậm theo chiều cao, profile 0; đi kèm `slowdown_*_height/speed/acc` (S profile). Cho chi tiết cao mảnh (P/TODO ngữ nghĩa). |

### 8.5 Seam, scarf

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `seam_position` | B+O | enum | Aligned | aligned | P | c | `aligned` (S profile). `back` khi cần giấu mặt trước (S). |
| `seam_gap` | B+O | % | 15 | (mặc định mã) | P | c | 15% mặc định mã; không có trong profile. Orca khuyên 0-15% khi PA/retraction chuẩn (S wiki Orca). |
| `seam_placement_away_from_overhangs` | B | bool | false | 0 | P | c | Chỉ BS: seam tránh nhô, profile 0 (S). Bật cho seam đẹp (P). |
| `seam_slope_type` | B+O | enum | None | none | P | c | `none`/`external`/`all` (S mã). Profile none. |
| `override_filament_scarf_seam_setting` | B | bool | false | 0 | P | c | BỎ SÓT: profile 0 nghĩa scarf lấy theo FILAMENT (`filament_scarf_seam_type`=none). Muốn bật scarf ở process phải đặt =1 (S mô tả mã). |
| `filament_scarf_seam_type` | B | enum[] | 0 | none | F | c | FILAMENT, `none` (S profile). Bật scarf cho PETG Basic: đổi tại đây hoặc override process. |
| `filament_scarf_height` | B | mm|%[] (mm/%) | (10, true) | 10% | F | c | 10% (S profile). |
| `filament_scarf_length` | B | float[] | 10 | 10 | F | c | 10 mm (S profile); 0 tắt (S mã). |
| `filament_scarf_gap` | B | mm|%[] (mm/%) | (0, 0) | 0% | F | c | 0% (S profile). |
| `seam_slope_conditional` | B+O | bool | true | (mặc định mã) | P | c | Chỉ áp cho đường trơn; mặc định true (S mã). |
| `scarf_angle_threshold` | B+O | int (°) | 155 | 155 | P | c | 155° (S profile). |
| `seam_slope_min_length` | B+O | float | 10 | 10 | P | c | 10 mm (S profile); 0 tắt. |
| `seam_slope_start_height` | B+O | mm|% (mm/%) | 10, true | 10% | P | c | 10% (S profile). |
| `seam_slope_steps` | B+O | int | 10 | (mặc định mã) | P | c | 10 (mặc định mã). |
| `seam_slope_inner_walls` | B+O | bool | true | (mặc định mã) | P | c | true (mặc định mã). |
| `seam_slope_entire_loop` | B+O | bool | false | (mặc định mã) | P | c | false (mặc định mã). |
| `seam_slope_gap` | B | mm|% (mm/%) | 0, 0 | 0 | P | c | 0 (S profile). |
| `apply_scarf_seam_on_circles` | B | bool | true | (mặc định mã) | P | c | Chỉ BS: true (S mã); scarf trên hình tròn cho kích thước chính xác. |
| `wipe_on_loops` | O | bool | false | — | P | c | CHỈ Orca. |
| `role_based_wipe_speed` | O | bool | true | — | P | c | CHỈ Orca. BS dùng `wipe_speed`. |
| `wipe_speed` | B+O | % | 80 | (mặc định mã) | P | c | 80% mặc định mã, tính theo tốc độ di chuyển (S mô tả mã). Không có trong profile. |
| `wipe_before_external_loop` | O | bool | false | — | P | c | CHỈ Orca. |

### 8.6 Nhô, cầu

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `detect_overhang_wall` | B+O | bool | true | 1 | P | c | 1 (S profile). |
| `enable_overhang_speed` | B+O | bool[] | true | 1 | P | c | 1 (S profile). |
| `overhang_1_4_speed` | B+O | float[] (mm/s) | 0 | 0 | P | c | 0 (S profile): 0 = không chậm. |
| `overhang_2_4_speed` | B+O | float[] (mm/s) | 0 | 50 | P | c | 50 mm/s (S profile). |
| `overhang_3_4_speed` | B+O | float[] (mm/s) | 0 | 30 | P | c | 30 mm/s (S profile). |
| `overhang_4_4_speed` | B+O | float[] (mm/s) | 0 | 10 | P | c | 10 mm/s (S profile). |
| `overhang_totally_speed` | B | float[] (mm/s) | 10 | 10 | P | c | 10 mm/s (S profile); chỉ BS. |
| `override_process_overhang_speed` | B | bool[] | false | 0 | F | c | FILAMENT, 0 (S profile): filament PETG có bộ `filament_overhang_*` (0/50/30/10/10) nhưng chỉ hiệu lực khi =1 (S mô tả mã). |
| `detect_floating_vertical_shell` | B | bool | true | 1 | P | c | Chỉ BS: làm chậm tường dọc lơ lửng như cầu (S mã); profile 1. |
| `bridge_speed` | B+O | float[] (mm/s) | 25 | 50 | P | c | Process 50 mm/s; filament PETG `filament_bridge_speed` 25 mm/s (S profile). Thứ tự ưu tiên chưa xác nhận (TODO). |
| `bridge_flow` | B+O | float | 1 | 1 | P | c | 1 (S profile). 0.9-0.95 giảm võng (S mô tả mã; số P). |
| `thick_bridges` | B+O | bool | false | (mặc định mã) | P | c | false mặc định mã. Cầu ngắn đẹp hơn khi tắt; cầu dài tin cậy hơn khi bật (S mô tả mã). |
| `bridge_angle` | B+O | float (°) | 0. | (mặc định mã) | P | c | 0 = tự động (mã). |
| `max_bridge_length` | B+O | float (mm) | 10 | 0 | P | c | Profile 0; nghĩa ở process chưa rõ (TODO). |
| `internal_bridge_support_thickness` | B | float (mm) | 0 | 0.8 | P | c | Chỉ BS: vòng neo cho cầu trong, profile 0.8 mm (S). Giảm võng đỉnh. |
| `counterbore_hole_bridging` | B+O | enum | None | (mặc định mã) | P | c | BS/Orca; cầu lỗ bậc (S wiki Orca). |
| `internal_bridge_speed` | O | mm|%[] (mm/s|%) | (150, true) | — | P | c | CHỈ Orca. |
| `internal_bridge_flow` | O | float | 1 | — | P | c | CHỈ Orca. |
| `internal_bridge_density` | O | % | 100 | — | P | c | CHỈ Orca. |
| `bridge_density` | O | % | 100 | — | P | c | CHỈ Orca; trần 125% (S wiki Orca). |
| `thick_internal_bridges` | O | bool | true | — | P | c | CHỈ Orca. |
| `overhang_reverse` | O | bool | false | — | P | c | CHỈ Orca. |
| `extra_perimeters_on_overhangs` | O | bool | false | — | P | c | CHỈ Orca. |
| `make_overhang_printable` | O | bool | false | — | P | a | CHỈ Orca; sửa hình học nhô để đỡ support (S). Quy tắc STLab: sửa model, không dùng slicer. |

### 8.7 Làm mát, quạt, dòng (khóa FILAMENT)

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `fan_min_speed` | B+O | int[] | 20 | 30 | F | c | 30% (S profile). |
| `fan_max_speed` | B+O | int[] | 100 | 50 | F | c | 50% (S profile). |
| `fan_cooling_layer_time` | B+O | int[] (s) | 60 | 30 | F | c | 30 s (S profile). |
| `slow_down_for_layer_cooling` | B+O | bool[] | true | 1 | F | c | 1 (S profile). |
| `slow_down_layer_time` | B+O | int[] (s) | 5 | 12 | F | c | 12 s (S profile). Chi tiết nhỏ 15-20 s (P). |
| `slow_down_min_speed` | B+O | float[] (mm/s) | 10. | 10 | F | c | 10 mm/s (S profile). |
| `overhang_fan_speed` | B+O | int[] | 100 | 50 | F | c | 50% (S profile). Chỉ cho nhô và cầu, KHÔNG cho interface support (S mã). |
| `overhang_fan_threshold` | B+O | enum[] | Overhang_threshold_bri | 10% | F | c | 10% (S profile). |
| `enable_overhang_bridge_fan` | B+O | bool[] | true | (mặc định mã) | F | c | true (mặc định mã); profile không khai. |
| `overhang_threshold_participating_cooling` | B | enum[] | EnumsGeneric{ Overhang | (mặc định mã) | F | c | Chỉ BS: mức nhô tham gia làm chậm tản nhiệt (S mã). Không có trong profile. |
| `reduce_fan_stop_start_freq` | B+O | bool[] | false | 1 | F | c | 1 (S profile). |
| `full_fan_speed_layer` | B+O | int[] | 0 | 0 | F | c | 0 (S profile). |
| `pre_start_fan_time` | B | float[] (s) | 0.0 | 0 | F | c | 2 s (S profile filament). |
| `cooling_slowdown_logic` | B | enum[] | UniformCooling | uniform_cooling | F | c | BỎ SÓT, chỉ BS 02.09: `uniform_cooling` (profile) hoặc `consistent_surface`: bảo toàn tốc độ tường ngoài khi chậm cho nguội (S mô tả mã). Bề mặt đẹp (P). |
| `no_slow_down_for_cooling_on_outwalls` | B | bool[] | false | 0 | F | c | BỎ SÓT, chỉ BS: tường ngoài không chậm theo layer-time (S mô tả mã), profile 0. Orca: `dont_slow_down_outer_wall`. |
| `cooling_perimeter_transition_distance` | B | float[] (mm) | 10.0 | 10 | F | c | 10 mm (S profile); chỉ khi `consistent_surface` (S mã). |
| `support_material_interface_fan_speed` | O | int[] | -1 | — | F | a | BỎ SÓT: CHỈ Orca (filament): quạt cao ở interface làm support dễ gỡ (S wiki Orca). BS 02.09 KHÔNG có; thay bằng custom G-code (TODO). |
| `internal_bridge_fan_speed` | O | int[] | -1 | — | F | c | CHỈ Orca. |
| `initial_layer_fan_speed` | O | int[] | -1 | — | F | b | CHỈ Orca; BS dùng `first_x_layer_part_fan_speed`. |
| `additional_cooling_fan_speed` | B+O | int[] | 0 | 0 | F | c | Quạt phụ; A1 `auxiliary_fan=0` nên vô nghĩa (S profile). |
| `filament_max_volumetric_speed` | B+O | float[] (mm³/s) | 2. | 13 | F | c | 13 mm³/s (S profile PETG Basic). 10 mm³/s cho cầu/chi tiết nhỏ (P). |
| `filament_flow_ratio` | B+O | float[] | 1. | 0.94 | F | c | 0.94 (S profile). |
| `filament_adaptive_volumetric_speed` | B+O | bool[] | false | 0 | F | c | 0 (S profile). |
| `nozzle_temperature` | B+O | int[] | 200 | 245 | F | c | 245 °C, dải 230-270 (S profile). |

### 8.8 Retraction, wipe, di chuyển (tơ PETG)

| Khóa | Có ở | Kiểu (đv) | Mã | A1 | Phạm vi | Ảnh hưởng | Ghi chú / đề xuất A1+PETG Basic |
|---|---|---|---|---|---|---|---|
| `retraction_length` | B+O | float[] (mm) | 0.8 | 0.8 | — | c | MACHINE 0.8 mm; FILAMENT `filament_retraction_length` 0.4 mm ghi đè (S profile). 0.6 thử (P). |
| `retraction_speed` | B+O | float[] (mm/s) | 30. | 30 | — | c | MACHINE 30 mm/s; filament nil = theo máy (S profile). |
| `deretraction_speed` | B+O | float[] (mm/s) | 0. | 30 | — | c | MACHINE 30 (S profile). |
| `retract_before_wipe` | B+O | %[] | 100 | 0% | — | c | MACHINE 0% (S profile). |
| `wipe` | B+O | bool[] | false | 1 | — | c | MACHINE 1 (S profile). |
| `wipe_distance` | B+O | float[] (mm) | 2. | 2 | — | c | MACHINE 2 mm; FILAMENT `filament_wipe_distance` 1 mm (S profile). |
| `z_hop` | B+O | float[] (mm) | 0.4 | 0.4 | — | c | MACHINE 0.4 mm; filament loại Spiral Lift (S profile). Z-hop để lại vết/tơ; 0.2 thử (P). |
| `z_hop_types` | B+O | enum[] | Spiral | Auto Lift | M | c | MACHINE `Auto Lift`; filament Spiral Lift (S profile). |
| `retract_lift_above` | B+O | float[] (mm) | 0. | 0 | — | c | 0 (S profile). |
| `retract_lift_below` | B+O | float[] (mm) | 0. | 255 | — | c | 255 (S profile). |
| `retraction_minimum_travel` | B+O | float[] (mm) | 2. | 1 | — | c | 1 mm (S profile). |
| `retract_when_changing_layer` | B+O | bool[] | false | 1 | — | c | 1 (S profile). |
| `retract_restart_extra` | B+O | float[] (mm) | 0. | 0 | — | c | 0 (S profile). |
| `reduce_crossing_wall` | B+O | bool | false | 0 | P | c | 0 (S profile). 1 giảm tơ PETG qua mặt chi tiết (P). |
| `max_travel_detour_distance` | B+O | mm|% (mm or %) | 0., false | 0 | P | c | 0 = không giới hạn (S mô tả mã). Đặt 50% khi bật `reduce_crossing_wall` để khỏi đi vòng xa (P). |
| `travel_speed` | B+O | float[] (mm/s) | 120 | 700 | P | c | 700 mm/s (S profile). |
| `filament_idle_travel_cooling_enabled` | B | bool[] | true | (mặc định mã) | F | c | BỎ SÓT, chỉ BS: tắt gia nhiệt không chạy rỗng có thể gây tơ (S mô tả mã). Không có trong profile. |
| `enable_pressure_advance` | B+O | bool[] | false | (mặc định mã) | F | c | Vô nghĩa với Bambu: dùng hiệu chuẩn tự động (S mô tả mã). |
| `ooze_prevention` | B+O | bool | false | (mặc định mã) | P | c | Chỉ cho đa đầu; không dùng. |

### 8.9 Bộ ghi đè đề xuất theo tình huống (8.x)

Cách dùng: gói `process` ghi vào `overrides` (dict `d.update(...)` trong `slice.py`); gói `filament` ghi vào `filament_overrides` (cũng đã có trong `slice.py`, dòng 284-285). Kiểu giá trị theo đúng profile hãng: khóa process dạng vector (tốc độ, gia tốc) là list chuỗi; khóa filament luôn là list chuỗi. S = có nguồn chính thức; P = đề xuất cần in thử (mọi số P chưa kiểm). Các bộ này CHỒNG được lên nhau, trừ xung đột khóa: ưu tiên bộ nói về hình học (small_parts, tall_thin) cho `brim_*` và tốc độ.


#### `support_easy`: Support dễ gỡ nhất (đánh đổi: mặt dưới thô hơn, có thể võng nhẹ)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `support_style` | `"tree_slim"` | P | gộp nhánh, ít điểm chạm |
| process | `support_top_z_distance` | `"0.25"` | P | khe Z lớn hơn 0.2 một bậc; wiki Bambu zh nói lớn = dễ gỡ |
| process | `support_bottom_z_distance` | `"0.25"` | P | như trên |
| process | `support_interface_top_layers` | `"1"` | P | wiki Orca: ít lớp = dễ gỡ |
| process | `support_interface_bottom_layers` | `"0"` | P | wiki Orca: 0 = dễ gỡ nhất |
| process | `support_interface_spacing` | `"0.5"` | S | giữ nguyên profile (thưa) |
| process | `support_interface_pattern` | `"concentric"` | P | wiki Orca: tróc nguyên mảng |
| process | `support_object_xy_distance` | `"0.4"` | P | tăng 0.05 so với 0.35 |
| process | `tree_support_tip_diameter` | `"0.6"` | P | mô tả mã: mũi mảnh = ít sẹo, dễ gỡ; mã 0.8 |
| process | `tree_support_branch_distance` | `"6"` | P | ít điểm chạm |
| process | `support_base_pattern_spacing` | `"3"` | P | thưa hơn 2.5 |
| filament | (không ghi đè) | | | BS 02.09 không có quạt interface (xem 8.7); không khóa filament nào cải thiện riêng tình huống này |

```json
{
  "process": {
    "support_style": "tree_slim",
    "support_top_z_distance": "0.25",
    "support_bottom_z_distance": "0.25",
    "support_interface_top_layers": "1",
    "support_interface_bottom_layers": "0",
    "support_interface_spacing": "0.5",
    "support_interface_pattern": "concentric",
    "support_object_xy_distance": "0.4",
    "tree_support_tip_diameter": "0.6",
    "tree_support_branch_distance": "6",
    "support_base_pattern_spacing": "3"
  },
  "filament": {}
}
```

#### `support_pretty`: Mặt tiếp xúc support đẹp nhất (đánh đổi: khó gỡ hơn, in lâu hơn)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `support_type` | `"normal(auto)"` | P | mặt nhô phẳng; tree để dưới dạng default nếu nhô tròn nhỏ |
| process | `support_style` | `"snug"` | P | mô tả mã: snug giảm sẹo, tiết kiệm nhựa |
| process | `support_on_build_plate_only` | `"1"` | P | hết sẹo trên mặt chi tiết |
| process | `support_top_z_distance` | `"0.2"` | S | profile; không đặt 0 với PETG cùng nhựa (wiki zh) |
| process | `support_interface_top_layers` | `"3"` | P | wiki Orca: nhiều lớp = mặt phẳng |
| process | `support_interface_spacing` | `"0"` | P | đặc; điều kiện của enable_support_ironing (S mã) |
| process | `enable_support_ironing` | `"1"` | P | ủi mặt interface; cần spacing 0 (S mã) |
| process | `support_interface_speed` | `["50"]` | P | chậm hơn 80 cho mặt mịn |
| process | `support_angle` | `"45"` | P | cắt chéo đường in mặt chi tiết |
| filament | `ironing_fan_speed` | `["30"]` | P | BS: khóa filament; mã nói hạ quạt khi ủi chống tắc |

```json
{
  "process": {
    "support_type": "normal(auto)",
    "support_style": "snug",
    "support_on_build_plate_only": "1",
    "support_top_z_distance": "0.2",
    "support_interface_top_layers": "3",
    "support_interface_spacing": "0",
    "enable_support_ironing": "1",
    "support_interface_speed": [
      "50"
    ],
    "support_angle": "45"
  },
  "filament": {
    "ironing_fan_speed": [
      "30"
    ]
  }
}
```

#### `brim_easy`: Brim bám đủ nhưng dễ gỡ, mép đẹp

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `brim_type` | `"outer_only"` | S | mô tả wiki Orca: dễ gỡ nhất; đã có trong slice.py |
| process | `brim_width` | `"4"` | P | 5 mm profile; 4 mm cho chân vừa |
| process | `brim_object_gap` | `"0.15"` | P | mô tả mã: khe lớn dễ gỡ; profile 0.1 |
| filament | (không ghi đè) | | | BS 02.09 không có quạt interface (xem 8.7); không khóa filament nào cải thiện riêng tình huống này |

```json
{
  "process": {
    "brim_type": "outer_only",
    "brim_width": "4",
    "brim_object_gap": "0.15"
  },
  "filament": {}
}
```

#### `surface_pretty`: Đỉnh và thành đẹp (đánh đổi: chậm hơn 1.5-2 lần)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `layer_height` | `"0.16"` | P | dựng sẵn bộ 0.16 trong profile hãng |
| process | `precise_outer_wall` | `"1"` | P | mô tả mã: tường ngoài chính xác, lớp đều |
| process | `outer_wall_speed` | `["120"]` | P | profile 200 |
| process | `outer_wall_acceleration` | `["3000"]` | P | profile 5000 |
| process | `top_surface_speed` | `["120"]` | P | profile 200 |
| process | `top_surface_acceleration` | `["1500"]` | P | profile 2000 |
| process | `top_solid_infill_flow_ratio` | `["0.98"]` | P | mô tả mã Orca: giảm nhẹ cho đỉnh nhẵn |
| process | `ironing_type` | `"topmost"` | P | chỉ cho đỉnh phẳng lớn; rủi ro heat creep (wiki Orca) |
| process | `seam_placement_away_from_overhangs` | `"1"` | P | chỉ BS |
| process | `override_filament_scarf_seam_setting` | `"1"` | S | bắt buộc để process điều khiển scarf (mô tả mã) |
| process | `seam_slope_type` | `"external"` | P | scarf cho chi tiết tròn trơn |
| process | `bridge_flow` | `"0.95"` | P | mô tả mã: giảm võng |
| filament | `cooling_slowdown_logic` | `["consistent_surface"]` | P | enum có trong mã; giữ tốc độ tường ngoài |
| filament | `no_slow_down_for_cooling_on_outwalls` | `["1"]` | P | mô tả mã: khỏi vân Z khi chậm theo layer-time |
| filament | `overhang_fan_speed` | `["70"]` | P | profile 50 |

```json
{
  "process": {
    "layer_height": "0.16",
    "precise_outer_wall": "1",
    "outer_wall_speed": [
      "120"
    ],
    "outer_wall_acceleration": [
      "3000"
    ],
    "top_surface_speed": [
      "120"
    ],
    "top_surface_acceleration": [
      "1500"
    ],
    "top_solid_infill_flow_ratio": [
      "0.98"
    ],
    "ironing_type": "topmost",
    "seam_placement_away_from_overhangs": "1",
    "override_filament_scarf_seam_setting": "1",
    "seam_slope_type": "external",
    "bridge_flow": "0.95"
  },
  "filament": {
    "cooling_slowdown_logic": [
      "consistent_surface"
    ],
    "no_slow_down_for_cooling_on_outwalls": [
      "1"
    ],
    "overhang_fan_speed": [
      "70"
    ]
  }
}
```

#### `petg_stringing`: Giảm sợi tơ PETG (đánh đổi: rủi ro tắc/bám lớp nếu hạ nhiệt quá)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `reduce_crossing_wall` | `"1"` | P | wiki Orca/mã: tránh vượt tường |
| process | `max_travel_detour_distance` | `"50%"` | P | giới hạn đường vòng; mô tả mã |
| filament | `nozzle_temperature` | `["240"]` | P | giảm 5 °C so với 245; dải hãng 230-270 (S profile) |
| filament | `filament_retraction_length` | `["0.6"]` | P | profile 0.4 (S); machine 0.8 |
| filament | `filament_wipe_distance` | `["2"]` | P | profile 1; machine 2 |
| filament | `filament_z_hop` | `["0.2"]` | P | machine 0.4; vết hop gây tơ |

```json
{
  "process": {
    "reduce_crossing_wall": "1",
    "max_travel_detour_distance": "50%"
  },
  "filament": {
    "nozzle_temperature": [
      "240"
    ],
    "filament_retraction_length": [
      "0.6"
    ],
    "filament_wipe_distance": [
      "2"
    ],
    "filament_z_hop": [
      "0.2"
    ]
  }
}
```

#### `small_parts`: Chi tiết nhỏ (<20x20 mm)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `wall_generator` | `"arachne"` | P | vách 0.4-0.84 mm |
| process | `small_perimeter_threshold` | `["6"]` | P | tường nhỏ chậm theo small_perimeter_speed (profile 50%) |
| process | `small_perimeter_speed` | `["50%"]` | S | giữ nguyên profile |
| process | `initial_layer_speed` | `["30"]` | P | profile 50 |
| process | `outer_wall_speed` | `["100"]` | P | profile 200 |
| process | `inner_wall_speed` | `["150"]` | P | profile 300 |
| process | `brim_type` | `"outer_only"` | S | đã có trong slice.py |
| process | `brim_width` | `"5"` | S | profile |
| process | `brim_object_gap` | `"0.1"` | S | profile |
| process | `only_one_wall_first_layer` | `"1"` | P | lớp đầu nhẹ |
| process | `reduce_crossing_wall` | `"1"` | P | ít vết |
| process | `detect_thin_wall` | `"1"` | P | vách 1 đường |
| filament | `slow_down_layer_time` | `["15"]` | P | profile 12; layer nhỏ nguội đủ |
| filament | `filament_max_volumetric_speed` | `["10"]` | P | profile 13 |

```json
{
  "process": {
    "wall_generator": "arachne",
    "small_perimeter_threshold": [
      "6"
    ],
    "small_perimeter_speed": [
      "50%"
    ],
    "initial_layer_speed": [
      "30"
    ],
    "outer_wall_speed": [
      "100"
    ],
    "inner_wall_speed": [
      "150"
    ],
    "brim_type": "outer_only",
    "brim_width": "5",
    "brim_object_gap": "0.1",
    "only_one_wall_first_layer": "1",
    "reduce_crossing_wall": "1",
    "detect_thin_wall": "1"
  },
  "filament": {
    "slow_down_layer_time": [
      "15"
    ],
    "filament_max_volumetric_speed": [
      "10"
    ]
  }
}
```

#### `tall_thin`: Chi tiết cao mảnh (aspect >= 2.5)

| Gói | Khóa | Giá trị | Mức | Lý do |
|---|---|---|---|---|
| process | `brim_type` | `"outer_only"` | S | slice.py |
| process | `brim_width` | `"8"` | P | mô tả mã: brim rộng hơn bám tốt hơn; số cần in thử |
| process | `brim_object_gap` | `"0.1"` | S | profile |
| process | `initial_layer_speed` | `["30"]` | P | profile 50 |
| process | `outer_wall_speed` | `["100"]` | P | giảm rung |
| process | `inner_wall_speed` | `["150"]` | P | giảm rung |
| process | `default_acceleration` | `["3000"]` | P | profile 6000 |
| process | `outer_wall_acceleration` | `["2000"]` | P | profile 5000 |
| process | `inner_wall_acceleration` | `["3000"]` | P | profile 0 (= mặc định) |
| process | `travel_acceleration` | `["5000"]` | P | profile 10000 |
| process | `enable_height_slowdown` | `["1"]` | P | TODO: xác nhận ngữ nghĩa slowdown_*_height |
| filament | (không ghi đè) | | | BS 02.09 không có quạt interface (xem 8.7); không khóa filament nào cải thiện riêng tình huống này |

```json
{
  "process": {
    "brim_type": "outer_only",
    "brim_width": "8",
    "brim_object_gap": "0.1",
    "initial_layer_speed": [
      "30"
    ],
    "outer_wall_speed": [
      "100"
    ],
    "inner_wall_speed": [
      "150"
    ],
    "default_acceleration": [
      "3000"
    ],
    "outer_wall_acceleration": [
      "2000"
    ],
    "inner_wall_acceleration": [
      "3000"
    ],
    "travel_acceleration": [
      "5000"
    ],
    "enable_height_slowdown": [
      "1"
    ]
  },
  "filament": {}
}
```
