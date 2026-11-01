"""Anh concept buoc 0 cho line-bot: 3 huong A/B/C x 3 goc nhin -> design/concepts/*.png + design/contact-sheet.png.

Khoi minh hoa (KHONG phai CAD): chi Mega 2560 dung kich thuoc do tu STEP (108,8 x 53,16 x 14,81 mm, hop bao gom
USB/jack); cac linh kien khac la khoi uoc luong de nhin ty le – kich thuoc that chot o buoc 1 (TODO trong brief).
Bao ngoai muc tieu: <= 180 x 180 x 150 mm (brief). Chay: python make_concepts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "concepts"
BG, INK, MUTED = "#15181c", "#e8e6e1", "#8a8f96"
C = {"khung": "#3a8fd9", "vo": "#e2702b", "mega": "#1f7a5a", "pin": "#c9b13a", "motor": "#9aa3ad",
     "banh": "#2b2b2b", "cam": "#c14953", "line": "#7d5fd3"}


def hop(ax, x, y, z, dx, dy, dz, mau, alpha=1.0):
    """Khoi hop goc (x, y, z) kich thuoc (dx, dy, dz) mm."""
    p = np.array([[x, y, z], [x + dx, y, z], [x + dx, y + dy, z], [x, y + dy, z],
                  [x, y, z + dz], [x + dx, y, z + dz], [x + dx, y + dy, z + dz], [x, y + dy, z + dz]])
    mat = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 3, 7, 4]]
    ax.add_collection3d(Poly3DCollection([p[m] for m in mat], facecolor=mau, edgecolor="#0b0d10",
                                         linewidths=0.4, alpha=alpha))


def tru(ax, cx, cy, cz, r, w, mau, truc="y", n=28):
    """Banh xe / tru tron quanh truc y."""
    t = np.linspace(0, 2 * np.pi, n)
    a, b = r * np.cos(t), r * np.sin(t)
    if truc == "y":
        p0 = np.c_[cx + a, np.full(n, cy), cz + b]
        p1 = np.c_[cx + a, np.full(n, cy + w), cz + b]
    else:
        p0 = np.c_[cx + a, cy + b, np.full(n, cz)]
        p1 = np.c_[cx + a, cy + b, np.full(n, cz + w)]
    mats = [[p0[i], p0[(i + 1) % n], p1[(i + 1) % n], p1[i]] for i in range(n)] + [list(p0), list(p1)]
    ax.add_collection3d(Poly3DCollection(mats, facecolor=mau, edgecolor="none"))


def chung(ax):
    """Linh kien chung 3 huong: 2 banh + motor N20, bi do, pin 2S, mang do line, HC-SR04. Truc x = huong chay."""
    for y0 in (-82, 70):                              # banh ~ O60 x 12 (uoc luong)
        tru(ax, -20, y0, 30, 30, 12, C["banh"])
    for y0 in (-70, 40):                              # N20 ~ 12 x 10 x 30 (than + hop so, uoc luong)
        hop(ax, -26, y0, 25, 12, 30, 10, C["motor"])
    hop(ax, 60, -6, 2, 12, 12, 10, C["motor"])        # bi do phia truoc
    hop(ax, -55, -36, 14, 70, 40, 20, C["pin"])       # pin 2S 18650 nam ngang (uoc luong)
    hop(ax, 70, -40, 6, 14, 80, 8, C["line"])         # mang do line 5-8 kenh o mui (uoc luong)


def concept_a(ax):
    chung(ax)
    hop(ax, -70, -60, 12, 160, 120, 3, C["khung"])            # tang duoi
    hop(ax, -70, -60, 60, 160, 120, 3, C["khung"], 0.55)      # tang tren
    for x in (-62, 80):
        for y in (-52, 48):
            hop(ax, x, y, 15, 4, 4, 45, MUTED)                 # cot M3
    hop(ax, -54.4, -26.6, 63, 108.8, 53.16, 14.81, C["mega"])  # Mega (kich thuoc do tu STEP)
    hop(ax, 82, -22, 40, 15, 45, 20, C["cam"])                # HC-SR04 o mui


def concept_b(ax):
    chung(ax)
    hop(ax, -54.4, -26.6, 40, 108.8, 53.16, 14.81, C["mega"])
    hop(ax, -78, -66, 10, 172, 132, 70, C["vo"], 0.35)         # vo lien bao kin
    hop(ax, 86, -22, 30, 8, 45, 20, C["cam"])


def concept_c(ax):
    chung(ax)
    hop(ax, -75, -70, 14, 165, 140, 4, C["khung"])
    for x in range(-70, 90, 16):                               # luoi lo buoc deu (minh hoa)
        for y in range(-62, 70, 16):
            hop(ax, x, y, 18, 3, 3, 0.5, "#0b0d10")
    for y in (-60, 52):
        hop(ax, -40, y, 18, 4, 8, 22, MUTED)                   # chan de Mega
    hop(ax, -54.4, -26.6, 40, 108.8, 53.16, 14.81, C["mega"])
    hop(ax, 82, -22, 30, 15, 45, 20, C["cam"])
    hop(ax, 40, 45, 18, 23, 12, 22, "#5a5f66")                 # cho gan them servo/cam bien


GOC = {"hong": (0, -90), "dinh": (90, -90), "3-4": (24, -55)}
NHAN = {"hong": "bóng hông", "dinh": "bóng đỉnh", "3-4": "phối cảnh 3/4"}
HUONG = {"A": ("A – Khung tầng", concept_a), "B": ("B – Thân liền", concept_b), "C": ("C – Khung lưới module", concept_c)}


def ve(ten, ham, goc):
    fig = plt.figure(figsize=(5, 4), dpi=110, facecolor=BG)
    ax = fig.add_subplot(projection="3d", facecolor=BG, computed_zorder=False)  # ve theo thu tu them
    ham(ax)
    ax.set_xlim(-95, 105); ax.set_ylim(-100, 100); ax.set_zlim(0, 150)
    ax.set_box_aspect((200, 200, 150))
    ax.view_init(*GOC[goc])
    ax.set_axis_off()
    fig.text(0.04, 0.93, f"{HUONG[ten][0]} · {NHAN[goc]}", color=INK, fontsize=11, weight="bold")
    fig.text(0.04, 0.03, "Khối minh họa – chỉ Mega đúng kích thước đo (mm)", color=MUTED, fontsize=7)
    f = OUT / f"concept-{ten.lower()}-{goc}.png"
    fig.savefig(f, facecolor=BG)
    plt.close(fig)
    return f


def main():
    OUT.mkdir(exist_ok=True)
    files = [[ve(t, h, g) for g in GOC] for t, (_, h) in HUONG.items()]
    imgs = [[plt.imread(f) for f in hang] for hang in files]
    sheet = np.vstack([np.hstack(h) for h in imgs])
    fig = plt.figure(figsize=(sheet.shape[1] / 110, sheet.shape[0] / 110 + 0.6), dpi=110, facecolor=BG)
    fig.text(0.01, 0.985, "line-bot – bước 0: chọn 1 hướng (khuyến nghị A)", color=INK, fontsize=13, weight="bold",
             va="top")
    ax = fig.add_axes([0, 0, 1, sheet.shape[0] / (sheet.shape[0] + 66)])
    ax.imshow(sheet); ax.set_axis_off()
    fig.savefig(HERE / "contact-sheet.png", facecolor=BG)
    print("OK", HERE / "contact-sheet.png")


if __name__ == "__main__":
    main()
