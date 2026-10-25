# BOM tủ điều khiển máy bơm (chốt 2026-10-25)

Motor 220 V 1 pha 2 HP (≈ 1,5 kW), dòng chạy ước tính ≈ 12,5 A (`power-and-wiring.md` mục 4). MCB/RCD dùng của tủ điện
nhà khách (Tuan bỏ qua kiểm). Wi-Fi tại chỗ đặt tủ: có. Thông số ghi theo yêu cầu kỹ thuật, không theo hãng –
`TODO` = kiểm datasheet món mua thật.

## Động lực + bảo vệ motor
| # | Món | Thông số cần | SL |
|---|---|---|---|
| 1 | Contactor | **AC-3 ≥ 18 A**, cuộn hút **220 VAC**, có ≥ 1 tiếp điểm phụ NO (báo chạy) | 1 |
| 2 | Relay nhiệt | Lắp được với contactor #1, **dải chỉnh ~9–13 A** (chứa 12,5 A), có tiếp điểm NC (+ NO báo lỗi nếu có) | 1 |
| 3 | Dây động lực | Cu **2,5 mm²** (L, N, PE) tới motor | theo khoảng cách |

## Mạch điều khiển (220 VAC cuộn hút)
| # | Món | Thông số cần | SL |
|---|---|---|---|
| 4 | Cầu chì mạch điều khiển + đế | **2 A** (bảo vệ cuộn hút, đèn, nguồn 5 V) | 1 |
| 5 | Nút dừng khẩn | Nấm đỏ, tự giữ, tiếp điểm **NC** | 1 |
| 6 | Công tắc xoay 3 vị trí | **TAY – TẮT – TỰ ĐỘNG**, 220 VAC | 1 |
| 7 | Đèn báo 220 VAC | Xanh = nguồn, Vàng = đang chạy, Đỏ = lỗi (relay nhiệt) | 3 |
| 8 | Dây điều khiển | Cu 1 mm², đầu cos | 1 cuộn nhỏ |

## Điện tử (ngăn điện áp thấp)
| # | Món | Thông số cần | SL |
|---|---|---|---|
| 9 | Bo ESP32 | **ESP32-DevKitC WROOM-32D** (cấp 5 V vào chân 5V) | 1 (+1 dự phòng) |
| 10 | Nguồn AC-DC cách ly | 220 VAC → **5 V ≥ 1 A**, loại module đóng kín | 1 |
| 11 | Module relay | 1 kênh, **opto, kích mức cao, chạy được với logic 3,3 V**, tiếp điểm 220 VAC (chỉ đóng cuộn hút) | 1 |
| 12 | Đo điện năng | **PZEM-004T v3 bản 100 A có CT kẹp** (bản 10 A không đủ) | 1 |
| 13 | Chuyển mức / chia áp UART | cho TX của PZEM → RX ESP32 (`TODO` mức TX PZEM) | 1 |

## Tủ + lắp đặt
| # | Món | Thông số cần | SL |
|---|---|---|---|
| 14 | Tủ nhựa | **IP65**, có ray DIN, đủ 2 ngăn (động lực / điện áp thấp); kích thước `TODO` sau bố trí (ước ~300 × 200 × 150 mm) | 1 |
| 15 | Ray DIN + cầu đấu | cầu đấu 2,5 mm² (động lực), 1 mm² (điều khiển), **cầu đấu PE** | bộ |
| 16 | Ốc siết cáp | IP65, cỡ theo dây | 3–4 |

## Chống chạy khô
- Mặc định: **phần mềm** – PZEM đo công suất thấp bất thường > 30 s → tắt + báo (ngưỡng `TODO` đo khi bơm có nước / mất nước).
- Thêm phao/công tắc áp (phần cứng, nối NC vào mạch cuộn hút) khi biết loại bơm – `TODO`.

## Ghi chú lắp
- Thứ tự mạch cuộn hút: L → cầu chì 2 A → E-stop NC → NC relay nhiệt → (chống chạy khô NC) → công tắc 3 vị trí
  (TAY: thẳng / TỰ ĐỘNG: qua relay ESP32) → cuộn hút A1; A2 → N.
- Ngăn điện áp thấp tách khỏi dây 220 V; nối đất tủ + motor; lần chạy đầu đo dòng bằng PZEM rồi **chỉnh relay nhiệt = dòng đo**.
