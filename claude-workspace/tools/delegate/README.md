# tools/delegate

Giao việc code/script cho executor free, Claude chỉ viết spec và duyệt kết quả. Gemini qua `agy` đang hết hạn mức tới ~2026-11-02, nên tầng dự phòng có thể không dùng được lúc này.

## Mục đích

Phân quyền 3 tầng:

- **Tầng 0 – Claude (tổng giám đốc):** viết spec, viết test/gate trước, chốt số liệu. Không tự viết code dài.
- **Tầng 1 – executor free:** viết code và tự chạy gate, lặp tới khi PASS (hoặc hết số vòng).
- **Claude:** chỉ đọc dòng JSON cuối (`result.json`). Log dài nằm trong thư mục run.

Quy tắc: executor **không tự chọn** kích thước, thông số hay ngưỡng. Thiếu số thì ghi `TODO` và dừng.

## File

- `delegate.py`: đọc spec, chọn executor, chạy vòng lặp, chạy gate, kiểm file đã đổi.
- `templates/spec.md`: mẫu spec (front matter + Mục tiêu, Đầu vào, Yêu cầu, Không làm, Tiêu chí PASS).
- `opencode.json`: luật cho OpenCode (cấm ghi ngoài cwd, cấm `.FCStd`, cấm git commit/push).
- `json_ok.py`: đọc khóa `true/false` trong file JSON, dùng làm lệnh gate.
- `selftest/`: spec thử `calc.py` + `test_calc.py`.

## Thứ tự executor

Mặc định `executor: auto` theo thứ tự:

1. **Codex exec** (chính, ChatGPT Free).
2. **OpenCode Zen free** (model `opencode/deepseek-v4.1-flash-free`).
3. **agy** (dự phòng, Gemini 3.8 Flash High).

Gặp lỗi 429 hoặc hết hạn mức thì đánh dấu executor đó và chuyển sang executor kế tiếp, vòng đó không tính. Trạng thái lưu ở `%LOCALAPPDATA%\stlab-usage\executors.json`.

```bash
cd D:/04_Stlab/04_STLAB_Toolhub/claude-workspace
python tools/delegate/delegate.py --status                    # xem executor nào đang bị giới hạn
python tools/delegate/delegate.py --mark-limit agy 2026-11-02T12:00   # đánh dấu agy hết hạn mức đến mốc này
python tools/delegate/delegate.py --clear-limit codex         # xóa đánh dấu
python tools/delegate/delegate.py <spec.md> --simulate-limit codex    # giả lập codex hết hạn mức (thử nghiệm)
```

Thời gian chờ hết hạn mức (`COOLDOWN_H` trong `delegate.py`): codex 5 giờ, opencode 1 giờ, agy 24 giờ. Đây là ước lượng, chưa xác nhận: TODO.

## Cách dùng

1. Chép `templates/spec.md` vào thư mục đặc tả, điền front matter:
   - `task`: tên việc kebab-case.
   - `cwd`: thư mục executor được làm việc (tương đối với `claude-workspace`).
   - `allow`: glob các file được tạo/sửa, tương đối theo `cwd`.
   - `gate`: lệnh kiểm, exit 0 = PASS.
   - `timeout_min` (mặc định 15), `max_rounds` (mặc định 2), `executor` (`auto` | `codex` | `opencode` | `agy`).
2. Claude viết test hoặc gate **trước**, chạy thử để chắc gate FAIL khi chưa có code.
3. Chạy từ `claude-workspace`:

   ```bash
   python tools/delegate/delegate.py tools/delegate/selftest/spec.md
   ```

