# CLI (freecadcmd --safe-mode): thay bo thu ve tay (XA004 tam phang + socket + XA003 nam TREN, cao 9 mm) bang STEP
# ghep cua hang "Remote Control Receiver-XA003-XA004" (cao 22,6 mm; XA003 cam MAT DUOI shield, header servo MAT TREN).
# Tuan 2026-10-24: "Model rx tx cua cyberbrick co shield..lúc ve can chu y". Khong in lai Base_housing: tam XA004 nang
# len z 21,7 bang 4 ong nang in roi dat len 4 tru cu (lo shield 4 x Ø2,7 tai ±11,5/±12 trung tam tru).
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
STEP = ("D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/community/cyberbrick-official/models/"
        "xa003-xa004-remote-control-receiver/remote-control-receiver.step")
BOARD_Z = 21.7            # mat duoi tam XA004 (mm): day loi XA003 phai cao hon dinh tru (12) - lan dau 19.0 cham tru
STANDOFF_TOP = 12.0       # dinh 4 tru cu tren Base_housing
CX, CY = 0.0, 35.0        # tam tam mach (= tam 4 tru: x ±11,5, y 23/47)
RISER_OD, RISER_ID = 5.6, 2.9

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-receiver-official-stack")
O = {o.Label: o for o in doc.Objects}
grp = [g for g in O["CB_XA004_receiver"].InList if g.isDerivedFrom("App::DocumentObjectGroup")]

# STEP hang: mach trong mat X-Z, chong theo Y (XA004 y -0.05..1.65, XA003 phia -Y, header servo phia +Y).
# -> world: x' = -x, y' = z + CY, z' = y + BOARD_Z + 0.05 (det +1); dau cam lon (STEP z -15..-4.5) nam duoi banh rang z60.
rx = Part.read(STEP)
m = App.Matrix(-1, 0, 0, CX, 0, 0, 1, CY, 0, 1, 0, BOARD_Z + 0.05, 0, 0, 0, 1)
rx.transformShape(m)
new = doc.addObject("Part::Feature", "CB_XA003_XA004_receiver")
new.Label = "CB_XA003_XA004_receiver"
new.Shape = rx
new.Label2 = "CyberBrick Remote Control Receiver XA003+XA004 (STEP hang, co shield)"

h = BOARD_Z - STANDOFF_TOP
risers = [Part.makeCylinder(RISER_OD / 2, h, V(CX + sx * 11.5, CY + sy * 12.0, STANDOFF_TOP)).cut(
          Part.makeCylinder(RISER_ID / 2, h, V(CX + sx * 11.5, CY + sy * 12.0, STANDOFF_TOP)))
          for sx in (-1, 1) for sy in (-1, 1)]
rs = doc.addObject("Part::Feature", "Receiver_riser")
rs.Label = "Receiver_riser"
rs.Shape = Part.makeCompound(risers)
rs.Label2 = "4 ong nang in roi: dat len 4 tru Base_housing, vit M2.5 dai hon (TODO chieu dai)"
for g in grp:
    g.addObject(new)
    g.addObject(rs)

for old in ("CB_XA004_receiver", "Socket_2x8", "CB_XA003_core"):
    doc.removeObject(O[old].Name)

doc.recompute()
print("RES receiver bb", [round(x, 2) for x in (rx.BoundBox.ZMin, rx.BoundBox.ZMax)], "riser h", h)
print("RES saved", se.save(doc, gui_from=bk), "backup", bk)
