# spec v0.4.0 – ghi clip AVI (MJPEG) khi có chuyển động

allow: `main/**`, `sdkconfig.defaults`, `README.md`, `test_v04.py`, `check_v04.py`
Nguồn ý tưởng: s60sc/ESP32-CAM_MJPEG2SD (AGPL-3.0) – **CHỈ lấy ý tưởng, KHÔNG chép code**. Định dạng AVI theo tài liệu
OpenDML/RIFF chuẩn (Microsoft AVI RIFF File Reference), tự viết.

## Giữ nguyên (v0.3.1 đang chạy ổn)
- Mọi thứ của spec-v03.md / spec-v031.md: nguyên tắc ô "khung mới nhất" đếm tham chiếu, task ghi thẻ riêng qua queue,
  không format thẻ, chỉ ghi trong `/sdcard/stlab-cam/`, dọn thư mục ngày cũ khi < 10 % hoặc < 200 MB, không thẻ không treo,
  thử mount lại 30 s, giới hạn nhiệt (tự hạ fps) của v0.3.1, OTA + rollback, bảng phân vùng, chân camera.
- Ảnh JPEG sự kiện `stlab-cam/YYYYMMDD/HHMMSS.jpg` vẫn ghi như cũ.

## Mới
1. Bộ đệm trước sự kiện trong PSRAM: vòng tròn giữ khung JPEG của `pre_s` giây gần nhất (mặc định 3 s) ở tốc độ ghi `clip_fps`
   (mặc định 5, khoảng 1–10). Chỉ chạy khi `motion=1` VÀ `clip=1` VÀ `sd_ok`. Giới hạn bộ đệm ≤ 2 MB PSRAM (đủ thì bỏ khung cũ).
2. Sự kiện chuyển động (khi `clip=1`) → task ghi thẻ mở `stlab-cam/YYYYMMDD/HHMMSS.avi` (chưa có giờ → `stlab-cam/boot/<s>.avi`),
   ghi khung trong bộ đệm rồi tiếp khung mới tới khi hết chuyển động `post_s` giây (mặc định 5, khoảng 2–30); tối đa `clip_max_s`
   60 s/clip. Chuyển động mới trong lúc đang ghi → kéo dài clip (không mở file mới).
3. AVI MJPEG chuẩn: RIFF 'AVI ', hdrl (avih + strl/strh 'vids' 'MJPG' + strf BITMAPINFOHEADER), movi ('00dc' từng khung,
   đệm chẵn byte), idx1 ở cuối. Ghi header giữ chỗ lúc mở, ghi lại số khung/kích thước/fps thật khi đóng.
   Rút thẻ/lỗi giữa chừng → đóng file nếu được, `sd_ok=false` như v0.3; không treo.
   Ghi theo khối (đệm ghi ≥ 16 KB) để thẻ không làm chậm; nếu queue ghi đầy → bỏ khung (đếm `clip_drop`), không chặn camera/HTTP.
4. Tham số qua `/control` (ngoài khoảng → 400): `clip` 0/1 (mặc định 0), `clip_fps`, `pre_s` 0–5, `post_s`. Lưu NVS như các tham số cũ.
5. `/status` thêm: `clip` (0/1), `clip_rec` (bool đang ghi), `clip_count`, `clip_drop`.
6. `/events`: mục có clip thêm `"clip": "stlab-cam/20261109/140322.avi"` (hoặc null). `GET /sd?f=` cho phép thêm đuôi `.avi`
   (Content-Type `video/x-msvideo`), giữ kiểm `..`/`\`/ký tự lạ như cũ. File lớn → gửi theo khối (httpd_resp_send_chunk).
7. UI (`index.html`): trong khối "Chuyển động" thêm công tắc "Ghi clip" + 2 ô Trước/Sau (giây); danh sách sự kiện có link clip.
8. Version 0.4.0.

## Gate (chạy trước khi báo xong)
- `build.ps1` build PASS, không warning mới trong `main/`.
- `check_v04.py` (không cần mạch): kiểm tĩnh mã có idx1/avih/'00dc'/không `format_if_mount_failed = true`, `/sd` chặn `..`;
  + unit test bộ ghi AVI nếu tách được hàm thuần (ví dụ viết lại logic header bằng Python và so cấu trúc với file mẫu).
- `test_v04.py` (mạch thật, qua `stlab-cam.local`): /status có trường mới; `/control?clip=1` OK, ngoài khoảng 400;
  KHÔNG có thẻ → clip_rec luôn false, không lỗi, stream vẫn chạy (Tuan chưa có thẻ TF). Phần có thẻ: đánh dấu SKIP + in hướng dẫn thử tay.
- Nạp lên mạch bằng OTA (`ota.py`, khóa trong biến môi trường `STLAB_CAM_OTA_KEY`), chạy test_v04.py + test_v031.py PASS.
  Không có mạng tới mạch → báo lại, KHÔNG bảo Tuan nạp USB.

## Cấm
- Không chép code MJPEG2SD (AGPL). Không thêm thư viện ngoài component IDF. Không đổi bảng phân vùng. Không ghi khóa/mật khẩu vào file/log.
