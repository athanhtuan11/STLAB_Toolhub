# CLI (freecadcmd --safe-mode, qua fc_cli.py): day thanh ngoai ranh thanh rang tren Housing_* tu 0,2 -> 0,9 mm.
# Vi sao (Tuan 2026-10-25: "housings khi in bi mat 1 ben thanh phia ngoai, bat support hay khong deu bi"):
# ranh thanh rang z +-6,3 (thanh 12 + khe 0,3, nong 2026-10-24) ma mat ngoai vo o z +-6,5 -> vach 0,2 mm < 1 duong dun
# 0,4 -> slicer bo, in ra thanh ho mat ngoai (x 15,7..70, cao ~6,6 mm khi in nam). Do lai bang lat cat lop luoi 3MF.
# Sua: dap them 0,7 mm ra NGOAI (khong doi ranh, khong doi khe) -> vach 0,9 = 2 duong (classic: ngoai 0,42 + trong 0,45).
# Khong day hon duoc: Boom001 vao toi z 7,52 khi L1 = 118 (duoi het, x 28..70) - lan dau dap 1,8 -> kinematics_test cham
# 313 mm3. Dap 0,7 -> mat ngoai 7,2, khe Boom 0,32 o tu the duoi het. He xi-lanh nhu 2026-10-24_cylinder_030_gearbox.py.
import sys
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
import FreeCAD as App, Part, safe_edit as se  # noqa: E401
from FreeCAD import Vector as V

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
SKIN_Z, PAD = 6.5, 0.7           # mat ngoai hien tai, chieu day dap them (ranh 6,3 -> vach 0,9)
X0, X1, YH = 14.7, 71.0, 6.1     # vung dap: ranh x 15,7..75 (+1 mm), toan be ngang vo quanh ranh
_f = open(P + "check/housing-rack-wall-2026-10-25.log", "w", encoding="utf-8")  # freecadcmd Windows khong in stdout

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-housing-rack-wall")
O = {o.Label: o for o in doc.Objects}
for tag, sgn in (("Shoulder", 1), ("Elbow", -1)):  # mat ngoai ranh: vai z = +6,5, khuyu z = -6,5 (he xi-lanh)
    R = O["Rack_" + tag].Placement
    ho = O["Housing_" + tag]
    hl = ho.Shape.copy(); hl.transformShape(R.inverse().toMatrix())
    zf = sgn * SKIN_Z
    assert abs((hl.BoundBox.ZMax if sgn > 0 else hl.BoundBox.ZMin) - zf) < 1e-3, (tag, "mat ngoai khong o", zf)
    # vet mat ngoai trong vung ranh -> dun ra ngoai (chi dap dung cho dang co vat lieu, khong tao khoi lo lung)
    sec = Part.makeCompound(hl.slice(V(0, 0, 1), zf - sgn * 0.05))
    face = Part.makeFace(sec.Wires, "Part::FaceMakerBullseye")
    face = face.common(Part.makeBox(X1 - X0, 2 * YH, 1, V(X0, -YH, zf - sgn * 0.05 - 0.5)))
    face.translate(V(0, 0, sgn * 0.05))
    pad = face.extrude(V(0, 0, sgn * PAD))
    new = hl.fuse(pad).removeSplitter()
    add = new.Volume - hl.Volume
    assert new.isValid() and len(new.Solids) == 1 and 150 < add < 1500, (tag, add, len(new.Solids))
    # kiem: vach giua ranh va mat ngoai >= 0,85 mm tai giua ranh (x 20,5..27,5 va 34..41,5 la cua so co san -> bo qua)
    for x in (18, 30, 50, 65):
        assert new.isInside(V(x, 0, sgn * (6.3 + 0.85)), 1e-4, True), (tag, "vach chua day", x)
        assert not new.isInside(V(x, 0, sgn * 6.2), 1e-4, True), (tag, "lap ranh", x)
    s = new.copy(); s.transformShape(R.toMatrix())
    if not s.Placement.isSame(App.Placement(), 1e-9):
        s = Part.makeCompound([s])
    se.apply(ho, s)
    assert ho.Placement.isSame(App.Placement(), 1e-6)
    print(tag, "them mm3", round(add, 1), file=_f, flush=True)
doc.recompute()
print("saved", se.save(doc, gui_from=bk), "backup", bk, file=_f, flush=True)
