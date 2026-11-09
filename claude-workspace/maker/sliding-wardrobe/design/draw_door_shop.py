"""Ban ve gia cong canh: KHUNG CANH rieng + LAM SONG rieng (so lay tu parts.json – build_wardrobe.py xuat).

Chay: python draw_door_shop.py
Xuat: renders/15-khung-canh.png, renders/16-lam-song.png, door-cut-list.csv
Toa do tren ban ve: x tu mep TRAI canh (nhin tu TRUOC), z tu MEP DUOI canh (day ong vien duoi).
"""
import csv, io, json, os, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
m = json.load(open(os.path.join(HERE, "parts.json"), encoding="utf-8"))["meta"]
P = m["P"]
DWS, DX0, KB = m["DWS"], m["DX0"], m["KB"]
FW, FDP, DHD, DH = m["FW"], m["FDP"], m["DHD"], m["DH"]
dz0 = m["dz"][0]
LW, LT = P["lam_w"], P["lam_t"]
GS, GE = P["lam_gap_side"], P["lam_gap_end"]
RB_D, RB_W = P["rail_back"][0], P["rail_back"][1]
NRB = P["n_rail_back"]
ZL0 = FW + GE                                    # mep duoi lam (tu day canh)
RAILS = [ZL0 + (n + 0.5) * DH / NRB for n in range(NRB)]     # tam giang sau
ZLK = m["Z_LOCK"] - dz0                          # cao khoa tu day canh
SKIRT_H = dz0 + FW - P["skirt_gap"]
STEEL, LAM, RED, BLUE = "#2B2D30", "#8B6A4F", "#C0392B", "#1F6FB2"


def save(fig, name):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    path = os.path.join(OUT, name)
    for _ in range(10):
        try:
            open(path, "wb").write(buf.getvalue())
            return
        except OSError:
            time.sleep(1)
    open(path.replace(".png", "-moi.png"), "wb").write(buf.getvalue())


def dim(ax, x0, y0, x1, y1, txt, off=0, vert=False, fs=7, c="k"):
    if vert:
        ax.annotate("", (x0 + off, y0), (x0 + off, y1), arrowprops=dict(arrowstyle="<->", lw=0.6, color=c))
        ax.text(x0 + off - 12, (y0 + y1) / 2, txt, rotation=90, ha="right", va="center", fontsize=fs, color=c)
    else:
        ax.annotate("", (x0, y0 + off), (x1, y0 + off), arrowprops=dict(arrowstyle="<->", lw=0.6, color=c))
        ax.text((x0 + x1) / 2, y0 + off + 10, txt, ha="center", va="bottom", fontsize=fs, color=c)


def door_holes(i):
    """Lo/phu kien rieng cua canh i (toa do canh). Tra list (loai, x, z, ghi chu)."""
    dw = DWS[i]
    h = [("TR", P["roller_in"], DHD, "tán rút ren M8 – con lăn trên"),
         ("TR", dw - P["roller_in"], DHD, "tán rút ren M8 – con lăn trên"),
         ("CN", dw / 2, DHD, "tán rút ren M8 – khóa chống nhảy + chốt bi"),
         ("CB", P["wheel_in"], 0, "càng bánh dưới"), ("CB", dw - P["wheel_in"], 0, "càng bánh dưới")]
    for L in m["LOCKS"]:
        if L["front"] == i:
            h.append(("KH", L["x"] - DX0[i], ZLK, f"khóa ấn: lỗ Ø{P['lock_d']} xuyên lam, thân bắt giằng 2"))
        if L["back"] == i:
            h.append(("LB", L["x"] - DX0[i], ZLK, f"lỗ Ø{P['plunger_d'] + 2} mặt TRƯỚC viền đứng – bắt chốt khóa"))
    return h


