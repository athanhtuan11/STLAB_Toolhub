# Bước 0 – Giao diện: block-coding-car

Tuan 2026-11-16: "dự án robotics áp dụng kit ESP32-S3 thực hiện nhiệm vụ tương tự ScratchJr, học sinh học trên máy tính nhưng
điều khiển được xe thực tế, tối ưu cho bé cấp 1 (học từ lớp 1)". Thiết kế mới của STLab – không chép icon/nhân vật/giao diện ScratchJr.
Hệ thiết kế: `studio/design/DESIGN.md`. Chưa chọn dáng + bố cục app thì chưa làm cơ khí, firmware, app thật.

## Brief
- **Sản phẩm:** xe nhỏ đi trên thảm ô vuông 150 × 150 mm. Bé lập trình bằng khối icon trên máy tính lab, xem xe ảo chạy thử,
  bấm **Chạy xe thật** → xe đi đúng chuỗi, khối đang chạy sáng lên trên màn hình.
- **Cho ai:** học sinh **lớp 1–3** (bắt đầu từ lớp 1, 6–7 tuổi, mới tập đọc), nhóm 2 bé / 1 máy + 1 xe, giáo viên STLab.
  Buổi 30 phút.
- **Cảm giác:** vui – chắc tay – "hiểu ngay không cần chữ".
- **Kích thước bao:** xe ≤ 120 × 120 × 100 mm (quay tại chỗ không lấn ô 150 mm). Thảm 6 × 6 ô = 900 × 900 mm.
- **Đế xe dùng chung với card-coding-robot** (2 × 28BYJ-48 + bánh, 4 × AA NiMH nằm phẳng sát đáy, bi đỡ). Phần trên (vỏ) khác.
- **Linh kiện:** ESP32-S3 N16R8 DevKit (`TODO` đo bo thật), 2 × 28BYJ-48 5 V + ULN2003, 2 WS2812 làm mắt (hướng mặt rõ),
  MAX98357A + loa nhỏ, nút **Dừng** đỏ ≥ 25 mm trên nóc, công tắc nguồn giấu. Số liệu điện: datasheet, chưa có ghi `TODO`.
- **Nhựa:** Bambu PETG Basic @BBL A1, hạn chế AMS → part đơn sắc ráp lại. Không vẽ support vào STL.

## Nguyên tắc app cho bé lớp 1
- Không cần đọc: khối icon ≥ 64 px, màu theo nhóm – **xanh dương** di chuyển, **vàng** điều khiển (bắt đầu/lặp/chờ),
  **tím** âm thanh/đèn, **đỏ** kết thúc. Giữ chuột lên khối → đọc tên tiếng Việt (TTS VieNeu).
- 1 dải lệnh ngang, ≤ 12 khối; kéo thả chuột/chạm. Nút DỪNG đỏ luôn hiện. Không tài khoản.
- Lưới ô ảo + xe ảo chạy giống xe thật (dạy được khi thiếu xe). Trạng thái kết nối xe bằng màu + icon xe đúng màu thân.
- Bộ khối theo cấp: **Cấp 1** Bắt đầu, Tiến, Lùi, Quay trái, Quay phải, Kết thúc · **Cấp 2** + Lặp ×2/×3, Âm thanh, Đèn mắt, Chờ ·
  **Cấp 3** + số ô 1–4 trên khối, Khi bấm nút trên xe. (Chốt lại sau rà soát GDPT 2018 Tin học lớp 1–3.)

## Rà soát giáo dục (2026-11-16) – `docs/research-notes/education/block-coding-car-curriculum.md`
- GDPT 2018: Tin học bắt đầu **lớp 3**; lớp 1–2 gọi là hoạt động STEM/trải nghiệm (TODO đối chiếu Phụ lục TT 32/2018).
- Đề xuất chỉnh bộ khối (chờ Tuan duyệt cùng bố cục): Bắt đầu = ô cố định đầu dải; bỏ khối Kết thúc; Lặp = 1 khối (không cặp mở/đóng);
  bỏ Chờ khỏi v1; "Khi bấm nút trên xe" sang v2; Cấp 1–2 ≤ 8 khối (giả thuyết, thử thực địa).
