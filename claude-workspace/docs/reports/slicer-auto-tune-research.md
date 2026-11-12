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
| Scarf seam | `seam_slope_type`, `scarf_angle_threshold`(155) | `none` | `external` cho chi tiết tròn trơn; in thử | P | PrintConfig BS; wiki Orca |
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
| Mặt trước/đẹp | Biết mặt chọn | `seam_position=back` hoặc aligned + scarf `external` nếu chi tiết tròn trơn | P |
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
