# Rà repo: cần cải thiện gì (agent free phân tích, Claude kiểm lại)

Ngày: 2026-10-26 · Người yêu cầu: Tuan · Trạng thái: **nghiên cứu, chưa sửa** (chờ Tuan chọn mục)

## Cách làm
- **Gemini (agy)** đọc mã (bản chép trong `D:\04_Stlab\agy-scratch`, đã xóa sau khi xong): gói 1 = `tools/robotics-cad`
  (scripts, CLAUDE.md, thresholds, project-template, test + print.yaml của pushrod-arm); gói 2 = `studio/` (Toolhub,
  launcher), `CLAUDE.md`, `maker/CLAUDE.md`, `custom/agents|hooks|statusline|skills` (bỏ `parent-report`). Đã quét khóa/mật
  khẩu trước khi chép (không có).
- **Codex** tra web thực hành tốt 2026 (CI FreeCAD, pre-commit, uv, Claude Code, secret scanning…).
- **Claude kiểm từng nhận xét HIGH/MED trong mã thật** (đọc đoạn mã, thử FreeCAD, đo thời gian). Gemini đưa 31 nhận xét:
  **9 sai**, nhiều cái bị thổi mức độ → bảng dưới chỉ giữ mức Claude đánh giá lại.

## 1. Lỗi thật / rủi ro (đã kiểm)
| # | Mức | Chỗ | Vấn đề | Sửa | Công |
|---|---|---|---|---|---|
| 1 | **MED** | `prepare-print.py` ~85–92 + `printability.py:167` `kiem_lop` | Lưới STL không kín → `kiem_lop` trả `"luoi khong kin - khong kiem duoc theo lop"`, `prepare-print` chỉ xét `roi…`/`vuon ra` → **im lặng PASS** | Thêm nhánh: loại khác → WARN "không kiểm được theo lớp" | S |
| 2 | **MED** | `assembly_paths.py:121` `main` | Duyệt `doc.Objects` phẳng, dùng `o.Shape` cục bộ – chi tiết trong `App::Part`/`Link` sai tọa độ hoặc bị bỏ (pushrod-arm để phẳng nên chưa lộ) | Dùng chung `check.chi_tiet_la` (đã đi xuyên Part/Link) | M |
| 3 | **MED** | `studio/toolhub/printprep.py` `_song`, `tat` | Chỉ kiểm PID còn tồn tại; nếu Windows cấp lại PID cho tiến trình khác, nút "Tắt" chạy `taskkill /T /F` **nhầm tiến trình** | So thêm tên ảnh (`python.exe`/`freecadcmd`) trong `tasklist /FO CSV` trước khi kill | S |
| 4 | LOW | `printprep.py` `chay` | File log mở rồi đưa cho `Popen`, tiến trình cha không đóng → rò handle mỗi lần chạy | `log.close()` sau `Popen` | S |
| 5 | LOW | `printprep.py` `anh` | Ảnh lấy đường dẫn từ JSON, chỉ kiểm đuôi `.png` – không kiểm nằm trong dự án (JSON do script mình sinh nên rủi ro thấp) | Kiểm `is_relative_to(dự án)` | S |
| 6 | LOW | `safe_edit.py` `restore_gui` | `ZipFile(gui_from)` không đóng (vẫn chạy được vì CPython đóng `ZipFile(dst)` ngay) | Dùng `with` | S |
| 7 | LOW | `thresholds.yaml` `min_overlap_mm3: 0.1` + `check.py` `danh_gia_cap` | Chồng < 0,1 mm³ báo INFO "chạm nhau" – chủ ý (bỏ nhiễu lưới), nhưng che chồng rất nhỏ ở chi tiết động | Ghi rõ lý do trong thresholds; chi tiết động đã có quét khớp | S |
| 8 | LOW | `check.py` `chay_song_song` | Chờ tiến trình con không có hạn giờ tổng (OCC treo → treo) – `[chưa thử]` | Thêm hạn giờ + kill | S |

