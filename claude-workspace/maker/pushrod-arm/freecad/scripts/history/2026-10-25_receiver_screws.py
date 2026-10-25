# CLI (qua fc_cli.py): them 4 vit M2.5x16 bat bo thu XA003/XA004 qua 4 ong nang vao tru Base_housing (ASSEMBLY buoc 4).
# Do tren model 2026-10-25: mach XA004 day 1,7 (z 21,7-23,4) + ong nang 9,7 (z 12-21,7) = 11,4; lo moi O2,2 trong tru sau
# 5,0 (z 7-12). M2.5x16: an vao nhua 4,6 mm, mui vit cach day lo 0,4 mm. x14 chi an 2,6 -> yeu.
# Vit dau tru luc giac chim ISO 4762 / DIN 912 (mu O4,5 cao 2,5) - cung kieu cac vit khac trong model.
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
L, HEAD_D, HEAD_K, D = 16.0, 4.5, 2.5, 2.5
_f = open(P + "check/receiver-screws-2026-10-25.log", "w", encoding="utf-8")
doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-receiver-screws")
O = {o.Label: o for o in doc.Objects}
assert not any(lb.startswith("M2_5x16_receiver") for lb in O), "da co vit bo thu"
board_top = max(s.BoundBox.ZMax for s in O["CB_XA003_XA004_receiver"].Shape.Solids
                if s.BoundBox.XLength > 25 and s.BoundBox.YLength > 25)          # mat tren mach XA004
grp = [g for g in O["Receiver_riser"].InList if g.isDerivedFrom("App::DocumentObjectGroup")]
for k, r in enumerate(O["Receiver_riser"].Shape.Solids):
    c = r.BoundBox.Center
    shank = Part.makeCylinder(D / 2, L, V(c.x, c.y, board_top - L), V(0, 0, 1))
    head = Part.makeCylinder(HEAD_D / 2, HEAD_K, V(c.x, c.y, board_top), V(0, 0, 1))
    o = doc.addObject("Part::Feature", "M2_5x16_receiver" + ("" if k == 0 else "%03d" % k))
    o.Label = o.Name
    o.Shape = shank.fuse(head).removeSplitter()
    o.Label2 = "Vit M2.5x16 ISO 4762 - bat bo thu qua ong nang vao tru de"
    for g in grp:
        g.addObject(o)
    print(o.Label, "mui vit z %.2f, an vao tru %.2f mm" % (board_top - L, 12.0 - (board_top - L)), file=_f, flush=True)
print("saved", se.save(doc, gui_from=bk), "backup", bk, file=_f, flush=True)
