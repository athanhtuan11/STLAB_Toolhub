# sesame-quadruped – in thử robot 4 chân Sesame

Nguồn: [dorianborian/sesame-robot](https://github.com/dorianborian/sesame-robot) @ `bb87021` (2026-11-08), Apache-2.0.
Tác giả đã in và chạy thật, nên dùng nguyên STL làm chuẩn thông số (không vẽ lại). Mục đích: thử cho mảng robotics quadruped ESP32.
Nghiên cứu: `docs/reports/research-scout-deep-dive-2026-11-09.md`.

## In (Bambu A1, Bambu PETG Basic, Textured PEI)
| Bàn | File | Thời gian | Nhựa | Ghi chú |
|---|---|---|---|---|
| p1-body | `print/plates/p1-body/p1-body.3mf` | 3 h 52 | 64,9 g | khung + nắp đáy + 8 khớp, không support; nắp đáy dựng đứng (cao 79 mm, dày 7 mm) → có brim |
| p2-top-cover | `print/plates/p2-top-cover/p2-top-cover.3mf` | 55 ph | 16,9 g | **cần tô support** trong Bambu Studio: vùng trần ~1182 mm² ở z 30,6 (tác giả cũng dùng support) |

- STL gốc để theo hướng CAD; `print/stl/` đã xoay sang hướng in (chọn trong 24 hướng vuông góc, ít phần nhô ra nhất, giữ nguyên hình).
- Tác giả thiết kế cho PLA (infill 8–10 %, 2 wall, honeycomb). In PETG: khe lắp có thể khác chút – thử 1 khớp với servo trước.
- Kích thước đo từ STL: chi tiết lớn nhất 79,2 mm (vừa bàn 256 × 256 mm).

## Linh kiện (theo BOM gốc `hardware/bom/README.md`)
- 8 × servo MG90S **loại 180°** (loại 360° không chạy), mua dư 2.
- ESP32-S2 Mini (Lolin) + perfboard ~5 × 7 cm + header 3 chân × 8, buck 5 V/3 A.
- OLED SSD1306 0,96" I2C, công tắc KCD1, dây silicon 22 AWG + 30 AWG, co nhiệt.
- ~40 ốc M2 × 5 tự ren, 10 ốc M2.5 × 5 (bắt horn servo).
- Pin: Bambu Lab 14500 7,4 V 800 mAh (vừa hốc khung v121) + sạc đúng loại. Nguồn cần ≥ 5 V / 3 A.
- Giá ở VN: TODO.

## An toàn
- Pin Li-ion 2S 7,4 V: không cắt giắc gốc của pin (làm dây chuyển XT30/JST), đi qua công tắc + buck trước khi vào rail,
  co nhiệt mọi mối hàn, tháo pin khi hàn.
- 8 servo kéo dòng đỉnh lớn: buck phải đủ 3 A; servo kẹt sẽ nóng – tắt nguồn khi chân bị chặn.
