# Kiem va cham NHANH cho quet khop / mo phong (Tuan 2026-10-24: "kiem tra qua lau").
# Chia luoi moi chi tiet 1 LAN (manifold3d), moi tu the chi nhan ma tran vi tri -> giao khoi ~ms/cap
# (B-rep common/distToShape: 0,1-12 s/cap, do 2026-10-24 tren pushrod-arm).
# Linh kien STEP luoi ho (N20, servo) -> bao loi tung manh nhu check.py (hoi beo, khong bo sot).
#
#   import fast_collide
#   fc = fast_collide.Collider({lbl: obj, ...})     # goi khi model DANG o tu the goc
#   ... doi Placement cac obj ...
#   fc.hits([("Housing_Shoulder", "Boom001"), ...])  # -> ["a x b: 12.3 mm3", ...]
#   fc.gap("Worm_Shoulder", "Pinion_WormWheel_Shoulder")  # khe nho nhat (mm), None neu > xa
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".pylib"))
import manifold3d  # noqa: E402
import MeshPart  # noqa: E402


def _mesh(shape, lin, ang):
    return MeshPart.meshFromShape(Shape=shape, LinearDeflection=lin, AngularDeflection=ang)


def _manifold(shape, lin=0.05, ang=0.2618, hull_fallback=True):
    m = _mesh(shape, lin, ang)
    mm = manifold3d.Mesh(vert_properties=np.array([(p.x, p.y, p.z) for p in m.Topology[0]], dtype=np.float32),
                         tri_verts=np.array(m.Topology[1], dtype=np.uint32))
    mm.merge()
    mf = manifold3d.Manifold(mm)
    if mf.status() == manifold3d.Error.NoError and not mf.is_empty():
        return mf, False
    if not hull_fallback:
        return None, False
    manh = [np.array([(p.x, p.y, p.z) for p in c.Topology[0]]) for c in m.getSeparateComponents()]
    return manifold3d.Manifold.batch_boolean(
        [manifold3d.Manifold.hull_points(p) for p in manh if len(p) >= 4], manifold3d.OpType.Add), True


def _m34(pl):
    m = pl.toMatrix()
    return np.array([[m.A11, m.A12, m.A13, m.A14], [m.A21, m.A22, m.A23, m.A24], [m.A31, m.A32, m.A33, m.A34]],
                    dtype=np.float64)


class Collider:
    def __init__(self, objs, lin=0.05, ang=0.2618, min_mm3=0.5):
        """objs: {label: FreeCAD object}. Luu luoi o vi tri HIEN TAI (tu the goc)."""
        self.objs, self.min = objs, min_mm3
        self.base, self.pl0, self.hull = {}, {}, set()
        for lbl, o in objs.items():
            mf, hull = _manifold(o.Shape, lin, ang)
            if mf is None:
                continue
            self.base[lbl], self.pl0[lbl] = mf, o.Placement.inverse()
            if hull:
                self.hull.add(lbl)
        self._cur = {}

    def _now(self, lbl):
        """Manifold tai vi tri hien tai = (Placement hien tai * Placement goc^-1) * luoi goc; cache theo Placement."""
        pl = self.objs[lbl].Placement
        key = tuple(round(x, 6) for x in (*pl.Base, *pl.Rotation.Q))
        c = self._cur.get(lbl)
        if c is None or c[0] != key:
            c = (key, self.base[lbl].transform(_m34(pl.multiply(self.pl0[lbl]))))
            self._cur[lbl] = c
        return c[1]

    def volume(self, a, b):
        if a not in self.base or b not in self.base:
            return None
        ma, mb = self._now(a), self._now(b)
        (ax0, ay0, az0), (ax1, ay1, az1) = np.split(np.array(ma.bounding_box()), 2)
        (bx0, by0, bz0), (bx1, by1, bz1) = np.split(np.array(mb.bounding_box()), 2)
        if ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0 or az1 < bz0 or bz1 < az0:
            return 0.0
        return (ma ^ mb).volume()

    def gap(self, a, b, xa=5.0):
        """Khe nho nhat (mm) neu < xa, nguoc lai None. Giu xa <= ~20 mm: 50 mm do 2026-10-24 tra sai/treo."""
        if a not in self.base or b not in self.base:
            return None
        d = self._now(a).min_gap(self._now(b), xa)
        return None if d >= xa - 1e-9 else d

    def hits(self, pairs):
        out = []
        for a, b in pairs:
            v = self.volume(a, b)
            if v is not None and v > self.min:
                tag = " (bao loi)" if a in self.hull or b in self.hull else ""
                out.append("%s x %s: %.1f mm3%s" % (a, b, v, tag))
        return out
