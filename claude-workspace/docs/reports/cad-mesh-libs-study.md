# Nghiên cứu thư viện đọc mesh/CAD và kiểm tra in 3D cho STLab

Phạm vi: đọc mã nguồn đã clone, không cài và không chạy repo. Các đường dẫn dưới đây tính tương đối từ `claude-workspace`. Các đề xuất là hướng tích hợp; cần giữ ngưỡng hiện có theo cấu hình STLab.

## 1. trimesh

- API tổng quát là `trimesh.load(...)`; `trimesh.load_mesh(...)` ép kết quả về `Trimesh`, còn `trimesh.load_scene(...)` giữ scene và nhiều node. Bộ nạp chọn importer theo định dạng trong `community/mikedh-trimesh/trimesh/exchange/load.py`; STL ASCII/binary ở `trimesh/exchange/stl.py`.
- 3MF đi qua importer 3MF của exchange; dữ liệu có thể được giữ thành scene, nhưng repo không chứng minh đọc được metadata nhiều plate riêng của Bambu. Không đồng nhất khả năng nạp mesh 3MF với việc hiểu plate, project setting hoặc tên object của Bambu. Importer 3MF có tại `community/mikedh-trimesh/trimesh/exchange/threemf.py` (Claude kiểm lại 2026-10-27; bản nháp ghi nhầm "không thấy").
- Kiểm tra kín: `Trimesh.is_watertight` kiểm tra mỗi cạnh thuộc đúng hai mặt; `is_volume` bổ sung hướng mặt/điều kiện volume. Thể tích có ở `Trimesh.volume` và `trimesh/triangles.py` (`mass_properties`). Section giao mặt phẳng nằm ở `Trimesh.section(...)` trong `trimesh/base.py`.
- Tìm mặt phẳng/trụ là bài toán fit primitive chứ không phải API B-rep chính xác: `trimesh/geometry.py` có fit/đoạn hình học; cần xác minh thuật toán trụ cụ thể trước khi dựa vào tên API (TODO). Ray có `mesh.ray.intersects_location`, `intersects_id`, `intersects_first` trong `trimesh/ray/ray_triangle.py`; Embree là backend tùy chọn ở `ray/ray_pyembree.py`.
- Phụ thuộc nền bắt buộc: NumPy (thể hiện import ở mã lõi/package metadata). Backend gia tốc ray Embree/embreex và `rtree`/spatial index là tùy chọn; feature phụ thuộc tùy chọn khác không cần lắp cả bộ cho STL/3MF cơ bản. Xem `community/mikedh-trimesh/pyproject.toml` và `trimesh/ray/`.
- So với STLab: `tools/model-study/study_3mf.py` đã tự đọc binary/ASCII STL, component 3MF, transform, tên, plate, thể tích và edge closure. `tools/model-study/measure_holes.py` tự cắt lát theo trục và fit vòng tròn qua nhiều lát; chưa có ray hay primitive B-rep. Đưa trimesh vào chỉ có lợi nếu giảm mã tự duy trì; cần thử tải 3MF plate thực tế trước khi thay parser.

## 2. CadQuery va build123d

- CadQuery đọc STEP bằng `cq.importers.importStep(path)`; importer tạo `Workplane` từ shape trong `community/cadquery-cadquery/cadquery/occ_impl/importers/`. Duyệt mặt bằng `shape.Faces()`; `Face.geomType()` phân loại `CYLINDER`; `Face._geomAdaptor()`/các phương thức mặt trả về surface/geometry OCCT. Xem `cadquery/occ_impl/shapes.py`.
- build123d có `import_step(path)` trong `community/gumyr-build123d/src/build123d/importers.py`; `Shape.faces()` trả danh sách `Face`. `Face.geom_type` phân biệt mặt trụ; API/topology dùng `BRepAdaptor_Surface`/`Geom_CylindricalSurface` OCP để đọc cylinder. Với mặt trụ, surface OCCT có `Cylinder().Radius()`, `Axis()` và `Location()` (trục và điểm gốc/tâm định nghĩa surface). Xem `src/build123d/topology/two_d.py`, `topology/shape_core.py` và importer.
- Hai dự án bọc OCCT: CadQuery dùng OCP/CadQuery OCP, build123d import trực tiếp `OCP.*`. FreeCAD cũng dùng OCCT làm hình học lõi: bằng chứng mã nguồn trong checkout này là `tools/cad-delegation/gate.py` import `Part`/`FreeCAD` và thaoует `Part` shape (nền CAD của FreeCAD); tài liệu/code dự án không chứng minh API tương thích với CadQuery, nên không suy luận tên API FreeCAD tương ứng. (không suy ra API FreeCAD từ các wrapper này.)
- Đây là hướng tốt cho STEP vì còn mặt trụ chính xác thay vì lưới tam giác. Cần trích xuất surface adaptor và chuyển tọa độ sau transform một cách có chủ đích; không áp dụng cho STL vốn chỉ còn tam giác.

