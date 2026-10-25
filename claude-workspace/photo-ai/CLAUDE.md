# photo-ai – tự sửa ảnh sự kiện cho Facebook

**TẠM DỪNG (Tuan 2026-10-25):** tập trung CAD + Blender; dùng lại khi LightCraft có bản tạo ảnh AI. Không tự làm tiếp.

Ảnh từ máy ảnh (Nikon D7100, JPEG) + điện thoại → lọc → LightCraft chỉnh màu → xuất Facebook.
Nguồn và license: `docs/COMMUNITY.md` mục "Ảnh AI – LightCraft".

## Quy tắc
- **Ảnh gốc chỉ đọc.** Làm việc trong thư mục riêng (`<nguon>-edit/`); không ghi gì vào thư mục nguồn.
- **Không tự xóa ảnh.** Lọc chỉ chia nhóm; Tuan duyệt nhóm `xem-lai` / `loai`.
- **Đưa Tuan ảnh, không đưa file `.txt`.** Nhóm = thư mục ảnh xem trước; Tuan kéo ảnh giữa các thư mục.
- **Riêng tư:** ảnh có trẻ em → xuất luôn `removeLocation=true` (ảnh D7100 đều có GPS);
  **không giữ Artist/Copyright** (Tuan quyết 2026-10-21) → `metadata=none`. Chỉ đăng ảnh gia đình đã đồng ý.
- LightCraft: **không dùng `develop.auto`** (ảnh ngược sáng bị xám, đục). Dùng preset.
  `app.export path=` phải là file; nhiều ảnh dùng `dir=` + `ids=`.

## Bước 1 – lọc (`scripts/cull.py`)
```bash
uv run scripts/cull.py <thu-muc-anh> --out <nguon>-edit/cull
```
- Ra `cull/{dat,xem-lai,loai,trung-lap}/` (ảnh xem trước 2048 px, không EXIF) + `tong-quan-<nhom>.jpg` (kèm lý do).
  Chạy lại khi thư mục nhóm đã có ảnh → phải `--force` (xóa cả ảnh Tuan đã kéo).
- YuNet (OpenCV) tìm mặt → **nhòe**: phương sai Laplacian vùng mặt (ảnh 3000 px, thu về 160 px),
  so với trung vị cả loạt → **mắt nhắm**: `eyeBlinkLeft/Right` của MediaPipe Face Landmarker trên mặt đã cắt.
- Mặt chính = cạnh ≥ 45% mặt lớn nhất (bỏ người phía sau, ảnh in trên túi quà).
- Chụp liên tiếp: pHash ≤ 12 và cách ≤ 4 s → một loạt, giữ ảnh tốt nhất, còn lại `trung-lap`.
- Ngưỡng (hiệu chỉnh 2026-10-21 trên 24 mặt, ảnh 20/10): nhắm ≥ 0,80 loại, ≥ 0,45 xem lại
  (0,5–0,8 thường là cười híp/khóc); nhòe < 30% trung vị loại, < 55% xem lại.
- Giới hạn: mặt nghiêng/quay đi/quá nhỏ → không thấy mặt → `xem-lai`.

## Bước 2 – chỉnh màu + xuất + QA (`scripts/develop.py`)
```bash
uv run scripts/develop.py <thu-muc-anh> --list <nguon>-edit/cull/dat --out <nguon>-edit/xuat
```
- Mỗi ảnh: `lightcraft-cli render` (không cần thư viện), preset `presets/outdoor-event.json`
  (JSON phẳng) truyền bằng `--set k=v`. **`render --settings` không áp file này** (thử 2026-10-21: ảnh ra như gốc).
- Xuất Facebook: cạnh dài 2048 px, sRGB, quality 90, `removeLocation=true`, `metadata=none` (xóa hết EXIF, vẫn giữ ICC sRGB – đã kiểm).
- QA (`qa.csv`): cạnh dài, còn GPS, ICC sRGB, preset có áp (chênh với gốc ≥ 1/255), cháy sáng/bết đen
  > 3% **và tăng hơn gốc** > 1 điểm % (trời cháy sẵn trong ảnh gốc thì không báo). `contact-<n>.jpg`: 40 ảnh/trang.
