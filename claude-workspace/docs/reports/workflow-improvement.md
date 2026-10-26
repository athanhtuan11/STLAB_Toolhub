# Cải thiện quy trình: phân quyền agent · vẽ CAD · testing · hiệu năng

Ngày: 2026-10-26 · Người yêu cầu: Tuan ("cải thiện working flow – phân quyền agent chạy, khả năng vẽ, testing, performance")
· Trạng thái: **nghiên cứu, chưa sửa** (chờ Tuan duyệt thứ tự ở mục 5)

Nguồn: số đo thật (profile `check.py`), Gemini đọc quy tắc + script vẽ (bản chép trong agy-scratch, đã xóa), Codex tra docs
chính thức (permissions, subagents, hooks, auto mode). Claude kiểm từng đề xuất với repo – 2 đề xuất của Gemini **đã có sẵn**
(bỏ `ignore-pair=LK_*|*`, so `metrics.json` với commit trước) nên không đưa vào.

## 1. Hiệu năng – đo được, lợi lớn nhất
Profile `check.py` pushrod-arm (92 chi tiết, 2 118 cặp, **tất cả lấy từ cache**): 78 s chạy riêng (132 s khi chạy song song
với export-stl + metrics trong `prepare-print`).

| Chỗ tốn | Thời gian | Vì sao |
|---|---|---|
| `anh_va_cham` (ảnh `collisions.png`, matplotlib 3 hướng) | **69 s = 88 %** | Vẽ lại **mỗi lần** dù không có gì đổi; `_ve_luoi` 50 s, `savefig` 10 s |
| `Shape.tessellate` | 9 s | Gọi **trong vòng lặp hướng nhìn**: 92 chi tiết × 3 = 276 lần (chỉ cần 92) |
| `khoa_ct` (khóa cache) | 5,8 s | Băm hình mỗi chi tiết |

Sửa (công S, không đổi kết quả kiểm):
- Ảnh va chạm: **chỉ vẽ lại khi tập khóa chi tiết + kết quả cặp đổi** (lưu băm cạnh ảnh); không đổi → giữ ảnh cũ.
- Tessellate 1 lần/chi tiết rồi dùng cho cả 3 hướng; lưới thô hơn cho ảnh tổng (0,5 → 1,0 mm, chỉ để xem).
- Dự kiến: kiểm nhanh pushrod-arm **78 s → ~10 s** khi model không đổi; `prepare-print` cả quy trình ~3,5 → ~2 phút (phần còn
  lại chủ yếu là Bambu cắt lớp 65 s). Song song gây tranh CPU (78 → 132 s) – đo lại sau khi sửa ảnh rồi mới quyết.

## 2. Phân quyền + giao việc agent
Hiện trạng chạy tốt hôm nay: `check-runner` (Haiku) chạy kiểm dài; Gemini đọc mã; Codex tra web. Bài học:
- **Codex trên Windows không đọc được file** (sandbox chặn shell) → chỉ tra web. **Gemini đọc mã tốt nhưng ~30 % nhận xét
  sai** (rà repo: 9/31) → quy tắc: Claude kiểm mọi nhận xét HIGH/MED trước khi tin.

| # | Đề xuất | Lợi | Công |
|---|---|---|---|
| A1 | **Luật cho phép theo dự án** `.claude/settings.json` (workspace): chạy `freecadcmd`/Python FreeCAD **với script trong `tools/robotics-cad/scripts` và `maker/*/freecad/scripts`**, `uv run` trong `studio/`, `curl` chỉ `api.github.com`. Rồi chạy skill có sẵn **`/fewer-permission-prompts`** để đề xuất thêm từ lịch sử (duyệt từng luật) | Bớt hỏi quyền khi lặp kiểm/vẽ; vẫn chặn lệnh lạ | S |
| A2 | Giữ `deny`/hỏi cho: sửa `community/**`, `~/.claude/settings.json`, `ExecutionPolicy`, `taskkill` | Lan can giữ nguyên | S |
| A3 | **Skill `community-scout`**: mẫu prompt chia việc Codex (web) + Gemini (đọc mã trong agy-scratch) + script kiểm GitHub API (sao, push, license, tồn tại) → báo cáo | Hôm nay làm tay 3 lần; chuẩn hóa → ít quota Claude, ít sai | S–M |
| A4 | `doc-writer` giữ `Bash` (cần chép file vào agy-scratch) nhưng thêm luật cho phép chỉ `cp`/`rm` trong `D:\04_Stlab\agy-scratch` (subagent `tools:` không giới hạn được mẫu lệnh – phải dùng `permissions`, theo docs subagents) | Chặt hơn mà không hỏng việc | S |

## 3. Khả năng vẽ CAD
| # | Đề xuất | Lợi | Công |
|---|---|---|---|
| B1 | **Thư viện chung `tools/robotics-cad/scripts/cad_lib.py`**: `box`, `xcyl`, `rrect`, `giot_nuoc` (lỗ giọt nước tự in), `put/local` (đổi hệ), khe chuẩn (0,2 lắp / 0,3 trượt / chốt Ø+0,6), bo/vát an toàn in; có test | Đang chép lại ở 8 script dự án → lệch nhau, dễ sai; vẽ nhanh hơn | S–M |
| B2 | **Chuẩn: dự án MỚI dựng từ tham số** (kiểu `build_car.py`: chạy lại = model mới, FCStd là file sinh) | Tái lập từ git, không phụ thuộc FCStd chỉ có trên máy | Quy ước (S) |
| B3 | pushrod-arm (18 script vá trên FCStd không lên git): **chưa chuyển** (L, rủi ro) – trước mắt sao lưu FCStd + xuất STEP từng chi tiết làm mốc; chuyển dần theo cụm khi vẽ lại | Giảm rủi ro mất model | M |
| B4 | Vòng duyệt ảnh CLI (`mpl_render`, concept → contact-sheet) đã chạy tốt (cyberbrick-car GT) → đưa vào `project-template` thành bước 0 | Khớp quy tắc "giao diện trước" | S |

## 4. Testing
| # | Đề xuất | Lợi | Công |
|---|---|---|---|
| C1 | `project-template/freecad/tests/test_model.py` dùng chung: mọi chi tiết hợp lệ / 1 solid / không ẩn, va chạm = `check.py`, **tháo lắp được** (`assembly_paths.trapped` như T9Assemble), STL in không lơ lửng | Dự án mới có test ngay (hiện chỉ pushrod-arm có) | S–M |
| C2 | Thêm **`assembly_paths`** làm 1 tầng trong `prepare-print` (WARN khi kẹt) | Bắt lỗi "in rời không lắp được" trước khi in (bài học xi-lanh 2026-10-26) | S |
| C3 | Test cho chính bộ công cụ `tools/robotics-cad/tests/` (FCStd/STL mẫu nhỏ: hộp chồng nhau, lỗ kẹt, STL hở…) | Sửa công cụ không làm hỏng ngầm (như lỗi "lưới không kín" vừa sửa) | M |

## 5. Thứ tự đề xuất
1. **Hiệu năng ảnh va chạm** (mục 1) – S, lợi ngay mỗi lần kiểm.
2. **A1 + A2 luật quyền** + chạy `/fewer-permission-prompts` – S.
3. **B1 `cad_lib.py`** + **C1 test mẫu** + **C2 assembly_paths trong prepare-print** – S–M.
4. A3 skill `community-scout`, B4 bước 0 vào template – S.
5. Để sau: C3 test công cụ (M), B3 chuyển pushrod-arm sang tham số (L).
