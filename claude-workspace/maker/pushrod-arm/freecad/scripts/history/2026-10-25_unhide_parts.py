# CLI: hien lai chi tiet bi AN sau lan Luu GUI 2026-10-24 21:15 (hinh hoc khong doi - da so voi backup 15:06).
# Danh sach = dung tieu chi test_no_hidden_parts (Part::Feature co solid, an, khong nam trong Part::Feature khac) + nhom cha.
# Sua CA App Visibility LAN GuiDocument.xml (cach cua 2026-10-24_unhide_parts.py).
import builtins
import re
import shutil
import sys
import zipfile
sys.path.insert(0, "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/robotics-cad/scripts")
import FreeCAD as App, safe_edit as se  # noqa: E401

P = "D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
_f = open(P + "check/unhide-2026-10-25.log", "w", encoding="utf-8")  # freecadcmd Windows khong in stdout


def print(*a):
    builtins.print(*a, file=_f, flush=True)


doc = App.openDocument(P + "pushrod_arm.FCStd")
se.guard(doc, rest_json=P + "pushrod_arm_rest.json")
bk = se.backup(doc, "before-unhide-parts")
names, changed = [], []
for o in doc.Objects:
    if (o.isDerivedFrom("Part::Feature") and not o.Shape.isNull() and o.Shape.Solids and not o.Visibility
            and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)):
        o.Visibility = True
        names.append(o.Name); changed.append(o.Label)
for o in doc.Objects:  # GUI an nhom -> an con
    if o.isDerivedFrom("App::DocumentObjectGroup") and any(c.Name in names for c in o.Group) and not o.Visibility:
        o.Visibility = True; names.append(o.Name); changed.append(o.Label)
f = se.save(doc, gui_from=bk)
App.closeDocument(doc.Name)

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
print("RES unhidden", len(changed), sorted(changed), "backup", bk)
