# elephant-backpack-clicker

Balô clicky + đầu voi (mẫu cộng đồng, zip `Elephant_stls.zip`: 5 đầu voi giống nhau + 3 balô giống nhau).
Tuan yêu cầu (2026-11-14): đổi chữ ELEPHANT → **STLAB**, một mẫu → **SMALL TREE**.

## Trạng thái
- 2026-11-14: 2 balô mới xong, cắt lớp WARN (support có sẵn từ thiết kế gốc), **chờ in thử**.

## File để duyệt / đo
- **SolidCraft (đo kích thước):** `blender/out/elephant-backpack.sc` – 4 component xếp hàng: balô gốc | STLAB | SMALL TREE | voi (mm).
- **Blender:** `blender/elephant-backpack.blend` (cùng 4 chi tiết, đơn vị mm).
- **Ảnh:** `blender/out/review/` – `0-overview.png` + ảnh cận tấm nhãn từng balô.
- Sinh lại: `blender -b -P blender/export_review.py -- <thư mục dự án>` rồi `python blender/export_cad.py blender/out`.

## Cách sửa
- Chữ gốc: chữ nổi 0,7 mm, đỉnh phẳng z 34,18 mm, trên tấm nhãn cong nhẹ (z 33,34–33,55 mm), tấm phẳng 30,9 × 10 mm.
- `blender/make_cutter.py`: khối cắt có đáy = mặt tấm nhãn nội suy từ lưới (−0,02 mm) → gọt sạch chữ cũ, tấm nhãn gần như nguyên.
- `blender/build_text.py`: boolean EXACT (lưới gốc có ~150 cạnh không kín ở z ≤ 31 mm, solver MANIFOLD bỏ qua), đắp chữ mới
  chân ngầm 0,4 mm, đỉnh z 34,18 mm như gốc.
  - STLAB: Arial Black, 26,7 × 5,5 mm.
  - SMALL TREE: Impact, 26,0 × 4,8 mm (nét ~0,9 mm; Arial Narrow nét ~0,6 mm quá mảnh).
- `blender/decimate.py`: giảm còn 150k tam giác/chi tiết cho Bambu Studio (sai lệch tối đa 0,018 mm, đo bằng `blender/deviation.py`).

## In
- `print/print.yaml`: p1-stlab (balô STLAB + voi), p2-small-tree (balô SMALL TREE + voi); PETG, 0,20 mm.
  Mỗi bàn ~1 h 10, ~30,7 g. Bàn in `.3mf`: `print/plates/<bàn>/`.
- **Cần tô support trong Bambu Studio**: balô – gờ nắp ở z 18,6 và 23,9 mm (rộng 52,8 mm); voi – vùng z 5,5 mm (~118 mm²).
- Cắt lớp có giới hạn RAM: `python tools/print/scripts/memjob.py 3 -- python tools/print/scripts/slice.py maker/elephant-backpack-clicker/print/print.yaml`.

## Dựng lại
1. Giải nén zip ra thư mục tạm; `python -I blender/make_cutter.py <obj_6_backpack.stl> blender/out/cutter.stl blender/out/info.json` (venv `tools/model-study`).
2. `blender -b --factory-startup -P blender/build_text.py -- <bag.stl> blender/out/cutter.stl blender/out/info.json print/stl-full/backpack-stlab.stl "STLAB" C:/Windows/Fonts/ariblk.ttf 5.5 28 <ảnh>`
   (SMALL TREE: `impact.ttf 4.8 29.5`).
3. `blender ... -P blender/decimate.py -- print/stl-full/<x>.stl print/stl/<x>.stl 150000`.
