"""Ban ve kich thuoc + bang vat tu + contact sheet tu parts.json (build_wardrobe.py xuat).

Chay: python draw_plans.py  (tu design/)
"""
import csv, io, json, math, os, time
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from PIL import Image, ImageDraw, ImageFont

def save(fig, path):
    """Ghi PNG, thu lai neu file dang bi khoa (trinh xem anh/dong bo)."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=105, bbox_inches="tight")
    for _ in range(10):
        try:
            with open(path, "wb") as f:
                f.write(buf.getvalue())
            return
        except OSError:
            time.sleep(1)
    alt = path.replace(".png", "-moi.png")
    open(alt, "wb").write(buf.getvalue())
    print("KHOA FILE, ghi sang", alt)


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
data = json.load(open(os.path.join(HERE, "parts.json"), encoding="utf-8"))
m, parts = data["meta"], data["parts"]
P = m["P"]
W, D, DW, OV, k, H_TOP = P["W"], P["D"], m["DW"], m["OV"], m["k"], m["H_TOP"]
DWS, DX0, OPEN, KB, FW, FDP, DHD = m["DWS"], m["DX0"], m["OPEN"], m["KB"], m["FW"], m["FDP"], m["DHD"]
XL, YM = m["x_lines"], m["y_mid"]
C = {"steel": "#2B2D30", "lam": "#8B6A4F", "board": "#D9C7A6", "rod": "#7D8790", "alu": "#B9BEC3"}
# kg/m tinh tu tiet dien hop (thep 7,85 g/cm3) - do day theo gia dinh, TODO theo hang mua
KGM = {"la3x40": 3 * 40 * 7.85e-3, "13x26": (2 * 39 * 1.0 - 4 * 1.0 ** 2) * 7.85e-3, "40x40": (4 * 40 * 1.4 - 4 * 1.4 ** 2) * 7.85e-3, "40x80": (2 * 120 * 1.4 - 4 * 1.4 ** 2) * 7.85e-3,
       "20x40": (2 * 60 * 1.2 - 4 * 1.2 ** 2) * 7.85e-3,
       "40x80v": (2 * 120 * 1.4 - 4 * 1.4 ** 2) * 7.85e-3}


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
    save(fig, os.path.join(OUT, "10-ban-ve-khung-sat.png"))
    plt.close(fig)


def door_and_plan():
    fig = plt.figure(figsize=(16, 9))
    a0 = fig.add_axes([0.0, 0.05, 0.22, 0.9])
    a1 = fig.add_axes([0.24, 0.45, 0.55, 0.5])
    a2 = fig.add_axes([0.80, 0.05, 0.2, 0.9])
    # 1 canh: tam nhua phu mat truoc, khung (net dut trang) phia sau
    PW = P["panel_w"]
    for j in range(k):
        a0.add_patch(Rectangle((j * PW, 0), PW, DHD, fc=C["lam"], ec="k", lw=0.6))
    for x0_, w_ in [(0, FW), (DW - FW, FW)]:
        a0.add_patch(Rectangle((x0_, 0), w_, DHD, fc="none", ec="w", ls="--", lw=0.8))
    for zr in m["HR_Z"]:
        a0.add_patch(Rectangle((FW, zr - m["dz"][0] - P["h_rail"][1] / 2), DW - 2 * FW, P["h_rail"][1], fc="none", ec="w", ls="--", lw=0.8))
    a0.add_patch(Rectangle((0, 0), DW, FW, fc="none", ec="w", ls="--", lw=0.8))
    a0.add_patch(Rectangle((0, DHD - FW), DW, FW, fc="none", ec="w", ls="--", lw=0.8))
    dim(a0, 0, DHD, DW, DHD, f"{DW} = {k} tấm × {PW}", off=80, fs=7)
    dim(a0, 0, 0, 0, DHD, f"{DHD:.0f} = dài tấm nhựa", off=-60, vert=True, fs=7)
    a0.text(DW / 2, -150, f"Tấm nhựa {PW}×{P['panel_L']}×{P['panel_t']} bắt vít lên mặt trước khung\n"
            f"khung: viền hộp 20×40 nằm + {P['h_rails']} thanh ngang 20×40 nằm (móc hèm bắt vào)\n"
            f"2 cánh giống nhau = {min(DWS)}; 2 cụm bánh dưới đáy", ha="center", fontsize=8)
    a0.set_xlim(-320, DW + 100); a0.set_ylim(-380, DHD + 250); a0.set_aspect("equal"); a0.axis("off")
    a0.set_title(f"CÁNH {k} TẤM NHỰA (nhìn trước)", fontsize=11)
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
        yl = m["YF"][i % 2]
        x0, dwi = DX0[i], DWS[i]
        a1.add_patch(Rectangle((x0, yl), dwi, m["DT"], fc=C["lam"], ec="k", lw=0.5, alpha=0.9))
        a1.add_patch(Rectangle((x0, yl + m["PT"]), FW, FDP, fc=C["steel"]))
        a1.add_patch(Rectangle((x0 + dwi - FW, yl + m["PT"]), FW, FDP, fc=C["steel"]))
        a1.text(x0 + dwi / 2, -40 if front else 150, f"Cánh {i + 1}: {KB[i]} tấm, {DWS[i]} – ray {'ngoài' if front else 'trong'}",
                ha="center", fontsize=7)
    for b, spec in enumerate(m["BAYS"]):
        a1.text((XL[b] + XL[b + 1]) / 2, D / 2 + 60, spec["name"], ha="center", fontsize=8)
    a1.plot([0, W], [YM, YM], ls=":", c="#1a4d80", lw=1)
    a1.text(W / 2, YM - 30, f"tim ống treo – cách mặt trong khung {YM - P['DZ']:.0f}", ha="center", fontsize=7,
            color="#1a4d80")
    dim(a1, DX0[1], -150, DWS[0], -150, f"chồng mí {OV:.0f}", off=0, fs=7)
    dim(a1, W, 0, W, P["DZ"], f"ray {P['DZ']}", off=170, vert=True, fs=7)
    dim(a1, W, 0, W, D, f"sâu {D}", off=280, vert=True, fs=7)
    a1.set_xlim(-200, W + 350); a1.set_ylim(-300, D + 150); a1.invert_yaxis()
    a1.set_aspect("equal"); a1.axis("off")
    a1.set_title("MẶT BẰNG (mặt trước ở trên) – cột trước giữa nấp sau chỗ chồng mí; 2 khung lửng không cột trước", fontsize=11)
    a1.text(0, D + 330, f"Lùa 1 cánh hết cỡ: mở nửa trái {OPEN[0]:.0f} hoặc nửa phải {OPEN[1]:.0f}. Ray dưới: 2 thanh U chấn 40x40 tường–tường", fontsize=9)
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
        a2.add_patch(Rectangle((ln - FDP / 2 - m["PT"], m["dz"][0]), FDP + m["PT"], DHD, fc=C["lam"], alpha=0.8))
    a2.set_xlim(-100, D + 150); a2.set_ylim(-50, H_TOP + 150); a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("MẶT CẮT khoang 2 tầng", fontsize=11)
    save(fig, os.path.join(OUT, "11-canh-mat-bang-mat-cat.png"))
    plt.close(fig)


BAR_KGM = {"Sat hop 40x40": KGM["40x40"], "Sat hop 20x40": KGM["20x40"],
           "U chan 40x40x2.0": (40 + 2 * 38) * 2.0 * 7.85e-3}


def bars_6m(stock=6000, kerf=3):
    """So cay 6 m moi loai sat (first-fit decreasing). Tra {loai: (so cay, tong dai mm, so do cat tung cay)}."""
    cuts = {}
    for pt in parts:
        k = pt["kind"]
        spec = ("Sat hop " + pt["spec"]) if k in ("steel", "dframe") else \
               "Sat hop 20x40" if k in ("be-joist", "be-strip") else \
               f"U chan {P['U'][0]}x{P['U'][1]}x{P['U'][2]}" if k in ("utrack", "utrack-top") else None
        if spec:
            cuts.setdefault(spec, []).append(pt["L"])
    out = {}
    for spec, L in sorted(cuts.items()):
        bins = []
        for x in sorted(L, reverse=True):
            for b in bins:
                if sum(b) + kerf * len(b) + x <= stock:
                    b.append(x)
                    break
            else:
                bins.append([x])
        plan = []
        for b in bins:
            c = Counter(b)
            plan.append("+".join(f"{q}x{v:g}" if q > 1 else f"{v:g}" for v, q in sorted(c.items(), reverse=True)))
        out[spec] = (len(bins), sum(L), plan)
    return out


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
        elif pt["kind"] == "panel":
            rows[(f"Tam nhua trong nha {P['panel_w']}x{P['panel_L']}x{P['panel_t']}", P["panel_L"], "mat canh (nguyen tam, khong cat)")] += 1
        elif pt["kind"] == "fascia":
            rows[(f"Tam che ray (cat doc tu tam nhua {P['panel_w']}x{P['panel_L']})", f"{pt['L']} x {pt['Wd']}", "che ray tren/duoi: 1 tam nguyen 2900 + 1 mau sat tuong phai")] += 1
        elif pt["kind"] == "wallbracket":
            rows[(pt["spec"], "", "cot sau - tuong sau (2 do cao)")] += 1
        elif pt["kind"] == "tab":
            rows[(pt["spec"], "", "noi U trong vao 3 cot truoc (duoi mieng U)")] += 1
        elif pt["kind"] == "utrack-top":
            UB, UH, UT = P["U"]
            rows[(pt["spec"], pt["L"], "ray TREN up nguoc, dan huong (bat duoi 5 dau dam dinh)")] += 1
            kg += (UB + 2 * (UH - UT)) * UT * 7.85e-3 * pt["L"] / 1000
        elif pt["kind"] == "stop":
            rows[(pt["spec"], "", "trong ray treo")] += 1
        elif pt["kind"] == "eprof":
            rows[("Nep nhom U boc mep canh (tay nam)", pt["L"], "2 mep moi canh")] += 1
        elif pt["kind"] == "skirt":
            rows[(f"La che chan 3x{pt['Wd']:.0f}", pt["L"], "mat truoc day canh")] += 1
            kg += 3 * pt["Wd"] * 7.85e-3 * pt["L"] / 1000
        elif pt["kind"] == "utrack":
            UB, UH, UT = P["U"]
            rows[(pt["spec"], pt["L"], "ray duoi CHIU TAI, nam ngua, vit dau bang + no xuong san")] += 1
            kg += (UB + 2 * (UH - UT)) * UT * 7.85e-3 * pt["L"] / 1000
        elif pt["kind"] == "be-strip":
            rows[(pt["spec"], pt["L"], "dem giua 2 thanh U (be tu)")] += 1
        elif pt["kind"] == "be-joist":
            rows[("Sat hop 20x40 (dan be, dat nam)", pt["L"], "be tu")] += 1
            kg += KGM["20x40"] * pt["L"] / 1000
        elif pt["kind"] == "be-board":
            rows[(f"Van be {P['be_board']}", f"{pt['L']} x {pt['Wd']}", "mat be tu (khoet lo chan cot)")] += 1
        elif pt["kind"] == "bogie":
            rows[("Cang banh (2 ban ma + truc M8, vit chinh cao) han day vien duoi", "", "2 cum/canh")] += 1
        elif pt["kind"] == "stop-u":
            rows[("Chan cuoi cao su trong long U", "", "2 dau moi thanh U")] += 1
        elif pt["kind"] == "rback":
            rows[("Sat hop 13x26", pt["L"], "giang sau lam (canh)")] += 1
            kg += KGM["13x26"] * pt["L"] / 1000
    path = os.path.join(HERE, "bom.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["vat_tu", "dai_mm", "vi_tri", "so_luong"])
        for (a, L, v), q in sorted(rows.items(), key=lambda r: (r[0][0], str(r[0][1]))):
            w.writerow([a, L, v, q])
        w.writerow([])
        w.writerow(["Banh 608 boc POM O32x12 (hoac banh o bi tuong duong)", "", "4 duoi (truc ngang) + 2 tren (truc dung) / canh", 6 * P["door_n"]])
        w.writerow(["Bulong truc M8 banh duoi", "", "4/canh", 4 * P["door_n"]])
        w.writerow(["Bulong M8 dai ~60 + dai oc khoa + tan rut ren M8 (banh dan huong tren, chinh cao)", "", "2/canh", 2 * P["door_n"]])
        w.writerow(["Vit no dau bang (khoan con) bat U xuong san, ~400 mm/vit", "", "2 thanh U", 2 * (P["W"] // 400 + 1)])
        w.writerow(["Khoa an tu cua lua (push lock)", "", "cho chong mi", len(m["LOCKS"])])
        w.writerow(["Ron choi chong bui (mep chong mi)", m["DH"], "1/canh", P["door_n"]])
        w.writerow(["No M8 xuyen dan be xuong san (thay ban de chan cot)", "", "3 dan be, ~600/cai", 3 * (P["W"] // 600 + 1)])
        w.writerow(["LUU Y", "", f"tai moi banh >= (khoi luong canh / 4) x 1.5 = {m['WHEEL_NEED']:.0f} kg (canh ~{m['DOOR_KG'][0]:.0f} kg voi panel_kg={P['panel_kg']})", ""])
        w.writerow(["Khoi luong sat uoc tinh (kg)", round(kg, 1), "do day 1.4/1.2 gia dinh", ""])
        w.writerow([])
        w.writerow(["TONG HOP CAY 6 M (xep cat FFD, mach cat 3, cat chi tiet Tuan tu theo ban ve)", "", "chi tiet cat", "so cay 6 m"])
        tot = 0.0
        for spec, (n, used, plan) in bars_6m().items():
            kgb = BAR_KGM[spec] * 6
            tot += n * kgb
            w.writerow([spec, round(used / 1000, 1), " | ".join(plan), n, f"{kgb:.1f} kg/cay", f"{n * kgb:.0f} kg"])
        w.writerow(["TONG SAT MUA (cay 6 m)", "", "do day gia dinh: 40x40x1.4, 20x40x1.2, U 40x40x2 - TODO theo hang", "", "", f"{tot:.0f} kg"])
    tube_m = Counter()
    for pt in parts:
        if pt["kind"] in ("steel", "dframe", "rback"):
            tube_m[pt["spec"]] += pt["L"] / 1000
    return kg, tube_m


def contact():
    names = ["01-mat-truoc-dong-cua", "03-iso-mo-nua-trai", "05-iso-mo-nua-phai",
             "12-mat-cat-ray", "13-mat-bang-hanh-trinh", "10-ban-ve-khung-sat"]
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
    dr.text((10, 8), f"Tủ âm tường cửa lùa 2 cánh – bệ 40 + U chấn chịu tải, ray hộp 40x40 bắt dưới đầu dầm đỉnh – cánh tấm nhựa {P['panel_w']}x{P['panel_L']}x{P['panel_t']} – ray U sơn đen – "
            f"W={W}, cánh {'-'.join(map(str, KB))} tấm ({'/'.join(map(str, DWS))}), chồng mí {OV:.0f}", fill="black", font=font)
    sheet.save(os.path.join(OUT, "00-contact-sheet.png"))


front_elevation()
door_and_plan()
kg, tm = bom()
contact()
print("SAT:", {s: round(v, 1) for s, v in tm.items()}, "m; ~%.0f kg" % kg)
print("TAM NHUA:", sum(KB), "tam canh; canh", DWS, "chong mi %.1f" % OV, "mo", [round(o) for o in OPEN])
print("PLANS OK")
