# Spec: tự chỉnh ngưỡng khi dùng thật + chỉnh bằng giọng + script phân tích cho agent voice-tuner

Claude viết 2026-11-12. Tuan đồng ý: "máy chủ tự update ngưỡng khi testing thực tế", chỉnh bằng giọng, có agent chuyên phân tích.

## Module `server/live/tuning.py`
- `BOUNDS = {"barge_threshold": (0.6, 0.95), "barge_ms": (240, 1200), "agc_target_dbfs": (-24, -12), "agc_max_gain_db": (0, 24)}`;
  mặc định 0.85 / 600 / −18 / 18. Biến môi trường `STLAB_BARGE_THRESHOLD`/`STLAB_BARGE_MS` (nếu đặt) là giá trị khởi đầu khi CHƯA có file.
- `Tuning(path, now=time.time)`: đọc/ghi JSON `{values:{...}, history:[{t, param, old, new, reason}]}`; `get`, `set(name, v, reason="manual")`
  kẹp trong BOUNDS, ghi history, lưu ngay (ghi file tạm rồi đổi tên); tham số lạ → KeyError. Đường dẫn: `STLAB_TUNING_PATH`
  hoặc `server/data/tuning.json`.
- `on_barge_outcome(kind)`: `"false"` (ngắt nhầm) → threshold +0.03, ms +80; `"missed"` (bé phải chạm nút) → threshold −0.02, ms −40;
  cooldown 20 s giữa 2 lần tự chỉnh; reason `"auto:false"`/`"auto:missed"`. Đúng như `test_tuning.py`.
- `Agc(target_dbfs, max_gain_db)`: `process(pcm16 bytes) -> bytes` cùng độ dài; khuếch đại mượt (attack nhanh khi quá to, release chậm),
  không bao giờ tràn (giới hạn đỉnh), chỉ tăng gain khi khung > −50 dBFS (không kéo nền/im lặng lên), không giảm giọng to dưới mức gốc
  quá cần thiết. Đúng như test.

## Bridge `server/live/bridge.py`
- BargeGate đọc ngưỡng từ `Tuning` (mỗi phiên/mỗi khi đổi), thay cho hằng BARGE_THRESHOLD/BARGE_MS hiện tại.
- AGC: mic PCM (sau VadGate, trước `send_realtime_input`) qua `Agc` với giá trị từ Tuning. Áp dụng cho mọi bo.
- Phân loại sau mỗi `[BARGE]`:
  - **false** nếu trong 3 s sau đó không có input transcription nào, HOẶC transcription giống câu cô vừa nói (tỷ lệ giống ≥ 0,6, so
    sau khi bỏ dấu/hoa thường – tiếng vọng bị nhận thành lời).
  - **missed**: thiết bị gửi `abort` (bé chạm nút) trong lúc cô đang nói VÀ VadGate thấy giọng người trong 2 s trước đó mà BargeGate chưa ngắt.
  - Gọi `tuning.on_barge_outcome(...)`; khi giá trị đổi, log `[TUNE] barge <kind> -> barge_threshold X barge_ms Y`.
- **Chế độ kỹ thuật** (người lớn): transcription chứa "chế độ kỹ thuật" (so bỏ dấu: "che do ky thuat") → `tech_mode = True` trong
  10 phút, cầu nối báo Gemini "[tech mode on]…". Công cụ Gemini:
  - `tech_tune(param, action)` – param: `mic` (agc_target_dbfs), `barge` (barge_threshold + barge_ms), `gain` (agc_max_gain_db);
    action: `up` / `down` / số cụ thể. "tăng độ nhạy mic" = agc_target +2 dB; "khó ngắt lời hơn" = barge +0.03/+80 ms. Trả giá trị mới.
  - `tech_report()` – đọc giá trị hiện tại + 3 lần đổi gần nhất.
  - Khi `tech_mode` False: 2 công cụ trả lỗi "chưa mở chế độ kỹ thuật" và KHÔNG đổi gì. Log `[TUNE] voice ...`.
  - Thêm 3–4 dòng tiếng Anh vào `prompt-teacher.md` (mục TECH MODE): chỉ dùng khi người lớn mở, đọc số ngắn gọn, xong quay lại bài.

## Script `server/tune/analyze.py` (cho agent voice-tuner)
- `python analyze.py [--log runtime/live.log] [--since HH:MM] [--json]`: đọc log (chịu được dòng lẫn byte NUL / mã hóa hỏng – bỏ qua),
  đếm `barges`, `tune_changes`, `music_plays`, phiên (`sessions` theo "thiet bi ket noi"/"ngat"), `levels` {voice_dbfs_median, noise_dbfs_median,
  n} từ `[LIVE-LEVEL]`, `metrics` từ `[LIVE-METRIC]`, `tuning` hiện tại (đọc tuning.json nếu có), `suggestions` (list chuỗi tiếng Việt,
  vd "giọng trung vị −24 dBFS < −20 → tăng agc_target" / "barge > 3 lần/phút → có thể tiếng vọng").
- Không có `--json`: in báo cáo ngắn tiếng Việt.

## Gate (Claude viết, KHÔNG sửa)
`runtime\.venv\Scripts\python.exe -X utf8 test_tuning.py` PASS + các gate cũ PASS:
`test_detour test_full_duplex test_vad_near test_free test_curriculum test_progress test_roadmap test_switch test_topic test_seed_lessons`.

## Được sửa
`server/live/tuning.py` (mới), `server/live/bridge.py`, `server/live/duplex.py` (nếu cần cho ngưỡng động, test_full_duplex vẫn PASS),
`server/tune/analyze.py` (mới), `server/prompt-teacher.md`, `server/README.md`.

## Không làm
- Không khởi động lại máy chủ đang chạy, không chạy test_live*, không đụng `server/data/*` (trừ khi test tạo file tạm), firmware.
- Không gửi log/lời bé ra dịch vụ ngoài. Không commit.
