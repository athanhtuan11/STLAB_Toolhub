# MAU phong cach anh huong dan lap moi (Tuan 2026-10-25: "chua ro net va mau sac chua phu hop") - 3 buoc de duyet.
# Theo Agrawala et al. SIGGRAPH 2003 (action diagram: tach chi tiet moi theo huong lap + duong dan; chi tiet moi phai thay ro;
# 1 phan chi tiet cu lam boi canh) + phong cach CyberBrick Mini T (khoi mau trung tinh + vien dam, 1 mau nhan).
# Chay qua gui_run.py (FC_FILE, FC_SCRIPT, FC_OUT, PROTO_OUT). KHONG Luu file.
import os
import time

import FreeCAD as App
import FreeCADGui as Gui
import Part
from FreeCAD import Vector as V

OUT = os.environ.get("PROTO_OUT", App.getUserAppDataDir())
W, H = 2400, 1800                     # chup gap doi roi thu nho -> net min
DONE = (0.83, 0.87, 0.85)             # xam nhat (#D3DDD8 STLab "line")
NEW = (0.91, 0.70, 0.23)              # vang STLab "highlight" #E8B33A
EDGE = (0.09, 0.14, 0.11)             # vien #16231D
doc = App.ActiveDocument
view = Gui.getDocument(doc.Name).ActiveView
O = {o.Label: o for o in doc.Objects}
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature") and o.Shape.Solids
         and not any(p.isDerivedFrom("Part::Feature") for p in o.InList)]
for g in doc.Objects:
    if g.isDerivedFrom("App::DocumentObjectGroup"):
        g.ViewObject.Visibility = True
R_sh = O["Rack_Shoulder"].Placement.Rotation


def settle():
    for _ in range(3):
        Gui.updateGui()
        time.sleep(0.05)


# (ma, chi tiet da lap hien (bo canh), [(chi tiet moi, vector tach mm)], huong nhin)
STEPS = [
    ("09", ["Base_deck", "Slide_ring", "Turntable"],
     [("Turntable_gear_m1_z60", V(0, 0, -22)), ("M2_5x10_gear", V(0, 0, -45)), ("M2_5x10_gear001", V(0, 0, -45))],
     V(-1, 1, 0.8)),                                   # nhin tu duoi len (vit bat tu duoi); None = isometric chuan
    ("18", ["Turret_one_piece", "Turntable", "Base_deck"],
     [("Boom001", V(0, 0, 0)), ("Spacer_S", V(0, 0, 0)), ("Spacer_S001", V(0, 0, 0)),
      ("Pin_S", V(0, -55, 0)), ("Pin_S_washer", V(0, 25, 0)), ("Pin_S_M2_5x6", V(0, 40, 0))],
     None),
    ("27", ["Housing_Shoulder", "Pinion_WormWheel_Shoulder", "Rack_Shoulder"],
     [("CB_030_gearbox_Shoulder", R_sh.multVec(V(0, 45, 0))), ("Worm_Shoulder", R_sh.multVec(V(0, 45, 0))),
      ("Pin_gearbox_Shoulder", R_sh.multVec(V(30, 0, 0)))],
     None),
]
saved = {o.Name: (o.ViewObject.Visibility, tuple(o.ViewObject.ShapeColor), o.ViewObject.DisplayMode,
                  o.ViewObject.LineWidth, tuple(o.ViewObject.LineColor), o.ViewObject.Transparency, App.Placement(o.Placement))
         for o in parts}
tmp = []
try:
    for code, ctx, new, vdir in STEPS:
        newo = [O[n] for n, _ in new]
        show = set(ctx) | {n for n, _ in new}
        for o in parts:
            vo = o.ViewObject
            vo.Visibility = o.Label in show
            vo.Transparency = 0
            vo.DisplayMode = "Flat Lines"
            vo.LineColor = EDGE
            vo.LineWidth = 4
            vo.ShapeColor = NEW if o in newo else DONE
        for n, d in new:                                # tach theo huong lap + duong dan net dut
            o = O[n]
            if d.Length > 0:
                c0 = o.Shape.BoundBox.Center
                o.Placement = App.Placement(d, App.Rotation()).multiply(o.Placement)
                ln = doc.addObject("Part::Feature", "guide_tmp")
                ln.Shape = Part.LineSegment(c0, c0 + d).toShape()
                ln.ViewObject.LineColor = EDGE
                ln.ViewObject.LineWidth = 6
                ln.ViewObject.DrawStyle = "Dashed"
                tmp.append(ln)
        settle()
        if vdir is None:
            view.viewIsometric()
        else:
            view.setViewDirection((vdir.x, vdir.y, vdir.z))
        Gui.Selection.clearSelection()
        for n in show:
            Gui.Selection.addSelection(O[n])
        Gui.SendMsgToActiveView("ViewSelection")      # khung = cum dang lap, khong ca canh tay
        Gui.Selection.clearSelection()                  # bo mau chon (xanh) truoc khi chup
        settle()
        view.saveImage(os.path.join(OUT, "proto-%s.png" % code), W, H, "White")
        for n, d in new:
            O[n].Placement = saved[O[n].Name][6]
        for ln in tmp:
            doc.removeObject(ln.Name)
        tmp = []
finally:
    for ln in tmp:
        doc.removeObject(ln.Name)
    for o in parts:
        v, col, dm, lw, lc, tr, pl = saved[o.Name]
        vo = o.ViewObject
        vo.Visibility, vo.ShapeColor, vo.DisplayMode, vo.LineWidth, vo.LineColor, vo.Transparency = v, col, dm, lw, lc, tr
        o.Placement = pl