- Đã có file xuất thì bỏ qua; `--force` để xuất lại. 97 ảnh ≈ 90 s (4 luồng).

## Bước 3 – chọn kiểu màu trên Toolhub > **Sửa ảnh** (cách chính)
- Nhập thư mục ảnh gốc → chọn một tấm → tích kiểu màu (preset STLab / LUT phim / XMP), bật "Nâng sáng người",
  kéo độ mạnh → so sánh **Gốc | Đã áp** (giữ Space: ô phải hiện gốc). Ưng rồi bấm **Áp dụng cho tất cả**
  → `develop.py --look <id> --strength <0..1> [--local]` chạy nền → `<nguon>-edit/xuat-<kieu>[-local]-<%>/` + QA + contact.
- Ảnh xử lý = `cull/dat/` nếu có (nhóm Tuan đã duyệt), không thì cả thư mục nguồn.
- Xem trước 1600 px trong `<nguon>-edit/lab/preview/`; xuất thật cho cùng kết quả (chênh ~2/255, đã kiểm).
- Logic dùng chung ở `scripts/looklib.py`: under/over + trộn theo độ mạnh (trang web chồng ảnh bằng opacity).

## Thử kiểu màu bằng dòng lệnh (`scripts/looks.py`, PhotoCraft)
```bash
uv run scripts/luts.py --default                     # HaldCLUT cộng đồng -> luts/*.cube (33³)
uv run scripts/looks.py <thu-muc-anh> DSC_3043 DSC_3110 --out <nguon>-edit/looks [--only portra160nc ...]
```
- Kiểu màu khai báo trong `presets/looks.json`: `base` (preset STLab), LUT (`hald`/`cube`, áp lên base bằng
  PhotoCraft Color Lookup), `xmp` (preset Lightroom, LightCraft áp lên ảnh gốc). Ra `so-sanh-<anh>.jpg` có nhãn.
- PhotoCraft sửa cục bộ (thử 2026-10-21, ổn): `select.subject` → `select.modify.feather {radius:40}` →
  `image.adjustments.shadowsHighlights {shadowAmount:25,...}` + `curves [[0,0],[128,138],[255,255]]` → `select.deselect`
  → `colorLookup`. Mặt ngược sáng sáng và nổi khối hơn, nền giữ nguyên.
- PhotoCraft cần đường dẫn Windows (`D:/...`) và **chép EXIF từ ảnh vào** → chỉ đưa ảnh đã xóa metadata.
- Nguồn + license: `docs/COMMUNITY.md` mục "LUT / preset cộng đồng cho ảnh".

## Phóng ảnh nhỏ – Real-ESRGAN (giai đoạn 4, cài 2026-10-22)
```bash
tools/realesrgan/realesrgan-ncnn-vulkan.exe -i in.png -o out.png -n realesrgan-x4plus -s 4
```
- Chạy GPU (Vulkan, GTX 1660 SUPER): 800→3200 px ≈ 8 s. Tải lại zip theo `tools/SHA256SUMS` (release Real-ESRGAN v0.2.5.0).
- Thử 2026-10-22 (`D:/temp/102D7100-edit/upscale-test/so-sanh-phong-anh.jpg`): nét hơn bicubic rõ, nhưng da mịn kiểu sáp,
  chữ bị viền đen → **chỉ dùng cho ảnh điện thoại/ảnh cắt có cạnh dài < 2048 px**, không áp cho ảnh D7100.
- Chưa nối vào `develop.py`. TODO: rembg (`birefnet-general` hoặc `bria-rmbg`) – môi trường uv riêng.

## Model (không đưa lên git, kiểm bằng `models/SHA256SUMS`)
- `face_detection_yunet_2023mar.onnx` – opencv_zoo @ `yunet-zoo-commit.txt`, MIT.
- `face_landmarker.task` – MediaPipe float16/1, Apache-2.0.
