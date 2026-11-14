# elephant-backpack-clicker

Balô clicky + đầu voi (mẫu MakerWorld). Tuan yêu cầu 2026-11-14: đổi chữ ELEPHANT → **STLAB**, một mẫu → **SMALL TREE**,
**giữ nguyên màu** của tác giả.

## Trạng thái

- 2026-11-14: 3mf có màu xong (2 balô STLAB + 1 SMALL TREE + 5 voi), Bambu Studio CLI cắt lớp OK, **chờ in thử**.
- Bản đơn sắc cắt từ STL (gọt chữ bằng boolean) đã thay, nằm trong `backup/20261114-elephant-mono-thay-bang-3mf-mau/`.

## File để in / duyệt / đo (chỉ trên máy, không lên git)

- **In:** `print/color/elephant-backpack-color.3mf`, mở bằng Bambu Studio. Có 2 bàn: bàn 1 là 3 balô, bàn 2 là 5 voi.
- **Đo (SolidCraft):** `blender/out/color/elephant-backpack-color.sc`. Mỗi balô (gốc | STLAB | SMALL TREE) tách thành 2 component trắng / xám.
- **Blender:** `blender/elephant-backpack-color.blend`, mỗi balô 1 collection, mỗi chi tiết giữ màu.
- **Ảnh:** `blender/out/review-color/`, gồm `0-overview.png`, ảnh mặt trước và ảnh cận tấm nhãn của từng balô.
- Nguồn gốc: `community/makerworld-elephant-backpack-clicker/Elephant.3mf` (bản STL zip không có màu).

## Thông tin màu của mẫu gốc (`source/color-map.json`)

- 3 nhựa Bambu PLA Matte: slot 1 trắng `#FFFFFF`, slot 2 đen `#161616`, slot 3 xám `#9B9EA0`.
- Lớp 0,20 mm (voi 0,12 mm). Support dạng tree(manual): tác giả đã tô sẵn vùng support, phần này vẫn giữ.
- **Balô:** 34 chi tiết rời, màu gán theo chi tiết (mặc định xám, các chi tiết số 9, 10, 11, 16, 17, 19, 23, 25 màu trắng).
  - Tấm nhãn là chi tiết 16 (trắng). Chữ ELEPHANT gồm 8 chi tiết xám, id 26 và 34–40 (mỗi id một chữ cái).
- **Voi:** 1 lưới, màu tô theo từng tam giác (`paint_color`), giữ nguyên không sửa.

## Cách làm lại

1. `python -I source/read_3mf.py <3mf đã giải nén> source/color-map.json`: đọc chi tiết, màu và paint.
2. `python -I source/extract_parts.py <goc.3mf> source/parts 7,...,40`: tách chi tiết (tọa độ object balô).
3. `blender -b -P blender/make_text_part.py -- source/parts/part-16.stl source/text/text-stlab.stl "STLAB" C:/Windows/Fonts/ariblk.ttf 5.5 28`.
   SMALL TREE thì dùng `impact.ttf 4.8 29.5`. Mặt trước chữ phẳng y = −17,093 như chữ gốc. Mặt sau được trừ đi tấm nhãn nên ôm sát mặt cong, không lấn sang chi tiết trắng.
4. `python -I source/build_3mf.py <goc.3mf> print/color/elephant-backpack-color.3mf source/text/text-stlab.stl source/text/text-small-tree.stl`:
   mỗi balô bỏ 8 chi tiết chữ cũ, thêm 1 chi tiết chữ xám (slot 3). Object 41 và 43 thành STLAB, 42 thành SMALL TREE. Mục `<assemble>` (khung nhìn lắp ráp) bị bỏ.
5. `blender -b -P blender/render_color.py -- <thư mục dự án>` rồi `python blender/export_cad.py blender/out/color`: tạo ảnh, `.blend` và `.sc`.
6. Kiểm tra: `python tools/print/scripts/memjob.py 3 -- bambu-studio.exe --slice 0 --export-3mf x.3mf --outputdir print/color/sliced print/color/elephant-backpack-color.3mf`.

## Chữ mới

- STLAB: font Arial Black, 26,7 × 5,5 mm. SMALL TREE: font Impact, 26,0 × 4,8 mm. Cả hai nổi khoảng 0,67 mm, màu xám.
- Chữ gốc ELEPHANT: 30,8 × 4,36 mm. Tấm nhãn phẳng: 30,9 × 10 mm.

## In (kết quả cắt lớp Bambu CLI, profile tác giả)

| Bàn | Gồm | Thời gian | Đổi nhựa | Nhựa (gồm xả + tháp) |
|---|---|---|---|---|
| 1 | 2 balô STLAB + 1 balô SMALL TREE | 6 h 10 | 119 lần | trắng 83,5 g + xám 38,7 g |
| 2 | 5 voi | 4 h 46 | 84 lần | trắng 12,6 g + đen 7,2 g + xám 41,7 g |

- Cần AMS (2–3 màu). Lượng xả và tháp prime tốn khoảng 40 g ở bàn 1.
- Profile tác giả dùng PLA Matte. Muốn đổi nhựa thì chọn lại trong Bambu Studio, màu theo slot giữ nguyên.
