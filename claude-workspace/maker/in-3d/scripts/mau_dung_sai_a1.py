"""Sinh mau in thu dung sai lap ghep cho Bambu A1 (chay bang FreeCAD, khong can GUI).

    "C:\\Program Files\\FreeCAD 1.1\\bin\\freecadcmd.exe" mau_dung_sai_a1.py

Tam A: lo truc 5 mm, lo M3 xuyen, lo M3 cho vit tu tao ren. Tam B: hoc o bi 608.
Moi lo khac so (mm) ben canh. Ket qua: ../models/mau-dung-sai-a1/ (FCStd, STEP, STL tung tam).
Doi gia tri trong PARAMS roi chay lai. Don vi: mm.
"""
import os

import FreeCAD
import Mesh
import Part

PARAMS = {
    "truc5": [5.0, 5.1, 5.2, 5.3, 5.4],          # lo cho truc/thanh 5 mm (truc dong co, ty thep)
    "m3_xuyen": [3.0, 3.2, 3.4, 3.6],            # lo M3 de vit di qua
    "m3_tu_ren": [2.5, 2.7, 2.9],                # lo de vit M3 tu tao ren vao nhua
    "o608": [22.0, 22.1, 22.2, 22.3, 22.4],      # hoc o bi 608 (D ngoai 22 mm, day 7 mm)
    "day_tam_a": 6.0,
    "hoc_608_sau": 7.0, "day_day_608": 2.0,
    "chu_cao": 3.5, "chu_sau": 0.6,              # chu khac tren mat tren
    "font": r"C:\Windows\Fonts\arialbd.ttf",
}

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "models", "mau-dung-sai-a1"))


def label(text, x, y, z_top, p):
    """Chu khac lom tren mat tren (z_top), goc trai duoi tai (x, y)."""
    if not os.path.exists(p["font"]):
        return None
    wires = Part.makeWireString(text, p["font"], p["chu_cao"], 0)
    faces = []
    for char in wires:
        for w in char:
            if w.isClosed():
                faces.append(Part.Face(w))
    if not faces:
        return None
    # mat chu: xu ly lo trong chu (vd so 0, 8) bang cach lay XOR theo thu tu dien tich
    faces.sort(key=lambda f: -f.Area)
    shape = None
    for f in faces:
        solid = f.extrude(FreeCAD.Vector(0, 0, p["chu_sau"] + 0.01))
        shape = solid if shape is None else (shape.cut(solid) if shape.common(solid).Volume > 1e-6 else shape.fuse(solid))
    shape.translate(FreeCAD.Vector(x, y, z_top - p["chu_sau"]))
    return shape


def hole(d, x, y, z0, h):
    return Part.makeCylinder(d / 2, h, FreeCAD.Vector(x, y, z0))


def tam_a(p):
    t = p["day_tam_a"]
    pitch = 16.0
    cols = max(len(p["truc5"]), len(p["m3_xuyen"]) + len(p["m3_tu_ren"]))
    w, h = pitch * cols + 8, 46.0
    body = Part.makeBox(w, h, t)
    cuts = []
    rows = [(34.0, p["truc5"]), (14.0, p["m3_xuyen"] + p["m3_tu_ren"])]
    for y, ds in rows:
        for i, d in enumerate(ds):
            x = 4 + pitch / 2 + i * pitch
            cuts.append(hole(d, x, y, -1, t + 2))
            lb = label(f"{d:.1f}", x - 5, y - 10.5 if y < 30 else y + 5.5, t, p)
            if lb:
                cuts.append(lb)
    # vach phan cach M3 xuyen / M3 tu ren
    xs = 4 + len(p["m3_xuyen"]) * pitch
    cuts.append(Part.makeBox(0.8, 14, p["chu_sau"] + 0.01, FreeCAD.Vector(xs - 0.4, 7, t - p["chu_sau"])))
    return body.cut(Part.makeCompound(cuts)).removeSplitter()


def tam_b(p):
    t = p["hoc_608_sau"] + p["day_day_608"]
    pitch = 29.0
    n = len(p["o608"])
    w, h = pitch * n + 6, 40.0
    body = Part.makeBox(w, h, t)
    cuts = []
    for i, d in enumerate(p["o608"]):
        x, y = 3 + pitch / 2 + i * pitch, 22.0
        cuts.append(hole(d, x, y, p["day_day_608"], p["hoc_608_sau"] + 1))   # hoc o bi
        cuts.append(hole(12.0, x, y, -1, t + 2))                              # lo day o bi ra
        lb = label(f"{d:.1f}", x - 6, 2.5, t, p)
        if lb:
            cuts.append(lb)
    return body.cut(Part.makeCompound(cuts)).removeSplitter()


def main():
    os.makedirs(OUT, exist_ok=True)
    doc = FreeCAD.newDocument("mau_dung_sai_a1")
    a = doc.addObject("Part::Feature", "TamA_truc5_M3")
    a.Shape = tam_a(PARAMS)
    b = doc.addObject("Part::Feature", "TamB_o608")
    b.Shape = tam_b(PARAMS)
    b.Placement.Base = FreeCAD.Vector(0, a.Shape.BoundBox.YLength + 10, 0)
    doc.recompute()
    doc.saveAs(os.path.join(OUT, "mau-dung-sai-a1.FCStd"))
    Part.export([a, b], os.path.join(OUT, "mau-dung-sai-a1.step"))
    for obj, name in ((a, "tam-a-truc5-m3.stl"), (b, "tam-b-o608.stl")):
        Mesh.export([obj], os.path.join(OUT, name))
    for obj in (a, b):
        bb = obj.Shape.BoundBox
        print(f"{obj.Name}: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm, "
              f"the tich {obj.Shape.Volume / 1000:.1f} cm3, hop le={obj.Shape.isValid()}")
    print("Da ghi vao:", OUT)


main()
