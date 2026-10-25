"""Xuat STL theo HUONG IN tu file FreeCAD, theo muc `export:` trong print.yaml (dung chung moi du an).

Chay: "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" scripts/export-stl.py --pass <print.yaml>
(thuong goi qua prepare-print.py). Chi DOC file .FCStd da luu, khong sua.

print.yaml:
    fcstd: ../model.FCStd          # tuong doi theo file yaml
    rest_pose: ../rest.json        # tuy chon: {Name: [[x,y,z],[q0,q1,q2,q3]]} -> dua ve tu the goc truoc khi xuat
                                   # (file luu luc dang mo phong van xuat dung)
    export:
      mesh: {linear_mm: 0.03, angular_rad: 0.2618}
      rules:                       # moi chi tiet khop quy tac DAU TIEN (names = Label, glob)
        - {names: [Base_housing], group: 01_Base}
        - {names: [Rack_Shoulder], group: 05_Shoulder, rotate: {x: 90}, frame: Rack_Shoulder}
        - {names: [Jaw_*_pad], group: 06_Gripper, rotate: {x: 90}, frame: [x, y, z, ax, ay, az, deg], suffix: _TPU}
        - {names: [Spacer_D], group: 04_Forearm, rotate: {x: 90}, split_solids: true}
    - frame: Label doi tuong (lay Placement cua no) hoac placement [x,y,z, truc x,y,z, goc do]: dua chi tiet
      ve he toa do khung truoc khi xoay (vd. xi-lanh nghieng theo thanh rang).
    - rotate: quay quanh truc x, y, z (do) theo thu tu khai bao.
    - support: true -> CHI GHI CHU "Tuan them support trong slicer" (danh sach `support_trong_slicer` trong ket qua).
      KHONG dung support vao STL nua (Tuan 2026-10-25: support tu ve lap lo truc Worm + ranh thanh rang Housing
      -> "support in toi se tu them trong phan mem slice. tu gio tro di khong can them support vo").
Ra: <stl>/<group>__<Label>[_<k>]<suffix>.stl, dat tam giua ban in, day Z = 0. Xoa STL cu khong con trong danh sach.
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
    goc = (cfg_p.parent / cfg.get("data_dir", ".")).resolve()  # FCStd/STL co the o ngoai repo
    stl_dir = (goc / cfg["stl"]).resolve()
    stl_dir.mkdir(parents=True, exist_ok=True)
    x = cfg["export"]
    doc = App.openDocument(str((goc / cfg["fcstd"]).resolve()))
    if cfg.get("rest_pose"):  # chi doi trong bo nho, khong luu
        rest = json.loads((goc / cfg["rest_pose"]).read_text(encoding="utf-8"))
        for o in doc.Objects:
            if o.Name in rest:
                b, q = rest[o.Name]
                o.Placement = App.Placement(V(*b), App.Rotation(*q))
    OBJ = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
    luoi = x.get("mesh", {})
    ghi, chua, sp = set(), [], []
    for o in OBJ.values():
        qt = next((q for q in x["rules"] if any(fnmatch.fnmatch(o.Label, g) for g in q["names"])), None)
        if qt is None:
            continue
        s = o.Shape.copy()
        s.Placement = xoay(qt.get("rotate")).multiply(khung(qt.get("frame"), OBJ).inverse()).multiply(s.Placement)
        sols = s.Solids if qt.get("split_solids") and len(s.Solids) > 1 else [s]
        for k, so in enumerate(sols):
            ten = o.Label + (f"_{k + 1}" if len(sols) > 1 else "")
            so = so.copy()
            bb = so.BoundBox
            so.translate(V(-bb.Center.x, -bb.Center.y, -bb.ZMin))
            m = MeshPart.meshFromShape(Shape=so, LinearDeflection=luoi.get("linear_mm", 0.03),
                                       AngularDeflection=luoi.get("angular_rad", 0.2618), Relative=False)
            fn = f"{qt['group']}__{ten}{qt.get('suffix', '')}.stl"
            if qt.get("support"):
                sp.append(fn)  # Tuan to support trong Bambu Studio (khong dung vao STL)
            m.write(str(stl_dir / fn))
            ghi.add(fn)
    for q in x["rules"]:  # quy tac khong khop doi tuong nao -> bao (de sot do doi ten)
        if not any(fnmatch.fnmatch(lb, g) for lb in OBJ for g in q["names"]):
            chua.append(q["names"])
    cu = [f.name for f in stl_dir.glob("*.stl") if f.name not in ghi]
    for f in cu:
        (stl_dir / f).unlink()  # STL sinh tu lan truoc, khong con trong danh sach -> xoa de khong cat lop nham
    kq = {"so_stl": len(ghi), "quy_tac_khong_khop": chua, "xoa_stl_cu": cu, "support_trong_slicer": sp,
          "s": round(time.time() - t0, 1)}
    (stl_dir / "_export-stl.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
    print("XUAT-STL", json.dumps(kq, ensure_ascii=False), flush=True)


main()
