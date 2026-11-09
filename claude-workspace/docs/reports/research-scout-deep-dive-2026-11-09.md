# Research scout – đào sâu 2026-11-09

Ghi chú phương pháp: số liệu lấy từ trang nguồn qua WebFetch (tóm tắt tự động); mục nào không thấy trong nguồn ghi TODO. Ngày pushed_at lấy từ api.github.com.

## Tóm tắt
1. Quadruped: Sesame (8 servo MG90, ~50-60 USD, Apache-2.0, 5k sao) hợp học sinh hơn Leika (12 servo 20-35 kg, MIT, 93 sao, phức tạp). Khuyến nghị làm thử Sesame.
2. MJPEG2SD chạy ESP32-S3 + OV3660, có SD, motion, audio, nhưng AGPL-3.0: chỉ nên tham khảo ý tưởng, không copy code vào firmware esp32-s3-cam nếu không muốn AGPL.
3. stackchan-mcp xác nhận xiaozhi có MCP; hữu ích làm ý tưởng điều khiển, không có gì cho bài học tiếng Anh. ESPHome 2026.11 thêm i2s_audio full duplex + ES7210 TDM chuẩn bị AEC: theo dõi cho bản S3 codec.
4. LeRobot v0.7.0: nhiều model lớn, cần GPU; có remote inference (policy-server) nên PC yếu vẫn lái robot được nếu có máy GPU khác. Bài blog không nêu giá/arm rẻ nhất: theo dõi.
5. F3D 4.0 đọc được .FCStd (hữu ích khi FreeCAD GUI crash) – cần thử headless trên máy mình; BMCU-C chỉ thông tin (không áp dụng cho AMS lite), ESP32-S31 chạy Linux: bỏ qua.

## 1. Quadruped: Sesame vs Leika

### Sesame (dorianborian/sesame-robot)
- Là gì: quadruped mini ESP32, mặt OLED, web UI + JSON API + serial CLI. https://github.com/dorianborian/sesame-robot
- License Apache-2.0; ~4993 sao; pushed 2026-11-08 (api.github.com/repos/dorianborian/sesame-robot).
- BOM: 8 servo MG90 180°, 2 servo/chân; MCU khuyến nghị Lolin S2 Mini (hoặc board Sesame Distro V3); nguồn 5 V 3 A (USB-C PD hoặc pin + buck); tác giả ước tính 50-60 USD phần cứng. (cùng nguồn)
- In: có STL (tác giả đã in + chạy thật → dùng làm chuẩn thông số), thiết kế cho PLA; hướng dẫn `hardware/printing/README.md`: infill 8-10 %, 2 wall, honeycomb; chỉ Top Cover cần support (tô tay), khớp chân không support, Top Cover nên brim ngoài.
- Đo trực tiếp STL (commit bb87021, 2026-11-08, trimesh): toàn bộ chi tiết ≤ 79,2 mm → vừa bàn A1 256x256 mm thoải mái, 1 bàn in được cả bộ.
  - Internal-Frame-v121 79,2 x 15,7 x 68,1 mm; Bottom-Cover-v121 79,2 x 7,3 x 54,2 mm; Top-Cover-Enclosed-v117 79,2 x 38,2 x 37,4 mm (mesh không kín, cần sửa khi slice) / Cat-v100 79,2 x 43,1 x 37,6 mm / No-Ears-v100 79,2 x 33,7 x 37,4 mm.
  - Khớp L1/L2/R1/R2: 20,3 x 30,5 x 49,5 mm (mỗi cái 5,2 cm³); L3/L4/R3/R4: 9,5 x 19,0 x 58,4 mm (4,7 cm³).
  - Thể tích đặc 100 % cả bộ (frame + bottom + 8 khớp + 1 top cover) ≈ 108 cm³ (top Cat) → cận trên ~137 g PETG (1,27 g/cm³); thực tế infill 10 % nhẹ hơn nhiều: TODO cân bằng slice.py.
- BOM gốc (`hardware/bom/README.md`): 8x MG90S **loại 180°** (tác giả nhấn mạnh, loại 360° không chạy), OLED SSD1306 0,96" I2C, công tắc KCD1, ESP32-S2 Mini (Lolin) + perfboard 5x7 cm + buck 5 V/3 A, ốc M2x5 tự ren ~40, M2.5x5 máy x10 (bắt horn servo), pin Bambu Lab 14500 7,4 V 800 mAh (vừa hốc khung v121). Nguồn ≥ 5 V/3 A.
- An toàn: pin Li-ion 2S 7,4 V – không cắt giắc gốc của pin, làm dây chuyển XT30/JST; đi qua công tắc + buck trước khi vào rail; bọc co nhiệt mọi mối hàn.
- Độ chín: firmware mô tả "basic implementation"; có Sesame Studio (animation), simulator, ML tools, Discord hỗ trợ. 171 commit.
- Nhược: 8 DOF, chỉ 2 khớp/chân, đi đơn giản; MG90 hay nóng/mòn bánh răng nhựa (nhận xét của mình, chưa có nguồn).

