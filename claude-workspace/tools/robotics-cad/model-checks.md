# Kiểm tra model FreeCAD trước khi in 3D

Dự án robotics – STLab. Máy: Windows 11, **FreeCAD 1.1.4** (`App.Version()` = 1.1.4, build 2026-09-28, git `4fd3bf32` = tag `1.1.4`), máy in Bambu Lab A1, nhựa PLA/PETG.
Viết ngày 2026-10-21. Mọi đoạn code ghi "đã chạy" đều đã chạy bằng `freecadcmd.exe` trên máy này, cùng ngày. Đơn vị: mm, N, MPa, g, °C.

---

## 0. Tóm tắt 1 trang – checklist trước khi in

| # | Kiểm | Công cụ GUI | API / lệnh (đã chạy) | Ngưỡng đạt |
|---|------|-------------|----------------------|------------|
| 1 | Solid hợp lệ, kín | Part → Check Geometry (bật **Run boolean operation check**) | `s.isValid()`, `s.check(True)`, `len(s.Solids)==1`, `sh.isClosed()` | isValid True, BOP "OK", đúng 1 solid, mọi shell kín |
| 2 | Bỏ cạnh thừa | PartDesign/Part: thuộc tính **Refine = true** | `s.removeSplitter()` | – |
| 3 | Va chạm tĩnh trong lắp ráp | Assembly (không có lệnh kiểm giao thoa) | `a.common(b).Volume`, `a.distToShape(b)[0]` | common = 0 mm³; khe hở ≥ dung sai thiết kế (TODO A1) |
| 4 | Va chạm khi khớp quay hết hành trình | Assembly → Simulation (chỉ xem bằng mắt) | quét góc: xoay shape / chỉnh `Offset2` của joint + `asm.solve()` rồi `common()` | common = 0 ở mọi bước góc |
| 4b | **Lắp được** (2026-10-26): chi tiết in rời có đường đưa vào chỗ | không có | `scripts/assembly_paths.py` (tịnh tiến 12 hướng, bước 0,2 mm) | mọi cặp đang chạm có hướng tách; ngoại lệ ghi lý do |
| 5 | Thành mỏng | không có công cụ đo độ dày có sẵn | script bắn tia `solid.common(LineSegment)` (mục 5.2) | ≥ 0,84 mm = 2 × đường in 0,42 mm (đầu 0,4 mm mặc định, skill `bambu-a1`); chịu lực: 1,2–1,6 mm |
| 6 | Overhang | không có công cụ phân tích draft trong FreeCAD 1.1 | duyệt facet mesh, `Normal.z < -cos(45°)` (mục 5.3) | góc với mặt bàn ≥ 45° hoặc có support (Bambu wiki) |
| 7 | Lưới xuất ra sạch | Mesh → Analyze → **Evaluate and Repair** | `m.isSolid()`, `hasNonManifolds()`, `hasSelfIntersections()`, `countNonUniformOrientedFacets()` | isSolid True, các has* False, 0 facet ngược |
| 8 | Độ mịn lỗ lắp ghép | Mesh From Shape: Surface/Angular deviation | `MeshPart.meshFromShape(..., LinearDeflection, AngularDeflection)` | sai lệch đường kính lỗ < 0,01 mm (xem bảng 2.3) |
| 9 | Khối lượng, trọng tâm, quán tính | Check Geometry → *Expand shape content*; Measure → Center of mass | `Volume`, `CenterOfMass`, `MatrixOfInertia`, `PrincipalProperties` | so với cân thực tế sau in |
| 10 | Độ bền (chi tiết chịu lực) | FEM: Gmsh + CalculiX | `ObjectsFem` + `femtools.ccxtools.FemToolsCcx` | σ_vonMises × hệ số an toàn (TODO) < độ bền theo **phương Z** của TDS |
| 11 | Xuất file | File → Export | STEP: `Import.export`; 3MF: `mesh.write("x.3mf")` | Khuyến nghị **STEP** cho Bambu Studio (mục 2.4) |
| 12 | Tự động hóa | Test workbench (tắt mặc định từ 1.1) | `freecadcmd -P <thư mục> -t <module_test>` → exit code 1 khi FAIL | – |

Thứ tự khuyến nghị: **1 → 2 → 3/4/4b → 5/6 → 9 → 10 (nếu chịu lực) → 7/8 → 11**. Lỗi hình học (bước 1) làm sai mọi bước sau (boolean, khối lượng, mesh), nên luôn sửa trước.

---

## 1. Kiểm hình học solid

### 1.1 Làm gì / GUI
- **Part → Check Geometry**: kiểm B-rep có hợp lệ không. Tùy chọn (wiki [S1]): *Skip this settings page*, **Run boolean operation check** (BOP), *Single-threaded* (chậm hơn nhưng ổn định hơn), *Log errors*, *Expand shape content* (hiện số vertex/edge/face/shell/solid, diện tích, thể tích, khối lượng, trọng tâm, mômen quán tính, bán kính quán tính…), *Advanced shape content*, và chọn từng loại BOP check: *Bad type, Self-intersect, Too small edge, Nonrecoverable face, Continuity, Incompatibility of face/vertex/edge, Invalid curve on surface*.
- Bản 1.1 bổ sung: hiển thị tolerance trong tab Shape Content, mục kết quả cho shape hợp lệ, báo cáo ra Report view; thêm công cụ **Part → Set Tolerance** [S2].
- Wiki ghi rõ: *FreeCAD không có cách tự sửa hình học* – lỗi phải sửa ở bước dựng model [S1].
- **Refine**: thuộc tính `Refine` của feature Part/PartDesign, hoặc Part → Copy → Refine Shape; bỏ cạnh thừa trên mặt phẳng/trụ, tránh in ra vết cạnh không mong muốn [S3].

