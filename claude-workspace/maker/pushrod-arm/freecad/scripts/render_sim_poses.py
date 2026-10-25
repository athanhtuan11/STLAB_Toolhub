# Mo phong assembly -> anh tu the: dung CHINH logic macro pushrod_arm_sim (set_pose + check_collisions) trong GUI rieng.
#   set FC_FILE=.../pushrod_arm.FCStd  set FC_SCRIPT=<file nay>
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCAD.exe" --safe-mode tools/robotics-cad/scripts/gui_run.py
# Ra: freecad/images/sim/<tu the>.png + _sim.json (va cham tung tu the). Khong Luu .FCStd.
import json
import os

import FreeCAD as App
import FreeCADGui as Gui

FC = os.path.dirname(App.ActiveDocument.FileName)
OUT = os.path.join(FC, "images", "sim")
os.makedirs(OUT, exist_ok=True)
src = open(os.path.join(FC, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read().split("class Panel", 1)[0]
G = {"__name__": "sim"}
exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
set_pose, check, fast = G["set_pose"], G["check_collisions"], G["fast_collider"]()
LMIN, LMAX, L1MAX, L1_0, L2_0 = G["LMIN"], G["LMAX"], G["L1MAX"], G["L1_0"], G["L2_0"]
POSES = [("1-rest", 0, L1_0, L2_0, 0), ("2-shoulder-in-elbow-out", 0, LMIN, LMAX, -26),
         ("3-shoulder-out-elbow-in", 0, L1MAX, LMIN, 0), ("4-both-out", 0, L1MAX, LMAX, -55),
         ("5-both-in", 0, LMIN, LMIN, 3), ("6-yaw90-mid", 90, (LMIN + L1MAX) / 2, (LMIN + LMAX) / 2, -26)]
v = Gui.ActiveDocument.ActiveView
for o in App.ActiveDocument.Objects:
    if o.isDerivedFrom("Part::Feature") and o.ViewObject:
        o.ViewObject.Visibility = not o.Label.startswith("M2_5")
res = []
for name, yaw, L1, L2, grip in POSES:
    ok = set_pose(yaw, L1, L2, grip)
    hits = check(fast) if ok else ["khong toi duoc"]
    res.append({"pose": name, "yaw": yaw, "L1": round(L1, 1), "L2": round(L2, 1), "grip": grip, "hits": hits})
    for cam, fn in (("front", v.viewFront), ("iso", v.viewIsometric)):
        fn(); v.fitAll()
        v.saveImage(os.path.join(OUT, "%s-%s.png" % (name, cam)), 1200, 900, "White")
set_pose(0, L1_0, L2_0, 0)
json.dump(res, open(os.path.join(OUT, "_sim.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
