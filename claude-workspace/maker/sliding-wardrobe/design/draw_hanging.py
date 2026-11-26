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
    hh = P["tube"][0]
    PT = meta["PT"]
    fig, (a_top, a_bot) = plt.subplots(2, 1, figsize=(8.5, 11))
    UB, UH, UT = P["U"]
    for ax, (zlo, zhi), title in ((a_top, (dz1 - 120, zt1 + hh + 30), "TREN: dau dam dinh + U chan 40x40 UP NGUOC + banh 608 truc dung (CHI DAN HUONG) + tam che ray"),
                                  (a_bot, (-25, dz0 + 110), "DUOI: BE TU 40 - U chan chim + cum banh 608 POM (CHIU TAI) + tam che ray")):
        for li, yc in enumerate((L0, L1)):
            yf0 = yc - FDP / 2
            # canh: vien hop 20x40 (mat cat: 40 sau x 20 cao) + tam nhua 10 phu mat truoc
            rect(ax, yf0, dz0, FDP, 20, STEEL, z=3)
            rect(ax, yf0, dz1 - 20, FDP, 20, STEEL, z=3)
            rect(ax, yf0 - PT, dz0, PT, dz1 - dz0, LAM, z=3)
            ax.text(yc, (zlo + zhi) / 2, f"C{li + 1}", ha="center", va="center", fontsize=11, color="white", zorder=4,
                    fontweight="bold")
            # U tren up nguoc + banh dan huong truc dung (mat cat qua truc: banh = chu nhat O x day) + bulong M8
            UB_t, UH_t, UT_t = P["U"]
            rect(ax, yc - UB_t / 2, zt1 - UT_t, UB_t, UT_t, STEEL, z=3)
            rect(ax, yc - UB_t / 2, zt0, UT_t, UH_t, STEEL, z=3)
            rect(ax, yc + UB_t / 2 - UT_t, zt0, UT_t, UH_t, STEEL, z=3)
            g0, g1 = meta["z_guide"]
            rect(ax, yc - P["guide_d"] / 2, g0, P["guide_d"], g1 - g0, NYL, z=5)
            rect(ax, yc - 4, dz1, 8, g1 + 2 - dz1, "#DADDE0", z=4)
            rect(ax, yc - 6.5, dz1, 13, 6, "#999", z=4)
            # U chan nam ngua + cang banh + banh (mat cat qua truc banh: banh thay rong wheel_w, cao wheel_d)
            yk = yc
            yc = meta["UL"][li]
            rect(ax, yc - UB / 2, 0, UB, UT, STEEL, z=3)
            rect(ax, yc - UB / 2, 0, UT, UH, STEEL, z=3)
            rect(ax, yc + UB / 2 - UT, 0, UT, UH, STEEL, z=3)
            za = meta["z_axle"]
            bw = P["bogie_w"]
            rect(ax, yc - bw / 2, za + 4, bw, UH - 8 - za, "#555", z=4)
            y_a, y_b = max(yc - bw / 2, yk - FDP / 2), min(yc + bw / 2, yk + FDP / 2)
            rect(ax, y_a, UH - 4, y_b - y_a, dz0 - UH + 4, "#555", z=4)
            rect(ax, yc - bw / 2, za - 3, (bw - P["wheel_w"]) / 2 - 1, 7, "#555", z=4)
            rect(ax, yc + P["wheel_w"] / 2 + 1, za - 3, (bw - P["wheel_w"]) / 2 - 1, 7, "#555", z=4)
            rect(ax, yc - P["wheel_w"] / 2, UT, P["wheel_w"], P["wheel_d"], NYL, z=5)
            rect(ax, yc - 4, za - 4, 8, 8, "#DADDE0", z=6)
        # be tu: thanh dem giua 2 U + dan 20x40 nam + van, mat van = mieng U
        UB_, UH_, UT_ = P["U"]
        rect(ax, meta["UL"][0] + UB_ / 2, 0, meta["UL"][1] - meta["UL"][0] - UB_, UH_, STEEL, z=3)   # thanh giua
        yb0 = meta["UL"][1] + UB_ / 2
        DZ = P["DZ"]
        rect(ax, yb0, 0, 40, P["be_joist"][1], STEEL, z=3)                      # dan be truoc ap sat U trong (han doc), do cot truoc
        rect(ax, DZ, P["be_joist"][1], 40, 200, STEEL, z=2)                     # cot truoc dung tren dan
        rect(ax, yb0, UH_ - P["be_board"], 140, P["be_board"], "#D9C7A6", z=3)
        # dau dam dinh keo dai (ray bat thang duoi) + tam che ray tren/duoi (cung mat canh ngoai)
        rect(ax, L0 - tw / 2, zt1, DZ + 40 - (L0 - tw / 2), hh, STEEL, z=3, hatch="//")
        yfa = meta["YF"][0]
        rect(ax, yfa, dz1 + P["fascia_gap"], PT, zt1 + hh - dz1 - P["fascia_gap"], "#C9A27E", z=5)
        rect(ax, meta["UL"][0] - UB_ / 2 - PT, 0, PT, UH_, "#C9A27E", z=5)
        ax.text(yb0 + 4, UH_ - P["be_board"] / 2, "van be", fontsize=7, va="center", zorder=6)
        rect(ax, -10, -25, 185, 25, "#CFC8BC", ec="none", z=0, hatch="..")    # san
        ax.set_xlim(-10, 175)
        ax.set_ylim(zlo, zhi)
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("sau tu (mm, truoc -> sau)")
        ax.grid(alpha=0.2)
    # kich thuoc
    dim(a_top, 150, dz1, 150, zt0, f"{P['hanger_gap']} (banh ha het nam duoi)", 2)
    dim(a_top, 150, zt0, 150, zt1, f"U tren {th}, nhac toi da {P['guide_top_gap']}", 2)
    dim(a_top, 150, zt1, 150, zt1 + hh, f"dam dinh {hh}", 2)
    a_top.text(0, zt1 + hh + 15, f"dinh dam {meta['H_TOP']:.0f} tu san; tam che ray (vang nhat) cung mat canh ngoai", fontsize=8)
    dim(a_bot, 150, 0, 150, UH, f"U cao {UH}", 2)
    dim(a_bot, 150, UH, 150, dz0, f"{P['u_gap']} ho", 2)
    dim(a_bot, meta["UL"][0] - UB / 2, -12, meta["UL"][1] + UB / 2, -12, "2 U + thanh giua 20, han kep", 2, "h")
    a_bot.text(-5, dz0 + 90, f"banh 608 POM O{P['wheel_d']}x{P['wheel_w']}, 2 cum x 2 banh / canh, can >= {meta['WHEEL_NEED']:.0f} kg/banh\n"
               f"cang {P['bogie_w']} trong long U {meta['U_IN']:.0f} -> chan canh lac +-{(meta['U_IN'] - P['bogie_w']) / 2:g} mm",
               fontsize=8)
    fig.suptitle(f"Mat cat qua cum banh  |  khe giua 2 canh {meta['GAP_DOOR']:.0f}  |  canh ~{meta['DOOR_KG'][0]:.0f} kg (tam nhua {P['panel_kg']} kg/tam)",
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
            rect(ax, x0, meta["YF"][i], DWS[i], meta["DT"], [LAM, "#7A5538"][i], z=3)
            ax.text(x0 + DWS[i] / 2, yc, f"C{i + 1}", color="white", ha="center", va="center", fontsize=8, zorder=4)
        for yc in meta["UL"]:
            rect(ax, 0, yc - P["U"][0] / 2, W, P["U"][0], "none", ec="#1565C0", lw=0.8, z=4)
        for i, yc in enumerate(meta["UL"]):
            for xb in (DX0[i] + dx[i] + P["bogie_in"], DX0[i] + dx[i] + DWS[i] - P["bogie_in"]):
                ax.add_patch(Circle((xb, yc), 14, fc="#F2F2EE", ec="black", lw=0.6, zorder=5))
        for xl in meta["X_FULL"]:
            rect(ax, xl - 20, P["DZ"], 40, 40, STEEL, z=2)
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
