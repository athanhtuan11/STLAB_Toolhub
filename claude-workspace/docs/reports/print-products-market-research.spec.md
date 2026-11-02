---
task: print-products-market-research
cwd: .
allow: ["docs/reports/print-products-market-research.md"]
read: ["docs/reports/3d-print-cost-quote-oss.md", "docs/reports/community-for-repo-growth.md", "docs/reports/reverse-engineering-model-cong-dong.md", "maker/CLAUDE.md", "tools/model-study/fit-library", "docs/COMMUNITY.md"]
gate: 'python tools/delegate/check_report.py docs/reports/print-products-market-research.md "## 1. Boi canh STLab" "## 2. Nen tang cong dong" "## 3. Xu huong mau in" "## 4. Danh muc san pham" "## 5. Thi truong dia phuong" "## 6. Phap ly va an toan" "## 7. Quy trinh STLab" "## 8. De xuat xep loi/cong" --max-todo 12 --min-files 6'
ky_nang: [bao-cao]
timeout_min: 60
max_rounds: 3
executor: copilot
---

# Mục tiêu
Viết `docs/reports/print-products-market-research.md` (tiếng Việt có dấu, ≤ 320 dòng): nghiên cứu **tạo mẫu in 3D tự thiết kế
để (a) đăng cộng đồng (MakerWorld, Printables…) và (b) in bán tại địa phương** – xét **mọi dạng sản phẩm** (Tuan 2026-11-02).
Chỉ ĐỌC + tra web; **không vẽ, không cài, không sửa gì** – Tuan chọn rồi mới làm ("nghiên cứu trước, cải tiến sau").

# Bối cảnh bắt buộc
- STLab: trung tâm STEAM ở Đức Trọng, Lâm Đồng (gần Đà Lạt: du lịch, cà phê, hoa, rau, nông trại; sân bay Liên Khương).
  Khách: phụ huynh/học sinh lớp 3–12, quán cà phê, nông hộ, khách du lịch, trường học.
- Máy: **Bambu Lab A1** (bàn 256×256×256 mm), nhựa mặc định **Bambu PETG Basic**, bàn Textured PEI. Có AMS lite hay không: `TODO`
  → mẫu cần nhiều màu phải ghi cột "cần AMS". Không vẽ support trong STL (Tuan tô trong Bambu Studio).
- Thiết kế bằng FreeCAD script tham số + render Blender. Đã có tab báo giá `/quote` (markup 60 %, hỏng 15 %, giá sỉ ≥50 −10 %,
  ≥100 −15 %) – dùng để ước giá, không tự đặt giá bán.
- **Ranh giới đã chốt:** model người khác chỉ để học thông số (fit-library); mẫu đăng/bán = **thiết kế mới của STLab**.
  Không remix để đăng, không in bán model của người khác (Standard Digital File License của MakerWorld cấm thương mại).

# Mục bắt buộc (đúng tiêu đề)
- `## 1. Boi canh STLab`: 2 mục tiêu (điểm/uy tín cộng đồng + doanh thu địa phương) và chỗ chúng hỗ trợ nhau; ràng buộc máy/nhựa.
- `## 2. Nen tang cong dong`: MakerWorld (cơ chế điểm/Boost/quà đổi, Exclusive/Original, Print Profile, Maker Lab/parametric
  customizer, cách xếp hạng/Trending, luật đăng, các tùy chọn license khi đăng và license nào cho phép **chính mình** in bán),
  Printables (Prusameters/club), Thingiverse, Cults3D (bán file), Thangs. Bảng so sánh: thu nhập/điểm, lượng người dùng, công đăng.
- `## 3. Xu huong mau in`: nhóm mẫu đang được tải/boost nhiều 2025–2026 (print-in-place, articulated, Gridfinity/Multiboard,
  fidget, đèn, organizer, parametric…), đặc điểm trang mẫu thành công (ảnh, video, profile, hướng dẫn, nhiều biến thể). Có số
  liệu thì ghi nguồn; không có → mô tả định tính + `TODO`.
- `## 4. Danh muc san pham`: bảng **≥ 14 nhóm** phủ mọi dạng: gia dụng/organizer, đồ chơi + fidget, giáo dục STEAM (mô hình,
  kit lắp), quà lưu niệm Đà Lạt/Lâm Đồng, nông nghiệp (cà phê, hoa, tưới, nhãn cây, khay ươm), quán cà phê/cửa hàng (kệ menu,
  đế QR, bảng tên), phụ kiện điện thoại/máy tính/bàn học, xe máy/xe đạp, đèn + decor (lithophane, đèn ngủ), vỏ hộp điện tử
  (ESP32/smart home), phụ kiện CyberBrick/robot, phụ tùng thay thế, thú cưng, đồ dùng văn phòng/trường học, phụ kiện máy in 3D.
  Cột: ví dụ mẫu | hợp đăng cộng đồng (cao/vừa/thấp) | hợp bán địa phương | thời gian in + khối lượng ước (g) | độ khó thiết kế |
  PETG phù hợp? | rủi ro.
- `## 5. Thi truong dia phuong`: giá bán tham khảo đồ in 3D ở VN (Shopee, Facebook, TikTok Shop – có link), kênh bán ở Đức
  Trọng/Đà Lạt (fanpage, chợ, quán cà phê, shop lưu niệm, trường, nông trại, sự kiện Open Lab), đặt hàng theo yêu cầu (tên, logo).
- `## 6. Phap ly va an toan`: thương hiệu/nhân vật có bản quyền (không làm), an toàn đồ chơi trẻ em (chi tiết nhỏ, cạnh sắc),
  PETG tiếp xúc thực phẩm (thực tế bề mặt in, không khẳng định "food safe"), chịu nhiệt PETG ngoài trời/xe máy (có nguồn),
  quy định bán hàng online/hộ kinh doanh ở VN chỉ ghi ở mức tóm tắt có nguồn.
- `## 7. Quy trinh STLab`: ý tưởng → FreeCAD tham số → in thử A1 → ảnh/render → gói MakerWorld (3MF + profile A1 PETG, ảnh,
  mô tả EN + VI, tag) → Tuan tự bấm đăng → in bán + `/quote`. Việc nào Claude/agent làm được, việc nào Tuan làm.
- `## 8. De xuat xep loi/cong`: bảng **12–20 sản phẩm cụ thể** (không phải nhóm): sản phẩm | nhóm | lợi cộng đồng | lợi bán
  địa phương | công thiết kế (giờ) | cần AMS? | rủi ro | nguồn. Xếp giảm dần; đánh dấu **5 mẫu nên làm trước** (ưu tiên: một
  màu, không support, in < 3 h, có nét địa phương hoặc gắn STEAM, dễ làm biến thể tham số).

# Quy tắc
- Mỗi khẳng định về nền tảng/thị trường (cơ chế điểm, license, giá bán, số tải, giới hạn) phải có link nguồn gốc + ngày truy cập
  2026-11-02. Không chắc → `TODO`. **Không bịa** giá, số tải, quy định. Không chép mô tả/ảnh mẫu người khác.

# Tiêu chí PASS
Gate exit 0.