### 1.2 API (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
```python
import Part
s = Part.Shape(); s.read(r"...\file.step")
ok      = s.isValid()                      # B-rep hợp lệ
nsolid  = len(s.Solids)                    # phải = 1 cho chi tiết in
closed  = all(sh.isClosed() for sh in s.Shells)
try:
    s.check(True)                          # True = chạy thêm BOP check; lỗi -> ném exception kèm danh sách lỗi
    bop = "OK"
except Exception as e:
    bop = str(e)
refined = s.removeSplitter()               # tương đương Refine
f = s.copy(); fixed = f.fix(1e-7, 1e-7, 1e-3)   # (tol, minTol, maxTol) -> bool
```

Kết quả thử với STEP trong thư viện (`library/components.yaml`):

| Model | isValid | `check()` | `check(True)` (BOP) | Ghi chú |
|---|---|---|---|---|
| SG90 + horn (freecad-library) | True | OK | OK | Shape là **Compound** 1 solid |
| 608ZZ | True | OK | OK | Solid |
| N20 tiêu chuẩn (Pololu) | True | OK | lỗi `BOPAlgo GeomAbs_C0` (nhiều face) | **1 solid nhưng 3 shell** |
| N20 hộp số 1000:1 | **False** | `Self-intersecting wire`, `Unorientable shape` | như bên trái | `fix()` trả False, vẫn lỗi |
| Servo 9g CyberBrick | True | OK | lỗi `BOPAlgo SelfIntersect` | isValid True nhưng BOP vẫn báo lỗi |
| Mặt "nơ" tự cắt đùn lên (tự tạo) | False | Self-intersecting wire | – | Volume = 0 mm³ |
| 2 hộp fuse | – | – | – | 10 face → 6 face sau `removeSplitter()` |
| Shell hở (hộp bỏ 1 mặt) | True (!) | – | – | `isClosed()` False, 0 solid, nhưng `Volume` vẫn trả 800 mm³ |

### 1.3 Cạm bẫy
- **`isValid()` True chưa đủ**: servo CyberBrick qua `isValid` nhưng BOP báo SelfIntersect. Luôn chạy BOP (`check(True)`) cho chi tiết sẽ cắt/fuse.
- **Shell hở vẫn có `Volume`** khác 0 → không dùng Volume để kết luận "kín"; kiểm `Solids` và `isClosed()`.
- STEP linh kiện mua (N20 1000:1) lỗi và `fix()` không sửa được. Với linh kiện **không in**, lỗi này chỉ ảnh hưởng khi dùng nó làm dao cắt boolean → nên cắt bằng **khối bao đơn giản** (hộp/trụ theo kích thước datasheet) thay vì cắt bằng STEP gốc.
- Kết quả boolean (`fuse/cut`) trả về **Compound** (đã thấy: `ShapeType == "Compound"`); Compound **không có** thuộc tính `CenterOfMass`/`MatrixOfInertia` → lấy `shape.Solids[0]`.
- Module `Part.ShapeFix` / ShapeFix chi tiết: **chưa thử**.

---

## 2. Kiểm lưới trước khi xuất STL/3MF

### 2.1 GUI
- **Meshes → Analyze → Evaluate and Repair**: các kiểm tra trong hộp thoại (lấy từ `DlgEvaluateMesh.ui` tag 1.1.4 [S4]): *Orientation, Duplicated faces, Duplicated points, Non-manifolds, Degenerated faces, Face indices, Self-intersections, Folds on surface* (tùy chọn), *All above tests together*, nút *Repair*, *Repetitive repair*.
- Wiki ghi: lệnh này **không phát hiện lỗ hở** – dùng **Mesh EvaluateSolid**; sửa lỗi có thể xoá facet tạo lỗ, vá bằng *Mesh FillupHoles* [S5].
- Tạo mesh từ shape: **Meshes → Mesh From Shape**, mesher Standard có *Surface deviation* (độ lệch tuyến tính tối đa) và *Angular deviation* [S6]. File → Export trực tiếp từ Part dùng *Maximum mesh deviation* trong Preferences → Import-Export → Mesh Formats; có tùy chọn *Export 3MF as model type* [S7].

