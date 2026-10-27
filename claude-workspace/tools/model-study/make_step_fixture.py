# Chi tiet mau STEP biet truoc so do cho gate measure_step.py (Claude viet, executor KHONG sua).
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" make_step_fixture.py <thu muc ra>
# Tam 40x24x6 (x -20..20, y -12..12, z 0..6):
#  - lo xuyen Z D3.2 tai (-12, 0)  [chu y: KHONG removeSplitter -> mat tru co the tach 2 nua]
#  - lo xuyen Z D3.2 tai (12, 0)   [cung D, khac tam -> 2 dac trung rieng]
#  - lo mu Y D5.0 sau 8 tu mat y=-12, tam (0, z 3)
#  - chot D3.0 dai 10 theo +X tu mat x=20, tam (y 0, z 3)
#  - bo canh R2 doc canh tren x=-20,y.. (cung 90 do -> kind "arc", khong phai hole/pin)
import os, sys
import FreeCAD as App, Part

V = App.Vector
out = [a for a in sys.argv[1:] if not a.endswith(".py")][0]
os.makedirs(out, exist_ok=True)
plate = Part.makeBox(40, 24, 6, V(-20, -12, 0))
plate = plate.makeFillet(2.0, [e for e in plate.Edges
                               if abs(e.BoundBox.XMin + 20) < 1e-6 and abs(e.BoundBox.XMax + 20) < 1e-6
                               and abs(e.BoundBox.ZMin - 6) < 1e-6 and abs(e.BoundBox.ZMax - 6) < 1e-6])
for x in (-12, 12):
    plate = plate.cut(Part.makeCylinder(1.6, 8, V(x, 0, -1), V(0, 0, 1)))
plate = plate.cut(Part.makeCylinder(2.5, 9, V(0, -13, 3), V(0, 1, 0)))
shape = plate.fuse(Part.makeCylinder(1.5, 10, V(20, 0, 3), V(1, 0, 0)))
shape.exportStep(os.path.join(out, "fixture.step"))
print("fixture ok", len(shape.Faces), "faces")
