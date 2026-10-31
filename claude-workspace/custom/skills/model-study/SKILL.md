---
name: model-study
description: Reverse engineering model in 3D cong dong da chay duoc (MakerWorld/Printables .3mf/.stl/.step) de rut thong so lap ghep chinh xac (lo, chot, khe, boss, lo bac) vao kho fit-library, roi moi dua ra y tuong/ban chuan hon. Dung khi Tuan dua file model thanh pham, noi "nghien cuu file nay", "hoc cach tac gia lam", "lam ban chuan hon", va TRUOC KHI thiet ke bat ky chi tiet lap ghep nao (tra fit-library).
---

# Nghiên cứu model cộng đồng → kho thông số (Tuan 2026-10-27, nâng cấp 2026-10-30)

Mục tiêu: AI thiết kế sau này dùng **số đã đo/đã in thử**, không tự đoán khe/lỗ.
Báo cáo nguồn cộng đồng: `docs/reports/reverse-engineering-model-cong-dong.md`.
Công cụ ở `tools/model-study/` – chạy bằng `.venv\Scripts\python.exe` (uv; lần đầu `uv sync` trong thư mục đó).

## Ai làm gì
| Bước | Ai |
|---|---|
| 1–3 chạy script | phiên chính (lệnh ngắn) hoặc `check-runner` (khi nhiều file, log dài) |
| 4 gán nhãn giao diện + fit, quyết định khe | **Claude phiên chính** (hình học/khe – không giao model free) |
| 6 dựng bản cải tiến | executor qua `delegate.py` theo spec Claude viết (số lấy từ fit-library) |

## Các bước
1. **Đặt file**: `community/<nguon>-<tac-gia>-<ten>/` (git bỏ qua). License MakerWorld = dùng cá nhân, KHÔNG lên
   GitHub. Không sửa trong đó. Có STEP thì xin Tuan tải STEP (đo chính xác hơn STL).
   Model Tuan đưa = **sản phẩm hoàn thiện, đã in + chạy** (Tuan 2026-10-31) → khe đo được là khe đã chạy, không đề xuất
   in thử để "xác minh". Lấy luôn từ 3mf: tác giả/license (`3D/3dmodel.model` metadata), hướng dẫn lắp PDF + code trong
   `Auxiliaries/`, **máy + nhựa + `xy_hole_compensation`** trong `Metadata/project_settings.config` → ghi vào `print` của
   mục kho (khác nhựa STLab thì chỉ mối ép cần lưu ý).
2. **Tách + ảnh**: `uv run --with matplotlib python study_3mf.py <file.3mf|thu-muc-stl> _out/<ten>` → `parts/*.stl`, `parts.csv`,
   `contact-sheet.png` (duyệt bằng ảnh), `summary.md`.
3. **Đo**:
   - STL (mọi trục): `.venv\Scripts\python.exe measure_features.py _out/<ten>/parts/*.stl --json _out/<ten>/features.json`
     → lỗ/boss/cung (`arc`), `through`, lỗ bậc (`groups` counterbore), `rms_mm`, `confidence`.
   - STEP (chính xác ±0,001): `measure_step.py` qua freecadcmd.
   - `measure_holes.py` cũ (chỉ trục x/y/z) – chỉ để đối chiếu.
   - Lỗ không tròn (double-D, lục giác, then) → `arc` coverage < 300°: **cắt lát** `trimesh.intersections.mesh_plane`
     rồi đo cạnh phẳng (không cần networkx). STL có thể chứa nhiều thân chồng nhau (thể tích > hộp bao) → suy ghép
     cặp từ hình học, ghi rõ trong `note`.
   - Đọc hướng dẫn lắp PDF (`uv run --with pymupdf`, `sys.stdout.reconfigure(encoding='utf-8')`) để biết linh kiện,
     vít, kiểu lắp (ép/bấm/vít) trước khi gán nhãn.
4. **Gán nhãn + đưa vào kho** (Claude): xem contact sheet + features.json, xác định giao diện (vd `rotate-joint-5mm`,
   `screw-M2.5`, `servo-9g-mount-screw`, `bearing-608-seat`) và loại fit (`rotate|slide|press|clearance|self-tap`).
   Ghép cặp lỗ–chốt để tính khe. Thêm bằng
   `fit_lib.add_from_features(...)` (tự ghi nguồn + method `stl-fit`) hoặc sửa tay `fit-library/fits.json`, rồi
   `python fit-library/fit_lib.py check`. Confidence < 0,7 hoặc rms lớn → ghi `note`, không dùng làm mặc định.
5. **Ghi chú nghiên cứu**: `docs/research-notes/<ten>-fits.md` (giao `doc-writer`, đưa gạch đầu dòng số đo).
5b. **Rút mẫu thiết kế vào skill**: cách làm hay (cơ cấu, kiểu lắp, kiểu in) → thêm gạch đầu dòng vào mục
   "Mẫu thiết kế đã chạy" của skill `robotics-cad` (kèm số + nguồn). Không có bước này thì lần thiết kế sau không dùng tới.
6. **Thiết kế bản chuẩn hơn**: trước khi chọn bất kỳ khe/lỗ nào → `fit_lib.py recommend <interface>`.
   - `basis: verified` (STLab in thử A1 + PETG) → dùng luôn.
   - `basis: community` (sản phẩm đã chạy) → dùng làm mặc định, ghi nguồn trong spec. Khác nhựa (PLA→PETG) thì mối ép
     in 1 chi tiết trước; STLab in thật xong → thêm mục `verified: true`, `method: print-test`.
   - Không có trong kho → `TODO`, hỏi Tuan / in thử; **không bịa số**.
   - Áp dụng thêm luật [khe lắp ghép – co ngót] (memory) và support/brim của Tuan.

## Không làm
- Không đưa file/ảnh model cộng đồng lên git. Ảnh render trong `maker/` cũng không commit.
- Model free (Codex/agy/…) không tự quyết khe, kích thước lắp ghép.
