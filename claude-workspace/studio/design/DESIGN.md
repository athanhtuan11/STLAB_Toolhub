# STLab – hệ thiết kế dùng chung

Áp dụng cho Toolhub (web), workbench STLab trong FreeCAD, trang web điều khiển ESP32 và ảnh/mockup ở bước 0
"Giao diện" của mọi dự án (Tuan 2026-10-24). Nghiên cứu: `docs/design-first-research.md`.

**Nguồn duy nhất:** `tokens.json` (thư mục này). Sửa màu ở đó, rồi chạy `python studio/design/build_tokens.py`. Script sinh
`toolhub/static/tokens.css` và **kiểm tương phản** (lỗi → exit 1). Workbench đọc thẳng `tokens.json`, icon sinh lại bằng
`python tools/robotics-cad/workbench/make_icons.py`. **Không đặt mã hex trong code giao diện** (trừ file sinh và lớp phủ 3D).

## Chủ thể → lựa chọn
STLab là trung tâm STEAM ở Đức Trọng, Lâm Đồng: cao nguyên, rừng thông, sương sớm. Học sinh làm robot in 3D.
Người dùng là Tuan, giáo viên và học sinh, nên giao diện phải đọc nhanh, rõ việc cần làm, dùng được trên điện thoại.

| Vai | Sáng | Tối | Lý do |
|---|---|---|---|
| Nền "sương" | `#ECF1EF` | `#101714` | xanh xám nhạt của sương cao nguyên, dịu mắt hơn xám trung tính |
| Màu chính "thông" | `#1E5A45` | `#6CC19B` | rừng thông Lâm Đồng; nút chính, tab đang mở, liên kết |
| Điểm nhấn "sợi nhựa" | `#E8B33A` | `#F0C152` | cuộn nhựa in 3D; **chỉ một chỗ**: dấu nhận diện cạnh chữ STLAB (và highlight hiếm) |
| Chữ | `#16231D` | `#E3EBE7` | mực xanh đen, không dùng đen thuần |
| PASS / WARN / FAIL | `#257A45` / `#9A6400` / `#B3341F` | `#5CCB86` / `#E8B33A` / `#F07A63` | đạt ≥ 4,5:1 trên nền thẻ |

Màu theo **bước quy trình** (icon workbench, nhãn bước): 0 Giao diện `#C2577E` · 1 Dự án `#3F6E9E` · 2 Linh kiện `#6E5BA6`
· 3 Thiết kế `#1E5A45` · 4 Kiểm tra `#B3341F` · 5 In 3D `#B87A00` · 6 Tài liệu `#4F6B3A` (chữ trắng ≥ 3:1).

**Chữ:** Be Vietnam Pro (font do người Việt làm cho tiếng Việt, OFL-1.1), lưu sẵn trong `toolhub/static/fonts/`, không
cần internet. 400 thân, 600 nhấn, 700 tiêu đề. Workbench dùng font của FreeCAD (Qt), không ép font.

## Nguyên tắc
1. **Một điểm nhấn.** Vàng sợi nhựa chỉ ở dấu nhận diện; mọi thứ khác dùng xanh thông và trung tính.
2. **Chỉ hiện điều cần làm.** Trang chính chỉ có lỗi cần chú ý, việc đang làm, nút chính. Thông tin hệ thống để vào "Thêm".
3. **Trạng thái bằng chữ và màu**, không chỉ bằng màu (người mù màu vẫn đọc được "WARN").
4. **Viết bằng ngôn ngữ người dùng:** nút ghi đúng việc nó làm ("Chuẩn bị in", "Mở"), lỗi nói rõ cách sửa.
5. **Toolhub luôn tối** (Tuan 2026-10-27) – chọn bằng `toolhub_theme` trong `tokens.json` (`dark` | `light` | `auto`
   theo hệ thống). Bộ màu sáng vẫn giữ cho workbench FreeCAD và trang ESP32. Không có nút đổi theme trên trang.

## Checklist "đẹp" kiểm được (bước 0 và mỗi lần sửa giao diện)
- [ ] `build_tokens.py` exit 0 (tương phản đạt) · không có hex mới trong code giao diện (`grep`).
- [ ] Ảnh chụp ở 1280 px và ≤ 520 px (điện thoại): không tràn ngang, nút ≥ 44 px trên trang ESP32/điện thoại.
- [ ] Sáng và tối đều đọc được (chụp cả hai).
- [ ] Bàn phím: thấy viền focus.
- [ ] Sản phẩm (dáng): nhìn bóng đen vẫn nhận ra; ≤ 3 màu nhựa, mỗi chi tiết 1 màu, chỉ màu cuộn đang có; concept chọn
      vẫn qua `printability.py`.

## Ở từng nơi
- **Toolhub:** `base.html` nạp `fonts.css` → `tokens.css` → `style.css`; `style.css` chỉ dùng `var(--…)`.
- **Workbench:** `stlab_wb/core.py` `tokens()`; `dialogs.COLOR` chọn bộ sáng/tối theo màu nền Qt của FreeCAD.
- **ESP32 (sắp tới):** chép biến từ `tokens.css` vào trang nhúng (không tải font, dùng `system-ui`), nút ≥ 44 px.
