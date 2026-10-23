# Chay trong FreeCAD GUI qua RPC (gui noi dung file): mo pushrod_arm, backup, dua ve tu the goc (rest.json), kiem, Luu.
# Dung khi file bi Luu luc dang mo phong (da gap 2026-10-23).
import FreeCAD as App, json, time
P = r"D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
docs = [d for d in App.listDocuments().values() if d.FileName.replace("\\", "/").lower() == (P + "pushrod_arm.FCStd").lower()]
if docs:  # da mo san (co the Tuan dang sua) -> co thay doi chua luu thi dung
    doc = docs[0]
    assert doc.UndoCount == 0, "co thao tac chua luu (UndoCount > 0) - dung lai"  # isTouched() bat sau khi nap file, khong tin duoc
else:  # vua mo tu file: trang thai "touched" do FreeCAD dat khi nap, noi dung = file da luu
    doc = App.openDocument(P + "pushrod_arm.FCStd")
bk = P + "backup/pushrod_arm.%s.before-reset-rest-pose.FCStd" % time.strftime("%Y%m%d-%H%M%S")
doc.saveCopy(bk)
rest = json.load(open(P + "pushrod_arm_rest.json"))
doi = 0
for o in doc.Objects:
    if o.Name in rest:
        b, q = rest[o.Name]
        R = App.Placement(App.Vector(*b), App.Rotation(*q))
        if not o.Placement.isSame(R, 1e-9):
            o.Placement = R
            doi += 1
doc.recompute()
con_lech = [o.Label for o in doc.Objects if o.Name in rest and not o.Placement.isSame(
    App.Placement(App.Vector(*rest[o.Name][0]), App.Rotation(*rest[o.Name][1])), 1e-6)]
if not con_lech:
    doc.save()
print(json.dumps({"backup": bk, "doi_placement": doi, "con_lech": con_lech, "da_luu": not con_lech}, ensure_ascii=False))
try:
    import FreeCADGui as Gui
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