### 2.2 API (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
```python
import MeshPart
m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.2618, Relative=False)
rep = {
  "isSolid": m.isSolid(),                      # kín (không lỗ)
  "nonManifold": m.hasNonManifolds(),
  "selfIntersect": m.hasSelfIntersections(),
  "flipped": m.countNonUniformOrientedFacets(),# normal ngược
  "components": m.countComponents(),           # >1: nhiều mảnh rời/chồng nhau
  "corrupt": m.hasCorruptedFacets(), "invalidPts": m.hasInvalidPoints(),
}
# sửa (chạy trên bản copy):
m2 = m.copy()
m2.fillupHoles(1000, 0, 0.0); m2.fixDegenerations(0.0)
m2.removeDuplicatedFacets(); m2.removeDuplicatedPoints(); m2.fixIndices()
m2.harmonizeNormals(); m2.removeNonManifolds(); m2.fixSelfIntersections()
m.write("chi-tiet.3mf")                        # đuôi file quyết định định dạng (stl, 3mf, obj đã thử)
```
Kết quả thử:
- Tấm 30×30×5 mm có lỗ Ø3 mm: mesh sạch (`isSolid` True, các `has*` False).
- Xoá 3 facet → `isSolid` False (các `has*` khác vẫn False – **chỉ `isSolid` bắt được lỗ**); sau chuỗi sửa trên → `isSolid` True, đủ 208 facet.
- Thêm 1 facet trùng ngược → `hasSelfIntersections` True, `hasPointsOnEdge` True, 2 component.
- 2 hộp chồng nhau gộp 1 mesh → `isSolid` **True** nhưng `hasSelfIntersections` True; `fixSelfIntersections()` xoá facet → hết tự cắt nhưng `isSolid` thành False. ⇒ **Sửa chồng lấn ở CAD (fuse), đừng sửa ở mesh.**
- Mesh của STEP N20 tiêu chuẩn (solid 3 shell): `hasNonManifolds` True, `hasSelfIntersections` True, `isSolid` False, 4 component.
- Định dạng: `.stl`, `.3mf`, `.obj` ghi được; `.amf` báo "File format not supported" khi gọi `mesh.write`. Đọc lại 3MF đủ 208 facet.

### 2.3 Tessellation và lỗ lắp ghép (đã chạy)
Lỗ Ø3 mm, đo số đoạn thẳng xấp xỉ đường tròn; đa giác nội tiếp nên **lỗ nhỏ đi** ở giữa mỗi đoạn:

| LinearDeflection (mm) | AngularDeflection (rad) | Số đoạn trên lỗ | Đường kính nội tiếp (mm) | Facet |
|---|---|---|---|---|
| 0,5 | 0,5236 | 24 | 2,9743 | 112 |
| 0,1 | 0,5236 | 24 | 2,9743 | 112 |
| 0,05 | 0,2618 | 48 | 2,9936 | 208 |
| 0,01 | 0,0873 | 144 | 2,9993 | 592 |

- Với lỗ nhỏ, **AngularDeflection quyết định**, LinearDeflection 0,5 hay 0,1 mm cho cùng kết quả. Thiếu ~0,026 mm đường kính ở 0,5236 rad.
- Khuyến nghị: `LinearDeflection=0.05`, `AngularDeflection=0.2618` (15°) → sai < 0,01 mm, file vẫn nhỏ. Sai số này nhỏ hơn nhiều so với sai số in FDM (TODO đo A1), nhưng cộng dồn vào dung sai.

### 2.4 Nên xuất gì cho Bambu Studio – khuyến nghị
**Khuyến nghị: STEP** cho chi tiết đơn/lắp ráp. Bambu Studio nhập STEP (dựa trên OpenCASCADE), tự chia lưới với dung sai nhỏ hơn một nửa dung sai arc-fitting mặc định, giữ đường cong để sinh nhiều lệnh cung G2/G3 hơn, và giữ vị trí tương đối các part trong Assembly View [S8].
- Đánh đổi: STEP để Studio quyết định độ mịn (chỉnh *linear/angle deflection* trong Studio); lỗi B-rep trong STEP sẽ thành lỗi mesh ở Studio → phải qua bước 1 trước.
- **3MF** khi muốn tự kiểm soát lưới (đã evaluate ở FreeCAD) hoặc khi STEP nhập lỗi; nhỏ hơn STL (đã thấy 2,6 kB vs 10,5 kB cùng mesh). **STL** chỉ để tương thích; không mang đơn vị.

---

## 3. Va chạm / giao thoa và chuyển động

### 3.1 Assembly workbench FreeCAD 1.1
- Dùng solver mã nguồn mở **Ondsel solver** [S9]. Joint (đọc từ `JointObject.py` bản cài): Fixed, Revolute, Cylindrical, Slider, Ball, Distance, Parallel, Perpendicular, Angle, RackPinion, Screw, Gears, Belt. Revolute có `AngleMin/AngleMax` + `EnableAngleMin/Max`; Slider/Cylindrical có `LengthMin/Max`.
- **Simulation (mới ở 1.1)** – Assembly → Simulation: thêm *Motion* (chọn joint Revolute/Slider/Cylindrical, kiểu Angular/Linear, công thức theo `time`), đặt Start/End/Step/Tolerance, **Generate** rồi phát animation [S10][S11]. Đây là mô phỏng **động học** (vị trí theo thời gian), không có lực/động lực học.
- **Không có lệnh phát hiện giao thoa/va chạm** trong Assembly 1.1: không tìm thấy lệnh nào trong danh sách công cụ của wiki [S9] và grep `interfer|collision` trong `Mod/Assembly` bản cài không ra lệnh nào. ⇒ kiểm giao thoa bằng script.

