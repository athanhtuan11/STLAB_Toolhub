# Nghiên cứu công cụ reverse engineering model in 3D (cộng đồng)

Ngày: 2026-10-30. Phạm vi: công cụ đọc model đã thành phẩm (STL/3MF/STEP) để rút thông số chi tiết như lỗ, chốt, khe lắp, boss, ổ servo và ổ bi.

Nguồn tra: Codex (ask-gpt) tra web; Claude kiểm số sao và ngày cập nhật qua GitHub API ngày 2026-10-30. Số liệu chỉ lấy từ hai nguồn này. Chỗ chưa kiểm được ghi `TODO`.

## 1. Mục tiêu

Tuan: "AI lên ý tưởng thì chi tiết chỉn chu, không sai lệch."

Cụ thể: từ model cộng đồng đã in được, rút ra lỗ, chốt, khe lắp, boss, ổ servo và ổ bi, rồi lưu thành kho dữ liệu. AI thiết kế tra kho trước khi đặt kích thước, thay vì tự đoán.

## 2. Kết luận

- Chưa có công cụ cộng đồng chuẩn, tự động hoàn toàn: đưa model vào và nhận đúng danh sách chi tiết có dung sai.
- Hướng khả thi: ghép thư viện đo hình học (trimesh và pyRANSAC-3D cho mesh; OCCT qua FreeCAD cho STEP) với kho dung sai riêng của STLab.
- Dung sai FDM phụ thuộc máy, nhựa và hướng in, nên kho dung sai phải do STLab tự đo.

## 3. Bảng nguồn

| Tên | Link | Làm gì | Sao | Cập nhật | License | Đánh giá |
|---|---|---|---|---|---|---|
| trimesh | https://github.com/mikedh/trimesh | Đọc STL/3MF, cắt lát, lấy mẫu | 3714 | 2026-10-29 | MIT | Dùng |
| pyRANSAC-3D | https://github.com/leomariga/pyRANSAC-3D | Khớp phẳng/trụ/nón/cầu, trục bất kỳ | 671 | 2026-08-28 | Apache-2.0 | Dùng |
| Open3D | https://github.com/isl-org/Open3D | Xử lý point cloud/mesh | 14146 | 2026-09-30 | API: NOASSERTION; README: MIT (`TODO` kiểm) | Mạnh nhưng nặng |
| pythonOCC | https://github.com/tpaviot/pythonocc-core | Mặt giải tích từ STEP | 1990 | 2026-10-18 | LGPL-3.0 | STLab đã có `measure_step.py` cùng hướng; không có sẵn hàm nhận dạng lỗ (issue #1411) |
| Detessellate | https://github.com/DesignWeaver3D/Detessellate | Macro FreeCAD dựng sketch/khối từ mesh | 102 | 2026-09-12 | LGPL-2.1 | Hỗ trợ dựng tay |
| MeshToFeatures | https://github.com/MasoudMiM/MeshToFeatures | Mesh thành cây PartDesign, chỉ chi tiết prismatic | 21 | 2026-10-30 | LGPL-2.1 | Thử |
| Quiddity | https://github.com/pzfreo/quiddity | STEP thành lỗ, lỗ bậc, boss, rãnh, bo góc | 11 | 2026-10-15 | Apache-2.0 | Thử |
| CAD-Recode | https://github.com/filaPro/cad-recode | AI từ điểm sang CadQuery | 276 | 2025-11-16 | NOASSERTION | Loại: cần GPU, máy yếu |
| Point2CAD | https://github.com/prs-eth/point2cad | Nhận dạng primitive từ point cloud | 464 | 2024-09-24 | API: Apache-2.0; Codex nói CC-BY-NC (`TODO` kiểm) | Loại: không còn cập nhật |
| CGAL | https://github.com/CGAL/cgal | Shape Detection | 6096 | 2026-10-29 | Theo dự án (`TODO` kiểm) | Loại: mạnh nhưng C++, khó tích hợp |
| ComplexGen | https://github.com/guohaoxiang/complexgen | Nghiên cứu CAD từ point cloud | 132 | 2026-01-17 | MIT | Loại: nghiên cứu, chạy trên Linux |

Ghi chú về license: STLab làm dự án phi thương mại, nên license không chặn việc dùng. Các license cần xem lại khi có thương mại được ghi riêng ở chính sách license của STLab.

## 4. Lưu ý

- Workbench Reverse Engineering có sẵn của FreeCAD gần như không có chức năng. Tài liệu FreeCAD ghi nhóm này ở trạng thái sandbox. Không dùng làm nền cho kho dữ liệu.
- Không có bộ dữ liệu dung sai FDM chuẩn của cộng đồng. Chỉ có hai nguồn tham khảo:
  - Mẫu in thử dung sai: https://www.printables.com/model/116911-clearance-tolerance-test
  - Bộ đo nhỏ: https://fitcheck.bakedbean3d.com/data/
- Cả hai đều phụ thuộc máy, nhựa và hướng in. Không lấy số của chúng làm thông số chung cho STLab.

## 5. Hiện trạng STLab

- `tools/model-study/study_3mf.py`: đọc STL/3MF, tên, plate, bounding box, thể tích và watertight thô.
- `tools/model-study/measure_holes.py`: đo lỗ theo trục x/y/z. Chưa đo được trục bất kỳ.
- `tools/model-study/measure_step.py`: đo chính xác từ STEP (mặt trụ).

## 6. Lộ trình (Tuan duyệt 2026-10-30)

Thứ tự thực hiện; số trong ngoặc là nhãn trong đề xuất gốc:

1. (Mục 1) Nâng cấp đo STL bằng trimesh + pyRANSAC-3D: đo trục bất kỳ, ghi sai số, phân loại lỗ xuyên, lỗ bậc, boss, ổ servo và ổ bi.
2. (Mục 2) Kho fit-library dạng JSON. AI thiết kế bắt buộc tra kho trước khi đặt kích thước lắp ghép.
3. (Mục 5) Skill model-study.
4. (Mục 4) Thử MeshToFeatures và Quiddity trên tay máy tipflow.
5. (Mục 3) In mẫu dung sai A1 + PETG và đo thật.

## 7. TODO

- Kiểm license Open3D (API NOASSERTION, README MIT).
- Kiểm license Point2CAD (API Apache-2.0; Codex nói CC-BY-NC).
- Kiểm license CGAL theo đúng revision dùng.
- Kiểm lại số sao và ngày cập nhật trước khi chốt tài liệu chia sẻ ra ngoài.
