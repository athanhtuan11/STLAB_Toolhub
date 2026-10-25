# "Build replay": anh dung model TUNG BUOC cho video gioi thieu / huong dan hoc sinh (Tuan 2026-10-24: moi du an FreeCAD
# co clip). Chay trong FreeCAD GUI RIENG qua gui_run.py (khong dung phien cua Tuan), KHONG Luu file, khong doi Tip:
#   set FC_FILE=<file.FCStd>  set FC_SCRIPT=<duong dan file nay>  set FC_OUT=<log>
#   set REPLAY_OUT=<thu muc anh>  [set REPLAY_MODE=auto|body|parts]  [set REPLAY_SIZE=1920x1080]
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode maker/robotics-cad/scripts/gui_run.py
# - body  (PartDesign): moi feature cua moi Body = 1 anh (Display Mode Through: Shape feature = khoi tich luy toi buoc do);
#   feature co Profile (Pad/Pocket/Revolution...) -> them 1 anh SKETCH truoc ("ve roi moi Pad").
# - parts (chi Part::Feature, vd. pushrod-arm sinh bang script - khong co lich su): moi nhom (App::DocumentObjectGroup) theo
#   thu tu cay = 1 anh, chi tiet cu mo, chi tiet MOI dac. Thu tu lap that: freecad/scripts/render_assembly.py cua du an.
# - auto: co PartDesign::Body -> body, khong -> parts.
# Ra: <REPLAY_OUT>/step-XX.png + steps.json [{n, kind, label, type, dims}] -> chu thich / loi doc (make_reel.py `say:`).
# Camera co dinh (isometric, fit theo model day du) de cac khung khong nhay. Doc nghien cuu: docs/project-video-tutorial-
# hashtag-workflow.md muc 1.2.
import json
import os

import FreeCAD as App
import FreeCADGui as Gui

DIMS = ("Length", "Length2", "Angle", "Radius", "Size", "Depth", "Offset", "Occurrences")


def dims(o):
    out = {}
    for k in DIMS:
        if k in o.PropertiesList:
            v = getattr(o, k)
            out[k] = round(v.Value, 2) if hasattr(v, "Value") else v
    return out


def main():
    doc = App.ActiveDocument
    gd = Gui.getDocument(doc.Name)
    view = gd.ActiveView
    out = os.environ["REPLAY_OUT"]
    w, h = (int(x) for x in os.environ.get("REPLAY_SIZE", "1920x1080").split("x"))
    os.makedirs(out, exist_ok=True)
    bodies = [o for o in doc.Objects if o.TypeId == "PartDesign::Body"]
    mode = os.environ.get("REPLAY_MODE", "auto")
    mode = ("body" if bodies else "parts") if mode == "auto" else mode
    objs = [o for o in doc.Objects if hasattr(o, "ViewObject") and o.ViewObject]
    cu = {o.Name: (o.ViewObject.Visibility, getattr(o.ViewObject, "Transparency", 0)) for o in objs}
    steps = []

    def shot(kind, label, typ, d):
        Gui.updateGui()
        n = len(steps) + 1
        view.saveImage(os.path.join(out, f"step-{n:02d}.png"), w, h, "White")
        steps.append({"n": n, "kind": kind, "label": label, "type": typ, "dims": d})

    parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids
             and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
    groups = [g for g in doc.Objects if g.isDerivedFrom("App::DocumentObjectGroup")]
    try:
        # camera theo model DAY DU: hien trang thai cuoi truoc khi fit (file luu tu CLI mo ra co the an het)
        # bat nhom TRUOC: bat/tat 1 nhom FreeCAD bat/tat luon moi con (lan dau buoc 1 da hien ca tay)
        for g in groups:
            g.ViewObject.Visibility = True
        for o in objs:
            if o not in groups:
                o.ViewObject.Visibility = False
        for o in ([b.Tip for b in bodies if b.Tip] + bodies) if mode == "body" else parts:
            o.ViewObject.Visibility = True
        Gui.updateGui()
        view.viewIsometric()
        view.fitAll()
        for o in objs:
            if o not in groups:
                o.ViewObject.Visibility = False
        if mode == "body":
            for b in bodies:
                b.ViewObject.Visibility = True
                feats = [f for f in b.Group if f.isDerivedFrom("PartDesign::Feature")]
                for f in feats:
                    prof = getattr(f, "Profile", None)
                    sk = prof[0] if isinstance(prof, tuple) else prof
                    if sk is not None and sk.isDerivedFrom("Sketcher::SketchObject"):
                        sk.ViewObject.Visibility = True
                        shot("sketch", sk.Label, sk.TypeId, {"constraints": len(sk.Constraints)})
                        sk.ViewObject.Visibility = False
                    for g in feats:
                        g.ViewObject.Visibility = g is f
                    shot("feature", f.Label, f.TypeId, dims(f))
                for g in feats:  # Body xong: giu feature cuoi (Tip) cho Body sau
                    g.ViewObject.Visibility = g is b.Tip
        else:
            seen, order = set(), []
            for g in groups:
                mem = [o for o in g.Group if o in parts and o.Name not in seen]
                if mem:
                    order.append((g.Label, mem))
                    seen.update(o.Name for o in mem)
            rest = [o for o in parts if o.Name not in seen]
            if rest:
                order.append(("Khac", rest))
            shown = []
            for lab, mem in order:
                for o in shown:
                    o.ViewObject.Transparency = 75
                for o in mem:
                    o.ViewObject.Visibility = True
                    o.ViewObject.Transparency = 0
                shown += mem
                shot("group", lab, "App::DocumentObjectGroup", {"parts": [o.Label for o in mem]})
    finally:
        for o in objs:  # tra hien thi nhu cu (khong Luu file, nhung GUI nay co the con mo)
            o.ViewObject.Visibility, t = cu[o.Name]
            if "Transparency" in o.ViewObject.PropertiesList:
                o.ViewObject.Transparency = t
    with open(os.path.join(out, "steps.json"), "w", encoding="utf-8") as fp:
        json.dump({"file": doc.FileName, "mode": mode, "size": [w, h], "steps": steps}, fp, ensure_ascii=False, indent=1)


main()