### 3.2 Kiểm giao thoa bằng script (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
```python
v = a.common(b).Volume          # > 0 -> chồng lấn (mm³)
d = a.distToShape(b)[0]         # khoảng cách nhỏ nhất (mm); 0 nếu chạm/chồng
# quét góc khớp quay quanh trục Z qua gốc:
for deg in range(0, 91, 10):
    arm = arm0.copy(); arm.rotate(App.Vector(0,0,0), App.Vector(0,0,1), deg)
    print(deg, arm.common(obst).Volume, arm.distToShape(obst)[0])
```
- SG90 + horn (2 STEP để rời): common 0 mm³, khoảng cách 20,13 mm; dời horn vào thân: common 146,98 mm³, d = 0. Mỗi phép ~0,01 s.
- Quét tay 60×10×5 mm qua vật cản: giao ở 20°–40° (85 / 453 / 26 mm³), không giao ở 10° và 50° → **bước góc 10° có thể bỏ sót chi tiết mảnh**; chọn bước sao cho cung quét ở đầu tay < bề dày nhỏ nhất của vật, hoặc dùng `distToShape` giảm dần để tinh chỉnh quanh vùng nghi ngờ.
- Assembly headless (đã chạy): tạo `Assembly::AssemblyObject`, `JointObject.GroundedJoint`, `JointObject.Joint(j, 1)` (Revolute), `j.Proxy.setJointConnectors(j, [[base,["Face6","Vertex6"]],[arm,["Face5","Vertex1"]]])`, `asm.solve()` trả 0; đổi `j.Offset2 = App.Placement(App.Vector(), App.Rotation(App.Vector(0,0,1), deg))` rồi `asm.solve()` → tay quay đúng (yaw = −deg, **chú ý dấu ngược**). Sau đó lấy `arm.Shape` để `common()`. Cách này dùng được cho quét góc trên lắp ráp thật; tham chiếu `Face/Vertex` phải lấy từ joint đã tạo trong GUI.
- Cạm bẫy: `common()` cần solid hợp lệ (bước 1); hai mặt chỉ chạm nhau cho Volume ≈ 0 → dùng `distToShape` để kiểm **khe hở tối thiểu**, không chỉ "có chồng hay không".

### 3.3 RobotCAD v12.10.3 (đọc mã nguồn local)
- Joint có `LowerLimit`/`UpperLimit` (nhóm *Limits*), xuất vào thẻ `<limit lower upper>` của URDF (`joint_proxy.py`). Bộ chuyển Assembly → RobotCAD ánh xạ `AngleMin/AngleMax` của Revolute sang `LowerLimit/UpperLimit` (`wb_constants.py`, `ASSEMBLY_WB_JOINTS_MATCHING`).
- Collision: mỗi link có phần tử *Real / Visual / Collision*; có công cụ tạo collision từ bounding box (hộp, cầu, trụ theo trục) hoặc bản sao vật thể (`ui/command_*_from_bounding_box.py`, `command_create_collision_copy_obj.py`) – dùng cho URDF/Gazebo, **không** phải bộ kiểm va chạm trong FreeCAD.
- Có tool MCP `check_overlap` (`mcp/tools_registry.py`): quyết định chồng lấn bằng `child.common(parent).Volume` (ngưỡng 1e-6), kèm AABB và `distToShape` – cùng phương pháp mục 3.2, chỉ cho cặp link cha-con ở tư thế hiện tại.
- Va chạm theo hành trình khớp / self-collision: cần mô phỏng ngoài (Gazebo/MoveIt – yêu cầu Linux/WSL2 như CLAUDE.md đã ghi). Phần này **chưa thử**.

---

## 4. Độ bền: FEM + CalculiX

### 4.1 FreeCAD 1.1 trên máy có ccx/Gmsh không?
- Có: `C:/Program Files/FreeCAD 1.1/bin/ccx.exe` (**CalculiX 2.22**, `ccx -v`), `bin/gmsh.exe` (**Gmsh 4.15.0**), `bin/NETGENPlugin.dll` + `nglib4smesh.dll`.
- **Cạm bẫy (đã gặp):** FEM tìm `ccx` và `gmsh` bằng `shutil.which()` qua PATH hoặc đường dẫn trong Preferences (`femtools/ccxtools.py`, `femmesh/gmshtools.py`). Trong `freecadcmd` trên máy này `bin/` **không có trong PATH** và Preferences để trống → báo "Gmsh binary not found". Cách xử lý không cần sửa cấu hình: đầu script thêm
  `os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]`.
  Trong GUI: **chưa thử**; nếu lỗi thì đặt *Gmsh path* / *CalculiX binary* trong Preferences → FEM [S12].
- Netgen **mới** (1.1) cần Python binding `netgen` cài riêng [S13] – trên máy **không có** (`No module named 'netgen'`). Netgen **legacy** (`ObjectsFem.makeMeshNetgenLegacy`) chạy được headless (thử: 9 614 nút). Khuyến nghị dùng **Gmsh** (có sẵn, đã kiểm).

### 4.2 Quy trình tĩnh tuyến tính (GUI)
Analysis container → Solver CalculiX (static) → Material solid (E, ν) → Constraint Fixed (mặt bắt vít) → Constraint Force (N, hướng) → Mesh Gmsh (ElementOrder 2nd, CharacteristicLengthMax) → Run → xem von Mises, chuyển vị. Ví dụ mẫu có sẵn: `Mod/Fem/femexamples/ccx_cantilever_faceload.py`. 1.1 có tùy chọn solver CalculiX bản refactor chỉ lưu kết quả vào pipeline [S13].

