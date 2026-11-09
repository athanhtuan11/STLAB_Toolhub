"""Ban ve kich thuoc + bang cat van + contact sheet tu parts.json (do build_wardrobe.py xuat).

Chay: python draw_plans.py   (tu thu muc design/)
"""
import csv, json, os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
data = json.load(open(os.path.join(HERE, "parts.json"), encoding="utf-8"))
meta, parts = data["meta"], data["parts"]
P = meta["P"]
W, H, D, T, CL = meta["W_body"], P["H"], P["D"], P["T"], meta["CL"]
SHEET = (2440, 1220)                    # kho van chuan (TODO: xac nhan kho xuong dung)
COL = {"carcass": "#D6C3A3", "interior": "#E4D6BC", "back": "#EFE8DA", "drawer": "#FFFFFF",
       "rod": "#8A9096", "alu": "#B9BEC3", "door": "#8B6A4F", "dark": "#333"}


def dim(ax, x0, y0, x1, y1, txt, off=0, vert=False, fs=8):
    if vert:
        ax.annotate("", (x0 + off, y0), (x0 + off, y1), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(x0 + off - 25, (y0 + y1) / 2, txt, rotation=90, ha="right", va="center", fontsize=fs)
    else:
        ax.annotate("", (x0, y0 + off), (x1, y0 + off), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((x0 + x1) / 2, y0 + off + 20, txt, ha="center", va="bottom", fontsize=fs)


def front_elevation():
    fig, ax = plt.subplots(figsize=(15, 13))
    for pt in parts:
        x0, x1, y0, y1, z0, z1 = pt["bbox"]
        g = pt["group"]
        if g.startswith("Canh") or g in ("Ray", "Moi truong") or "-nk" in pt["name"] and "mat" not in pt["name"]:
            continue
        if g == "Op lam song":
            for xx in ((-CL, 0), (W, W + CL)):
                ax.add_patch(Rectangle((xx[0], 0), CL, H, fc=COL["door"], ec="k", lw=0.3))
            continue
        if pt["mat"] == "back":
            continue
        ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=COL.get(pt["mat"], "#ccc"), ec="k", lw=0.4))
    # kich thuoc tong
    dim(ax, -CL, H, W + CL, H, f"Rộng tổng {W + 2 * CL:.0f} (thân {W:.0f} + ốp lam sóng 2×{CL})", off=120)
    dim(ax, -CL, 0, -CL, H, f"Cao {H}", off=-150, vert=True)
    dim(ax, -CL, 0, -CL, P["H_low"], f"Module dưới {P['H_low']}", off=-60, vert=True)
    # tung khoang
    for b, ((bx0, bx1), spec) in enumerate(zip(meta["bay_x"], meta["BAYS"])):
        dim(ax, bx0, H, bx1, H, f"lòng {bx1 - bx0:.0f}", off=-260, fs=7)
        ax.text((bx0 + bx1) / 2, P["H_low"] - 120, spec["name"], ha="center", fontsize=9, weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.8))
        for zt in spec["shelves"]:
            ax.text(bx0 + 15, zt + 10, f"kệ {zt}", fontsize=6.5, color="#444")
        for zr in spec["rods"]:
            ax.text(bx1 - 15, zr + 25, f"ống Ø{P['rod_d']} @ {zr}", fontsize=6.5, ha="right", color="#1a4d80")
        z = P["plinth"] + T
        for k, h in enumerate(spec["drawers"]):
            ax.text((bx0 + bx1) / 2, z + h / 2, f"ngăn kéo {h}", fontsize=6.5, ha="center", va="center")
            z += h
    ax.text(W / 2, P["H_low"] + (H - P["H_low"]) / 2, "Hộp nóc: chăn mền, vali (đồ theo mùa)",
            ha="center", fontsize=9, style="italic")
    ax.set_xlim(-450, W + 250)
    ax.set_ylim(-150, H + 350)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("MẶT ĐỨNG BỐ TRÍ TRONG (bỏ cánh) – đơn vị mm, cao độ tính từ sàn", fontsize=12)
    fig.savefig(os.path.join(OUT, "10-ban-ve-mat-dung.png"), dpi=110, bbox_inches="tight")
    plt.close(fig)


