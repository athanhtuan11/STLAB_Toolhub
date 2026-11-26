# english-teacher – thiết bị nói chuyện dạy tiếng Anh cho bé 2–5 tuổi

Dự án Tuan mở 2026-11-05 (song song esp32-s3-cam). Kế hoạch: `C:\Users\hoang\.claude\plans\ng-l-m-tr-c-cuddly-curry.md`.

## Mục tiêu
- Bé 2–5 tuổi. **Từ 2026-11-08: Gemini tự lên bài theo độ tuổi, không ràng buộc, không giới hạn buổi** (bài tự do `server/free-lesson.on`);
  luôn có phụ huynh ngồi cạnh → không làm bộ lọc an toàn tự động. (Trước: bài theo chủ đề + AI chỉ nói trong phạm vi bài.)
- Bản 1: **ESP32-A1S Audio Kit** (có sẵn) – thử ý tưởng + nội dung; không khử vọng → bé **bấm KEY4** để ngắt lời cô.
- Bản 2: ESP32-S3 **trò chuyện trực tiếp, bé ngắt lời cô bằng giọng**. **2026-11-12 Tuan: mạch INMP441 + MAX98357A đã về,
  làm bản S3 realtime thay A1S** (thay quyết định 11-08 "phải bo có codec"). Không codec → AEC trên bo bằng **tham chiếu phần mềm**
  (mẫu PCM ra loa chép vào vòng đệm, trễ `STLAB_AEC_REF_DELAY_MS`, AFE "MR" + `USE_DEVICE_AEC` mở khóa bằng patch) + cầu nối lọc
  ngắt lời (`server/live/duplex.py` BargeGate: Silero ≥ 0,7 liên tục ≥ 240 ms mới tính là bé ngắt). Kém hơn tham chiếu phần cứng –
  phải đo thật; nếu vọng còn nhiều → cách âm mic/loa, chỉnh trễ, nâng ngưỡng; cuối cùng mới quay lại bo có codec.
  Spec: `firmware/xiaozhi-s3/spec-s3-realtime.md`, gate `firmware/xiaozhi-s3/check_s3.py` + `server/test_full_duplex.py`.
- Nền: 78/xiaozhi-esp32 **v2.5.2** (ESP-IDF 6.1) + máy chủ xinnan-tech/xiaozhi-esp32-server **tự chạy trên máy lab**.

## Đã biết (có nguồn)
- **2026-11-17 Tuan: bo A1S không còn dùng cho Cú Bông** → firmware xiaozhi-a1s + CAD/in bản A1S chuyển vào `backup/20261117-remove-a1s-cu-bong/`;
  thông số bo + firmware dò A1S chuyển sang `tools/esp32-a1s/` (dùng cho guitar-sai-thanh, drum-pad). Ghi chú lịch sử A1S bên dưới giữ để tra cứu.
- xiaozhi v2.5.2 (nền bản S3): ESP-IDF 6.1, xem mục Firmware.

- **Cơ khí** (2026-11-06): loa **Ø52 × cao 26 mm** (Tuan đo), **4 Ω 3 W** (nhãn loa, Tuan đọc 2026-11-12). **Bản S3: 1 loa duy nhất** (Tuan chốt 2026-11-12, thay 2 loa trái + phải; 2026-11-26 đổi lại 2 loa, mỗi loa 1 ampli) → vỏ S3 sau này: 1 loa, khay bo S3 N16R8, mic xa loa. Không ghép 2 loa vào 1 MAX98357A (song song 2 Ω quá tải).

## An toàn
- Nguồn USB 5 V. Pin Li-ion (nếu dùng): chỉ cell có mạch bảo vệ, ngăn bắt vít – chưa thiết kế.
- Âm lượng trần trong firmware (tai bé). Vỏ không chi tiết nhỏ rời (bé < 3 tuổi hóc), vít giấu.
- Giọng bé chỉ tới máy chủ trong lab; không lưu ghi âm lâu dài; cần phụ huynh đồng ý trước khi bé dùng thử.
- Khóa API trong biến môi trường, không vào file.

## Firmware
- **ESP-IDF 6.1** (cho xiaozhi v2.5.2) cài 2026-11-05: nguồn `C:\Espressif\frameworks\esp-idf-v6.1`, công cụ riêng
  `C:\Espressif\tools-v6.1` (~6,4 GB, esp32 + esp32s3; không đụng 5.5.4). Kích hoạt trong PowerShell: xóa biến MSYS →
  `$env:IDF_TOOLS_PATH='C:\Espressif\tools-v6.1'; . C:\Espressif\frameworks\esp-idf-v6.1\export.ps1`. Kiểm: `idf.py --version` = v6.1.