### 4.3 Script hóa (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
Dầm công-xôn 100×10×10 mm, ngàm mặt x=0, lực 10 N hướng −Z ở mặt x=100, **E = 2000 MPa, ν = 0,35 là giá trị thử, không phải số liệu vật liệu**:
```python
import os, sys, FreeCAD as App, ObjectsFem
os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]
from femtools import ccxtools
from femmesh.gmshtools import GmshTools
doc = App.newDocument("fem")
box = doc.addObject("Part::Box", "Box"); box.Length, box.Width, box.Height = 100, 10, 10; doc.recompute()
an = ObjectsFem.makeAnalysis(doc, "Analysis")
sol = ObjectsFem.makeSolverCalculiXCcxTools(doc, "CalculiXCcxTools")
sol.AnalysisType = "static"; sol.GeometricalNonlinearity = "linear"; an.addObject(sol)
mo = ObjectsFem.makeMaterialSolid(doc, "Mat"); m = mo.Material
m["Name"] = "TestPolymer"; m["YoungsModulus"] = "2000 MPa"; m["PoissonRatio"] = "0.35"; mo.Material = m; an.addObject(mo)
fx = ObjectsFem.makeConstraintFixed(doc, "Fixed"); fx.References = [(box, "Face1")]; an.addObject(fx)
fo = ObjectsFem.makeConstraintForce(doc, "Force"); fo.References = [(box, "Face2")]
fo.Force = "10 N"; fo.Direction = (box, ["Edge5"]); fo.Reversed = True; an.addObject(fo)   # Edge5 // +Z
msh = ObjectsFem.makeMeshGmsh(doc, "Mesh"); msh.Shape = box
msh.CharacteristicLengthMax = "2.0 mm"; msh.ElementOrder = "2nd"; an.addObject(msh); doc.recompute()
GmshTools(msh).create_mesh()
fea = ccxtools.FemToolsCcx(an, sol)
fea.purge_results(); fea.update_objects(); fea.setup_working_dir()
assert fea.check_prerequisites() == ""
fea.write_inp_file(); fea.ccx_run(); fea.load_results()
r = [o for o in an.Group if o.isDerivedFrom("Fem::FemResultObject")][0]
print(max(r.DisplacementLengths), max(r.vonMises))   # mm, MPa
```
| Đại lượng | FEM (Tet10, 11 233 nút) | Giải tích (Euler-Bernoulli) |
|---|---|---|
| Võng đầu dầm | 2,0005 mm | F·L³/(3·E·I) = 2,000 mm |
| σ max (ngàm) | 6,013 MPa | M·c/I = 6,000 MPa |
| σ ở x = 50 mm, thớ trên | 3,061 MPa | 3,000 MPa |

Thời gian: Gmsh 0,6 s, CalculiX ~4,4 s. Chuỗi Gmsh → ccx → đọc kết quả **chạy được** trong freecadcmd.

### 4.4 Số liệu vật liệu (TDS chính hãng Bambu Lab, mẫu in 100% infill)

| Vật liệu (TDS) | Khối lượng riêng | E (X-Y) | E (Z) | σ kéo (X-Y) | σ kéo (Z) | HDT 0,45 MPa | Max overhang (TDS) |
|---|---|---|---|---|---|---|---|
| PLA Basic (V3.0) [S14] | 1,24 g/cm³ | 2580 ± 220 MPa | 2060 ± 170 MPa | 35 ± 4 MPa | 31 ± 3 MPa | 57 °C | 55° |
| PETG Basic (V3.0) [S15] | 1,25 g/cm³ | 2780 ± 65 MPa | 2550 ± 100 MPa | 51 ± 1 MPa | 35 ± 6 MPa | 71 °C | ~70° |
| PETG HF (V1.0) [S16] | 1,28 g/cm³ | 1810 ± 190 MPa | 1540 ± 130 MPa | 34 ± 4 MPa | 23 ± 4 MPa | 69 °C | ~70° |

- Điều kiện mẫu: infill 100%; mẫu PLA được ủ/sấy 55 °C 8 h, PETG HF 75 °C 8 h trước khi thử (theo TDS). TDS ghi giá trị **chỉ để tham khảo thiết kế**, chi tiết thật phụ thuộc máy in, thông số in, model.
- **Hệ số Poisson ν: TDS không có → TODO** (bài thử dùng 0,35 chỉ để chạy chuỗi).
- Bảng được trích bằng `pdftotext -table`; bản `-layout` lệch cột (dễ đọc nhầm) – nếu dùng số nào cho tính toán quan trọng, mở PDF gốc đối chiếu.
- TDS **không ghi rõ** "Max overhang angle" đo từ phương nào (khác với quy ước góc so với mặt bàn của Bambu wiki ở mục 5) → coi là tham khảo.

### 4.5 Rủi ro khi dùng FEM cho chi tiết in FDM – đọc kỹ
1. **Dị hướng**: FEM ở trên dùng vật liệu **đẳng hướng**. Chi tiết in yếu hơn theo phương Z (giữa các lớp): PETG HF σ_Z/σ_XY ≈ 23/34 ≈ 0,68. Khuyến nghị: nhập **E_Z và so ứng suất với σ_Z** (bảo thủ), và đặt hướng in sao cho ứng suất kéo chính nằm trong mặt XY.
2. **Infill/thành**: số liệu TDS là 100% infill; in 15–20% infill thì độ cứng và bền thấp hơn nhiều – mức giảm **TODO** (không có số liệu chính hãng). Chi tiết chịu lực: tăng số wall / infill hoặc mô hình hóa như chi tiết đặc rồi kiểm bằng mẫu thử.
3. **Ứng suất cực đại ở ngàm/góc nhọn** là điểm kỳ dị lưới: làm mịn lưới thì σ max có thể tăng mãi. Đọc ứng suất cách ngàm một đoạn, bo góc trong model, kiểm hội tụ lưới (2 kích thước lưới).
4. Nhựa **rão (creep)** và mềm dần khi nóng (HDT PLA 57 °C ở 0,45 MPa) – FEM tuyến tính tĩnh không thấy được. Chi tiết gần động cơ/pin hoặc ngoài nắng: ưu tiên PETG.
5. **Hệ số an toàn: TODO** – chưa tìm được nguồn chính hãng/tiêu chuẩn cho chi tiết FDM. Đề xuất STLab tự xác định bằng thử phá hủy mẫu in thật (cùng thông số in) rồi ghi vào tools/robotics-cad/CLAUDE.md. Cho tới khi có: coi kết quả FEM chỉ để **so sánh phương án** (A cứng hơn B), không để khẳng định "đủ bền".

