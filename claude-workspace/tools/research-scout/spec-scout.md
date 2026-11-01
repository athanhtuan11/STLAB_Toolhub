---
task: research-scout
cwd: tools/research-scout
allow:
  - "scan.py"
  - "scout.py"
  - "digest.py"
  - "store.py"
  - "watch.yaml"
  - "register-tasks.ps1"
  - "README.md"
gate: "python tests\\test_scout.py"
timeout_min: 30
max_rounds: 2
executor: auto
---

# Mục tiêu
Agent nghiên cứu tự động "research-scout" cho STLab (Tuan 2026-11-01: "agent siêng quét, tìm kiếm, ngâm cứu để đưa ra
gợi ý"). Tầng 1 quét tin công khai mỗi ngày (không dùng AI, miễn phí); tầng 2 mỗi tuần nhờ AI miễn phí qua `agy` viết
"Gợi ý cho Tuan". Toolhub `/research` (việc sau) đọc qua `store.py`.

# Đầu vào
- Gate `tests/test_scout.py` + `tests/fixtures/` (Claude viết, KHÔNG sửa) – đặc tả chính xác lệnh, khóa JSON, bảng DB.

# Yêu cầu
## store.py (stdlib sqlite3) – API dùng chung
- DB: biến `STLAB_RESEARCH_DB`, mặc định `%LOCALAPPDATA%/stlab-research/research.db` (đọc biến mỗi lần mở kết nối).
- Bảng `items(id, source, url UNIQUE, title, summary, published, topic, score, status, first_seen, extra)`;
  `status` ∈ moi | quan-tam | bo-qua. Bảng `digests(id, week, created, model, content, item_ids)` (`item_ids` = JSON list).
- Hàm: `add_item(...)` (trả True nếu mới), `list_items(topic=None, status=None, limit=200)` (điểm cao trước),
  `set_status(id, status)` → bool, `latest_digest()` → dict | None, `topics(watch_path=None)` → list topic từ watch,
  `topic_weight(topic)` = weight trong watch × (1 + 0,2·(số quan-tam − số bo-qua) của topic), kẹp 0,2…3,0.
## scan.py – tầng 1
- Đọc watch từ `STLAB_RESEARCH_WATCH` (mặc định `watch.yaml` cạnh script; JSON cũng phải đọc được – dùng yaml.safe_load).
- Nguồn: GitHub search API (`/search/repositories`, lọc `min_stars`, `pushed_days`); releases mới nhất của `repos`;
  RSS 2.0 + Atom (`feeds`, parse bằng xml.etree, không thư viện ngoài); Hacker News Algolia
  (`search_by_date?query=...&tags=story`, lọc `min_points`). urllib, hạn 20 s mỗi yêu cầu, User-Agent "stlab-research-scout".
- **Chế độ fixtures** (`STLAB_RESEARCH_FIXTURES`): không gọi mạng; GitHub search → `github_search.json`; release
  `owner/repo` → `releases_<owner>__<repo>.json`; feed tên N → `feed_<N>.xml`; HN → `hn.json`. Thiếu file = lỗi của nguồn đó.
- Gán `topic`: chủ đề có keyword (không phân biệt hoa thường, trong title+summary) với weight lớn nhất; không khớp →
  topic đầu danh sách khớp `source` hoặc "khac". `score` = điểm gốc (github: log10(sao+1); release: 2; feed: 1;
  hn: log10(points+1)) × topic_weight × hệ số mới (≤ 7 ngày theo `STLAB_RESEARCH_NOW` hoặc giờ thật: 1,0; cũ hơn: 0,5).
- Lỗi 1 nguồn không làm dừng cả lượt; ghi vào `errors` (có tên nguồn). Dòng JSON cuối:
  `{"new", "by_source": {github, release, feed, hn}, "errors": [...]}`; exit 0 trừ khi DB/watch hỏng.
- `--rescore`: tính lại score mọi item theo trọng số hiện tại (không gọi mạng).
## scout.py – CLI nhỏ
- `mark <id> <quan-tam|bo-qua|moi>` → JSON `{"id","status"}`; id không có hoặc status sai → exit 1.
## digest.py – tầng 2 (tuần)
- Chọn item status ≠ bo-qua, `first_seen` trong `digest.days` ngày, điểm cao nhất, tối đa `digest.top_n`.
- Prompt tiếng Việt: bối cảnh STLab (trung tâm STEAM Lâm Đồng: robot, in 3D Bambu A1, Arduino/ESP32/Raspberry Pi/STM32,
  FreeCAD, lớp 4–12) + mỗi item 1 dòng bắt đầu `- ` gồm tiêu đề, url, tóm tắt ≤ 200 ký tự, topic. Yêu cầu AI: top 5 gợi ý,
  mỗi gợi ý: vì sao hợp STLab + việc nên làm + mức tin cậy; không bịa số. **Chỉ dữ liệu công khai đã quét** – không chèn
  đường dẫn máy, nội dung repo, tên dự án nội bộ.
- Ghi prompt ra file tạm (in đường dẫn `prompt_file`). Gọi AI: nếu có `STLAB_RESEARCH_LLM_CMD` → chạy lệnh đó (shell, prompt
  qua stdin); ngược lại chuỗi agy `agy -p <prompt> --model <m> --sandbox` (cwd = thư mục tạm rỗng) lần lượt
  `gemini-3.8-flash-medium` → `claude-sonnet-4-6` → `claude-opus-4-6-thinking` → `gpt-oss-120b-medium`; exit ≠ 0 hoặc
  có "429"/"quota" → model kế. Hết → lưu bản thô (danh sách item) với `model = "khong-ai"`.
- `week` = ISO tuần của NOW (`YYYY-Www`). Đã có digest tuần này → bỏ qua (trừ `--force`). `--print-chain` → in
  `{"chain": [...]}`. Dòng JSON cuối: `{"week","model","items","prompt_file","errors"}`.
## watch.yaml – danh sách mặc định (Claude chốt chủ đề; executor điền url/query hợp lý, KHÔNG thêm chủ đề)
Chủ đề (id): `arduino`, `esp32`, `raspberry-pi`, `stm32`, `line-robot`, `robot-arm`, `freecad`, `3d-print-bambu`,
`cyberbrick`, `smart-home`, `ai-agent-free`, `steam-education`. Repo theo dõi bản mới: espressif/esp-idf,
espressif/arduino-esp32, raspberrypi/pico-sdk, arduino/ArduinoCore-renesas, stm32duino/Arduino_Core_STM32,
FreeCAD/FreeCAD, bambulab/BambuStudio, anthropics/claude-code, openai/codex. Feed: blog Arduino, tin Raspberry Pi,
blog FreeCAD, Hackaday (URL feed executor tra – ghi chú `# TODO kiểm` nếu không chắc). HN: "line follower", "esp32",
"raspberry pi pico", "3d printing", "freecad". `digest: {top_n: 10, days: 7}`.
## register-tasks.ps1
Như `../backup/register-tasks.ps1`: `STLab-Research-Scan` hằng ngày 07:00 (`python scan.py`), `STLab-Research-Digest`
Chủ nhật 07:30 (`python digest.py`); `-Unregister`. Không tự chạy.
## README.md ngắn tiếng Việt.

# Không làm
- Không chạy register-tasks.ps1, không gọi agy thật, không sửa tests/.

# Tiêu chí PASS
- Gate exit 0. Claude tự chạy scan.py thật 1 lần (mạng) để kiểm feed/URL.