## 2. Gemini nhận xét SAI (đã kiểm – không làm)
| Nhận xét | Vì sao sai |
|---|---|
| `slice.py` `bo_khe`: tên có `.stl` nên không khớp cảnh báo → FAIL | Lần cắt lớp R10 hôm nay gắn đúng "CAN SUPPORT" (WARN) – khớp chạy đúng |
| `check.py` khóa cache dùng `Center.Length` → che va chạm khi xoay | Thử FreeCAD: `Part.getShape` giữ vị trí trong `Placement` (xoay 90° → chuỗi Placement đổi) → khóa đổi |
| `safe_edit.apply` nhân đôi Placement | Gán `obj.Shape` lấy Placement của shape (= Placement cũ) – đã dùng đúng trong các lần sửa model |
| `launcher.mcp_check` lỗi `p` chưa gán khi `Popen` hỏng | `except OSError` đã `return` trước |
| Thiếu `winlayout.py` | File có (`studio/winlayout.py`) – chỉ không chép vào gói gửi Gemini |
| Hook `usage_alert.py` chặn Claude 8 s | Hook đặt `async: true` |
| Trang chính chậm vì `tasklist` | Đo: 14 dự án 0,23 s |
| `maker/CLAUDE.md` "vi phạm" vì agent VoltAgent dùng `sonnet` | Sonnet vẫn trong gói Pro (không trả thêm); chỉ tốn quota hơn Haiku – xem mục 3 |
| Trùng Label làm mất chi tiết (export-stl, metrics) | FreeCAD mặc định bắt Label duy nhất trong 1 file (`[chưa thử]` với tùy chọn DuplicateLabels) |

## 3. Cấu hình Claude Code (nhẹ, nên làm khi rảnh)
- `CLAUDE.md` workspace (81 dòng, nạp **mọi phiên**) có ghi chú kiểu nhật ký (ngày thử, TODO) – chuyển chi tiết sang
  `docs/model-routing.md`, giữ quy tắc ngắn. Skill `robotics-cad/SKILL.md` (153 dòng) có đoạn "ca thật pushrod-arm" dài –
  có thể chuyển sang `harness-lab`/docs, giữ quy tắc chung. Theo `harness-lab/README.md`: sửa CLAUDE.md/skill phải **Tuan duyệt**.
- Agent VoltAgent (`embedded-systems`, `python-pro`…) mặc định `sonnet` – tốn quota Pro hơn Haiku; cân nhắc `model: haiku`
  cho việc đơn giản.
- `check-runner`/`git-scribe`/`doc-writer` có `Bash` (cần để chạy kiểm, git, cp/rm agy-scratch). Muốn chặt hơn: luật
  `permissions` theo mẫu lệnh `[chưa kiểm cú pháp cho subagent]`.

## 4. Thực hành tốt cộng đồng (Codex tra web – chưa kiểm từng nguồn)
| # | Việc | Lợi | Bước đầu | Công |
|---|---|---|---|---|
| 1 | **pre-commit**: ruff + `check-added-large-files` | Bắt lỗi Python + chặn file STL/STEP lớn lọt vào git | `.pre-commit-config.yaml` 2 hook ([pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)) | S |
| 2 | **Test cho chính bộ công cụ** (`tools/robotics-cad`) – Gemini cũng nêu | Sửa `check.py`/`slice.py` không làm hỏng ngầm; mục 1–2 bảng trên sẽ được test bắt | `tools/robotics-cad/tests/` với FCStd/STL mẫu nhỏ, chạy `freecadcmd` | M |
| 3 | **CI GitHub Actions** chạy test FreeCAD headless (Linux trước) | Mỗi lần push tự kiểm | Job Linux + FreeCAD AppImage/conda ([docs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)) | L |
| 4 | **Secret scanning + push protection** (GitHub) | Chặn lỡ đẩy token | Bật trong Settings repo (tùy gói/repo riêng tư – `[chưa kiểm]`) | S |
| 5 | **Sao lưu FCStd ngoài git** (FCStd không lên git) | Mất máy = mất model gốc | Chép định kỳ `freecad/*.FCStd` + `backup/` sang ổ/đám mây thứ hai, thử khôi phục | M |
| 6 | Tự kiểm bản mới của repo ghim (`pins.tsv`) theo lịch | Đỡ phải nhớ chạy `update-community.sh check` | Lịch chạy `check` hằng tuần → báo cáo (Renovate với pins.tsv `[chưa kiểm]`) | M |

## 5. Đề xuất thứ tự (chờ Tuan)
1. **Sửa nhanh 4 lỗi thật** (mục 1: #1, #3, #4, #6 – đều công S, ~30 phút, chạy lại kiểm pushrod-arm + cyberbrick-car).
2. **pre-commit** (ruff + chặn file lớn) – S.
3. **Sao lưu FCStd** ra chỗ thứ hai – vì FCStd chỉ có trên máy (nguy cơ mất lớn nhất).
4. `assembly_paths` dùng `chi_tiet_la` + bộ test cho công cụ – M, làm khi có dự án dùng App::Part/Link.
5. CI GitHub Actions – L, để sau.
