# Cú Bông – loa dạy tiếng Anh (bản ESP32-S3)

Cú Bông là chú loa biết nói, giúp em học tiếng Anh. Bản này dùng bo ESP32-S3 với mic, ampli và 1 loa.
Em làm theo đúng thứ tự từng mục. Gặp chỗ không chắc thì hỏi thầy/cô trước khi làm tiếp.

## 1. Linh kiện

| Linh kiện | Số lượng | Ghi chú |
|---|---|---|
| ESP32-S3 N16R8 devkit | 1 | Bo chính |
| Mic INMP441 | 1 | Thu giọng em (I2S) |
| Ampli MAX98357A | 1 | Đưa tiếng ra loa (I2S) |
| Loa 52 mm, 4 Ω 3 W | 1 | Cao 26 mm |
| Tụ hóa 1000 µF 16 V | 1 | Có cực |
| Switch MX | 1 | Nút nói, trên đỉnh đầu |
| Nắp nút (button-cap) | 1 | In sẵn |
| Hàng rào chân cắm (pin header) | đi kèm module | Hàn vào mic và ampli |
| Dây Dupont cái–cái hoặc dây điện mềm | ~12 sợi | Nối tín hiệu và nguồn |
| Cáp USB-C thẳng | TODO | Cấp nguồn và nạp chương trình |
| Keo nóng | TODO | Dán khay ampli, giữ nắp mic |
| Bàn in PETG (6 bàn A–F) | 6 | In không support |

## 2. An toàn

- **INMP441 chỉ cấp 3,3 V.** Cấp 5 V có thể làm hỏng mic.
- **MAX98357A cấp 5 V.** Không lấy điện từ chân 3,3 V của bo, vì bo sẽ chập chờn.
- **Hai dây loa (+ và −) không được nối vào GND.** Chạm GND là hỏng ampli.
- **Tụ hóa có cực.** Chân dài (+) vào VIN, chân ngắn có vạch trắng (−) vào GND. Cắm ngược tụ có thể phồng, nổ.
- **Chỉ hàn khi có thầy/cô bên cạnh.** Làm ở chỗ thoáng, không hít khói hàn, rửa tay sau khi hàn.
- **Rút USB khi hàn.** Mỏ hàn khoảng 330–350 °C. Hàn xong để nguội, không chạm vào đầu mỏ.
- **Nguồn:** dùng củ sạc 5 V ≥ 2 A. Đang cấp nguồn ngoài vào chân 5V thì không cắm thêm cáp máy tính.
- **Âm lượng thử ≤ 70.** Nghe rè thì hạ âm lượng xuống.

## 3. Sơ đồ đấu dây

Nhìn sơ đồ, cắm từng dây, tích ô khi xong.

<!-- wiring -->

**Tụ 1000 µF:** mắc song song với nguồn của ampli để tránh sụt áp khi loa kêu to. Hàn tụ sát chân VIN và GND trên module MAX98357A, không hàn ở đầu bo ESP32. Kiểm lại vạch trắng nằm phía GND trước khi cắm điện.

```
  Bo ESP32-S3 5V ───────────┬──────── VIN  (MAX98357A)
                            │
                          ( + )   chân dài, phía KHÔNG có vạch
                         [ 1000 µF ]
                          ( − )   chân ngắn, phía có VẠCH trắng
                            │
  Bo ESP32-S3 GND ──────────┴──────── GND  (MAX98357A)
```

## 4. Hàn và nối dây

1. Cắm hàng rào chân cắm vào breadboard để giữ thẳng. Đặt module INMP441 hoặc MAX98357A lên rồi hàn từng chân.
2. Kiểm tra mối hàn: tròn, hình nón, không dính sang chân bên cạnh.
3. Trên MAX98357A, hàn cầu đấu vít 2 chân (hoặc 2 dây) ở cổng loa.
4. Hàn tụ 1000 µF theo mục 3. Đúng cực!
5. Hàn 2 dây vào 2 chân của switch MX. Một dây nối GPIO1, một dây nối GND.
6. Nối dây theo sơ đồ mục 3. Mic: chân L/R phải nối GND, không để trống. GAIN và SD của ampli để trống.
7. Dây I2S càng ngắn càng tốt (khuyến nghị ≤ 15 cm). Không dùng GPIO35, 36, 37 vì PSRAM đang chiếm.

## 5. In và lắp vỏ

1. In đủ 6 bàn A–F bằng PETG. Không cần support.
2. Lắp loa vào vành loa. Đặt vòng ép lên, xoay để 3 chốt vào rãnh, xoay 30° cho khóa. Mép loa nằm dưới 4 lẫy lò xo PETG của vòng ép.
3. Dán khay ampli xuống sàn vỏ bằng keo nóng. Không cần vít.
4. Lắp mic: cắm ống dẫn âm vào gờ lõm trên vách trán. Trượt nắp kẹp mic từ dưới lên, vào 2 rãnh. Nếu lỏng thì chấm keo nóng.
5. Đặt switch MX và nắp nút vào đỉnh đầu. Nắp nằm trong vỏ.
6. Lắp bo ESP32-S3 từ trên xuống trước khi đóng 2 nửa vỏ. Cổng USB-C hướng ra lưng.
7. Đóng 2 nửa vỏ. Mic đặt xa loa nhất có thể, lỗ mic không hướng vào loa.

## 6. Nạp chương trình

TODO: Thầy/cô nạp sẵn firmware hoặc hướng dẫn tại lớp.

## 7. Kiểm tra và sửa lỗi

**Kiểm trước khi cắm điện:**

1. Dùng đồng hồ vạn năng, thang thông mạch. Đo 5V–GND và 3V3–GND: đồng hồ **không** được kêu.
2. Kiểm từng dây theo sơ đồ mục 3. Đầu này và đầu kia phải kêu.
3. Loa + và loa − không được thông với GND.
4. Cắm USB. Đèn bo phải sáng. Không có mùi khét, không linh kiện nào nóng tay. Có bất thường thì rút USB ngay.

**Thử:**

1. Bấm nút nói (khi đã lắp vỏ) hoặc nút BOOT (khi thử trên bàn). Cô chào em.
2. Em nói "Hello". Cô trả lời.
3. Lúc cô đang nói, em nói chen "Cô ơi!". Cô dừng lại và nghe em.

**Lỗi thường gặp:**

- **Bo tự khởi động lại khi loa to** (brownout): cấp 5 V riêng cho ampli qua module USB-C, nối chung GND. Nhờ thầy/cô giúp.
- **Cô tự ngắt lời khi không ai nói:** tiếng loa vọng vào mic. Đưa mic xa loa hơn, rồi báo thầy/cô để chỉnh.
