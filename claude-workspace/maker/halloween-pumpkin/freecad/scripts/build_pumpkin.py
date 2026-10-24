"""Bi ngo Halloween tham so cho video "robot cam bi ngo" (y tuong #17, docs/trend-content-ideas.md).

Chay (Python di kem FreeCAD co numpy + matplotlib):
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" freecad/scripts/build_pumpkin.py
Ra: print/stl/<bien_the>.stl (1 luoi kin: than + cuong; in 2 mau = doi cuon o z bat dau cuong, in ra man hinh)
    va design/concepts/<bien_the>.png + design/contact-sheet.png (duyet bang anh).

Rang buoc (do tren model pushrod-arm 2026-10-24, khe 2 dem kep: 0 do 7 mm, -20 do 32 mm, -30 do 42 mm, mo het 63 mm):
    duong kinh 36-46 mm -> kep mo ~nua hanh trinh la om duoc.
In khong support: mat duoi doc toi da 45 do (ban kinh tang <= 1 mm moi 1 mm chieu cao tu day), day phang.
Khong dung FreeCAD B-rep (luoi truc tiep) vi day la dao cu quay video, khong lap rap.
"""

import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "print" / "stl"
CONC = ROOT / "design" / "concepts"

# id: (duong kinh mm, cao than mm, so mui, do sau ranh 0..1, ban kinh day mm, cuong: cao, Ø mm, nghieng do)
VARIANTS = {
    "A_round8": dict(d=40, h=32, lobes=8, groove=0.10, base_r=10, stem=(9, 6, 12), note="Tròn 8 múi, kinh điển"),
    "B_tall10": dict(d=36, h=40, lobes=10, groove=0.08, base_r=9, stem=(10, 5.5, 18), note="Cao 10 múi, thanh"),
    "C_wide12": dict(d=46, h=28, lobes=12, groove=0.12, base_r=13, stem=(7, 7, 6), note="Bè 12 múi, mập"),
}
NZ, NT = 80, 240


def profile(z, d, h, base_r):
    """Ban kinh tron xoay o do cao z (0..h): nua tren elip; nua duoi = min mem (R, r_day + z).
    Min mem cua 2 ham doc 0 va doc 1 co doc trong [0, 1] -> mat duoi khong bao gio doc hon 45 do."""
    R = d / 2
    upper = np.where(z >= h / 2, R * np.sqrt(np.clip(1 - ((z - h / 2) / (h / 2)) ** 2, 0, 1)), R)
    k = 2.0  # do bo tron chuyen tiep (mm)
    return -k * np.logaddexp(-upper / k, -(base_r + z) / k)


def pumpkin(v):
    """1 LUOI KIN LIEN MACH: than (co mui) di len toi khi ban kinh = ban kinh cuong, roi cuong noi tiep.
    -> khong co mat day cuong nam trong than (truoc day printability bao nham "nho ra" o do).
    Tra ve (tam giac, z_noi): z_noi = do cao bat dau cuong = lop doi cuon neu in 2 mau."""
    R, h = v["d"] / 2, v["h"]
    hs, ds, tilt = v["stem"]
    rs = ds / 2
    t = np.linspace(0, 2 * math.pi, NT, endpoint=False)
    z = np.linspace(0, h, NZ)
    r0 = profile(z, v["d"], h, v["base_r"])
    keep = r0 > rs
    zb, rb = z[keep], r0[keep]
    fade = np.clip((rb - rs) / (0.3 * R), 0, 1)[:, None]  # mui mo dan khi sat cuong
    lobe = 1 - v["groove"] * fade * np.abs(np.cos(v["lobes"] * t[None, :] / 2)) ** 6
    Rb = rb[:, None] * lobe
    zj = zb[-1]
    zs = np.linspace(0, hs, 24)[1:]
    Rs = rs * (1 - 0.25 * zs / hs)[:, None] * (1 + 0.08 * np.cos(6 * t[None, :]) * (zs / hs)[:, None])
    Rs[-1, :] = 0  # dinh kin
    lean = (math.tan(math.radians(tilt)) * zs ** 2 / hs)[:, None]  # cong nhe, <= 18 do: khong can support
    X = np.vstack([Rb * np.cos(t), Rs * np.cos(t) + lean])
    Y = np.vstack([Rb * np.sin(t), Rs * np.sin(t)])
    Z = np.vstack([np.repeat(zb[:, None], NT, 1), np.repeat((zs + zj)[:, None], NT, 1)])
    return grid_mesh(X, Y, Z), zj


def grid_mesh(X, Y, Z):
    """Luoi (nz x nt) dong theo goc, day phang o hang dau, dinh la hang cuoi (r=0)."""
    nz, nt = X.shape
    P = np.stack([X, Y, Z], -1)
    tris = []
    for i in range(nz - 1):
        for j in range(nt):
            k = (j + 1) % nt
            a, b, c, d = P[i, j], P[i, k], P[i + 1, j], P[i + 1, k]
            tris += [(a, b, d), (a, d, c)]
    ctr = np.array([0.0, 0.0, Z[0, 0]]) + np.array([X[0].mean(), Y[0].mean(), 0])
    for j in range(nt):  # nap day
        tris.append((ctr, P[0, (j + 1) % nt], P[0, j]))
    return np.array(tris)


def write_stl(path, tri):
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(tri), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = n, tri
    with open(path, "wb") as f:
        f.write(b"STLab halloween-pumpkin".ljust(80, b" "))
        f.write(np.uint32(len(tri)).tobytes())
        f.write(rec.tobytes())


def render(path, b, s, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(4, 4.4), dpi=150)
    ax = fig.add_subplot(projection="3d")
    light = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    for tri, base in ((b, np.array([0.93, 0.47, 0.13])), (s, np.array([0.30, 0.45, 0.20]))):
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
        shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
        ax.add_collection3d(Poly3DCollection(tri, facecolors=np.clip(base * shade[:, None], 0, 1), linewidths=0))
    m = max(np.ptp(b[:, :, 0]), np.ptp(b[:, :, 2]) + 12) / 2
    ax.set_xlim(-m, m), ax.set_ylim(-m, m), ax.set_zlim(0, 2 * m)
    ax.view_init(elev=18, azim=-60)
    ax.set_axis_off()
    fig.suptitle(title, fontsize=10)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    STL.mkdir(parents=True, exist_ok=True)
    CONC.mkdir(parents=True, exist_ok=True)
    pngs = []
    for k, v in VARIANTS.items():
        tri, zj = pumpkin(v)
        write_stl(STL / f"{k}.stl", tri)
        t = f"{k}: Ø{v['d']} × cao {tri[:, :, 2].max():.0f} mm – {v['note']} (cuống từ z {zj:.1f})"
        cz = tri[:, :, 2].mean(1)
        render(CONC / f"{k}.png", tri[cz < zj], tri[cz >= zj], t)
        pngs.append(CONC / f"{k}.png")
        print(t)
    from PIL import Image
    ims = [Image.open(p) for p in pngs]
    w, h = sum(i.width for i in ims), max(i.height for i in ims)
    sheet = Image.new("RGB", (w, h), "white")
    x = 0
    for i in ims:
        sheet.paste(i, (x, 0))
        x += i.width
    sheet.save(ROOT / "design" / "contact-sheet.png")


if __name__ == "__main__":
    main()
