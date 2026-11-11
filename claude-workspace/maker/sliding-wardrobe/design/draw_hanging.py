"""Ban ve he cua treo 2 canh (doc parts.json do build_wardrobe.py sinh ra).

Chay (tu design/, sau khi build):  python draw_hanging.py
Ra: renders/12-mat-cat-treo-dan-huong.png (mat cat dung tai x = W/2: ray treo + ranh/chot dan huong san)
    renders/13-mat-bang-hanh-trinh.png (mat bang: 3 vi tri cua 2 canh, chot dan huong luon nam duoi ca 2 canh)
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE, "parts.json"), encoding="utf-8"))["meta"]
P = meta["P"]
OUT = os.path.join(HERE, "renders")
STEEL, LAM, ALU, NYL, RUB = "#2B2D30", "#9C6B47", "#B9BEC3", "#F2F2EE", "#C0392B"


def rect(ax, x0, y0, w, h, fc, ec="black", lw=0.8, z=2, hatch=None):
    ax.add_patch(Rectangle((x0, y0), w, h, fc=fc, ec=ec, lw=lw, zorder=z, hatch=hatch))


def dim(ax, x0, y0, x1, y1, txt, off=0, side="v"):
    ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#1565C0"))
    xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
    ax.text(xm + (off if side == "v" else 0), ym + (off if side == "h" else 0), txt, color="#1565C0", fontsize=8,
            ha="left" if side == "v" else "center", va="center" if side == "v" else "bottom")


def section():
    """Mat cat dung (truc ngang = y truoc->sau, truc dung = z) - 2 khung: tren (ray) va duoi (dan huong)."""
    L0, L1 = meta["LANES"]
    FDP = meta["FDP"]
    dz0, dz1 = meta["dz"]
    zt0, zt1 = meta["z_track"]
    tw, th = P["track"]
    hh = P["header"][1]
    fig, (a_top, a_bot) = plt.subplots(2, 1, figsize=(8.5, 11))
    for ax, (zlo, zhi), title in ((a_top, (dz1 - 120, zt1 + hh + 30), "TREN: dam 40x80 dung + ray treo TAI NANG (ve theo hop 40x40) + xe treo >= 65 kg"),
                                  (a_bot, (-25, dz0 + 110), "DUOI: doan U chan 40x40x2 + 2 mieng POM (giua tu) + gan sat la duoi canh")):
        for li, yc in enumerate((L0, L1)):
            yf0 = yc - FDP / 2
            # canh: vien hop 20x40 (mat cat: 40 sau x 20 cao), lam phia sau mat truoc ~1
            rect(ax, yf0, dz0, FDP, 20, STEEL, z=3)
            rect(ax, yf0, dz1 - 20, FDP, 20, STEEL, z=3)
            rect(ax, yf0 + 1, dz0 + 20, FDP - 14, dz1 - dz0 - 40, LAM, z=1)
            ax.text(yc, (zlo + zhi) / 2, f"C{li + 1}", ha="center", va="center", fontsize=11, color="white", zorder=4,
                    fontweight="bold")
            # ray hop + dam
            rect(ax, yc - tw / 2, zt0, tw, th, "none", ec=ALU, lw=2.2, z=3)
            rect(ax, yc - 20, zt1, 40, hh, STEEL, z=3, hatch="//")
            # xe treo + bulong + bat
            rect(ax, yc - 8, zt0 + 4, 16, P["trolley_h"], "#555", z=4)
            ax.add_patch(Circle((yc, zt0 + 14), 7, fc=NYL, ec="black", lw=0.6, zorder=5))
            rect(ax, yc - 4, dz1 + 6, 8, zt0 + 8 - dz1 - 6, "#DADDE0", z=4)
            rect(ax, yc - 15, dz1, 30, 6, STEEL, z=4)
            # doan U + POM + gan
            UB, UH, UT = P["U"]
            rect(ax, yc - UB / 2, 0, UB, UT, STEEL, z=3)
            rect(ax, yc - UB / 2, 0, UT, UH, STEEL, z=3)
            rect(ax, yc + UB / 2 - UT, 0, UT, UH, STEEL, z=3)
            pt = meta["POM_T"]
            rect(ax, yc - UB / 2 + UT, UT, pt, UH - UT, NYL, z=3)
            rect(ax, yc + UB / 2 - UT - pt, UT, pt, UH - UT, NYL, z=3)
            rect(ax, yc - P["fin_t"] / 2, P["fin_bottom"], P["fin_t"], dz0 - P["fin_bottom"], STEEL, z=4)
        rect(ax, -10, -25, 140, 25, "#CFC8BC", ec="none", z=0, hatch="..")    # san
        ax.set_xlim(-10, 130)
        ax.set_ylim(zlo, zhi)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("sau tu (mm, truoc -> sau)")
        ax.grid(alpha=0.2)
    # kich thuoc
    dim(a_top, 112, dz1, 112, zt0, f"{P['hanger_gap']} khe chinh cao (TODO)", 2)
    dim(a_top, 112, zt0, 112, zt1, f"ray {th}", 2)
    dim(a_top, 112, zt1, 112, zt1 + hh, f"dam {hh}", 2)
    a_top.text(0, zt1 + hh + 15, f"dinh dam {meta['H_TOP']:.0f} tu san", fontsize=8)
    dim(a_bot, 112, 0, 112, P["U"][1], f"U cao {P['U'][1]} (chi o giua, dai {P['guide_L']})", 2)
    dim(a_bot, 112, P["U"][1], 112, dz0, f"{P['u_gap']} ho", 2)
    a_bot.text(-5, dz0 + 90, f"gan la {P['fin_t']} an {meta['FIN_H'] - P['u_gap']:.0f} vao khe POM -> chan canh lac +-{P['fin_clear']} mm\n"
               f"doan U {meta['GX'][0]:.0f}..{meta['GX'][1]:.0f} luon nam duoi ca 2 canh (khong lo, khong vap)", fontsize=8)
    fig.suptitle(f"Mat cat cua treo tai x = {meta['X_GUIDE']:.0f}  |  khe giua 2 canh {meta['GAP_DOOR']:.0f}  |  "
                 f"canh ~{meta['DOOR_KG'][0]:.0f} kg (lam_kg TODO)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "12-mat-cat-treo-dan-huong.png"), dpi=150)


def plan():
    W = P["W"]
    DWS, DX0, TR = meta["DWS"], meta["DX0"], meta["TRAVEL"]
    L0, L1 = meta["LANES"]
    fig, axs = plt.subplots(3, 1, figsize=(11, 6.5))
    states = [("Dong ca 2 canh", [0, 0]), (f"C1 lua phai {TR[0][1]:.0f} -> mo nua trai", [TR[0][1], 0]),
              (f"C2 lua trai {TR[1][0]:.0f} -> mo nua phai", [0, -TR[1][0]])]
    for ax, (title, dx) in zip(axs, states):
        rect(ax, -60, -30, 60, 160, "#E9E6E0", ec="none")
        rect(ax, W, -30, 60, 160, "#E9E6E0", ec="none")
        for i, yc in enumerate((L0, L1)):
            x0 = DX0[i] + dx[i]
            rect(ax, x0, yc - 20, DWS[i], 40, [LAM, "#7A5538"][i], z=3)
            ax.text(x0 + DWS[i] / 2, yc, f"C{i + 1}", color="white", ha="center", va="center", fontsize=8, zorder=4)
        rect(ax, meta["GX"][0], L0 - 20, meta["GX"][1] - meta["GX"][0], L1 - L0 + 40, "#1565C0", ec="none", z=5)
        for xl in meta["X_FULL"]:
            rect(ax, xl - 20, 120, 40, 40, STEEL, z=2)
        ax.set_xlim(-80, W + 80)
        ax.set_ylim(-35, 175)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        ax.set_yticks([])
    axs[-1].set_xlabel("tuong trai -> tuong phai (mm).  O xanh = doan U dan huong (luon khuat duoi 2 canh).  O vuong den = cot truoc")
    fig.suptitle(f"Mat bang: canh {DWS[0]:.0f}, chong mi {meta['OV']:.0f}, mo moi nua {meta['OPEN'][0]:.0f}", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "13-mat-bang-hanh-trinh.png"), dpi=150)


if __name__ == "__main__":
    section()
    plan()
    print("OK 12-mat-cat-treo-dan-huong.png, 13-mat-bang-hanh-trinh.png")
