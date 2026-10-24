# CLI: hien lai chi tiet bi AN (Visibility=False) - metrics/check/BOM/xuat STL bo qua chi tiet an -> 2026-10-24
# prepare-print bao "da xoa" Pin_A..E, Boom001, Forearm..., BOM con 6 vit M2.5x6 (dung: 21). An tu truoc phien nay
# (ban backup 14:23 da an). Danh sach = cac chi tiet trong metrics.json + BOM.csv o commit HEAD (lan chay tot) + chi tiet moi.
# Sua CA App Visibility LAN GuiDocument.xml (neu khong, mo bang GUI se an lai va lan Luu sau lai hong).
import json
import re
import shutil
import sys
import zipfile
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/scripts")
import FreeCAD as App, safe_edit as se  # noqa: E401

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
want = set(json.load(open(sys.argv[-1] if sys.argv[-1].endswith(".json") else P + "../head_labels.json")))
want |= {"CB_030_gearbox_Shoulder", "CB_030_gearbox_Elbow", "Pin_gearbox_Shoulder", "Pin_gearbox_Elbow",
         "CB_XA003_XA004_receiver", "Receiver_riser"}

doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-unhide-parts")
names, changed = [], []
for o in doc.Objects:
    if o.Label in want:
        names.append(o.Name)
        if not o.Visibility:
            o.Visibility = True
            changed.append(o.Label)
    # nhom chua chi tiet: hien nhom (GUI an nhom -> an con)
for o in doc.Objects:
    if o.isDerivedFrom("App::DocumentObjectGroup") and any(c.Name in names for c in o.Group) and not o.Visibility:
        o.Visibility = True; names.append(o.Name); changed.append(o.Label)
f = se.save(doc, gui_from=bk)
App.closeDocument(doc.Name)

# GuiDocument.xml: Visibility cua ViewProvider -> true cho cac object tren
tmp = f + ".tmp"
with zipfile.ZipFile(f) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        data = zi.read(it.filename)
        if it.filename == "GuiDocument.xml":
            x = data.decode("utf-8"); n0 = 0
            for nm in names:
                pat = re.compile(r'(<ViewProvider name="%s"[^>]*>.*?<Property name="Visibility"[^>]*>\s*<Bool value=")false(")'
                                 % re.escape(nm), re.S)
                x, k = pat.subn(r"\1true\2", x, count=1); n0 += k
            data = x.encode("utf-8"); print("RES GuiDocument visibility fixed", n0)
        zo.writestr(it, data)
shutil.move(tmp, f)
print("RES unhidden", len(changed), sorted(changed))