- UI: khối ≥ 96 px, vùng thả rộng, vừa **bấm để thêm** vừa kéo để sắp xếp (trẻ 6–8 kéo chính xác còn khó); mũi tên theo hướng mặt xe.
- Lộ trình 8 buổi × 30 phút trong báo cáo.

## 3 hướng dáng xe (Tuan chọn bằng ảnh)
| | A – Xe hộp mặt cười | B – Bọ rùa | C – Cú con (dùng lại vỏ card-coding-robot) |
|---|---|---|---|
| Dáng | Khối xe bo tròn, kính chắn gió = mặt LED, nóc phẳng có nút Dừng | Vòm thấp, mắt LED ở đầu, chấm lưng | Thân trứng đứng, mắt to |
| Hợp với | Bé hiểu ngay "đây là xe", hướng mặt rõ cho Quay trái/phải | Trọng tâm thấp, khó lật, in nhanh | Một vỏ cho 2 dự án, cùng thương hiệu Cú Bông |
| Đổi lại | Cao hơn B; phải làm khác hẳn xe đồ chơi thương mại | Nóc cong → nút Dừng khó đặt | Cao 98 mm dễ lật khi quay; "cú" không giống xe |

**Khuyến nghị: A – Xe hộp mặt cười** – bé lớp 1 nhận ra "xe" ngay, hướng mặt rõ (quan trọng nhất khi học trái/phải),
nóc phẳng đặt nút Dừng + nhãn màu tên xe. Đế chung nên vẫn đổi sang B/C được sau.

## 3 bố cục app (Tuan chọn bằng ảnh) – `ui-mockups/`
| | U1 – Sân khấu trên, dải lệnh dưới | U2 – Lưới trái, khối phải | U3 – Thẻ lớn theo cấp |
|---|---|---|---|
| Bố cục | Lưới ô ảo phía trên, dải lệnh giữa, kho khối theo màu ở đáy | Lưới lớn bên trái, kho khối cột phải, dải lệnh đáy | Khối to như thẻ, tab Cấp 1/2/3, dải lệnh đánh số |
| Hợp với | Quen mắt kiểu ScratchJr, màn 16:9 lab | Màn rộng, giáo viên chiếu | Bé nhỏ nhất, chuột vụng |
| Đổi lại | Lưới nhỏ hơn U2 | Mắt bé đi xa giữa kho khối và dải lệnh | Ít khối/màn, phải bấm tab |

**Khuyến nghị: U1** – kéo khối theo chiều dọc ngắn (kho khối ngay dưới dải lệnh), lưới vẫn đủ 6 × 6.

## Đầu ra bước 0 (ảnh – Tuan duyệt)
- `concepts/` – 3 dáng: hông, đỉnh, 3/4, đặt trên ô 150 mm + bàn tay trẻ 6 tuổi làm thước. `cmf.png`.
- `ui-mockups/` – 3 bố cục app 1920 × 1080 (ảnh chụp từ HTML tĩnh).
- `contact-sheet.png` gộp tất cả.

## Quyết định
<!-- Tuan chọn: ngày | dáng xe | bố cục app | ghi chú → chép 1 dòng vào README "Lịch sử sửa" -->

## Chờ Tuan quyết (2026-11-16) – xem `contact-sheet.png`
1. **Dáng xe** A / B / C (khuyến nghị A). Ghi chú: A hơi "bánh tầng" – CAD sẽ bo mượt.
2. **Bố cục app** U1 / U2 / U3 (khuyến nghị U1).
3. **Bộ khối** theo đề xuất rà soát giáo dục (bỏ Kết thúc, Lặp 1 khối, bỏ Chờ v1)? Khuyến nghị: đồng ý.
4. **Màu nút Dừng** ở bản thân xanh: thêm 1 cuộn đỏ nhỏ (4 màu, khuyến nghị – nút Dừng đỏ là quy ước an toàn) hay bỏ trắng.
- Kỹ thuật tự xử lý giai đoạn 1: tính trọng tâm (pin sau trục, 1 bi đỡ), đo bo S3/ULN2003/hộp pin thật.