### Leika (runeharlyk/SpotMicroESP32-Leika)
- Là gì: nền tảng quadruped ESP32 với web controller (SvelteKit) và mô phỏng MuJoCo; FreeRTOS, IK, gait, IMU fusion. https://github.com/runeharlyk/SpotMicroESP32-Leika
- License MIT; 93 sao; pushed 2026-11-08; 1624 commit; Releases trống; web flasher cho firmware dựng sẵn.
- BOM (https://raw.githubusercontent.com/runeharlyk/SpotMicroESP32-Leika/master/docs/1_components.md): 12 servo 20-35 kg (tối thiểu MG996R, khuyến nghị CLS6336HV; bản Leika Mini dùng MG92B), PCA9685, ESP32-S3 N8R8 (khuyến nghị), buck LM2596/XL4015, pin 7,6-8,4 V (tác giả dùng 4x18650 2s2p), ốc: M2x8 84, M3x8 92, M3x20 64, vòng bi 625ZZ x12. Không có giá: TODO.
- In: thư mục hardware/ có CAD, danh sách STL/kích thước: TODO. Đây là thiết kế Spot Micro (thân to), khả năng cần chia bàn: TODO.
- Độ khó: PlatformIO + Node + pnpm + protoc + nanopb; suy luận: trung bình-cao.
- Rủi ro an toàn: pin Li-ion 18650 2s2p + 12 servo công suất lớn, dòng đỉnh cao: cần cầu chì, BMS, buck đủ A (TODO tính dòng).

### So sánh và khuyến nghị
| Tiêu chí | Sesame | Leika |
|---|---|---|
| Servo | 8x MG90 | 12x 20-35 kg |
| Chi phí | ~50-60 USD (tác giả) | TODO, rõ ràng cao hơn |
| Lớp 6-12 | hợp (lớp 6 cần kèm) | hợp lớp 10-12 / giáo viên |
| Phần mềm | Arduino IDE | PlatformIO+Node |
| Hệ sinh thái | 5k sao | 93 sao nhưng mô phỏng tốt |

Khuyến nghị: LÀM thử Sesame (in 1 bộ bằng PETG, đo kích thước; tự vẽ lại nếu đăng bán theo quy tắc "model RE chỉ đọc thông số"). Leika: THEO DÕI, chỉ lấy phần web UI/IK làm tham khảo. Đánh đổi: Sesame dễ nhưng ít khả năng mở rộng; PETG cứng hơn PLA nên khe lắp cần kiểm lại; mặc định nhóm dùng PETG còn tác giả thiết kế cho PLA.

## 2. ESP32-CAM_MJPEG2SD (s60sc)
- https://github.com/s60sc/ESP32-CAM_MJPEG2SD ; AGPL-3.0; 1781 sao; pushed 2026-11-07; 950 commit; Releases trống.
- Hỗ trợ ESP32 và ESP32-S3 (S3 nhanh gấp ~2 do PSRAM); OV3660 nằm trong danh sách camera hỗ trợ; ghi chú: OV3660 điện áp cấp quá cao so với regulator nội nên nóng, cần tản nhiệt. Khớp với hiện tượng vỏ ~50 °C của esp32-s3-cam.
- Tránh board ghi "ESPS3 RE:1.0".
- SD: AVI theo ngày/giờ/size/fps, âm thanh WAV trong AVI, time-lapse, dashcam; FTP/HTTPS/WebDAV tải file.
- Motion: so sánh ảnh xám nhỏ trên camera, chỉnh độ nhạy, không dùng với size > SXGA; hỗ trợ PIR/radar.
- Audio: mic I2S (INMP441) 16-bit mono 16 kHz, PDM chỉ S3; intercom 2 chiều trên S3.
- Khác: MQTT/Home Assistant, Telegram, RTSP.
- Tái dùng cho esp32-s3-cam: ý tưởng cấu trúc ghi SD (AVI + thư mục theo ngày), cách motion; khuyến nghị THEO DÕI/THAM KHẢO. Vì AGPL-3.0, copy code vào firmware của mình buộc phát hành mã nguồn khi phân phối/dịch vụ mạng; nếu firmware chỉ dùng nội bộ lab thì ít rủi ro (theo quy tắc license: ghi chú, không chặn, đưa vào bảng "xem lại khi thương mại"). Đánh đổi: dùng thẳng MJPEG2SD tiết kiệm công viết SD/audio nhưng mất firmware OTA + motion đã tự viết; chọn tùy việc: nếu thẻ TF là ưu tiên, thử nạp MJPEG2SD lên board để so (TODO thử).

## 3. stackchan-mcp và hệ sinh thái MCP của xiaozhi
- https://github.com/kisaragi-mochi/stackchan-mcp : cổng MCP cho robot M5Stack StackChan (M5 CoreS3, ESP32-S3 16 MB flash 8 MB PSRAM); 178 sao, 67 fork; 73 issue mở; 220 commit; ngày commit cuối: TODO (không thấy).
- License: MIT cho gateway và phần lớn firmware; file SCServo_lib GPL-3.0 là tùy chọn, bật lên thì firmware thành GPL-3.0.
- Cách dùng xiaozhi: firmware là git subtree của xiaozhi-esp32 (qua fork) + board StackChan; gateway có MCP server stdio cho LLM client, MCP client WebSocket phía ESP32, HTTP server nhận ảnh; thiết bị tìm gateway qua mDNS, xác thực bearer token.
- Công cụ: điều khiển đầu 2 servo SCS0009, camera GC0308 320x240, cảm ứng, biểu cảm, `say` (VOICEVOX mặc định, Fish Audio/ElevenLabs là cloud), `listen` (faster-whisper hoặc OpenAI, mặc định tiếng Nhật).
- Liên quan english-teacher bản S3: xác nhận xiaozhi hỗ trợ MCP phía thiết bị để LLM gọi công cụ (đổi biểu cảm, hiện chữ, camera). Không có giáo trình/chế độ trẻ em. Cần gateway Python chạy ở máy chủ lab (đã có bridge Gemini). Tài liệu MCP chính thức của xiaozhi-esp32: TODO (chưa đọc).
- Khuyến nghị: THEO DÕI; khi làm bản S3, đọc tài liệu MCP của xiaozhi và thử đăng ký 1 tool (ví dụ hiện từ vựng lên màn hình). Đánh đổi: thêm tính năng cho bé nhưng thêm điểm hỏng; luôn có phụ huynh cạnh bé nên không cần bộ lọc theo ghi chú dự án.

## 4. LeRobot v0.7.0
- Nguồn: https://huggingface.co/blog/lerobot/lerobot-release-v070
- Mới: can thiệp ngôn ngữ khi chạy (/subtask, /vqa, /autosteer); stream dataset từ Hub/Bucket/LanceDB không cần tải; huấn luyện FSDP2/HSDP, FP16, EMA, Trackio (thay W&B); ACT train nhanh 2,8x trên H100 và 3,3x trên A100 nhờ augment ảnh trên GPU; world action models (Cosmos 3, FLUX 3 Action, ...); VLA mới (G0.5 license phi thương mại...); `lerobot-policy-server` chạy policy trên máy GPU, robot chỉ lo cảm biến/động cơ (module async_inference cũ bị gỡ); simulator thống nhất; phần cứng mới: I2RT YAM, Seeed reBot B601, Unitree G1.
- SO-101: bài chỉ nhắc ở checkpoint (FLUX 3 Action, G0.5), không nói có phải mới; arm rẻ nhất: bài không nêu; giá: không có. Yêu cầu tối thiểu: TODO (bài nêu GPU datacenter cho model lớn, không áp dụng cho nhóm nhỏ).
- Khả thi STLab (máy yếu): train cần GPU, nên không tự train; chỉ khả thi nếu thuê GPU đám mây hoặc dùng policy-server trên máy khác (TODO tìm phương án chi phí). Khuyến nghị: THEO DÕI; nếu làm, bắt đầu từ SO-101 (TODO kiểm giá/bộ in trên repo SO-ARM100) và chỉ teleoperation + ghi dataset, chưa train. Đánh đổi: cộng đồng lớn nhưng tốn thời gian/GPU, ít hợp lớp 6.

## 5. ESPHome 2026.11.0 beta
- https://beta.esphome.io/changelog/2026.11.0.html (chỉ đọc được 100000/441193 ký tự đầu; mục Breaking Changes chưa thấy: TODO đọc tiếp).
- micro_wake_word: đặt model trong RAM nội (#20529), chọn core cho tác vụ inference (#20126), thời lượng buffer thu cấu hình được (#20942).
- voice_assistant: timeout bắt đầu phát TTS cấu hình được (#18707).
- i2s_audio: speaker `keep_alive` chống tiếng pop (#15565), full duplex (#19959), hỗ trợ ESP32-S31 (#20115).
- es7210: TDM chuẩn bị cho acoustic echo cancellation (#18954); es8388: cấu hình DAC/ADC ban đầu (#16342).
- Liên quan: hướng "voice + smart home" và bản S3 codec của english-teacher (ES8388/ES7210 là codec phổ biến; AEC đang được chuẩn bị). Khuyến nghị: THEO DÕI, đợi bản stable rồi thử satellite voice trên board S3 có codec. Đánh đổi: ESPHome mạnh về Home Assistant nhưng tách khỏi xiaozhi; chọn 1 stack cho 1 thiết bị.

## 6. FreeCAD / F3D
- F3D 4.0 hỗ trợ file FreeCAD (.FCStd) (https://blog.freecad.org/2026/11/05/f3d-updated-now-supports-freecad-files/); bản mới nhất v4.0.1, 2026-10-31 (https://api.github.com/repos/f3d-app/f3d/releases/latest). FreeCAD dùng F3D nội bộ tạo thumbnail STEP; Manyfold dùng F3D xem trước FCStd.
- Bài không nói gì về headless/offscreen, màu, giới hạn: TODO. (F3D có chế độ xuất ảnh dòng lệnh theo hiểu biết chung, nhưng chưa xác nhận từ nguồn; trang docs thử đọc bị 404.)
- FreeCAD v26.3: giai đoạn sửa lỗi trước phát hành, RC2 ngày 2026-10-18, còn 2 blocker (giảm 3 so với tuần trước), chưa có ngày phát hành; có weekly-2026.11.04; màu giờ xuất được sang STEP/IGES (https://blog.freecad.org/2026/11/04/wip-wednesday-4-november-2026/).
- Khuyến nghị: LÀM thử nhỏ: cài F3D 4.0.1, chạy `f3d` trên 1 file .FCStd của dự án, kiểm tra ảnh render ra file không cần GUI FreeCAD và màu giữ không. Nếu được, thêm vào bước duyệt bằng ảnh. Đánh đổi: nhanh, không crash, nhưng không thay được freecadcmd; .FCStd tạo bằng CLI không có gui_from có thể mất màu. Chưa nâng lên 26.3 cho tới khi ra bản chính thức (theo dõi).

## 7. BMCU-C-PJARCZAK
- https://github.com/jarczakpawel/BMCU-C-PJARCZAK : firmware cộng đồng cho board đệm filament BMCU 370C (Hall) dùng cho A1/A1 mini/P1S; 755 sao; 32 commit; license: TODO (không thấy); ngày commit cuối: TODO.
- BMCU không phải AMS Lite; máy phải đặt chế độ AMS. A1 firmware 01.05.00.00-01.07.02.00: chạy được; từ 01.08.00.00 trở lên bị lỗi tương thích chặn slice (tác giả gợi ý OrcaStudio).
- Rủi ro: Bambu hạn chế qua firmware; nạp/cắm khi máy bật có thể hỏng board; không bảo hành; không cập nhật firmware máy khi đang gắn.
- Khuyến nghị: BỎ. Tuan đã có AMS lite và ưu tiên hạn chế AMS (part đơn sắc), rủi ro hỏng máy/khóa firmware lớn hơn lợi ích.

## 8. Hackaday: Linux trên ESP32
- https://hackaday.com/2026/11/07/proper-linux-on-an-esp32/ : chip Espressif ESP32-S31 (RISC-V lõi kép, Wi-Fi 6, có MMU nên chạy Linux đầy đủ, không phải nommu); đang port kernel 6.x; bài không nêu RAM, hiệu năng thấp; comment độc giả nói 16-32 MB RAM (chưa kiểm chứng).
- ESPHome cũng đã bắt đầu hỗ trợ ESP32-S31 (mục 5).
- Khuyến nghị: BỎ (theo dõi nhẹ). Chưa có ứng dụng cho dự án hiện tại; đáng nhìn lại khi S31 có dev board dễ mua và codec audio.

## Bảng ưu tiên
| # | Việc | Quyết định | Công sức | Lý do |
|---|---|---|---|---|
| 1 | F3D xem .FCStd headless | Làm thử | Thấp | Giải quyết GUI crash, thêm ảnh duyệt |
| 2 | Sesame quadruped (in 1 bộ, đo) | Làm thử | Trung bình | Rẻ, 8 servo, Apache-2.0 |
| 3 | MJPEG2SD đối chiếu SD/motion cho esp32-s3-cam | Theo dõi / thử nạp để so | Thấp-TB | Hữu ích nhưng AGPL |
| 4 | MCP xiaozhi cho english-teacher S3 | Theo dõi | Thấp | Chờ có board S3 codec |
| 5 | ESPHome 2026.11 voice | Theo dõi (đợi stable) | Thấp | AEC/full duplex đang hình thành |
| 6 | LeRobot v0.7.0 | Theo dõi | Cao | Cần GPU, chưa có giá arm |
| 7 | Leika | Theo dõi | Cao | 12 servo nặng, phức tạp |
| 8 | BMCU-C | Bỏ | - | Rủi ro máy, đã có AMS lite |
| 9 | ESP32-S31 Linux | Bỏ | - | Chưa liên quan |
