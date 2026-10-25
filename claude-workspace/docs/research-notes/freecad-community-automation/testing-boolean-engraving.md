# FreeCAD tự động hóa: testing/CI, boolean với STEP hãng, khắc chữ cho in 3D

Ghi chú nghiên cứu, ngày 2026-10-24. Bối cảnh: FreeCAD 1.1.4, Windows, Python. Mã nguồn được đọc từ nhánh `main` của FreeCAD trên GitHub vào ngày 2026-10-24, nên có thể khác chút ít so với tag 1.1.4 (TODO: đối chiếu lại với tag `1.1.4`).
Độ tin cậy: **Cao** = mã nguồn hoặc tài liệu chính thức; **TB** = diễn đàn/tracker hoặc dự án cộng đồng; **Thấp** = một người dùng nói, hoặc là suy luận.

## A. Testing / CI cho model CAD

### Takeaway
`FreeCADCmd -t <module>` chạy `unittest`, và script khởi động test (`src/App/FreeCADTest.py`) gọi `sys.exit(0 if wasSuccessful() else 1)`. Điều này khớp với số đo của lab (thất bại → exit 1). Hiện không có "framework test model CAD" nào phổ biến cho FreeCAD. Cách thực dụng nhất: tự viết module `Test*.py` dùng `unittest`, mở `.FCStd` rồi assert volume/bbox/khe hở/`isValid()`, chạy bằng `FreeCADCmd -t`. Các dự án CI cộng đồng (fcbot) mới ở mức export file, chưa kiểm yêu cầu thiết kế.

