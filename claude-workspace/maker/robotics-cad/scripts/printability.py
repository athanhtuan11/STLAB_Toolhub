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
            "brim_contact_max_mm2": 120.0, "brim_aspect_min": 2.5,
            "support_gap_max_mm": 0.6, "support_gap_mm": 0.2,
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
    """Cac cum mat nho ra CAN DO (chung cho phan_tich va tao_support) -> (thong tin cum, chi so tam giac)."""
    ok, nz, dt, zmin, zmax = _hinh(tri)
    # mat up xuong, nghieng it hon (overhang_deg - tol) so voi phuong ngang; tol: vat dung 45 do van in duoc.
    # mat sat ban (zmax <= bed_near_mm): lop dau ep xuong ban in duoc
    goc = ng["overhang_deg"] - ng["overhang_tol_deg"]
    nho = ok & (zmax > ng["bed_near_mm"]) & (-nz > np.cos(np.radians(goc)))
    # da co do ngay ben duoi (support tu ve Support_* / support sinh boi tao_support, khe <= support_gap_max_mm)
    nho[_co_do_duoi(tri, nz, np.nonzero(nho)[0], ng["support_gap_max_mm"])] = False
    cum, chon = [], []
    for c in _cum(tri, nho):
        pts = tri[c].reshape(-1, 3)
        dx, dy = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
        dien_tich = float(dt[c].sum())
        rong_dai = _rong_dai(tri[c])
        # bo qua: nho / hep (bac cau duoc: noc lo ngang) / sat ban / dai hep (ren, vat nho - moi lop nho < 1 vet)
        if (dien_tich >= ng["support_min_patch_mm2"] and min(dx, dy) > ng["bridge_max_mm"]
                and float(zmax[c].max()) >= ng["min_patch_height_mm"] and rong_dai > ng["short_overhang_mm"]):
            cum.append({"mm2": round(dien_tich, 1), "rong_mm": round(min(dx, dy), 1), "dai_mm": round(rong_dai, 1),
                        "z_mm": round(float(zmin[c].min()), 1)})
            chon.append(c)
    return cum, (np.concatenate(chon) if chon else np.zeros(0, dtype=int)), nz


def tao_support(tri, nguong=None):
    """Support TU VE (khong de slicer sinh): duoi moi tam giac nho ra chua duoc do -> lang tru dung tu ban (hoac tu mat
    chi tiet ngay ben duoi) len toi mat nho ra, chua khe Z `support_gap_mm` de be. tri: (n,3,3) theo HUONG IN, day z=0.
    Tra (m,3,3) tam giac cac lang tru (moi lang tru 1 vo kin; slicer gop cac vo chong nhau)."""
    ng = dict(MAC_DINH, **(nguong or {}))
    tri = np.asarray(tri, dtype=np.float64)
    _, idx, nz = vung_can_do(tri, ng)
    if len(idx) == 0:
        return np.zeros((0, 3, 3))
    gap = ng["support_gap_mm"]
    # day lang tru: mat NGUA cao nhat ben duoi tam tam giac (neu co) + gap, khong thi ban (z 0)
    up = tri[nz > 0.3]
    cen = tri[idx].mean(axis=1)
    day = np.zeros(len(idx))
    if len(up):
        a = up[:, 0]
        v0, v1 = (up[:, 1] - a)[:, :2], (up[:, 2] - a)[:, :2]
        d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
        den = np.where(np.abs(d00 * d11 - d01 * d01) > 1e-12, d00 * d11 - d01 * d01, np.nan)
        for s in range(0, len(idx), 2000):
            c = cen[s:s + 2000]
            v2 = c[:, None, :2] - a[None, :, :2]
            d20, d21 = (v2 * v0[None]).sum(2), (v2 * v1[None]).sum(2)
            v = (d11[None] * d20 - d01[None] * d21) / den[None]
            w = (d00[None] * d21 - d01[None] * d20) / den[None]
            u = 1 - v - w
            z = u * up[None, :, 0, 2] + v * up[None, :, 1, 2] + w * up[None, :, 2, 2]
            duoi = (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6) & (z < c[:, None, 2] - 1e-3)
            zz = np.where(duoi, z, -np.inf).max(axis=1)
            day[s:s + 2000] = np.where(np.isfinite(zz), zz + gap, 0.0)
    out = []
    for k, i in enumerate(idx):
        t = tri[i].copy()
        t[:, 2] -= gap
        if t[:, 2].max() - day[k] < 0.05:  # khong con cho (mat ngay tren mat duoi) -> bo
            continue
        b = t.copy()
        b[:, 2] = day[k]
        # dinh: t (huong len = nguoc tam giac nho ra), day: b (huong xuong), 3 mat ben
        pr = [[t[0], t[2], t[1]], [b[0], b[1], b[2]]]
        for j in range(3):
            p, q = j, (j + 1) % 3
            pr += [[b[q], b[p], t[p]], [b[q], t[p], t[q]]]  # canh chung di nguoc chieu mat day/dinh
        pr = np.array(pr)
        if np.einsum("ij,ij->i", pr[:, 0], np.cross(pr[:, 1], pr[:, 2])).sum() < 0:  # vo kin, phap tuyen ra ngoai
            pr = pr[:, ::-1]
        out.append(pr)
    return np.concatenate(out).astype(np.float64) if out else np.zeros((0, 3, 3))


def ghi_stl(p, tri):
    tri = np.asarray(tri, dtype=np.float32)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(tri), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = n, tri
    with open(p, "wb") as f:
        f.write(b"STLab printability support".ljust(80, b" "))
        f.write(np.uint32(len(tri)).tobytes())
        f.write(rec.tobytes())


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