## Bảng khe lắp (quy tắc maker/CLAUDE.md: khe = kích thước thật + 0,2 mm; ngàm xoay ≥ 0,40) – bản có màn, rà 2026-11-26
| Cặp lắp | Kích thước thật | Vẽ | Khe/bên | Nguồn |
|---|---|---|---|---|
| Kính màn MSP2807 ↔ hốc face-plate | 69,2 × 50,0 | 69,8 × 50,6 | 0,3 | datasheet + **in thật ĐẠT 2026-11-26** (giữ) |
| PCB màn ↔ hốc | 86,0 × 50,0 | 86,4 × 50,6 | 0,2 (x) / 0,3 (z) | in thật ĐẠT (giữ) |
| Vít PCB màn M2.5 tự ren | lỗ Ø2,4 | Ø2,4 | – | fit-library, in thật (ngoại lệ) |
| Vít vành chặn M2.5 × 6 | Ø2,5 | lỗ thông Ø2,8 | 0,15 | fit-library (ngoại lệ) |
| Đĩa face-plate ↔ lỗ vỏ | 94 × 58 R14 (đổi 2026-11-26, cạnh thẳng/khe không đổi) | lỗ +0,3 mỗi bên | 0,3 | gate PASS, in thật ĐẠT |
| Vành chặn 104 × 68 ↔ hốc vỏ | 104 × 68 | hốc 104,6 × 68,6 | 0,3 | như trên |
| Loa Ø52 ↔ hốc | Ø52 | Ø52,6 | 0,3 | đo thật 2026-11-06 |
| Vòng ép loa ↔ thân loa | Ø52 (mép) | gờ giữ Ø48,0 | – (giữ mép 2,0/bên) | in thật ĐẠT 2026-11-26 |
| Ngàm xoay vòng ép: ống tay / chốt / rãnh | – | 0,40 / 0,40 / 0,45 | 0,40–0,45 | in thật (vành loa lần 1) |
| Nút nói ↔ lỗ vỏ | Ø50 | lỗ Ø50,8 | 0,4 | gate PASS |
| Ổ switch MX | 14,00 | 14,00 + rãnh V | – | fit-library catpaw (ngoại lệ); **nút nói Tuan in thử 2026-11-26 ĐẠT "rất tốt" (p6-test-gon: mini-cap hốc 9,8)** |
| Chữ thập 4,19 × 1,25, ống Ø5,71 | – | giữ | – | fit-library (ngoại lệ) |
| PCB mic Ø15 × 1,6 ↔ hốc | Ø15 | hốc Ø16,4 | 0,7 | gate; **ron xốp 1,2 mm trong khe 1,0** (ép 0,2) |
| PCB mic ↔ kẹp mic | Ø15 | Ø15,6 | 0,3 | gate PASS |
| Kẹp mic ↔ lỗ lót vỏ | Ø20,8 | lỗ Ø21,8 | 0,5 | gate PASS |
| Bo ESP32-S3 ↔ ray | 25,4–28,6 (**chưa đo hàng thật**) | ray 29,6 | ≥ 0,5 | TODO đo bo thật |
| Bo S3 ↔ khoang (z) | 16 (giữ chỗ) | 16,4 | 0,2 | giữ chỗ, TODO đo |
| USB-C ↔ lỗ cáp | 14 × 9 (giữ chỗ) | 14 × 9 R2, mái cách cổng 0,3 | 0,3 | TODO đo cáp |
| PCB ampli ↔ ray khay | 18,0 × 19,4 | rãnh +0,25 (x), z +0,4 | 0,25 / 0,2 | TODO đo ampli thật |
| Vít khay ampli | M2.5 | mồi Ø2,2 | – | tự ren (TODO thử) |
| Tai ốc M3 ↔ hốc lục giác | 5,5 AF | **5,9** (cũ 5,8) | **0,20** (cũ 0,15) | nâng 2026-11-26 |
| Vít M3 ↔ lỗ thông | Ø3,0 | Ø3,4 | 0,2 | quy tắc |
| Chốt định vị 2 nửa | Ø2,0 | chốt/lỗ chép từ bản A1S | 0,2 (TODO kiểm lại) | bản cũ đã in |

