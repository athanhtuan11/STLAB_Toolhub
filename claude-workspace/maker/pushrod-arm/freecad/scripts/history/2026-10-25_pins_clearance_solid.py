# CLI (freecadcmd --safe-mode, qua fc_cli.py): dung lai 7 chot khop (Pin_S, Pin_A..E, Pin_jaw2).
# Tuan 2026-10-25: in ra "qua khit khong the nhet vo" Boom001/Turret_one_piece...; "lam rong nen yeu luc";
# "neu bat oc vit cuoi thi chi can lam ren vua du cho loai oc".
# Do truoc khi sua: than O5,0 trong lo O5,4 = 0,2 mm/ben; mu O9 x 1,6; lo vit O2,2 sau 4,8 (= dung phan vit an vao ->
# vit cham day); than DAC trong model, "rong" do in infill 40 % -> chot chuyen sang ban in 100 %.
# Sua: than SHAFT_D (khe quay >= 0,3 mm/ben voi lo O5,4 da in), vat dau 0,4, mat phang day (in nam) cach tam 2,0 nhu cu,
# lo vit O2,2 sau SCREW_DEPTH = 6 (vit M2.5x6) - 1,2 (washer) + 0,7 du. Chi in lai chot, giu nguyen chi tiet co lo.
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
SHAFT_D = float(sys.argv[1]) if len(sys.argv) > 1 else 4.8   # doi sau khi thu bo chot thu (pin gauge)
HEAD_R, HEAD_T = 4.5, 1.6
TIP_CH = 0.4
FLAT_FROM_AXIS = 2.0           # mat phang day cach tam truc (in nam, khong support)
SCREW_D, SCREW_DEPTH = 2.2, 6.0 - 1.2 + 0.7
PINS = ["Pin_S", "Pin_A", "Pin_B", "Pin_C", "Pin_D", "Pin_E", "Pin_jaw2"]
_f = open(P + "check/pins-2026-10-25.log", "w", encoding="utf-8")


def log(*a):
    print(*a, file=_f, flush=True)


def cyl(r, t0, t1, c, ax):
    return Part.makeCylinder(r, t1 - t0, c + ax * t0, ax)


doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-pins-clearance-solid")
O = {o.Label: o for o in doc.Objects}
for name in PINS:
    o = O[name]
    pl = App.Placement(o.Placement)
    # Dung trong HE RIENG cua chot (Pin_jaw2 di theo cum kep, Placement != I). Khong dung transformShape de doi he:
    # FreeCAD chi gan Placement chu khong bien doi hinh -> Placement bi ap 2 lan (lan chay dau 2026-10-25 lech Pin_jaw2).
    s = o.Shape.copy()
    s.Placement = App.Placement()
    down = pl.Rotation.inverted().multVec(V(0, 0, -1))   # huong -Z the gioi (mat ban in) trong he rieng
    big = max((f for f in s.Faces if isinstance(f.Surface, Part.Cylinder)), key=lambda f: f.Area)
    ax = V(big.Surface.Axis); c = V(big.Surface.Center)
    ts = [v.Point.sub(c).dot(ax) for v in s.Vertexes]
    t0, t1 = min(ts), max(ts)
    # mu nam o dau t0? (mat cat gan t0 rong 9) - neu khong thi dao truc
    near = s.slice(ax, (c + ax * (t0 + 0.3)).dot(ax))
    if max(max(w.BoundBox.XLength, w.BoundBox.YLength, w.BoundBox.ZLength) for w in near) < 8:
        ax = ax * -1
        t0, t1 = -t1, -t0
    r = SHAFT_D / 2
    head = cyl(HEAD_R, t0, t0 + HEAD_T, c, ax)
    shaft = cyl(r, t0 + HEAD_T - 0.01, t1 - TIP_CH, c, ax)
    tip = Part.makeCone(r, r - TIP_CH, TIP_CH, c + ax * (t1 - TIP_CH), ax)
    pin = head.fuse([shaft, tip]).removeSplitter()
    # mat phang day (in nam): nua khong gian phia "down" cach truc FLAT_FROM_AXIS - giong chot cu
    knife = Part.makeBox(200, 200, 100, V(-100, -100, 0))
    knife.Placement = App.Placement(c + down * FLAT_FROM_AXIS, App.Rotation(V(0, 0, 1), down))
    pin = pin.cut(knife)
    pin = pin.cut(cyl(SCREW_D / 2, t1 - SCREW_DEPTH, t1 + 0.1, c, ax))
    assert pin.isValid() and len(pin.Solids) == 1, name
    v0 = s.Volume
    o.Shape = pin
    o.Placement = pl
    log(f"{name}: than O{SHAFT_D}, lo vit sau {SCREW_DEPTH:.1f}, V {v0:.0f} -> {o.Shape.Volume:.0f} mm3, "
        f"bbox the gioi z {o.Shape.BoundBox.ZMin:.2f}..{o.Shape.BoundBox.ZMax:.2f}")
log("saved", se.save(doc, gui_from=bk), "backup", bk)