4. Đọc dòng JSON cuối hoặc `result.json` trong thư mục run:
   `%LOCALAPPDATA%\stlab-usage\delegate-runs\<thời-gian>-<task>\`
   (gồm `prompt-N.txt`, `<executor>-N.log`, `gate-N.log`, `result.json`).

Các trường trong `result.json`: `verdict` (PASS/WARN/FAIL), `passed`, `rounds`, `changed`, `forbidden_touched`, `outside_allow`, `skipped`, `error`.

Gate nhiều bước: `gate.py` của `cad-delegation` luôn exit 0, nên phải nối thêm `json_ok.py`:

```yaml
gate: '"C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" ../../gate.py . && python ../../../delegate/json_ok.py gate.json passed'
```

Xem `tools/cad-delegation/pilot-opencode/knuckle/task.md` làm mẫu.

## An toàn

- Từ chối `cwd` nằm trong `stlab/parent-reports` hoặc `community` (dữ liệu không được gửi ra ngoài, nguồn ghim không được sửa).
- **FAIL** nếu executor đụng `.FCStd`, `print.yaml`, `community/`, `.env` hoặc `parent-reports/`.
- **WARN** nếu executor sửa file ngoài `allow`. Claude kiểm tay trước khi nhận.
- OpenCode **không có sandbox hệ điều hành** trên Windows. Bù bằng `opencode.json`: cấm ghi ngoài cwd, cấm `.FCStd`, cấm `git commit/push/reset/checkout`. Đã thử thật (2026-10-27): luật cấm có hiệu lực.
- Script không tự hoàn tác thay đổi. Kiểm `git status` sau mỗi lần chạy.

## Chạy song song, mất điện

Sự cố 2026-10-27: hai phiên Claude cùng giao việc vào `tools/model-study` (một phiên "holes", một phiên "fits", trùng nhau), rồi cúp điện cắt ngang. Run không có `result.json`; hai bên ghi đè `_out/arm` của nhau, và `delegate.py` tưởng file do phiên kia ghi là executor sửa nên báo WARN sai.

Cách xử lý hiện tại:

- **Khóa theo cwd:** `%LOCALAPPDATA%\stlab-usage\locks\<cwd>.json` (ghi pid, task, start, run_dir). Pid còn sống → từ chối giao thêm vào cwd đó, báo tác vụ đang chạy.
- **Khóa mồ côi:** pid đã chết (mất điện, bị kill) → khóa được ghi đè. Khóa tự xóa khi chạy xong.
- **Trạng thái run:** mỗi run ghi `state.json` (state `running`, pid, spec). `--status` có thêm `runs_without_result`: `running` (pid còn sống) hoặc `interrupted` (pid đã chết) → chạy lại spec đó.
- **Kiểm pid trên Windows** dùng `OpenProcess`/`GetExitCodeProcess`, vì `os.kill(pid, 0)` trên Windows sẽ giết tiến trình.
- **Dừng tay một run:** `taskkill /T /F /PID <pid trong file khóa>`, rồi xóa file khóa. Không kill `codex.exe` theo tên vì có thể là của phiên khác.
- **In tiếng Việt khi stdout bị pipe (cp1252):** đã sửa. Đã thử thật: selftest OpenCode PASS 29 s; khóa có pid sống bị từ chối, khóa pid chết được vượt.
- **Resume run bị cắt ngang:** `python tools/delegate/delegate.py --resume <tên run hoặc đường dẫn run_dir>` chạy lại spec đã lưu trong `state.json` vào một `run_dir` MỚI. Prompt vòng 1 thêm đuôi ~40 dòng log executor và gate của lần trước; `result.json` có khóa `resumed_from`. Từ chối nếu run đã có `result.json`, thiếu `spec`, hoặc tiến trình còn sống (tránh chạy trùng).
- **`--status` với run thiếu `state.json`/pid:** nếu vẫn có khóa còn sống trỏ tới `run_dir` đó thì báo `running`. Trước đây báo nhầm `interrupted` (lỗi gặp thật 2026-10-27).
- **Run không PASS:** ghi `handoff.md` trong `run_dir` (task, verdict, từng vòng: executor, giây, dòng cuối, gate exit và đuôi gate, file đã đổi/cấm/ngoài allow, bước tiếp theo). `result.json` có khóa `handoff` trỏ tới file này.
- **Kiểm:** `python tests/test_delegate.py` (chạy từ `tools/delegate`), không gọi executor thật. OpenCode viết qua delegate.py, vòng 1 PASS 100 s; Claude thêm chặn resume khi run còn sống.
- Ý tưởng lấy từ `docs/reports/agent-orchestration-ai-memory-ruflo.md` mục 6.

## Cài OpenCode

```powershell
npm i -g opencode-ai@1.19.4 --allow-scripts=opencode-ai
opencode models opencode        # liệt kê model Zen free
```

Cờ `--allow-scripts=opencode-ai` là bắt buộc: postinstall mới chép binary Windows. Thiếu cờ này, `opencode.exe` báo "is not a valid application". Zen free chạy không cần đăng nhập.

Gỡ:

```powershell
npm uninstall -g opencode-ai
Remove-Item -Recurse "$env:USERPROFILE\.local\share\opencode"
```

Hạn mức Zen free: TODO (chưa rõ).

## Kết quả thử

- 2026-10-27, `selftest` (`calc.py` + `test_calc.py`): Codex PASS 19 s; OpenCode PASS 24 s.
- 2026-10-27, giả lập Codex hết hạn mức: auto chuyển sang OpenCode đúng.
- 2026-10-27, pilot CAD Knuckle_L qua OpenCode: gate 26/26 PASS vòng 1, 147 s, `compare.py` lệch 0,00 % so với mẫu.

Xem thêm: `docs/model-routing.md` (mục Phân quyền 3 tầng) và `tools/cad-delegation/README.md`.
