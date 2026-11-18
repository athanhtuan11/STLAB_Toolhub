# Hướng dẫn lắp tủ điều khiển máy bơm từ xa (ESP32 + RainMaker)

## Thông tin công trình
| Mục | Giá trị |
|---|---|
| Máy bơm | 220 V, 1 pha, 2 HP (≈ 1,5 kW); dòng chạy ước tính ≈ 11–12,5 A, khởi động ~60–90 A. Dòng trên nhãn: TODO ghi khi tới nơi |
| Điều khiển | ESP32-DevKitC WROOM-32D, firmware pump-control **1.2.0**, app **ESP RainMaker**, Wi-Fi 2,4 GHz nhà khách |
| Phạm vi | **Chỉ bật/tắt từ xa.** Không có bảo vệ motor (relay nhiệt, dừng khẩn, chống chạy khô, đo dòng) – đã chốt 2026-10-25 |
| Bảo vệ nguồn | MCB + RCD của tủ điện nhà khách (nhánh riêng cho bơm 16–25 A; RCD 30 mA) |
| Người lắp | Tuan (STLab) – thợ điện có kinh nghiệm. **Không giao học sinh/khách tự đấu** |

## An toàn – đọc trước khi làm
- 220 V AC + nước: **cắt MCB nhánh bơm, treo biển "Đang sửa – cấm đóng điện"**, thử không điện bằng bút thử/đồng hồ trước khi chạm.
- Nối đất **PE** (dây vàng-xanh) cho vỏ tủ (nếu có phần kim loại) và vỏ motor.
- ESP32 + module relay **chỉ đóng cuộn hút contactor**. Dòng motor đi qua **tiếp điểm chính contactor**, không bao giờ qua relay module.
- Ngăn điện áp thấp (ESP32, nguồn 5 V, relay) đặt **tách** khỏi dây 220 V động lực; dây 220 V không đi đè lên bo ESP32.
- Khi cắm USB vào ESP32 để nạp/xem log: **ngắt nguồn 5 V của tủ** (chỉ 1 nguồn cho bo tại 1 lúc – theo Espressif).
- Tủ nhựa mua sẵn (IP65 nếu ngoài trời). **Không** dùng vỏ in 3D PETG cho tủ điện (không chống cháy).
- Lắp xong: bấm nút **TEST** của RCD nhà khách – phải nhảy.

## Vật tư (đánh dấu khi chuẩn bị)
| # | Món | Thông số | SL | ☐ |
|---|---|---|---|---|
| 1 | Contactor | **LS Metasol MC-22b** (AC-3 22 A, phụ 1NO+1NC). Cuộn hút phải **220 VAC** – TODO đọc nhãn cuộn | 1 | ☐ |
| 2 | Bo ESP32 | ESP32-DevKitC WROOM-32D, đã nạp firmware 1.2.0 | 1 | ☐ |
| 3 | Nguồn AC-DC cách ly | 220 VAC → **5 V ≥ 1 A**, loại đóng kín | 1 | ☐ |
| 4 | Module relay | Opto 1–2 kênh 5 V, có jumper H/L | 1 | ☐ |
| 5 | Công tắc xoay | 3 vị trí giữ **TAY – TẮT – TỰ ĐỘNG**, Ø22 mm, **2NO**, ≥ 220 VAC | 1 | ☐ |
| 6 | Tủ nhựa | IP65 nếu ngoài trời, ray DIN, cầu đấu, ốc siết cáp | 1 | ☐ |
| 7 | Dây động lực | Cu **2,5 mm²** (L, N, PE). Đường dây > ~20 m: TODO tính sụt áp, có thể 4 mm² | theo thực tế | ☐ |
| 8 | Dây điều khiển | Cu 1 mm² (mạch cuộn hút 220 V); dây Dupont/0,5 mm² cho 5 V | – | ☐ |
| 9 | Phụ kiện | Đầu cos pin/cos chĩa, gen co nhiệt, dây rút, nhãn dán, đế/ốc gắn bo ESP32 | – | ☐ |

**Dụng cụ:** bút thử điện, đồng hồ vạn năng, kìm tuốt + kìm bấm cos, tua vít, khoan + mũi khoét **Ø22 mm**, laptop + cáp micro-USB (kết nối app lần đầu).

