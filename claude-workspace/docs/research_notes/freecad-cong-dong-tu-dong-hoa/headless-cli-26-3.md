# FreeCAD headless / FreeCADCmd và thay đổi ở 26.3 cho tự động hóa Python

Phạm vi: FreeCAD 1.1.4 (phát hành 2026-09-28, bản bảo trì cuối của dòng 1.1.x) trên Windows 11, chạy script qua `FreeCADCmd.exe`; so sánh với 26.3 (RC2 ngày 2026-10-18, bản chính thức dự kiến tháng 11/2026).
Ngày ghi chú: 2026-10-24. Ghi chú mức tin cậy: **[CAO]** = mã nguồn hoặc PR đã merge; **[TB]** = issue hoặc ý kiến maintainer; **[THẤP]** = ý kiến cá nhân hoặc suy luận.
Lưu ý về nguồn: wiki.freecad.org chặn bot (Anubis), nên mình đọc wiki qua bản mirror `FreeCAD/FreeCAD-documentation` và bản wikitext của Release notes 26.3 trong repo `Reqrefusion/FreeCAD-Documentation-Project`. Mã nguồn đọc trực tiếp ở các tag `1.1.4`, `26.3rc2` và `main` trên GitHub.

## 1. Lưu từ FreeCADCmd làm mất GuiDocument.xml và dữ liệu hiển thị (màu, Visibility, ShapeAppearance, thumbnail)

### Takeaway
Việc FreeCADCmd lưu mà không có GuiDocument.xml là thiết kế, không phải bug: ở chế độ headless không có Gui document nên cũng không có ViewProvider để lưu. Upstream không có PR nào "giữ dữ liệu view khi lưu từ CLI", kể cả ở 26.3. Thứ upstream sửa ở 26.3 là phía *mở file* trong GUI (Visibility và fit view, xem mục 2). Vậy nếu cần giữ màu, ShapeAppearance và thumbnail thì phải lưu từ một tiến trình có GUI.

