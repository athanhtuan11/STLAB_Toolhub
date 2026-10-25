# CLI (freecadcmd --safe-mode, qua fc_cli.py): vat mieng lo truc hop so tren Worm_* 0,4 mm x 45 do.
# Vi sao (2026-10-25): Worm in DUNG, mieng lo up xuong ban -> lop dau PETG be vao trong (profile chi bu elephant foot 0,075),
# khe huong kinh lo chi 0,32 -> vat mieng de bu be + dan truc vao. Danh doi: mat vat khoa xoay ngan 0,4 / 8,4 mm.
# He xi-lanh nhu 2026-10-24_cylinder_030_gearbox.py: truc vit // x tai y 9,4, z = zs*20,25; mat moay-o x = 44,9.
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
X_FACE, R_HOLE, CH = 44.9, 2.96, 0.4   # mat moay-o, ban kinh lo tron (truc 2,64 + khe 0,32), vat
_f = open(P + "check/worm-chamfer-2026-10-25.log", "w", encoding="utf-8")  # freecadcmd Windows khong in stdout

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-worm-socket-chamfer")
O = {o.Label: o for o in doc.Objects}
for tag, zs in (("Shoulder", -1), ("Elbow", 1)):
    R = O["Rack_" + tag].Placement
    cone = Part.makeCone(R_HOLE + CH + 0.2, R_HOLE, CH + 0.2, V(X_FACE - 0.2, 9.4, zs * 20.25), V(1, 0, 0))
    cone.transformShape(R.toMatrix())
    w = O["Worm_" + tag]
    s, info = se.safe_cut(w, cone, solids=1)
    print(tag, info, file=_f, flush=True)
    se.apply(w, s)
    assert w.Placement.isSame(App.Placement(), 1e-6)
print("saved", se.save(doc, gui_from=bk), "backup", bk, file=_f, flush=True)
