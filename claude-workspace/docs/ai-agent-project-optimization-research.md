# Nghiên cứu: tối ưu AI agent và tối ưu dự án – học từ các repo robotics/phần cứng

Viết 2026-10-25. Số liệu GitHub tra cùng ngày (GitHub REST API + tải file thô từ raw.githubusercontent.com, chỉ đọc).
Tuan sửa/bổ sung trực tiếp file này. **Chỉ đề xuất** – theo `harness-lab/README.md`, sửa CLAUDE.md/skill/hook phải Tuan duyệt.

**Phạm vi:** không đi vào dự án cụ thể. Câu hỏi: các repo robotics/phần cứng lớn và tài liệu chính thức của Anthropic,
OpenAI, GitHub tổ chức **file hướng dẫn agent, kiểm thử, môi trường, quy trình người + agent** thế nào để agent ít sai,
dự án chạy trơn → STLab đang có gì, thiếu gì.

**Không lặp:** CI/GitHub Actions cho FreeCAD, test hồi quy model, release → [freecad-automation-research.md](freecad-automation-research.md)
(mục 3, 7). Bẫy freecadcmd → mục 7 file đó + [reports/freecad-community-automation.md](reports/freecad-community-automation.md).
Quy trình CAD → [cad-standard-workflow.md](cad-standard-workflow.md). Mảng robotics → [robotics-github-landscape-research.md](robotics-github-landscape-research.md).
Dung sai/in → [cad-community-gaps-research.md](cad-community-gaps-research.md). Cơ cấu/dạy CAD → [cad-mechanisms-teaching-research.md](cad-mechanisms-teaching-research.md).

**Nhãn:** **[nguồn gốc]** = file trong repo / docs chính thức / paper · **[API]** = GitHub API 2026-10-25 (★ = sao, push = `pushed_at`)
· **(thứ cấp)** = blog/tổng hợp · `TODO` = chưa xác nhận. Trích dẫn giữ nguyên tiếng Anh.

## 0. Kết luận nhanh

1. **AGENTS.md đã thành chuẩn chung trong repo robotics lớn** (LeRobot, PX4, ArduPilot, Isaac Lab, KiCad, ESPHome,
   Home Assistant, xiaozhi-esp32, Zephyr). Mẫu phổ biến: `AGENTS.md` ngắn (20–100 dòng) + `CLAUDE.md` chỉ là `@AGENTS.md`
   hoặc symlink. Nội dung tốt nhất = **lệnh build/test chính xác + điều agent hay làm sai + cấm sửa file sinh tự động**,
   không phải mô tả dự án. STLab dùng mỗi Claude → chưa cần AGENTS.md; cần học **cách viết**, không cần đổi tên file.
2. **"Quy tắc khuyên" ≠ "quy tắc bắt buộc".** Docs Claude Code nói thẳng: CLAUDE.md/memory là ngữ cảnh, *không* được
   ép; muốn chặn chắc thì dùng **hook**. STLab có ~20 quy tắc trong memory/CLAUDE.md nhưng **0 hook** (đã đọc
   `~/.claude/settings.json`, không có `.claude/settings*.json` trong repo). 3/4 sự cố 2026-10-24/25 là loại hook/test chặn được.
3. **Kiểm trên artifact cuối, không chỉ trên model.** Repo phần cứng tốt kiểm thứ thật sự chạy: ArduPilot/PX4 chạy
   SITL, Zephyr chạy `native_sim`, xiaozhi ghi rõ *"A successful build is not hardware validation."* Với STLab artifact
   cuối là **G-code trong .3mf**, không phải FCStd hay STL.
4. **Im lặng = lỗi.** Mẫu chung (Building effective agents: *"ground truth from the environment at each step"*; KiCad MCP
   từ chối ghi đè file đã đổi trên đĩa): công cụ phải **FAIL to tiếng** khi bỏ qua thứ gì (chi tiết ẩn, exception,
   file bị đổi ngoài phiên). STLab đã vá từng ca (fc_cli.py, `test_no_hidden_parts`), chưa thành nguyên tắc chung.
5. **CLAUDE.md gọn, chi tiết đẩy sang skill / rule theo đường dẫn.** Docs: *"target under 200 lines per CLAUDE.md"*;
   PX4 chỉ 20 dòng + 7 skill + 11 file rule `applyTo`. `tools/robotics-cad/CLAUDE.md` của STLab 156 dòng, trộn lệnh,
   chính sách support, an toàn lắp, lịch sử thử nghiệm → nên tách.
6. **Bài học → bài kiểm.** Anthropic khuyên bắt đầu eval với *"20-50 simple tasks drawn from real failures"* –
   đúng thứ `harness-lab/inbox.md` đang gom (8 mục chưa xử lý). Không cần làm GĐ2 ngay, nhưng mỗi sự cố nên kết thúc
   bằng **1 test hoặc 1 hook**, không chỉ 1 dòng quy tắc.
7. **Quy tắc trung thực về kiểm thử** là điểm chung mạnh nhất: ArduPilot *"Never fabricate test results"*, Zephyr
   *"State what you did not do (not built, not run, not run on hardware)"*. STLab nên đưa vào CLAUDE.md gốc 1 dòng:
   báo "đã kiểm gì / chưa kiểm gì / cần in thử".

## 1. File hướng dẫn agent trong repo robotics/phần cứng

### 1.1 Cộng đồng làm gì [nguồn gốc][API]

Đã kiểm thư mục gốc của 21 repo (tải raw `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`…).

