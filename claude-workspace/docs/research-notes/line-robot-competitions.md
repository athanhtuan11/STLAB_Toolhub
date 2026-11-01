# Cuộc thi robot dò line / tránh vật cản cho học sinh – tổng hợp 2026-11-01

> **Mục đích:** chọn chuẩn luật cho `maker/line-bot`. Dùng cho bước 0 (concept) và bước 1 (chốt linh kiện).
> **Ghi chú nguồn:**
> - **[Claude đã đọc PDF]** – Claude đọc trực tiếp file luật gốc.
> - **[Codex tra, chưa đối chiếu]** – Codex tra web, chưa đối chiếu với luật gốc. Trước khi dùng làm ràng buộc thiết kế phải đọc lại nguồn.

## 1. Tóm tắt

- Chuẩn chọn: **RoboCupJunior Rescue Line 2026** (dò line + giao lộ + vật cản + dốc). Lý do và đánh đổi: xem mục 5.
- Bản sau (THPT, 4 bánh lái, cảm biến/camera): **WRO Future Engineers 2026**.
- Chưa biết: lịch giải và thể lệ vòng khu vực tại Lâm Đồng (TODO).

## 2. Từng cuộc thi

### 2.1 ROBOTACON WRO 2026 (Việt Nam) – [Codex tra, chưa đối chiếu]

- Đơn vị tổ chức: Công ty Việt Tinh Anh cùng đơn vị địa phương.
- Bảng RoboMission: B1 tuổi 8–12, B2 tuổi 11–15, B3 tuổi 14–19 (theo thông báo của Sở KH&CN Gia Lai).
- Dùng bộ LEGO Education theo thể lệ → **xe tự chế không dùng được** ở bảng này.
- Chung kết toàn quốc mở rộng 8/2026. Mùa 2026–2027: chưa công bố (TODO).
- Nguồn: https://skhcn.gialai.gov.vn/Home/ChiTietTin/?tin=NjE1MA%3D%3D

### 2.2 Cuộc thi Sáng tạo Robotics toàn quốc 2026 (Trung ương Đoàn) – [Codex tra, chưa đối chiếu]

- Bảng: R1 (tiểu học), R2 (THCS), R3 (THPT), R4 (lớp 4–11).
- Lịch: vòng loại mô phỏng RoboSim ngày 28/6; vòng khu vực trực tiếp tháng 9; chung kết 23–25/10/2026.
- Nguồn PDF kế hoạch: https://tainangviet.vn/source/files/RBT2026_Kehoach_Thele.pdf
- TODO: đọc thể lệ vòng khu vực xem có cho xe tự chế và luật dò line không.

### 2.3 Hội thi Tin học trẻ 2026 – [Codex tra, chưa đối chiếu]

- Không thấy bảng robot dò line trên tinhoctre.vn.

### 2.4 WRO Future Engineers 2026 (Self-Driving Cars) – [Claude đã đọc PDF]

Nguồn: https://wro.hr/wp-content/uploads/2026/01/WRO-2026-Future-Engineers-Self-Driving-Cars-General-Rules.pdf

- Xe ≤ 300 × 200 mm, cao ≤ 300 mm; khối lượng ≤ 1,5 kg.
- Xe 4 bánh có cơ cấu lái.
- Sa bàn 3200 × 3200 mm; đường đua trong 3000 × 3000 mm.
- Tường cao 100 mm; vạch dày 20 mm.

Theo Codex – [Codex tra, chưa đối chiếu]:
- Tuổi 14–22.
- Mọi vi điều khiển, cảm biến, camera và chi tiết in 3D đều được phép.
- Không liên lạc không dây khi thi.
- Biển đỏ/xanh 50 × 50 × 100 mm.
- Mỗi lượt tối đa 3 phút.

### 2.5 RoboCupJunior Rescue Line 2026 – [Claude đã đọc PDF]

Nguồn: https://junior.robocup.org/wp-content/uploads/2026/02/RCJRescueLine2026-final.pdf (cập nhật 2026-03-29)

Sa bàn:
- Ô 30 × 30 cm, nền trắng; nhiều tầng nối bằng dốc.
- Line đen rộng 1–2 cm; cách mép/tường ≥ 10 cm.
- Dấu giao lộ xanh lá 25 × 25 mm. Không có dấu xanh → đi thẳng.
- Cửa ô ≥ 25 cm; trần thấp nhất 25 cm; bậc giữa ô ≤ 3 mm.

