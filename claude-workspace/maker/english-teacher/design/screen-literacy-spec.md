# Màn tương tác chữ viết – Cú Bông (đề xuất 2026-11-28, CHỜ DUYỆT ẢNH)

Ảnh duyệt: `contact-sheet-literacy.png` (6 màn, mockup 320 × 240). Dựng lại: `python make_screen_literacy.py`.
Nghiên cứu: `docs/research-notes/education/screen-literacy-cu-bong.md` (claude-workspace).

## Nguyên tắc (từ nghiên cứu)
- Màn **phụ trợ** cho lời cô, không thay lời cô. Cô vẫn dạy bằng giọng. Phụ huynh ngồi cạnh (xem cùng).
- **Hình + chữ, 1 từ mới mỗi lần.** Chữ thường, to, chữ cái đầu tô cam. Trẻ mầm non nhận từ chủ yếu qua hình (Ehri).
- **Chỉ tương tác gắn mục tiêu học**: chạm để nghe lại, chọn hình theo lời cô, chạm chữ cái nghe âm. **Không** hotspot trang trí,
  game phụ, hiệu ứng ồn ào (Takacs 2015; Hirsh-Pasek 2015).
- **Không tô chữ/viết** trên màn: cảm ứng điện trở kém chính xác + bé 2–3 tuổi chưa hợp (TODO nguồn).
- Thẻ tự về đôi mắt sau **8 s** không chạm. Tổng thời gian màn thuộc buổi học hiện có (không thêm buổi mới).

## Các màn
| Màn | Tuổi | Khi nào | Bé làm | Cô AI |
|---|---|---|---|---|
| A. Thẻ từ | 2–5 | cô nói 1 từ của bài (từ mới/ôn) | nhìn; chạm thẻ | đọc lại từ chậm; gạch chân vàng chạy theo tiếng |
| B. Chọn 1 trong 2 | 3–5 (2–3: tùy) | cô hỏi "Where is the cat?" | chạm thẻ to (144 × 180 px) | đúng: khen, mắt cười, viền xanh; sai: thẻ rung nhẹ, gợi ý lại |
| C. Chữ cái đầu | 4–5 | sau khi bé nói đúng từ 2 lần | chạm chữ "c" | "c says /k/ … cat" |
| D. Sticker cuối buổi | 2–5 | cô chào tạm biệt | chạm từng sticker | đọc lại từ đó |
| Mắt (đã có) | – | trò chuyện bình thường | – | – |

Mắt cú thu nhỏ ở dải trên mọi màn (cú vẫn "sống", đổi màu theo trạng thái Nghe/Nói/Khen).

## Luồng kỹ thuật (đề xuất)
1. **Máy chủ → bo:** cầu nối đã biết từ của buổi (new/review trong `lessons-seed`). Khi lời cô (transcript) chứa 1 từ đó → gửi MCP
   `tools/call self.screen.show_word {word, pic, mode}` (kênh `mcp_call` đã có trong `bridge.py`). Màn B/C: thêm tool Gemini
   `ask_pick(target, other)` / `first_letter(word)` để cô chủ động mở màn đúng lúc hỏi.
2. **Bo → máy chủ:** chạm thẻ → bo gửi thông báo MCP `stlab/touch {screen, word, choice}` → cầu nối chèn vào Gemini 1 câu ngắn
   ("Bé vừa chạm chữ cat – đọc lại chậm") hoặc chấm đúng/sai cho màn B.
3. **Bo vẽ:** lớp `OwlEyesDisplay` thêm lớp "thẻ" (LVGL), mắt thu nhỏ khi thẻ hiện. Hình từ phân vùng assets (8 MB, đang dùng 320 KB).

## Tài nguyên cần
- **Hình:** 256 từ mới trong Seed 1–3 (đếm từ `lessons-seed/ROADMAP.md`). Bộ hình giấy phép mở: **OpenMoji (CC BY-SA 4.0)** hoặc
  **Twemoji (CC BY 4.0)**, 96 × 96 RGB565 ≈ 18 KB/hình → ~4,6 MB vừa phân vùng assets. Từ không có emoji (sầu riêng, mít, đu đủ…,
  từ trừu tượng "please") → TODO: vẽ riêng hoặc chỉ hiện chữ. Ghi license vào `docs/COMMUNITY.md` khi chọn.
- **Phông:** chữ "a"/"g" 1 tầng cho bé mới đọc → **Andika (SIL OFL)** cỡ 56 px + 120 px (chỉ a–z, A–Z), chuyển bằng `lv_font_conv`.
  Mockup dùng Comic Sans + emoji Windows **chỉ để minh họa**, không đưa vào firmware.

## Câu hỏi chờ Tuan
1. Duyệt 6 màn trong `contact-sheet-literacy.png`? Bỏ/sửa màn nào?
2. Màn B (chọn 1 trong 2) cho cả bé 2–3 tuổi hay chỉ 3–5?
3. Bộ hình: OpenMoji (nét vẽ tay, cần ghi BY-SA) hay Twemoji (phẳng, giống mockup)?
4. Chữ thường hết (khuyến nghị) hay thêm chữ hoa cho tên riêng (Mummy, Daddy)?
