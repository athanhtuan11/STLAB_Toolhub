# spec-probe – firmware dò ESP32-A1S Audio Kit

cwd: `maker/english-teacher/firmware/probe-a1s`
allow: `main/**`, `CMakeLists.txt`, `sdkconfig.defaults`, `partitions.csv` (nếu cần), `build.ps1`, `flash.bat`, `README.md`
Không sửa: `check_probe.py`. Mẫu khuôn: `maker/esp32-s3-cam/firmware/probe/` (build.ps1 xóa biến MSYS + xóa .bin cũ, flash.bat,
IdfId `esp-idf-20ee62e792ea89630ac6a777ab3ebc57` = ESP-IDF 5.5.4). Project name `probe_a1s` → `build/probe_a1s.bin`, target `esp32`.
gate: `powershell -NoProfile -ExecutionPolicy Bypass -File build.ps1 && python check_probe.py`

## Bối cảnh
Bo Ai-Thinker ESP32-A1S Audio Kit của Tuan ở **COM5** (CP210x): ESP32-D0WD-V3 rev 3.1, flash 4 MB. Chưa biết: PSRAM, codec
(ES8388 hay AC101), bộ chân. 3 bộ chân ứng viên + nguồn: bảng trong `../../CLAUDE.md` mục "Đã biết". Không đoán thêm chân ngoài bảng.

## Firmware làm (chạy 1 lượt khi khởi động, log UART 115200, tiền tố `[DO]`)
1. Chip: model/rev, flash thật (`esp_flash_get_physical_size`), PSRAM (`CONFIG_SPIRAM=y` + `CONFIG_SPIRAM_IGNORE_NOTFOUND=y`, in
   kích thước hoặc "khong co"), heap trống.
2. Quét I2C trên 2 bộ chân (SCL/SDA 32/33 và 23/18), 100 kHz, pull-up trong; in mọi địa chỉ trả ACK; đánh dấu 0x10/0x11 = ES8388,
   0x1A = AC101. Dùng driver I2C mới (`i2c_master_probe`); nhả bus trước khi đổi chân.
3. Theo kết quả: init codec tối thiểu (ES8388: chuỗi thanh ghi theo datasheet/ESP-ADF; AC101: chỉ báo "AC101 – chua ho tro phat",
   dừng ở bước 4) với I2S chuẩn Philips 16 kHz 16-bit, MCLK GPIO0, chân I2S của bộ khớp.
   Ghi rõ nguồn chuỗi thanh ghi ES8388 trong comment (vd. ESP-ADF `es8388.c` hoặc xiaozhi `es8388_audio_codec.cc`).
4. Bật PA GPIO21 mức cao; phát bíp 1 kHz 1,5 s ở **âm lượng thấp** (hằng `VOL_MAX` trần, mặc định ~30 % – tai người thử gần loa);
   log `[DO] Bip – nghe thay tieng?`.
5. Thu micro 3 s (DIN 35): in RMS/peak mỗi 0,5 s; rồi phát lại 3 s vừa thu (cùng âm lượng trần) – Tuan nghe xác nhận.
   Nếu codec có cả 2 kênh micro thì in RMS từng kênh.
6. Đọc 6 nút (36,13,19,23,18,5; active low; GPIO36/39 không có pull-up trong – chỉ đọc) trong 15 s, log khi nút đổi trạng thái.
   GPIO đang dùng cho I2C/I2S của bộ chân khớp thì bỏ qua nút đó và ghi chú.
7. Dòng tổng kết: `[KQ] psram=<MB> codec=<ES8388@0x10|AC101@0x1A|khong thay> i2c=<scl>/<sda> i2s=<mclk>/<bck>/<ws>/<dout>/<din> pa=21 mic_rms=<..>`.
   Không reset vòng lặp; xong thì idle, nhấn nút bất kỳ để chạy lại bước 4–5.

## Nạp + thử trên mạch (sau khi gate PASS)
`idf.py -p COM5 flash monitor` (hoặc flash.bat COM5) – Tuan đã cắm mạch và đồng ý dò. Đọc log ~40 s, lưu vào `probe-log.txt`.
Báo nguyên dòng `[KQ]`. Phần "nghe thấy bíp / tiếng phát lại" phải hỏi Tuan – không tự kết luận.

## Không làm
Không Wi-Fi, không ghi NVS ngoài mặc định, không đổi eFuse, không âm lượng lớn, không thêm chân ngoài bảng ứng viên.