## Bước 1 – Kiểm linh kiện trên bàn (chưa cấp điện)
1. **Contactor:** đọc nhãn cuộn hút → phải ghi **220 VAC** (hoặc 220–240 V AC). Sai điện áp cuộn thì **dừng**, đổi cuộn/contactor. Ghi lại: TODO.
2. Đo điện trở cuộn hút A1–A2: phải có giá trị (không 0 Ω, không hở). Ghi lại: TODO Ω.
3. **Công tắc xoay:** đo thông mạch từng khối tiếp điểm ở cả 3 vị trí, ghi vào bảng dưới. Yêu cầu: vị trí giữa (TẮT) **cả 2 khối hở**.
4. **Module relay:** đặt jumper **H** (kích mức cao). Ghi nhớ 3 cọc ra: COM, NO, NC – chỉ dùng **COM + NO**.
5. **ESP32:** cấp USB từ laptop, mở log (`flash.ps1` / monitor) → thấy firmware **1.2.0**, relay ở TẮT. Bo mới chưa có firmware: nạp bằng `firmware/flash.ps1` (chỉ lần đầu; sau đó cập nhật OTA).

| Vị trí công tắc | Khối 1 (dùng cho TAY) | Khối 2 (dùng cho TỰ ĐỘNG) |
|---|---|---|
| TAY | phải **thông** ☐ | phải **hở** ☐ |
| TẮT | phải **hở** ☐ | phải **hở** ☐ |
| TỰ ĐỘNG | phải **hở** ☐ | phải **thông** ☐ |

**Kiểm tra:** cuộn hút 220 VAC, công tắc đúng bảng trên, relay jumper H, ESP32 chạy 1.2.0.

## Bước 2 – Bố trí và khoan tủ
1. Khoét lỗ **Ø22 mm** trên cửa tủ cho công tắc xoay, dán nhãn **TAY / TẮT / TỰ ĐỘNG**.
2. Gắn ray DIN. Bố trí 2 ngăn: **ngăn 220 V** (cầu đấu vào, contactor, nguồn 5 V) và **ngăn điện áp thấp** (ESP32, module relay).
3. ESP32 đặt chỗ **sóng Wi-Fi ra được** (không kẹp giữa tấm kim loại), cổng micro-USB quay ra chỗ cắm được khi cần.
4. Lắp ốc siết cáp ở **đáy tủ** (nước không chảy theo dây vào tủ): 1 lỗ cáp nguồn vào, 1 lỗ cáp ra motor.

**Kiểm tra:** cửa tủ đóng kín không cấn dây; công tắc xoay quay đủ 3 nấc.

## Bước 3 – Đấu mạch động lực (dây 2,5 mm²)
**⚠ 220 V:** Làm khi MCB nhánh bơm đã cắt và đã thử không điện.

| Từ | Đến | Dây |
|---|---|---|
| MCB nhánh bơm (tủ nhà) – L | Cầu đấu vào tủ – L | 2,5 mm² nâu/đỏ |
| MCB nhánh bơm (tủ nhà) – N | Cầu đấu vào tủ – N | 2,5 mm² xanh dương/đen |
| PE tủ nhà | Cầu đấu PE trong tủ | 2,5 mm² vàng-xanh |
| Cầu đấu L | Contactor cọc **1/L1** | 2,5 mm² |
| Cầu đấu N | Contactor cọc **3/L2** | 2,5 mm² |
| Contactor cọc **2/T1** | Motor – L | 2,5 mm² |
| Contactor cọc **4/T2** | Motor – N | 2,5 mm² |
| Cầu đấu PE | Vỏ motor (cọc tiếp đất) | 2,5 mm² vàng-xanh, **không qua contactor** |

- Contactor đóng cắt **cả L và N** (2 cực). Cọc 5/L3 – 6/T3 bỏ trống.
- Ký hiệu cọc theo chuẩn IEC in trên thân contactor – đối chiếu nhãn thật trước khi đấu.
- Siết chặt đầu cos; giật nhẹ từng dây để chắc không tuột.

**Kiểm tra:** đo thông mạch – contactor chưa hút: L1–T1 **hở**, L2–T2 **hở**; ấn tay đầu contactor (nếu có nút thử) → thông.

