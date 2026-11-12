"""Phan tich hinh hoc STL cho buoc Toi uu in (Toolhub)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np


def _import_printability():
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    import printability  # type: ignore
    return printability


class _UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.r[ra] < self.r[rb]:
            self.p[ra] = rb
        elif self.r[ra] > self.r[rb]:
            self.p[rb] = ra
        else:
            self.p[rb] = ra
            self.r[ra] += 1


def _component_count(tri):
    if len(tri) == 0:
        return 0
    v = np.round(tri.reshape(-1, 3), 4)
    _, vid = np.unique(v, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    nv = int(vid.max()) + 1
    uf = _UF(nv)
    for a, b, c in vid:
        uf.union(int(a), int(b))
        uf.union(int(b), int(c))
    tri_roots = set(uf.find(int(t[0])) for t in vid)
    return len(tri_roots)


def _holes(tri):
    if len(tri) == 0:
        return 0
    v = np.round(tri.reshape(-1, 3), 4)
    _, vid = np.unique(v, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    V = int(vid.max()) + 1
    edges = np.sort(np.concatenate([vid[:, [0, 1]], vid[:, [1, 2]], vid[:, [2, 0]]]), axis=1)
    E = int(np.unique(edges, axis=0).shape[0])
    F = int(len(tri))
    shells = _component_count(tri)
    chi = V - E + F
    g = (2 * shells - chi) / 2.0
    return max(0, int(round(g)))


def _hinh(tri):
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    cr = np.cross(e1, e2)
    s2 = np.linalg.norm(cr, axis=1)
    ok = s2 > 1e-9
    nz = np.where(ok, cr[:, 2] / np.where(ok, s2, 1), 0)
    return ok, nz, s2 / 2, tri[:, :, 2].min(axis=1), tri[:, :, 2].max(axis=1)


def _phan_tich_basic(tri):
    """Fallback khong can scipy: tinh chan, bbox va phat hien mat nho ra lon."""
    z0 = float(tri[:, :, 2].min()) if len(tri) else 0.0
    tri = tri - np.array([0, 0, z0])
    ok, nz, dt, zmin, zmax = _hinh(tri)
    tren_ban = zmax <= 0.2
    tiep_xuc = float(dt[tren_ban & (nz < -0.99)].sum())
    xy = tri.reshape(-1, 3) if len(tri) else np.zeros((0, 3))
    cao = float(np.ptp(xy[:, 2])) if len(xy) else 0.0
    # mat huong xuong (nz < -0.3) va khong sat ban -> cum nho ra
    down = ok & (zmax > 0.6) & (nz < -0.3)
    can_support = False
    max_over = 0.0
    if np.any(down):
        # chia theo muc zmax gan nhau
        ids = np.nonzero(down)[0]
        levels = {}
        for i in ids:
            key = round(float(zmax[i]), 1)
            levels.setdefault(key, []).append(i)
        for group in levels.values():
            idx = np.array(group, dtype=int)
            area = float(dt[idx].sum())
            if area >= 4.0:
                can_support = True
                if area > max_over:
                    max_over = area
    return {"can_support": bool(can_support), "cum_nho": ([{"mm2": max_over}] if max_over > 0 else []),
            "tiep_xuc_mm2": round(tiep_xuc, 1), "cao_mm": round(cao, 1)}


def features(stl_path):
    pr = _import_printability()
    tri = pr.doc_stl(stl_path)
    z0 = float(tri[:, :, 2].min()) if len(tri) else 0.0
    tri = tri - np.array([0, 0, z0])
    try:
        ph = pr.phan_tich(stl_path)
    except Exception:
        ph = _phan_tich_basic(tri)
    cum = ph.get("cum_nho") or []
    max_overhang_mm2 = max((float(c.get("mm2") or 0) for c in cum), default=0.0)
    xy = tri.reshape(-1, 3) if len(tri) else np.zeros((0, 3))
    bbox = [float(np.ptp(xy[:, 0])) if len(xy) else 0.0,
            float(np.ptp(xy[:, 1])) if len(xy) else 0.0,
            float(np.ptp(xy[:, 2])) if len(xy) else 0.0]
    short_xy = min(bbox[0], bbox[1]) if bbox[0] and bbox[1] else 0.0
    aspect = (bbox[2] / short_xy) if short_xy > 1e-9 else 0.0
    zmax = float(tri[:, :, 2].max()) if len(tri) else 0.0
    _, nz, dt, _, zmx = _hinh(tri)
    ok = np.ones(len(tri), dtype=bool) if len(tri) else np.zeros(0, dtype=bool)
    top_flat_mm2 = float(dt[ok & (nz > 0.99) & (zmx >= zmax - 0.2)].sum()) if len(tri) else 0.0
    total_area = float(dt[ok].sum()) if len(tri) else 0.0
    curved_area = float(dt[ok & (np.abs(nz) >= 0.5) & (np.abs(nz) <= 0.985)].sum()) if len(tri) else 0.0
    curved_frac = (curved_area / total_area) if total_area > 1e-12 else 0.0
    return {
        "can_support": bool(ph.get("can_support")),
        "contact_mm2": float(ph.get("tiep_xuc_mm2") or 0),
        "height_mm": float(ph.get("cao_mm") or 0),
        "aspect": float(aspect),
        "max_overhang_mm2": float(max_overhang_mm2),
        "bbox_mm": [round(bbox[0], 3), round(bbox[1], 3), round(bbox[2], 3)],
        "small": bool(max(bbox[0], bbox[1]) < 20),
        "top_flat_mm2": round(top_flat_mm2, 3),
        "curved_frac": float(curved_frac),
        "holes": _holes(tri),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    p = Path(sys.argv[1])
    for f in sorted(p.glob("*.stl")) if p.is_dir() else [p]:
        print(json.dumps(features(f), ensure_ascii=False))
