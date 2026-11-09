"""Ban ve kich thuoc + bang vat tu + contact sheet tu parts.json (build_wardrobe.py xuat).

Chay: python draw_plans.py  (tu design/)
"""
import csv, json, math, os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
data = json.load(open(os.path.join(HERE, "parts.json"), encoding="utf-8"))
m, parts = data["meta"], data["parts"]
P = m["P"]
W, D, DW, OV, k, H_TOP = P["W"], P["D"], m["DW"], m["OV"], m["k"], m["H_TOP"]
XL, YM = m["x_lines"], m["y_mid"]
C = {"steel": "#2B2D30", "lam": "#8B6A4F", "board": "#D9C7A6", "rod": "#7D8790", "alu": "#B9BEC3"}
# kg/m tinh tu tiet dien hop (thep 7,85 g/cm3) - do day theo gia dinh, TODO theo hang mua
KGM = {"40x40": (4 * 40 * 1.4 - 4 * 1.4 ** 2) * 7.85e-3, "40x80": (2 * 120 * 1.4 - 4 * 1.4 ** 2) * 7.85e-3,
       "20x40": (2 * 60 * 1.2 - 4 * 1.2 ** 2) * 7.85e-3}


def dim(ax, x0, y0, x1, y1, txt, off=0, vert=False, fs=8):
    if vert:
        ax.annotate("", (x0 + off, y0), (x0 + off, y1), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text(x0 + off - 25, (y0 + y1) / 2, txt, rotation=90, ha="right", va="center", fontsize=fs)
    else:
        ax.annotate("", (x0, y0 + off), (x1, y0 + off), arrowprops=dict(arrowstyle="<->", lw=0.7))
        ax.text((x0 + x1) / 2, y0 + off + 20, txt, ha="center", va="bottom", fontsize=fs)


def proj(pt, plane):
    x0, x1, y0, y1, z0, z1 = pt["bbox"]
    return (x0, z0, x1 - x0, z1 - z0) if plane == "xz" else (x0, y0, x1 - x0, y1 - y0) if plane == "xy" else (y0, z0, y1 - y0, z1 - z0)


def front_elevation():
    fig, ax = plt.subplots(figsize=(15, 14))
    ax.add_patch(Rectangle((-120, 0), 120, H_TOP + 150, fc="#ddd", hatch="//", ec="#999"))
    ax.add_patch(Rectangle((W, 0), 120, H_TOP + 150, fc="#ddd", hatch="//", ec="#999"))
    for pt in parts:
        if pt["group"] in ("Khung sat", "Van", "Ong treo") and not (pt["kind"] == "steel" and pt["bbox"][2] < 100
                                                                     and pt["Wd"] == 80):
            x, z, w, h = proj(pt, "xz")
            ax.add_patch(Rectangle((x, z), w, h, fc=C.get(pt["mat"], "#ccc"), ec="k", lw=0.3,
                                   alpha=0.85 if pt["mat"] == "steel" else 1))
    dim(ax, 0, H_TOP, W, H_TOP, f"Tường – tường {W} (đo lại)", off=150)
    dim(ax, -120, 0, -120, H_TOP, f"Đỉnh dầm {H_TOP:.0f}", off=-110, vert=True)
    dim(ax, -120, 0, -120, P["z_shelf"], f"Kệ nóc {P['z_shelf']}", off=-20, vert=True)
    for b, spec in enumerate(m["BAYS"]):
        xa, xb = XL[b] + 20, XL[b + 1] - 20
        dim(ax, xa, 0, xb, 0, f"lọt lòng {xb - xa:.0f}", off=-90, fs=7)
        ax.text((xa + xb) / 2, 1500, spec["name"], ha="center", fontsize=10, weight="bold",
                bbox=dict(fc="white", ec="none", alpha=0.85))
        for zr in spec["rods"]:
            ax.text((xa + xb) / 2, zr + 30, f"ống Ø{P['rod_d']} dài {xb - xa - 2:.0f} @ {zr}", ha="center",
                    fontsize=7.5, color="#1a4d80")
    for i, x in enumerate(XL):
        ax.text(x, -200, f"khung {i}\nx={x:.0f}", ha="center", fontsize=6.5, va="top")
    ax.text(W / 2, P["z_shelf"] + 330, "Hộp nóc: chăn mền, vali", ha="center", fontsize=9, style="italic")
    ax.set_xlim(-500, W + 250); ax.set_ylim(-420, H_TOP + 330)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("MẶT ĐỨNG KHUNG SẮT (bỏ cánh) – mm, cao độ từ sàn", fontsize=12)
    fig.savefig(os.path.join(OUT, "10-ban-ve-khung-sat.png"), dpi=105, bbox_inches="tight")
    plt.close(fig)


def door_and_plan():
    fig = plt.figure(figsize=(16, 9))
    a0 = fig.add_axes([0.0, 0.05, 0.22, 0.9])
    a1 = fig.add_axes([0.24, 0.45, 0.55, 0.5])
    a2 = fig.add_axes([0.80, 0.05, 0.2, 0.9])
    # 1 canh
    fw = P["door_frame"][1]
    for j in range(k):
        a0.add_patch(Rectangle((j * P["lam_w"], 0), P["lam_w"], m["DH"], fc=C["lam"], ec="k", lw=0.5))
    for xx in (10, DW - 10 - fw):
        a0.add_patch(Rectangle((xx, 0), fw, m["DH"], fc="none", ec="#222", ls="--", lw=0.8))
    for zz in (30, m["DH"] / 2, m["DH"] - 30):
        a0.add_patch(Rectangle((10 + fw, zz - 10), DW - 20 - 2 * fw, 20, fc="none", ec="#222", ls="--", lw=0.8))
    dim(a0, 0, m["DH"], DW, m["DH"], f"{DW} = {k} thanh × {P['lam_w']}", off=80)
    dim(a0, 0, 0, 0, m["DH"], f"{m['DH']} = lam nguyên cây", off=-60, vert=True)
    a0.text(DW / 2, -150, "Khung hộp 20×40 (nét đứt) sau lam\nbánh xe dưới, dẫn hướng trên", ha="center", fontsize=8)
    a0.set_xlim(-300, DW + 100); a0.set_ylim(-350, m["DH"] + 250); a0.set_aspect("equal"); a0.axis("off")
    a0.set_title("1 CÁNH (nhìn trước)", fontsize=11)
    # mat bang
    a1.add_patch(Rectangle((-120, -150), 120, D + 270, fc="#ddd", hatch="//", ec="#999"))
    a1.add_patch(Rectangle((W, -150), 120, D + 270, fc="#ddd", hatch="//", ec="#999"))
    a1.add_patch(Rectangle((-120, D), W + 240, 120, fc="#ddd", hatch="//", ec="#999"))
    for pt in parts:
        if pt["group"] == "Khung sat" and pt["kind"] == "steel" and pt["bbox"][5] - pt["bbox"][4] > 500:
            x, y, w, h = proj(pt, "xy")
            a1.add_patch(Rectangle((x, y), w, h, fc=C["steel"]))
    for i in range(P["door_n"]):
        front = i % 2 == 0
        yl = m["LANES"][i % 2] - P["door_frame"][0] / 2 - P["lam_t"]
        x0 = i * (DW - OV)
        a1.add_patch(Rectangle((x0, yl), DW, P["lam_t"] + 20, fc=C["lam"], ec="k", lw=0.5, alpha=0.9))
        a1.text(x0 + DW / 2, -40 if front else 150, f"Cánh {i + 1} – ray {'ngoài' if front else 'trong'}",
                ha="center", fontsize=7)
    for b, spec in enumerate(m["BAYS"]):
        a1.text((XL[b] + XL[b + 1]) / 2, D / 2 + 60, spec["name"], ha="center", fontsize=8)
    a1.plot([0, W], [YM, YM], ls=":", c="#1a4d80", lw=1)
    a1.text(W / 2, YM - 30, f"tim ống treo – cách mặt trong khung {YM - P['DZ']:.0f}", ha="center", fontsize=7,
            color="#1a4d80")
    dim(a1, 0, -150, DW, -150, f"cánh {DW}", off=0, fs=7)
    dim(a1, DW - OV, -230, DW, -230, f"chồng mí {OV:.0f}", off=0, fs=7)
    dim(a1, W, 0, W, P["DZ"], f"ray {P['DZ']}", off=170, vert=True, fs=7)
    dim(a1, W, 0, W, D, f"sâu {D}", off=280, vert=True, fs=7)
    a1.set_xlim(-200, W + 350); a1.set_ylim(-300, D + 150); a1.invert_yaxis()
    a1.set_aspect("equal"); a1.axis("off")
    a1.set_title("MẶT BẰNG (mặt trước ở trên) – cột giữa đứng sau chỗ chồng mí", fontsize=11)
    open_end, open_mid = DW - OV, DW - 2 * OV
    a1.text(0, D + 330, f"Lùa 1 cánh: khoang ngoài mở {open_end:.0f}, khoang giữa mở {open_mid:.0f}", fontsize=9)
    # mat cat
    a2.add_patch(Rectangle((D, 0), 100, H_TOP + 100, fc="#ddd", hatch="//", ec="#999"))
    for pt in parts:
        if pt["group"] in ("Khung sat", "Van") and abs(pt["bbox"][0] - XL[1] + 20) < 1:
            y, z, w, h = proj(pt, "yz")
            a2.add_patch(Rectangle((y, z), w, h, fc=C.get(pt["mat"]), ec="k", lw=0.3))
    a2.add_patch(Rectangle((P["DZ"], P["z_shelf"]), D - P["DZ"], P["board_t"], fc=C["board"]))
    for zr in (2050, 1030):
        a2.add_patch(Rectangle((YM - 225, zr - 900), 450, 850, fc="#cfe0f0", ec="#7aa", alpha=0.6))
        a2.add_patch(Circle((YM, zr), 27, fc=C["rod"], ec="k"))
        a2.text(YM, zr - 480, f"ống @ {zr}\náo ≤ 850\nmóc ~450", ha="center", fontsize=7)
    for ln in m["LANES"]:
        yl = ln - P["door_frame"][0] / 2 - P["lam_t"]
        a2.add_patch(Rectangle((yl, m["dz"][0]), P["lam_t"] + 20, m["DH"], fc=C["lam"], alpha=0.8))
    a2.set_xlim(-100, D + 150); a2.set_ylim(-50, H_TOP + 150); a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("MẶT CẮT khoang 2 tầng", fontsize=11)
    fig.savefig(os.path.join(OUT, "11-canh-mat-bang-mat-cat.png"), dpi=105, bbox_inches="tight")
    plt.close(fig)


def bom():
    rows = Counter()
    kg = 0.0
    for pt in parts:
        if pt["kind"] in ("steel", "dframe"):
            rows[("Sat hop " + pt["spec"], pt["L"], pt["name"].split("-", 1)[1].rstrip("0123456789-"))] += 1
            kg += KGM[pt["spec"]] * pt["L"] / 1000
        elif pt["kind"] == "plate":
            rows[("Ban de " + pt["spec"], "", "de cot giua bat no san")] += 1
        elif pt["kind"] == "board":
            rows[(f"Van ke {P['board_t']}", f"{pt['L']} x {pt['Wd']}", "ke hop noc")] += 1
        elif pt["kind"] == "rod":
            rows[(f"Ong inox tron {pt['spec']}", pt["L"], "ong treo")] += 1
        elif pt["kind"] == "lam":
            rows[(f"Lam song {P['lam_w']}x{P['lam_L']}x{P['lam_t']}", P["lam_L"], "canh (nguyen cay, khong cat)")] += 1
        elif pt["kind"] == "track":
            rows[(pt["spec"], pt["L"], "ray cua lua")] += 1
        elif pt["kind"] == "stop":
            rows[("Chan cuoi cao su", "", "2 dau moi mang tren")] += 1
        elif pt["kind"] == "eprof":
            rows[("Nep nhom U boc mep canh (tay nam)", pt["L"], "2 mep moi canh")] += 1
    path = os.path.join(HERE, "bom.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["vat_tu", "dai_mm", "vi_tri", "so_luong"])
        for (a, L, v), q in sorted(rows.items(), key=lambda r: (r[0][0], str(r[0][1]))):
            w.writerow([a, L, v, q])
        w.writerow([])
        w.writerow(["Banh do duoi (o bi, ranh U/V) + hop banh chinh cao", "", "2 banh/canh", 2 * P["door_n"]])
        w.writerow(["Banh dan huong tren truc dung", "", "2 banh/canh", 2 * P["door_n"]])
        w.writerow(["Khoa chong nhay ray", "", "1/canh", P["door_n"]])
        w.writerow(["Ron choi chong bui (mep chong mi)", m["DH"], "1/canh", P["door_n"]])
        w.writerow(["LUU Y", "", "tai moi banh >= (khoi luong canh / 2) x 1.5 – can 1 thanh lam truoc khi mua", ""])
        w.writerow(["Khoi luong sat uoc tinh (kg)", round(kg, 1), "do day 1.4/1.2 gia dinh", ""])
    tube_m = Counter()
    for pt in parts:
        if pt["kind"] in ("steel", "dframe"):
            tube_m[pt["spec"]] += pt["L"] / 1000
    return kg, tube_m


def rail_detail():
    """Mat cat chi tiet ray duoi + ray tren (phong to) + vi tri phu kien tren 1 canh."""
    fig = plt.figure(figsize=(17, 9.5))
    ab = fig.add_axes([0.0, 0.05, 0.33, 0.85])
    at = fig.add_axes([0.34, 0.05, 0.33, 0.85])
    ae = fig.add_axes([0.70, 0.05, 0.30, 0.85])
    L1, L2 = m["LANES"]
    dz0, dz1 = m["dz"]
    zr, (zc0, zc1) = m["z_ridge"], m["z_ch"]
    FD, LT = P["door_frame"][0], P["lam_t"]

    def door_sec(ax, ln, z0, z1):
        yl = ln - FD / 2 - LT
        ax.add_patch(Rectangle((yl, z0), LT, z1 - z0, fc=C["lam"], ec="k", lw=0.5))
        ax.add_patch(Rectangle((yl + LT, z0), FD, z1 - z0, fc="#555", ec="k", lw=0.5))

    # ray duoi
    ab.add_patch(Rectangle((-10, -12), P["DZ"] + 30, 12, fc="#ddd", hatch="//", ec="#999"))
    ab.add_patch(Rectangle((5, 0), P["DZ"] - 10, P["trk_base"], fc=C["alu"], ec="k", lw=0.5))
    for ln in (L1, L2):
        ab.add_patch(Rectangle((ln - P["ridge_w"] / 2, P["trk_base"]), P["ridge_w"], P["ridge_h"],
                               fc=C["alu"], ec="k", lw=0.5))
        door_sec(ab, ln, dz0, dz0 + 110)
        zw = zr - 3 + P["wheel_d"] / 2
        ab.add_patch(Rectangle((ln - P["wheel_t"] / 2, zw - P["wheel_d"] / 2), P["wheel_t"], P["wheel_d"],
                               fc="#f2f2ee", ec="k", lw=0.8, zorder=5))
        ab.add_patch(Rectangle((ln - 9, dz0 + 5), 18, 20, fc="none", ec="w", lw=0.8, ls="--", zorder=6))
    dim(ab, -5, 0, -5, zr, f"gờ {zr:.0f}", vert=True, fs=8)
    dim(ab, P["DZ"] + 10, zr, P["DZ"] + 10, dz0, f"khe {dz0 - zr:.0f}", vert=True, fs=8)
    dim(ab, L1, 125, L2, 125, f"2 lằn ray cách {L2 - L1:.0f}", fs=8)
    ab.text(P["DZ"] / 2, -45, "ray nhôm bắt vít + tắc kê xuống sàn", ha="center", fontsize=8)
    ab.text(P["DZ"] / 2, 175, f"Bánh đỡ dưới Ø{P['wheel_d']} (rãnh U/V, ổ bi), hộp bánh có vít chỉnh cao,\n"
            "bắt dưới thanh ngang khung cánh", ha="center", fontsize=8)
    ab.set_xlim(-60, P["DZ"] + 60); ab.set_ylim(-70, 205); ab.set_aspect("equal"); ab.axis("off")
    ab.set_title("MẶT CẮT RAY DƯỚI – chịu toàn bộ tải cánh", fontsize=11)
    # ray tren
    hz = m["H_TOP"]
    at.add_patch(Rectangle((-10, hz - 40), P["DZ"] + 20, 40, fc=C["steel"], ec="k"))
    at.text(P["DZ"] / 2, hz - 20, "dầm đầu cửa hộp 40×80 (bắt nở 2 tường)", color="w", ha="center",
            va="center", fontsize=7.5)
    at.add_patch(Rectangle((5, zc1), P["DZ"] - 10, P["ch_wall"], fc=C["alu"], ec="k", lw=0.5))
    cw = P["roller_d"] + 2
    for ln in (L1, L2):
        for sg in (-1, 1):
            yw = ln + sg * cw / 2
            at.add_patch(Rectangle((min(yw, yw + sg * 2), zc0), 2, zc1 - zc0, fc=C["alu"], ec="k", lw=0.5))
        door_sec(at, ln, dz1 - 110, dz1)
        at.add_patch(Rectangle((ln - P["roller_d"] / 2, dz1 + 4), P["roller_d"], P["roller_h"] - 4,
                               fc="#f2f2ee", ec="k"))
    at.add_patch(Rectangle((L2 - 10, dz1), 20, zc1 - P["aj_gap"] - dz1, fc="none", ec="#C0392B", lw=1.4, ls="--"))
    dim(at, P["DZ"] + 10, dz1, P["DZ"] + 10, zc0, f"{zc0 - dz1:.0f}", vert=True, fs=8)
    dim(at, P["DZ"] + 45, zc0, P["DZ"] + 45, zc1, f"lòng máng {zc1 - zc0:.0f}", vert=True, fs=8)
    dim(at, -20, zc0, -20, dz1 + P["roller_h"], f"ăn khớp {dz1 + P['roller_h'] - zc0:.0f}", vert=True, fs=8)
    dim(at, -55, dz1 + P["roller_h"], -55, zc1, f"nâng lắp {zc1 - dz1 - P['roller_h']:.0f}", vert=True, fs=8)
    at.text(P["DZ"] / 2, dz1 - 150,
            f"Bánh dẫn hướng trên Ø{P['roller_d']} trục đứng: không chịu tải, giữ cánh thẳng đứng.\n"
            f"Lắp: nâng cánh, đẩy bánh trên vào máng, hạ bánh dưới lên gờ.\n"
            f"Khóa chống nhảy (nét đỏ) vặn lên sau khi lắp: khe còn {P['aj_gap']} < {P['lift_off']}\n"
            "(độ nâng để bánh dưới thoát gờ) → không nhấc cánh ra được.",
            ha="center", fontsize=8)
    at.set_xlim(-120, P["DZ"] + 100); at.set_ylim(dz1 - 210, hz + 25); at.set_aspect("equal"); at.axis("off")
    at.set_title("MẶT CẮT RAY TRÊN – dẫn hướng + chống nhảy", fontsize=11)
    # 1 canh: vi tri phu kien
    sc = 0.1
    hh = m["DH"] * sc
    ae.add_patch(Rectangle((0, 0), DW, hh, fc="#eee", ec="k"))
    for xe in (0, DW - 15):
        ae.add_patch(Rectangle((xe, 0), 15, hh, fc=C["alu"]))
    for xw in (P["wheel_in"], DW - P["wheel_in"]):
        ae.add_patch(Circle((xw, -8), 18, fc="#f2f2ee", ec="k"))
    ae.text(P["wheel_in"], -40, f"bánh dưới cách mép {P['wheel_in']}", fontsize=7.5, va="top")
    for xr in (P["roller_in"], DW - P["roller_in"]):
        ae.add_patch(Rectangle((xr - 12, hh), 24, 14, fc="#f2f2ee", ec="k"))
    ae.text(P["roller_in"], hh + 25, f"bánh trên cách mép {P['roller_in']}", fontsize=7.5)
    ae.add_patch(Rectangle((DW / 2 - 20, hh), 40, 18, fc="#C0392B"))
    ae.text(DW / 2, hh + 60, "khóa chống nhảy", ha="center", fontsize=7.5, color="#C0392B")
    ae.text(DW / 2, hh / 2, f"Cánh {DW} × {m['DH']}\n(chiều cao vẽ ×0,1)\n\n2 mép: nẹp nhôm U bọc đầu lam\n= tay nắm, chống sứt mép",
            ha="center", va="center", fontsize=8)
    ae.text(DW / 2, -110, "Chặn cuối cao su ở 2 đầu mỗi máng trên.\nRon chổi dán mép chồng mí (chống bụi).",
            ha="center", va="top", fontsize=8)
    ae.set_xlim(-60, DW + 60); ae.set_ylim(-230, hh + 110); ae.set_aspect("equal"); ae.axis("off")
    ae.set_title("PHỤ KIỆN TRÊN 1 CÁNH", fontsize=11)
    fig.savefig(os.path.join(OUT, "12-chi-tiet-ray.png"), dpi=105, bbox_inches="tight")
    plt.close(fig)


def contact():
    names = ["01-mat-truoc-dong-cua", "03-iso-mo-khoang-1-4", "05-iso-mo-khoang-2-3",
             "12-chi-tiet-ray", "10-ban-ve-khung-sat", "11-canh-mat-bang-mat-cat"]
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
    dr.text((10, 8), f"Tủ âm tường cửa lùa 4 cánh – khung sắt + lam sóng {P['lam_w']}x{P['lam_L']}x{P['lam_t']} – "
            f"W={W}, cánh {DW} ({k} thanh), chồng mí {OV:.0f}", fill="black", font=font)
    sheet.save(os.path.join(OUT, "00-contact-sheet.png"))


front_elevation()
door_and_plan()
rail_detail()
kg, tm = bom()
contact()
print("SAT:", {s: round(v, 1) for s, v in tm.items()}, "m; ~%.0f kg" % kg)
print("LAM:", 4 * k, "thanh nguyen cay; canh", DW, "chong mi %.1f" % OV)
print("PLANS OK")