## Bước 4 – Đấu mạch cuộn hút (220 V, dây 1 mm²)
| Từ | Đến | Ghi chú |
|---|---|---|
| Cầu đấu L | Đầu vào khối 1 công tắc | |
| Đầu vào khối 1 | Đầu vào khối 2 công tắc | dây nối tắt (cầu) – cả 2 khối chung L |
| Đầu ra khối 1 (TAY) | Contactor **A1** | |
| Đầu ra khối 2 (TỰ ĐỘNG) | Module relay **COM** | |
| Module relay **NO** | Contactor **A1** | 2 dây chung cọc A1 (cos đôi) |
| Contactor **A2** | Cầu đấu N | |

- TAY: L → khối 1 → A1 → contactor hút → bơm chạy (không cần ESP32/Wi-Fi).
- TẮT: cả 2 khối hở → bơm **không chạy được** kể cả bấm trên app.
- TỰ ĐỘNG: L → khối 2 → relay (ESP32 điều khiển) → A1.
- Ở vị trí TAY: app **không tắt được** và không biết bơm đang chạy (ESP32 không đọc công tắc).

**Kiểm tra:** đo L–A1 (chưa điện): TAY = thông; TẮT = hở; TỰ ĐỘNG = hở (relay đang nhả).

## Bước 5 – Đấu nguồn 5 V + ESP32 + module relay
| Từ | Đến | Ghi chú |
|---|---|---|
| Cầu đấu L | Nguồn 5 V – đầu vào **L (AC)** | lấy trước contactor (ESP32 luôn có điện) |
| Cầu đấu N | Nguồn 5 V – đầu vào **N (AC)** | |
| Nguồn 5 V – **+5V** | ESP32 chân **5V** | |
| Nguồn 5 V – **+5V** | Module relay **VCC** | |
| Nguồn 5 V – **GND** | ESP32 **GND** + module relay **GND** | GND chung |
| ESP32 **GPIO26** | Module relay **IN1** | jumper **H** |

- **Không** cấp 5 V vào chân 3V3 hay GPIO bất kỳ – GPIO ESP32 chỉ chịu 3,3 V.
- Không cắm USB cùng lúc với nguồn 5 V của tủ.
- Dây 5 V đi riêng, bó gọn, cách dây 220 V.

**Kiểm tra:** trước khi cắm ESP32 – cấp điện thử nguồn 5 V, đo ra **5 V** (±5 %) rồi mới nối vào bo. TODO ghi điện áp đo được.

## Bước 6 – Kiểm tra trước khi đóng điện
1. Siết lại toàn bộ cọc (contactor, cầu đấu, công tắc, nguồn 5 V).
2. Đo cách điện thô bằng đồng hồ (thang Ω lớn nhất): L–PE, N–PE **không thông**.
3. Đo L–N phía vào tủ, công tắc ở TẮT: **không chập** (chỉ thấy tải nhỏ của nguồn 5 V).
4. Rút **dây motor** khỏi T1/T2 (hoặc chưa đấu) để thử không tải ở bước 7.
5. Đóng cửa ngăn 220 V; xoay công tắc về **TẮT**.

**Kiểm tra:** không có đầu dây trần lòi ra; PE đã nối vỏ motor.

## Bước 7 – Thử không tải (chưa nối motor)
**⚠ 220 V:** Đóng MCB nhánh bơm.

1. Đèn nguồn ESP32 sáng; relay **không** hút (firmware mặc định TẮT khi có điện).
2. Xoay **TAY** → contactor hút (nghe "cạch"). Xoay về **TẮT** → nhả.
3. Xoay **TỰ ĐỘNG** → contactor vẫn nhả (chưa bật trên app).
4. Cắt MCB rồi đóng lại vài lần: contactor **không** tự nhảy lúc ESP32 khởi động (GPIO26 không phát xung). Có nhảy → dừng, báo lại để sửa firmware.

**Kiểm tra:** TAY hút, TẮT nhả, TỰ ĐỘNG chờ lệnh app, khởi động không nhảy.

