# servo-horn-sg90 – arm servo in 3D (khớp SG90 + dáng CyberBrick)

Tuan yêu cầu 2026-11-12. Trạng thái, file, kiểm: `README.md`.

## Quy ước riêng
- Nguồn duy nhất: `solidcraft/params.json` → `python solidcraft/build_horn.py` → `servo-horn.sc` + `stl/` + `build-report.json`.
  Cắt lớp: `tools/print/scripts/slice.py tools/parts-library/printables/servo-horn-sg90/solidcraft/print/print.yaml` (Python của FreeCAD).
- Khớp trục (`hub`, `bore`, `screw`) = số Print2Drive đã chạy trên A1 + PETG (fit-library `sg90-horn/*`). Không tự đổi;
  muốn chặt/lỏng hơn → in thử, ghi kết quả vào fit-library (`verified: true`).
- Dáng arm (`arms.*`: w0, k, tip_c, tip_r, holes) = số fit từ STEP CyberBrick (`cyberbrick-horn/*`). Giữ để lắp lẫn CyberBrick.
- Lỗi nhân SolidCraft đã gặp: trụ đầu arm tiếp tuyến cạnh → union lỗi (vẽ 1 biên dạng line + arc); trụ + côn đồng trục cắt rời →
  cut lỗi (gộp thành 1 biên dạng `solid.revolve`).
- Model cộng đồng (`community/makerworld-servo-arm-sg90/`) chỉ để đọc số, không đăng lại.