---

## 5. Đặc thù in FDM

### 5.1 Khuyến nghị nhà sản xuất (có nguồn)
- **Overhang**: Bambu wiki – góc giữa mặt nghiêng và **mặt bàn** < 45° thì nên thêm support, > 45° thì không cần [S17]. (Ngưỡng *support threshold angle* trong Bambu Studio là khái niệm khác; giá trị nhập càng lớn càng nhiều support [S17].)
- **Bridge tối đa**: TDS PLA Basic 30 mm, PETG Basic/HF ~30 mm [S14][S15][S16].
- **Độ dày thành tối thiểu, dung sai lỗ/trục/snap-fit cho A1: TODO** – chưa thấy số chính hãng; STLab in mẫu dung sai (mẫu cũ maker/in-3d đã xóa 2026-10-23) rồi ghi vào `maker/in-3d/CLAUDE.md` (bảng hiện đang TODO).

### 5.2 Đo độ dày thành (script, đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
FreeCAD 1.1 **không có công cụ đo độ dày** (`Part Thickness` là lệnh *tạo vỏ rỗng*, không phải đo). Cách đã thử, chạy trên B-rep:
```python
def wall_thickness(solid, n=3):
    L = solid.BoundBox.DiagonalLength; res = []
    for fi, f in enumerate(solid.Faces):
        u0, u1, v0, v1 = f.ParameterRange
        for i in range(n):
            for j in range(n):
                u = u0 + (i + .5) * (u1 - u0) / n; v = v0 + (j + .5) * (v1 - v0) / n
                p = f.valueAt(u, v)
                if not f.isInside(p, 1e-6, True): continue
                nn = f.normalAt(u, v)
                if solid.isInside(p + nn * 1e-3, 1e-6, False): nn = -nn   # bảo đảm normal hướng ra
                seg = Part.LineSegment(p - nn * 1e-4, p - nn * L).toShape()
                c = solid.common(seg)                  # đoạn tia nằm trong vật
                if c.Edges:
                    e = min(c.Edges, key=lambda e: min((e.Vertexes[0].Point - p).Length, (e.Vertexes[-1].Point - p).Length))
                    res.append((e.Length + 1e-4, fi + 1, p))
    return sorted(res, key=lambda t: t[0])
```
Thử với vách 0,6 mm: trả đúng 0,6 mm tại Face3. Giới hạn: lấy mẫu 3×3 điểm/face → có thể **bỏ sót** gân nhỏ; tăng `n` cho chi tiết quan trọng (chậm hơn).
Lưu ý: `Mesh.nearestFacetOnRay()` **không dùng được** cho việc này – thử bắn tia từ trong ra, nó trả về facet ngay phía sau điểm gốc (khoảng cách ~0) thay vì mặt đối diện.

### 5.3 Phân tích overhang (script, đã chạy)
FreeCAD 1.1 không có công cụ phân tích draft/overhang tích hợp. Dùng normal facet của mesh:
```python
import math
zmin = s.BoundBox.ZMin; lim = 45.0     # độ, góc với mặt bàn (quy ước Bambu wiki)
area = sum(ft.Area for ft in m.Facets
           if ft.Normal.z < -math.cos(math.radians(lim))            # mặt úp xuống, dốc hơn 45°
           and sum(v[2] for v in ft.Points) / 3 > zmin + 0.01)      # bỏ mặt đáy nằm trên bàn
```
Thử: mái ngang 30×7,4 mm giữa 2 vách → 222,0 mm² (đúng giải tích). Kết quả phụ thuộc **hướng đặt in** – chạy lại sau khi xoay chi tiết theo hướng sẽ in. Ngưỡng 45° là của wiki; ngưỡng thực tế A1 cho PLA/PETG STLab: TODO (in mẫu overhang).

---

## 6. Khối lượng, trọng tâm, quán tính

### 6.1 API (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
```python
so = shape.Solids[0]                 # Compound không có CenterOfMass!
V   = so.Volume                      # mm³
com = so.CenterOfMass                # mm
I   = so.MatrixOfInertia             # mật độ = 1, quanh trọng tâm, đơn vị mm^5 (= mm³·mm²)
pp  = so.PrincipalProperties         # Moments, FirstAxisOfInertia..., RadiusOfGyration
rho = 1.24e-3                        # g/mm³ (PLA Basic TDS 1,24 g/cm³)
mass_g = V * rho
I_kg_m2 = I * (mass_g / 1000 / V) * 1e-6   # nhân khối lượng/thể tích, mm² -> m²
```
- Kiểm chứng: hộp 10×20×30 mm, `MatrixOfInertia.A33` = 250 000 = V·(10²+20²)/12 → đúng công thức, quanh trọng tâm, mật độ 1.
- Gá thử (thể tích 5 247,83 mm³) → nếu đặc 100% PLA: 5,24783 cm³ × 1,24 g/cm³ ≈ 6,51 g.
- GUI: Check Geometry → *Expand shape content* hiện Volume, Mass, Center of mass, Moments, trục quán tính [S1]; Measure có *Center of mass* (`Mod/Measure/MeasureCOM.py`). **Không thấy lệnh "Mass properties" riêng trong 1.1** (không có trong release notes 1.1 [S2], không tìm thấy trong bản cài).