## 3. Multi-Agent-CAD

- Repo có luồng đơn chi tiết và luồng thử nghiệm assembly. Trong luồng đơn, node/agent phân vai tạo brief/kế hoạch hình học, sinh CAD (cadpy/build123d), thực thi xuất hình, kiểm tra hình học/ảnh, Judge độc lập và repair khi lỗi. Vòng lặp có giới hạn; kết quả vẫn cần người xác nhận trước sản xuất. Xem `community/pan-chera-multi-agent-cad/multi_agent_cad/nodes.py`, `graph.py`, `schemas.py`, `README.md`.
- Với assembly, có phân rã chi tiết, kế hoạch mating/joint, sinh từng part, lắp, QA và repair; tài liệu gọi đây là technology preview và yêu cầu kiểm tra joints/geometry. Xem `community/pan-chera-multi-agent-cad/mac_assembly/README.md` và `mac_assembly/`.
- README liệt kê cấu hình theo stage/provider; mặc định DashScope OpenAI-compatible, có lựa chọn provider/model khác. Không suy ra một model duy nhất cho mọi agent; cấu hình thực tế được nạp từ `multi_agent_cad/config.py` và hướng dẫn provider trong README.
- STLab `tools/delegate/delegate.py` giao một spec cho executor Codex/OpenCode/agy, khóa theo cwd, giới hạn lượt và chạy gate; nó là điều phối executor theo hợp約, không tự chia vai hình học hay tự repair CAD. `tools/cad-delegation/gate.py` chạy kiểm tra tất định theo spec (solid hợp lệ, bbox, vùng rỗng/đặc, khe, chuyển động và in nếu khai báo); không có Judge thị giác/LLM. Có thể học cách tách stage và lưu kết quả, nhưng gate spec hiện có là nguồn xác nhận.

## 4. OrcaSlicer 3MF

- `community/orcaslicer-orcaslicer/src/libslic3r/Format/3mf.cpp` là luồng 3MF tiêu chuẩn; `bbs_3mf.cpp` bổ sung định dạng dự án Bambu. Mã xử lý resource object, component tham chiếu object/path, transform, build item, tên và metadata trong `model_settings.config`; đọc plate/project metadata và mapping instance/object với plate. Có lưu/đọc cut information và cấu hình in theo object/volume trong các hàm Bambu. Tên chi tiết của từng key khác nhau giữa nhánh chuẩn và Bambu; kiểm tra các hàm parse/serialize tương ứng trong hai file trước khi dựa vào key cụ thể.
- STLab `tools/model-study/study_3mf.py` đã đọc `3D/3dmodel.model`, mesh vertices/triangles, component lồng và transform, tên từ `Metadata/model_settings.config`, `Metadata/plate_N.json` và mapping `plater_id`/`object_id`; trả mesh build item, plate, bounding box, thể tích và watertight thô.
- Những phần chưa thấy trong script STLab: cut information/đối tượng cắt; cấu hình in riêng theo object hoặc volume và process/filament setting; metadata đầy đủ ngoài key name; quan hệ instance/component và transform sau khi ghép không xuất báo cáo chi tiết; màu/texture/material và thông tin dự án khác. Script chỉ xuất tên, plate, mesh và số đo cơ bản, không tái dựng project Orca/Bambu để tiếp tục slicing.
- Nên giữ parser đọc an toàn, chỉ bổ sung trường có nhu cầu rõ ràng và fixture 3MF đại diện. Tên trường/định nghĩa thuộc implementation Orca; không coi mọi 3MF đều có các phần mở rộng đó.

