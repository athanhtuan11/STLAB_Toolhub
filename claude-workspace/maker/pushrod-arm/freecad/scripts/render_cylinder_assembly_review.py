# Anh duyet 2026-10-26 (CLI, matplotlib, khong GUI): xi-lanh Elbow TRUOC / SAU sua "lap duoc".
#   FreeCADCmd --safe-mode fc_cli.py --pass render_cylinder_assembly_review.py <truoc.FCStd> <sau.FCStd> <out.png>
# Hang 1: cat doc truc (y = 0, he xi-lanh). Hang 2: mieng ong (x = mieng - 3) + vien piston (net dut).
# Hang 3: cat z = 2 quanh piston: hoc/ranh dai oc.
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import FreeCAD as App  # noqa: E402
from FreeCAD import Vector as V  # noqa: E402

TAG = "Elbow"
COL = {"Housing": "#7f8c8d", "Piston_rod": "#e67e22", "LK_Nut_M3_piston": "#2980b9", "LK_Threaded_rod_M3": "#27ae60"}


def parts(path):
    doc = App.openDocument(path)
    O = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
    F = O["Piston_rod_" + TAG].Placement
    out = {}
    for k in COL:
        lbl = [l for l in O if l.startswith(k) and l.endswith(TAG)][0]
        s = O[lbl].Shape.copy()
        s.Placement = F.inverse().multiply(s.Placement)
        out[k] = s
    App.closeDocument(doc.Name)
    return out


def draw(ax, shape, n, d, ij, color, ls="-", lw=1.2):
    for w in shape.slice(n, d):
        p = w.discretize(Deflection=0.02)
        ax.plot([q[ij[0]] for q in p], [q[ij[1]] for q in p], ls, color=color, lw=lw)


def panel(ax, P, row, title):
    hs = P["Housing"]
    xm = hs.BoundBox.XMax
    rod = P["Piston_rod"]
    if row == 0:
        for k, s in P.items():
            draw(ax, s, V(0, 1, 0), 0.0, (0, 2), COL[k])
        ax.set_xlim(15, xm + 25); ax.set_ylim(-14, 14); ax.set_xlabel("x (mm, doc truc)"); ax.set_ylabel("z (mm)")
    elif row == 1:
        x = xm - 3.0
        draw(ax, hs, V(1, 0, 0), x, (1, 2), COL["Housing"], lw=1.6)
        draw(ax, rod, V(1, 0, 0), x, (1, 2), COL["Piston_rod"])
        bb = P["LK_Nut_M3_piston"].BoundBox       # piston = quanh dai oc
        draw(ax, rod, V(1, 0, 0), (bb.XMin + bb.XMax) / 2 - 2.5, (1, 2), "#c0392b", "--", 1.4)
        ax.set_xlim(-10, 10); ax.set_ylim(-10, 10); ax.set_xlabel("y (mm)"); ax.set_ylabel("z (mm)")
        ax.text(-9.5, -9.4, "xam: mieng ong x %.1f | cam: ty | do net dut: tiet dien piston" % x, fontsize=8)
    else:
        bb = P["LK_Nut_M3_piston"].BoundBox
        for k in ("Housing", "Piston_rod", "LK_Nut_M3_piston", "LK_Threaded_rod_M3"):
            draw(ax, P[k], V(0, 0, 1), 2.0, (0, 1), COL[k])   # z = 2: gan mat phang dai oc (z = 0 goc luc giac lo ra 2 mat)
        xc = (bb.XMin + bb.XMax) / 2
        ax.set_xlim(xc - 12, xc + 12); ax.set_ylim(-6, 6); ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm, +y = mat tren khi in)")
    ax.set_aspect("equal"); ax.grid(alpha=0.3); ax.set_title(title, fontsize=10)


before, after, out = sys.argv[1], sys.argv[2], sys.argv[3]
PB, PA = parts(before), parts(after)
fig, axs = plt.subplots(3, 2, figsize=(16, 15))
titles = [("TRUOC: piston 6 x 10,4 lon hon bac mieng ong -> nhot", "SAU: long ong thang 6,6 x 8,6, ty 6 x 8 truot vao tu mieng"),
          ("TRUOC: mieng ong 6,6 x 8,6 < piston (net dut)", "SAU: ca ty (ke ca doan piston) lot mieng ong, khe 0,3"),
          ("TRUOC (cat z = 2): hoc dai oc KIN quanh dai oc -> nhot",
           "SAU (cat z = 2): ranh ho mat +y -> truot dai oc vao; trong ong thanh +y giu lai")]
for r in range(3):
    panel(axs[r][0], PB, r, titles[r][0])
    panel(axs[r][1], PA, r, titles[r][1])
fig.suptitle("pushrod-arm xi-lanh %s - kiem LAP DUOC (2026-10-26). Xam: Housing, cam: Piston_rod, xanh duong: dai oc M3, "
             "xanh la: ty ren M3" % TAG, fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.97))
fig.savefig(out, dpi=110)
print("saved", out)