### 6.2 RobotCAD tính thế nào (mã nguồn `ui/command_calculate_mass_and_inertia.py`, `freecad_utils.py`)
- Lấy shape *Real* của link → `Shape.MatrixOfInertia` (nhiều solid thì cộng theo định lý trục song song), khối lượng = `Volume × density` từ *material card* của link (hoặc của robot nếu link không có).
- Quy đổi: `I × mass / volume_mm3 × 1e-6` → kg·m²; tính trọng tâm toàn robot và vị trí joint so với trọng tâm tổng.
- Tùy chọn `CalculateInertiaBasedOnMass`: nhập **khối lượng cân thực tế**, RobotCAD giữ phân bố đều theo hình học. `MaterialNotCalculate`: bỏ qua link, nhập tay.

### 6.3 Cạm bẫy
- Khối lượng in **khác** solid vì infill/thành/top-bottom: khuyến nghị lấy khối lượng ước tính của Bambu Studio sau khi slice (hoặc cân chi tiết in) rồi dùng `CalculateInertiaBasedOnMass`. Sai lệch phân bố quán tính do infill: TODO (chưa đo).
- Linh kiện mua (servo, động cơ, pin): dùng khối lượng datasheet trong `components.yaml`, không dùng `Volume × ρ` của STEP (STEP thường rỗng/đơn giản hóa, vd. N20 nhiều shell).

---

## 7. Kiểm tự động

### 7.1 Test framework của FreeCAD (đã chạy)
- `freecadcmd -t` (không đối số) liệt kê test: TestAssemblyWorkbench, TestPartApp, TestPartDesignApp, MeshTestsApp, TestFemApp… [S18]. Test workbench bị **tắt mặc định từ 1.1** [S18][S2].
- `freecadcmd -t TestAssemblyWorkbench`: 8 test, OK (skipped=2), 0,16 s.
- **Test riêng của STLab**: viết module `unittest` bình thường, chạy
  `freecadcmd -P <thư-mục-chứa-module> -t test_stlab_drc`
  Đã thử: in kết quả từng test, **exit code 1** khi có FAIL, 0 khi đạt → dùng được trong script/CI.
- Truyền đối số cho script: `freecadcmd script.py --pass file.FCStd x=1` → `sys.argv` nhận `--pass file.FCStd x=1`. Không dùng `--pass` thì đối số thừa bị FreeCAD coi là **file cần mở**.
- stdout của freecadcmd lẫn thanh tiến độ (`(  5 %)`…) → ghi kết quả ra **JSON** thay vì đọc stdout.

### 7.2 Mẫu "design rule check" cho .FCStd (đã chạy trên FreeCAD 1.1.4 ngày 2026-10-21)
Luồng đã thử trên file mẫu (1 Body PartDesign + 1 Part::Feature):
1. `App.openDocument(fcstd)`; chọn đối tượng gốc: `PartDesign::Body`, và `Part::Feature` không có `InList` / không nằm trong Body.
2. Mỗi đối tượng: `isValid`, `check(True)`, số solid, shell kín (mục 1) → thể tích, trọng tâm, bounding box (mục 6) → mesh 0,05 mm / 0,2618 rad và evaluate (mục 2) → độ dày thành (5.2) → diện tích overhang (5.3) → ghi 3MF.
3. `json.dump(report)`; `App.closeDocument()`.
Kết quả mẫu: Body đạt mọi kiểm tra; chi tiết vách mỏng báo overhang 222 mm². Lần chạy DRC này đo độ dày bằng `Mesh.nearestFacetOnRay` nên **không ra số** (xem cạm bẫy 5.2); hàm B-rep ở 5.2 được thử riêng trên cùng hình học và trả 0,6 mm (< ngưỡng thử 0,8 mm → sẽ FAIL đúng mong đợi). Khi viết script thật, dùng hàm 5.2.

### 7.3 Lưu ý môi trường máy
- Mỗi lần chạy freecadcmd có lỗi `Error in InitApplications … Mod\freecad.robotcad\freecad\robotcad` (WinError 2): `package.xml` của RobotCAD khai báo `<subdirectory>freecad/robotcad</subdirectory>` nhưng thư mục thật là `freecad/cross`. Các thử nghiệm trên vẫn chạy và `import freecad.cross` vẫn được; không sửa (thuộc `community/`). Có thể báo upstream – TODO.
- Thông báo `ROS_DISTRO is not set` của RobotCAD là bình thường trên Windows.

---

## 8. Đề xuất bước tiếp

> **Cập nhật 2026-10-23:** mục 1 đã làm thành `scripts/check.py`, nhưng đo độ dày (5.2) và va chạm (3.2) chuyển sang
> **lưới** (numpy/scipy + manifold3d) vì bản B-rep quá chậm (bánh răng ~700 s/chi tiết). Khả năng in theo hướng in thật
> giao cho slicer: `scripts/slice.py` (Bambu Studio CLI); cả vòng: `scripts/prepare-print.py`. Quy trình 2 tầng: xem `CLAUDE.md` mục Quy trình.
> Bản B-rep ở 5.2 lấy mẫu 3×3 điểm/mặt nên **bỏ sót** mép sắc 0,02–0,12 mm mà bản lưới bắt được (đã đối chiếu cùng tia).
1. Viết `tools/robotics-cad/scripts/kiem-tra.py`: gom mục 1, 2, 3.2, 5.2, 5.3, 6 thành 1 script chạy `freecadcmd scripts/kiem-tra.py --pass <file.FCStd> [--quet-khop <joint>:<min>:<max>:<buoc>]`, ghi `bao-cao-kiem-tra.json` + 3MF; tự thêm `bin/` vào PATH cho FEM. Ngưỡng (độ dày, overhang, dung sai) đọc từ 1 file YAML, mặc định `TODO` → báo "chưa có ngưỡng" thay vì tự đoán.
2. In mẫu dung sai + overhang + bridge trên A1 (PLA, PETG) → ghi kết quả vào tools/robotics-cad/CLAUDE.md, rồi đưa ngưỡng vào YAML.
3. In và kéo/uốn mẫu đơn giản (cùng thông số in) để có hệ số hiệu chỉnh FEM ↔ thực tế và hệ số an toàn cho STLab.
4. Bọc các kiểm tra thành `unittest` (7.1) để chạy hàng loạt mọi file trong `models/`.

