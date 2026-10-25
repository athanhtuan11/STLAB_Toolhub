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

MAC_DINH = {"overhang_deg": 45, "overhang_tol_deg": 2.0, "support_min_patch_mm2": 4.0, "min_patch_height_mm": 1.0, "bridge_max_mm": 5.0,
            "bridge_closed_max_mm": 8.0, "bed_tol_mm": 0.2,
            "brim_contact_max_mm2": 120.0, "brim_aspect_min": 2.5,
            "support_gap_max_mm": 0.6,
            "bed_near_mm": 0.6, "short_overhang_mm": 2.5}


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


def _rong_dai(tri):
    """Be rong dai nho ra tren hinh chieu XY = 2 * dien tich / chu vi bien (dai hep: ren, vat nho, mep lo)."""
    xy = tri[:, :, :2]
    a = 0.5 * np.abs(np.cross(xy[:, 1] - xy[:, 0], xy[:, 2] - xy[:, 0])).sum()
    e = np.round(np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), 4)
    e = np.sort(e.view([("x", "f8"), ("y", "f8"), ("z", "f8")]).reshape(-1, 2), axis=1)
    u, c = np.unique(e, return_counts=True, axis=0)
    b = u[c == 1]
    if len(b) == 0:
        return float("inf")
    pts = np.array(b.tolist())  # (k, 2, 3)
    chu_vi = np.linalg.norm(pts[:, 1, :2] - pts[:, 0, :2], axis=1).sum()
    return 2 * a / chu_vi if chu_vi > 0 else float("inf")


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


def _mai_lo_kin(tri, nz, c):
    """Cum c la MAI LO KIN: moi dinh bien cua cum deu cham thanh dung DI XUONG (vd. day lo truc Ø5,9 in mieng lo
    xuong ban - Worm pushrod-arm 2026-10-25: support tu ve lap kin lo). Mai ngoai (go, vanh) co bien cham thanh di LEN."""
    v = np.round(tri.reshape(-1, 3), 3)
    _, vid = np.unique(v, axis=0, return_inverse=True)
    vid = vid.reshape(-1, 3)
    e = np.sort(np.concatenate([vid[c][:, [0, 1]], vid[c][:, [1, 2]], vid[c][:, [2, 0]]]), axis=1)
    u, n = np.unique(e, return_counts=True, axis=0)
    bien = np.unique(u[n == 1])
    if len(bien) == 0:
        return False
    zc = tri[c][:, :, 2].max()
    tuong = np.abs(nz) < 0.3                                      # thanh gan dung
    xuong = tuong & (tri[:, :, 2].min(axis=1) < zc - 0.2)         # keo xuong duoi mai
    co = np.zeros(vid.max() + 1, dtype=bool)
    co[vid[xuong].ravel()] = True
    return bool(co[bien].mean() >= 0.95)


def _co_do_duoi(tri, nz, idx, gap, khoi=2000):
    """Chi so (trong idx) cac tam giac co mat NGUA (nz > 0.3) nam ngay duoi tam cua no, cach <= gap mm theo Z."""
    if len(idx) == 0:
        return idx
    up = tri[nz > 0.3]
    if len(up) == 0:
        return idx[:0]
    a, b, c = up[:, 0], up[:, 1], up[:, 2]
    v0, v1 = (b - a)[:, :2], (c - a)[:, :2]
    d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
    den = d00 * d11 - d01 * d01
    hop = np.abs(den) > 1e-12
    a, v0, v1, d00, d01, d11, den = a[hop], v0[hop], v1[hop], d00[hop], d01[hop], d11[hop], den[hop]
    za, zb, zc = up[hop][:, 0, 2], up[hop][:, 1, 2], up[hop][:, 2, 2]
    ra = []
    for s in range(0, len(idx), khoi):
        cen = tri[idx[s:s + khoi]].mean(axis=1)                        # (m, 3)
        v2 = cen[:, None, :2] - a[None, :, :2]                         # (m, n, 2)
        d20, d21 = (v2 * v0[None]).sum(2), (v2 * v1[None]).sum(2)
        v = (d11[None] * d20 - d01[None] * d21) / den[None]
        w = (d00[None] * d21 - d01[None] * d20) / den[None]
        u = 1 - v - w
        trong = (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6)
        z = u * za[None] + v * zb[None] + w * zc[None]
        kc = cen[:, None, 2] - z
        ra.append((trong & (kc > 1e-3) & (kc <= gap)).any(axis=1))
    return idx[np.concatenate(ra)]


