"""Phan tich STL THEO HUONG IN truoc khi cat lop: phan nho can support + chi tiet nho can brim.

Vi sao (Tuan in pushrod-arm 2026-10-23): slicer chi bao "floating regions" khi co cum nhua roi han; phan NHO RA
(tai, go, mat duoi nam ngang) van dinh vao chi tiet nen KHONG bi bao -> slice.py khong bat support -> in hong.
Chi tiet nho / cao manh bong khoi ban -> can brim.

Dung: slice.py goi `phan_tich(stl, nguong)` cho moi STL; chay tay:
    "C:/Program Files/FreeCAD 1.1/bin/python.exe" scripts/printability.py <stl hoac thu muc stl>
Nguong: thresholds.yaml muc `print:` (overhang_deg chung voi check.py).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

MAC_DINH = {"overhang_deg": 45, "overhang_tol_deg": 2.0, "support_min_patch_mm2": 4.0, "min_patch_height_mm": 1.0, "bridge_max_mm": 5.0, "bed_tol_mm": 0.2,
            "brim_contact_max_mm2": 120.0, "brim_aspect_min": 2.5}


def doc_stl(p):
    """-> mang (n, 3, 3) toa do tam giac (STL nhi phan hoac ASCII)."""
    b = Path(p).read_bytes()
    n = int.from_bytes(b[80:84], "little") if len(b) >= 84 else 0
    if len(b) == 84 + 50 * n:
        rec = np.frombuffer(b[84:], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n)
        return rec["v"].astype(np.float64)
    v = [list(map(float, ln.split()[1:4])) for ln in b.decode("ascii", "replace").splitlines()
         if ln.strip().startswith("vertex")]
    return np.array(v, dtype=np.float64).reshape(-1, 3, 3)


def _cum(tri, chon):
    """Gom tam giac duoc chon thanh cum lien thong (chung dinh) -> list mang chi so."""
    idx = np.nonzero(chon)[0]
    if len(idx) == 0:
        return []
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    v = np.round(tri[idx].reshape(-1, 3), 3)
    _, vid = np.unique(v, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    nv = vid.max() + 1
    t = np.repeat(np.arange(len(idx)), 3)
    g = coo_matrix((np.ones(len(t)), (t, vid.ravel())), shape=(len(idx), nv)).tocsr()
    a = g @ g.T  # 2 tam giac chung >= 1 dinh -> noi
    k, lab = connected_components(a, directed=False)
    return [idx[lab == i] for i in range(k)]


def phan_tich(stl, nguong=None):
    ng = dict(MAC_DINH, **(nguong or {}))
    tri = doc_stl(stl)
    z0 = tri[:, :, 2].min()
    tri = tri - np.array([0, 0, z0])                       # day = ban in
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    cr = np.cross(e1, e2)
    s2 = np.linalg.norm(cr, axis=1)
    dt = s2 / 2
    ok = s2 > 1e-9
    nz = np.where(ok, cr[:, 2] / np.where(ok, s2, 1), 0)
    zmin, zmax = tri[:, :, 2].min(axis=1), tri[:, :, 2].max(axis=1)
    tren_ban = zmax <= ng["bed_tol_mm"]
    # mat up xuong, nghieng it hon (overhang_deg - tol) so voi phuong ngang -> can do (khong tinh mat nam tren ban).
    # tol: vat dung 45 do in duoc khong support, luoi lam lech vai phan do
    goc = ng["overhang_deg"] - ng["overhang_tol_deg"]
    nho = ok & ~tren_ban & (-nz > np.cos(np.radians(goc)))
    cum = []
    for c in _cum(tri, nho):
        pts = tri[c].reshape(-1, 3)
        dx, dy = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
        dien_tich = float(dt[c].sum())
        # bac cau: dai hep (vd. noc lo ngang D3) slicer tu bac duoc; chi tinh cum rong va du lon
        cao_cum = float(zmax[c].max())  # vat nho sat ban (vd. vat chong chan voi 0.5 mm) -> bo qua
        if (dien_tich >= ng["support_min_patch_mm2"] and min(dx, dy) > ng["bridge_max_mm"]
                and cao_cum >= ng["min_patch_height_mm"]):
            cum.append({"mm2": round(dien_tich, 1), "rong_mm": round(min(dx, dy), 1),
                        "z_mm": round(float(zmin[c].min()), 1)})
    tiep_xuc = float(dt[tren_ban & (nz < -0.99)].sum())
    xy = tri.reshape(-1, 3)
    w = sorted([float(np.ptp(xy[:, 0])), float(np.ptp(xy[:, 1]))])
    cao = float(np.ptp(xy[:, 2]))
    ti_le = cao / max(w[0], 1e-6)
    ly_do_brim = []
    if tiep_xuc < ng["brim_contact_max_mm2"]:
        ly_do_brim.append(f"chan nho {tiep_xuc:.0f} mm2")
    if ti_le >= ng["brim_aspect_min"]:
        ly_do_brim.append(f"cao/manh {cao:.0f}/{w[0]:.0f} mm")
    return {"stl": Path(stl).name, "can_support": bool(cum), "cum_nho": sorted(cum, key=lambda c: -c["mm2"])[:5],
            "tiep_xuc_mm2": round(tiep_xuc, 1), "cao_mm": round(cao, 1), "can_brim": bool(ly_do_brim),
            "ly_do_brim": ly_do_brim}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    p = Path(sys.argv[1])
    for f in sorted(p.glob("*.stl")) if p.is_dir() else [p]:
        r = phan_tich(f)
        if r["can_support"] or r["can_brim"]:
            print(json.dumps(r, ensure_ascii=False))
