---
task: delegate-pipeline-pain-2026-11
cwd: .
allow: ["docs/reports/delegate-pipeline-pain-2026-11.md"]
read: ["tools/delegate", "tools/render", "org", "custom/agents", "docs/model-routing.md", "docs/reports/repo-improvement-review.md", "maker/cyberbrick-arm/freecad"]
gate: 'python tools/delegate/check_report.py docs/reports/delegate-pipeline-pain-2026-11.md "## 1. Su co thuc te" "## 2. Codex CLI tren Windows" "## 3. Viec song song va khoa cwd" "## 4. Gate sai duong" "## 5. Agent Claude Code tren Windows" "## 6. Render Blender headless" "## 7. De xuat xep loi/cong" --max-todo 6 --min-files 6'
ky_nang: [bao-cao]
timeout_min: 40
max_rounds: 3
executor: copilot
---

# Mục tiêu
Viết `docs/reports/delegate-pipeline-pain-2026-11.md` (tiếng Việt có dấu, ≤ 220 dòng): **nghiên cứu cộng đồng/tài liệu gốc** để cải
tiến đường ống giao việc của STLab, dựa trên 5 sự cố THẬT ngày 2026-11-02. Chỉ ĐỌC + tra web; **không sửa gì** trong repo
(Tuan quyết rồi mới sửa – quy tắc "nghiên cứu trước, cải tiến sau").

# Sự cố thật (Claude ghi – đọc `tools/delegate/delegate.py`, `org/agents.yaml`, `tools/render/*` để hiểu)
1. **Codex exec sandbox Windows** (`--sandbox workspace-write`): (a) cwd `maker/cyberbrick-arm` → không đọc được
   `community/` và `tools/` ngoài cwd → ESCALATE; (b) cwd `.` → tạo file mới được, nhưng lần sau **sửa/xóa file do chính
   phiên sandbox trước tạo thì lỗi** ("Failed to delete file … apply_patch verification failed"), kể cả sau khi Claude chép
   lại file để reset ACL; FreeCAD trong sandbox không tạo được cache Qt (`…/Packages/sandbox.{…}/AC/Temp/…`).
2. **Khóa cwd**: delegate.py từ chối việc thứ 2 cùng cwd `.`; và khi cwd `.` thì "changed/outside_allow" tính cả file do
   Claude/executor khác sửa song song → verdict FAIL oan.
3. **Gate sai đường**: gate render 4 test PASS nhưng ảnh chỉ là Cube mặc định của Blender (`--factory-startup`); test chỉ
   kiểm ảnh "không trơn" + kích thước. Gate CAD trước đó cũng từng PASS khi sonar dựng sai chiều (thiếu test hướng).
4. **Agent Claude Code mới** (`~/.claude/agents/*.md`) không nạp trong phiên đang chạy; symlink Windows cần Admin
   (`New-Item -ItemType SymbolicLink` báo "Administrator privilege required"); tạm hardlink vào `.claude/agents` của repo.
5. **Render Blender headless**: đường dẫn tương đối `--out` → Blender ghi ra `C:\`; mặt phẳng loang do smooth shading;
   mép phông đen lọt khung.

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Su co thuc te`: tóm 5 sự cố trên (ngắn, dẫn file/dòng mã liên quan trong repo).
- `## 2. Codex CLI tren Windows`: tài liệu chính thức OpenAI Codex CLI (sandbox Windows, `writable_roots`/`--add-dir`,
  config.toml, chế độ sandbox, issue GitHub openai/codex về apply_patch/delete trên Windows) – nguyên nhân khả dĩ + cách
  cấu hình đúng; dẫn link + phiên bản/ngày.
- `## 3. Viec song song va khoa cwd`: thực hành cộng đồng cho nhiều agent song song (git worktree mỗi việc, thư mục tạm
  riêng, so diff theo baseline của chính việc đó thay vì toàn cây) – ví dụ dự án có sao, còn cập nhật.
- `## 4. Gate sai duong`: cách viết gate bắt "PASS mà sai": golden image / perceptual diff (vd. pixelmatch, SSIM),
  kiểm màu/điểm ảnh theo vùng, kiểm hướng/hình học bắt buộc, mutation testing nhẹ cho gate; nguồn có uy tín.
- `## 5. Agent Claude Code tren Windows`: tài liệu chính thức Claude Code về subagent (thư mục user/project, lúc nạp,
  `/agents`), Windows Developer Mode cho symlink không cần Admin, lựa chọn thay thế.
- `## 6. Render Blender headless`: best practice `blender -b --factory-startup -P`, đường dẫn tuyệt đối/`bpy.path.abspath`,
  auto smooth trong Blender 4.1+/5.x (modifier "Smooth by Angle"), phông cyclorama/shadow catcher; dự án cộng đồng render
  CAD tự động (có sao, còn cập nhật – vd. BlenderProc, các addon product render) + license.
- `## 7. De xuat xep loi/cong`: bảng ≤ 12 dòng: đề xuất | sự cố nào | lợi (cao/vừa/thấp) | công (giờ) | rủi ro | nguồn.
  Xếp lợi/công giảm dần. Không đề xuất trả phí (chỉ Claude Pro), không model local.

# Quy tắc
- Mỗi khẳng định kỹ thuật bên ngoài phải có link nguồn gốc (docs chính thức, issue/PR, repo) + ngày truy cập 2026-11-02.
  Không chắc → `TODO`. Không bịa cờ dòng lệnh hay khóa config – chỉ ghi cái thấy trong tài liệu/mã.
- Dự án cộng đồng: ghi số sao (nếu thấy), commit gần nhất, license.

# Tiêu chí PASS
Gate exit 0.