| Repo | ★ / push / license | File agent (số dòng) | Điểm đáng học |
|---|---|---|---|
| [huggingface/lerobot](https://github.com/huggingface/lerobot/blob/main/AGENTS.md) | 28 447 / 2026-10-24 / Apache-2.0 | `AGENTS.md` 57; `CLAUDE.md` = symlink | Mục "Key Commands" (`uv sync --locked`, `uv run pytest tests -svv --maxfail=10`, `pre-commit run --all-files`); test phần cứng dùng *skip decorators*; CI tách `fast_tests` (mọi PR) / `full_tests` (GPU, sau duyệt); *"Prioritize use of `uv run`"* |
| [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot/blob/main/AGENTS.md) | 12 897 / 2026-10-25 / BSD-3 | `AGENTS.md` **20**; `CLAUDE.md` = `@AGENTS.md`; `.claude/skills/` 7 skill (build-px4-linux, commit, pr, review-pr, grilling…); `.github/instructions/` 11 file `applyTo` | File gốc chỉ là **bảng chỉ đường**: build → skill, commit → skill, review theo đường dẫn → rule `applyTo`. *"read only the `.github/instructions/*.instructions.md` files whose `applyTo` patterns match the affected paths"* |
| [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot/blob/master/AGENTS.md) | 16 200 / 2026-10-23 / GPL-3.0 | `AGENTS.md` 398 | Mục "What AI Should NOT Do": *"Never fabricate test results"*, *"Do not guess at safety-critical logic … stop and flag it for human review"*, *"Do not change parameter indices"* (giá trị đã nằm trong cấu hình người dùng), *"Do not remove or weaken existing tests"*. Test = SITL autotest + GTest |
| [isaac-sim/IsaacLab](https://github.com/isaac-sim/IsaacLab/blob/main/AGENTS.md) | 8 456 / 2026-10-25 / NOASSERTION (TODO) | `AGENTS.md` 42; `CLAUDE.md` = `@AGENTS.md`; `skills/developer/` 7 skill | *"The guide owns shared contribution rules. Update them there instead of copying them into this file or skills."* Skill để trong repo, *"do not duplicate their contents in tool-specific discovery directories"*, có lệnh **kiểm skill** (`tools/skills/cli.py check`). *"Do not commit generated plans, scratch files, or agent artifacts"* |
| [KiCad/kicad-source-mirror](https://github.com/KiCad/kicad-source-mirror/blob/master/AGENTS.md) | 3 068 / 2026-10-24 / GPL-3.0 | `AGENTS.md` 58 | *"Do not manually edit _base.cpp/.h files, these are generated"*; file `.wxfb` agent sửa được nhưng *"must be resaved via wxFormBuilder"* (giống FCStd: sửa xong phải qua đúng công cụ để giữ định dạng). Cấm agent tự mở issue/MR |
| [esphome/esphome](https://github.com/esphome/esphome/blob/dev/AGENTS.md) | 11 951 / 2026-10-25 / NOASSERTION | `AGENTS.md` **1 092**; `CLAUDE.md`/`GEMINI.md`/copilot = symlink; `.claude/settings.json` có **hook SessionStart** chạy `script/setup` | Phản ví dụ về độ dài; nhưng hook tự dựng môi trường khi mở phiên là mẫu hay. Giải thích *vì sao* quy tắc tồn tại (heap fragmentation → *"We have seen field crashes"*) |
| [home-assistant/core](https://github.com/home-assistant/core/blob/dev/AGENTS.md) | 91 709 / 2026-10-25 / Apache-2.0 | `AGENTS.md` 57; `copilot-instructions.md` 197 (**sinh bằng script**, chỉ cho review); `.claude/skills/` 8 + `.claude/agents/` | Test snapshot Syrupy (`.ambr`); *"Autonomous contributions are not accepted"*; instructions review sinh tự động từ PR template → không lệch nhau |
| [78/xiaozhi-esp32](https://github.com/78/xiaozhi-esp32/blob/main/AGENTS.md) | 31 888 / 2026-10-25 / MIT | `AGENTS.md` 93 | Mục **Validation** theo loại thay đổi (board / core / audio / UI); *"Always report what was tested and what still needs physical hardware. A successful build is not hardware validation."*; *"Keep detailed or fast-changing information in those files, not here."* |
| [zephyrproject-rtos/zephyr](https://github.com/zephyrproject-rtos/zephyr/blob/main/AGENTS.md) | 16 893 / 2026-10-24 / Apache-2.0 | `AGENTS.md` 202; `CLAUDE.md` = `@AGENTS.md`; copilot 27 | Mục **"Code rules agents get wrong most often"**; bẫy worktree: *"otherwise the workspace's registered checkout is built silently instead of your tree"*; *"Fix the cause, never work around a check"*; trailer `Assisted-by:` |
| [dimensionalOS/dimos](https://github.com/dimensionalOS/dimos/blob/main/AGENTS.md) | 4 685 / 2026-10-25 / NOASSERTION | `AGENTS.md` 401 + `docs/coding-agents/` | Robot (Go2, G1) điều khiển qua MCP; `uv.lock` + `flake.nix` |
| [anthropics/claude-code](https://github.com/anthropics/claude-code/blob/main/CLAUDE.md) | 153 300 / 2026-10-24 / không license | `CLAUDE.md` 40 | Chỉ nói về an toàn CI chạy Claude (runner chặn mạng, `--permission-mode auto`, workflow tự kiểm cấu hình) |
| ros2/rclcpp, ros-navigation/navigation2, google-deepmind/mujoco, FreeCAD/FreeCAD, espressif/esp-idf, gazebosim/gz-sim | – | **Không có** ở thư mục gốc | FreeCAD dùng `pixi.toml`; nav2 có `.devcontainer` |

**Chuẩn AGENTS.md** [nguồn gốc]: [agents.md](https://agents.md/) – *"stewarded by the Agentic AI Foundation under the
Linux Foundation"*, *"used by over 60k open-source projects"*; file gần nhất trong cây thư mục thắng. Mục gợi ý: tổng quan,
lệnh build/test, code style, testing, bảo mật, quy ước commit/PR.
- **Claude Code**: đọc `AGENTS.md` **chỉ khi không có CLAUDE.md** (cần v2.1.277+); có CLAUDE.md thì dùng `@AGENTS.md`
  để nạp chung ([memory docs](https://code.claude.com/docs/en/memory)).
- **Codex**: nối `AGENTS.md` từ gốc git xuống thư mục hiện tại, giới hạn `project_doc_max_bytes` = **32 KiB**, quá thì
  cắt ([Codex docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md)).
- **Copilot**: `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md` (frontmatter `applyTo` glob,
  `excludeAgent`), đọc cả `AGENTS.md`, `CLAUDE.md` ([GitHub docs](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)).

**Điểm chung rút ra:**
1. File gốc ngắn, làm **mục lục trỏ tới** tài liệu/skill/rule đã có (PX4, IsaacLab, xiaozhi). Không chép quy tắc 2 nơi.
2. Lệnh **chép-dán chạy được** (`uv run pytest …`), không mô tả bằng lời.
3. Danh sách **"agent hay làm sai"** viết từ lỗi thật (Zephyr, ArduPilot) – đúng tinh thần harness-lab.
4. Cấm sửa **file sinh tự động/vendor** và nêu cách tái sinh (KiCad, xiaozhi, HA translations).
5. Quy định **báo cáo trung thực**: đã kiểm gì, chưa kiểm gì (xiaozhi, Zephyr, ArduPilot).

### 1.2 STLab đang có

- `CLAUDE.md` gốc 39 dòng (cấu trúc, quy tắc cộng đồng, git) + 12 CLAUDE.md dự án (13–57 dòng) + `tools/robotics-cad/CLAUDE.md`
  **156 dòng**. Global `~/.claude/CLAUDE.md` (cách trả lời, đơn vị, an toàn). Memory 22 dòng chỉ mục + 22 file (dưới ngưỡng 200 dòng/25 KB).
- Chưa có mục "Lệnh kiểm" kiểu chép-dán ở đầu file dự án; lệnh nằm rải trong đoạn văn mục 4 của robotics-cad.

### 1.3 Khoảng trống

- `robotics-cad/CLAUDE.md` trộn 4 loại: lệnh, chính sách (support/brim), an toàn lắp ráp (đã có ở memory `luu-y-huong-dan-lap`),
  lịch sử thử nghiệm ("đã thử… đừng thử lại"). Lịch sử thử → `freecad-automation-research.md` mục 7 đã có, chỉ cần link.
- Không có danh sách "Claude hay làm sai ở STLab" tập trung – nó nằm rải trong inbox, memory, CLAUDE.md.
- Không có quy tắc báo "đã kiểm / chưa kiểm / cần in thử" (hiện chỉ có "kiểm ổn thì tự push").

## 2. Hướng dẫn chính thức về tối ưu agent (đối chiếu từng điểm)

Nguồn: [Claude Code best practices](https://code.claude.com/docs/en/best-practices), [memory](https://code.claude.com/docs/en/memory),
[hooks](https://code.claude.com/docs/en/hooks), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29),
[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024-12-19),
[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) (2026-01-09).

| Khuyến nghị chính thức | Trích | STLab hiện tại | Khoảng trống |
|---|---|---|---|
| Cho agent cách **tự kiểm** | *"Give Claude a check it can run … It's the difference between a session you watch and one you walk away from."* | Có: `prepare-print.py`, unittest `-t`, `metrics.json` | Kiểm chưa phủ artifact cuối (G-code); chưa có cổng tự động ở cuối lượt (Stop hook / `/goal`) |
| CLAUDE.md ngắn | *"For each line, ask: Would removing this cause Claude to make mistakes?"*; *"target under 200 lines"* | Gốc 39 dòng tốt; robotics-cad 156 | Tách robotics-cad |
| Rule theo đường dẫn | `.claude/rules/*.md` với frontmatter `paths:` – *"only load into context when Claude works with matching files"* | Chưa dùng; dùng CLAUDE.md lồng (cũng nạp khi chạm thư mục con) | Quy tắc FreeCAD CLI chỉ cần khi đụng `**/*.FCStd`, `**/freecad/**` → rule `paths:` |
| Hook cho quy tắc **bắt buộc** | *"Unlike CLAUDE.md instructions which are advisory, hooks are deterministic"*; memory docs: *"To block an action regardless of what Claude decides, use a PreToolUse hook"* | **0 hook** | Xem đề xuất H1–H4 |
| Skill cho kiến thức thỉnh thoảng cần | *"For domain knowledge or workflows that are only relevant sometimes, use skills"* | Có: robotics-cad, freecad-scripts, video-ai… (symlink, 1 nguồn – giống IsaacLab) | Chưa có lệnh kiểm skill (IsaacLab có `cli.py check`); `skill-creator` có eval |
| Subagent kiểm độc lập | *"the agent doing the work isn't the one grading it"*; adversarial review chỉ báo lỗi ảnh hưởng đúng/sai | Chưa có `.claude/agents/` | Subagent "soát bàn in" xem ảnh + báo cáo, cố bác bỏ PASS |
| Quyền | allowlist + sandbox + auto mode | `~/.claude/settings.json` chỉ có `allow` (kể cả `git push *`), **không có `deny`** | `deny` sửa `community/**` – hiện chỉ là lời dặn |
| Quản lý ngữ cảnh | *"/clear between unrelated tasks"*; sửa >2 lần thì làm lại phiên mới | Không thấy quy ước | Nhắc trong CLAUDE.md gốc (1 dòng) hoặc bỏ qua |
| Song song nhiều phiên | worktree cho sửa code; Writer/Reviewer | Sự cố 2 phiên cùng FreeCAD | Worktree không giải được (FreeCAD là 1 tiến trình chung) → cần **khóa** (H1) |
| Công cụ chống sai (poka-yoke) | *"Change the arguments so that it is harder to make mistakes."* | `safe_edit.py`, `fc_cli.py` đúng hướng này | Mở rộng: công cụ báo FAIL thay vì bỏ qua |
| Eval từ lỗi thật | *"20-50 simple tasks drawn from real failures"*; regression eval ~100%; *"grade what the agent produced, not the path"* | harness-lab GĐ0–1 (inbox) | GĐ2 = biến mục inbox thành task; chấm bằng code (test) trước |
| Ghi chú ngoài ngữ cảnh | NOTES.md / structured note-taking | memory tự động + inbox + README "Lịch sử in" | Đã ổn |

**Khác biệt đáng học từ OpenAI/GitHub:** Codex cắt hướng dẫn ở 32 KiB (lý do thêm để file ngắn). Copilot cho phép tách
**hướng dẫn review** riêng (`excludeAgent`), HA sinh file review từ PR template bằng script → một nguồn, không lệch.

## 3. MCP & công cụ agent cho robotics/CAD/EDA [API 2026-10-25]

| Dự án | ★ / push / license | Mức trưởng thành | Điểm đáng học cho STLab |
|---|---|---|---|
| [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) | 3 040 / 2026-10-25 / MIT | Đang dùng (ghim v0.1.27) | `exec()` code tùy ý qua XML-RPC – không có khóa phiên, không kiểm file đổi trên đĩa |
| [mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) | 2 934 / 2026-10-01 / MIT | 244 tool; IPC *"under active development"*; phát triển mới chuyển sang Konnect (Rust, AGPL-3.0) | **`save_project` từ chối ghi đè board đã đổi trên đĩa từ lúc nạp** (trừ `force`); GUI driver chỉ 127.0.0.1 + **token theo phiên** → chính là 2 lỗi STLab gặp |
| [lamaalrajih/kicad-mcp](https://github.com/lamaalrajih/kicad-mcp) | 529 / 2025-10-17 / MIT | Ít cập nhật | DRC, BOM qua MCP |
| [robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) | 1 505 / 2026-10-24 / Apache-2.0 | ROS 1 + ROS 2 qua rosbridge, devcontainer | README không nêu chế độ chỉ-đọc / danh sách topic cho phép / e-stop → tự thêm lớp an toàn nếu dùng với robot thật |
| [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp) | 5 212 / 2026-10-24 / MIT | Đã ghim, chưa bật | Có tool xóa/restart → nếu bật nên dùng token user hạn chế |
| HA [MCP Server tích hợp](https://www.home-assistant.io/integrations/mcp_server/) | chính thức, từ 2025.2 | OAuth 2.0 + PKCE, chỉ entity đã "exposed" | Mẫu tốt về **giới hạn phạm vi** agent: agent chỉ thấy cái được phơi ra |
| [gumyr/build123d](https://github.com/gumyr/build123d) | 3 519 / 2026-10-23 / Apache-2.0 | Ổn định | CAD-as-code: diff được trên git, test bằng pytest thường – agent kiểm dễ hơn FCStd nhị phân |
| [CadQuery/cadquery](https://github.com/CadQuery/cadquery) | 5 990 / 2026-10-24 / NOASSERTION (TODO: file LICENSE) | Ổn định | Định dạng đích của nhiều benchmark LLM-CAD |
| [Kamel773/CAD_Code_Generation](https://github.com/Kamel773/CAD_Code_Generation) (CADPrompt + CADCodeVerify, ICLR 2025, [paper](https://arxiv.org/abs/2410.05340)) | 66 / 2025-02-28 / **không license** | Nghiên cứu | CADPrompt = 200 prompt + code chuẩn; CADCodeVerify = **VLM xem ảnh render rồi sửa code** → vòng "render ảnh → tự soát" giống quy tắc duyệt bằng ảnh của STLab |
| [SadilKhan/Text2CAD](https://github.com/SadilKhan/Text2CAD) | 491 / 2025-05-15 / NOASSERTION (TODO) | NeurIPS'24 | Chỉ tham khảo |
| [filaPro/cad-recode](https://github.com/filaPro/cad-recode) | 273 / 2025-11-16 / NOASSERTION (TODO) | ICCV 2025, point cloud → code CadQuery | Chỉ tham khảo |

**Rút ra:** MCP CAD/EDA trưởng thành nhất đã có **khóa phiên + chống ghi đè**; MCP robot (ROS) chưa có lớp an toàn
→ STLab tự thêm bằng hook/quy tắc. Benchmark LLM-CAD đều chấm bằng **hình học của kết quả** (không chấm code) – cùng
hướng "grade outcomes".

## 4. Kiểm thử & vòng phản hồi

### 4.1 Cộng đồng làm gì

| Kỹ thuật | Ví dụ gốc | Ý nghĩa cho STLab |
|---|---|---|
| Sim-in-the-loop | ArduPilot SITL autotest (`Tools/autotest`), PX4 SITL, Zephyr `west twister -p native_sim` | Tương đương: quét khớp `fast_collide.py`, mô phỏng tư thế – đã có |
| Phân tầng nhanh/chậm | LeRobot `fast_tests` mỗi PR, `full_tests` GPU sau duyệt, `latest_deps_tests` hằng ngày | Đã có 2 tầng (check.py / slice.py) – đúng hướng |
| Test phần cứng bị skip rõ ràng | LeRobot *"Hardware tests use skip decorators"* | Test cần in thật → đánh dấu "cần in thử" thay vì im lặng |
| Validation theo loại thay đổi | xiaozhi mục Validation | Bảng "sửa X → chạy Y" trong CLAUDE.md dự án |
| Snapshot/golden | HA Syrupy `.ambr`; [pytest-regressions](https://github.com/ESSS/pytest-regressions) (TODO ★) | `metrics.json` + `git diff` đã là golden số; thiếu golden **G-code/lớp** |
| Kiểm chính file sinh | KiBot (CI KiCad: DRC/ERC + xuất Gerber trong CI) – [INTI-CMNB/KiBot](https://github.com/INTI-CMNB/KiBot) 753★ / 2026-10-22 / AGPL-3.0 | Mẫu "kiểm file xuất xưởng, không chỉ file thiết kế" |
| Không lách kiểm | Zephyr *"Fix the cause, never work around a check"*; ArduPilot *"Do not remove or weaken existing tests"* | Đưa vào CLAUDE.md (ngưỡng `thresholds.yaml` chỉ đổi khi Tuan duyệt) |
| Eval agent | Anthropic: capability vs regression, code-grader trước, đọc transcript | harness-lab GĐ2 |

### 4.2 STLab đang có
`prepare-print.py` (kiểm hết rồi mới cắt lớp), 14 test trong `test_pushrod_arm.py` (có `test_no_hidden_parts`,
`test_worm_stl_socket_open` kiểm trên STL), `fc_cli.py` (exit code thật), `metrics.json` hồi quy, `/print-result` ghi kết quả in.

### 4.3 Khoảng trống
- Kiểm lỗ/hình học trên **STL** (kể cả support tự vẽ) nhưng chưa trên **G-code**: support/brim/“lấp khe” do slicer sinh
  chỉ thấy trong G-code. Đề xuất: đọc G-code trong .3mf, ở dải Z của lỗ trục kiểm không có đường đùn nằm trong vòng
  tròn lỗ (TODO: xác nhận `slice.py` xuất .3mf có kèm `Metadata/plate_N.gcode` – chưa kiểm).
- `check.py` dòng 106 và `metrics.py` dòng 48 vẫn **bỏ qua chi tiết `Visibility=False` không báo** – test dự án chặn
  được, nhưng dự án mới (cyberbrick-car…) chưa có test này.
- Test chỉ có ở pushrod-arm; `project-template/` chưa có `tests/` mẫu (TODO kiểm lại).
- Không có CI; mọi kiểm chạy tay hoặc qua Toolhub.

## 5. Tái lập & môi trường

| Công cụ | Repo dùng | Ghi chú |
|---|---|---|
| **uv** + `uv.lock` | LeRobot, Isaac Lab, dimos, HA (`uv run --no-sync pytest`) | Lock cứng; agent được dặn dùng `uv run`, không `pip` |
| **pixi** ([prefix-dev/pixi](https://github.com/prefix-dev/pixi) 7 898★ / BSD-3) | FreeCAD (`pixi.toml` 263 dòng); RoboStack đóng gói ROS 2 qua conda ([ros-humble](https://github.com/RoboStack/ros-humble) 171★ / MIT) | Hợp với phụ thuộc C++/hệ thống, chạy cả Windows |
| devcontainer | PX4, nav2, HA, ESPHome, dimos | Chủ yếu Linux |
| Nix flake | dimos, openai/codex | Không hợp Windows |
| Hook SessionStart dựng môi trường | ESPHome `.claude/settings.json` (chạy `script/setup` nếu chưa có venv, timeout 900 s) | Mẫu để STLab báo tình trạng môi trường đầu phiên |

**STLab:** FreeCAD 1.1.4 dùng Python đi kèm; `community/` ghim theo commit (`pins.tsv`) – đã tốt hơn nhiều repo về ghim
nguồn ngoài. Thiếu: lock cho venv Toolhub/scripts Python thường (TODO: kiểm `studio/` có `requirements.txt` ghim phiên bản
chưa). Không cần devcontainer/Nix (Windows, phần mềm GUI).

## 6. Quy trình con người + agent

| Thực hành | Nguồn | STLab |
|---|---|---|
| Con người chịu trách nhiệm, agent không tự đăng | HA *"Autonomous contributions are not accepted"*; KiCad cấm agent tự mở issue/MR; ArduPilot *"No AI in discussions"* | Đã có: "không tự đăng" (marketing), chỉ push khi kiểm ổn |
| Ghi nhận AI trong commit | Zephyr/KiCad/PX4 `Assisted-by:`; Isaac Lab, PX4 cấm `Co-Authored-By` AI | STLab dùng `Co-Authored-By` – repo riêng, không cần đổi |
| Hỏi trước khi đụng phần nguy hiểm | ArduPilot *"When to seek guidance first … affects flight safety"* | Có trong global CLAUDE.md (an toàn pin, điện áp) |
| Một nguồn quy tắc | Isaac Lab, xiaozhi: chi tiết ở docs, file agent chỉ trỏ | Một nguồn cho skill đã có; quy tắc thì trùng giữa memory ↔ CLAUDE.md (vd. "1 phiên giữ FreeCAD" ở cả 2 + inbox) |
| Nhật ký quyết định (ADR) | [adr.github.io](https://adr.github.io/) (Michael Nygard) – TODO: chưa thấy repo robotics nào trong bảng 1.1 dùng ADR trong file agent | Quyết định của Tuan nằm trong memory (`Why:` / `How to apply:`) – thực chất là ADR nhẹ, đủ dùng |
| Phân vai nhiều phiên | Claude Code worktree, Writer/Reviewer, agent teams (thử nghiệm) | 2 phiên cùng FreeCAD → cần khóa tài nguyên, không phải worktree |
| Giới hạn quyền | claude-code CI: runner chặn mạng + `--permission-mode auto`; HA MCP chỉ entity được phơi | Chỉ `allow`, không `deny`; cổng FilmCraft/LightCraft không token (đã ghi trong `apps.json`) |

## Đối chiếu sự cố STLab

| Sự cố (2026-10-24/25) | Loại lỗi | Cộng đồng chặn thế nào | STLab đã làm | Còn thiếu |
|---|---|---|---|---|
| Lỗ trục Worm có trong model, **support lấp lỗ trong file in** | Kiểm sai tầng (model ≠ artifact) | xiaozhi *"A successful build is not hardware validation"*; KiBot kiểm Gerber; Anthropic *"grade what the agent produced"* | Luật "mái lỗ kín", `test_worm_stl_socket_open` trên STL (commit `62fd3bd`) | Kiểm trên **G-code**; khai "lỗ chức năng" trong `print.yaml` để mọi dự án được kiểm, không chỉ pushrod-arm |
| FCStd bị Lưu từ GUI làm ẩn chi tiết; `check.py`/`metrics.py` **âm thầm bỏ qua** chi tiết ẩn | Lọc im lặng + file đổi ngoài phiên | KiCad MCP `save_project` từ chối ghi đè file đổi trên đĩa; KiCad AGENTS.md *"must be resaved via wxFormBuilder"*; HA *"prefer direct key access … so contract violations are surfaced instead of silently masked"* | `test_no_hidden_parts`, `safe_edit.save(gui_from=)` | `check.py`/`metrics.py`: chi tiết ẩn không nằm trong danh sách bỏ qua → **FAIL**; so số chi tiết với lần trước (metrics đã có số liệu, thêm luật) |
| **2 phiên Claude** cùng điều khiển FreeCAD | Tranh chấp tài nguyên chung | KiCad MCP GUI driver: token theo phiên; Claude Code: worktree (cho file), không có khóa cho app | Quy tắc "1 phiên giữ FreeCAD" (CLAUDE.md + memory) – chỉ là lời khuyên | **Hook PreToolUse** trên `mcp__freecad__.*` kiểm file khóa chứa `session_id` (hook nhận `session_id` trong input) |
| `freecadcmd` nuốt exception, **exit 0** | Thành công giả | Zephyr *"never work around a check"*; Building effective agents *"ground truth from the environment"* | `fc_cli.py` (exit code thật), prepare-print không đọc kết quả cũ (commit `d12078d`) | Hook PostToolUse trên Bash: lệnh có `freecadcmd` mà output chứa `Traceback`/`Exception` → exit 2 báo Claude (lưới an toàn khi gọi thẳng freecadcmd không qua `fc_cli.py`) |

## Đề xuất xếp theo lợi/công

CHỈ ĐỀ XUẤT – Tuan duyệt từng mục (quy tắc harness-lab). Lợi/công: Cao / Vừa / Thấp.

| # | Việc | Lợi | Công | Đánh đổi | Nơi sửa |
|---|---|---|---|---|---|
| H1 | Khóa FreeCAD theo phiên: PreToolUse hook trên `mcp__freecad__.*` (và Bash có `FreeCAD.exe`/RPC 9875) đọc `%TEMP%/stlab-freecad.lock`; khác `session_id` → deny kèm lý do; lệnh mở FreeCAD qua Toolhub ghi khóa | Cao (sự cố thật, lặp 2 lần) | Thấp–Vừa (~1 script Python + 6 dòng settings) | Khóa treo khi phiên chết → cần hết hạn (vd. 30 phút) hoặc lệnh `unlock` | hook (`claude-workspace/.claude/settings.json`) |
| T1 | `check.py`/`metrics.py`: chi tiết ẩn không khai `ignore` → FAIL; báo khi số chi tiết khác lần trước | Cao | Thấp | Phải khai `ignore` cho chi tiết ẩn cố ý (dao cắt, linh kiện tham khảo) | test / scripts robotics-cad |
| T2 | Kiểm trên G-code: đọc `.gcode` trong .3mf, kiểm "lỗ chức năng" khai trong `print.yaml` không bị đùn lấp | Cao (chặn đúng lỗi in hỏng) | Vừa | Cần xác nhận .3mf có G-code (TODO); thêm ~vài giây/bàn | test / `prepare-print.py` |
| C1 | CLAUDE.md gốc thêm 3 dòng: (a) báo "đã kiểm gì / chưa kiểm / cần in thử", không nói PASS khi chưa chạy; (b) không nới ngưỡng/xóa test để qua kiểm; (c) không sửa file sinh tự động (STL, .3mf, BOM.csv, metrics.json) bằng tay | Cao | Thấp | Thêm 3 dòng ngữ cảnh mỗi phiên | CLAUDE.md |
| H2 | PostToolUse hook trên Bash: lệnh `freecadcmd` mà output có `Traceback`/`Exception` → exit 2 kèm dòng lỗi | Vừa | Thấp | Có thể báo nhầm khi script in exception có chủ đích | hook |
| P1 | `permissions.deny` cho `Edit`/`Write` vào `claude-workspace/community/**` (TODO: kiểm cú pháp đường dẫn trong [permissions docs](https://code.claude.com/docs/en/permissions)) | Vừa | Thấp | `update-community.sh` chạy qua Bash nên không bị chặn – đúng ý | settings |
| C2 | Tách `tools/robotics-cad/CLAUDE.md` (156 dòng): giữ ~40 dòng lệnh + mục lục; chuyển quy ước FreeCAD CLI sang `.claude/rules/freecad-cli.md` (`paths: **/freecad/**, **/*.FCStd, tools/robotics-cad/scripts/**`); an toàn lắp → trỏ memory/ASSEMBLY; lịch sử thử → link research mục 7 | Vừa | Vừa | Mất 1 lần rà; rule `paths:` cần test xem có nạp đúng không | CLAUDE.md / rules |
| C3 | Mỗi CLAUDE.md dự án có khối "Lệnh kiểm" chép-dán + bảng "sửa X → chạy Y" (mẫu xiaozhi); thêm vào `project-template/CLAUDE.md` | Vừa | Thấp | – | CLAUDE.md / template |
| C4 | Mục "Claude hay làm sai ở STLab" (≤ 10 dòng) gom từ inbox đã duyệt, thay cho quy tắc rải rác | Vừa | Thấp | Phải duy trì khi duyệt inbox hàng tuần | CLAUDE.md |
| H3 | SessionStart hook in 3–5 dòng: FreeCAD đang mở? khóa thuộc phiên nào? `git status` ngắn, số mục inbox chưa xử lý | Vừa | Thấp | Tốn vài trăm token mỗi phiên | hook |
| A1 | Subagent `.claude/agents/print-reviewer.md`: chỉ đọc ảnh contact sheet + báo cáo prepare-print, cố bác bỏ PASS trước khi Tuan in | Vừa | Thấp | Thêm 1–2 phút/lần; dễ báo lỗi vụn → dặn chỉ báo lỗi ảnh hưởng in/lắp | subagent |
| E1 | harness-lab GĐ2 nhẹ: mỗi mục inbox đã duyệt → 1 test (code-grader) trong `harness-lab/regression/`; chưa làm chấm A/B | Vừa (lâu dài Cao) | Vừa | Đi quá phạm vi GĐ0–1 Tuan đã chốt → chờ Tuan | test / harness-lab |
| C5 | Gộp quy tắc trùng memory ↔ CLAUDE.md (vd. "1 phiên giữ FreeCAD" ở cả hai): memory giữ `Why`, CLAUDE.md giữ quy tắc | Thấp–Vừa | Thấp | – | memory / CLAUDE.md |
| R1 | Ghim venv Python của Toolhub/scripts bằng `uv.lock` (LeRobot/HA) | Thấp–Vừa | Vừa | Thêm công cụ uv | env |
| CI1 | GitHub Actions chạy ruff + test thuần Python (printability trên STL mẫu nhỏ trong repo) | Thấp | Vừa | FCStd không lên git → CI chỉ phủ phần nhỏ (đã kết luận ở freecad-automation-research mục 3.1) | CI |
| X1 | AGENTS.md + `CLAUDE.md` = `@AGENTS.md` (mẫu PX4) | Thấp (chỉ khi dùng Codex/Copilot) | Thấp | Không có lợi khi chỉ dùng Claude | – |

**Top 5 nên làm trước:** H1 (khóa FreeCAD) · T1 (chi tiết ẩn → FAIL) · C1 (3 dòng trung thực/không lách kiểm) · T2 (kiểm G-code) · C2+C3 (tách robotics-cad, khối lệnh kiểm).

## Bảng xem lại khi thương mại

| Nguồn | License | Dùng ở đây |
|---|---|---|
| INTI-CMNB/KiBot | AGPL-3.0 | Chỉ tham khảo mẫu CI KiCad |
| Kamel773/CAD_Code_Generation (CADPrompt) | Không có license | Chỉ đọc paper |
| SadilKhan/Text2CAD, filaPro/cad-recode | NOASSERTION – TODO đọc file LICENSE (có thể NC) | Chỉ tham khảo |
| Konnect (KiCad MCP bản Rust) | AGPL-3.0 (theo README mixelpixx) | Chưa dùng |
| ArduPilot, KiCad, Zephyr… AGENTS.md | GPL/Apache – chỉ trích dẫn ý | Không chép mã |

## Điểm chưa xác nhận (TODO)

- `slice.py` xuất .3mf có kèm G-code từng bàn không (`Metadata/plate_N.gcode`) – điều kiện cho T2.
- Cú pháp đường dẫn trong `permissions.deny` trên Windows (tương đối/tuyệt đối) – kiểm trước khi làm P1.
- `.claude/rules/` với `paths:` có nạp khi Claude chỉ chạy `freecadcmd` qua Bash (không Read file) không – docs nói nạp khi
  Claude làm việc với file khớp; với Bash có thể không → kiểm bằng `/context` trước khi tách C2.
- License thật của Isaac Lab, ESPHome, dimos, CadQuery, Text2CAD, cad-recode (API trả NOASSERTION).
- `project-template/` đã có thư mục `tests/` mẫu chưa; `studio/` có ghim phiên bản phụ thuộc chưa.
- Chỉ kiểm file ở **thư mục gốc** 21 repo; ros2/FreeCAD/MuJoCo có thể có hướng dẫn agent ở thư mục con hoặc trong CONTRIBUTING.
- Harness² (Google Research) – nguồn gốc ý tưởng harness-lab – chưa đọc lại bài gốc trong lần này.
- ★ của pytest-regressions chưa tra (hết hạn mức API không xác thực; máy không có `gh`).

## Nguồn

**File agent trong repo [nguồn gốc]:** [lerobot AGENTS.md](https://github.com/huggingface/lerobot/blob/main/AGENTS.md) ·
[PX4 AGENTS.md](https://github.com/PX4/PX4-Autopilot/blob/main/AGENTS.md), [PX4 .claude/skills](https://github.com/PX4/PX4-Autopilot/tree/main/.claude/skills), [PX4 .github/instructions](https://github.com/PX4/PX4-Autopilot/tree/main/.github/instructions) ·
[ArduPilot AGENTS.md](https://github.com/ArduPilot/ardupilot/blob/master/AGENTS.md) · [Isaac Lab AGENTS.md](https://github.com/isaac-sim/IsaacLab/blob/main/AGENTS.md) ·
[KiCad AGENTS.md](https://github.com/KiCad/kicad-source-mirror/blob/master/AGENTS.md) · [ESPHome AGENTS.md](https://github.com/esphome/esphome/blob/dev/AGENTS.md), [ESPHome .claude/settings.json](https://github.com/esphome/esphome/blob/dev/.claude/settings.json) ·
[HA AGENTS.md](https://github.com/home-assistant/core/blob/dev/AGENTS.md), [HA copilot-instructions](https://github.com/home-assistant/core/blob/dev/.github/copilot-instructions.md) ·
[xiaozhi-esp32 AGENTS.md](https://github.com/78/xiaozhi-esp32/blob/main/AGENTS.md) · [Zephyr AGENTS.md](https://github.com/zephyrproject-rtos/zephyr/blob/main/AGENTS.md) ·
[dimos AGENTS.md](https://github.com/dimensionalOS/dimos/blob/main/AGENTS.md) · [claude-code CLAUDE.md](https://github.com/anthropics/claude-code/blob/main/CLAUDE.md)

**Tài liệu chính thức [nguồn gốc]:** [agents.md](https://agents.md/) · [Claude Code best practices](https://code.claude.com/docs/en/best-practices) ·
[Claude Code memory](https://code.claude.com/docs/en/memory) · [Claude Code hooks](https://code.claude.com/docs/en/hooks) ·
[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) · [Copilot repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions) ·
[Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) ·
[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) ·
[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) ·
[HA MCP Server integration](https://www.home-assistant.io/integrations/mcp_server/)

**Công cụ/MCP/paper [nguồn gốc][API]:** [neka-nat/freecad-mcp](https://github.com/neka-nat/freecad-mcp) ·
[mixelpixx/KiCAD-MCP-Server](https://github.com/mixelpixx/KiCAD-MCP-Server) · [lamaalrajih/kicad-mcp](https://github.com/lamaalrajih/kicad-mcp) ·
[robotmcp/ros-mcp-server](https://github.com/robotmcp/ros-mcp-server) · [homeassistant-ai/ha-mcp](https://github.com/homeassistant-ai/ha-mcp) ·
[build123d](https://github.com/gumyr/build123d) · [CadQuery](https://github.com/CadQuery/cadquery) ·
[CADPrompt/CADCodeVerify](https://github.com/Kamel773/CAD_Code_Generation), [arXiv 2410.05340](https://arxiv.org/abs/2410.05340) ·
[Text2CAD](https://github.com/SadilKhan/Text2CAD) · [CAD-Recode](https://github.com/filaPro/cad-recode) ·
[KiBot](https://github.com/INTI-CMNB/KiBot) · [pixi](https://github.com/prefix-dev/pixi) · [RoboStack ros-humble](https://github.com/RoboStack/ros-humble) ·
[claude-code-action](https://github.com/anthropics/claude-code-action) (9 636★, MIT) · [ADR](https://adr.github.io/)

**Đối chiếu nội bộ STLab:** `CLAUDE.md`, `tools/robotics-cad/CLAUDE.md`, `harness-lab/README.md`, `harness-lab/inbox.md`,
`~/.claude/settings.json`, memory `kiem-tra-2-tang`, `tu-dong-luu-va-push`, `freecad-cli-truoc`,
`maker/pushrod-arm/freecad/tests/test_pushrod_arm.py`, `tools/robotics-cad/scripts/check.py` (dòng 106), `metrics.py` (dòng 48).
