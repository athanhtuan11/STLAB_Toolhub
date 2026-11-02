# Nghiên cứu clicker / nút nhấn fidget (2026-11-02)

Codex tra web 2026-11-02; Claude chưa mở từng link. Số trên Printables là các con số hiển thị ở trang tìm kiếm, chưa rõ cột nào là lượt tải/like – không dùng để xếp hạng chính xác. Bối cảnh: tiếp nối docs/reports/print-products-market-research.md mục 10 (clicker hạt cà phê/atiso).

## 1. Mẫu cụ thể đang có

Cột "số hiển thị" giữ nguyên chuỗi số từ trang tìm kiếm, chưa rõ ý nghĩa từng cột.

| Mẫu | Tác giả / nền tảng | Số hiển thị | Cơ chế / phần cứng | Link |
|---|---|---|---|---|
| Fidget Clicker – Easy To Print! | M4trix / Printables | 90 · 2.744 · 8 · 5.309 | in liền, < 6 g nhựa | https://www.printables.com/model/1045067-fidget-clicker-easy-to-print |
| Print-In-Place Fidget Clicker | Frankee / Printables | 12,1K · 4,2 · 118,7K · 22 | in liền | https://www.printables.com/search/models?q=tag%3Aclicker |
| Skull Key Switch Fidget Toy | decay3d / Printables | 2,7K · 4,9 · 13,2K · 30 | switch bàn phím | (cùng link tìm kiếm) |
| Mechanical Switch Fidget Click | kriswillcode / Printables | 598 · 4,6 · 2K · 23 | switch bàn phím | — |
| Cute Cat Paw Clicker – No Keyboard Switch Required | voxo3d / Printables | 820 · 4,6 · 9,1K · 22 | không cần switch | — |
| Satisfying Clicking Fidget Button | ThreeD-Michael / Printables | 366 · 4,9 · 1,8K · 14 | TODO | — |
| Fidget Toy – Clicker Coin (V1, V2) | Matt Tranchina / Printables | 2,4K · 4,5 · 14,1K · 12 (V1); 806 · 4,7 · 3,7K · 6 (V2) | TODO | — |
| Clicky Rotate Counter | BaGooN / Printables | 3,2K · 4,9 · 9,4K · 16 | xoay đếm | — |
| Figet Clicking Wheel | Giwi / Printables | 787 · 4,9 · 6,9K · 22 | bánh xe | — |
| Fidget Clicker Keychain | xik / Printables | 242 · 5,0 · 3,3K · 20 | bản remix thêm lò xo, in < 20 phút | https://www.printables.com/model/1734139-clicker |
| Gen 1 Starters – Keyboard clickers | Agustin Arroyo / Printables | 571 · 4,9 · 1,9K · 12 | switch bàn phím | — |
| Clicker Fidget Keychain | Tom S / Printables | 227 · 4,5 · 3,8K · 17 | TODO | — |
| Force-Feedback Clicker Spinner | Zendama / Printables | 261 · 5,0 · 771 · 19 | xoay + click | — |
| 2x3 Fidget Clicker + Keychain | MakerWorld (qua 3dgo.app) | TODO | 6 nút kiểu cơ | https://3dgo.app/models/makerworld/1828269 |
| ABC Clicker Fidget Keychain | MakerWorld | TODO | cần switch | https://makerworld.com/en/models/2179835-abc-clicker-fidget-keychain |
| Keyboard Clicker Fidget Spinner | MakerWorld | TODO | phím MX + 2 bạc đạn 608ZZ, ép | https://makerworld.com/en/models/2523859-keyboard-clicker-fidget-spinner |

Chủ đề lặp lại trên Printables: bánh macaron trái tim, bí ngô, Minecraft, chân mèo. Nhân vật/hình dễ thương là nét chung.

## 2. Phân loại cơ chế

