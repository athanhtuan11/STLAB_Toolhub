"""Sua model FreeCAD bang script AN TOAN: chan doc dang do, sao luu, boolean co kiem, chi Luu khi dat.

Dung trong script sua model (gui qua RPC/MCP vao FreeCAD dang mo, hoac chay freecadcmd):
    import sys; sys.path.insert(0, r"D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/tools/robotics-cad/scripts")
    import safe_edit as se
    doc = App.getDocument("pushrod_arm")
    se.guard(doc, rest_json=".../pushrod_arm_rest.json")      # UndoCount == 0, dung tu the goc -> khong thi dung
    bk = se.backup(doc, "truoc-mai-servo")                    # freecad/backup/<ten>.<thoi gian>.<ghi chu>.FCStd
    shp, info = se.safe_cut(O["Gripper_frame"], dao, max_mm3=20)   # loi -> SafeEditError, KHONG doi gi
    se.apply(O["Gripper_frame"], shp)                         # giu nguyen Placement
    se.save(doc)                                              # chi goi khi moi kiem deu dat

Vi sao (da gap 2026-10-23): STEP linh kien (servo/N20 CyberBrick) loi BOP -> `cut` tra ve shape "hop le" nhung
bo 0 mm3 (that bai AM THAM). safe_cut so luong vat lieu bo di voi muc KY VONG doc lap:
    - `expect_mm3` neu nguoi viet script biet truoc, hoac
    - the tich giao tinh tren LUOI bang manifold3d (khong dung BOP, nen khong bi STEP loi danh lua).
mesh_mm: do min luoi uoc luong (mac dinh 0.02 mm; chi tiet lon / mat B-spline -> 0.2-0.3 cho nhanh,
noi rel_tol tuong ung). Lech -> thu lai boolean "fuzzy" (Part.Shape.cut(tools, tolerance), co tu OCC 7.x / FreeCAD 0.20) voi dung sai tang dan;
van lech -> SafeEditError (giu nguyen model). Khi do: dung dao cat don gian (hop, mat dun) thay cho STEP.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import FreeCAD as App
import MeshPart

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / ".pylib"))  # manifold3d (docs/COMMUNITY.md)
try:
    import manifold3d
    import numpy as np
except ImportError:  # khong co -> bat buoc truyen expect_mm3 hoac max_mm3
    manifold3d = None

FUZZY_MM = (0.0, 1e-4, 1e-3, 1e-2)  # 0 = boolean thuong; dung sai lon hon co the lam tron chi tiet nho < 0.01 mm


class SafeEditError(RuntimeError):
    pass


def guard(doc, rest_json=None, tol=1e-6):
    """Dung neu doc co thao tac chua Luu (vd. dang mo phong) hoac khong o tu the goc (rest.json)."""
    if doc.UndoCount:
        raise SafeEditError(f"{doc.Name}: {doc.UndoCount} thao tac chua Luu (dang mo phong?) - dung, hoi Tuan")
    if rest_json:
        import json
        rest = json.loads(Path(rest_json).read_text(encoding="utf-8"))
        lech = [o.Label for o in doc.Objects if o.Name in rest and not o.Placement.isSame(
            App.Placement(App.Vector(*rest[o.Name][0]), App.Rotation(*rest[o.Name][1])), tol)]
        if lech:
            raise SafeEditError(f"khong o tu the goc: {lech[:5]} - chay freecad/scripts/reset_rest_pose.py")


def backup(doc, note="truoc-sua"):
    d = Path(doc.FileName).parent / "backup"
    d.mkdir(exist_ok=True)
    f = d / f"{Path(doc.FileName).stem}.{time.strftime('%Y%m%d-%H%M%S')}.{note}.FCStd"
    if App.GuiUp:
        doc.saveCopy(str(f))
    else:
        # CLI: saveCopy cung BO du lieu hien thi -> backup mat GUI, save(gui_from=backup) khong con gi de chep lai
        # (2026-10-24: mat mau/an hien qua 4 lan sua). Sau guard() (UndoCount 0) file tren dia = noi dung doc.
        import shutil
        shutil.copy2(doc.FileName, f)
    return f


def _local(obj_or_shape, tool):
    """Dua ca 2 ve he toa do cua chi tiet (boolean tren shape Placement = goc, giong cach sua tay truoc day)."""
    if hasattr(obj_or_shape, "Shape"):
        plc = App.Placement(obj_or_shape.Placement)
        base = obj_or_shape.Shape.copy()
    else:
        plc = App.Placement(obj_or_shape.Placement)
        base = obj_or_shape.copy()
    base.Placement = App.Placement()
    t = tool.copy()
    t.transformShape(plc.inverse().toMatrix())
    return base, t, plc


def _manifold(shape, linear_mm):
    m = MeshPart.meshFromShape(Shape=shape, LinearDeflection=linear_mm, AngularDeflection=0.2618, Relative=False)
    pts, tris = m.Topology
    mf = manifold3d.Manifold(manifold3d.Mesh(np.array([tuple(p) for p in pts], dtype=np.float32),
                                             np.array(tris, dtype=np.uint32)))
    return mf if mf.status() == manifold3d.Error.NoError else None


def mesh_common_mm3(a, b, linear_mm=0.02):
    """The tich giao a & b tinh tren luoi (manifold3d). None neu khong co manifold3d hoac luoi khong kin."""
    if manifold3d is None or not a.BoundBox.intersect(b.BoundBox):
        return None if manifold3d is None else 0.0
    ma, mb = _manifold(a, linear_mm), _manifold(b, linear_mm)
    if ma is None or mb is None:
        return None
    return (ma ^ mb).volume()


def _boolean(op, obj_or_shape, tool, expect_mm3, max_mm3, rel_tol, abs_tol_mm3, solids, fuzzy, mesh_mm=0.02):
    base, t, plc = _local(obj_or_shape, tool)
    v0 = base.Volume
    uoc, nguon = expect_mm3, "expect_mm3"
    if uoc is None:
        g = mesh_common_mm3(base, t, mesh_mm)
        if g is not None:
            uoc, nguon = (g if op == "cut" else t.Volume - g), "luoi manifold3d"
    if uoc is None and max_mm3 is None:
        raise SafeEditError("khong uoc duoc luong thay doi (luoi khong kin / thieu manifold3d) - truyen expect_mm3 "
                            "hoac max_mm3")
    can = len(base.Solids) if solids is None else solids
    thu = []
    for fz in fuzzy:
        try:
            if op == "cut":
                r = base.cut([t], fz) if fz else base.cut(t)
            else:
                r = base.fuse([t], fz) if fz else base.fuse(t)
                r2 = r.removeSplitter()  # gop mat thua; tren mat B-spline co the LON NGUOC solid (gap 2026-10-23)
                if r2.isValid() and r2.Volume > 0 and abs(r2.Volume - r.Volume) < 1e-3 * max(1.0, abs(r.Volume)):
                    r = r2
        except Exception as e:  # OCC nem loi khi boolean hong
            thu.append({"fuzzy_mm": fz, "loi": str(e)[:120]})
            continue
        doi = (v0 - r.Volume) if op == "cut" else (r.Volume - v0)
        lech_ok = uoc is None or abs(doi - uoc) <= max(abs_tol_mm3, rel_tol * uoc)
        ok = (r.isValid() and len(r.Solids) == can and doi > 1e-3 and lech_ok
              and (max_mm3 is None or doi <= max_mm3))
        thu.append({"fuzzy_mm": fz, "doi_mm3": round(doi, 3), "valid": r.isValid(), "solid": len(r.Solids), "ok": ok})
        if ok:
            r.Placement = plc
            return r, {"op": op, "uoc_mm3": None if uoc is None else round(uoc, 3), "nguon_uoc": nguon,
                       "doi_mm3": round(doi, 3), "fuzzy_mm": fz, "thu": thu}
    raise SafeEditError(f"{op} khong dat (uoc {uoc and round(uoc, 3)} mm3 tu {nguon}, can {can} solid"
                        f"{'' if max_mm3 is None else f', toi da {max_mm3} mm3'}): {thu}"
                        " -> dung dao cat don gian (hop / mat dun) thay cho STEP linh kien")


def safe_cut(obj_or_shape, tool, expect_mm3=None, max_mm3=None, rel_tol=0.1, abs_tol_mm3=0.5, solids=None,
             fuzzy=FUZZY_MM, mesh_mm=0.02):
    """Tru `tool` khoi chi tiet. Tra (shape moi, info) - shape co Placement cu; KHONG gan vao object.
    Dat khi: isValid, so solid = truoc (hoac `solids`), luong bo di khop muc uoc (+-max(abs_tol, rel_tol*uoc)),
    khong vuot `max_mm3`. Loi -> SafeEditError."""
    return _boolean("cut", obj_or_shape, tool, expect_mm3, max_mm3, rel_tol, abs_tol_mm3, solids, fuzzy, mesh_mm)


def safe_fuse(obj_or_shape, tool, expect_mm3=None, max_mm3=None, rel_tol=0.1, abs_tol_mm3=0.5, solids=None,
              fuzzy=FUZZY_MM, mesh_mm=0.02):
    """Them `tool` vao chi tiet (vd. gan gan, vat). Luong them uoc = V(tool) - V(giao) tren luoi."""
    return _boolean("fuse", obj_or_shape, tool, expect_mm3, max_mm3, rel_tol, abs_tol_mm3, solids, fuzzy, mesh_mm)


def apply(obj, shape):
    obj.Shape = shape  # shape tu safe_cut/safe_fuse da mang Placement cu


def save(doc, gui_from=None):
    """Luu. Chay freecadcmd (khong GUI) thi FreeCAD BO du lieu hien thi (GuiDocument.xml, mau, thumbnail - do
    2026-10-24: 365 -> 108 file trong FCStd, hinh hoc giu nguyen) -> truyen gui_from=<file backup truoc khi sua>
    de chep lai: chi tiet cu giu mau/an hien, chi tiet moi nhan mau mac dinh."""
    doc.recompute()
    doc.save()
    if gui_from and not App.GuiUp:
        restore_gui(doc.FileName, gui_from)
    return doc.FileName


def restore_gui(fcstd, gui_from):
    """Chep file chi-hien-thi (co trong gui_from, khong co trong fcstd) vao fcstd. GUI phai DONG file nay."""
    import shutil
    import zipfile
    dst = Path(fcstd)
    with zipfile.ZipFile(dst) as d:   # dong handle truoc tmp.replace(dst) (Windows khoa file dang mo)
        have = set(d.namelist())
    tmp = dst.with_suffix(".tmp.FCStd")
    shutil.copy2(dst, tmp)
    with zipfile.ZipFile(gui_from) as src, zipfile.ZipFile(tmp, "a", zipfile.ZIP_DEFLATED) as z:
        add = [n for n in src.namelist() if n not in have]
        for n in add:
            z.writestr(n, src.read(n))
    tmp.replace(dst)
    return add