# =====================================================================  SHEET A: KHUNG CANH
def frame_elev(ax, i, title):
    dw = DWS[i]
    # vien (cat xien 45)
    poly = lambda pts: ax.add_patch(Polygon(pts, closed=True, fc=STEEL, ec="w", lw=0.6))
    poly([(0, 0), (dw, 0), (dw - FW, FW), (FW, FW)])                     # ngang duoi
    poly([(0, DHD), (dw, DHD), (dw - FW, DHD - FW), (FW, DHD - FW)])     # ngang tren
    poly([(0, 0), (FW, FW), (FW, DHD - FW), (0, DHD)])                   # dung trai
    poly([(dw, 0), (dw - FW, FW), (dw - FW, DHD - FW), (dw, DHD)])       # dung phai
    for n, zc in enumerate(RAILS):
        ax.add_patch(Rectangle((FW, zc - RB_W / 2), dw - 2 * FW, RB_W, fc="#666", ec="k", lw=0.5))
        ax.text(dw / 2, zc + RB_W / 2 + 8, f"③ giằng {n + 1}", ha="center", fontsize=6.5)
        dim(ax, dw, 0, dw, zc, f"{zc:.0f}", off=40 + 38 * n, vert=True, fs=6.5)
    ax.add_patch(Rectangle((0, -(dz0 - P["skirt_gap"])), dw, SKIRT_H, fc="none", ec=STEEL, ls="--", lw=0.8))
    ax.text(dw / 2, -(dz0 - P["skirt_gap"]) / 2, f"⑤ tấm che chân (mặt trước) {dw}×{SKIRT_H:.0f}", ha="center",
            va="center", fontsize=6.5)
    for kind, x, z, note in door_holes(i):
        if kind == "TR":
            ax.add_patch(Circle((x, z + 12), 9, fc="#ddd", ec="k"))
        elif kind == "CN":
            ax.add_patch(Rectangle((x - 12, z), 24, 14, fc=RED, ec="k"))
        elif kind == "CB":
            ax.add_patch(Rectangle((x - 30, -P["wheel_bracket"] - P["wheel_d"]), 60, P["wheel_d"] + P["wheel_bracket"],
                                   fc="#999", ec="k", lw=0.6))
            ax.add_patch(Circle((x, -P["wheel_bracket"] - P["wheel_d"] / 2), P["wheel_d"] / 2, fc="#DADDE0", ec="k"))
        elif kind == "KH":
            ax.add_patch(Circle((x, z), 16, fc="none", ec=BLUE, lw=1.6))
            ax.text(x, z - 45, f"khóa x={x:.0f}\nz={z:.0f}", ha="center", va="top", fontsize=6.5, color=BLUE)
        elif kind == "LB":
            ax.add_patch(Circle((x, z), 9, fc=BLUE, ec="k"))
            ax.text(x + (25 if x < dw / 2 else -25), z, f"lỗ Ø10\nz={z:.0f}", ha="left" if x < dw / 2 else "right",
                    va="center", fontsize=6.5, color=BLUE)
    dim(ax, 0, DHD, dw, DHD, f"{dw}", off=55, fs=8)
    dim(ax, 0, 0, 0, DHD, f"{DHD:.0f}", off=-40, vert=True, fs=8)
    dim(ax, 0, -P["wheel_d"] - 25, P["wheel_in"], -P["wheel_d"] - 25, f"{P['wheel_in']}", fs=6.5)
    dim(ax, 0, DHD + 25, P["roller_in"], DHD + 25, f"{P['roller_in']}", fs=6.5)
    ax.text(FW / 2, DHD / 2, "① viền đứng", rotation=90, color="w", ha="center", va="center", fontsize=6.5)
    ax.text(dw / 2, DHD - FW / 2, "② viền ngang trên", color="w", ha="center", va="center", fontsize=6)
    ax.text(dw / 2, FW / 2, "② viền ngang dưới", color="w", ha="center", va="center", fontsize=6)
    ax.set_xlim(-170, dw + 230); ax.set_ylim(-230, DHD + 170); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=11)