### Cited Findings
- **Exit code (Cao, mã nguồn main, 2026-10):** `src/App/FreeCADTest.py` là init script thứ 3, chỉ chạy ở chế độ test không có GUI. Nó gọi `TestApp.RunConfiguredTextTest()`, log "FreeCAD test done", rồi `sys.exit(0 if testResult.wasSuccessful() else 1)`. → **Khớp** với số đo của lab — [FreeCADTest.py](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/App/FreeCADTest.py)
- **Lịch sử (TB):** commit năm 2016 đổi script test sang trả exit 1 khi có test fail. Lúc đó dùng `os._exit()` vì `SystemExitException` của interpreter nuốt `sys.exit()`. Bản main hiện tại đã dùng lại `sys.exit` (xem dòng trên) — [commit mirror gitea](https://gitea.suzanne.soy/suzanne.soy/FreeCAD/commit/272cbd198d88cc2036e8dc2c2aa4db207e93139f)
- **Hàm `Test.TestText(s)` / `Test(s)` trong `src/Mod/Test/TestApp.py` không thoát process.** Hàm này chỉ chạy `unittest.TextTestRunner(stream=sys.stdout, verbosity=2)` rồi trả `retval`. Vì vậy nếu gọi test từ script Python của mình (không qua `-t`), mình phải tự `sys.exit(0 if r.wasSuccessful() else 1)` (Cao) — [TestApp.py](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Test/TestApp.py)
- **Wiki Testing (Cao, chính thức nhưng có phần cũ — danh sách test "as of 0.15"):** chạy tất cả bằng `freecad --run-test 0`, một module bằng `freecad -t TestDraft`, console bằng `freecad -c -t TestPartDesignApp`. Từ Python: `import Test, TestFemApp; Test.runTestsFromModule(TestFemApp)`, `Test.runTestsFromClass(...)`. `FreeCAD.__unit_test__` liệt kê các module test; ở console mode thiếu test GUI (tên kết thúc bằng "Gui") — [wiki Testing (mirror docs)](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Testing.md)
- **Headless (Cao):** wiki Headless_FreeCAD nêu `FreeCADCmd -t 0` để chạy toàn bộ test suite, và `-t TestArch` cho một module. Các module trong `Mod/` có thể không import được từ Python thường nếu chưa thêm path vào `sys.path` — [Headless FreeCAD](https://wiki.freecad.org/Headless_FreeCAD)
- **Trong file test Draft:** test chạy được bằng cả `FreeCAD` lẫn `FreeCADCmd`, nhưng ở console "some functions cannot be tested as the view providers are not available" (Cao, bản mirror) — [TestDraft.py mirror](https://huggingface.co/AbdulElahGwaith/FreeCAD/blob/main/src/Mod/Draft/TestDraft.py)
- **CI của chính FreeCAD:** chạy `FreeCADCmd -t 0` trên thư mục build và lần nữa sau khi install (TB, xem qua mirror bên thứ ba) — [CI_master.yml mirror](https://gitverse.ru/gbykov/FreeCAD/content/main/.github/workflows/CI_master.yml); [wiki Continuous Integration](https://wiki.freecad.org/Continuous_Integration)
- **fcbot (cá nhân, TB):** CI cho file FreeCAD, lấy cảm hứng từ KiBot. Nó xuất STEP/STL/PDF TechDraw/PNG theo cấu hình YAML, có Docker image `ghcr.io/asymworks/fcbot` và GitHub Action `asymworks/fcbot@v0`. "currently supports FreeCAD 1.0 running on Debian Testing using Python 3.13". Repo có 3 sao, 15 commit, không có release → còn sơ khai, **không kiểm yêu cầu thiết kế** — [asymworks/fcbot](https://github.com/asymworks/fcbot)
- **Docker:** wiki có trang "FreeCAD Docker CLI mode" (image `amrit3701/freecad-cli`, không GUI). Trang ghi là chưa hoàn thiện và image dùng Python 3.8 → đã cũ (TB) — [FreeCAD Docker CLI mode](https://wiki.freecad.org/FreeCAD_Docker_CLI_mode)
- **Cạm bẫy CI tự dựng:** một người dùng GitLab gặp trường hợp build FreeCAD xong, nhưng binary test abort ở bước test do lỗi thư viện (TB) — [GitLab forum](https://forum.gitlab.com/t/build-successful-but-running-binary-in-test-stage-fails/55866)
- **Bên build123d/CadQuery:** chỉ thấy các công cụ MCP/wrapper báo volume, area, tâm khối, bbox lấy giải tích từ B-rep (không lấy từ mesh) để làm "oracle" so sánh. Không tìm được hướng dẫn regression-test chính thức (Thấp/TB) — [build123d-mcp PyPI](https://pypi.org/project/build123d-mcp/0.3.54/); [caid PyPI](https://pypi.org/project/caid/)

### Inferences
- Mẫu test đề xuất cho lab (suy luận): `TestStlabModels.py` dùng `unittest.TestCase`. Trong `setUpClass` gọi `App.openDocument(path)` rồi `doc.recompute()`. Các assert:
  - không có object nào ở trạng thái `Invalid`/touched sau recompute;
  - `shape.isValid()`;
  - `shape.Volume` nằm trong ±1 % so với giá trị tham chiếu lưu trong YAML;
  - `BoundBox` nằm trong kích thước bàn in A1 (TODO: lấy kích thước bàn từ profile máy, không ghi cứng);
  - khe hở giữa các chi tiết: `a.Shape.distToShape(b.Shape)[0] >= clearance_mm`;
  - va chạm: `a.Shape.common(b.Shape).Volume < 1e-6`.
  
  Chạy bằng `FreeCADCmd -t TestStlabModels` (đặt module vào `Mod/` hoặc thêm vào `sys.path`), sau đó đọc exit code. Cách này hợp với `fc_cli.py` lab đã có.
- Trên Windows, chạy CI cục bộ hoặc qua self-hosted runner sẽ thực tế hơn dựng AppImage/Docker Linux, vì lab đã có 1.1.4 cài sẵn (suy luận).
- Regression nên so trên số đo B-rep (Volume, Area, BoundBox, số Solid/Face) có dung sai, không so hash file `.FCStd` (vì file là zip, có timestamp) (suy luận).

### Gaps
- Chưa xác nhận được ở tag 1.1.4 rằng `FreeCADTest.py` vẫn giống bản main (TODO: mở file trong thư mục cài đặt `bin/../Ext` hoặc `lib` để kiểm).
- Gói conda-forge `freecad` 1.1.x: chưa tìm được nguồn chính về phiên bản và cách import (TODO: xem feedstock conda-forge).
- Chưa tìm được AppImage chính thức nào đi kèm hướng dẫn GitHub Actions. Cách "giải nén AppImage rồi chạy FreeCADCmd -t" chỉ là suy luận.
- Chưa thấy dự án mã nguồn mở nào chạy test yêu cầu thiết kế (clearance/volume) trực tiếp trên `.FCStd`.
- pytest với Python của FreeCAD: không có nguồn chính thức. Muốn dùng thì phải cài pytest vào Python đi kèm FreeCAD (TODO: thử `python.exe -m pip install pytest` trong thư mục `bin`).

## B. Boolean với STEP hãng (open shell, tự giao, non-manifold)

### Takeaway
Bản 1.x của FreeCAD tự bật fuzzy theo kích thước bbox và chạy song song. Nó kiểm `BRepCheck_Analyzer` trên cả hai đầu vào nhưng **chỉ in warning, không dừng**. Hệ quả: boolean với STEP hỏng có thể "thành công" mà vẫn ra kết quả sai. Script phải tự kiểm trước và sau (`isValid()`, `check(True)`, kiểu shape là Solid, volume thay đổi hợp lý). Theo OCCT, kết quả boolean trên solid hở "cannot be always guaranteed".

### Cited Findings
- **Mã nguồn `FCBRepAlgoAPI_BooleanOperation.cpp` (Cao, main 2026-10; bản quyền 2024 Eric Price):**
  - Constructor mặc định gọi `SetRunParallel(Standard_True); SetNonDestructive(Standard_True);`
  - Constructor có tham số gọi `setAutoFuzzy()`, rồi đến RunParallel và NonDestructive.
  - `if (!BRepCheck_Analyzer(theS1).IsValid()) Base::Console().warning("Base shape is not valid for boolean operation");` và tương tự "Tool shape is not valid…" → **chỉ cảnh báo**.
  - Auto-fuzzy: `SetFuzzyValue(Part::FuzzyHelper::getBooleanFuzzy() * sqrt(bounds.SquareExtent()) * Precision::Confusion())`, tức tỉ lệ với đường chéo bbox của mọi argument và tool.
  - Có `RecursiveCutFusedTools`: khi cut với ≥2 tool, nó fuse các tool lại trước rồi mới cut.
  
  → **Khớp** với số đo lab (RunParallel + BRepCheck hai đầu vào + auto-fuzzy), thêm chi tiết NonDestructive và "chỉ warning" — [FCBRepAlgoAPI_BooleanOperation.cpp](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Part/App/FCBRepAlgoAPI_BooleanOperation.cpp)
- **`FuzzyHelper.cpp` (Cao):** mặc định `double BooleanFuzzy = 1.0;`. Có `setBooleanFuzzy(base)`, `getBooleanFuzzy()`, và `withBooleanFuzzy(base, func)`. Hàm cuối khôi phục giá trị cũ sau khi chạy, nhưng không theo RAII nên nếu `func` throw thì không khôi phục. Với `Precision::Confusion()` = 1e-7 (giá trị OCCT chuẩn, tự biết, không lấy từ trang này), một chi tiết bbox chéo 100 mm có fuzzy ≈ 1e-5 mm — [FuzzyHelper.cpp](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Part/App/FuzzyHelper.cpp)
- **API Python (Cao, `TopoShape.pyi` main):**
  - `cut(tool, tolerance=0.0)`, `common(tools, tolerance=0.0)`, `fuse(tools, tolerance=0.0, *, noElementMap=False)`: tolerance là fuzzy toàn cục cho phép boolean.
  - `generalFuse(shapes, fuzzy_value=0.0)`: fuzzy "in addition to tolerances of the input shapes".
  - `check(runBopCheck=False)`: báo lỗi cấu trúc; khi truyền `True` thì chạy thêm BOP check.
  - `isValid()`; `fix(working_precision, minimum_precision, maximum_precision)` trả True/False.
  - `removeSplitter()` (= Refine); `sewShape(tolerance=1e-06)`; `fixTolerance(value, ShapeType)`; `limitTolerance(tmin, tmax=0, ShapeType)`; `removeInternalWires(minimalArea)`; `isClosed()`.
  
  — [TopoShape.pyi](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Part/App/TopoShape.pyi)
- **Wiki Part_CheckGeometry (Cao):** kiểm BRep có hợp lệ không. Tùy chọn "Run BOP check" chạy thêm kiểm Boolean OPerations. "FreeCAD has no methods to automatically repair geometry", tức phải sửa bằng tay ở các bước dựng — [Part_CheckGeometry](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Part_CheckGeometry.md). *Ghi chú: câu này mâu thuẫn một phần với việc API vẫn có `fix()`/`sewShape()`/ShapeFix. Có thể hiểu là "không tự sửa được một cách đáng tin cậy".*
- **Wiki Part_Boolean (Cao):** OCCT "sometimes has problems producing boolean results when the input objects share an edge or a face". Khi có mặt đồng phẳng, phép boolean sau có thể fail dù phép trước thành công. Khuyên cho các hình giao nhau rõ ràng (tool nhô ra ngoài) và dùng CheckGeometry — [Part_Boolean](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Part_Boolean.md)
- **OCCT spec Boolean (Cao, chính thức):**
  - Fuzzy dùng để xử lý "touching and near-coincident, misaligned entities". Giá trị nên đặt theo khe hở/độ lấn đo được rồi "slightly increase it". Mặc định là `Precision::Confusion()`.
  - Trong một ví dụ, fuzzy còn chạy nhanh hơn phép thường.
  - Argument phải hợp lệ theo `BRepCheck_Analyzer` và `BOPAlgo_ArgumentAnalyzer`, và "should not be self-interfered". Tính hợp lệ của argument là "necessary but insufficient".
  - Với solid hở: "the correct result of Boolean operation on open solids cannot be always guaranteed".
  - Có Gluing option (mặc định tắt) để tăng tốc khi các argument trùng nhau.
  - Kiểm `HasErrors()`/`HasWarnings()` sau khi `Perform()`.
  
  — [OCCT Boolean Operations spec](https://occt3d.com/dev/doc/overview/html/specification__boolean_operations.html)
- **Refine = `removeSplitter()` (TB, tracker):** Refine làm sạch các cạnh thừa bằng cách "sewing the concerning faces" — [tracker #839](https://tracker.freecad.org/view.php?id=839)
- **Tăng tolerance có hại (TB):** sửa bằng cách tăng tolerance của vertex cho ra kết quả mong muốn trước mắt, nhưng "bad for follow-up operations" — [tracker #1739](https://tracker.freecad.org/view.php?id=1739)
- **Fuzzy trong GUI (TB, cũ):** yêu cầu tính năng fuzzy boolean, lúc đó chỉ có trong Defeaturing WB, sau chuyển lên GitHub #5612. Hiện tại fuzzy đã tự bật trong core (theo mã nguồn ở trên) — [tracker #1967](https://tracker.freecad.org/view.php?id=1967)
- **CadQuery #697 (TB):** STEP hiển thị sai sau khi cut. Có người nghi lỗi fuzzy boolean của OCCT, người khác cho là hình học không hợp lệ bị exporter STL làm mịn che đi — [CadQuery #697](https://github.com/CadQuery/cadquery/issues/697)

### Inferences
- Quy trình script đề xuất cho STEP hãng (suy luận, ghép từ các nguồn trên):
  1. Import STEP rồi duyệt `shape.Solids`. Nếu không có solid mà chỉ có shell/face thì `sewShape(tol)` → `Part.Solid(Part.Shell(...))`.
  2. Chạy `fix(1e-7, 1e-7, 1e-3)` (TODO: chọn ngưỡng theo thử nghiệm), sau đó `isValid()` và `check(True)` bọc trong try/except, vì `check` raise khi có lỗi.
  3. **Ưu tiên không boolean trực tiếp với mesh/shape của hãng**: dùng primitive đơn giản (hộp/trụ theo datasheet) làm tool cắt, chỉ dùng STEP để xem hoặc kiểm va chạm.
  4. Sau boolean, kiểm `result.isValid()`, `len(result.Solids)==kỳ vọng`, và `0 < result.Volume < base.Volume` (với cut). Nếu volume không đổi thì coi như **fail im lặng**.
  5. Cuối cùng gọi `removeSplitter()`.
- Vì FreeCAD chỉ log warning khi đầu vào invalid, script headless nên bắt Console observer hoặc tự gọi `BRepCheck` qua `isValid()` trước khi boolean, để chuyển cảnh báo thành lỗi có exit code (suy luận).
- Fuzzy tự động rất nhỏ (cỡ 1e-5 mm ở bbox 100 mm), nên khe hở của STEP hãng ở mức 0,01 mm sẽ không tự được xử lý. Lúc đó phải truyền `tolerance` cụ thể, ví dụ `cut(tool, 0.01)`, theo khuyến nghị OCCT là "đo khe rồi tăng nhẹ" (suy luận + Cao).

### Gaps
- Không tìm được thread forum.freecad.org cụ thể về BOPCheck với open shell từ STEP hãng.
- Chưa rõ tham số `tolerance` truyền từ Python có **thay thế** hay **cộng thêm** vào auto-fuzzy hay không (TODO: đọc `TopoShape::makeElementBoolean` / `TopoShapeExpansion.cpp`).
- Chưa xác minh có tham số người dùng nào (ParamGet) đặt được `BooleanFuzzy` hay không (TODO).
- Chưa đọc tài liệu `BOPTools` (JoinFeatures/SplitFeatures) và `Part.ShapeFix` (TODO).

## C. Khắc chữ/số bằng script cho chi tiết in 3D

### Takeaway
Có hai cách: `Draft.make_shapestring(String, FontFile, Size, Tracking)` (thành object tham số, có MakeFace và Fuse) hoặc `Part.makeWireString` (chỉ ra wire, phải tự dựng face có lỗ). Lab đã chạy được `makeWireString` + `arialbd.ttf` cỡ 6 mm, sâu 0,4 mm ở mặt bed. Kết quả này **phù hợp** với kinh nghiệm cộng đồng (font đậm; độ sâu là bội của lớp in). Cộng đồng chưa có con số chính thức nào từ Prusa hay Bambu.

### Cited Findings
- **Wiki Draft ShapeString (Cao):**
  - Chữ ký `make_shapestring(String, FontFile, Size=100, Tracking=0)`; Size là chiều cao chữ tính bằng mm.
  - Hỗ trợ `.ttf`, `.otf`, `.pfb`.
  - Thuộc tính **Make Face** ("Fill letters with faces") và **Fuse** (v1.0; "usually not required (can be very slow)").
  - Justification (9 kiểu) có từ v1.0; đường dẫn font tương đối có từ v1.1 (yêu cầu tài liệu đã được lưu ít nhất 1 lần).
  - Trên Windows, "access to the default font folder is restricted": có thể bật **DontUseNativeFontDialog** hoặc gõ đường dẫn trực tiếp.
  - "font contours are allowed to overlap and have small gaps", nên có thể sinh hình học có vấn đề. Chữ quá nhỏ có thể méo.
  
  — [Draft_ShapeString](https://raw.githubusercontent.com/FreeCAD/FreeCAD-documentation/main/wiki/Draft_ShapeString.md)
- **Chữ có lỗ (A, B, 0, 8) (TB, tracker cũ):** dev chỉ ra "for letters with voids the shape has inverted orientation", làm boolean fail. Workaround: Draft Downgrade ra face rồi extrude — [tracker #1143](https://tracker.freecad.org/view.php?id=1143)
- **Face từ nhiều wire (TB):** wire lớn nhất làm biên ngoài, các wire bên trong làm lỗ, và nên sắp outer trước inner — [devtalk: Unifying make-faces-from-wires](https://devtalk.freecad.org/t/unifying-make-faces-from-wires-routines/14635). Với `Part.Face` có lỗ thì wire lỗ cần đảo hướng — [tracker #1510](https://tracker.freecad.org/view.php?id=1510)
- **`Part.makeWireString` có test chính thức** (`src/Mod/Test/testmakeWireString.py`). Hàm nhận chuỗi, đường dẫn font, (tên font), chiều cao, tracking; chữ ký đã đổi qua các phiên bản (TB, bản mirror) — [testmakeWireString.py mirror](https://huggingface.co/AbdulElahGwaith/FreeCAD/blob/main/src/Mod/Test/testmakeWireString.py). TODO: kiểm chữ ký chính xác ở 1.1.4 bằng `help(Part.makeWireString)`.
- **Mã nguồn ShapeString** (`draftobjects/shapestring.py`) là chỗ nên đọc để copy logic dựng face có lỗ — [shapestring.py mirror](https://huggingface.co/AbdulElahGwaith/FreeCAD/blob/main/src/Mod/Draft/draftobjects/shapestring.py). *Chưa đọc chi tiết; nhớ là dùng FaceMakerBullseye nhưng chưa xác minh → TODO.*
- **Wiki tutorial ShapeString:** quy trình chính thức ShapeString → Part Extrude → Part Cut để khắc — [Draft ShapeString tutorial](https://wiki.freecad.org/Draft_ShapeString_tutorial/tr)
- **Kích thước/độ sâu FDM (TB/Thấp, chỉ là ý kiến diễn đàn, không có số chính thức):**
  - Prusa forum: chữ nhỏ nhất "without special calculation" khoảng 10 mm cao. Một người khác nói 4 mm là mức tối thiểu họ từng làm được (phụ thuộc lớp đầu và tốc độ in).
  - Độ sâu deboss 0,6–1 mm, hoặc 0,6–0,8 mm; nên lấy bội của chiều cao lớp.
  - Có thể giảm perimeter xuống 1 bằng modifier.
  - Chữ biến mất khi slice: chữ quá nhỏ so với nozzle; cách khắc phục là dùng nozzle 0,25 mm hoặc tăng cỡ chữ / đổi font.
  
  — [Prusa forum: issue with debossed text](https://forum.prusa3d.com/forum/english-forum-original-prusa-i3-mk4s-how-do-i-print-this/issue-with-debossed-text); [Prusa forum: help me fix my small text](https://forum.prusa3d.com/forum/prusaslicer/help-me-fix-my-small-text/)
- **PrusaSlicer Text tool:** có Height và depth; chọn Operation "Cut" để khắc lõm; có "Use surface"/"Per glyph" cho mặt cong (bên thứ ba, TB) — [All3DP PrusaSlicer text](https://all3dp.com/2/prusaslicer-text-simply-explained/); [Printables article (Prusa)](https://www.printables.com/article/creative-uses-of-prusaslicer-3d-text-and-printing-lbZ4wdw)
- **Bambu:** không tìm thấy cỡ chữ tối thiểu chính thức. Có model MakerWorld "customizable text size guide" in thử font 2–7 mm. Một người dùng Bambu forum khuyên dựng chữ trong CAD thay vì dùng công cụ text của Bambu Studio (TB) — [MakerWorld text size guide](https://makerworld.com/en/models/914513-customizable-text-size-guide); [Bambu forum recessed text bottom](https://forum.bambulab.com/t/newbie-here-print-colored-recessed-text-on-bottom/100016)
- **Nozzle 0,4 mm cho chữ nổi nhỏ:** in ra kiểu "bare tree trunks"; chuyển sang nozzle 0,2 mm thì cải thiện (Thấp, 1 người dùng) — [Autodesk forum](https://forums.autodesk.com/t5/fusion-design-validate-document/emboss-or-deboss-an-image/m-p/12840003/highlight/true)
- **Materialise (in kim loại, không phải FDM):** nét tối thiểu 0,8 mm, sâu 0,8 mm. Chỉ dùng để tham khảo — [Materialise forum](https://i.materialise.com/forum/t/how-can-i-be-so-sure-about-the-quality-of-print-for-my-model/583)

### Inferences
- Kết quả của lab (6 mm, Arial Bold, sâu 0,4 mm = 2 lớp 0,2 mm, mặt bed) nằm trong vùng "4 mm tối thiểu ↔ 10 mm an toàn" và đúng quy tắc "độ sâu là bội của lớp", nên là cấu hình hợp lý (suy luận).
- Khắc ở mặt bed: chữ lõm bị lật gương khi nhìn từ dưới lên. Cần `mirror` chuỗi trước khi cut, nếu không chữ đọc ngược (suy luận, TODO: kiểm lại model lab đã mirror chưa).
- Mặt trên: độ sâu 0,4–0,6 mm là đủ. Mặt bên (dọc): chữ in theo lớp nên rõ hơn; cạnh trên của chữ lõm là phần nhô ngang, ở cỡ chữ nhỏ thường in được không cần support (suy luận, chưa có nguồn).
- Nét chữ tối thiểu nên ≥ 2 × đường kính nozzle (≈ 0,8 mm với nozzle 0,4) để slicer tạo được 2 đường perimeter. Đây là quy tắc thường gặp, **chưa tìm được nguồn chính** → TODO.
- Đường dẫn font trên Windows: `C:\Windows\Fonts\arialbd.ttf` (đã dùng thực tế ở lab). Nên copy file font vào thư mục dự án để script không phụ thuộc máy (suy luận; v1.1 hỗ trợ đường dẫn tương đối theo wiki).
- Script nên kiểm sau khi cut: `result.isValid()` và volume giảm đúng bằng xấp xỉ diện tích chữ × độ sâu, để bắt trường hợp chữ có lỗ bị đảo hướng làm cut sai mà không báo lỗi (suy luận).

### Gaps
- Không có số liệu chính thức của Prusa hay Bambu về cỡ chữ, độ sâu hay nét tối thiểu cho FDM.
- Chưa xác minh chữ ký `Part.makeWireString` ở 1.1.4, và cũng chưa xác minh `make_shapestring` dùng FaceMaker nào.
- Chưa có nguồn cho quy tắc khắc ở mặt bên/mặt trên và cho "min stroke width = 2 × nozzle".
