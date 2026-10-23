# in-3d – Bambu Lab A1

## Mục tiêu
Kho model, profile và ghi chú in cho máy Bambu Lab A1.

## Cấu trúc
- `models/<du-an>/`: STL/3MF/STEP, kèm `README.md` (vật liệu, profile, thời gian in).
- `profiles/`: profile Bambu Studio đã tinh chỉnh (ghi lý do khi sửa).
- `nhat-ky-in.md`: lỗi in và cách xử lý.

## Skill
- `bambu-a1` (tự viết, chỉ tư vấn, không điều khiển máy).
- Không dùng MCP điều khiển máy in: xem lý do trong `docs/COMMUNITY.md`.

## Dung sai A1 (đường kính vẽ trong CAD, lỗ thẳng đứng, đầu 0,4 mm, lớp 0,20 mm)
Đo bằng mẫu `models/mau-dung-sai-a1/` (hướng dẫn trong README ở đó). Chưa in thử → giữ TODO, không đoán.
| Lắp ghép | PLA | PETG |
|---|---|---|
| Trục 5 mm – vừa | TODO | TODO |
| Ổ bi 608 – ép | TODO | TODO |
| M3 xuyên | TODO | TODO |
| M3 tự tạo ren | TODO | TODO |

## TODO
- Đầu phun mặc định: **0,4 mm** thép không gỉ (Tuan chốt 2026-10-21); profile mặc định "0.20mm Standard @BBL A1"
  (lớp 0,20 mm, đường in 0,42 mm) – chi tiết trong skill `bambu-a1`.
- TODO: có AMS lite không, các loại nhựa đang có.
