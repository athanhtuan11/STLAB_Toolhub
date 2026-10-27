---
task: model-study-render
cwd: tools/model-study
allow: ["render.py", "study_3mf.py", "_out/**", "_out/*"]
gate: "python test_render.py && python test_study.py"
timeout_min: 20
max_rounds: 2
executor: auto
---

# Mục tiêu
Contact sheet của `study_3mf.py` vỡ hình với lưới nhiều tam giác (01, 06, 09, 13, 15, 21, 23): code đang lấy mẫu con
`tri[::step]` (bỏ tam giác → thủng) và `Poly3DCollection` của matplotlib vẽ sai thứ tự sâu.
Thay bằng render z-buffer tự viết bằng numpy.

# Yêu cầu
1. File mới `render.py`, hàm `render_iso(tri, size_px=360) -> np.ndarray` (H=W=size_px, 3 kênh, uint8):
   - `tri`: mảng (n,3,3) mm. Vẽ **mọi** tam giác, không lấy mẫu con.
   - Chiếu trực giao hướng iso (nhìn từ phía +X, -Y, +Z giống ảnh cũ: azim -60°, elev 30°), tự canh giữa và co
     sao cho hình chiếm ~85 % cạnh khung, giữ tỉ lệ trục bằng nhau.
   - Raster bằng z-buffer (numpy vector hoá theo khối tam giác, hoặc lặp theo tam giác có bbox pixel nhỏ – tùy, miễn
     lưới 170k tam giác render < 10 s). Tam giác nhỏ hơn 1 pixel vẫn phải tô ít nhất pixel chứa tâm của nó.
   - Đổ bóng theo pháp tuyến tam giác (tính từ đỉnh, lấy |n·l| để không phụ thuộc chiều pháp tuyến), màu xanh như cũ
     (0.30, 0.58, 0.78) × shade, shade trong [0.25, 1]. Nền trắng (255).
2. `study_3mf.py`: contact sheet dùng `render_iso` (mỗi ô `imshow` ảnh, tắt trục), giữ tiêu đề ô và bố cục lưới cũ.
   Các đầu ra khác (parts/, parts.csv, summary.md) giữ nguyên.
- Chỉ thư viện chuẩn + numpy + matplotlib. Không cài gói pip.

# Không làm
- Không sửa `test_render.py`, `test_study.py`, `test_holes.py`, `_sample/`.

# Tiêu chí PASS
`python test_render.py && python test_study.py` exit 0.
