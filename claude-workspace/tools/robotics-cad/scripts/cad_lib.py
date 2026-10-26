"""Ham dung hinh dung chung cho script FreeCAD cua STLab (ra soat quy trinh 2026-10-26, docs/reports/workflow-improvement.md).

Vi sao: truoc day moi script tu chep box/xcyl/rrect/giot_nuoc; `box` co 3 kieu tham so khac nhau giua cac file
((x0,y0,z0,x1,y1,z1) | (x0,x1,y0,y1,z0,z1) | (x0,y0,z0,dai,rong,cao)) -> chep nham = hinh sai khong bao loi.
Quy uoc o day: tham so DAT TEN, khoang toa do la cap (dau, cuoi) theo truc, don vi mm.
    import sys; sys.path.insert(0, ".../tools/robotics-cad/scripts"); from cad_lib import *
Test: "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode -P tools/robotics-cad/tests -t test_cad_lib
Du an cu (pushrod-arm history, build_car.py) giu ham rieng - khong sua script da chay; dung thu vien nay cho script MOI.
"""
import math

import FreeCAD as App
import Part

V = App.Vector
AXES = {"x": V(1, 0, 0), "y": V(0, 1, 0), "z": V(0, 0, 1)}
_OTHER = {"x": ("y", "z"), "y": ("x", "z"), "z": ("x", "y")}

# Khe lap ghep chuan STLab (Tuan chot - xem memory khe-lap-ghep-co-ngot, pushrod-arm 2026-10-24/25), mm
FIT = 0.2          # lap ghep thuong (moi ben)
SLIDE = 0.3        # ranh truot, banh rang an khop (moi ben)
PIN = 0.3          # chot xuyen lo (moi ben): lo = chot + 2*PIN


def _span(ab):
    a, b = float(ab[0]), float(ab[1])
    if a == b:
        raise ValueError("khoang rong: %r" % (ab,))
    return (a, b) if a < b else (b, a)


def _pt(axis, t, at):
    """Diem tren truc `axis` tai toa do t; 2 truc con lai lay tu `at` theo thu tu _OTHER (x:(y,z) y:(x,z) z:(x,y))."""
    c = {axis: t, _OTHER[axis][0]: at[0], _OTHER[axis][1]: at[1]}
    return V(c["x"], c["y"], c["z"])


def pos(solid):
    """Khoi dun tu Part.Face(da giac) co the AM the tich (thu tu dinh nguoc) -> boolean sau do hong am tham."""
    return solid if solid.Volume >= 0 else solid.reversed()


def box(*, x, y, z):
    """Hop theo khoang: box(x=(0, 10), y=(-2, 2), z=(0, 5)). Thu tu dau/cuoi khong quan trong."""
    (x0, x1), (y0, y1), (z0, z1) = _span(x), _span(y), _span(z)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, axis, span, at=(0.0, 0.0)):
    """Tru ban kinh r doc truc 'x'|'y'|'z' tu span[0] toi span[1]; at = toa do 2 truc con lai (x:(y,z) y:(x,z) z:(x,y))."""
    a0, a1 = _span(span)
    return Part.makeCylinder(r, a1 - a0, _pt(axis, a0, at), AXES[axis])


def rrect(axis, span, half, r, at=(0.0, 0.0)):
    """Lang tru chu nhat bo 4 goc doc `axis`: half = (nua canh truc thu 1, nua canh truc thu 2) theo _OTHER, ban kinh r."""
    u, w = _OTHER[axis]
    hu, hw = half
    if not 0 < r <= min(hu, hw):
        raise ValueError("r phai trong (0, min(half)]")
    cu, cw = at

    def bx(du, dw):
        return box(**{axis: span, u: (cu - du, cu + du), w: (cw - dw, cw + dw)})
    s = bx(hu - r, hw).fuse(bx(hu, hw - r))
    for su in (-1, 1):
        for sw in (-1, 1):
            s = s.fuse(cyl(r, axis, span, (cu + su * (hu - r), cw + sw * (hw - r))))
    return s.removeSplitter()


def teardrop(r, axis, span, at, tip=1, inset=0.98):
    """Lo NGANG tu in khong can do (in theo +Z): tron + mui 45 do huong z*tip. axis 'x'|'y' (lo doc Z thi dung cyl).
    at = (toa do truc ngang con lai, z tam). Mui ve tam giac lot `inset` vao trong duong tron (tranh tiep tuyen trung mat)."""
    if axis not in ("x", "y"):
        raise ValueError("teardrop chi cho lo ngang (axis x|y)")
    a0, a1 = _span(span)
    other, zc = at
    c45 = inset * r * math.cos(math.radians(45))
    dz = tip * r * math.sqrt(2)

    def p(o, z):
        return _pt(axis, a0, (o, z))
    tri = Part.Face(Part.makePolygon([p(other + c45, zc + tip * c45), p(other, zc + dz),
                                      p(other - c45, zc + tip * c45), p(other + c45, zc + tip * c45)]))
    return cyl(r, axis, (a0, a1), at).fuse(pos(tri.extrude(AXES[axis] * (a1 - a0)))).removeSplitter()


def local(obj, frame):
    """Hinh cua obj trong he `frame` (App.Placement) - chi doi Placement, hinh hoc giu nguyen."""
    s = obj.Shape.copy()
    s.Placement = frame.inverse().multiply(s.Placement)
    return s


def put(obj, shape, frame):
    """Gan shape (dung trong he `frame`) vao obj. obj.Shape = shape LAY Placement cua shape -> phai gop frame*pl
    (bai hoc 2026-10-25: gan thang lam chi tiet nhay sai cho)."""
    pl = shape.Placement
    obj.Placement = App.Placement()
    obj.Shape = shape
    obj.Placement = frame.multiply(pl)