def _hinh(tri):
    e1, e2 = tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]
    cr = np.cross(e1, e2)
    s2 = np.linalg.norm(cr, axis=1)
    ok = s2 > 1e-9
    nz = np.where(ok, cr[:, 2] / np.where(ok, s2, 1), 0)
    return ok, nz, s2 / 2, tri[:, :, 2].min(axis=1), tri[:, :, 2].max(axis=1)


def vung_can_do(tri, ng):
    """Cac cum mat nho ra CAN DO (phan_tich) -> (thong tin cum, chi so tam giac)."""
    ok, nz, dt, zmin, zmax = _hinh(tri)
    # mat up xuong, nghieng it hon (overhang_deg - tol) so voi phuong ngang; tol: vat dung 45 do van in duoc.
    # mat sat ban (zmax <= bed_near_mm): lop dau ep xuong ban in duoc
    goc = ng["overhang_deg"] - ng["overhang_tol_deg"]
    nho = ok & (zmax > ng["bed_near_mm"]) & (-nz > np.cos(np.radians(goc)))
    # da co do ngay ben duoi (khe <= support_gap_max_mm)
    nho[_co_do_duoi(tri, nz, np.nonzero(nho)[0], ng["support_gap_max_mm"])] = False
    cum, chon = [], []
    for c in _cum(tri, nho):
        pts = tri[c].reshape(-1, 3)
        dx, dy = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
        dien_tich = float(dt[c].sum())
        rong_dai = _rong_dai(tri[c])
        # bo qua: nho / hep (bac cau duoc: noc lo ngang) / sat ban / dai hep (ren, vat nho - moi lop nho < 1 vet)
        cau = ng["bridge_max_mm"]
        if min(dx, dy) <= ng["bridge_closed_max_mm"] and _mai_lo_kin(tri, nz, c):
            cau = ng["bridge_closed_max_mm"]  # mai lo kin: bac cau neo moi phia
        if (dien_tich >= ng["support_min_patch_mm2"] and min(dx, dy) > cau
                and float(zmax[c].max()) >= ng["min_patch_height_mm"] and rong_dai > ng["short_overhang_mm"]):
            cum.append({"mm2": round(dien_tich, 1), "rong_mm": round(min(dx, dy), 1), "dai_mm": round(rong_dai, 1),
                        "z_mm": round(float(zmin[c].min()), 1)})
            chon.append(c)
    return cum, (np.concatenate(chon) if chon else np.zeros(0, dtype=int)), nz


def kiem_lop(stl, lop_mm=0.2, vuon_mm=0.3, dien_tich_min_mm2=0.5):
    """Kiem THEO LOP nhu slicer (manifold3d cat lop): moi lop so voi lop duoi -> phan vuon ra > vuon_mm (cantilever)
    va cum ROI (floating). Tra danh sach {loai, z_mm, mm2, bao_xy}. Slicer chi bao "floating ..." khong chi cho - ham
    nay chi dung cho (da dung tim loi than xe cyberbrick-car 2026-10-23)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / ".pylib"))
    import manifold3d as m3
    tri = doc_stl(stl)
    tri = tri - np.array([0, 0, tri[:, :, 2].min()])
    v, idx = np.unique(np.round(tri.reshape(-1, 3), 5), axis=0, return_inverse=True)
    m = m3.Manifold(m3.Mesh(v.astype(np.float32), idx.reshape(-1, 3).astype(np.uint32)))
    if m.status() != m3.Error.NoError:
        return [{"loai": "luoi khong kin - khong kiem duoc theo lop"}]
    ra, truoc, z, h = [], None, lop_mm / 2, float(tri[:, :, 2].max())
    while z < h:
        cs = m.slice(z)
        if truoc is not None and cs.area() > 0:
            vr = cs - truoc.offset(vuon_mm, m3.JoinType.Round)
            if vr.area() > dien_tich_min_mm2:
                ra.append({"loai": "vuon ra", "z_mm": round(z, 2), "mm2": round(vr.area(), 1),
                           "bao_xy": [round(x, 1) for x in vr.bounds()]})
            for dao in cs.decompose():
                if (dao ^ truoc).area() < 1e-6 and dao.area() > 0.05:
                    ra.append({"loai": "roi (floating)", "z_mm": round(z, 2), "mm2": round(dao.area(), 2),
                               "bao_xy": [round(x, 1) for x in dao.bounds()]})
        truoc, z = cs, z + lop_mm
    return ra


def phan_tich(stl, nguong=None):
    ng = dict(MAC_DINH, **(nguong or {}))
    tri = doc_stl(stl)
    z0 = tri[:, :, 2].min()
    tri = tri - np.array([0, 0, z0])                       # day = ban in
    ok, nz, dt, zmin, zmax = _hinh(tri)
    tren_ban = zmax <= ng["bed_tol_mm"]
    cum, _, _ = vung_can_do(tri, ng)
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
