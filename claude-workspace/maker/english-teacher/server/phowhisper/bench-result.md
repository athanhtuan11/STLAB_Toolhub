# Ket qua do ASR (2026-11-07)

CPU i5-13400F, cpu_threads=8, int8, beam 1, initial_prompt cua whisper-local, sau 1 lan lam nong.
Am thanh = Edge TTS (HoaiMy, NamMinh; toc do x1.25 va cao do x1.25 doi bang ffmpeg vi giong vi-VN tu choi rate/pitch) - GIA LAP, KHONG phai giong tre that. 24 cau x 6 bien the.

| Mo hinh | ms TB/cau | ms p95 | WER % | CER % | dung nguyen cau % | cau ngan dung (Da/Vang a/Co ne/Hong) | n |
|---|---|---|---|---|---|---|---|
| Whisper small (hien tai, lang tu do) | 2558 | 4061 | 29.0 | 17.9 | 47.2 | 0/24 (0%) | 144 |
| PhoWhisper-small | 1288 | 2141 | 48.6 | 39.2 | 42.4 | 6/24 (25%) | 144 |
| PhoWhisper-medium | 3017 | 3820 | 22.4 | 19.8 | 54.2 | 8/24 (33%) | 144 |