## 5. OrcaSlicer support

- Phân tích support thực hiện trên layer sau slicing: vùng overhang lấy từ hình học layer và quan hệ với layer dưới; sau đó áp khoảng cách XY, interface, kiểu support và lọc vùng nhỏ. Mã chính nằm ở `community/orcaslicer-orcaslicer/src/libslic3r/Support/SupportMaterial.cpp` và `SupportCommon.cpp`; tham số cấu hình/đối tượng ở `SupportParameters.hpp` và khai báo option trong `community/orcaslicer-orcaslicer/src/libslic3r/Support/SupportParameters.hpp`.
- Góc overhang trong Orca là option `support_threshold_angle` (kiểm tra tên/ý nghĩa tại PrintConfig; ngưỡng có thể thay theo cấu hình vật liệu/độ dốc). Bridge được nhận diện theo đường đùn và chiều dài/điều kiện span; có xử lý bridge và vùng bridge không đồng nghĩa một ngưỡng toàn cục duy nhất. Các island là polygon đảo trên từng layer; vùng nhỏ có lọc theo diện tích/chiều dài trong pipeline support. Ngưỡng định lượng bridge/island phụ thuộc option và code path; chưa thấy đủ căn cứ để gán một giá trị chung.
- STLab `tools/robotics-cad/scripts/printability.py` phân loại tam giác STL theo pháp tuyến/góc `overhang_deg` trừ `overhang_tol_deg`; loại phần sát bàn, phần có vật đỡ dưới trong `support_gap_max_mm`, gom connected components, bỏ bridge ngắn theo `bridge_max_mm`/`bridge_closed_max_mm`, vùng nhỏ theo `support_min_patch_mm2`/`min_patch_height_mm`, phát hiện mái lỗ kín và vùng cần brim. Đây là xấp xỉ mesh trước slicing; Orca đánh giá theo layer, profile máy/vật liệu và support config. Vì vậy dùng Orca để hiểu tiêu chí/đối chiếu, không bê ngưỡng của slicer thành thông số an toàn chung.

## 6. Ap dung cho STLab

| Đề xuất cụ thể | Nguồn để xem | Công sức | Rủi ro giấy phép |
|---|---|---|---|
| Thêm kiểm tra STL bằng mesh `is_watertight` và volume có hướng như bước chẩn đoán phụ; giữ output hiện tại để đối chiếu. | `community/mikedh-trimesh/trimesh/base.py`, `community/mikedh-trimesh/trimesh/repair.py`, `tools/model-study/study_3mf.py` | Nhỏ | Kiểm tra license trước khi thêm dependency; không sao chép mã. |
| Bổ sung tùy chọn xuất section 2D cho vị trí người dùng chọn để xem lỗ/biên mesh; không tự đặt bước lát mới. | `community/mikedh-trimesh/trimesh/base.py`, `community/mikedh-trimesh/trimesh/intersections.py`, `tools/model-study/measure_holes.py` | Vừa | Tích hợp dependency; không chép mã nguồn. |
| Ưu tiên đo trụ STEP bằng CadQuery/build123d/OCP trong FreeCAD Python chỉ sau kiểm chứng tương thích môi trường STLab; lấy radius/axis/location từ surface. | `community/cadquery-cadquery/cadquery/occ_impl/shapes.py`, `community/cadquery-cadquery/cadquery/occ_impl/importers/__init__.py`, `community/gumyr-build123d/src/build123d/topology/two_d.py` | Vừa | Xác minh license dependency; dùng API, không chép implementation. |
| Báo cáo rõ giới hạn plate/cut/object settings của parser hiện tại và thêm các trường cần dùng vào CSV/JSON theo fixture. | `tools/model-study/study_3mf.py`, `community/orcaslicer-orcaslicer/src/libslic3r/Format/bbs_3mf.cpp` | Vừa | OrcaSlicer AGPL-3.0: chỉ học ý tưởng, không chép mã. |
| Tạo bộ đối chiếu kết quả support theo các file STL đã có, ghi profile/nguồn ngưỡng cùng kết quả để tránh coi heuristic là cam kết in được. | `tools/robotics-cad/scripts/printability.py`, `community/orcaslicer-orcaslicer/src/libslic3r/Support/SupportMaterial.cpp` | Vừa | OrcaSlicer AGPL-3.0: chỉ học ý tưởng, không chép mã. |
| Bổ sung tóm tắt từng check và nguyên nhân fail của gate vào báo cáo delegate, giữ nguyên gate hình học tất định. | `tools/delegate/delegate.py`, `tools/cad-delegation/gate.py` | Nhỏ | Kiểm tra giấy phép hiện có trước chia sẻ; không sao chép mã Orca. |
| Trên máy Windows yếu, giữ đọc STL/3MF dạng streaming/NumPy và chạy tùy chọn nặng theo yêu cầu; đo thời gian/bộ nhớ trên máy thật trước khi bật mặc định. | `tools/model-study/study_3mf.py`, `tools/model-study/measure_holes.py` | Vừa | Không phát sinh rủi ro Orca nếu không dùng mã của Orca. |
| Trước thêm dependency, xác minh tương thích Python 3.13/FreeCAD 1.1 và giấy phép của phiên bản dự kiến; chưa có bằng chứng tương thích thì ghi TODO. | `community/mikedh-trimesh/pyproject.toml`, `tools/cad-delegation/gate.py` | Nhỏ | Trimesh/CadQuery/build123d mỗi dự án có license riêng; cần đọc license của đúng revision. |