### Cited Findings
- Wiki chính thức (Headless_FreeCAD, sửa lần cuối 2025-01-15) nói rõ: ở headless *"không thể tạo hoặc truy cập view provider"*. Có thể load `FreeCADGui`, nhưng *"không có cách truy cập GUI document vì nó sẽ không được tạo, do đó không tồn tại view provider"*. Thứ duy nhất làm được là tạo scenegraph bằng `Gui.subgraphFromObject(obj)` sau `Gui.setupWithoutGUI()`. **[CAO, official]** — [FreeCAD-documentation/wiki/Headless_FreeCAD.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Headless_FreeCAD.md)
- Wiki Start_up_and_Configuration: console mode có mọi module *"trừ module FreeCADGui"*, và *"các module phụ thuộc FreeCADGui cũng có thể không dùng được"*. **[CAO, official]** — [Start_up_and_Configuration.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Start_up_and_Configuration.md)
- Issue #28714 (jgenunez, 2026-03-27, đã đóng 2026-08-21) mô tả đúng tình trạng của lab: file .FCStd tạo bằng CLI có Document.xml nhưng không có GuiDocument.xml, nên GUI *"phải suy ra trạng thái render lúc mở"*. Một người bình luận (2026-06-21) đề xuất coi đây là *"thiếu trạng thái GUI restore"*, không phải file hỏng. **[TB]** — [issue #28714](https://github.com/FreeCAD/FreeCAD/issues/28714)
- Với Assembly, issue #28714 không đủ: trong file Assembly tạo headless rồi mở bằng GUI, `joint.ViewObject.Proxy` được unpickle thành số nguyên `1` thay vì `ViewProviderJoint`, nên `Assembly_ActivateAssembly` báo `AttributeError: 'int' object has no attribute 'redrawJointPlacements'`. Issue #33697 (2026-10-18) vẫn mở. Đã có PR #33768 ("lazy recovery" của joint view provider), nhưng mình chưa xác minh trạng thái merge của nó. **[TB]** — [issue #33697](https://github.com/FreeCAD/FreeCAD/issues/33697)
- 26.3 đổi cách chụp thumbnail: dùng camera riêng, khung vừa hình, home view và nền trong suốt (PR #32489). Phần này vẫn thuộc GUI. Mình không thấy nói tới thumbnail khi lưu từ CLI. **[CAO, official release notes]** — [Release_notes_26.3 (wikitext mirror)](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext)
- Lỗi cũ có liên quan: bộ Project Utility (gộp lại .FCStd) từng bỏ qua GuiDocument.xml làm mất màu, đã sửa ở 0.15 (rất cũ, chỉ để tham khảo). Màu cũng từng không xuất sang STEP được từ freecadcmd vì `ImportGui.export` cần GUI. **[TB, cũ]** — [tracker 1845](https://tracker.freecad.org/view.php?id=1845), [tracker 3165](https://tracker.freecad.org/view.php?id=3165)
- Khi chuyển từ 0.21 sang 1.x, `ShapeColor` đổi thành cây thuộc tính `ShapeAppearance`. Đây là thuộc tính của ViewProvider nên nằm trong GuiDocument.xml. **[TB, fork bên thứ ba]** — [zff.dev forward_comp #2](https://zff.dev/xwzCAD/FreeCAD21/pulls/2)

### Inferences
- **Xác nhận** đo đạc của lab (365 file xuống 108 file trong zip). GuiDocument.xml và mọi file ảnh/màu gắn với ViewProvider (ví dụ `*.DiffuseColor`, `thumbnails/Thumbnail.png`) chỉ do Gui::Document ghi. Không có Gui::Document thì các file đó không được ghi. Mình suy ra điều này từ wiki Headless; chưa đọc code `Gui::Document::SaveDocFile` để liệt kê đủ từng file. **[TB]**
- Các cách làm khả thi, xếp theo khuyến nghị:
  1. **Tách hai pha (khuyên dùng):** FreeCADCmd chỉ dựng hình và kiểm (nhanh, chạy trong CI). Bước "hoàn thiện", gồm màu, ShapeAppearance, thumbnail và render, chạy bằng `FreeCAD.exe <script>.py` (có GUI), rồi lưu từ GUI. Đánh đổi: chậm hơn và phải mở cửa sổ. Nếu file cũ đã có GuiDocument.xml thì vẫn giữ được.
  2. **Mở file cũ đã có view data, sửa bằng CLI, rồi tiêm lại GuiDocument.xml cùng các file màu từ bản cũ vào zip mới.** Đánh đổi: GuiDocument.xml tham chiếu object theo `name`, nên object mới sẽ không có view data và object bị xóa sẽ để lại entry thừa. Cách này giòn và mình **không tìm thấy nguồn cộng đồng nào khuyến nghị nó**. **[THẤP]**
  3. Đừng hy vọng 26.3 tự sửa: không có PR nào ghi view data từ CLI. TODO: theo dõi xem có issue/PR "save view properties headless" mới không.

### Gaps
- Chưa tìm thấy issue GitHub hay thread forum nào báo đúng "lưu từ FreeCADCmd làm mất ShapeAppearance/màu" ở 1.x; lý do khả dĩ là cộng đồng coi đây là hành vi đã biết. TODO.
- Chưa xác minh trạng thái PR #33768 (Assembly).

## 2. File lưu từ FreeCADCmd, mở trong GUI thì TẤT CẢ object bị ẩn (kể cả App.Visibility = False)

### Takeaway
**Đã biết, đã giải thích và đã sửa ở 26.3, nhưng KHÔNG backport về 1.1.x.** Nguyên nhân: khi restore mà không có GuiDocument.xml, ViewProvider mới tạo bị `hide()`, rồi giá trị đó bị đồng bộ ngược đè lên `App.Visibility`. Bản sửa nằm ở PR #28967 (merge 2026-04-13). PR #30906 (merge 2026-08-21) bổ sung việc tự fit view.

### Cited Findings
- Issue #28555 (aavogt, 2026-03-23, đóng 2026-04-13), tiêu đề *"setting .Visibility attribute while headless is mostly ignored"*. Script chạy `--console` đặt `Visibility=True` và in ra True, nhưng mở trong GUI thì in False và object bị ẩn. **[TB]** — [issue #28555](https://github.com/FreeCAD/FreeCAD/issues/28555)
- Phân tích nguyên nhân (kimimgo, CONTRIBUTOR, 2026-03-29): `App::DocumentObject::Visibility` mang status `Property::Output`. Khi restore, (1) `ViewProviderDocumentObject::startRestoring()` gọi `hide()` nên VP Visibility thành false; (2) `attach()` đồng bộ VP sang App, đè `pcObj->Visibility` thành false; (3) giá trị True đặt từ headless bị mất. **[TB, contributor]** — [issue #28555, bình luận](https://github.com/FreeCAD/FreeCAD/issues/28555)
- PR #28967 *"Gui: fix visibility not restored when opening headless-generated files"* (Bojan9597, mở 2026-04-01, hyarion merge 2026-04-13, commit 6be61a9) chặn lan truyền từ `hide()` bằng cờ User1 trong `startRestoring()`, và trong `finishRestoring()` đồng bộ App sang VP khi thiếu GuiDocument.xml. chennes chọn PR này thay cho #28715 vì *"ít code bằng một nửa, không giữ state thừa"*. Milestone 26.3 (trước đó gọi là 1.2). Không có nhãn backport. **[CAO]** — [PR #28967](https://github.com/FreeCAD/FreeCAD/pull/28967)
- Mã ở tag `26.3rc2` có đúng đoạn này trong `ViewProviderDocumentObject::finishRestoring()`: chú thích *"Sync VP visibility from App object in case no GuiDocument.xml was present"*, kèm `Visibility.setValue(obj->Visibility.getValue())` dưới `ObjectStatusLocker(User1)`. **[CAO, mã nguồn]** — [ViewProviderDocumentObject.cpp @26.3rc2](https://github.com/FreeCAD/FreeCAD/blob/26.3rc2/src/Gui/ViewProviderDocumentObject.cpp)
- PR #30906 *"Gui: fit view when GuiDocument.xml is missing"* (pieterhijma merge 2026-08-21, milestone 26.3) gọi `viewAll()` trên 3D view đầu tiên khi thiếu GuiDocument.xml, và thêm GUI regression test ở `src/Mod/Test/GuiDocument.py` (geometry visible giữ visible, hidden giữ hidden). Nó đóng #28714. **[CAO]** — [PR #30906](https://github.com/FreeCAD/FreeCAD/pull/30906)
- Phần còn sót (aavogt, 2026-05-08): sau khi sửa, `BooleanFragments` (BOPTools) vẫn không ẩn được, và `CCX_Results_Mesh` (FEM) cũng vậy. Tức là object có ViewProvider Python hoặc tự đổi visibility con vẫn có thể sai. **[TB]** — [issue #28555, bình luận 2026-05-08](https://github.com/FreeCAD/FreeCAD/issues/28555)
- Release notes của 1.1.1, 1.1.2, 1.1.3 và 1.1.4 không có #28967 hay #30906. Mục visibility duy nhất ở 1.1.4 là #31559 (icon visibility của link group), không liên quan. **[CAO]** — [release 1.1.4](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.4), [1.1.3](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3), [1.1.2](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.2), [1.1.1](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.1)
- Issue mới, cùng họ lỗi: #33675 (2026-10-17, đang mở), *"Hidden member of a Python group is shown again after reopening the file"*. **[TB]** — [issue #33675](https://github.com/FreeCAD/FreeCAD/issues/33675)

### Inferences
- **Xác nhận** đo đạc của lab (85/85 object bị ẩn, App.Visibility thành False), cả hiện tượng lẫn cơ chế. Trên 1.1.4 lỗi sẽ không được sửa, vì 1.1.4 là bản 1.1.x cuối cùng.
- Cách xử lý trên 1.1.4: sau khi mở trong GUI, chạy một macro đặt lại `o.ViewObject.Visibility = <giá trị mong muốn>` từ một manifest (ví dụ JSON do script CLI ghi ra), rồi lưu từ GUI. Không dùng được `App.Visibility` làm nguồn vì nó đã bị đè thành False. Một cách khác là tạo, hoặc mở rồi lưu lại, file trong `FreeCAD.exe` để có GuiDocument.xml. **[THẤP, suy luận]**

### Gaps
- Chưa rõ #28967 có xử lý object nằm trong `App::Part`/`Body` (visibility phân cấp) và `App::Link` hay không. Test của #30906 chỉ nói chung chung "visible/hidden geometry". TODO: thử bằng 26.3rc2 với model của lab.

## 3. FreeCADCmd trả exit code 0 dù script raise exception (và in thông báo gây hiểu lầm)

### Takeaway
**Đúng, và là thiết kế của mã nguồn ở cả 1.1.4 lẫn 26.3rc2.** `processFiles()` bắt mọi `Base::Exception`, chỉ in `Exception while processing file` rồi chạy tiếp, nên tiến trình thoát với code 0. Chỉ `SystemExit` (`sys.exit(n)`) được ném lên `main()` để thành exit code. Không có PR nào đổi chuyện này ở 26.3. Cách làm chuẩn: bọc `main()` trong `try/except`, gọi `sys.exit(1)` khi lỗi, và gọi `main()` ở cấp module (không dùng guard `__main__`).

### Cited Findings
- `src/App/Application.cpp` @1.1.4, `Application::processFiles`: file `.py` được chạy bằng `Interpreter().loadModule(fileNamePure)`, tức là **import**. Nếu import ném `Base::PyException` thì có nhánh `catch` *"if loading the module does not work, try just running the script (run in __main__)"* gọi `runFile(...)` **chạy lại lần nữa**. Bên ngoài, `catch (const Base::SystemExitException&) { throw; }` chuyển tiếp lên main, còn `catch (const Base::Exception& e)` chỉ `Console().error("Exception while processing file: %s [%s]")`. `.FCMacro`/`.FCScript` chạy thẳng bằng `runFile`. **[CAO, mã nguồn]** — [Application.cpp @1.1.4](https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/App/Application.cpp)
- Ở `26.3rc2` đoạn `.py`, gồm cả nhánh import rồi fallback `runFile`, giống hệt. Khác biệt duy nhất ở `processFiles` giữa 1.1.4 và main là thêm `.fcbak` và đổi format log. **[CAO]** — [Application.cpp @26.3rc2](https://github.com/FreeCAD/FreeCAD/blob/26.3rc2/src/App/Application.cpp)
- `src/Main/MainCmd.cpp` @1.1.4: `catch (SystemExitException& e) { exit(e.getExitCode()); }`, `catch (Base::Exception&) { exit(1); }`, `catch (...) { exit(1); }`. Nhưng exception của script đã bị nuốt ở tầng dưới nên không tới được đây. Ở 26.3, MainCmd thêm `WindowsCrashReporter::install(<UserAppData>/CrashReports)` trên MSVC, còn logic exit không đổi. **[CAO]** — [MainCmd.cpp @1.1.4](https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/Main/MainCmd.cpp), [MainCmd.cpp @main](https://github.com/FreeCAD/FreeCAD/blob/main/src/Main/MainCmd.cpp)
- `SystemExitException` (Base/Interpreter.cpp): `sys.exit(int)` cho đúng mã đó; `sys.exit("chuỗi")` cho 1; **`sys.exit()` không đối số cũng cho 1**, khác CPython (CPython cho 0). Theo commit năm 2016, exit code của `sys.exit()` được truyền lên shell. **[CAO, mã nguồn]** — [Interpreter.cpp @1.1.4](https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/Base/Interpreter.cpp); [mirror commit 2016](https://gitea.suzanne.soy/suzanne.soy/FreeCAD/commits/commit/0875dfad34f693598174fa0705a1387c11df01bb)
- Issue #31734 (Raminzed, 2026-08-03, đang mở): `FreeCADCmd myscript.py` **import** script, nên guard `if __name__ == "__main__": main()` không chạy gì. Kết quả là *"exit 0, nothing runs"*, để lại `__pycache__/*.pyc`. Cách tác giả đề xuất là `if __name__ == "__main__" or "FreeCAD" in sys.modules: main()`. bdieterm (CONTRIBUTOR, 2026-08-04) xác nhận và thêm: `freecadcmd ./this.py` sẽ chạy module easter-egg `this` của Python, không chạy file của bạn (tương tự `antigravity.py`); đuôi `.FCMacro`/`.FCScript` thì chạy bình thường. Hành vi này có từ năm 2007. Ngày 2026-08-19 lỗi *"vẫn còn"* trên weekly. Có thể dùng thẳng `python.exe` đi kèm FreeCAD để `import FreeCAD`. **[TB, contributor]** — [issue #31734](https://github.com/FreeCAD/FreeCAD/issues/31734); thread cũ [forum t=84908](https://forum.freecad.org/viewtopic.php?t=84908)
- Issue #31987 (2026-08-15, đang mở): `freecadcmd -c "<code>"` crash với *"filesystem error: status: File name too long"* nếu khoảng 255 byte đầu của đoạn code không có `/`, vì chuỗi code bị coi như đường dẫn file. flaviut (CONTRIBUTOR, 2026-09-30) cho rằng *"CLI Python của FreeCAD cần làm lại kiểu breaking"*; đây là ý kiến cá nhân, chưa có kế hoạch. **[TB]** — [issue #31987](https://github.com/FreeCAD/FreeCAD/issues/31987)
- Lỗi crash khi lưu: #33493 (2026-10-12, đang mở), file `part.FCStd` có thể bị mất nếu FreeCAD bị kill giữa lúc lưu. Điều này đáng lưu ý nếu wrapper dùng timeout và kill tiến trình. **[TB]** — [issue #33493](https://github.com/FreeCAD/FreeCAD/issues/33493)

### Inferences
- **Xác nhận** đo đạc của lab (exit 0 khi lỗi). "Thông báo gây hiểu lầm" nhiều khả năng do nhánh fallback: import lỗi thì `runFile` chạy **lần hai** với `__name__ == "__main__"`. Lần chạy hai có thể ném lỗi khác hoặc tạo side-effect hai lần (ghi file, tạo document thứ hai), rồi chỉ một dòng `Exception while processing file` được in ra. **[TB, suy từ mã]**
- Mẫu khuyên dùng cho lab (1.1.4 và 26.3 như nhau):
  ```python
  import sys, traceback
  def main(): ...
  try:
      main()
  except SystemExit:
      raise
  except BaseException:
      traceback.print_exc()
      sys.exit(1)          # SystemExit được FreeCADCmd chuyển thành exit code
  else:
      sys.exit(0)          # tránh rơi vào prompt tương tác; LƯU Ý sys.exit() không đối số = 1
  ```
  `sys.exit(0)` ở cuối còn chặn trường hợp RunMode "Cmd" mở prompt chờ stdin; mình suy ra điều này từ `runApplication()`, chưa thử. Nếu sợ `closeAllDocuments()` hoặc destructor treo/crash lúc thoát thì dùng `os._exit(code)` sau khi đã `doc.save()` và flush stdout (đánh đổi: không chạy cleanup). Cách lab đang dùng, `fc_cli.py` đọc một sentinel/JSON kết quả do script ghi ra, vẫn là lớp bảo vệ tốt nhất vì không phụ thuộc exit code. **[THẤP, khuyến nghị]**
- Nên đặt đuôi `.FCMacro` hoặc gọi `main()` ở cấp module để tránh bẫy import/chạy hai lần. Không đặt tên script trùng module chuẩn (`this.py`, `test.py`...).

### Gaps
- Không tìm thấy issue/PR nào riêng về "FreeCADCmd nuốt exception, exit 0" (tìm GitHub bằng "FreeCADCmd exit code", "freecadcmd exception return"). Có thể chưa ai báo; đây là ứng viên để lab báo lên upstream. TODO.

## 4. FreeCADGui.setupWithoutGUI() và render ảnh không mở cửa sổ

### Takeaway
`setupWithoutGUI()` chỉ khởi tạo phần Coin/Inventor của FreeCADGui (các node, type system), để dùng được `subgraphFromObject()` và pivy. Nó **không** tạo Gui document hay ViewProvider. Trên Windows, cách đáng tin nhất để có ảnh giống GUI là chạy `FreeCAD.exe` (GUI) với script, gọi `ActiveView.saveImage()`, rồi tự thoát. Render thuần headless bằng `SoOffscreenRenderer` vẫn là issue mở, các cách cộng đồng đưa ra *"dường như không chạy"*.

### Cited Findings
- Wiki Headless_FreeCAD (official): sau `Gui.setupWithoutGUI()` chỉ có `Gui.subgraphFromObject(obj)`, *"không có cách truy cập GUI document… không tồn tại view provider"*. **[CAO]** — [Headless_FreeCAD.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Headless_FreeCAD.md)
- Wiki Embedding_FreeCADGui: `setupWithoutGUI()` dùng khi nhúng scenegraph FreeCAD vào ứng dụng Qt riêng (viewer pivy `sogui`/`quarter`, `viewer.setSceneGraph(FreeCADGui.subgraphFromObject(obj))`). Trang dẫn thread *"Using Gui functions without Gui.showMainWindow() in python script"*. Ví dụ dùng PyQt4 nên đã rất cũ. **[CAO nhưng cũ]** — [Embedding_FreeCADGui.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Embedding_FreeCADGui.md); [forum t=12575](https://forum.freecadweb.org/viewtopic.php?t=12575)
- Issue #13356 *"CLI: User can't generate an image without using GUI"* (sliptonic, maintainer CAM, 2024-04-07, **vẫn mở**): *"vấn đề đã được nêu và xử lý nhiều lần trên forum. Các giải pháp hiện có dường như không chạy."* Ví dụ đi theo hướng `Shape.writeInventor()`, `SoDB.readAll`, `SoOffscreenRenderer(viewport).render(root)`, và *"luôn trả 0"*. Issue dẫn các thread forum t=33389, t=14691, t=78314, t=32500, t=5082. **[TB, maintainer]** — [issue #13356](https://github.com/FreeCAD/FreeCAD/issues/13356)
- Issue #5710 (từ năm 2017, đang mở): TechDraw không xuất SVG/PDF headless được. **[TB]** — [issue #5710](https://github.com/FreeCAD/FreeCAD/issues/5710)
- Issue #31987 (2026-08-15) gọi `freecadcmd -c` cộng `FreeCADGui.showMainWindow()` dưới `xvfb-run` là *"kỹ thuật có tài liệu để tạo thumbnail/screenshot headless"* (Linux AppImage 1.1.3). Nhưng nó crash nếu code truyền qua `-c` không có `/` ở khoảng 255 byte đầu; truyền qua file `.py` thì không dính lỗi này. **[TB]** — [issue #31987](https://github.com/FreeCAD/FreeCAD/issues/31987)
- Std_ViewScreenShot (official): `Gui.ActiveDocument.ActiveView.saveImage('C:/temp/test.png',1656,783,'Current')`. Phương thức mặc định là *offscreen* (có anti-alias); "Offscreen (Old)" không chạy trên nhiều hệ Linux mới vì phụ thuộc driver. **[CAO]** — [Std_ViewScreenShot.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Std_ViewScreenShot.md)
- Thread forum "Screenshot via script" (t=53959). Mình chưa đọc nội dung chi tiết. — [forum t=53959](https://forum.freecad.org/viewtopic.php?t=53959)
- Một dự án bên thứ ba (dcc-mcp-freecad PR #52) đánh dấu render_view là `host_limited` khi không có FreeCADGui, và ghi chú rằng tắt notification area của FreeCAD giúp tránh deadlock dưới Qt platform `offscreen`. **[THẤP, bên thứ ba]** — [dcc-mcp-freecad PR #52](https://github.com/dcc-mcp/dcc-mcp-freecad/pull/52)
- Một script cũ (mailing list, khoảng 2010) dùng `mw.showMinimized()` trước khi lưu ảnh. **[THẤP, rất cũ]** — [free-cad mailman](https://sourceforge.net/p/free-cad/mailman/message/25885312/)

### Inferences
- **Xác nhận** đo đạc của lab (setupWithoutGUI không có ViewProvider hay getDocument).
- Khuyến nghị trên Windows 11 là **`FreeCAD.exe render_script.py`** (script truyền như file, GUI chạy nó sau khi main window đã lên). Trong script: `doc = App.openDocument(...)`, đặt màu và camera qua `Gui.ActiveDocument.ActiveView`, `Gui.updateGui()`, `saveImage(path, w, h, 'White')`, rồi `os._exit(0)` (hoặc `Gui.getMainWindow().close()`). Đánh đổi: cửa sổ nháy lên vài giây và cần desktop session (không chạy được trong service/SSH không có desktop). Mình thử nghiệm `--safe-mode` để tránh addon làm chậm; chưa kiểm chứng. **[THẤP, suy luận]**
- `QT_QPA_PLATFORM=offscreen` trên Windows: Qt có plugin `offscreen`, nhưng việc Coin/OpenGL có render được hay không thì chưa có nguồn xác nhận. TODO: thử.
- Trên Linux, `xvfb-run` cộng GUI là con đường cộng đồng hay dùng (theo #31987).
- `SoOffscreenRenderer` qua pivy từ FreeCADCmd: không có màu ViewProvider (chỉ có shape), và có báo cáo `render()` trả 0, nên **không khuyên dùng**.

### Gaps
- Chưa đọc trực tiếp các thread forum t=33389, t=78314 (wiki/forum chặn bot). TODO.
- Chưa có nguồn chính thức nào khuyến nghị một cách render headless trên Windows.

## 5. FreeCAD 26.3: thay đổi ảnh hưởng tới Python API, headless, Assembly, định dạng file, CLI

### Takeaway
26.3 là bản kế tiếp 1.1 (trước gọi là 1.2), với cách đánh số mới theo lịch. RC1 ra 2026-10-08, RC2 ngày 2026-10-18, bản chính thức dự kiến tháng 11/2026. Release notes **chưa liệt kê mục "Removed/Changed Python API"** (các mục còn trống). Với tự động hóa, các thay đổi đáng chú ý nhất là: sửa Visibility/fit view khi mở file CLI, chụp thumbnail kiểu mới, hỗ trợ OCC 8, typing stubs, fine-grained recompute (thử nghiệm), và đổi layout gói Windows sang `bin\freecad.exe` (từ weekly 2026-10-14). Mã xử lý CLI script và exit code **không đổi**.

### Cited Findings
- Về đánh số phiên bản, RC1 ghi: *"26.3 follows 1.1. Nothing was skipped and nothing was renamed. FreeCAD has moved to three releases per year on fixed dates with calendar-based version numbers, so the next releases will be 27.1, 27.2 and 27.3."* RC1 ra 2026-10-08, *"final release targeted for November"*. **[CAO, official]** — [26.3rc1](https://github.com/FreeCAD/FreeCAD/releases/tag/26.3rc1)
- RC2 (2026-10-18): *"Some defaults and behaviours changed, so it is worth reading the release notes before opening older documents with this build. Please do not use a release candidate for production work, and keep backups."* Vẫn còn blocker mở. Weekly build hiện mang số 27.1.0-dev. **[CAO]** — [26.3rc2](https://github.com/FreeCAD/FreeCAD/releases/tag/26.3rc2)
- Release notes 26.3 (bản nháp đầu trang ghi *"under development"*): các mục *Removed Python API* và *Changed Python API* trống. *New Python API* chỉ có trình sinh typing stub `.pyi` cho phần C++/PyCXX (PR #29334). **[CAO, nhưng tài liệu chưa xong]** — [Release_notes_26.3.wikitext](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext)
- Các mục Core liên quan tới script (cùng nguồn): hỗ trợ OpenCascade 8 nhưng vẫn tương thích OCC 7 (PR #25502); **fine-grained recomputes** theo phụ thuộc thuộc tính, thử nghiệm, bật bằng preference (PR #25603); thumbnail dùng camera riêng, home view, nền trong suốt (PR #32489); mở được `.FCBak` trực tiếp (PR #28454, `processFiles` cũng nhận `.fcbak`); macro được phép là thư mục (PR #27005); bỏ preference "Using undo/redo in documents" (PR #30616); CMake cảnh báo Qt5 sắp bị bỏ (PR #30222). **[CAO]** — [Release_notes_26.3.wikitext](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext)
- Assembly 26.3: Snapshot (lưu/khôi phục placement và visibility, PR #25384); joint Rigid Group (PR #29605); kéo được phần chưa grounded (PR #30998); Link Array trong Assembly; Simulation xuất video qua PyAV thay cho OpenCV (PR #30333); solver message trong task panel (PR #24623). Không thấy ghi thay đổi API Python của Assembly. **[CAO]** — [Release_notes_26.3.wikitext](https://github.com/Reqrefusion/FreeCAD-Documentation-Project/blob/main/wiki/Release_notes_26.3.wikitext)
- Đổi tên/bỏ thuộc tính có thể làm vỡ script: BIM bỏ `Cut Distance` của SectionPlane (PR #32644); CAM bỏ `AddTipLength` của Drilling (PR #32711); giá trị `CutPattern` của Slot đổi tên thành `Bidirectional`/`Directional` và bỏ `LayerMode` (PR #25867); Tapping gộp vào Drilling (PR #27506). **[CAO]** — cùng nguồn
- Addon Manager: bỏ danh sách `ALLOWED_PYTHON_PACKAGES.txt`, thay bằng constraints file theo từng phiên bản Python và không gọi PyPI trực tiếp (AddonManager PR #455/#345). Việc này ảnh hưởng tới cách cài thư viện pip cho script. **[CAO]** — cùng nguồn
- Gói Windows: release weekly-2026.10.07 ghi chạy `\FreeCAD.exe`, còn weekly-2026.10.14 và 10.21 ghi `\bin\freecad.exe`. Chưa rõ bản 26.3 final dùng layout nào. **[TB]** — [weekly-2026.10.21](https://github.com/FreeCAD/FreeCAD/releases/tag/weekly-2026.10.21), [weekly-2026.10.07](https://github.com/FreeCAD/FreeCAD/releases/tag/weekly-2026.10.07)
- Lỗi RC2 liên quan script: BIM legacy IFC importer lỗi với IfcOpenShell 0.8.5 đi kèm (#33854, 2026-10-24). **[TB]** — [issue #33854](https://github.com/FreeCAD/FreeCAD/issues/33854)
- Lời kêu gọi chính thức: dev addon/macro nên build thử với nhánh `releases/FreeCAD-26-3` (tạo ngày 2026-09-30) và báo những gì bị vỡ. **[CAO]** — [Discussion #32821](https://github.com/FreeCAD/FreeCAD/discussions/32821)
- Blog chính thức có bài "top 20 tính năng 26.3" (2026-08-14), không nói về Python API. — [blog.freecad.org](https://blog.freecad.org/2026/08/14/freecad-26-3-top-20-new-features-talk/)

### Inferences
- Các script của lab dùng Part/PartDesign/Assembly cơ bản: chưa thấy breaking change nào được công bố. Rủi ro chính là hành vi OCC 8 (nếu bản build Windows chuyển sang OCC 8; TODO kiểm `FreeCAD.Version()`) và đường dẫn exe đổi sang `bin\`. Nên để đường dẫn exe trong biến môi trường hoặc cấu hình, không hard-code.
- Nên giữ 1.1.4 cho công việc thật cho tới 26.3.0 final. Có thể chạy song song 26.3rc2 dạng portable để chạy thử bộ `prepare-print.py`.

### Gaps
- Phiên bản Python, Qt và OCC trong gói Windows 26.3: TODO (không tìm thấy trong release notes).
- Mục Removed/Changed Python API của release notes chưa được điền, nên chưa thể kết luận là "không có breaking".

## 6. Tùy chọn dòng lệnh (--safe-mode, -t, --pass, -l/--log-file) theo ghi nhận cộng đồng

### Takeaway
Danh sách tùy chọn chính thức (wiki, đến bản 1.0) là: `-c`, `-l/--write-log`, `--log-file`, `-u`, `-s`, `-t/--run-test`, `-r/--run-open`, `-M`, `-P`, `--single-instance`, `--safe-mode`, `--pass`, `--response-file`, `--dump-config`, `--get-config`, `--set-config`, `--keep-deprecated-paths`. Ghi nhận cộng đồng: `-t` với một số test suite crash do PySide 6.11; `-c` coi code như tên file (#31987); file `.py` bị import thay vì chạy (#31734).

### Cited Findings
- `FreeCAD --help` (1.0, wiki): `-t [--run-test] arg` *"use 0 (zero) to run all tests. If no argument is provided then return list of all available tests"*; `-r` giống `-t` nhưng *"Keeps UI open"*; `--safe-mode` *"Force enable safe mode"*; `--pass arg` *"Ignores the following arguments and pass them through to be used by a script"*; `-l` ghi FreeCAD.log vào thư mục user; `--log-file` ghi ra file tùy ý. Tùy chọn có thể viết `--opt arg` hoặc `--opt=arg`. `--get-config` hiện popup và *"The `--console` flag is not honored"*. **[CAO, official]** — [Start_up_and_Configuration.md](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Start_up_and_Configuration.md)
- Wiki: FreeCADCmd tương đương `FreeCAD --console`; có thể truyền code qua stdin (`FreeCAD --console <<EOF`). **[CAO]** — cùng nguồn
- Issue #29311 *"FreeCADCmd -t TestArch --safe-mode crashes"* (đóng 2026-04-12): SIGSEGV, maintainer marioalexis84 (MEMBER, 2026-04-16) quy cho *"PySide 6.11"*. **[TB]** — [issue #29311](https://github.com/FreeCAD/FreeCAD/issues/29311)
- Ví dụ cộng đồng dùng `--console --safe-mode < script.py` (đọc stdin) để tái hiện lỗi (#28555). **[TB]** — [issue #28555](https://github.com/FreeCAD/FreeCAD/issues/28555)
- Issue #32326 (macOS 1.1.3, đã đóng): tạo mesh Gmsh/Netgen crash khi chạy headless (freecadcmd) mà không có traceback hay crash log. Nó cho thấy crash native ở CLI có thể không để lại gì; 26.3 thêm WindowsCrashReporter cho bản build MSVC. **[TB]** — [issue #32326](https://github.com/FreeCAD/FreeCAD/issues/32326), [MainCmd.cpp @main](https://github.com/FreeCAD/FreeCAD/blob/main/src/Main/MainCmd.cpp)

### Inferences
- `--pass` là cách sạch để truyền tham số vào script, ví dụ `FreeCADCmd.exe build.py --pass --out D:\x.FCStd`; script đọc `sys.argv` sau `--pass`. Mình chưa kiểm hình dạng chính xác của `sys.argv` trong 1.1.4 (TODO). Biến môi trường là phương án thay thế an toàn.
- `--safe-mode` phù hợp cho CI vì tắt addon/macro người dùng. Đánh đổi: nếu script cần addon (ví dụ fasteners) thì phải dùng `-M` để chỉ đường dẫn module.
- `--log-file <path>` cộng mẫu `sys.exit(code)` ở mục 3 là cách để wrapper vừa có log vừa có exit code đúng.

### Gaps
- Trang Start_up_and_Configuration mới cập nhật tới bản 1.0. Chưa xác minh 1.1.4/26.3 có thêm hay bớt tùy chọn nào (TODO: chạy `FreeCADCmd.exe --help` trên máy lab và lưu lại).
- Chưa tìm thấy thảo luận cộng đồng cụ thể nào về `-l` hay `--log-file` trên Windows.
