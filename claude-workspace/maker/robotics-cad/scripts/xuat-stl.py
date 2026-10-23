"""Xuat STL theo HUONG IN tu file FreeCAD, theo muc `xuat:` trong ban-in.yaml (dung chung moi du an).

Chay: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" scripts/xuat-stl.py --pass <ban-in.yaml>
(thuong goi qua chuan-bi-in.py). Chi DOC file .FCStd da luu, khong sua.

ban-in.yaml:
    fcstd: ../model.FCStd          # tuong doi theo file yaml
    tu_the_goc: ../rest.json       # tuy chon: {Name: [[x,y,z],[q0,q1,q2,q3]]} -> dua ve tu the goc truoc khi xuat
                                   # (file luu luc dang mo phong van xuat dung)
    xuat:
      luoi: {linear_mm: 0.03, angular_rad: 0.2618}
      quy_tac:                     # moi chi tiet khop quy tac DAU TIEN (ten = Label, glob)
        - {ten: [Base_housing], nhom: 01_Base}
        - {ten: [Rack_Shoulder], nhom: 05_Vai, xoay: {x: 90}, khung: Rack_Shoulder}
        - {ten: [Jaw_*_pad], nhom: 06_Kep, xoay: {x: 90}, khung: [x, y, z, ax, ay, az, do], hau_to: _TPU}
        - {ten: [Spacer_D], nhom: 04_Forearm, xoay: {x: 90}, tach_solid: true}
    - khung: Label doi tuong (lay Placement cua no) hoac placement [x,y,z, truc x,y,z, goc do]: dua chi tiet
      ve he toa do khung truoc khi xoay (vd. xi-lanh nghieng theo thanh rang).
    - xoay: quay quanh truc x, y, z (do) theo thu tu khai bao.
Ra: <stl>/<nhom>__<ten>[_<k>]<hau_to>.stl, dat tam giua ban in, day Z = 0. Xoa STL cu khong con trong danh sach.
"""

import fnmatch
import json
import sys
import time
from pathlib import Path

import FreeCAD as App
import MeshPart
import yaml

V = App.Vector


def khung(spec, OBJ):
    if spec is None:
        return App.Placement()
    if isinstance(spec, str):
        return App.Placement(OBJ[spec].Placement)
    x, y, z, ax, ay, az, goc = spec
    return App.Placement(V(x, y, z), App.Rotation(V(ax, ay, az), goc))


def xoay(spec):
    p = App.Placement()
    for truc, goc in (spec or {}).items():
        p = App.Placement(V(), App.Rotation({"x": V(1, 0, 0), "y": V(0, 1, 0), "z": V(0, 0, 1)}[truc], goc)).multiply(p)
    return p


def main():
    t0 = time.time()
    cfg_p = Path(sys.argv[sys.argv.index("--pass") + 1]).resolve()
    cfg = yaml.safe_load(cfg_p.read_text(encoding="utf-8"))
    goc = cfg_p.parent
    stl_dir = (goc / cfg["stl"]).resolve()
    stl_dir.mkdir(parents=True, exist_ok=True)
    x = cfg["xuat"]
    doc = App.openDocument(str((goc / cfg["fcstd"]).resolve()))
    if cfg.get("tu_the_goc"):  # chi doi trong bo nho, khong luu
        rest = json.loads((goc / cfg["tu_the_goc"]).read_text(encoding="utf-8"))
        for o in doc.Objects:
            if o.Name in rest:
                b, q = rest[o.Name]
                o.Placement = App.Placement(V(*b), App.Rotation(*q))
    OBJ = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
    luoi = x.get("luoi", {})
    ghi, chua = set(), []
    for o in OBJ.values():
        qt = next((q for q in x["quy_tac"] if any(fnmatch.fnmatch(o.Label, g) for g in q["ten"])), None)
        if qt is None:
            continue
        s = o.Shape.copy()
        s.Placement = xoay(qt.get("xoay")).multiply(khung(qt.get("khung"), OBJ).inverse()).multiply(s.Placement)
        sols = s.Solids if qt.get("tach_solid") and len(s.Solids) > 1 else [s]
        for k, so in enumerate(sols):
            ten = o.Label + (f"_{k + 1}" if len(sols) > 1 else "")
            so = so.copy()
            bb = so.BoundBox
            so.translate(V(-bb.Center.x, -bb.Center.y, -bb.ZMin))
            m = MeshPart.meshFromShape(Shape=so, LinearDeflection=luoi.get("linear_mm", 0.03),
                                       AngularDeflection=luoi.get("angular_rad", 0.2618), Relative=False)
            fn = f"{qt['nhom']}__{ten}{qt.get('hau_to', '')}.stl"
            m.write(str(stl_dir / fn))
            ghi.add(fn)
    for q in x["quy_tac"]:  # quy tac khong khop doi tuong nao -> bao (de sot do doi ten)
        if not any(fnmatch.fnmatch(lb, g) for lb in OBJ for g in q["ten"]):
            chua.append(q["ten"])
    cu = [f.name for f in stl_dir.glob("*.stl") if f.name not in ghi]
    for f in cu:
        (stl_dir / f).unlink()  # STL sinh tu lan truoc, khong con trong danh sach -> xoa de khong cat lop nham
    kq = {"so_stl": len(ghi), "quy_tac_khong_khop": chua, "xoa_stl_cu": cu, "s": round(time.time() - t0, 1)}
    (stl_dir / "_xuat-stl.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
    print("XUAT-STL", json.dumps(kq, ensure_ascii=False), flush=True)


main()