## Trạng thái
- 2026-11-26: **dáng A2 V2** = mắt màn TFT 2,8" cảm ứng (MSP2807) + **2 loa Ø52 H0** (sườn quay ngang; H25 bỏ vì phải support), gờ giữ loa Ø48, mỗi loa 1 MAX98357A.
  CAD `cad/build_owl_s3_screen.py` → `out-s3-screen`: gate PASS, 5 bàn `plates-s3-screen` PASS không support (~16 h, ~443 g); lỗ màn V1.1 đối xứng 80 × 44; chờ duyệt dáng + kết quả bàn thử v3.
  **Bàn thử v3** `p1-fit-test.3mf` (face-plate, speaker-ring-L, button-cap) CHỜ IN. Firmware bản 1 loa, CHƯA có driver màn/cảm ứng, CHƯA thử ampli 2.
  File bản S3 1 loa cũ → `cad/backup/` + `print/backup/20261126-ban-s3-1-loa-thay-bang-ban-man/`. Câu hỏi chờ Tuan: xem `README.md`.
- 2026-11-15: **Trang giáo trình `/curriculum`** trên bridge (`server/live/curriculum_web.py`, cổng 8003; ra ngoài
  `https://engteacher.mamnoncaynho.com/curriculum`): xem 24 unit Seed + giáo án, **ghim bài theo máy** (`Curriculum.pin`, lưu
  `learners.json` khóa `pins`) tới khi Bỏ ghim; đang trong buổi thì đổi bài ngay (`ACTIVE_SESSIONS`). Bé vẫn xin đổi bằng giọng
  trong buổi; buổi sau về bài ghim. PIN = biến môi trường `STLAB_CURRICULUM_PIN` (chưa đặt → 503). Gate `server/test_curriculum_web.py`.
  Bật: xem `server/deploy/README.md`. Chưa thử trên mạch thật (gửi bài giữa buổi chờ `turn_complete`).
- 2026-11-12: **Lộ trình = giáo trình Seed** (Tuan chọn thay 12 bài cũ): `lessons-seed/` (24 bài + ROADMAP.md) sinh từ
  `stlab/english-curriculum/seed/units.yaml` bằng `seed/export_device.py` – sửa units.yaml rồi chạy lại, không sửa tay.
  2–3 tuổi học Seed 1; 4–5 tuổi Seed 2 → Seed 3. `bridge.py` mặc định `lessons-seed`, quay lại bài cũ: `STLAB_LESSONS_DIR=..\lessons`.
  Gate `server/test_seed_lessons.py` PASS + 6 test cũ PASS. **Đã kích hoạt 09:12**: bài tự do TẮT (`free-lesson.off`, đổi
  tên lại `.on` để bật), bridge khởi động lại với lessons-seed. Mục tiêu "Gemini tự lên bài" ở trên không còn là mặc định.
- 2026-11-08 tối (mới nhất; chi tiết từng bước trong git log + `docs/review-2026-11-08.md`):
  - Máy chủ đang chạy **Gemini Live** (`server/live.on`, cầu nối `server/live/bridge.py`) + **bài tự do** (`server/free-lesson.on`), IP cố định 192.168.1.56.
    Chế độ xinnan (`run.py`, Whisper tại máy) vẫn còn, nhưng không có hồ sơ bé/lộ trình.
  - Tự chạy khi đăng nhập: task `STLab xiaozhi server` → `run.ps1` → `run-live.ps1` (ghi nối `runtime/live.log` có dòng `[RUN-LIVE]`,
    bridge thoát thì tự chạy lại sau 10 s). Tuan chạy lại `server\install-autostart.ps1` 1 lần để Windows tự khởi động lại task khi lỗi.
  - Hồ sơ: `server/data/learners.json` (bo A1S → `kay` qua `devices.json`), giọng `server/data/voiceprints/` (phụ huynh đồng ý 2026-11-06); không lên git.
  - Gate offline: `test_free`, `test_curriculum`, `test_progress`, `test_roadmap`, `test_switch`, `test_topic` (chạy bằng `runtime\.venv\Scripts\python.exe -X utf8`).
  - CAD: nút âm lượng đang được đưa về **lưng** (cụm nút rời vol-pod, `cad/spec-vol-back.md`).
