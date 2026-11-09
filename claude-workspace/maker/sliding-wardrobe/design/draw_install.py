"""Hinh giai thich cach gan ray tren + ray duoi (theo phu kien dinh mua: con lan 608 O32, ray U O21).

Chay: python draw_install.py  -> renders/14-cach-gan-ray.png
So lieu phu kien la gia dinh theo link da tra, TODO do hang that.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
STEEL, LAM, ALU, NYL, WALL = "#2B2D30", "#8B6A4F", "#B9BEC3", "#F2F2EE", "#ddd"
LANE = (30, 78)          # tam 2 lan ray (mm tu mat truoc)
FDP = 40                 # day canh
ROLL_D, ROLL_W = 32, 12  # con lan 608 boc POM 8x32x12 (TODO do that)
CH = ROLL_D + 3          # long mang = O + 3 (tu han)
LA_T, LA_H = 3, 40       # sat la 3x40 lam thanh mang
RAIL_D = 21              # ray U O21 (TODO hinh dang that)
WHEEL_D, WHEEL_W = 48, 22


def door(ax, yc, z0, z1, alpha=1.0):
    y0 = yc - FDP / 2
    ax.add_patch(Rectangle((y0, z0), FDP, z1 - z0, fc=LAM, ec="k", lw=0.6, alpha=alpha))


fig = plt.figure(figsize=(18, 10))
a1 = fig.add_axes([0.00, 0.08, 0.30, 0.84])
a2 = fig.add_axes([0.33, 0.08, 0.30, 0.84])
a3 = fig.add_axes([0.66, 0.08, 0.34, 0.84])

# ---------------- 1. ray tren
hz = 200
a1.add_patch(Rectangle((-15, hz), 130, 80, fc=STEEL, ec="k"))
a1.text(50, hz + 40, "dầm đầu cửa hộp 40×80\n(đã hàn vào khung, 2 đầu bắt tường)", color="w", ha="center", va="center",
        fontsize=8)
for yc in LANE:
    for s in (-1, 1):
        yw = yc + s * CH / 2 + (0 if s > 0 else -LA_T)
        a1.add_patch(Rectangle((yw, hz - LA_H), LA_T, LA_H, fc=STEEL, ec="k", lw=0.6))
    a1.add_patch(Rectangle((yc - ROLL_D / 2, hz - 30), ROLL_D, ROLL_W, fc=NYL, ec="k"))
    a1.plot([yc, yc], [hz - 45, hz - 18], c="k", lw=1.5)
    door(a1, yc, hz - 160, hz - 45)
a1.annotate("sắt la 3×40 hàn dọc dưới dầm\n(4 thanh = 2 máng)", (LANE[0] - CH / 2 - 2, hz - 20),
            (-70, hz - 110), fontsize=8, arrowprops=dict(arrowstyle="->"))
a1.annotate(f"con lăn 608 Ø{ROLL_D}\nbắt bu lông M8 lên đầu cánh", (LANE[1], hz - 24), (115, hz - 100), fontsize=8,
            arrowprops=dict(arrowstyle="->"))
a1.annotate("", (LANE[0] - CH / 2, hz + 95), (LANE[0] + CH / 2, hz + 95), arrowprops=dict(arrowstyle="<->"))
a1.text(LANE[0], hz + 102, f"lòng {CH}", ha="center", fontsize=8)
a1.text(50, hz - 200,
        "CÁCH LÀM\n"
        "1. Cắt 4 thanh la dài bằng dầm (≈3 m).\n"
        f"2. Kẹp 2 cữ gỗ dày {CH} vào giữa từng cặp la\n"
        "   (cữ chạy dọc, đặt cách nhau ~0,5 m).\n"
        "3. Hàn đính la vào mặt dưới dầm mỗi 150–200,\n"
        "   rút cữ, mài, sơn đen.\n"
        "→ 2 máng chữ U úp ngược, miệng hướng xuống.",
        ha="center", va="top", fontsize=9)
a1.set_xlim(-110, 200); a1.set_ylim(-160, hz + 130); a1.set_aspect("equal"); a1.axis("off")
a1.set_title("(1) RAY TRÊN – máng dẫn hướng (cắt ngang)", fontsize=12)

# ---------------- 2. ray duoi
a2.add_patch(Rectangle((-30, -25), 170, 25, fc=WALL, hatch="//", ec="#999"))
for yc in LANE:
    a2.add_patch(Rectangle((yc - 20, 0), 40, 4, fc=ALU, ec="k", lw=0.6))           # de/tai ray
    a2.add_patch(Rectangle((yc - 3, 4), 6, 10, fc=ALU, ec="k", lw=0.6))
    a2.add_patch(Circle((yc, 4 + 10 + RAIL_D / 2 - 4), RAIL_D / 2, fc=ALU, ec="k"))
    zr = 4 + 10 + RAIL_D - 4
    zb = zr - 6                                   # day ranh banh om dinh ray
    a2.add_patch(Rectangle((yc - WHEEL_W / 2, zb), WHEEL_W, WHEEL_D, fc=NYL, ec="k"))   # cat ngang: banh day 22
    a2.add_patch(Rectangle((yc - 4, zb + WHEEL_D / 2 - 4), 8, 8, fc="#888"))            # truc
    door(a2, yc, zb + WHEEL_D - 18, zb + WHEEL_D + 100, alpha=0.9)
    a2.plot([yc - 12, yc - 12], [0, -18], c="k", lw=2)
    a2.plot([yc + 12, yc + 12], [0, -18], c="k", lw=2)
a2.annotate("ray U Ø21 (đỉnh tròn)\nrãnh U của bánh ôm lên", (LANE[0], 30), (-25, 120), fontsize=8,
            arrowprops=dict(arrowstyle="->"))
a2.annotate("tai/đế ray: vít + tắc kê\nxuống sàn mỗi 400–500", (LANE[1] + 12, -10), (95, -70), fontsize=8,
            arrowprops=dict(arrowstyle="->"))
a2.annotate(f"bánh BX48PU Ø{WHEEL_D}\nhàn mặt sau viền dưới cánh", (LANE[1] + 11, 50), (110, 110), fontsize=8,
            arrowprops=dict(arrowstyle="->"))
a2.text(55, -110,
        "CÁCH LÀM\n"
        "1. Ray không có lỗ đế: hàn tai sắt la\n"
        "   3×30 dài 40 vào chân ray mỗi 400–500,\n"
        "   khoan lỗ Ø6 ở tai.\n"
        "2. Đặt ray đúng đường mực (bước (3)),\n"
        "   khoan sàn qua lỗ tai, bắt vít + tắc kê.\n"
        "3. 2 ray song song, cách tâm 48.",
        ha="center", va="top", fontsize=9)
a2.set_xlim(-60, 190); a2.set_ylim(-260, 170); a2.set_aspect("equal"); a2.axis("off")
a2.set_title("(2) RAY DƯỚI – ray U chịu tải (cắt ngang)", fontsize=12)

# ---------------- 3. canh thang: day doi
H = 1000
a3.add_patch(Rectangle((-20, H), 140, 40, fc=STEEL))
a3.add_patch(Rectangle((-40, -30), 200, 30, fc=WALL, hatch="//", ec="#999"))
for yc, c in zip(LANE, ("#C0392B", "#1F6FB2")):
    a3.plot([yc, yc], [H, 15], ls="--", c=c, lw=1.4)
    a3.add_patch(Circle((yc, 22), 6, fc=c))
    a3.add_patch(Rectangle((yc - 4, H - 40), 8, 40, fc="none", ec=c, lw=1.5))
a3.text(LANE[0] - 10, H / 2, "dây dọi\nmáng ngoài", ha="right", fontsize=9, color="#C0392B")
a3.text(LANE[1] + 10, H / 2, "dây dọi\nmáng trong", ha="left", fontsize=9, color="#1F6FB2")
a3.text(55, -60,
        "(3) DÓNG RAY DƯỚI THEO RAY TRÊN\n"
        "1. Làm ray trên ((1)) trước, cố định xong.\n"
        "2. Ở 2 đầu + giữa: thả dây dọi (hoặc laser)\n"
        "   từ TÂM mỗi máng xuống sàn → chấm mực.\n"
        "3. Búng dây mực nối các chấm → 2 đường.\n"
        "4. Đặt ray dưới lên đường mực rồi bắt vít ((2)).\n"
        "   Lệch ≤ 2 → cánh đứng thẳng, lùa nhẹ.\n"
        "5. Treo cánh: nâng 25 → con lăn vào máng →\n"
        "   đặt bánh lên ray → hạ xuống.",
        ha="center", va="top", fontsize=9)
a3.set_xlim(-170, 280); a3.set_ylim(-420, H + 80); a3.set_aspect("equal"); a3.axis("off")
a3.set_title("(3) Ray dưới phải THẲNG ĐỨNG dưới ray trên", fontsize=12)

fig.suptitle("CÁCH GẮN RAY TRÊN + RAY DƯỚI (mm) – số phụ kiện theo hàng định mua, đo lại khi có hàng", fontsize=13)
fig.savefig(os.path.join(OUT, "14-cach-gan-ray.png"), dpi=100, bbox_inches="tight")
print("OK")
