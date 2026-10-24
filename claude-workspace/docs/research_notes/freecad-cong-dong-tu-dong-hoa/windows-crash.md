# FreeCAD GUI crash trên Windows (1.1.x, 26.3 RC): nguyên nhân + cách cộng đồng chẩn đoán

Ngày nghiên cứu: 2026-10-24. Phạm vi: Windows 10/11, FreeCAD 1.0 – 1.1.4, 26.3 RC.
Bối cảnh lab: FreeCAD 1.1.4, Windows 11, addon RobotCAD / LCInterlocking / Fasteners / SheetMetal / Gears / FreeCADMCP (RPC cổng 9875), file ~8 MB, STEP hãng có open shell, gửi Python qua XML-RPC.

Mốc phiên bản (nguồn chính thức, GitHub Releases API): 1.1.0 = 2026-03-25, 1.1.1 = 2026-04-14, 1.1.2 = 2026-07-23, 1.1.3 = 2026-07-25, 1.1.4 = 2026-09-28 (release note: "last planned maintenance release in the 1.1.x series"), 26.3rc1 = 2026-10-08, 26.3rc2 = 2026-10-18 — [GitHub releases](https://github.com/FreeCAD/FreeCAD/releases)

Ghi chú nguồn: wiki.freecad.org chặn bot (Anubis) khi fetch ngày 2026-10-24, nên các trang wiki được đọc qua bản mirror [FreeCAD-documentation](https://github.com/FreeCAD/FreeCAD-documentation) (trang Start_up_and_Configuration commit cuối 2025-01-15, có thể cũ hơn wiki live). Chi tiết đường dẫn crash.dmp / crash.log / thư mục versioned được kiểm trực tiếp trong source tag `1.1.4`.

## 1. Nguyên nhân crash hay gặp nhất trên Windows

### Takeaway
Trong 1.1.x, các nhóm nguyên nhân có bằng chứng rõ nhất là: (a) cấu hình/addon cũ khi nâng cấp (migration config, addon PySide2/Qt5, pip package lẫn vào `%APPDATA%\Python`), (b) GPU/OpenGL driver (đặc biệt NVIDIA RTX trên Win 11 gây chậm/treo cả máy), (c) bug core theo từng workbench (Sketcher, TechDraw, PartDesign, Spreadsheet) và hình học lỗi khi mở file, (d) code Python chạm document/Coin3D từ thread không phải GUI. Không tìm thấy bug crash nào riêng cho RobotCAD/LCInterlocking/SheetMetal/Gears trong 1.1.x.

### Cited Findings
**Addon / cấu hình cũ / Qt-PySide**
- #28627 (2026-03-25, Win 10, 1.1.0): crash ngay khi khởi động "every time". Log cho thấy module phụ thuộc PySide2 — dev 3x380V: "PySide2 dependency of some your modules. That will not work with Qt6". Nhưng chennes (dev chính) kết luận nguyên nhân thật là **code migration config** (gặp đường dẫn dài trong `%APPDATA%\FreeCAD` cũ, ném exception không bắt), "addon failures are being caught and handled as expected". Workaround: đổi tên `%APPDATA%\Roaming\FreeCAD` → khởi động sạch. Fix được hứa đưa vào 1.1.1; issue đóng 2026-03-30 (completed). Chính thức (dev), độ tin cao — [#28627](https://github.com/FreeCAD/FreeCAD/issues/28627)
- #28894 (2026-03-31, Win 11, 1.1): "DLL load failed while importing QtCore", GUI hiện một nửa. Nguyên nhân: PySide6/shiboken6 cài bằng `pip --user` nằm trong `%APPDATA%\Python\Python311\site-packages` xung đột với bản FreeCAD đóng gói. Maintainer adrianinsaval: "remove/rename your `%APPDATA%\Python\Python311\site-packages` folder ... use virtual environments". Đóng 2026-04-07 (người dùng xác nhận gỡ PySide6 là hết) — [#28894](https://github.com/FreeCAD/FreeCAD/issues/28894)
- Một người dùng khác (brummbrum, cùng thread #28627) báo nâng cấp 1.0.2→1.1 giữ cấu hình cũ gây "tons of errors" từ addon Help cũ và Addon Manager không đọc được cache (xóa cache rồi dựng lại) — ý kiến cá nhân, độ tin trung bình — [#28627](https://github.com/FreeCAD/FreeCAD/issues/28627)
- Fasteners: #32406 (2026-09-04, 26.3 weekly, Linux) crash khi đổi cỡ ren; maintainer nghi Fasteners WB; log có "PropertyPythonObject::Restore: blocked import of module 'FastenersCmd' during document restore. Only modules from FreeCAD or installed addons are permitted". Tác giả Fasteners (shaise) nói đã sửa hàm "unsafe" trong bản Fasteners mới; sau khi cập nhật, weekly 2026-09-30 không còn crash. Liên quan trực tiếp vì lab dùng Fasteners: **khi lên 26.3 phải cập nhật Fasteners** — [#32406](https://github.com/FreeCAD/FreeCAD/issues/32406)
- KiCadStepUp: #30113 (2026-05-12, open) "Crash when importing a KiCAD Board with KiCADStepUp addon" — ví dụ addon import gây crash (chỉ đọc tiêu đề) — [#30113](https://github.com/FreeCAD/FreeCAD/issues/30113)

**GPU / OpenGL / Coin3D**
- #29376 (2026-04-14, Win 11 build 26200, 1.1.0, **Confirmed, Priority: High, còn open**): sau 5–30 phút dùng, cả PC chậm tới mức phải reboot, kể cả model đơn giản; có trong 1.0.2, 1.1, 1.2 weekly. Syres916 (maintainer): ≥3 người dùng Windows với các card NVIDIA RTX khác nhau báo trên forum. Workaround cộng đồng: `Ctrl+Shift+Win+B` (reset driver đồ họa) giúp hồi phục; maintainer adrianinsaval gợi ý bật "Use software OpenGL" hoặc **đổi tên `bin/opengl32sw.dll` thành `bin/opengl32.dll`** (software rendering, "I don't recommend leaving that renamed unless required"); 2 người dùng báo đổi dll thì hết (chưa chắc chắn, theo dõi ngắn). Ghi chú: một người báo bật/tắt option "Use software OpenGL" không khác gì — [#29376](https://github.com/FreeCAD/FreeCAD/issues/29376)
- #23379 (2025-08-26, Win 11, 1.1.0dev, open, Needs confirmation): GUI không phản hồi, log `ARB::createContext: wglCreateContextAttribsARB() failed` / "No valid GL context found". Một người trên Arch xác nhận lỗi tương tự do driver NVIDIA lệch phiên bản → "not a FreeCAD issue but something driver/package related" (ý kiến cá nhân) — [#23379](https://github.com/FreeCAD/FreeCAD/issues/23379)
- Tài liệu Preferences: "Use software OpenGL — If checked, OpenGL will use the CPU instead of the GPU. This option is useful for troubleshooting graphics card and driver problems. Changing this option requires a restart" (Preferences → Display → 3D View). Cũng có option "Use OpenGL VBO" — [Preferences_Editor (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Preferences_Editor.md)
- 1.1.1 có backport "Gui: update CoinPtr to not use boost::intrusive_ptr" (#28623); 1.1.4 có "fix COIN3D_MICRO_VERSION regex for coin 4.0.10" (build-level) — [1.1.1](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.1), [1.1.4](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4)

**STEP / hình học lỗi / recompute nặng**
- 1.1.4 có fix "[Part] Fix seg fault when opening file with faulty geometry" (#31812, backport #31837) — liên quan trực tiếp tới file có STEP hãng open shell — [1.1.4 release](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4), [PR #31812](https://github.com/FreeCAD/FreeCAD/pull/31812)
- #33758 (2026-10-20, open, 27.1dev/Linux): export STEP có màu **làm sập cả app** (stack smashing trong OCCT `XCAFDoc_ColorTool::AddColor`) nếu `ShapeAppearance` Transparency nằm ngoài 0–1 (ví dụ ghi 60.0); FreeCAD vẫn lưu giá trị sai nên file crash mỗi lần export. Dễ xảy ra khi script/AI đặt transparency kiểu phần trăm — [#33758](https://github.com/FreeCAD/FreeCAD/issues/33758)
- #33183 (2026-10-03, 26.3dev macOS): file 7,2 MB crash ngay khi mở, cả safe mode; nguyên nhân TechDraw `QGICaption::snapToView`, trùng #33134, đã fix (#33135) trước 26.3 — [#33183](https://github.com/FreeCAD/FreeCAD/issues/33183)
- #33685 (2026-10-18, open): segfault trong `Document::recompute` (enforceRecompute) khi spreadsheet thay đổi sau các object dùng nó; #32732 (2026-09-16, open): VarSet lưu bán kính fillet gây crash — [#33685](https://github.com/FreeCAD/FreeCAD/issues/33685), [#32732](https://github.com/FreeCAD/FreeCAD/issues/32732)
- #29139 (2026-04-07, open, Priority High): "FreeCad 1.1 crashes at changing attachment offset" (chỉ đọc tiêu đề + label) — [#29139](https://github.com/FreeCAD/FreeCAD/issues/29139)

**Python từ thread không phải GUI**
- Source FreeCADMCP (neka-nat, `rpc_server.py`, nhánh main, đọc 2026-10-24): "FreeCAD documents and the Coin3D scenegraph are NOT thread-safe. Code run here executes off the GUI thread, so it must not touch them directly ... `doc.save()` or any `ViewObject` from this thread races the GUI thread" — [rpc_server.py](https://github.com/neka-nat/freecad-mcp/blob/main/addon/FreeCADMCP/rpc_server/rpc_server.py)
- #32877 (2026-09-22, open): `FreeCAD.openDocument(path, hidden=True)` đổi `ActiveDocument` sang doc ẩn; nếu đang edit Sketch rồi double-click sketch → crash; workaround gọi `App.setActiveDocument()` sau khi load. Liên quan khi script RPC mở file phụ trong lúc người dùng đang thao tác — [#32877](https://github.com/FreeCAD/FreeCAD/issues/32877)

### Inferences
- Với lab: thủ phạm Windows-specific có khả năng cao nhất là (1) driver NVIDIA/Intel → thử software OpenGL trước, (2) package pip lạ trong `%APPDATA%\Python\Python311\site-packages` (nếu từng `pip install --user` bằng Python 3.11 hệ thống), (3) addon chưa tương thích Qt6/PySide6.
- Rủi ro riêng của lab: script MCP đặt thuộc tính sai miền (transparency, placement) có thể tạo file "độc" crash lặp lại khi export.

### Gaps
- Không tìm thấy issue crash nào cho RobotCAD (2 issue cũ 2025 chỉ về cài đặt/container), LCInterlocking, SheetMetal, Gears trong 1.1.x — TODO: kiểm tracker từng addon nếu nghi ngờ.
- Không có thống kê định lượng "nguyên nhân nào phổ biến nhất"; xếp hạng trên là suy luận từ mẫu issue.
- Không tìm thấy nguồn chính thức về crash riêng GPU Intel/AMD trên Windows trong 1.1.x (chennes nói AMD của anh không bị #29376).

## 2. Công cụ chẩn đoán dev khuyến nghị

### Takeaway
Thứ tự cộng đồng/maintainer dùng: safe mode (`--safe-mode` hoặc Help → Restart in safe mode) → log file (`-l` / `--log-file`) → đổi tên thư mục cấu hình (versioned `%APPDATA%\FreeCAD\v1-1`) → software OpenGL → gỡ pip package lạ → bật/tắt addon từng cái → về bản weekly để xem đã fix chưa. Trên Windows, bản build MSVC tự ghi `crash.dmp` (minidump) và `crash.log` vào thư mục user data.

### Cited Findings
- Safe mode: thêm từ 1.0, "temporarily disables user configurations, addons, themes and other customizations to run FreeCAD in a 'factory reset' state for debugging" (PR #16858); vào bằng Help → Restart in safe mode, thoát bằng cách restart lần nữa; CLI `--safe-mode` — [Release notes 1.0 (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Release_notes_1.0.md), [Std_RestartInSafeMode (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Std_RestartInSafeMode.md)
- Mẫu báo lỗi GitHub yêu cầu "About Info (in Safe Mode)"; maintainer thường hỏi "Can you reproduce ... in the latest weekly in safe mode?" — [#30967](https://github.com/FreeCAD/FreeCAD/issues/30967), [#28627](https://github.com/FreeCAD/FreeCAD/issues/28627). Ví dụ diễn giải: #32406 "in safe mode it doesn't happen" → nghi addon (Fasteners) — [#32406](https://github.com/FreeCAD/FreeCAD/issues/32406)
- CLI (FreeCAD --help): `-l [--write-log]` "Writes FreeCAD.log to the user directory"; `--log-file arg` ghi log ra file tùy ý; `-u/--user-cfg`, `-s/--system-cfg` chọn file cấu hình khác; `--safe-mode`; `--keep-deprecated-paths` (giữ config ở đường dẫn cũ); `-c/--console` — [Start_up_and_Configuration (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Start_up_and_Configuration.md)
- Wiki gợi ý tách cấu hình bằng file .bat: `start FreeCAD.exe -u FreeCAD/user.cfg -s FreeCAD/system.cfg --write-log`; dev onekk khuyên cách này (thư mục user config riêng) trong #28627 — [Start_up_and_Configuration (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Start_up_and_Configuration.md), [#28627](https://github.com/FreeCAD/FreeCAD/issues/28627)
- Thư mục cấu hình versioned: source 1.1.4 ghi "Starting in FreeCAD v1.1, we switched to using a versioned config path"; tên thư mục `fmt::format("v{}-{}", major, minor)` → `v1-1`; migration "is NOT automatic" ở tầng App, Gui hỏi người dùng có migrate không. Máy lab đang có `%APPDATA%\FreeCAD\v1-1\` (user.cfg, system.cfg, Mod, Macro) và `%LOCALAPPDATA%\FreeCAD\cache` (kiểm 2026-10-24) — [ApplicationDirectories.cpp @1.1.4](https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/App/ApplicationDirectories.cpp)
- Minidump: `src/Main/MainGui.cpp` @1.1.4, khi `_MSC_VER`: "create a dump file when the application crashes" → `getUserAppDataDir() + "crash.dmp"`, dùng `MiniDumpWriteDump` (kiểu `MiniDumpNormal`) qua `SetUnhandledExceptionFilter`; đồng thời StackWalker ghi stack vào `UserAppData + "crash.log"` — [MainGui.cpp @1.1.4](https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/Main/MainGui.cpp)
- Report view: Preferences → General → Report view có "Redirect Python output" và "Redirect Python errors" (đưa print/traceback vào Report view) — [Report_view (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Report_view.md)
- Backtrace chính thức trong wiki Debugging chỉ có hướng dẫn gdb (Linux)/lldb (macOS), cần "debug build"; không có mục Windows — [Debugging (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Debugging.md)
- Software rendering: option "Use software OpenGL" (restart) hoặc đổi tên `bin\opengl32sw.dll` → `bin\opengl32.dll` (maintainer adrianinsaval, 2026-05-02, chỉ dùng tạm) — [#29376](https://github.com/FreeCAD/FreeCAD/issues/29376)
- Xung đột Python: đổi tên/xóa `%APPDATA%\Python\Python311\site-packages` (maintainer adrianinsaval, 2026-04-06) — [#28894](https://github.com/FreeCAD/FreeCAD/issues/28894)
- Treo khi khôi phục tài liệu (document recovery) sau crash: #30967 (Linux, 1.1.1, open) — recovery stall làm FreeCAD đóng băng lúc khởi động; dữ liệu recovery nằm trong thư mục cache versioned (`v1-1`). Dev tritao: để lấy stack khi treo, chạy dưới debugger rồi Ctrl-C + `bt` — [#30967](https://github.com/FreeCAD/FreeCAD/issues/30967)
- #30612 (2026-06-05): người dùng đề xuất gói "Stabilized Env" (CrashGuard, biến môi trường `PYTHONFAULTHANDLER=1`, full crash dump); maintainer maxwxyz trả lời "Please check out our AI policy", đóng **not_planned**. Không phải khuyến nghị chính thức — [#30612](https://github.com/FreeCAD/FreeCAD/issues/30612)

### Inferences
Checklist đề xuất cho lab (suy luận từ các nguồn trên, xếp theo chi phí thấp → cao):
1. Ghi lại: phiên bản (Help → About → Copy to clipboard), thao tác cuối, file. Xem `%APPDATA%\FreeCAD\v1-1\crash.log` và `crash.dmp` ngay sau crash (đường dẫn suy ra từ source: `getUserAppDataDir()` với 1.1 là thư mục versioned — TODO xác nhận bằng một crash thật, hiện máy lab chưa có file này).
2. Chạy từ console có log: `"C:\Program Files\FreeCAD 1.1\bin\FreeCAD.exe" --log-file D:\fc-logs\fc.log` (đường dẫn cài đặt mặc định thấy trong #28894/#30612; kiểm lại trên máy).
3. `--safe-mode`: nếu hết crash → nghi addon/cấu hình; nếu vẫn crash → nghi core/driver/file.
4. Nếu hết trong safe mode: chuyển addon từ `v1-1\Mod` sang thư mục khác (máy lab đã có `Mod-backup`) rồi trả lại từng cái; tắt FreeCADMCP đầu tiên vì nó chạy code trong GUI thread.
5. Nghi GPU (treo, chậm dần, vùng 3D đen, lỗi `wglCreateContextAttribsARB`): bật "Use software OpenGL" → restart; cập nhật driver; thử `Ctrl+Shift+Win+B`.
6. Lỗi import Qt/PySide/DLL: kiểm `%APPDATA%\Python\Python311\site-packages`.
7. Cấu hình hỏng: đổi tên `%APPDATA%\FreeCAD\v1-1` (không xóa) → khởi động sạch → copy lại `user.cfg` nếu ổn.
8. Crash theo file: mở bằng `FreeCADCmd` (không GUI) để tách lỗi hình học khỏi lỗi hiển thị; thử bản weekly/26.3 RC trong thư mục portable với `-u`/`-s` riêng trước khi báo lỗi.
9. Phân tích `crash.dmp`: mở bằng WinDbg / Visual Studio (công cụ Windows chung — không có hướng dẫn chính thức của FreeCAD, TODO).

### Gaps
- Không có trang wiki chính thức về đọc `crash.dmp` trên Windows; không rõ FreeCAD có phát hành file PDB cho bản release không — TODO.
- Không xác minh được wiki live (bị Anubis chặn); mirror có thể lệch.
- Chưa xác nhận bằng thực nghiệm `crash.dmp` thật sự xuất hiện trong `v1-1\` với bản installer 1.1.4.

## 3. Bug crash đã biết 1.1.0–1.1.4 (đã fix chưa) và MCP server gây treo

### Takeaway
1.1.1–1.1.4 chủ yếu vá crash cụ thể (migration config Windows, TechDraw khi load, drag-and-drop, hình học lỗi khi mở file); nhiều bug crash vẫn open và chỉ sửa ở nhánh dev/26.3. Với FreeCADMCP (neka-nat), treo GUI là vấn đề đã ghi nhận (issue #115 còn open) và các bản sửa từ 2026-08 đến 2026-09 đã thêm timeout, status không dùng GUI thread, và công cụ chạy headless.

### Cited Findings
**FreeCAD core**
- Fix trong 1.1.1 (2026-04-14): crash migration config Windows (#28627, chennes: "We'll get this merged and added to the 1.1.1 release"); "Part: fix crash when hovering over internal faces in Projection on Surface"; "Avoid LowerDistanceParameter exception to prevent MacOS crash" — [#28627](https://github.com/FreeCAD/FreeCAD/issues/28627), [1.1.1](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.1)
- Fix trong 1.1.2 (2026-07-23) và 1.1.3 (2026-07-25, cùng danh sách thay đổi): "TechDraw: prevent crash on document load"; "Fixes possible crashes in ComplexGeoDataPy::setElementName"; "Fix possible crash when opening by drag and drop"; "Fix possible crash in DrawViewPart"; "Part: Fix crash in wireEncirclesAxis"; "Fix crash in GeoFeaturePy::getGlobalPlacementOf"; "App: Get Addon name from Metadata" — [1.1.2](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2), [1.1.3](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3)
- Fix trong 1.1.4 (2026-09-28): "[Part] Fix seg fault when opening file with faulty geometry"; 2 bản vá bảo mật cho file FCStd độc hại — [1.1.4](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4)
- Đã fix trước 1.1.0: #28671 crash khi tìm "ToggleTransparency" trong Parameter Editor (Blocker, đóng 2026-03-26) — [#28671](https://github.com/FreeCAD/FreeCAD/issues/28671)
- Vẫn open (2026-10-24), có thể gặp trên 1.1.4: #29376 chậm/treo PC với NVIDIA (Win 11, High); #29139 crash khi đổi attachment offset (High); #29654 crash khi thêm offset cho SubShapeBinder; #32877 `openDocument(hidden=True)`; #23379 mất GL context — [#29376](https://github.com/FreeCAD/FreeCAD/issues/29376), [#29139](https://github.com/FreeCAD/FreeCAD/issues/29139), [#29654](https://github.com/FreeCAD/FreeCAD/issues/29654), [#32877](https://github.com/FreeCAD/FreeCAD/issues/32877), [#23379](https://github.com/FreeCAD/FreeCAD/issues/23379)
- 26.3 RC (2026-10): nhiều regression crash mới mở trên nhánh dev, ví dụ #33698 "Crash with 26.3rc2 when trying to set impossible fillets", #33685 segfault recompute + spreadsheet, #33461 Sketcher force close khi đổi dimension; phần lớn crash RC trên Linux là AppImage/fontconfig (#33377, #33431) — [#33698](https://github.com/FreeCAD/FreeCAD/issues/33698), [#33685](https://github.com/FreeCAD/FreeCAD/issues/33685), [#33461](https://github.com/FreeCAD/FreeCAD/issues/33461), [#33377](https://github.com/FreeCAD/FreeCAD/issues/33377)

**FreeCAD MCP (neka-nat/freecad-mcp; addon FreeCADMCP, cổng mặc định 9875)**
- Kiến trúc: `start_rpc_server(port: int = 9875)`; server XML-RPC chạy trên thread riêng, công việc GUI được đưa vào hàng đợi và chạy trên Qt main thread qua `QtCore.QTimer.singleShot(500, process_gui_tasks)`; `EXECUTE_CODE_TIMEOUT = 90` giây ("use execute_code_async for heavy OCCT ops"), trần `MAX_EXECUTE_CODE_TIMEOUT = 1800` — [rpc_server.py](https://github.com/neka-nat/freecad-mcp/blob/main/addon/FreeCADMCP/rpc_server/rpc_server.py)
- #115 (2026-08-09, **open**, Windows, FreeCAD 1.1.3): sau exception trong `execute_code` để lại object `FeaturePython` hỏng (không có Proxy, bug FreeCAD #31849), lệnh sau chạm vào object đó làm GUI dispatch treo vô hạn; mọi lệnh sau, kể cả `list_documents()`, timeout ("after waiting 4 minutes"); "The only recovery I found was fully restarting the FreeCAD application" — [#115](https://github.com/neka-nat/freecad-mcp/issues/115)
- #125 (2026-08-28, đóng 2026-09-05): `get_rpc_status` không trả lời được khi GUI thread kẹt vì `SimpleXMLRPCServer` xử lý một request mỗi lần; sửa bằng xử lý đồng thời (PR #124/#126/#128) — [#125](https://github.com/neka-nat/freecad-mcp/issues/125)
- PR #137 (merged 2026-09-10): `execute_code_headless` — chạy script "potentially crashing" trong process `freecadcmd` riêng "so a native crash does not terminate the GUI process and its unsaved documents"; báo crash native, timeout, stdout — [PR #137](https://github.com/neka-nat/freecad-mcp/pull/137)
- PR #141 (merged 2026-09-17): timeout theo từng lệnh cho `execute_code` vì "STEP import/export can outlast the fixed 90-second execute_code budget"; "Running GUI work still cannot be force-cancelled"; cần cập nhật cả addon — [PR #141](https://github.com/neka-nat/freecad-mcp/pull/141)
- Các sửa khác: #132 (timeout tính từ lúc bắt đầu chạy, không từ lúc vào hàng), #131 (`execute_code_async` có đường an toàn ghi document qua `commit()`), #149/#145 (kiểm phiên bản addon ↔ server, tránh "silent version skew"), #55 (open: print() mất do race StringIO/QTimer) — [repo issues](https://github.com/neka-nat/freecad-mcp/issues?q=freeze+OR+hang+OR+timeout)
- Các fork khác (mario-2015, LBurny/cadpilot, maximedns5) mô tả cùng mô hình: `execute_code` trên GUI thread, `execute_code_async` chỉ cho tính toán không chạm doc/GUI; maximedns5 nói Sketcher `.solve()`, `deleteAllGeometry()`, `movePoint()` trên sketch có ràng buộc "known to hang" solver và server chặn trước (nguồn thứ cấp: glama.ai listing, độ tin thấp-trung bình) — [glama maximedns5](https://glama.ai/mcp/servers/maximedns5/freecad-mcp/tools/execute_code_async), [glama ahelja/FreeCAD-MCP](https://glama.ai/mcp/servers/ahelja/FreeCAD-MCP)

### Inferences
- Nếu addon FreeCADMCP của lab cài trước 2026-09, có thể thiếu timeout per-call, status không kẹt, headless — nên kiểm phiên bản addon và server khớp nhau (#145).
- Treo khi gửi code qua RPC phần lớn không phải "crash" mà là GUI thread bị chặn (code chạy lâu, solver kẹt, object hỏng); dấu hiệu: Windows báo "Not Responding", RPC timeout.

### Gaps
- Không rõ "FreeCADMCP" lab dùng có đúng là neka-nat/freecad-mcp không (cổng 9875 trùng mặc định của neka-nat) — TODO kiểm `Mod\FreeCADMCP`.
- Không có tag release nào của neka-nat/freecad-mcp lấy được qua API (danh sách releases rỗng) — không ghim được phiên bản cụ thể.
- Không tìm thấy danh sách chính thức "known issues 1.1.4 trên Windows".

## 4. Giữ GUI ổn định khi tự động hóa

### Takeaway
Nguyên tắc nhất quán giữa nguồn chính thức và cộng đồng: document/Coin3D không thread-safe → chỉ chạm từ GUI thread, giữ mỗi lệnh GUI ngắn, đẩy việc nặng (STEP import, boolean lớn, kiểm tra) sang process `FreeCADCmd` riêng, để crash native không làm mất tài liệu chưa lưu.

### Cited Findings
- `FreeCADCmd`/`--console` là bản headless chính thức: "FreeCAD is usually built with two executables: a GUI-capable one ... and a headless one, called FreeCADCmd" — [Start_up_and_Configuration (mirror)](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Start_up_and_Configuration.md)
- FreeCADMCP: không chạm document/ViewObject từ worker thread; dùng `commit(fn)` để đưa phần ghi về GUI thread; `execute_code_async` cho OCCT nặng; `execute_code_headless` (process riêng) cho script có thể crash — [rpc_server.py](https://github.com/neka-nat/freecad-mcp/blob/main/addon/FreeCADMCP/rpc_server/rpc_server.py), [PR #137](https://github.com/neka-nat/freecad-mcp/pull/137)
- Việc GUI đang chạy "cannot be force-cancelled" → timeout chỉ giải phóng client, không cứu GUI — [PR #141](https://github.com/neka-nat/freecad-mcp/pull/141)
- Một exception giữa chừng có thể để lại object hỏng làm mọi lệnh sau treo — [#115](https://github.com/neka-nat/freecad-mcp/issues/115)
- `openDocument(hidden=True)` đổi ActiveDocument → gây crash khi người dùng đang edit; gọi `App.setActiveDocument()` lại sau đó — [#32877](https://github.com/FreeCAD/FreeCAD/issues/32877)
- Giá trị thuộc tính ngoài miền (Transparency > 1) được lưu im lặng và làm sập export STEP — [#33758](https://github.com/FreeCAD/FreeCAD/issues/33758)

### Inferences
Quy tắc đề xuất cho lab:
1. Lưu file (`doc.save()` hoặc bản sao) **trước** mỗi lô lệnh RPC; bật autosave/recovery.
2. Mỗi lệnh `execute_code` ngắn (vài giây), không vòng lặp dài; recompute lớn/STEP import → chạy trong `FreeCADCmd` subprocess (repo này đã có `fc_cli.py` theo commit d12078d), GUI chỉ mở kết quả.
3. Bọc code gửi vào GUI bằng `try/except` + `doc.openTransaction()/abortTransaction()` để không để object nửa vời (suy luận từ #115; TODO thử thực tế).
4. Không gọi API document/Gui từ `threading.Thread` tự tạo; nếu cần, dùng `QTimer.singleShot` hoặc `commit()` của FreeCADMCP.
5. Kiểm miền giá trị trước khi set (transparency 0–1, đơn vị mm/độ).
6. Không dùng `hidden=True` khi người dùng đang ở chế độ edit; hoặc set lại ActiveDocument.
7. Khi GUI "Not Responding" do RPC: chờ hết timeout; nếu vẫn kẹt → kill process, mở lại, dùng document recovery (lưu ý #30967: recovery có thể tự treo, khi đó đổi tên thư mục recovery trong cache `v1-1`).

### Gaps
- Không tìm được trang wiki chính thức (wiki live bị chặn) phát biểu trực tiếp "FreeCAD API không thread-safe"; phát biểu đang dẫn từ source FreeCADMCP (nguồn cộng đồng) — TODO tìm bài forum của dev (forum.freecad.org cũng có khả năng bị chặn bot).
- Chưa đo hiệu năng recompute file 8 MB trong FreeCADCmd so với GUI.
