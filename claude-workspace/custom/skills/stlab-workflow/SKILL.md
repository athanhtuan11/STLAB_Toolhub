---
name: stlab-workflow
description: Quy trinh lam viec chuan cua STLab tu luc nhan viec toi luc xong - phan viec (Claude chi quyet dinh + spec + gate), giao code qua delegate.py, kiem, commit qua git-scribe, cap nhat memory, luu quy trinh lap lai thanh skill. Dung cho MOI viec sua code/script/Toolhub/firmware trong claude-workspace, khi Tuan noi "lam", "sua", "them tinh nang", va khi ket thuc mot viec.
---

# Quy trình làm việc STLab (một nguồn: file này + `claude-workspace/CLAUDE.md` mục "Phân việc theo model")

Viết lần đầu 2026-10-30 sau khi Tuan rà soát: "working flow chưa đồng bộ, làm rồi nhưng không tự lưu skill".
Sổ nhân sự `org/agents.yaml` là nguồn duy nhất về agent; file này chỉ mô tả **trình tự**.

## 0. Nhận việc
- Đọc memory liên quan (MEMORY.md đã nạp sẵn). Nhiều hướng → nêu khuyến nghị + đánh đổi, hỏi Tuan một lần.
- "Nghiên cứu / rà soát xem cần cải thiện gì" = **báo cáo trước, không tự sửa**. Tuan chốt rồi mới làm.
- Dự án mới / tính năng có giao diện → bước 0 "giao diện trước": mockup, duyệt bằng ảnh.

## 1. Phân việc – trước mỗi lệnh hỏi "đây có phải quyết định / CAD / an toàn không?"
| Việc | Ai |
|---|---|
| Quyết định, spec, gate (test), hình học/khe/động học, an toàn điện–pin–nhiệt | Claude (phiên chính) |
| Viết/sửa code, script, firmware, Toolhub | `python tools/delegate/delegate.py <spec.md>` (chạy nền) |
| Đọc/tóm tắt tài liệu dài | `ask-gemini` (agy) – chép file vào `D:\04_Stlab\agy-scratch\<viec>` |
| Tra web | `ask-gpt` (Codex) |
| Viết tài liệu (README, ASSEMBLY.md, báo cáo) | agent `doc-writer` |
| Chạy kiểm dài, slice, đọc log | agent `check-runner` |
| Commit + push | agent `git-scribe` |
Ngoại lệ: việc ≲ 30 dòng (nhỏ hơn viết spec) Claude tự sửa.

## 2. Giao code
0. **Chọn tầng** (Tuan 2026-11-03): firmware/phần cứng/API lạ hoặc free đã FAIL 1 vòng → agent `coder` (Sonnet, cùng
   spec + gate, gọi bằng Agent tool); còn lại → `delegate.py` (free). Gate tĩnh phải chặn mã giả (khối rỗng, chỉ comment).
1. **Viết gate trước**: test trong `.../tests/test_<viec>.py` (DB/thư mục tạm qua biến môi trường, không đụng dữ liệu
   thật). Chạy thử → phải ĐỎ đúng chỗ.