def sheet_frame():
    fig = plt.figure(figsize=(24, 15))
    a1 = fig.add_axes([0.00, 0.30, 0.20, 0.66])
    a2 = fig.add_axes([0.20, 0.30, 0.17, 0.66])
    frame_elev(a1, 1, f"CÁNH 4 THANH (C2, C3) – {DWS[1]}×{DHD:.0f}\nnhìn từ TRƯỚC – lỗ vẽ theo C2 (C3: bảng D)")
    frame_elev(a2, 0, f"CÁNH 3 THANH (C1, C4) – {DWS[0]}×{DHD:.0f}\nnhìn từ TRƯỚC – lỗ vẽ theo C1 (C4: bảng D)")
    # ---- chi tiet
    d1 = fig.add_axes([0.39, 0.66, 0.14, 0.28])     # goc xien
    d1.add_patch(Polygon([(0, 0), (120, 0), (100, 20), (20, 20)], fc=STEEL, ec="w"))
    d1.add_patch(Polygon([(0, 0), (20, 20), (20, 120), (0, 120)], fc="#444", ec="w"))
    d1.plot([0, 20], [0, 20], c=RED, lw=2)
    d1.text(60, -18, "② cắt xiên 45°", ha="center", fontsize=8)
    d1.text(-8, 70, "① xiên 45°", rotation=90, ha="right", va="center", fontsize=8)
    d1.text(60, 75, "Hàn kín mối xiên (đỏ)\ncả 4 mặt, mài phẳng.\nĐo 2 đường chéo\nlệch ≤ 2 mới hàn chết.",
            fontsize=8, va="center")
    d1.set_xlim(-30, 190); d1.set_ylim(-35, 135); d1.set_aspect("equal"); d1.axis("off")
    d1.set_title("A. Góc viền", fontsize=10)

    d2 = fig.add_axes([0.54, 0.66, 0.20, 0.28])     # mat cat ngang canh tai giang
    d2.add_patch(Rectangle((0, 0), FW, FDP, fc=STEEL)); d2.add_patch(Rectangle((1.2, 1.2), FW - 2.4, FDP - 2.4, fc="w"))
    d2.add_patch(Rectangle((FW + GS, FDP - RB_D - LT), 150, LT, fc=LAM, ec="k", lw=0.5))
    d2.add_patch(Rectangle((FW, FDP - RB_D), 160, RB_D, fc="#666", ec="k", lw=0.5))
    d2.plot([FW + GS + 55, FW + GS + 55], [FDP + 6, FDP - RB_D - 14], c=RED, lw=1.5)
    d2.text(FW + GS + 60, FDP + 10, "vít 4×25 bắt từ SAU, xuyên giằng vào lam\n(khoan mồi Ø3, không lòi mặt trước)",
            fontsize=7.5, color=RED)
    dim(d2, -8, 0, -8, FDP, f"dày cánh {FDP}", vert=True, fs=7)
    dim(d2, 0, -6, FW, -6, f"{FW}", fs=7)
    d2.text(90, -14, f"mặt TRƯỚC (lam lùi {FDP - RB_D - LT:.0f})", ha="center", fontsize=7.5)
    d2.text(90, FDP + 30, "mặt SAU (trong tủ)", ha="center", fontsize=7.5)
    d2.text(FW / 2, FDP / 2, "①", color="w", ha="center", va="center", fontsize=8)
    d2.text(100, FDP - RB_D / 2, f"③ giằng {RB_D}×{RB_W}", color="w", ha="center", va="center", fontsize=7)
    d2.text(100, FDP - RB_D - LT / 2, f"lam {LT}", color="w", ha="center", va="center", fontsize=7)
    d2.set_xlim(-45, 190); d2.set_ylim(-30, FDP + 45); d2.set_aspect("equal"); d2.axis("off")
    d2.set_title("B. Mặt cắt ngang tại giằng (nhìn từ trên)", fontsize=10)

    d3 = fig.add_axes([0.76, 0.62, 0.23, 0.34])     # cang banh
    wd, wt = P["wheel_d"], P["wheel_t"]
    sp = wt + 4
    d3.add_patch(Rectangle((-30, 0), 60 + 10, FW, fc=STEEL)); d3.text(5, FW / 2, "② viền dưới 20×40", color="w",
                                                                   ha="center", va="center", fontsize=7)
    d3.add_patch(Rectangle((-30, -wd - 8), 60, wd + 8, fc="#999", ec="k"))
    d3.add_patch(Circle((0, -8 - wd / 2), wd / 2, fc="#DADDE0", ec="k"))
    d3.add_patch(FancyBboxPatch((-4, -8 - wd / 2 - 6), 8, 12, boxstyle="round,pad=0.5", fc="w", ec="k"))
    d3.text(45, -8 - wd / 2, "lỗ trục ô van ±5\n(chỉnh cao)", fontsize=7.5, va="center")
    d3.text(0, -wd - 30, "NHÌN NGANG (dọc cánh)", ha="center", fontsize=7.5)
    ox = 130
    d3.add_patch(Rectangle((ox - FDP / 2, 0), FDP, FW, fc=STEEL))
    for s in (-1, 1):
        d3.add_patch(Rectangle((ox + s * sp / 2 - (3 if s < 0 else 0), -wd - 8), 3, wd + 8, fc="#999", ec="k"))
    d3.add_patch(Rectangle((ox - wt / 2, -8 - wd), wt, wd, fc="#DADDE0", ec="k"))
    d3.plot([ox - sp / 2 - 8, ox + sp / 2 + 8], [-8 - wd / 2] * 2, c="k", lw=2)
    d3.text(ox, -wd - 30, "NHÌN TỪ ĐẦU CÁNH", ha="center", fontsize=7.5)
    dim(d3, ox - sp / 2, 15 + FW, ox + sp / 2, 15 + FW, f"{sp} (bánh {wt} + 2 long đền)", fs=7)
    d3.text(70, -wd - 55, f"④ Càng bánh: 2 bản mã 3×30×{wd + 8 + 10} hàn ĐÁY viền dưới, đúng tâm cánh.\n"
            f"Bu lông trục xuyên 2 bản mã (cỡ theo lỗ bánh – TODO). Bánh Ø{wd}×{wt} rãnh U.\n"
            f"Tâm càng cách mép cánh {P['wheel_in']}.", ha="center", va="top", fontsize=7.5)
    d3.set_xlim(-60, 230); d3.set_ylim(-150, 60); d3.set_aspect("equal"); d3.axis("off")
    d3.set_title("C. Càng bánh dưới", fontsize=10)

    d4 = fig.add_axes([0.39, 0.33, 0.30, 0.30])     # bang lo tung canh
    d4.axis("off")
    rows = [["Cánh", "Ray", "Số thanh", "Rộng", "Lỗ / phụ kiện riêng (x từ mép trái, z từ đáy cánh)"]]
    for i in range(4):
        extra = []
        for kind, x, z, note in door_holes(i):
            if kind in ("KH", "LB"):
                extra.append(f"{'KHÓA' if kind == 'KH' else 'lỗ chốt'} x={x:.0f} z={z:.0f}")
        rows.append([f"C{i + 1}", "ngoài" if i % 2 == 0 else "trong", str(KB[i]), str(DWS[i]),
                     "; ".join(extra) if extra else "–"])
    t = d4.table(cellText=rows, loc="upper center", cellLoc="left", colWidths=[0.07, 0.08, 0.09, 0.08, 0.68])
    t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.8)
    d4.text(0.0, 0.25,
            "Chung cho mọi cánh:\n"
            f"• 2 tán rút ren M8 trên mặt trên viền trên, cách mép {P['roller_in']} (con lăn 608 Ø{P['roller_d']}).\n"
            "• 1 tán rút ren M8 giữa viền trên (khóa chống nhảy + vít bi lò xo).\n"
            f"• 2 càng bánh dưới cách mép {P['wheel_in']}; tấm che chân hàn mặt trước viền dưới.\n"
            "• Lỗ khóa/lỗ chốt: khoan SAU khi treo cánh, theo vị trí thực tế (bảng trên là vị trí thiết kế).",
            fontsize=8.5, va="top", transform=d4.transAxes)
    d4.set_title("D. Lỗ & phụ kiện từng cánh", fontsize=10)

    # ---- bang cat sat
    d5 = fig.add_axes([0.71, 0.33, 0.28, 0.27]); d5.axis("off")
    cl = cut_rows()
    t2 = d5.table(cellText=[["#", "Chi tiết", "Vật liệu", "Dài", "Cắt", "SL"]] + cl, loc="upper center",
                  cellLoc="left", colWidths=[0.06, 0.30, 0.22, 0.11, 0.17, 0.08])
    t2.auto_set_font_size(False); t2.set_fontsize(8.5); t2.scale(1, 1.6)
    d5.set_title("E. Bảng cắt sắt cho 4 cánh", fontsize=10)

    fig.text(0.01, 0.27,
             "TRÌNH TỰ GIA CÔNG 1 CÁNH\n"
             "1. Cắt ① ② xiên 45° (máy cắt bàn, kẹp ê-ke). Cắt ③ vuông, ⑤ theo bảng.\n"
             "2. Đặt ① ② lên mặt phẳng, kẹp ê-ke 4 góc → hàn đính → đo 2 đường chéo (lệch ≤ 2) → hàn kín, so le mặt trước/sau.\n"
             f"3. Hàn 4 giằng ③ áp mặt SAU (mặt sau giằng phẳng mặt sau viền), tâm tại z = {', '.join(f'{z:.0f}' for z in RAILS)}.\n"
             "4. Hàn 2 càng bánh ④ dưới đáy viền dưới (đúng tâm chiều dày cánh). Hàn ⑤ che chân mặt trước.\n"
             "5. Khoan + rút 3 tán ren M8 ở viền trên. Khoan mồi Ø3 trên giằng cho vít bắt lam (xem tờ LAM SÓNG).\n"
             "6. Mài mối hàn → sơn lót chống gỉ → sơn đen mờ. KHÔ HẲN mới bắt lam.",
             fontsize=10, va="top")
    fig.suptitle(y=1.02, t="BẢN VẼ GIA CÔNG – KHUNG CÁNH (sắt hộp 20×40×1,2 đặt nằm, giằng 13×26×1,0) – mm", fontsize=14)
    save(fig, "15-khung-canh.png")
    plt.close(fig)