Giới hạn: không chạy thử các repo, không suy ra tương thích nhị phân với Python 3.13/FreeCAD 1.1, cũng không khuyến nghị thông số in/safety mới. Các nội dung chưa tìm thấy bằng chứng cần được xác minh trước khi triển khai.

## 7. Kết luận của Claude (tổng giám đốc) – chờ Tuan duyệt

**Đã thử thật 2026-10-27:** FreeCAD 1.1 (`freecadcmd`, cùng nền OCCT với CadQuery/build123d) đọc STEP mẫu và lấy mặt
trụ bằng `Part.read()` → `face.Surface` là `Part.Cylinder` → `Radius`, `Axis`, `Center`; phân biệt lỗ/chốt bằng hướng
pháp tuyến so với trục. Kết quả: lỗ **Ø3,200** trục Z, chốt **Ø3,000** trục X – đúng số dựng. → **Không cần cài
CadQuery/build123d**; chỉ học cách duyệt mặt từ `community/gumyr-build123d/src/build123d/topology/two_d.py`.

Đề xuất (theo thứ tự giá trị):
1. **`measure_step.py` (freecadcmd):** khi model cộng đồng có STEP → đo lỗ/chốt CHÍNH XÁC từ mặt trụ (thay cắt lát lưới,
   sai số ~0,05–0,1 mm của `measure_holes.py`); STL vẫn dùng cách cũ. Nhỏ–vừa. Giao Codex/OpenCode, gate = chi tiết mẫu
   biết trước số đo.
2. **`study_3mf.py` đọc thêm** cấu hình in theo object (support, infill, tường) + cut info trong `model_settings.config`
   → biết tác giả in chi tiết nào cần support, để so với `printability.py`. Vừa. Chỉ học cấu trúc từ OrcaSlicer (AGPL),
   không chép mã.
3. **Đối chiếu `printability.py` với tiêu chí Orca** (đánh giá theo lớp sau slicing, `support_threshold_angle`) – dùng
   chính file 3MF cộng đồng có support tác giả đã tô làm "đáp án". Vừa.
4. **trimesh: chưa dùng.** Công cụ tự viết đang đủ; chỉ cân nhắc khi cần ray/boolean (thêm phụ thuộc pip).
5. **Multi-Agent-CAD: học ý** tách stage (brief → sinh CAD → kiểm hình học → Judge → sửa) cho `tools/cad-delegation`;
   không cài (dùng DashScope/API trả phí). Giữ gate tất định làm nguồn xác nhận, Judge bằng ảnh chỉ là phụ.