- 2026-11-06:
  - Sửa lỗi KEY4 không phản hồi: firmware cứng IP 192.168.1.47, máy lab đổi DHCP sang 192.168.1.65 → `firmware/xiaozhi-a1s/wifi-nvs.py` nạp thêm khóa NVS `ota_url`; đổi IP chỉ cần `python wifi-nvs.py --port COM5 [--server IP]`, không build lại. Đã đặt IP cố định trên modem Viettel 192.168.1.1 (Tuan, 2026-11-06): máy lab MAC 60:FF:9E:C8:B9:36 → **192.168.1.56** (sửa lại 12:35; bo nạp ota_url .56).
  - Chế độ nói chuyện rảnh tay (Tuan chọn, giọng bé chỉ ở máy lab, KHÔNG Gemini Live): chạm KEY4 1 lần = mở phiên; bé nói, máy chủ tự chốt câu (VAD im 600 ms), cô nói xong tự nghe tiếp; chạm KEY4 khi cô đang nói = ngắt lời; chạm khi đang nghe = kết thúc; im 30 s → cô chào tạm biệt và nghỉ; nói "tạm biệt cô"/"bye bye"/"goodbye"/"thôi nghỉ" = kết thúc. A1S (ESP32) không có khử vọng AEC nên không ngắt lời cô bằng giọng được – cần bản ESP32-S3.
  - Nguyên nhân chậm đã đo: Whisper ~2 s; Gemini thường 0,6–1 s nhưng ngẫu nhiên treo 21,8 s hoặc > 60 s. Sửa: `server/run.py` gọi Gemini REST SSE trực tiếp, gửi thêm 1 yêu cầu nếu sau 1,5 s chưa có chữ (tối đa 2), gặp 429 (hết hạn mức/phút) thì không gửi thêm, quá 12 s trả câu "Cô chưa nghe rõ, con nói lại nhé!". Gate `server/test_llm_latency.py` (12 lượt cách 4 s): 12/12, p50 0,94 s, max 2,35 s. Log mỗi lượt: dòng `[STLAB-T] llm_ttft=…`.
  - Firmware mới (KEY4 chạm) đã build + nạp COM5, khởi động sạch, OTA tới 192.168.1.65 OK. CHƯA thử giọng thật với chế độ mới – Tuan thử lần sau (cần khởi động lại máy chủ để nạp `run.py` + cấu hình mới).
  - Máy chủ tự bật khi đăng nhập Windows: Tuan chạy 1 lần `server\install-autostart.ps1` (gỡ: `-Remove`) – Claude không được quyền tự đăng ký.
- 2026-11-05 đêm (Tuan ngủ, Claude tự làm): bo A1S chạy xiaozhi + Wi-Fi tự nạp (`firmware/xiaozhi-a1s/wifi-nvs.py`), phát 2 kênh L=R (chờ Tuan nghe lại);
  máy chủ **song ngữ Việt–Anh**: Whisper small tại máy 127.0.0.1:8010, Gemini 3.1 flash-lite (gửi song song khi chậm), Edge `en-US-AvaMultilingualNeural` −12 %;
  test_server 17/17 + test_e2e (giả lập bo) PASS – trễ thả nút → tiếng đầu ~3,8–7,4 s, có lần 11 s do Gemini. CAD Cú Bông v1 2 loa (gate PASS), 3 bài học `lessons/`.
  **Sáng mai:** bật máy chủ `server
un.ps1` → giữ KEY4 nói thử tiếng Việt + tiếng Anh, nghe 2 loa; nghe `server/out-voice/*.mp3` chọn giọng; duyệt `cad/out/owl-preview.png`; cắt lớp + print.yaml cùng Tuan.
- 2026-11-05: **Tuan chọn dáng A – Cú Bông** (design/contact-sheet.png, design-spec.md): không màn hình, mắt = LED RGB đổi màu
  (nghe xanh dương / nói vàng / khen hồng / ngủ tím mờ), nút "nói" Ø50 trên đỉnh, **2 loa trái + phải ở 2 sườn** (Tuan đổi 2026-11-05; trước: 1 loa ở bụng), 3 màu (mơ/kem/bơ – tách part, hạn chế AMS).
  Cần: LED RGB (vd. WS2812) + chân trống trên Audio Kit (TODO); Tuan đo bo Audio Kit + độ sâu loa Ø52 trước khi CAD; pin hay USB: chưa chốt.
- 2026-11-05: tạo dự án, đọc chip qua esptool. Đang: firmware dò + bước 0 dáng sản phẩm.
- 2026-11-18: **bàn in thử S3 v2** theo góp ý Tuan (bezel đạt; ring/nắp nút/kẹp mic/khay ampli làm lại; hàn dây thẳng, không jack) – chi tiết `cad/README.md` mục "Bàn in thử v2". `print/plates-s3-test/p1-fit-test/p1-fit-test.3mf` PASS 73 ph 34,2 g (5 chi tiết + bộ thử chữ thập). Gate CAD thêm kiểm module thật + kẹp/khay không chạm vỏ. Cần băng xốp 2 mm (loa) + 2 vít M2.5 × 6 (khay ampli). Chờ Tuan in thử.
