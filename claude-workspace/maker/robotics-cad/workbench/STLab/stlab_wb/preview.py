"""Xem HUONG IN ngay trong 3D: chi tiet da chon -> xoay theo quy tac export (print.yaml), dat tren ban A1 ao canh model.

Chi ve vao scenegraph (Coin), KHONG them object vao tai lieu -> khong lam doi file / UndoCount.
To do: mat up xuong doc hon (overhang_deg - tol) va khong sat ban = nho ra (xem nhanh; ket qua chinh van la
printability.py trong Chuan bi in).
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
import yaml
from pivy import coin

from . import core

_node = {}  # doc.Name -> (view, SoSeparator)


def clear(doc=None):
    doc = doc or App.ActiveDocument
    if doc and doc.Name in _node:
        view, n = _node.pop(doc.Name)
        try:
            view.getSceneGraph().removeChild(n)
        except Exception:
            pass
        return True
    return False


def _thresholds():
    t = yaml.safe_load((core.RCAD / "thresholds.yaml").read_text(encoding="utf-8"))
    p = t.get("print") or {}
    return t.get("overhang_deg", 45) - p.get("overhang_tol_deg", 2.0), p.get("bed_near_mm", 0.6)


def _mesh_node(shape, color, deg, bed_near):
    pts, tris = shape.tessellate(0.1)
    lim = -math.cos(math.radians(deg))
    coords, idx, mats, n_over = coin.SoCoordinate3(), [], [], 0
    coords.point.setValues(0, len(pts), [(p.x, p.y, p.z) for p in pts])
    for a, b, c in tris:
        pa, pb, pc = pts[a], pts[b], pts[c]
        nrm = (pb - pa).cross(pc - pa)
        ln = nrm.Length
        over = ln > 1e-12 and nrm.z / ln < lim and min(pa.z, pb.z, pc.z) > bed_near
        n_over += over
        mats.append(1 if over else 0)
        idx += [a, b, c, -1]
    sep = coin.SoSeparator()
    mat = coin.SoMaterial()
    mat.diffuseColor.setValues(0, 2, [color, (0.9, 0.15, 0.1)])
    bind = coin.SoMaterialBinding()
    bind.value = coin.SoMaterialBinding.PER_FACE_INDEXED
    fs = coin.SoIndexedFaceSet()
    fs.coordIndex.setValues(0, len(idx), idx)
    fs.materialIndex.setValues(0, len(mats), mats)
    hints = coin.SoShapeHints()
    hints.vertexOrdering = coin.SoShapeHints.COUNTERCLOCKWISE
    hints.creaseAngle = 0.5
    for x in (hints, mat, bind, coords, fs):
        sep.addChild(x)
    return sep, n_over


def _bed(w, d):
    sep = coin.SoSeparator()
    mat = coin.SoMaterial()
    mat.diffuseColor = (0.55, 0.6, 0.65)
    mat.transparency = 0.6
    tr = coin.SoTranslation()
    tr.translation = (0, 0, -0.6)
    cube = coin.SoCube()
    cube.width, cube.height, cube.depth = w, d, 1.0
    sep.addChild(mat)
    sep.addChild(tr)
    sep.addChild(cube)
    # khung vien ban
    ln = coin.SoSeparator()
    lc = coin.SoBaseColor()
    lc.rgb = (0.2, 0.2, 0.2)
    co = coin.SoCoordinate3()
    co.point.setValues(0, 5, [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0),
                              (-w / 2, -d / 2, 0)])
    ls = coin.SoLineSet()
    ls.numVertices.setValue(5)
    for x in (lc, co, ls):
        ln.addChild(x)
    sep.addChild(ln)
    return sep


def show(objs, project):
    """-> (so chi tiet ve, [(Label, ly do bo qua)], so tam giac nho ra)."""
    doc = objs[0].Document
    clear(doc)
    deg, bed_near = _thresholds()
    W, D, _ = core.BED_MM
    shapes, skip = [], []
    for o in objs:
        s, q = core.print_shape(o, project)
        if s is None:
            skip.append((o.Label, "không khớp quy tắc export trong print.yaml"))
        else:
            shapes.append((o.Label, s))
    if not shapes:
        return 0, skip, 0
    # xep thanh hang tren ban ao (chi de nhin; xep ban that do slicer lam)
    gap, x, row_y, row_h, placed = 8.0, -W / 2, -D / 2, 0.0, []
    for lb, s in shapes:
        bb = s.BoundBox
        if x + bb.XLength > W / 2 and placed:
            x, row_y, row_h = -W / 2, row_y + row_h + gap, 0.0
        s.translate(App.Vector(x - bb.XMin, row_y - bb.YMin, 0))
        x += bb.XLength + gap
        row_h = max(row_h, bb.YLength)
        placed.append((lb, s))
    root = coin.SoSeparator()
    root.setName("STLab_PrintPreview")
    # dat ban ao ben phai toan bo model
    all_bb = App.BoundBox()
    for o in core.parts(doc):
        all_bb.add(o.Shape.BoundBox)
    off = coin.SoTranslation()
    off.translation = (all_bb.XMax + 40 + W / 2 if all_bb.isValid() else 0,
                       all_bb.Center.y if all_bb.isValid() else 0, all_bb.ZMin if all_bb.isValid() else 0)
    root.addChild(off)
    root.addChild(_bed(W, D))
    n_over = 0
    for lb, s in placed:
        node, n = _mesh_node(s, (0.25, 0.7, 0.85), deg, bed_near)  # xanh: khac mau model
        root.addChild(node)
        n_over += n
    view = Gui.ActiveDocument.ActiveView
    view.getSceneGraph().addChild(root)
    _node[doc.Name] = (view, root)
    view.fitAll()
    return len(placed), skip, n_over