def cut_rows():
    n3, n4 = KB.count(3), KB.count(4)
    w3, w4 = DWS[KB.index(3)], DWS[KB.index(4)]
    return [["①", "viền đứng", "hộp 20×40×1,2", f"{DHD:.0f}", "xiên 45° 2 đầu", str(2 * 4)],
            ["②", "viền ngang (cánh 4 thanh)", "hộp 20×40×1,2", f"{w4}", "xiên 45° 2 đầu", str(2 * n4)],
            ["②", "viền ngang (cánh 3 thanh)", "hộp 20×40×1,2", f"{w3}", "xiên 45° 2 đầu", str(2 * n3)],
            ["③", "giằng sau (cánh 4 thanh)", f"hộp {RB_D}×{RB_W}×1,0", f"{w4 - 2 * FW}", "vuông", str(NRB * n4)],
            ["③", "giằng sau (cánh 3 thanh)", f"hộp {RB_D}×{RB_W}×1,0", f"{w3 - 2 * FW}", "vuông", str(NRB * n3)],
            ["④", "bản mã càng bánh", "thép tấm 3×30", f"{P['wheel_d'] + 18}", "vuông + lỗ ô van", str(2 * 2 * 4)],
            ["⑤", "che chân (cánh 4 thanh)", f"la/tôn 3×{SKIRT_H:.0f}", f"{w4}", "vuông", str(n4)],
            ["⑤", "che chân (cánh 3 thanh)", f"la/tôn 3×{SKIRT_H:.0f}", f"{w3}", "vuông", str(n3)]]