| Loại | Tạo tiếng click thế nào | Phần cứng | Hợp STLab? |
|---|---|---|---|
| Switch bàn phím (keycap in + switch trong thân in) | Tiếng/cảm giác do switch (clicky/tactile/linear) | Switch; ép vào. Ví dụ Etsy: https://www.etsy.com/listing/4332194667/3d-printed-animal-keyboard-fidget | Có, đề xuất #1 và #3 |
| In liền đàn hồi / snap-through | Thân in uốn rồi bật lại | Không | Có, đề xuất #2 |
| Lò xo / bánh cóc | TODO | Lò xo, bánh cóc | Có, cơ cấu khó hơn (đề xuất #4) |
| Nam châm (haptic slider) | Lực hút/đẩy. Reddit người dùng thích (giai thoại): https://www.reddit.com/r/fidgettoys/comments/1p92xgy/okay_i_found_my_goto/ | Nam châm | Không cho đồ trẻ em |
| Bút click / click-clack | TODO | TODO | TODO |
| Khác | Bánh xe, đếm xoay, toggle, infinity cube | TODO | TODO |

Kết luận nguồn: cả switch và in liền đều phổ biến. Chưa có số đo chặt để nói loại nào hot nhất.

## 3. Vật liệu

- Hướng dẫn snap-fit chung ưu tiên PETG (dẻo, ít nứt), PLA giòn: https://help.makelab.com/help/article/snap-fit-and-living-hinge-design-for-3d-printing
- Một hướng dẫn gợi ý PLA cho clicker cứng, PETG chỗ cần uốn: https://www.4additive.com/en/functional-3d-printed-fidget-toys-guide/
- PETG có làm tiếng click "mềm/đục" hơn không: TODO, phải in thử.

## 4. Giá bán / phần cứng

- Etsy: clicker switch 2,50 USD https://www.etsy.com/listing/4501279263/3d-printed-mechanical-keyboard-fidget
- Etsy: thú ảo 5,90 USD https://www.etsy.com/listing/4319777409/virtual-pet-fidget-clicker-custom
- Etsy: hình thú 14,99+ USD (link mục 2)
- Etsy: file số bộ 4 mẫu 6,99 USD https://www.etsy.com/listing/4486600993/retro-inspired-fidget-clicker-set-3d
- Giá switch lẻ và nam châm 6×3 mm ở VN: TODO (Tuan tự xem Shopee).

## 5. An toàn

**CẢNH BÁO:**

- Nam châm nhỏ: nuốt ≥ 2 viên gây tổn thương ruột nghiêm trọng. Tránh cho trẻ nhỏ: https://www.cpsc.gov/safety-education/safety-guides/toys/ingested-magnets-can-cause-serious-intestinal-injuries
- Switch, lò xo, keycap tháo được là chi tiết nhỏ. Người bán Etsy ghi "không hợp trẻ nhỏ".

## 6. Đề xuất cho STLab

| # | Mẫu | Cơ chế | Lý do | Rủi ro |
|---|---|---|---|---|
| 1 ★ | Clicker switch hình hạt cà phê / bông atiso / đầu dê Tết (keycap in tạo hình, thân móc khóa) | Switch bàn phím | Tiếng click chắc chắn, thiết kế dễ; nét địa phương nằm ở keycap; đổi keycap = biến thể nhanh; hợp bán quà | Cần mua switch (giá TODO); chi tiết nhỏ, ghi "trên 8 tuổi" (độ tuổi TODO theo QCVN) |
| 2 ★ | Clicker in liền không phần cứng (bản "Easy" của STLab) | Snap-through | Không phần cứng, giá vốn thấp, dân MakerWorld thích; đăng cộng đồng | PETG có thể click yếu, in mẫu thử 3 độ dày lưỡi gà trước |
| 3 | Bộ 2×3 nút "bàn phím mini" với keycap chữ STLab/tên học sinh | Switch | Cá nhân hóa tên (bán được giá hơn) | Nhiều switch, giá vốn cao |
| 4 | Clicker xoay đếm (đếm số lần) cho học sinh | Bánh cóc in liền | Gắn STEAM (đếm, tỉ số) | Cơ cấu khó hơn |

Không làm loại nam châm cho đồ trẻ em.

**Khuyến nghị:** làm #1 trước (chắc ăn, 1 mẫu thân + nhiều keycap); #2 làm song song bằng mẫu thử. Dùng Blender (không phải robotics). Mẫu thiết kế mới, không chép mẫu trên.

## 7. Nguồn

- https://www.printables.com/model/1045067-fidget-clicker-easy-to-print
- https://www.printables.com/search/models?q=tag%3Aclicker
- https://www.printables.com/model/1734139-clicker
- https://3dgo.app/models/makerworld/1828269
- https://makerworld.com/en/models/2179835-abc-clicker-fidget-keychain
- https://makerworld.com/en/models/2523859-keyboard-clicker-fidget-spinner
- https://www.etsy.com/listing/4332194667/3d-printed-animal-keyboard-fidget
- https://www.reddit.com/r/fidgettoys/comments/1p92xgy/okay_i_found_my_goto/
- https://help.makelab.com/help/article/snap-fit-and-living-hinge-design-for-3d-printing
- https://www.4additive.com/en/functional-3d-printed-fidget-toys-guide/
- https://www.etsy.com/listing/4501279263/3d-printed-mechanical-keyboard-fidget
- https://www.etsy.com/listing/4319777409/virtual-pet-fidget-clicker-custom
- https://www.etsy.com/listing/4486600993/retro-inspired-fidget-clicker-set-3d
- https://www.cpsc.gov/safety-education/safety-guides/toys/ingested-magnets-can-cause-serious-intestinal-injuries
