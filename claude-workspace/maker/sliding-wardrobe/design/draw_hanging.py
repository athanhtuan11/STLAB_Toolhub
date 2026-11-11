"""Ban ve he cua treo 2 canh (doc parts.json do build_wardrobe.py sinh ra).

Chay (tu design/, sau khi build):  python draw_hanging.py
Ra: renders/12-mat-cat-ray.png (mat cat dung qua cum banh: ray tren giu dung + U chan duoi chiu tai)
    renders/13-mat-bang-hanh-trinh.png (mat bang: 3 vi tri cua 2 canh)
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
    UB, UH, UT = P["U"]
    for ax, (zlo, zhi), title in ((a_top, (dz1 - 120, zt1 + hh + 30), "TREN: dam 40x40 + ray hop 40x40 + xe treo (CHI GIU DUNG, ho 3)"),
                                  (a_bot, (-25, dz0 + 110), "DUOI: BE TU 40 - U chan chim ngang mat be + cum banh 608 POM (CHIU TAI)")):
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
            # U chan nam ngua + cang banh + banh (mat cat qua truc banh: banh thay rong wheel_w, cao wheel_d)
            rect(ax, yc - UB / 2, 0, UB, UT, STEEL, z=3)
            rect(ax, yc - UB / 2, 0, UT, UH, STEEL, z=3)
            rect(ax, yc + UB / 2 - UT, 0, UT, UH, STEEL, z=3)
            za = meta["z_axle"]
            bw = P["bogie_w"]
            rect(ax, yc - bw / 2, za + 4, bw, dz0 - za - 4, "#555", z=4)
            rect(ax, yc - bw / 2, za - 3, (bw - P["wheel_w"]) / 2 - 1, 7, "#555", z=4)
            rect(ax, yc + P["wheel_w"] / 2 + 1, za - 3, (bw - P["wheel_w"]) / 2 - 1, 7, "#555", z=4)
            rect(ax, yc - P["wheel_w"] / 2, UT, P["wheel_w"], P["wheel_d"], NYL, z=5)
            rect(ax, yc - 4, za - 4, 8, 8, "#DADDE0", z=6)
        # be tu: thanh dem giua 2 U + dan 20x40 nam + van, mat van = mieng U
        UB_, UH_, UT_ = P["U"]
        rect(ax, L0 + UB_ / 2, 0, L1 - L0 - UB_, UH_, STEEL, z=3)
        yb0 = L1 + UB_ / 2
        rect(ax, yb0, 0, 40, P["be_joist"][1], STEEL, z=3)
        rect(ax, yb0, UH_ - P["be_board"], 140, P["be_board"], "#D9C7A6", z=3)
        ax.text(yb0 + 4, UH_ - P["be_board"] / 2, "van be", fontsize=7, va="center", zorder=6)
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
    dim(a_bot, 112, 0, 112, UH, f"U cao {UH}", 2)
    dim(a_bot, 112, UH, 112, dz0, f"{P['u_gap']} ho", 2)
    dim(a_bot, L1 - UB / 2, -12, L1 + UB / 2, -12, f"U {UB} = day canh", 2, "h")
    a_bot.text(-5, dz0 + 90, f"banh 608 POM O{P['wheel_d']}x{P['wheel_w']}, 2 cum x 2 banh / canh, can >= {meta['WHEEL_NEED']:.0f} kg/banh\n"
               f"cang {P['bogie_w']} trong long U {meta['U_IN']:.0f} -> chan canh lac +-{(meta['U_IN'] - P['bogie_w']) / 2:g} mm",
               fontsize=8)
    fig.suptitle(f"Mat cat qua cum banh  |  khe giua 2 canh {meta['GAP_DOOR']:.0f}  |  canh ~{meta['DOOR_KG'][0]:.0f} kg (lam ~3 kg/thanh)",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "12-mat-cat-ray.png"), dpi=150)


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
        for yc in (L0, L1):
            rect(ax, 0, yc - P["U"][0] / 2, W, P["U"][0], "none", ec="#1565C0", lw=0.8, z=4)
        for i, yc in enumerate((L0, L1)):
            for xb in (DX0[i] + dx[i] + P["bogie_in"], DX0[i] + dx[i] + DWS[i] - P["bogie_in"]):
                ax.add_patch(Circle((xb, yc), 14, fc="#F2F2EE", ec="black", lw=0.6, zorder=5))
        for xl in meta["X_FULL"]:
            rect(ax, xl - 20, 120, 40, 40, STEEL, z=2)
        ax.set_xlim(-80, W + 80)
        ax.set_ylim(-35, 175)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=9)
        ax.set_yticks([])
    axs[-1].set_xlabel("tuong trai -> tuong phai (mm).  Vien xanh = 2 thanh U chan duoi.  Tron trang = cum banh.  O vuong den = cot truoc")
    fig.suptitle(f"Mat bang: canh {DWS[0]:.0f}, chong mi {meta['OV']:.0f}, mo moi nua {meta['OPEN'][0]:.0f}", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "13-mat-bang-hanh-trinh.png"), dpi=150)


if __name__ == "__main__":
    section()
    plan()
    print("OK 12-mat-cat-ray.png, 13-mat-bang-hanh-trinh.png")