def plan_doors():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw=dict(width_ratios=[3, 1.1]))
    # mat bang canh
    a1.add_patch(Rectangle((0, 0), W, D, fc="#F6F1E7", ec="k", lw=0.6))
    a1.add_patch(Rectangle((-CL, 0), CL, D, fc=COL["door"]))
    a1.add_patch(Rectangle((W, 0), CL, D, fc=COL["door"]))
    dw = meta["door_w"]
    for i in range(P["door_n"]):
        front = i % 2 == 0
        yc = 30 if front else 72
        x0 = T + i * (dw - P["door_ov"])
        a1.add_patch(Rectangle((x0, yc - P["door_t"] / 2), dw, P["door_t"], fc=COL["door"], ec="k", lw=0.5))
        a1.text(x0 + dw / 2, yc - 45 if front else yc + 30, f"Cánh {i + 1} ({'ray ngoài' if front else 'ray trong'})",
                ha="center", fontsize=7)
    for (bx0, bx1) in meta["bay_x"]:
        a1.add_patch(Rectangle((bx0, P["DZ"]), bx1 - bx0, D - P["DZ"] - P["T_back"], fc="none", ec="#999", ls="--"))
    dim(a1, T, D, T + dw, D, f"cánh {dw:.1f}", off=60)
    dim(a1, T + dw - P["door_ov"], D, T + dw, D, f"chồng {P['door_ov']}", off=160, fs=7)
    dim(a1, -CL, 0, -CL, D, f"sâu {D}", off=-60, vert=True)
    dim(a1, W + CL, 0, W + CL, P["DZ"], f"ray {P['DZ']}", off=120, vert=True, fs=7)
    a1.text(W / 2, D / 2, f"Lòng sâu sử dụng {D - P['DZ'] - P['T_back']} mm", ha="center", fontsize=9)
    a1.set_xlim(-250, W + 300); a1.set_ylim(-120, D + 330)
    a1.invert_yaxis(); a1.set_aspect("equal"); a1.axis("off")
    a1.set_title("MẶT BẰNG – 4 cánh trên 2 ray (mặt trước ở dưới)", fontsize=11)
    # mat cat canh khoang treo
    a2.add_patch(Rectangle((0, 0), D, H, fc="#F6F1E7", ec="k", lw=0.6))
    a2.add_patch(Rectangle((D - P["T_back"], 0), P["T_back"], H, fc=COL["back"], ec="k", lw=0.3))
    yr = (P["DZ"] + D - P["T_back"]) / 2
    for zt in (P["plinth"] + T, P["H_low"], P["H_low"] + T, H):
        a2.add_patch(Rectangle((P["DZ"], zt - T), D - P["DZ"] - P["T_back"], T, fc=COL["carcass"], ec="k", lw=0.3))
    for zr in (2050, 1030):
        a2.add_patch(Rectangle((yr - 225, zr - 900), 450, 850, fc="#cfe0f0", ec="#7aa", alpha=0.6))
        a2.add_patch(plt.Circle((yr, zr), P["rod_d"] / 2 * 2, fc=COL["rod"], ec="k"))
        a2.text(yr, zr - 470, f"ống Ø{P['rod_d']} @ {zr}\náo dài ≤ 850\nmóc rộng ~450", ha="center", fontsize=7)
    a2.add_patch(Rectangle((30 - 9, P["plinth"] + T + 15), 18, meta["door_h"], fc=COL["door"]))
    a2.add_patch(Rectangle((72 - 9, P["plinth"] + T + 15), 18, meta["door_h"], fc=COL["door"], alpha=0.6))
    dim(a2, P["DZ"], 2050, yr, 2050, f"{yr - P['DZ']:.0f}", off=-90, fs=7)
    a2.set_xlim(-150, D + 200); a2.set_ylim(-80, H + 100)
    a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("MẶT CẮT khoang treo 2 tầng (K1, K4)", fontsize=11)
    fig.savefig(os.path.join(OUT, "11-mat-bang-va-mat-cat.png"), dpi=110, bbox_inches="tight")
    plt.close(fig)


def cut_list():
    rows = Counter()
    for pt in parts:
        if not pt["cut"]:
            continue
        rows[(pt["mat"], pt["L"], pt["Wd"], pt["Th"], pt["name"].split("-")[-1].rstrip("0123456789"))] += 1
    bad = []
    path = os.path.join(HERE, "cut-list.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["vat_lieu", "dai_mm", "rong_mm", "day_mm", "loai", "so_luong", "vua_kho_2440x1220"])
        for (m, L, Wd, Th, kind), q in sorted(rows.items(), key=lambda r: (-r[0][3], -r[0][1])):
            ok = L <= SHEET[0] and Wd <= SHEET[1]
            if not ok:
                bad.append((kind, L, Wd))
            w.writerow([m, L, Wd, Th, kind, q, "OK" if ok else "VUOT KHO"])
        rods = [pt for pt in parts if pt["mat"] == "rod" and "ong-treo" in pt["name"]]
        w.writerow([])
        w.writerow(["ong inox tron", "", "", f"Ø{P['rod_d']}", "ong treo", len(rods),
                    "dai moi ong " + ", ".join(sorted({str(r['L']) for r in rods}))])
        w.writerow(["lam song", H, "", "", "op 2 vach ngoai (nguyen cay)", "", f"TODO so thanh = {D}/rong thanh x 2"])
        w.writerow(["lam song", round(meta["door_h"] - 65), "", "", "dan 4 canh (cat tu thanh 2900)", "",
                    f"TODO so thanh = {meta['door_w'] - 40:.0f}/rong thanh x 4"])
    area = sum(pt["L"] * pt["Wd"] for pt in parts if pt["cut"] and pt["Th"] >= 15) / 1e6
    return bad, area


def contact():
    names = ["01-mat-truoc-dong-cua", "03-iso-mo-khoang-1-4", "05-iso-mo-khoang-2-3",
             "04-iso-khong-cua", "10-ban-ve-mat-dung", "11-mat-bang-va-mat-cat"]
    tw, th = 800, 640
    sheet = Image.new("RGB", (tw * 3, th * 2 + 40), "white")
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n + ".png")).convert("RGB")
        im.thumbnail((tw - 10, th - 30))
        x, y = (i % 3) * tw, (i // 3) * th + 40
        sheet.paste(im, (x + (tw - im.width) // 2, y + 25))
        dr.text((x + 10, y + 2), n, fill="black", font=font)
    dr.text((10, 8), "Tủ áo cửa lùa 4 cánh – lam sóng 2900 – contact sheet", fill="black", font=font)
    sheet.save(os.path.join(OUT, "00-contact-sheet.png"))


front_elevation()
plan_doors()
bad, area = cut_list()
contact()
print("VAN >=15mm: %.2f m2 (~%.1f tam 2440x1220 chua tinh hao hut)" % (area, area / 2.977))
print("VUOT KHO:", bad or "khong")
print("PLANS OK")