Điểm:

| Hạng mục | Điểm |
|---|---|
| Giao lộ / ngõ cụt | 10 |
| Dốc | 10 |
| Gờ giảm tốc | 10 |
| Bắt lại line sau đứt | 10 |
| Bập bênh | 20 |
| Mỗi vật cản (gạch, khối, vật nặng) | 20 |

- Robot kẹt được khởi động lại ở checkpoint.
- Khu sơ tán: vào bằng băng bạc phản quang, ra bằng băng đen. Nạn nhân là quả cầu Ø4–5 cm.
- Không dùng điện lưới; tối đa 48 V DC / 25 V AC RMS.

Lịch tuyển đội Việt Nam: TODO.

### 2.6 RobotChallenge Line Follower – [Codex tra, chưa đối chiếu]

- Line đen rộng 15 mm, nền trắng.
- Robot ≤ 300 × 300 mm, ≤ 3 kg.
- 3 lượt, lấy thời gian tốt nhất.
- Bản Enhanced có đứt line, vật cản và bập bênh.
- Nguồn: https://www.robotchallenge.org.cn/doc/en/RC-LineFollower.pdf

### 2.7 VEX IQ 2026–2027 (Level Up) và FLL

- Không phải cuộc thi dò line. VEX IQ 2026–2027 có nhiệm vụ nhặt túi đậu. [Codex tra, chưa đối chiếu]

## 3. Bảng so sánh

| Cuộc thi | Tuổi | Phần cứng tự chế? | Dò line | Vật cản |
|---|---|---|---|---|
| ROBOTACON WRO 2026 (RoboMission) | 8–19 (B1–B3) | Không – LEGO theo thể lệ [Codex] | TODO | TODO |
| Sáng tạo Robotics toàn quốc 2026 | R4 lớp 4–11; các bảng khác TODO | TODO | TODO | TODO |
| Tin học trẻ 2026 | – | – | Không thấy bảng [Codex] | Không thấy bảng [Codex] |
| WRO Future Engineers 2026 | 14–22 [Codex] | Có [Codex] | Không thấy line đen trong phần đã đọc (đường đua có tường 100 mm, vạch 20 mm) [Claude đọc PDF] | Biển đỏ/xanh [Codex] |
| **RCJ Rescue Line 2026** | TODO | Có (theo brief.md, luật mở phần cứng) | **Có** [Claude đọc PDF] | **Có** [Claude đọc PDF] |
| RobotChallenge Line Follower | TODO | TODO | Có, line đen 15 mm [Codex] | Chỉ bản Enhanced [Codex] |
| VEX IQ / FLL | – | – | Không | – |

## 4. Kết luận

- **STLab chọn chuẩn RCJ Rescue Line** cho `maker/line-bot`. Chi tiết ràng buộc (kích thước bao ≤ 180 × 180 × 150 mm) nằm ở `maker/line-bot/design/brief.md`.
- **WRO Future Engineers** cho bản sau (THPT), khi đội đủ kiến thức về cơ cấu lái và camera.
- Việc cần làm: hỏi Sở GD&ĐT và Tỉnh đoàn Lâm Đồng về lịch giải 2026–2027 (TODO).

## 5. Lý do chọn và đánh đổi

- RCJ Rescue Line có đủ hai yêu cầu chính: dò line và tránh vật cản. Luật mở phần cứng, sa bàn ô 30 × 30 cm làm được ở STLab.
- Đánh đổi: tuổi tham dự RCJ chưa rõ (TODO), và chưa biết có bảng nào ở Việt Nam dùng luật này. Nếu không có giải trong nước, line-bot vẫn dùng để dạy và làm bài chạy thử đo thời gian trên sa bàn tự làm.
- WRO FE cần cơ cấu lái 4 bánh, khác dạng xe vi sai của line-bot nên không chọn cho bản đầu.

## 6. TODO

- Đọc thể lệ vòng khu vực Robotics 2026 (có cho xe tự chế không).
- Lịch giải 2026–2027 cho học sinh Lâm Đồng (hỏi Sở GD&ĐT, Tỉnh đoàn).
- Lịch tuyển đội Việt Nam cho RCJ Rescue Line.
- Tuổi tham dự RCJ Rescue Line và RobotChallenge.
- Đối chiếu các mục đánh dấu [Codex tra, chưa đối chiếu] với PDF/website gốc.
