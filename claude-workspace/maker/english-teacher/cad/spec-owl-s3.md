# spec-owl-s3 – vỏ Cú Bông bản ESP32-S3 (1 loa), Blender bpy

Claude viết 2026-11-12. Tuan: "thiết kế lại Cú Bông để tôi in thử" sau khi chốt bản S3 1 loa 4 Ω 3 W.
Dáng giữ nguyên (Cú Bông A, đã duyệt) – chỉ đổi bố trí bên trong + lỗ.

## Cách làm
- Chép `build_owl.py` → **`build_owl_s3.py`** (giữ nguyên bản A1S), xuất ra **`out-s3/`** (STL đúng hướng in + `asm/` vị trí lắp + `owl-params.json` + 2 ảnh).
- Chép tiếp kiểu `print/print.yaml` → **`print/print-s3.yaml`**, `plates_dir: plates-s3`, STL ở `print/stl-s3/`, xếp bàn THEO MÀU như cũ
  (hạn chế AMS), cắt lớp `python ../../tools/print/scripts/slice.py print/print-s3.yaml` → mọi bàn PASS, **không support**
  (vẽ lại hình cho tự đứng: vát ≤ 45°, không mái treo).
- `export_cad.py` (nếu chạy được với out-s3) → `.sc` lắp ráp để Tuan đo (memory: CAD mở đo được = SolidCraft). Không chạy được thì ghi lý do.

## Thay đổi (Claude chốt, không đổi số)
1. **Loa: 1 cái ở BỤNG** – Ø52 × 26, mép trước 5 mm, thân sau mép < Ø39. Tâm loa x = 0, mặt loa hướng −Y (ra trước), z khoảng
   45–55 (giữa bụng). Dùng lại **nguyên cơ cấu** vành loa + ron EVA + vòng ép ngàm xoay 3 chốt của bản A1S (mọi số trong
   `speaker_clamp`), chỉ đổi trục x → y. Lưới loa Ø56 lỗ Ø2,8 bước 5,6 nằm trên vành loa (`speaker-bezel.stl`), vành lắp vào lỗ
   bụng (`belly.stl` khoét lỗ vừa vành, khe trượt 0,2–0,3). `speaker_pocket_d` 52,6.
   **Bỏ** 2 lỗ loa ở 2 sườn: sườn kín, giữ dáng cánh. Không còn file `speaker-bezel-L/R`, `speaker-ring-L/R`.
2. **Mic INMP441 ở TRÁN**: 3 lỗ Ø2,0 trên trán (giữa 2 mắt, trên mỏ), tâm cụm mic z ≥ 100, cách tâm loa ≥ 60 mm.
   Sau lỗ: ô giữ module ≥ 17 × 17 × 8 (PCB tròn Ø14–15 hoặc vuông 14 × 14 – lỗ âm của INMP441 xuyên PCB, mặt chưa xác định),
   **ron EVA vòng** dày ≥ 1,0 (ghi `mic.gasket_t`) ép giữa mặt module và vách trán quanh vùng lỗ; chi tiết in **`mic-clamp.stl`**
   (kẹp/nắp ép module vào ron, cài bằng ngàm hoặc 2 vấu trượt, không vít ngoài) – có rãnh cho 6 dây header đi ra sau.
   Vùng lỗ trán phủ ±4 mm quanh tâm (vị trí lỗ âm module lệch được).
3. **Bo ESP32-S3**: thư viện `tools/parts-library` DevKitC-1 = 70,2 × 25,4 × 13,2 (kèm anten); bo của Tuan là clone N16R8
   2 cổng USB-C, chưa có số → khối giữ chỗ **72 × 29 × 16** (`pcb_box`), dựng đứng ở nửa sau, **đầu USB xuống dưới**, ray rãnh
   giữ cạnh PCB rộng (rãnh 2,4 cho PCB 1,6 + chừa lệch rộng 25,4–28,6) + 1 tai chặn trên; cổng USB nằm ngay trên khe cáp.
4. **Khe cáp USB-C** ở chân LƯNG: ≥ 14 × 9 (đầu cắm USB-C) – giữ khe cũ 40 × 12 cũng được (`cable_slot: {side: back, w, h}`).
5. **Ampli MAX98357A**: khay **`amp-tray.stl`** (hoặc khay liền thân) giữ module ≥ 22 × 22 × 10 (`amp_box`, Adafruit 19,4 × 17,8 + cầu
   đấu), đặt sau loa trong bụng, tâm cách tâm loa ≤ 70 mm; có lỗ thoáng (ampli ấm khi to).
6. **3 switch MX** (giữ số fit-library catpaw như bản A1S): `talk` gpio **1** ở đỉnh đầu dưới nắp nút Ø50 (như cũ);
   `vol_up` gpio **40**, `vol_down` gpio **39** ở lưng – giữ nguyên cụm vol-pod v2 (vít M2.5 bắt từ trong, mặt cong theo vỏ).
7. Giữ: mắt (eye-ring, eye-diffuser – LED chưa có firmware, giữ chỗ), mỏ, tấm đế, khe nhiệt, chốt ghép 2 nửa, nắp nút không rút
   ra được (bé < 3 tuổi), vít giấu. Bỏ ray giữ bo Audio Kit 82 × 73.
8. `owl-params.json` thêm: `variant: "s3"`, `speakers` (1 mục `{center, axis: "y"}`), `pcb_center/pcb_box`, `amp_center/amp_box`,
   `mic: {center, box, holes, gasket_t}`, `cable_slot`, `mx.keys` GPIO mới; giữ các khóa cũ gate dùng (wall, speaker_clamp…).
9. Ảnh: `out-s3/owl-preview.png` (3/4 trước thấy loa bụng + lỗ mic trán), `out-s3/owl-exploded.png` (thấy bo S3, ampli, mic, loa).

## Gate (Claude viết, KHÔNG sửa)
`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P gate_owl_s3.py -- out-s3` → `PASS gate_owl_s3`
(gate đòi cả `print/plates-s3/print-report.json` mọi bàn PASS).

## Được sửa
`cad/build_owl_s3.py`, `cad/out-s3/**`, `print/print-s3.yaml`, `print/stl-s3/**`, `print/plates-s3/**`, `cad/README.md` (thêm mục S3).

## Không làm
- Không sửa `build_owl.py`, `gate_owl.py`, `out/`, `print/print.yaml`, `print/plates/` (bản A1S giữ nguyên).
- Không đổi số khe/vít/loa/switch ngoài spec; số nào thiếu nguồn → để rộng + ghi `TODO` trong README, không đoán chặt.
- Không commit.