## Bước 8 – Kết nối ESP32 với Wi-Fi và app
1. Cài app **ESP RainMaker** (iOS/Android), đăng nhập tài khoản sẽ dùng (STLab hoặc của khách – thiết bị gắn vào tài khoản đó).
2. Mở log ESP32 (laptop, **ngắt nguồn 5 V tủ khi cắm USB**) → thấy **mã QR**, tên `PROV_xxxx` và mã PoP.
3. App → **Add Device** → quét QR (hoặc chọn Bluetooth + nhập PoP) → chọn **Wi-Fi 2,4 GHz** nhà khách → nhập mật khẩu.
4. Chờ kết nối quá **30 phút** mà chưa xong → bấm nút **EN** trên bo để chạy lại.
5. Rút USB, cấp lại nguồn 5 V tủ → app thấy thiết bị **"May bom"** online.
6. Kiểm mục **"Giờ thiết bị"** trùng giờ Việt Nam (UTC+7).
7. Xoay công tắc **TỰ ĐỘNG** → bấm **Bật** trên app → contactor hút; **Tắt** → nhả.
8. Thử chống bật liên tục: tắt xong bấm bật ngay → app báo phải chờ **5 s**.
9. Đặt **"Chạy tối đa (phút)" = 5** → bật → chờ tự tắt + app báo "May bom da tu tat…". Xong đặt lại theo nhu cầu khách (mặc định 30 phút).

- Nút **BOOT** trên bo: giữ **3 s** = xóa Wi-Fi (đổi mạng); giữ **10 s** = reset nhà máy.
- Mật khẩu Wi-Fi khách **không** ghi vào giấy này / file dự án.

**Kiểm tra:** app bật/tắt được; tự tắt sau "Chạy tối đa"; giờ thiết bị đúng.

## Bước 9 – Thử có tải (nối motor)
**⚠ 220 V:** Cắt MCB, thử không điện, nối lại dây motor vào **2/T1, 4/T2**, PE vào vỏ motor. Đóng MCB.

1. **Có nước trong bơm/đường ống** trước khi chạy (không có bảo vệ chạy khô).
2. Xoay **TAY** → bơm chạy, nước lên. Xoay **TẮT** → bơm dừng.
3. Xoay **TỰ ĐỘNG** → bật/tắt từ app vài lần (cách nhau ≥ 5 s).
4. Đo dòng bằng ampe kìm trên dây L: lúc chạy ổn định TODO A; lúc khởi động (nếu kìm đo được) TODO A. So với nhãn motor.
5. Sờ (cẩn thận) contactor + nguồn 5 V sau 10–15 phút chạy: ấm nhẹ là bình thường, nóng rát → dừng kiểm tra cọc lỏng.
6. Motor không quay, kêu ù → cắt điện ngay, kiểm **tụ khởi động/tụ chạy** của motor.
7. Bấm **TEST** của RCD nhà khách → phải nhảy. Đóng lại.

**Kiểm tra:** bơm chạy cả TAY lẫn app, dòng chạy gần dòng nhãn, RCD nhảy khi TEST.

## Bước 10 – Hẹn giờ + bàn giao khách
1. App → **Schedules** → **Add Schedule** → thiết bị "May bom" → **Power = On** → giờ (vd. **06:00**) → lặp **mỗi ngày** → lưu. Thêm lịch **18:00** nếu cần.
2. Bơm tự tắt sau "Chạy tối đa (phút)" = thời gian tưới. Muốn sáng/chiều khác nhau: thêm lịch **Power = Off**, để "Chạy tối đa" dài hơn làm chốt an toàn.
3. Lịch chạy **trên ESP32**: mất Internet vẫn chạy nếu đã có giờ; mất điện + mất mạng cùng lúc → chờ có mạng lấy giờ lại.
4. Dán nhãn trong cửa tủ: sơ đồ bước 3–5, ngày lắp, số điện thoại STLab.
5. Hướng dẫn khách:
   - **TỰ ĐỘNG** = điều khiển bằng app/lịch. **TAY** = bơm chạy liên tục (khi mất Wi-Fi). **TẮT** = khóa bơm (khi sửa ống).
   - Ở **TAY**, app không tắt được bơm – nhớ xoay về TỰ ĐỘNG/TẮT.
   - Không có bảo vệ chạy khô / quá tải: **không để bơm chạy khi hết nước**; thấy bơm kêu lạ → xoay TẮT, gọi STLab.
   - Có thông báo "Ban moi" trên app → khi bơm đang **TẮT**, bấm **Cap nhat** (20–40 s, tự khởi động lại).
   - Đổi Wi-Fi nhà: gọi STLab (giữ BOOT 3 s rồi kết nối lại).

| Bàn giao | Kết quả |
|---|---|
| Ngày lắp | TODO |
| Dòng trên nhãn motor | TODO A |
| Dòng chạy đo được | TODO A |
| Chạy tối đa đã đặt | TODO phút |
| Lịch đã cài | TODO |
| Tài khoản RainMaker gắn thiết bị | TODO (không ghi mật khẩu) |
| Khách ký nhận | |
