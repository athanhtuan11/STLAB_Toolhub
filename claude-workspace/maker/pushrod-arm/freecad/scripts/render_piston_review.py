# Anh DUYET NHANH xi-lanh piston (2026-10-25) - CLI, khong GUI, khong chia luoi 3D:
# MAT CAT 2D (Shape.slice) qua mat phang giua xi-lanh / mat phang tay, to mau tung chi tiet.
# Tuan 2026-10-25: render 3D matplotlib ca tay (STEP servo, motor) qua lau -> chi cat lat (vai giay).
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode tools/robotics-cad/scripts/fc_cli.py --pass <file nay>
# Ra: freecad/images/review-piston/contact-sheet.png. Chi doc model, khong Luu.
import os
import time
import types

import FreeCAD as App
from FreeCAD import Vector as V
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402

t0 = time.time()
FC = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad"
OUT = os.path.join(FC, "images", "review-piston")
os.makedirs(OUT, exist_ok=True)
App.openDocument(os.path.join(FC, "pushrod_arm.FCStd"))
src = open(os.path.join(FC, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read().split("class Panel", 1)[0]
src = src.replace("import FreeCAD as App, FreeCADGui as Gui, math, json, os", "import FreeCAD as App, math, json, os")
src = src[:src.index("try:\n    from PySide")] + src[src.index("DOC = "):]
G = {"__name__": "sim", "Gui": types.SimpleNamespace(updateGui=lambda: None)}
exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
set_pose, OBJ = G["set_pose"], G["OBJ"]
LMIN, LMAX, L1MAX, L1_0, L2_0 = G["LMIN"], G["LMAX"], G["L1MAX"], G["L1_0"], G["L2_0"]
COL = [("Housing", "#c7ccd6"), ("CB_030", "#3373d9"), ("Gear_z28", "#d92626"), ("Gear_z12", "#f9c21a"),
       ("LK_Nut", "#444"), ("LK_Thread", "#8c8c99"), ("Piston_rod", "#9959bf"), ("Pin_gearbox", "#d92626"),
       ("Boom", "#cc6b26"), ("Forearm", "#cc6b26"), ("Turret", "#d97326"), ("Base", "#404247"), ("Pin_", "#999")]


def col(l): return next((c for k, c in COL if l.startswith(k)), "#b3b3b8")


def draw(ax, labels, F, y, alpha=0.9):
    """Cat moi chi tiet bang mat phang y (he F), ve vung cat (x, z) cua he F."""
    n = F.Rotation.multVec(V(0, 1, 0)); d = n.dot(F.multVec(V(0, y, 0)))
    inv = F.inverse()
    for l in labels:
        s = OBJ[l].Shape
        try:
            wires = s.slice(n, d)
        except Exception:
            continue
        for w in wires:
            pts = [inv.multVec(p) for p in w.discretize(Deflection=0.05)]
            if len(pts) > 2:
                ax.add_patch(Polygon([(p.x, p.z) for p in pts], closed=True, fc=col(l), ec="#222", lw=0.4, alpha=alpha))


fig, axs = plt.subplots(2, 3, figsize=(27, 14))
for row, tag in enumerate(("Elbow", "Shoulder")):
    grp = [l for l in G["ROD1" if tag == "Shoulder" else "ROD2"] if l in OBJ]
    lmax = LMAX if tag == "Elbow" else L1MAX
    for k, (nm, L) in enumerate((("rut het", LMIN), ("duoi het", lmax))):
        set_pose(0, L if tag == "Shoulder" else L1_0, L if tag == "Elbow" else L2_0, 0, update=False)
        F = OBJ["Piston_rod_" + tag].Placement
        F = App.Placement(F.Base - F.Rotation.multVec(V(L - (L1_0 if tag == "Shoulder" else L2_0), 0, 0)), F.Rotation)
        ax = axs[row][k]
        draw(ax, grp, F, 0.0)
        ax.set_aspect("equal"); ax.autoscale(); ax.grid(alpha=.25)
        ax.set_title("%s - %s (L %.0f mm) - mat cat giua xi-lanh" % (tag, nm, L), fontsize=14)
    # mat cat ngang qua tam banh rang (thay z28 -> z12 an khop): cat theo x tai giua banh rang
    ax = axs[row][2]
    set_pose(0, L1_0, L2_0, 0, update=False)
    F = OBJ["Piston_rod_" + tag].Placement
    gb = OBJ["Gear_z12_" + tag].Shape.copy(); gb.transformShape(F.inverse().toMatrix())
    xm = (gb.BoundBox.XMin + gb.BoundBox.XMax) / 2
    n = F.Rotation.multVec(V(1, 0, 0)); d = n.dot(F.multVec(V(xm, 0, 0))); inv = F.inverse()
    for l in grp:
        try:
            ws = OBJ[l].Shape.slice(n, d)
        except Exception:
            continue
        for w in ws:
            pts = [inv.multVec(p) for p in w.discretize(Deflection=0.03)]
            if len(pts) > 2:
                ax.add_patch(Polygon([(p.y, p.z) for p in pts], closed=True, fc=col(l), ec="#222", lw=0.4, alpha=0.9))
    ax.set_aspect("equal"); ax.autoscale(); ax.grid(alpha=.25)
    ax.set_title("%s - cat ngang qua banh rang: z28 (do) -> z12 (vang) + ty ren" % tag, fontsize=14)
fig.suptitle("pushrod-arm - xi-lanh PISTON (motor 030 + z28/z12 + ty ren M3 + piston kep dai oc M3)  -  2026-10-25"
             "\nxam = vo, xanh = hop so 030, tim = piston + ty, xam dam = dai oc / ty ren", fontsize=17)
plt.tight_layout(); fig.savefig(os.path.join(OUT, "cylinders.png"), dpi=70); plt.close(fig)

# toan canh: cat mat phang tay (y = 0 the gioi) o 3 tu the
fig, axs = plt.subplots(1, 3, figsize=(27, 9))
SKIP = {l for l in OBJ if l.startswith("M2_5")}
for ax, (nm, L1, L2) in zip(axs, (("goc", L1_0, L2_0), ("thu het", LMIN, LMIN), ("duoi het", L1MAX, LMAX))):
    set_pose(0, L1, L2, 0, update=False)
    draw(ax, [l for l in OBJ if l not in SKIP], App.Placement(), 0.0, 0.85)
    ax.set_aspect("equal"); ax.autoscale(); ax.grid(alpha=.25); ax.set_title("Toan canh (cat mat phang tay) - %s" % nm, fontsize=14)
plt.tight_layout(); fig.savefig(os.path.join(OUT, "arm-poses.png"), dpi=70); plt.close(fig)
print("render %.1f s" % (time.time() - t0))