# =====================================================================  SHEET B: LAM SONG
def sheet_lam():
    fig = plt.figure(figsize=(24, 15))
    # profile
    a0 = fig.add_axes([0.01, 0.70, 0.30, 0.25])
    pitch = LW / P["lam_waves"]
    base = 12
    a0.add_patch(Rectangle((0, 0), LW, base, fc=LAM, ec="k"))
    for k in range(P["lam_waves"]):
        cx = pitch / 2 + k * pitch
        a0.add_patch(plt.matplotlib.patches.Wedge((cx, base), pitch / 2 - 2, 0, 180, fc=LAM, ec="k"))
    for k in range(5):
        a0.add_patch(Rectangle((8 + k * 43, 2), 30, base - 4, fc="#5a4030", ec="none"))
    dim(a0, 0, -8, LW, -8, f"{LW}", fs=8)
    dim(a0, LW + 8, 0, LW + 8, LT, f"{LT}", vert=True, fs=8, off=20)
    a0.text(LW / 2, -40, f"Lam WPC ngoài trời {LW}×{LT}×{DH}, {P['lam_waves']} sóng (hình minh họa – TODO theo thanh thật:\n"
            "số sóng, kiểu ghép âm dương, lõi rỗng). Mặt SAU phẳng tì lên giằng.", ha="center", va="top", fontsize=8.5)
    a0.set_xlim(-30, LW + 60); a0.set_ylim(-80, LT + 40); a0.set_aspect("equal"); a0.axis("off")
    a0.set_title("A. Mặt cắt thanh lam (minh họa)", fontsize=10)

    def lam_elev(ax, i, title):
        dw = DWS[i]
        ax.add_patch(Rectangle((0, 0), dw, DHD, fc="none", ec=STEEL, lw=3))
        for j in range(KB[i]):
            x0 = FW + GS + j * LW
            ax.add_patch(Rectangle((x0, ZL0), LW, DH, fc=LAM, ec="k", lw=0.6, alpha=0.9))
            ax.text(x0 + LW / 2, ZL0 + DH - 120, f"L{j + 1}", ha="center", fontsize=10, color="w", weight="bold")
            for zc in RAILS:          # vit tu sau (bo vit trung than khoa)
                for sx in (55, LW - 55):
                    if any(k == "KH" and abs(x - (x0 + sx)) < 35 and abs(z - zc) < 30
                           for k, x, z, _ in door_holes(i)):
                        ax.plot(x0 + sx, zc, marker="o", mfc="none", c="#999", ms=7)
                        continue
                    ax.plot(x0 + sx, zc, marker="x", c=RED, ms=6, mew=1.5)
        for zc in RAILS:
            ax.plot([FW, dw - FW], [zc, zc], c="#ccc", lw=0.6, ls=":")
        for kind, x, z, note in door_holes(i):
            if kind == "KH":
                j = int((x - FW - GS) // LW)
                xl = x - FW - GS - j * LW
                ax.add_patch(Circle((x, z), P["lock_d"] / 2 * 1.6, fc="w", ec=BLUE, lw=2))
                ax.text(x, z - 60, f"Ø{P['lock_d']} trên L{j + 1}\ncách mép trái thanh {xl:.0f}\ncách đáy thanh {z - ZL0:.0f}",
                        ha="center", va="top", fontsize=7, color=BLUE, bbox=dict(fc="w", ec="none", alpha=0.85))
        dim(ax, 0, DHD, dw, DHD, f"{dw}", off=40, fs=8)
        dim(ax, FW + GS, 0, FW + GS + LW, 0, f"{LW}", off=-45, fs=7)
        dim(ax, 0, ZL0, 0, ZL0 + DH, f"lam {DH} (nguyên cây)", off=-35, vert=True, fs=7)
        ax.set_xlim(-120, dw + 60); ax.set_ylim(-110, DHD + 110); ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(title, fontsize=10)

    pos = [(0.33, 0.30, 0.15, 0.66), (0.48, 0.30, 0.17, 0.66), (0.65, 0.30, 0.17, 0.66), (0.82, 0.30, 0.15, 0.66)]
    for i in range(4):
        ax = fig.add_axes(list(pos[i]))
        lam_elev(ax, i, f"C{i + 1} – {KB[i]} thanh, ray {'ngoài' if i % 2 == 0 else 'trong'}\nnhìn từ TRƯỚC")

    a9 = fig.add_axes([0.01, 0.30, 0.30, 0.38]); a9.axis("off")
    n_v = sum(KB) * NRB * 2 - 3
    a9.text(0, 1,
            "B. QUY CÁCH\n"
            f"• Tổng {sum(KB)} thanh {LW}×{LT}×{DH} – KHÔNG CẮT ngắn, không xẻ dọc.\n"
            f"• Lọt trong viền: khe {GS} mỗi bên, {GE} mỗi đầu (giãn nở WPC – TODO theo hãng).\n"
            f"• Thanh L1 sát viền trái; các thanh ghép sát nhau theo âm dương.\n"
            "• Tất cả thanh cùng chiều sóng, cùng mặt (đánh dấu đầu TRÊN bằng bút chì trước khi lắp).\n\n"
            "C. BẮT VÍT (dấu × đỏ)\n"
            f"• Vít bắt từ MẶT SAU xuyên giằng 13×26 vào lam: {NRB} giằng × 2 vít/thanh\n"
            f"  = {NRB * 2} vít/thanh, tổng {n_v} vít.\n"
            "• Vị trí: cách 2 mép thanh 55, tại tâm mỗi giằng.\n"
            "• Chỗ có khóa (C1-L3, C3-L1, C3-L4 ở giằng 2): BỎ vít (vòng xám),\n"
            "  thân khóa đã ép lam vào giằng.\n"
            "• Vít tự khoan đầu dù 4×25 (TODO thử 1 vít: không lòi mặt trước).\n"
            "• Khoan mồi Ø3 vào lam, siết vừa tay (WPC dễ toét lỗ).\n\n"
            "D. LỖ KHÓA (chỉ C1, C3)\n"
            f"• Khoan Ø{P['lock_d']} (mũi khoét) xuyên lam đúng vị trí khóa (xanh).\n"
            "• Khoan khi lam đã bắt lên khung + cánh đã treo, dóng theo lỗ chốt C2/C4.\n"
            "• Thân khóa bắt vào giằng 2 phía sau.\n\n"
            "E. TRÌNH TỰ\n"
            "1. Khung sơn khô → đặt khung nằm sấp (mặt trước xuống, lót thảm).\n"
            "2. Thả lam vào viền từ phía sau, L1 → L4, chêm khe đều.\n"
            "3. Bắt vít từ sau qua giằng. 4. Lật lại kiểm mặt trước, lau sạch.",
            fontsize=9.5, va="top", transform=a9.transAxes)
    fig.suptitle(y=1.02, t=f"BẢN VẼ GIA CÔNG – LAM SÓNG (lắp vào khung cánh) – mm, z tính từ đáy cánh", fontsize=14)
    save(fig, "16-lam-song.png")
    plt.close(fig)


def write_csv():
    with open(os.path.join(HERE, "door-cut-list.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["ma", "chi_tiet", "vat_lieu", "dai_mm", "cat", "so_luong"])
        for r in cut_rows():
            w.writerow(r)
        w.writerow([])
        w.writerow(["lam", f"lam song {LW}x{LT}x{DH}", "WPC", DH, "khong cat", sum(KB)])
        w.writerow(["vit", "vit tu khoan 4x25 bat lam tu sau", "", "", "", sum(KB) * NRB * 2 - 3])
        w.writerow([])
        w.writerow(["canh", "loai", "x_mm", "z_mm", "ghi_chu"])
        for i in range(4):
            for kind, x, z, note in door_holes(i):
                w.writerow([f"C{i + 1}", kind, round(x, 1), round(z, 1), note])


sheet_frame()
sheet_lam()
write_csv()
print("DOOR SHOP OK", "giang z:", [round(z) for z in RAILS], "khoa z:", round(ZLK))
