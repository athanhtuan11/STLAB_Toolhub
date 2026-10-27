# Anh huong dan lap cyberbrick-car (CLI, khong mo GUI FreeCAD) - 2026-10-26:
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode ../../tools/robotics-cad/scripts/fc_cli.py --pass freecad/scripts/render_assembly_cli.py
# (cwd maker/cyberbrick-car). Ra freecad/images/assembly/step-XX.png + cover.png. CHI DOC cyberbrick_car.FCStd.
# Quy uoc anh (giong pushrod-arm ASSEMBLY.md): chi tiet MOI mau vang, phan DA LAP mau xam; buoc nho thi phong to vung moi.
import fnmatch
import os
import sys

import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(PROJ, "..", "..", "tools", "robotics-cad", "scripts"))
sys.path.insert(0, HERE)
from mpl_render import render  # noqa: E402
import gearbox_housing_dual as ghd  # noqa: E402
import cad_lib as cl  # noqa: E402

V = App.Vector
OUT = os.path.join(PROJ, "freecad", "images", "assembly")
MOI, CU, TPU = (0.98, 0.78, 0.10), (0.62, 0.64, 0.68), (0.15, 0.15, 0.15)

# (so, tieu de, [glob chi tiet MOI], goc nhin, phong_to)
STEPS = [
    (3, "Hop so vao khung + thanh chan tren", ["CB_Gearbox_*", "Gearbox_strap", "M2_5x6_strap_*"], (35.0, -60.0), True),
    (4, "Banh sau + lop", ["Wheel_R*", "CB_Tire_R*"], (25.0, -45.0), False),
    (5, "Khop lai trai/phai + chot lai M2.5x16", ["Knuckle_*", "M2_5x16_kingpin_*"], (40.0, -40.0), True),
    (6, "Banh truoc + lop + long den + vit dau truc", ["Wheel_F*", "CB_Tire_F*", "Washer_axle_*", "M2_5x6_axle_*"],
     (25.0, -35.0), True),
    (7, "Thanh giang + 2 vit tay lai", ["Tie_rod", "M2_5x6_tierod_*"], (55.0, -30.0), True),
    (8, "Servo lai vao gia + 2 vit M2x8", ["CB_Servo9g_180_steering", "M2x8_servo*"], (45.0, -50.0), True),
    (9, "Horn servo + chot horn M2x8", ["LK_Servo_horn", "M2x8_horn_pin"], (55.0, -40.0), True),
    (10, "Bo thu XA004 + 4 vit M2.5x6 tu duoi san", ["CB_XA004_receiver", "M2_5x6_receiver*"], (40.0, -60.0), True),
    (11, "Cong tac XA007 + 2 vit M2x6, pin PC003 vao khay", ["CB_Switch_XA007", "M2x6_switch*", "CB_Battery_PC003"],
     (40.0, -60.0), True),
    (12, "4 nam cham tren tru khung", ["CB_Magnet_4x2_chassis_*"], (50.0, -60.0), False),
    (13, "Than xe (4 nam cham trong gan than)", ["Body_coupe", "CB_Magnet_4x2_body_*"], (30.0, -50.0), False),
]


def mau(label):
    return TPU if label.startswith("CB_Tire") else None


def khung(shapes, pad=25.0):
    bb = App.BoundBox()
    for s in shapes:
        bb.add(s.BoundBox)
    c = bb.Center
    r = max(bb.XLength, bb.YLength, bb.ZLength) / 2 + pad
    return [Part.makeBox(2 * r, 2 * r, 2 * r, V(c.x - r, c.y - r, c.z - r))]


doc = App.openDocument(os.path.join(PROJ, "freecad", "cyberbrick_car.FCStd"))
O = {o.Label: o.Shape for o in doc.Objects if hasattr(o, "Shape") and o.Shape.Solids}
os.makedirs(OUT, exist_ok=True)

# ---- buoc 1-2: hop so 2 truc (rieng) ----
than, nap, truc, rest = ghd.dual_housing(doc)
AXX, AXZ = 0.0, 16.8
# bo trong bo 1 truc: chot thep o truc ra (Ø2,1, tam x 0) + banh rang ra lien truc (12 x 12,1, y > 5) - bo 2 truc thay bang
# truc kim loai xuyen 2 dau (Gemini doc huong dan lap hang 2026-10-26)
giu = [s for s in rest if not (abs(s.BoundBox.Center.x - AXX) < 0.5 and s.BoundBox.XLength < 2.5)
       and not (abs(s.BoundBox.Center.x - AXX) < 0.5 and s.BoundBox.Center.y > 5)]
truc_ra = cl.cyl(2.65, "y", (-18.0, 18.0), (AXX, AXZ))
no = 22.0   # tach cac lop theo Y de thay thu tu
lop = [(than, CU, 0.0), (truc_ra, (0.75, 0.75, 0.8), -1.0)]
for s in giu:
    lop.append((s, MOI, 0.0))
nap_no = nap.copy()
nap_no.translate(V(0, no, 0))
items = [(s.copy(), c) for s, c, _ in lop] + [(nap_no, CU)]
render(items, os.path.join(OUT, "step-01.png"), view=(20.0, -35.0), title="Buoc 1-2: hop so 2 truc - than, motor, banh rang, truc ra, nap")
render([(than, CU), (nap, CU), (truc_ra, (0.75, 0.75, 0.8))] + [(s, CU) for s in giu if s.BoundBox.XLength > 40],
       os.path.join(OUT, "step-02.png"), view=(20.0, -35.0), title="Buoc 2: dong nap - truc ra tho 2 ben")

# ---- buoc 3-13: lap vao xe ----
da = ["Chassis"]
for so, ten, moi, view, zoom in STEPS:
    lb_moi = [k for k in O if any(fnmatch.fnmatch(k, p) for p in moi)]
    lb_cu = [k for k in da if k in O]
    items = [(O[k], CU) for k in lb_cu] + [(O[k], mau(k) or MOI, 0.55 if k == "Body_coupe" else 1.0) for k in lb_moi]
    fit = khung([O[k] for k in lb_moi]) if zoom else [O[k] for k in lb_cu + lb_moi]
    render(items, os.path.join(OUT, "step-%02d.png" % so), view=view, fit=fit, title="Buoc %d: %s" % (so, ten))
    da += lb_moi
    print("STEP", so, len(lb_moi), "moi", flush=True)
render([(O[k], mau(k) or CU) for k in da if k in O], os.path.join(OUT, "cover.png"), view="iso", title="cyberbrick-car")
App.closeDocument(doc.Name)
print("ASSEMBLY_IMAGES_OK", len(STEPS) + 3)
