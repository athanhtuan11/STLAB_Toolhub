# Spec: build nhanh – A + B + D (Claude, 2026-11-05, Tuan duyệt)

Hiện trạng đo được: `build_cam_d.py` ~3 ph = 3 lần tính lại cả timeline (run --save 57 s, eval, run --in để xuất STL);
gate build lại lần nữa vào thư mục tạm (~4 ph). 95 % thời gian là boolean của truck, nhất là trên Body.
Mục tiêu: sửa 1 thông số chỉ thuộc 1 chi tiết → build + gate **< 30 s**; không gì đổi → build **< 5 s**.

## A. Một lần tính cho mỗi chi tiết
- Mỗi chi tiết (Body, Bezel, U_frame, Base, Pin_cap, Coupon, Coupon_ring) + nhóm Ref (Ref_Stack, Ref_Cam) có **script
  riêng** `build/<label>.json`, chạy **1 lần** `solidcraft-cli run <json> --save build/<label>.sc --results --json-out build/<label>.result.json --quiet`
  và xuất STL trong **cùng lần chạy** (lệnh `file.export_stl` ở cuối script, `quality: fine`, hoặc `--out`).
- Hướng in: xoay STL bằng numpy (body X −90°, bezel X +90°) rồi tịnh tiến zmin = 0 → `stl/<label thường>.stl`.
  Không chạy lại `run --in` / `eval` để xuất.
- Hình học **không đổi**: giữ nguyên các lệnh dựng hiện có (chỉ tách theo chi tiết).

## B. Chỉ dựng lại chi tiết đổi + chạy song song
- Khóa cache mỗi chi tiết = sha256 của JSON lệnh chi tiết đó (sort_keys) + phiên bản CLI (`solidcraft-cli --version`).
  Lưu `build/<label>.key`. Khóa trùng và đủ file ra (.sc, .result.json, STL) → bỏ qua.
  Không cần bảng phụ thuộc tay: đổi params nào thì JSON chi tiết dùng nó tự đổi.
- Các chi tiết cần dựng chạy **song song** (subprocess, tối đa = số nhân CPU / 2, ít nhất 2).
- `CAMD_NO_CACHE=1` → dựng lại hết.
- In 1 dòng tóm tắt: `CAMD OK built=<n> cached=<m> <giây> s`.
- `build-report.json` (gộp): `{"bodies": {label: {volume_mm3, bbox:{min,max}, closed, shells}}, "built": [...], "cached": [...], "seconds": x}`
  lấy từ các `*.result.json` (shells = `kernel.shells`).
- **File lắp ráp `cam_d.sc` cho Tuan mở**: ghép từ các chi tiết **không chạy lại boolean** (vd. `component.insert_design`
  các `build/<label>.sc`, hoặc xuất STEP từng chi tiết trong lần chạy A rồi `file.insert_step`) – chỉ dựng lại khi có chi
  tiết đổi; mục tiêu < 10 s. Vị trí lắp ráp giữ như hiện tại. Nếu SolidCraft không cho ghép được → ESCALATE, đừng chạy
  lại cả timeline.
- `build/` không commit (thêm `.gitignore` trong `solidcraft/`: `build/`, `stl/`, `plates/`, `cam_d.json`, `cam_d.sc`).
  `cam_d.json` (cả timeline) không cần sinh nữa, trừ khi tiện để debug.

## D. Gate dùng kết quả build
Gate mới `tests/test_build.py` (Claude viết, KHÔNG sửa): chạy `python build_cam_d.py` tại chỗ (có cache), đọc
`build-report.json` + `stl/`; thêm test cache (chạy lại lần 2: `built=0`, < 10 s) và test `cam_d.sc` có đủ body.

## Không làm
Không đổi hình học, `params.json`, `tests/`, file ngoài `solidcraft/`. Không commit.
