# Phiên tự chạy 2026-11-28 04:30 – tăng tốc chuỗi CAD (Tuan duyệt 2026-11-27 19:2x: "đồng ý", "tự chọn mục bạn thấy tốt nhất")

Bạn là phiên Claude Code chạy KHÔNG NGƯỜI TRÔNG trong `D:\04_Stlab\04_STLAB_Toolhub\claude-workspace`. Tuan đang ngủ, không hỏi được.
Đọc trước: `docs/reports/Tăng tốc chuỗi CAD tự động.md` (13 đề xuất), skill `stlab-workflow`, `mechanical-design` mục "Đầu ra file CAD".
Dự án thử: `maker/english-teacher/cad` (lệnh `python run_v3.py [--slice]`, gate phải PASS trước và sau mỗi việc).

## Quyết định Tuan đã duyệt
- Vòng sửa nhanh chỉ xuất **3MF lắp ráp** (mỗi part 1 object có tên, mm, đúng vị trí lắp). `.sc` + `.step` + `.blend` chỉ xuất khi
  **phát hành** (cờ `--release`, hoặc trước khi báo Tuan đo/duyệt). Sửa skill `mechanical-design` + `stlab-workflow` bước 8 + memory
  `cad-file-solidcraft-mac-dinh.md` cho khớp (không để memory và skill nói khác).

## Số đo ban đầu (2026-11-27, máy này)
- 16 part, tổng 78 568 tam giác (shell-front 21 608, 2 vành loa 10 7xx). STEP 89 MB, xuất CAD 38 s, dựng 12 s, assembly 4 s, gate 5 s.
- Cắt lớp 5 bàn 22–40 s, `peak_rss_mb` mỗi bàn 142–542 MB (C_speakers lớn nhất) → song song 2–3 bàn an toàn.

## Việc, theo thứ tự (làm tới đâu commit tới đó; hết token thì dừng sạch – không để file dở)
1. **Chế độ nhanh 3MF** trong `tools/cad-export/export_cad.py`: `--fast` ghi `<ten>.3mf` (zip XML tự viết, không thêm thư viện; mỗi STL
   1 `<object name=...>` + `<item>`; đơn vị mm). Mặc định `run_v3.py` dùng `--fast`; `run_v3.py --release` xuất đủ `.sc/.step/.blend`.
   Kiểm: mở 3MF bằng `bambu-studio.exe --info` exit 0, đếm object = số STL, đo thời gian.
2. **Cache xuất phát hành**: `--release` bỏ qua nếu md5 toàn bộ `asm/*.stl` + phiên bản script trùng lần trước (ghi `<ten>.cadhash`).
3. **Cache cắt lớp theo bàn** trong `tools/print/scripts/slice.py`: hash (STL của bàn + overrides + profile + phiên bản Bambu + tham số CLI);
   trùng và có `plates/<ban>/<ban>.3mf` + result PASS → dùng lại, in "CACHE". Có test/gate cho trường hợp đổi 1 STL thì chỉ bàn đó cắt lại.
   Không dùng `--no-check`. Nếu còn token: chạy song song tối đa 2 bàn (mỗi bàn 1 tiến trình, `--outputdir` riêng), giữ `memjob.py`.
4. (Nếu còn token) Cờ CLI rẻ: `--skip-useless-pick`, `--min-save` – chỉ giữ nếu đo thấy nhanh hơn và bàn in vẫn PASS.
5. KHÔNG đổi hình học/khe/số segment trong build lần này (để Tuan duyệt riêng).

## Quy tắc
- Gate trước/sau: `python run_v3.py --slice` PASS (assembly 0/0, kiểm in nhanh SẠCH, gate_owl_v3 PASS, 5 bàn PASS). FAIL thì sửa
  hoặc hoàn tác việc đó (git restore file của việc đó), ghi lý do – không commit đồ hỏng.
- Ghi bảng "trước / sau" (giây) vào cuối `docs/reports/Tăng tốc chuỗi CAD tự động.md` mục mới "Kết quả áp dụng 2026-11-28".
- Commit + push sau mỗi việc đạt (message kiểu repo, kết thúc bằng dòng Co-Authored-By như các commit trước). Không commit file khác
  đang dở trong working tree (pump-control, community/reports).
- Cập nhật memory (`kiem-tra-2-tang.md`, `cad-file-solidcraft-mac-dinh.md`) + MEMORY.md.
- Cuối phiên: viết tóm tắt ≤ 15 dòng vào `docs/plans/auto-run-20261128-cad-perf.result.md` (làm gì, đo gì, commit hash, còn gì).
- Không cài phần mềm, không đụng `community/`, không nạp firmware, không tắt máy (script ngoài lo việc tắt máy).