2. Chép `tools/delegate/templates/spec.md` → `spec-<viec>.md` cạnh code. `allow` hẹp nhất có thể; ghi rõ file nào đang
   có thay đổi chưa commit cần GIỮ; mục "Không làm".
   **`gate` chạy qua cmd.exe**: đường dẫn exe phải dùng `\` (`.venv\Scripts\python.exe`, `..\studio\.venv\...`) –
   `.venv/Scripts/...` báo "'.venv' is not recognized" (2 việc FAIL oan 2026-11-01). Chạy thử đúng chuỗi gate trước khi giao.
   Nhiều việc chạy song song → đặt `cwd` mỗi việc ở thư mục riêng (không dùng `cwd: .`), nếu không `outside_allow` báo
   nhầm file của việc khác.
3. `delegate.py` chạy nền; chỉ đọc dòng JSON cuối (`verdict`, `changed`, `encoding_broken`, `forbidden_touched`).
4. `verdict: FAIL` chỉ vì `encoding_broken` (Codex Windows mất dấu → `?`): `git diff` file đó, tìm chuỗi có `?`, sửa
   tay chuỗi tiếng Việt, chạy lại gate. Lỗi khác → đọc `handoff.md`, sửa spec/giao lại (tối đa 1 lần) rồi mới tự làm.
5. Tự kiểm thêm phần gate không phủ (JS: `node --check`; giao diện: chạy Toolhub xem/chụp ảnh).

## 3. Kết thúc việc (KHÔNG bỏ bước)
1. Gate PASS + tự kiểm xong → giao `git-scribe` commit + push, **chỉ liệt kê file của việc này** (working tree hay có
   việc dở khác). Kèm kết quả kiểm + dòng `Co-Authored-By` theo system reminder.
   **Không commit ảnh/video/âm thanh trong `maker/`** (Tuan 2026-10-30: tốn dung lượng cloud) – đã chặn bằng
   `.gitignore`; ảnh duyệt chỉ để trên máy.
2. Cập nhật memory: quyết định mới của Tuan → sửa file memory sẵn có (không tạo trùng) + dòng MEMORY.md.
3. **Quy trình lặp lại ≥ 2 lần mà chưa có skill → tạo skill** (bước 4).
4. **Dọn bản dư thừa vào `backup/`** (Tuan 2026-11-03 "tránh nhầm lẫn"; 2026-11-05 đổi: **chuyển vào backup, không
   xóa**): mỗi lần tạo file mới, bản cũ/bản lỗi/bản FAIL, `.FCBak` FreeCAD tự sinh, log + `.gcode` + `result.json` +
   `_profile/` của slicer, ảnh preview cũ, script/spec của phương án bỏ → `mv` vào `<thu-muc-du-an>/.../backup/<YYYYMMDD>-<ly-do>/`
   (dùng `backup/` sẵn có cạnh file, vd. `freecad/scripts/backup/`). Thư mục Tuan mở chỉ còn file dùng được: STL đúng
   hướng in, `.3mf` in được (PASS), ảnh xem trước, nguồn (params/script/FCStd). Không để song song `-fix`, `-old`.
   File đã commit thì `git mv`. Báo Tuan tên file đúng duy nhất.
5. **File in gửi Tuan = file bàn in `.3mf`** (Tuan 2026-11-05: không đưa STL rời, tốn thời gian mở + in): mỗi bàn 1 `plates/<ban>/<ban>.3mf`
   xếp sẵn mọi chi tiết, PASS; tên bàn `p<số>-<việc>` kebab-case tiếng Anh (vd. `p1-fit-test`, `p2-enclosure`), ảnh `preview.png`; slicer báo floating cantilever / cần support → sửa model cho tự đứng trước khi đưa.
   Chi tiết (mẫu tự dựng đã đặt đúng hướng in): cắt lớp với `--orient 0` (KHÔNG để Bambu tự xoay –
   2026-11-03 bị lật 180° nằm dưới bàn → "loading model fail"), rồi kiểm `transform` trong `3D/3dmodel.model` không
   xoay + `bambu-studio.exe --info <file>` exit 0 trước khi đưa đường dẫn.
6. **Hướng dẫn lắp luôn kèm PDF** (Tuan 2026-11-05): sửa `ASSEMBLY.md` xong → `python tools/print/scripts/assembly-pdf.py
   maker/<du-an>/ASSEMBLY.md` → đưa link `ASSEMBLY.pdf`. Ảnh lắp ráp dự án SolidCraft: `solidcraft/render_assembly.py`.
7. Báo Tuan: làm gì, kiểm gì (PASS/FAIL thật), còn gì chưa kiểm, commit hash.

## 4. Lưu quy trình thành skill
- Skill tự viết ở `custom/skills/<ten-kebab>/SKILL.md` (front matter `name`, `description` ghi rõ KHI NÀO dùng).
- Thêm dòng vào `community/links.tsv`: `~/.claude/skills/<ten>	custom/skills/<ten>` → `bash community/update-community.sh link`.
- Không copy skill sang nơi khác, không tải lên claude.ai. Skill dự án riêng → link vào `<du-an>/.claude/skills/`.
- Cập nhật skill khi quy trình đổi (đừng để memory và skill nói khác nhau).

## 5. Hạn mức
- Toolhub trang chính → ô Nhân sự AI: hạn mức từng nguồn + "lần cuối chạy". Claude chỉ có số khi chạy `claude` trong
  terminal (statusline); trong VS Code gõ `/usage`. agy chỉ cập nhật khi mở `agy` trong terminal.
- Executor gặp 429 → `delegate.py` tự chuyển người + ghi `executors.json`. Hết free → Haiku/phiên chính, không trả phí.
