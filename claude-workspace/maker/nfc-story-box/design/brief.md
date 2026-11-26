# Bước 0 – Giao diện: nfc-story-box (hộp kể chuyện Cú con)

Tuan 2026-11-26: "làm theo khuyến nghị" → hộp kể chuyện NFC trên bo **ESP32-A1S Audio Kit V2.2**, nhân vật **Cú con**
(cùng họ với Cú Bông `maker/english-teacher` và concept C của `maker/card-coding-robot`). **Thiết kế mới của STLab**: không chép
dáng, tên, nhân vật của sản phẩm thương mại nào (tránh kiểu khối vuông + tượng đặt trên nóc của Toniebox, hộp thẻ của Yoto).
Hệ thiết kế: `studio/design/DESIGN.md`. Chưa chọn dáng thì chưa làm cơ khí / firmware thật. CAD = SolidCraft.

## Brief
- **Sản phẩm:** bé đặt một **thẻ truyện** (đĩa in 3D có hình nổi + sticker NFC bên trong) lên chỗ đọc của Cú con → cú kể
  chuyện / hát bài của thẻ đó; nhấc thẻ ra → dừng; đặt lại → kể tiếp chỗ cũ. Không màn hình, không app, không mạng khi dùng.
- **Cho ai:** trẻ **3–6 tuổi** (mầm non), tự dùng một mình hoặc cạnh phụ huynh; góc đọc truyện ở lớp STLab / mầm non.
- **Học gì:** nghe truyện tiếng Việt + bản tiếng Anh cùng truyện (gắn giáo trình Seed `stlab/english-curriculum`), tự chọn – tự
  điều khiển (bé làm chủ), sau này thẻ "bé ghi âm" để bé kể lại. Nội dung: truyện tự soạn/TTS VieNeu hoặc nguồn có quyền dùng
  (`TODO` chọn nguồn truyện, không dùng sách có bản quyền).
- **Cảm giác:** ấm áp – mềm mại – "bạn cú biết kể chuyện". Đặt cạnh giường / góc đọc mà không giống máy móc.
- **Kích thước bao (Claude chốt, chỉnh khi đo bo thật):** ≤ 160 × 150 × 190 mm (rộng × sâu × cao). Đế rộng ≥ 130 mm để bé
  kéo/đẩy không lật. Vùng đặt thẻ ≥ Ø60 mm, phẳng hoặc lõm nhẹ (bé 3 tuổi đặt trúng không cần nhìn kỹ).
- **Thẻ truyện:** đĩa Ø50 × 5 mm, hình nổi + màu theo chủ đề, sticker NTAG213 ép giữa 2 lớp (dừng in ở lớp, nhét sticker – cách
  làm giống thẻ lệnh `card-coding-robot`). Kích thước không lọt ống thử chi tiết nhỏ (`TODO` tra TCVN 6238 / EN 71-1).
- **Điều khiển:** 3 nút to ≥ 25 mm đưa từ nút trên bo ra vỏ: **Chơi/Dừng**, **To hơn**, **Nhỏ hơn** (cánh cú hoặc bụng cú –
  mỗi concept tự đặt). Mắt cú = LED sáng dịu khi đang kể.
- **Linh kiện dự kiến (chốt ở giai đoạn 1):**
  - Bo ESP32-A1S Audio Kit V2.2: **82 × 73 mm** (datasheet Ai-Thinker; độ dày, lỗ vít, chiều cao linh kiện `TODO` đo bo thật).
    Chân đã dò: `tools/esp32-a1s/README.md`.
  - Âm thanh: file MP3 trên **thẻ microSD** của bo (SD 1-bit: CLK 14, CMD 15, D0 2) – truyện dài nên không để trong flash 4 MB.
  - Loa: 4 Ω 3 W Ø52 cao 26 mm (loại Tuan đã có, như `drum-pad`) – `TODO` xác nhận còn hàng.
  - Đọc NFC: **PN532 qua I2C chung bus codec (SCL 32, SDA 33)** – bo không còn chân SPI trống cho RC522. `TODO` kiểm địa chỉ
    PN532 không trùng ES8388 (0x10), khoảng đọc qua 2–3 mm PETG, kích thước module.
  - LED mắt: `TODO` chân GPIO trống (GPIO15 là SD CMD – không dùng được như `drum-pad`).
  - Nguồn: **USB 5 V adapter** (khuyến nghị v1 – không Li-ion trong đồ chơi trẻ 3–6). Đánh đổi: phải cắm điện, không mang đi.
- **Nhựa:** Bambu PETG Basic @BBL A1; hạn chế AMS → mỗi màu một part ráp lại. Không vẽ support vào STL.
- **Rủi ro bo:** chỉ có **1 bo A1S**, đang dùng cho `guitar-sai-thanh` và dự kiến `drum-pad` → `TODO` Tuan mua thêm bo hoặc dùng luân phiên.

## 3 hướng concept (Tuan chọn bằng ảnh)
| | A – Cú trên gốc cây | B – Cú ôm sách | C – Tổ cú |
|---|---|---|---|
| Dáng | Cú con thân trứng ngồi sau một "mặt gốc cây" thấp; thẻ đặt nằm lên mặt gốc cây phía trước | Cú đứng, hai cánh ôm cuốn sách trước ngực; thẻ đặt lên trang sách mở (mặt nghiêng ~15°) | Tổ tròn thấp, cú con ló đầu ở sau; thẻ đặt vào lòng tổ (lõm) |
| Hợp với | Bé 3 tuổi: đặt phẳng, đế rộng rất vững; loa hướng ra trước | Ý "đọc sách" rõ nhất; nút cánh tự nhiên | Lõm giữ thẻ không trượt; trọng tâm thấp nhất |
| Đổi lại | Chân đế dài → tốn nhựa, bàn in phải chia part | Mặt nghiêng → thẻ có thể trượt (cần gờ); cao → kém vững hơn | Cú nhỏ, ít "nhân vật"; tổ nhiều chi tiết vân → in lâu |

**Khuyến nghị: A – Cú trên gốc cây** (vững nhất cho bé 3 tuổi, vùng đọc phẳng lớn, loa và anten NFC tách xa nhau).

## An toàn trẻ 3–6 (ghi vào ASSEMBLY.md)
- Không chi tiết nhỏ tháo rời được; thẻ Ø50 mm; vít giấu dưới đáy; vỏ chỉ mở bằng tua vít.
- USB 5 V, không pin Li-ion ở v1. Trần âm lượng trong firmware (`TODO` đo dB ở 30 cm, chọn mức an toàn cho tai trẻ).
- Không mép sắc; dây USB đi ra sau, có chống giật dây. Nhiệt ampli + bo trong vỏ kín: `TODO` đo °C sau 1 giờ phát.

## Đầu ra bước 0 (ảnh – Tuan duyệt)
- `concepts/` – 3 concept: phối cảnh 3/4, nhìn hông, nhìn đỉnh; đặt trên bàn kèm bàn tay trẻ 4 tuổi + thẻ Ø50 làm thước.
- Mockup 4 thẻ truyện (Ø50) theo chủ đề.
- `cmf.png`, `contact-sheet.png` (~1200 px).

## Quyết định
<!-- Tuan chọn: ngày | concept | ghi chú → chép 1 dòng vào README "Lịch sử sửa" -->
2026-11-26 | **A – Cú trên gốc cây** | Tuan chọn + đổi bo sang **ESP32-S3 N16R8** (thay A1S) → RC522 SPI thay PN532, xem `hardware/BOM.md`.
