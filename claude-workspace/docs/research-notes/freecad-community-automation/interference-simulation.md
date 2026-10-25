# FreeCAD: kiểm va chạm/khe hở trong assembly và mô phỏng chuyển động bằng script

Ghi chú nghiên cứu ngày 2026-10-24. Bối cảnh: tay robot 4-DOF (xi-lanh pushrod/rack, bánh răng), FreeCAD 1.1.4, Windows, Python.
Mã nguồn FreeCAD đọc từ nhánh `releases/FreeCAD-1-1` trên GitHub, mã OCCT đọc từ tag `V7_8_1` (bản 1.1.4 dùng OCC 7.8.1 theo issue #33697).
Độ tin cậy: **Cao** = mã nguồn hoặc tài liệu chính thức; **TB** = tracker/diễn đàn hoặc dự án cộng đồng; **Thấp** = một người dùng nói, hoặc là suy luận.
Lưu ý: wiki.freecad.org chặn bot (Anubis, "Access Denied"), nên mình không đọc được trực tiếp trang `Assembly_CreateSimulation` và `Part_Shape_proximity`. Thay vào đó mình đọc mã nguồn.

## 1. Assembly workbench có sẵn chức năng kiểm interference/collision không?

### Takeaway
**Chưa có.** Tính đến 2026-10, Assembly WB (1.0/1.1) và core FreeCAD không có lệnh kiểm interference. Yêu cầu tính năng #28165 vẫn mở. Hiện chỉ có một bản POC "vibe-coded" ở fork cá nhân, chưa có PR, và dự kiến đặt ở **Inspection WB** chứ không phải Assembly. Người dùng đang làm thay bằng macro/addon chạy `Shape.common()` (HighlightCommon, KiCad StepUp) hoặc tự viết script.

### Cited Findings
- **Issue #28165 (TB, tracker chính thức).** Tên: "No Clash Detection of Intersecting Parts (Band Analysis and Interference Check)". Mở ngày 2026-03-07 bởi maxwxyz, tách ra từ #12454; Type: Feature; version 1.2-dev; trạng thái Open, nhãn "Status: Solution proposed".
  - Nhãn: thêm "Mod: Inspection" và "GSoC" ngày 2026-07-05; nhãn "Mod: Assembly" đã bị gỡ.
  - Theo dõi trong project "Mechanical Advisory Group" ở mức Todo (P2). Không có milestone, không có người nhận, không có PR liên kết.
  - Yêu cầu gồm: (1) kiểm chi tiết giao nhau, (2) ngưỡng khe hở min/max, (3) **kiểm va chạm trong suốt hành trình joint, có xét giới hạn joint** — đúng nhu cầu của lab.
  - [Issue #28165](https://github.com/FreeCAD/FreeCAD/issues/28165)
- **POC 2026-07-05 của maxwxyz (Thấp–TB, fork cá nhân, nhánh `band-analysis` trên github.com/maxwxyz/FreeCAD).**
  - Có 2 lệnh: Band analysis và Interference check.
  - Interference phân loại từng cặp thành clash / contact / clearance, tô màu đỏ / vàng / cyan.
  - Dùng được với solid, face, shell và PartDesign Body.
  - Còn thiếu: task panel, bảng kết quả, xuất CSV, progress/cancel.
  - Có 2 chế độ: "exact BRep" (chính xác, chỉ áp dụng cho solid) và "deviation-based" (cho model phức tạp, nơi BRep chậm, và cho mesh/scan).
  - Creymore góp ý: cần kiểm khe hở theo từng frame animation, và cần xử lý ren vít/lỗ ren (vốn luôn báo va chạm).
  - [Issue #28165, comments](https://github.com/FreeCAD/FreeCAD/issues/28165)
- **Issue #12454 "Assembly: Add ability to Wiggle / Animate the DOF" (TB).** Mở ngày 2024-02-16, vẫn Open, mức "Nice to have".
  - 2024-06-23: MiqCG chỉ tới một macro phát hiện va chạm, vì "trong 3D View không phải lúc nào cũng thấy rõ khi part lọt vào part khác".
  - 2026-03-09: PaddleStroke (dev chính của Assembly) đề nghị đóng issue này, và phần clash được tách sang #28165.
  - [Issue #12454](https://github.com/FreeCAD/FreeCAD/issues/12454)
- **Danh sách hàm Python của `AssemblyObject` trong 1.1 (Cao, mã nguồn).** Gồm `solve`, `generateSimulation`, `updateForFrame`, `numberOfFrames`, `undoSolve`, `ensureIdentityPlacements`, `clearUndo`, `isPartConnected`, `isPartGrounded`, `isJointConnectingPartToGround`, `exportAsASMT`, `getDownstreamParts`. **Không có hàm nào về collision/interference.** — [AssemblyObject.pyi (1.1)](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Assembly/App/AssemblyObject.pyi)
- **Bài blog (Thấp).** Ghi rằng FreeCAD không có collision detection, và người dùng giả lập bằng cách đặt giới hạn min/max cho joint. — [silica.io, phần 8](https://www.silica.io/a-pragmatic-introduction-to-freecad-part-8-assemblies/)

### Inferences
- Không nên chờ tính năng chính thức. Nhãn GSoC, P2 và chưa có PR cho thấy sớm nhất cũng phải đến 1.2 hoặc 26.x; ngày phát hành TODO. Cách chắc ăn là tự viết script.
- Bài toán "ren vít luôn báo va chạm" cũng sẽ gặp với bánh răng ăn khớp và rack. Lab cần một danh sách cặp được phép chạm, hoặc một ngưỡng thể tích.

### Gaps
- Mình không kiểm được nhánh 26.3 hay `main` có commit nào về interference sau 2026-07 không: GitHub API bị giới hạn rate, và máy không có `gh`. TODO: tìm trên GitHub với `repo:FreeCAD/FreeCAD interference is:pr`.
- Không đọc được wiki Assembly (bị Anubis chặn).

## 2. Addon/macro có kiểm clash: tình trạng 2025–2026

### Takeaway
Đã kiểm lại mã nguồn (shallow clone ngày 2026-10-24):
- Chỉ **KiCad StepUp** (lệnh Collisions) và macro **HighlightCommon** thực sự kiểm va chạm. Cả hai đều dùng `shape_a.common(shape_b).Volume > ngưỡng`, duyệt mọi cặp O(n²), và cần GUI selection.
- A2plus ghi rõ là không có collision check. Assembly3 và Manipulator không có.
- RobotCAD có tạo collision object cho URDF/MoveIt, nhưng việc kiểm va chạm diễn ra ở phía ROS.

### Cited Findings
- **A2plus (TB, commit cuối 2026-02-15).** README dòng 31 ghi: "No collision check of parts at moment. Planned for future versions". — [kbwbe/A2plus](https://github.com/kbwbe/A2plus)
- **Assembly3 (TB, commit cuối 2025-11-08).** Grep `collision|interferen|clash` không thấy công cụ kiểm va chạm nào. — [realthunder/FreeCAD_assembly3](https://github.com/realthunder/FreeCAD_assembly3)
- **Manipulator (easyw, commit cuối 2026-03-25).** Không có tính năng collision; chỉ có Mover/Aligner/Caliper. Grep chỉ trúng `oDraft.py`. — [easyw/Manipulator](https://github.com/easyw/Manipulator)
- **KiCad StepUp (TB, commit cuối 2026-09-04).** Hàm `routineCollisions()` trong `kicadStepUptools.py` (khoảng dòng 8705):
  - Cần chọn ít nhất 2 object qua `FreeCADGui.Selection`. Nó tự đi vào App::Part/Body và tự nhân placement của cha.
  - Gọi `common = acpy.common(bcpy)`; nếu `common.Volume > conflict_tolerance` thì tạo object "Collisions (A - B)".
  - Đoạn `distToShape` trong hàm đã bị comment bỏ.
  - [easyw/kicadStepUpMod](https://github.com/easyw/kicadStepUpMod)
  - Một người dùng KiCad forum kể: chạy trên 2 part thì tốt, chạy trên toàn bộ part thì crash (Thấp). — [KiCad forum](https://forum.kicad.info/t/3d-body-collision-detection/52359)
- **Macro HighlightCommon trong FreeCAD-macros (TB).**
  - Phiên bản 2.3.2, header ghi ngày 2021-07-01; file có commit trong repo ngày 2026-07-02; status "Production"; tác giả JMG, galou; license CC0.
  - Nếu chọn ít hơn 2 object thì duyệt *toàn bộ* `doc.Objects`. Gọi `shape_a.common(shape_b)`, báo va chạm khi `Volume > 1e-6` mm³, và gom kết quả vào group.
  - [HighlightCommon.FCMacro](https://github.com/FreeCAD/FreeCAD-macros/blob/master/Utility/HighlightCommon.FCMacro)
  - Grep cả repo FreeCAD-macros, ngoài macro này không thấy macro nào tên "Interference".
- **Assembly4 (TB).** Repo GitHub `Zolko-123/FreeCAD_Assembly4` trả 404 khi clone ngày 2026-10-24. Dự án đã chuyển sang Codeberg (`codeberg.org/zolko/assembly4`): v0.61.1, commit ngày 2026-06-25. Mình chưa kiểm mã Assembly4 có collision không (TODO). — [Codeberg Assembly4](https://codeberg.org/zolko/assembly4)
- **RobotCAD (freecad.robotcad / freecad.cross, commit cuối 2026-10-23, TB).**
  - Tự sinh collision object từ "Real" element của link: hộp/cầu/trụ bao quanh, hoặc bản sao.
  - Xuất URDF; tích hợp MoveIt: lấy planning scene qua service `/get_planning_scene`, có `attached_collision_object`.
  - Các tool MoveIt/Gazebo cần cài ROS2.
  - [drfenixion/freecad.robotcad](https://github.com/drfenixion/freecad.robotcad)
- **BIM/IFC.** IfcClash (thuộc IfcOpenShell) là CLI + thư viện kiểm intersection/collision/clearance, dùng `hppfcl`, xuất BCF/JSON; được dùng qua Bonsai (Blender). Mình không thấy nguồn nào nói BIM WB của FreeCAD tích hợp IfcClash. — [OSArch Bonsai clash](https://wiki.osarch.org/bonsai-clash-detection/)
- **"Part Check Geometry"** là công cụ kiểm tính hợp lệ của *một* shape (`isValid`/BOPCheck), không kiểm va chạm giữa các part. Nhận định này lấy từ hiểu biết sẵn có; trang wiki bị chặn nên chưa đối chiếu (TODO). Nó vẫn hữu ích để lọc shell lỗi trước khi chạy boolean.

### Inferences
- Cả hai công cụ cộng đồng đều dùng B-rep `common` theo cặp, tức là cùng loại chi phí với số đo B-rep common 0,08–3,2 s/cặp của lab. Không công cụ nào làm sweep theo tư thế.
- Với RobotCAD: lab đã có quy trình xuất URDF, nên MoveIt/FCL là một hướng sweep "chuẩn ngành". Đổi lại phải cài ROS2 (khó trên Windows) và chỉ dùng collision primitive/mesh thô.

### Gaps
- Chưa kiểm KinematicsWB (galou): repo `galou/freecad.kinematics` trả 404. TODO: tìm vị trí mới.
- Chưa kiểm Assembly4 bản Codeberg.

## 3. Kỹ thuật trong script: common, distToShape, proximity, mesh — hiệu năng và bẫy

### Takeaway
Mã nguồn **xác nhận** cả ba quan sát của lab:
- **(a)** Tham số `tol` của `distToShape` thực ra là `SetDeflection` (sai số hội tụ) chứ không phải ngưỡng dừng sớm, nên không làm nhanh hơn.
- **(b)** `Shape.proximity` chỉ đọc triangulation *đã có sẵn* trên face. Nó **ném lỗi khi không có cặp chồng lấn nào**, vì OCCT đặt `IsDone = (số cặp > 0)`, còn FreeCAD biến `!IsDone` thành exception "make sure the shapes are tessellated".
- **(c)** Thời gian `distToShape` dao động mạnh theo hình học. Một bài trên forum OCCT đo được chênh 17 lần (0,357 s so với 6,081 s) giữa hai cặp có số face tương đương.

Hướng mesh (manifold3d / trimesh+python-fcl) có wheel cp311 win_amd64, khớp với Python 3.11 của FreeCAD 1.1.4.

### Cited Findings
- **`distToShape` (Cao, mã nguồn 1.1).**
  - Chữ ký `distToShape(shape, tol=1e-7)`. Bên trong: `BRepExtrema_DistShapeShape extss; extss.SetDeflection(tol); extss.SetMultiThread(true)` (khi OCC ≥ 7.6), rồi gọi `Perform()`.
  - `tol` được truyền vào **deflection**, nên tăng `tol` không cho thuật toán "dừng khi đã biết dist > ngưỡng". → **Khớp** với số đo "tol không làm nhanh hơn" của lab.
  - Hàm đã bật multi-thread sẵn. Vì vậy nếu chạy song song nhiều `distToShape` bằng thread Python thì khó tăng tốc thêm (Thấp, suy luận).
  - [TopoShapePyImp.cpp (1.1)](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Part/App/TopoShapePyImp.cpp), [TopoShape.pyi](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Part/App/TopoShape.pyi)
- **Thời gian `distToShape` dao động (TB).** Bài forum OCCT ngày 2023-05-15, tác giả làm workbench lập trình tự lắp ráp (FreeCAD 0.21, OCC 7.5.1):
  - Cặp ly hợp nhiều đĩa (141/146 face) mất 6,081 s; cặp máy nén khí (163/195 face) mất 0,357 s, tức chênh khoảng 17 lần.
  - Phần chậm nằm ở bước `SolidTreatment` trong `Perform`. Bài không có trả lời.
  - → **Khớp** với khoảng 0,2–12 s/cặp của lab.
  - [OCCT forum (archive)](https://occt3d.com/dev/content/discrepancy-computation-times-when-applying-disttoshape-brepextremadistshapeshape-similar/index.html)
- **Issue #33842 (TB, 2026-10).** `distToShape` với điểm nằm *trong* solid cho kết quả không ổn định trong một dải mỏng gần bề mặt. Cách tác giả xử lý: phân loại bằng solid classifier trước. — [Issue #33842](https://github.com/FreeCAD/FreeCAD/issues/33842)
- **`Shape.proximity(shape, tol)` (Cao, mã nguồn 1.1).**
  - Trả về tuple `(list index face của self, list index face của shape)`, đánh số từ 1.
  - `tol` mặc định là `Precision::Confusion()` (1e-7), và hàm chỉ gọi `SetTolerance(tol)` khi `tol > 0`, nên luôn chạy nhánh overlap.
  - Khi `!IsDone()` thì raise `PartExceptionOCCError("BRepExtrema_ShapeProximity failed, make sure the shapes are tessellated")`.
  - [TopoShapePyImp.cpp (1.1)](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Part/App/TopoShapePyImp.cpp)
- **OCCT 7.8.1 (Cao, mã nguồn).**
  - `BRepExtrema_OverlapTool::Perform` đặt `myIsDone = (this->Select(mySet1->BVH(), mySet2->BVH()) > 0)`. Nghĩa là **khi không có cặp phần tử nào chồng lấn thì IsDone = false**, và FreeCAD báo lỗi y như khi chưa tessellate. → **Khớp và giải thích** hiện tượng "throws when no pair found" mà lab gặp.
  - `BRepExtrema_TriangleSet` đọc `BRep_Tool::Triangulation(face)` và bỏ qua face nào có triangulation null. → Phải gọi `shape.tessellate(dev)` (hoặc `BRepMesh`) trước.
  - [BRepExtrema_OverlapTool.cxx](https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/V7_8_1/src/BRepExtrema/BRepExtrema_OverlapTool.cxx), [BRepExtrema_ShapeProximity.cxx](https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/V7_8_1/src/BRepExtrema/BRepExtrema_ShapeProximity.cxx), [BRepExtrema_TriangleSet.cxx](https://raw.githubusercontent.com/Open-Cascade-SAS/OCCT/V7_8_1/src/BRepExtrema/BRepExtrema_TriangleSet.cxx)
  - Tài liệu OCCT nói kết quả là xấp xỉ, phụ thuộc deflection của triangulation, và hiệu năng cao nhờ dùng lại triangulation có sẵn. Tolerance = 0 thì chỉ bắt face cắt nhau; tolerance > 0 thì bắt cả face ở gần nhau trong khoảng đó. Từ 7.8, tolerance mặc định của constructor là `Precision::Infinite()` (chế độ tính giá trị proximity). — [OCCT 7.8 refman](https://dev.opencascade.org/doc/occt-7.8.0/refman/html/classBRepExtrema__ShapeProximity.html)
- **Pitfall chuyển động (Cao, suy từ mã).** BVH của proximity được xây từ triangulation *gắn với face và location*. Mình chưa kiểm việc đổi `Placement` có buộc dựng lại BVH không (TODO). Nếu có thì mỗi tư thế đều tốn chi phí init.
- **Mesh libs (Cao, PyPI ngày 2026-10-24).**
  - `manifold3d` 3.5.4 (2026-09-25): có wheel `cp311-win_amd64`.
  - `python-fcl` 0.7.0.11 (2026-04-08): có wheel `cp311-win_amd64`.
  - `trimesh` 5.2.0: pure-Python, cần Python ≥ 3.10.
  - [PyPI manifold3d](https://pypi.org/project/manifold3d/), [PyPI python-fcl](https://pypi.org/project/python-fcl/), [PyPI trimesh](https://pypi.org/project/trimesh/)
- **trimesh `CollisionManager` (Cao, tài liệu chính thức).** Bọc FCL (kiểu `fcl.BVHModel`).
  - `add_object(name, mesh, transform)`: mesh được nạp một lần.
  - `set_transform(name, T4x4)`: đổi tư thế mà không phải dựng lại.
  - `in_collision_internal(return_names=True)`: kiểm mọi cặp.
  - `min_distance_internal` / `min_distance_single`: lấy khe hở.
  - → Đây đúng là mô hình "mesh một lần, đổi transform mỗi pose", giống cách lab làm.
  - [trimesh.collision](https://trimesh.org/trimesh.collision.html)

### Inferences
- Kết quả của lab (sweep 30 pose giảm từ 395 s xuống 16 s; manifold3d 1–4 ms/cặp sau khi mesh) **phù hợp** với các nguồn. Các nguồn không có số benchmark trực tiếp nào cho manifold3d trong FreeCAD để so (Gap).
- Pipeline khuyến nghị (suy luận):
  1. Lọc nhanh bằng AABB/OBB.
  2. Kiểm cặp bằng mesh (manifold3d để lấy thể tích giao, hoặc FCL để lấy bool + min distance).
  3. Chỉ những cặp nghi ngờ mới xác nhận lại bằng B-rep `common` ở tư thế đó.
  4. Với `proximity`: bọc `try/except Part.OCCError` và coi lỗi là "không chạm", **nhưng** phải kiểm trước rằng cả hai shape đã có triangulation. Nếu không, mình không phân biệt được "không chạm" với "quên tessellate".
- Mesh là xấp xỉ theo deflection. Với khe hở bánh răng/rack cỡ 0,1–0,3 mm, deflection phải nhỏ hơn khe hở một bậc; số cụ thể TODO, cần đo.

### Gaps
- Mình không tìm được nguồn nào đo hiệu năng `Shape.proximity` hay manifold3d bên trong FreeCAD.
- Không có nguồn nào nói về độ an toàn khi chạy OCCT boolean đa luồng từ Python trong FreeCAD. GIL được nhả hay không: TODO.
- Chưa có nguồn về STEP của hãng bị shell lỗi làm `common` hỏng. Ghi chú `testing-boolean-engraving.md` cùng thư mục có thể đã đề cập.

## 4. Assembly Simulation (1.1): tạo và chạy từ Python/headless được không?

### Takeaway
**Phần lớn là được.** Phần solver nằm ở App (C++) và có binding Python: `assembly.generateSimulation(simObj)`, `assembly.numberOfFrames()`, `assembly.updateForFrame(i)`, cùng `solve()`. Nhưng hai class Python `Simulation`/`Motion` lại nằm trong `CommandCreateSimulation.py`, file import PySide khi `App.GuiUp`. Vì vậy chạy headless phải tự dựng object `App::FeaturePython` rồi gán Proxy. Mình chưa thấy ví dụ chính thức nào làm việc này. Simulation **không có collision detection**.

### Cited Findings
- **Binding Python của `AssemblyObject` trong 1.1 (Cao).**
  - `solve(enableRedo=False) -> int` trả 0 nếu OK; mã lỗi: -6 không có part cố định, -4 thừa ràng buộc (over-constrained), -3 ràng buộc xung đột, -5 ràng buộc sai dạng, -1 lỗi solver, -2 ràng buộc dư.
  - `generateSimulation(simulationObject) -> int`: cùng bộ mã lỗi.
  - `updateForFrame(index)`: cập nhật cả assembly về frame thứ index.
  - `numberOfFrames()`.
  - [AssemblyObject.pyi](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Assembly/App/AssemblyObject.pyi), [AssemblyObjectPyImp.cpp](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Assembly/App/AssemblyObjectPyImp.cpp)
- **Phía C++ (Cao, header trên `main`).** Có thêm `create_mbdSimulationParameters(sim)`, `getMotionsFromSimulation(sim)`, `preDrag/doDragStep/postDrag`, `getLastDoF()`, `signalSolverUpdate`. Solver là OndselSolver (MbD). — [AssemblyObject.h](https://raw.githubusercontent.com/FreeCAD/FreeCAD/main/src/Mod/Assembly/App/AssemblyObject.h)
- **Object Simulation (Cao, `CommandCreateSimulation.py` nhánh 1.1).**
  - Class `Simulation(feaPy)` thêm `App::GroupExtensionPython` và các property: `aTimeStart` = 0, `bTimeEnd` = 1 (s), `cTimeStepOutput` = 1e-2, `fGlobalErrorTolerance` = 1e-6, `jFramesPerSecond` = 30.
  - Class `Motion(feaPy, motionType, joint, formula)` có property `Joint` (`App::PropertyXLinkSubHidden`), `Formula` (chuỗi, ví dụ `'1.0*time'`, mặc định trong dialog là `"5*time"`) và `MotionType` (enum).
  - Task panel làm theo thứ tự: tạo `Simulation(...)`, tạo `Motion(motion, motionType, joint, formula)`, gọi `self.assembly.generateSimulation(self.simFeaturePy)`, `nFrms = self.assembly.numberOfFrames()`, rồi `self.assembly.updateForFrame(val)` khi kéo slider.
  - Đầu file có `if App.GuiUp:` để import PySide và Qt; ViewProvider và dialog cũng nằm chung file này.
  - [CommandCreateSimulation.py (1.1)](https://raw.githubusercontent.com/FreeCAD/FreeCAD/releases/FreeCAD-1-1/src/Mod/Assembly/CommandCreateSimulation.py)
- **Tạo joint headless (TB, dự án cộng đồng constraint-kit, 2026-10-15/16, thử trên 1.0.2).**
  - `Assembly::AssemblyObject` tạo được dưới `freecadcmd` (GuiUp: 0), và gọi được `solve()`/`undoSolve()`.
  - `JointObject.Joint(obj, index)` nhận **index int** trong `JointObject.JointTypes`; truyền tên dạng string sẽ gây `TypeError`.
  - Proxy của Slider/Screw/Belt/RackPinion chỉ dựng được khi joint *đã nằm trong* assembly, vì `getAssembly()` dò qua `InList`.
  - `GroundedJoint` chạy được.
  - **Nhưng** `Reference1/Reference2` (`PropertyXLinkSubHidden`) cần một định dạng đường dẫn không có tài liệu. Truyền `(obj, [""])` là sai: `isPartConnected` vẫn False và kéo joint không làm part di chuyển. Tác giả đã rút lại tuyên bố ban đầu là "fully scriptable".
  - Tác giả quay sang tự viết `motion.py` dạng closed-form (slide, screw_drive, rotate, belt) cùng một lệnh `sweep` kiểm interference ở mọi trạm. Lý do: chỉ kiểm hai đầu hành trình thì bỏ sót va chạm.
  - [constraint-kit #28](https://github.com/jajmangold/constraint-kit/issues/28)
- **Bug headless trên đúng bản 1.1.4 (TB, issue #33697, mở 2026-10-18, Windows 11, FreeCAD 1.1.4.20260928, OCC 7.8.1).**
  - Tạo assembly + joint Revolute bằng `freecadcmd`, lưu `.FCStd`, rồi mở trong GUI và kích hoạt assembly thì lỗi `'int' object has no attribute 'redrawJointPlacements'`, vì `ViewObject.Proxy` unpickle ra số 1.
  - Đã có PR sửa #33768, mở 2026-10-20, chưa merge tại thời điểm đọc.
  - Issue có kèm script tạo Revolute headless tối thiểu.
  - [Issue #33697](https://github.com/FreeCAD/FreeCAD/issues/33697)
- **Giới hạn joint (TB, docs cộng đồng).** Giới hạn joint được áp dụng trong Simulation nhưng không chặn solver tĩnh. — [freecad-docs joint types (không chính thức)](https://robertmassaioli.github.io/freecad-docs/assembly/concepts/joint-types/)
- Wiki chính thức `Assembly_CreateSimulation` ghi tính năng có từ 1.1 và đánh dấu trang là chưa hoàn thiện. Mình chỉ thấy qua snippet tìm kiếm, không đọc trực tiếp được (Anubis). — [wiki Assembly_CreateSimulation](https://wiki.freecad.org/Assembly_CreateSimulation)

### Inferences
- Với tay 4-DOF, cách đơn giản và chắc nhất (TB–Thấp, suy luận):
  - **Không dùng Simulation/time.** Đặt trực tiếp `Offset`/góc của từng joint (hoặc Placement của part, tính bằng kinematics closed-form), gọi `assembly.solve()`, rồi đọc `Shape`/`Placement` toàn cục của từng part.
  - Nếu muốn dùng Simulation: chạy trong FreeCAD GUI (`gui_run`), dựng object qua class `Simulation`/`Motion`, rồi lặp `for i in range(asm.numberOfFrames()): asm.updateForFrame(i)` và đọc placement. Headless thì phải import `CommandCreateSimulation` khi `GuiUp = False` (các dòng PySide được bọc trong `if`) — chưa kiểm, TODO.
- Bug #33697 cảnh báo: file tạo headless rồi mở trong GUI 1.1.4 có thể hỏng chỗ chỉnh joint. Khi tạo bằng script, nên tạo trong phiên GUI, hoặc chờ bản có PR #33768.
- Joint RackPinion/Gears chỉ ràng buộc tỉ số truyền, không kiểm biên dạng răng. Va chạm răng giả (mesh răng chồng nhau) sẽ luôn xuất hiện, nên phải loại trừ những cặp này khỏi kiểm va chạm.

### Gaps
- Mình không tìm thấy script mẫu chính thức nào tạo joint Slider/RackPinion/Gears và gọi `generateSimulation` từ Python. TODO: tìm trong `src/Mod/Assembly/AssemblyTests/` và trên forum Assembly.
- Chưa rõ định dạng `Reference1/2` đúng cho joint tạo bằng script ở bản 1.1. Có thể đọc từ một file `.FCStd` tạo bằng GUI để biết (TODO).

## 5. Cách cộng đồng quét dải joint và phát hiện va chạm

### Takeaway
Mình không tìm thấy công cụ FreeCAD nào làm sẵn "sweep joint range + collision". Có ba hướng:
- **(1)** Tự viết script: đặt tư thế → kiểm (giống constraint-kit, `sweep` theo từng trạm).
- **(2)** Xuất URDF bằng RobotCAD, rồi kiểm va chạm bằng MoveIt/FCL (cần ROS2).
- **(3)** Đưa mesh sang FCL/trimesh. Đây là cách IfcClash làm bên BIM (dùng `hppfcl`).

### Cited Findings
- constraint-kit `ckwb/motion.py`: lệnh `sweep` đưa part qua toàn hành trình và kiểm interference ở mọi trạm, có 17 test. Đây là dự án cá nhân, tháng 10/2026. — [constraint-kit #28](https://github.com/jajmangold/constraint-kit/issues/28)
- RobotCAD: tạo collision geometry, xuất URDF, lấy planning scene của MoveIt. Một số tool cần ROS2/Gazebo. — [freecad.robotcad README](https://github.com/drfenixion/freecad.robotcad)
- Yêu cầu chính thức #28165 có ghi "kiểm va chạm trong hành trình joint có xét giới hạn" nhưng chưa triển khai. — [Issue #28165](https://github.com/FreeCAD/FreeCAD/issues/28165)
- IfcClash: so nhóm A với nhóm B (hoặc A với chính A), có chế độ clearance, dùng hppfcl. — [OSArch](https://wiki.osarch.org/bonsai-clash-detection/)
- Bài devtalk về FreeCAD vẽ lại chậm: tạo lại shape ở mỗi chuyển động nhỏ là phần tốn kém, nên preview ở tầng hiển thị và chỉ recompute OCC khi chấp nhận thay đổi. — [devtalk](https://devtalk.freecad.org/t/why-is-freecad-so-slow-in-redrawing/56355)

### Inferences
- Cách lab đang làm (mesh một lần, mỗi pose chỉ đổi transform rồi kiểm bằng manifold3d hoặc FCL) **khớp** với mô hình của trimesh/FCL và IfcClash. Đó là cách chuẩn trong các hệ thống ngoài FreeCAD. Không nguồn nào mâu thuẫn với số đo của lab.
- Một rủi ro mà constraint-kit chỉ ra: chỉ kiểm ở các trạm rời rạc vẫn có thể bỏ sót va chạm giữa hai trạm (tunneling). Bước góc phải đủ nhỏ so với độ dày chi tiết, hoặc dùng FCL continuous collision. Mình chưa kiểm python-fcl có hỗ trợ continuous collision không (TODO).

### Gaps
- Chưa xác minh KinematicsWB (galou) vì repo trả 404, và chưa xác minh Robot WB cũ của FreeCAD có kiểm va chạm không.
- Không tìm được thread nào trên forum.freecad.org (Assembly subforum) về sweep + collision. Các lượt tìm chỉ ra issue GitHub.