## 9. Danh sách TODO
- Dung sai lắp ghép A1 (lỗ, trục, ổ bi 608, M3, snap-fit) – chờ mẫu `mau-dung-sai-a1`.
- Độ dày thành tối thiểu cho STLab (theo đầu phun đang dùng – chưa biết).
- Ngưỡng overhang thực tế A1 cho PLA/PETG.
- Hệ số an toàn cho chi tiết FDM; mức giảm bền theo infill; hệ số Poisson PLA/PETG (TDS không có).
- Kiểm FEM trong GUI có tự tìm Gmsh/ccx không.
- Mô phỏng va chạm theo hành trình bằng Gazebo/MoveIt qua RobotCAD (cần WSL2) – chưa thử.
- `Part.ShapeFix` chi tiết – chưa thử.
- Báo lỗi `package.xml` của RobotCAD cho upstream.

## 10. Nguồn
- [S1] FreeCAD wiki – Part CheckGeometry: https://wiki.freecad.org/Part_CheckGeometry
- [S2] FreeCAD wiki – Release notes 1.1: https://wiki.freecad.org/Release_notes_1.1
- [S3] FreeCAD wiki – Part RefineShape: https://wiki.freecad.org/Part_RefineShape
- [S4] Mã nguồn FreeCAD tag 1.1.4 – `src/Mod/Mesh/Gui/DlgEvaluateMesh.ui`: https://github.com/FreeCAD/FreeCAD/blob/1.1.4/src/Mod/Mesh/Gui/DlgEvaluateMesh.ui
- [S5] FreeCAD wiki – Mesh Evaluation: https://wiki.freecad.org/Mesh_Evaluation
- [S6] FreeCAD wiki – Mesh FromPartShape: https://wiki.freecad.org/Mesh_FromPartShape
- [S7] FreeCAD wiki – Import Export Preferences (Mesh Formats): https://wiki.freecad.org/Import_Export_Preferences
- [S8] Bambu Lab wiki – STEP import trong Bambu Studio: https://wiki.bambulab.com/en/software/bambu-studio/step
- [S9] FreeCAD wiki – Assembly Workbench: https://wiki.freecad.org/Assembly_Workbench
- [S10] FreeCAD wiki – Assembly CreateSimulation: https://wiki.freecad.org/Assembly_CreateSimulation
- [S11] FreeCAD PR #16414 (Create Simulation): https://github.com/FreeCAD/FreeCAD/pull/16414
- [S12] FreeCAD wiki – FEM Preferences: https://wiki.freecad.org/FEM_Preferences
- [S13] FreeCAD wiki – Release notes 1.1, mục FEM (Netgen Python, CalculiX pipeline): https://wiki.freecad.org/Release_notes_1.1
- [S14] Bambu Lab – PLA Basic Technical Data Sheet V3.0: https://store.bblcdn.com/s1/default/58b85d0f3db94878854a28fdb8a0006e/Bambu_PLA_Basic_Technical_Data_Sheet.pdf
- [S15] Bambu Lab – PETG Basic Technical Data Sheet V3.0: https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf
- [S16] Bambu Lab – PETG HF Technical Data Sheet V1.0 (link từ trang sản phẩm us.store.bambulab.com/products/petg-hf): https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf
- [S17] Bambu Lab wiki – Overhang: https://wiki.bambulab.com/en/filament-acc/filament/print-quality/overhang
- [S18] FreeCAD wiki – Testing (Test Framework): https://wiki.freecad.org/Testing
- [S19] CalculiX 2.22 manual (G. Dhondt): http://www.dhondt.de/ccx_2.22.pdf – tham khảo phần tử/định dạng .inp; chưa trích dẫn nội dung cụ thể.
- Mã nguồn local (đã đọc): `C:/Program Files/FreeCAD 1.1/Mod/Assembly/{JointObject.py, CommandCreateSimulation.py, AssemblyTests/TestCore.py}`, `Mod/Fem/{ObjectsFem.py, femtools/ccxtools.py, femmesh/gmshtools.py, femsolver/settings.py, femexamples/ccx_cantilever_*.py}`, `Mod/Measure/MeasureCOM.py`; RobotCAD `community/drfenixion-freecad-robotcad/freecad/cross/{joint_proxy.py, wb_constants.py, freecad_utils.py, ui/command_calculate_mass_and_inertia.py, mcp/tools_registry.py}`.
- Script thử (nháp, tạm thời): thư mục scratchpad phiên 2026-10-21, `t1_geom_mesh.py` … `t9_path.py`, `tmod/test_stlab_drc.py`, kết quả `t*_result.json`.
