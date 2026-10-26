"""Kiem tra model FreeCAD truoc khi in 3D - gom checklist model-checks.md thanh 1 lenh.

Chay (tien trinh freecadcmd rieng, KHONG dung FreeCAD dang mo / cong MCP):
    "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" scripts/check.py --pass <file.FCStd|.step> [khoa=gia-tri ...]

Tuy chon (sau --pass, dang khoa=gia-tri vi freecadcmd tu doc moi tham so "--x"):
    out=<thu muc>              noi ghi bao cao (mac dinh: <thu muc file>/check/<ten file>/)
    components="SG90*,N20*"     nhan (Label, glob) la linh kien mua: chi kiem hinh hoc + va cham, khong kiem in
    ignore-pair="Horn|Servo*"    cap duoc phep cham/chong (vd. horn lap tren truc servo); lap lai duoc
    mesh-pair="Gear*|Pinion*"    cap an khop (banh rang) hoac dem/washer long: khe nho -> INFO (chong van FAIL)
    multi-solid="Spacer_D,..." object co y gom nhieu manh: khong bat loi "N solid"
    sweep=Khop:min:max[:buoc]  quet khop Assembly (Revolute/Cylindrical: do; Slider: mm); lap lai duoc
    export=3mf | export=step    xuat tung chi tiet in vao thu muc bao cao
    thresholds=<file.yaml>     mac dinh thresholds.yaml (thu muc robotics-cad)
    jobs=<N>                   so tien trinh freecadcmd chay song song (mac dinh nua so luong CPU, toi da 8);
                               jobs=1: chay 1 tien trinh. Them luong KHONG giup: OpenCASCADE giu GIL.
    rebuild=1                  bo cache, kiem lai tat ca
    mode=fast (mac dinh)      hinh hoc (khong BOP) + luoi + va cham: dung khi dang thiet ke, file LAP RAP
    mode=full                  them BOP + do day thanh + overhang + khoi luong + anh tung chi tiet
                               (do day/overhang theo huong TRONG FILE; kiem in that = slice.py, dung huong in)

Ra: report.json, overview.png (bang PASS/WARN/FAIL), anh tung chi tiet, collisions.png, sweep-<khop>.png.
Exit code 1 neu co FAIL.
Cache (<out>/.cache/): chi tiet / cap chi tiet khong doi hinh dang + vi tri + nguong thi khong kiem lai.

Muc (theo model-checks.md): 1 hinh hoc + BOP, 2 luoi, 3.2 va cham + quet khop, 5.2 do day thanh,
5.3 overhang, 6 khoi luong/trong tam. FEM (muc 4) KHONG nam trong script nay.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import FreeCAD as App
import Part
import MeshPart
import yaml

HERE = Path(__file__).resolve().parent
# Thu vien cong dong cai rieng cho du an (khong dong vao ban cai FreeCAD), xem docs/COMMUNITY.md:
#   "C:/Program Files/FreeCAD 1.1/bin/python.exe" -m pip install --no-deps --target ../.pylib manifold3d==3.5.4
sys.path.insert(0, str(HERE.parent / ".pylib"))
try:
    import manifold3d  # noqa: E402 - va cham tren luoi (giao khoi + khe ho), thay boolean B-rep cham
except ImportError:
    manifold3d = None
CONTAINERS = ("App::Part", "Assembly::AssemblyObject", "App::DocumentObjectGroup")
MAU = {"PASS": "#4caf50", "WARN": "#ff9800", "FAIL": "#e53935", "INFO": "#9e9e9e", "-": "#eeeeee"}
NANG = {"-": 0, "INFO": 0, "PASS": 1, "WARN": 2, "FAIL": 3}
TEN = {"hinh_hoc": "Hình học", "luoi": "Lưới", "do_day": "Độ dày thành", "overhang": "Overhang",
       "khoi_luong": "Khối lượng"}


def tham_so():
    # freecadcmd tu doc moi tham so "--x" (ke ca sau --pass) -> dung dang khoa=gia-tri, doi lai thanh --khoa gia-tri
    argv = []
    for t in (sys.argv[sys.argv.index("--pass") + 1:] if "--pass" in sys.argv else []):
        k, eq, v = t.partition("=")
        argv += [f"--{k}", v] if eq and not Path(t).exists() else [t]
    ap = argparse.ArgumentParser(prog="check.py")
    ap.add_argument("file")
    ap.add_argument("--out")
    ap.add_argument("--components", default="")
    ap.add_argument("--ignore-pair", action="append", default=[])
    ap.add_argument("--mesh-pair", action="append", default=[])
    ap.add_argument("--multi-solid", default="")
    ap.add_argument("--sweep", action="append", default=[])
    ap.add_argument("--export", choices=["3mf", "step"])
    ap.add_argument("--thresholds", default=str(HERE.parent / "thresholds.yaml"))
    ap.add_argument("--jobs", type=int, default=min(8, max(1, (os.cpu_count() or 2) // 2)))
    ap.add_argument("--rebuild", default="")
    ap.add_argument("--mode", choices=["fast", "full"], default="fast")
    ap.add_argument("--part", default="")  # noi bo: "k/N" = tien trinh con thu k
    ap.add_argument("--tmp", default="")   # noi bo: thu muc trao doi voi tien trinh cha
    return ap.parse_args(argv)


def kq(trang_thai, tom_tat, **chi_tiet):
    return {"trang_thai": trang_thai, "tom_tat": tom_tat, **chi_tiet}


# ---------- lay chi tiet ----------

def chi_tiet_la(doc):
    """Moi chi tiet co solid, trong toa do toan cuc (di xuyen App::Part / Assembly / Link)."""
    ra, da_thay = [], set()

    def di(goc, obj, duong):
        lo = obj.getLinkedObject(True)
        if lo.TypeId in CONTAINERS:
            for sub in obj.getSubObjects():
                con = obj.getSubObject(sub, retType=1)
                if con is not None:
                    di(goc, con, duong + sub)
            return
        if not lo.isDerivedFrom("Part::Feature") or not getattr(obj, "Visibility", True):
            return
        shp = Part.getShape(goc, duong) if duong else Part.getShape(goc)
        if not shp.Solids or (goc.Name, duong) in da_thay:
            return
        da_thay.add((goc.Name, duong))
        file_goc = getattr(lo.Document, "FileName", "") or ""
        ra.append({"nhan": obj.Label, "obj": obj, "shape": shp, "file_goc": file_goc})

    for goc in doc.RootObjects:
        di(goc, goc, "")
    return ra


def la_linh_kien(ct, mau):
    if "community" in Path(ct["file_goc"]).parts:
        return True
    return any(fnmatch.fnmatch(ct["nhan"], m.strip()) for m in mau if m.strip())


# ---------- 1. hinh hoc ----------

def kiem_hinh_hoc(s, linh_kien, nhieu_solid=False, bop_kiem=True):
    """nhieu_solid: object co y gom nhieu manh (vd. 2 mieng dem) -> khong bat buoc 1 solid.
    bop_kiem=False (che do nhanh): bo BOP check - chiem ~50% thoi gian, chu yeu can khi dung chi tiet lam dao cat."""
    so_solid = len(s.Solids)
    kin = all(sh.isClosed() for sh in s.Shells)
    hop_le = s.isValid()
    bop = "bo qua (che do nhanh)"
    if bop_kiem:
        try:
            s.check(True)
            bop = "OK"
        except Exception as e:  # check() nem loi kem danh sach loi
            bop = str(e).strip()[:200] or "loi BOP"
    loi = []
    if not hop_le:
        loi.append("isValid False")
    if so_solid != 1 and not (nhieu_solid and so_solid > 1):
        loi.append(f"{so_solid} solid")
    if not kin:
        loi.append("shell ho")
    if bop_kiem and bop != "OK":
        loi.append(f"BOP: {bop}")
    if not loi:
        tt = "PASS"
    elif linh_kien:
        tt = "WARN"  # linh kien mua: chi anh huong khi dung lam dao cat boolean (1.3)
    else:
        tt = "FAIL"
    return kq(tt, "; ".join(loi) or "hop le, 1 solid kin, BOP OK",
              is_valid=hop_le, so_solid=so_solid, shell_kin=kin, bop=bop)


# ---------- 2. luoi ----------

def tao_luoi(s, ng):
    return MeshPart.meshFromShape(Shape=s, LinearDeflection=ng["mesh"]["linear_mm"],
                                  AngularDeflection=ng["mesh"]["angular_rad"], Relative=False)


def kiem_luoi(m):
    r = {"isSolid": m.isSolid(), "nonManifold": m.hasNonManifolds(),
         "selfIntersect": m.hasSelfIntersections(), "flipped": m.countNonUniformOrientedFacets(),
         "components": m.countComponents(), "facet": m.CountFacets}
    loi = []
    if not r["isSolid"]:
        loi.append("luoi ho")
    if r["nonManifold"]:
        loi.append("non-manifold")
    if r["selfIntersect"]:
        loi.append("tu cat")
    if r["flipped"]:
        loi.append(f"{r['flipped']} facet nguoc")
    return kq("FAIL" if loi else "PASS", "; ".join(loi) or f"sach, {r['facet']} facet", **r)


# ---------- 5.2 do day thanh ----------

def do_day_luoi(m, gioi_han, n_tia):
    """Do day thanh tren LUOI (numpy + scipy, khong dung boolean B-rep - truoc day chiem 96% thoi gian).

    Tia tu tam facet di nguoc phap tuyen, lay giao gan nhat voi mat doi dien (Moller-Trumbore).
    Chi xet trong gioi_han mm (thanh day hon -> khong quan tam). Sai so ~ do lech luoi (0.05 mm).
    """
    import numpy as np
    from scipy.spatial import cKDTree

    P = np.array([(p.x, p.y, p.z) for p in m.Topology[0]], dtype=float)
    F = np.array(m.Topology[1], dtype=np.int64)
    A, B, C = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    E1, E2 = B - A, C - A
    N = np.cross(E1, E2)
    dt = np.linalg.norm(N, axis=1)
    ok = dt > 1e-12
    N[ok] /= dt[ok, None]
    G = (A + B + C) / 3
    R = np.sqrt(np.max([((X - G) ** 2).sum(1) for X in (A, B, C)], axis=0))  # ban kinh bao tam giac
    idx = np.nonzero(dt / 2 > 1e-3)[0]  # bo tam giac suy bien (dien tich ~0 -> phap tuyen sai, da gap: Jaw_1)
    dt_tong = float(dt[idx].sum() / 2)
    if len(idx) > n_tia:  # lay mau theo dien tich, co dinh seed de lan chay sau giong lan truoc
        idx = np.random.default_rng(0).choice(idx, n_tia, replace=False, p=dt[idx] / dt[idx].sum())
        dt_moi_tia = np.full(len(dt), dt_tong / n_tia)  # moi tia dai dien ~ dt_tong / n_tia mm2
    else:
        dt_moi_tia = dt / 2
    goc = G[idx] - N[idx] * 1e-4
    D = -N[idx]
    r95 = float(np.percentile(R, 95))
    dai = np.nonzero(R > r95)[0]  # tam giac dai (mat phang lon) -> luon xet
    lan_can = cKDTree(G).query_ball_point(goc, gioi_han + r95)
    res = []
    for k, i in enumerate(idx):
        c = np.union1d(np.asarray(lan_can[k], dtype=np.int64), dai)
        c = c[(c != i) & ((N[c] @ D[k]) > 0)]  # chi mat "di ra" theo huong tia
        if not len(c):
            continue
        e1, e2 = E1[c], E2[c]
        pv = np.cross(D[k], e2)
        det = (e1 * pv).sum(1)
        tot = np.abs(det) > 1e-12
        inv = np.divide(1.0, det, out=np.zeros_like(det), where=tot)
        tv = goc[k] - A[c]
        u = (tv * pv).sum(1) * inv
        qv = np.cross(tv, e1)
        v = (qv @ D[k]) * inv
        t = (qv * e2).sum(1) * inv
        cham = tot & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6) & (t < gioi_han)
        if cham.any():
            res.append((float(t[cham].min()) + 1e-4, int(i), tuple(G[i]), float(dt_moi_tia[i])))
    return sorted(res), len(idx)


def kiem_do_day(m, ng):
    """FAIL khi VUNG mong >= do_day_dien_tich_min_mm2; nho hon = mep sac (slicer tu bo) -> WARN."""
    nguong = ng.get("min_wall_mm")
    gh = max(ng.get("wall_limit_mm", 5.0), 2 * (nguong or 0))
    mau, so_tia = do_day_luoi(m, gh, ng.get("wall_rays", 6000))
    if not mau:
        return kq("PASS" if nguong is not None else "INFO", f"khong co thanh mong hon {gh} mm",
                  so_tia=so_tia, diem_mong=[])
    mn = mau[0][0]
    mong = [t for t in mau if nguong is not None and t[0] < nguong]
    diem = [{"mm": round(t[0], 3), "facet": t[1], "xyz": [round(x, 2) for x in t[2]]} for t in (mong or mau[:1])[:20]]
    if nguong is None:
        return kq("INFO", f"min {mn:.2f} mm (chua co nguong)", min_mm=mn, so_tia=so_tia, diem_mong=diem)
    if not mong:
        return kq("PASS", f"min {mn:.2f} mm >= {nguong} mm", min_mm=mn, so_tia=so_tia, diem_mong=diem)
    dt_mong = sum(t[3] for t in mong)
    dt_min = ng.get("thin_area_min_mm2", 1.0)
    if dt_mong >= dt_min:
        return kq("FAIL", f"thanh mong: {dt_mong:.1f} mm2 < {nguong} mm (min {mn:.2f} mm)",
                  min_mm=mn, dien_tich_mong_mm2=round(dt_mong, 2), so_tia=so_tia, diem_mong=diem)
    return kq("WARN", f"mep sac {dt_mong:.2f} mm2 (min {mn:.2f} mm), slicer thuong bo",
              min_mm=mn, dien_tich_mong_mm2=round(dt_mong, 3), so_tia=so_tia, diem_mong=diem)


# ---------- 5.3 overhang ----------

def kiem_overhang(s, m, ng):
    lim = ng.get("overhang_deg")
    if lim is None:
        return kq("INFO", "chua co nguong", facet=[])
    zmin = s.BoundBox.ZMin
    cz = -math.cos(math.radians(lim))
    fs = [ft for ft in m.Facets if ft.Normal.z < cz and sum(v[2] for v in ft.Points) / 3 > zmin + 0.01]
    dt = sum(ft.Area for ft in fs)
    tt = "WARN" if dt > 0.01 else "PASS"
    tom = f"{dt:.0f} mm2 doc hon {lim} do -> can support hoac xoay" if tt == "WARN" else f"khong co (nguong {lim} do)"
    return kq(tt, tom,
              dien_tich_mm2=round(dt, 1), huong="theo huong hien tai trong file", facet=[ft.Index for ft in fs])


# ---------- 6. khoi luong ----------

def kiem_khoi_luong(s, ng):
    vl = ng.get("material")
    rho = (ng.get("density_g_cm3") or {}).get(vl)
    V = sum(so.Volume for so in s.Solids)
    so = max(s.Solids, key=lambda x: x.Volume)  # Compound khong co CenterOfMass (6.3)
    com = so.CenterOfMass
    r = {"the_tich_mm3": round(V, 1), "trong_tam_mm": [round(com.x, 2), round(com.y, 2), round(com.z, 2)]}
    if rho is None:
        return kq("INFO", f"V = {V:.0f} mm3 (chua co khoi luong rieng cho {vl})", **r)
    g = V / 1000 * rho
    return kq("INFO", f"{g:.1f} g neu dac 100% {vl}", khoi_luong_dac_g=round(g, 2), vat_lieu=vl, **r)


# ---------- 3.2 va cham ----------

def bb_khoang(a, b):
    dx = max(0, max(a.XMin, b.XMin) - min(a.XMax, b.XMax))
    dy = max(0, max(a.YMin, b.YMin) - min(a.YMax, b.YMax))
    dz = max(0, max(a.ZMin, b.ZMin) - min(a.ZMax, b.ZMax))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def duoc_bo(a, b, bo_cap):
    for c in bo_cap:
        x, _, y = c.partition("|")
        if (fnmatch.fnmatch(a, x) and fnmatch.fnmatch(b, y)) or (fnmatch.fnmatch(a, y) and fnmatch.fnmatch(b, x)):
            return True
    return False


def tinh_cap(sa, sb, xa):
    """Chong (mm3) + khe ho nho nhat (mm) giua 2 shape; xa hon xa (theo hop bao) thi khong tinh."""
    if bb_khoang(sa.BoundBox, sb.BoundBox) > xa:
        return {"the_tich_mm3": 0.0, "khe_ho_mm": None, "giao": None}
    try:
        c = sa.common(sb)
        v = c.Volume
    except Exception:
        c, v = None, float("nan")
    d = sa.distToShape(sb)[0]
    return {"the_tich_mm3": v, "khe_ho_mm": d, "giao": c if v and v > 1e-3 else None}


_MF = {}  # manifold theo (nhan, vi tri) - quet khop: chi tiet dung yen khong chia luoi lai
_BAO_LOI = set()  # khoa cua cac manifold thay bang bao loi (linh kien STEP loi)


def mf_ct(ct, ng):
    """Manifold (manifold3d) tu luoi cua chi tiet; None neu khong co thu vien hoac luoi khong kin."""
    if "mf" in ct:
        return ct["mf"]
    s = ct["shape"]
    bb, v0 = s.BoundBox, (s.Vertexes[0].Point if s.Vertexes else App.Vector())
    khoa = (ct["nhan"], round(bb.XMin, 4), round(bb.YMin, 4), round(bb.ZMin, 4), round(bb.XMax, 4),
            round(bb.YMax, 4), round(bb.ZMax, 4), round(v0.x, 4), round(v0.y, 4), round(v0.z, 4))
    if khoa not in _MF:
        _MF[khoa] = None
        if manifold3d is not None:
            import numpy as np
            m = ct.get("luoi") or tao_luoi(s, ng)
            mm = manifold3d.Mesh(vert_properties=np.array([(p.x, p.y, p.z) for p in m.Topology[0]], dtype=np.float32),
                                 tri_verts=np.array(m.Topology[1], dtype=np.uint32))
            mm.merge()  # gop dinh trung o duong noi cac mat
            mf = manifold3d.Manifold(mm)
            if mf.status() == manifold3d.Error.NoError and not mf.is_empty():
                _MF[khoa] = mf
            elif ct.get("linh_kien"):
                # STEP linh kien loi -> chia luoi TUNG SOLID (solid kin dung dung hinh), chi solid ho moi bao loi
                # (fast_collide._manifold - dung chung voi quet khop). 2026-10-24: bao loi ca cum hop so 030 bao
                # chong gia 154 mm3. Chi tiet IN thi khong lam the (phai sua o CAD).
                import fast_collide
                ms = ng["mesh"]
                mf, hull = fast_collide._manifold(s, ms["linear_mm"], ms["angular_rad"])
                _MF[khoa] = mf
                if hull:
                    _BAO_LOI.add(khoa)
    ct["mf"] = _MF[khoa]
    ct["bao_loi"] = khoa in _BAO_LOI
    return ct["mf"]


def tinh_cap_ct(a, b, ng, xa):
    """Chon cach nhanh nhat: hop bao -> luoi (manifold3d) -> B-rep (chi khi luoi khong kin)."""
    if bb_khoang(a["shape"].BoundBox, b["shape"].BoundBox) > xa:
        return {"the_tich_mm3": 0.0, "khe_ho_mm": None, "giao": None, "cach": "hop-bao"}
    if mf_ct(a, ng) is not None and mf_ct(b, ng) is not None:
        return {**tinh_cap_luoi(a["mf"], b["mf"], xa),
                "cach": "luoi-bao-loi" if a.get("bao_loi") or b.get("bao_loi") else "luoi"}
    return {**tinh_cap(a["shape"], b["shape"], xa), "cach": "brep"}


def tinh_cap_luoi(ma, mb, xa):
    """Nhu tinh_cap nhung tren luoi: manifold3d (giao khoi + min_gap), nhanh hon B-rep hang tram lan."""
    import Mesh
    d = ma.min_gap(mb, xa)
    if d >= xa - 1e-9:
        return {"the_tich_mm3": 0.0, "khe_ho_mm": None, "giao": None}
    gm = ma ^ mb
    v = gm.volume()
    giao = None
    if v > 1e-3:
        r = gm.to_mesh()
        P, T = r.vert_properties[:, :3], r.tri_verts
        giao = Mesh.Mesh([[tuple(map(float, P[k])) for k in t] for t in T])
        d = 0.0
    return {"the_tich_mm3": v, "khe_ho_mm": d, "giao": giao}


def danh_sach_cap(cts, bo_cap):
    return [(i, j) for i in range(len(cts)) for j in range(i + 1, len(cts))
            if not duoc_bo(cts[i]["nhan"], cts[j]["nhan"], bo_cap)]


def va_cham_cap(cts, ng, bo_cap, cache=None):
    xa = ng.get("near_distance_mm", 5)
    ra = []
    for i, j in danh_sach_cap(cts, bo_cap):
        a, b = cts[i], cts[j]
        key = (i, j, str(a["shape"].Placement), str(b["shape"].Placement),
               a["shape"].BoundBox.Center.Length, b["shape"].BoundBox.Center.Length)
        if cache is not None and key in cache:
            r = cache[key]
        else:
            r = tinh_cap_ct(a, b, ng, xa)
            if cache is not None:
                cache[key] = r
        ra.append({"a": a["nhan"], "b": b["nhan"], **r})
    return ra


def khe_qua_nho(d, ng):
    """Khe < nguong, tru sai so luoi (da giac noi tiep lam lo nho di ~0.01 mm -> khe thiet ke 0.2 do ra 0.19)."""
    kh = ng.get("min_clearance_mm")
    return kh is not None and d < kh - ng.get("clearance_tolerance_mm", 0.0)


def danh_gia_cap(c, ng, an_khop=()):
    kh = ng.get("min_clearance_mm")
    v, d = c["the_tich_mm3"], c["khe_ho_mm"]
    if v != v:  # nan
        return "WARN", "common() loi (hinh hoc hong?)"
    if v > ng.get("min_overlap_mm3", 1e-3):
        if c.get("cach") == "luoi-bao-loi":  # linh kien STEP loi -> bao loi "beo" hon that
            return "WARN", f"chong {v:.2f} mm3 (xap xi bang bao loi linh kien, kiem bang mat)"
        return "FAIL", f"chong {v:.2f} mm3"
    if d is None:
        return "PASS", "xa"
    if duoc_bo(c["a"], c["b"], an_khop):  # banh rang an khop: khe nho la dung thiet ke
        return "INFO", f"an khop, khe {d:.2f} mm"
    if d < 1e-4 or v > 1e-3:
        # mat lap ghep tinh (tam ap dem, de ap chan) la dung thiet ke; chi tiet chuyen dong da co quet khop
        return "INFO", "cham nhau (khe 0 mm)"
    if khe_qua_nho(d, ng):
        return "FAIL", f"khe {d:.2f} mm < {kh} mm"
    return ("PASS" if kh is not None else "INFO"), f"khe {d:.2f} mm" + ("" if kh is not None else " (chua co nguong)")


def kiem_va_cham(cap, so_ct, ng, an_khop=()):
    """cap: danh sach {a, b, the_tich_mm3, khe_ho_mm, giao} da tinh (tu cache / tien trinh con)."""
    ds, nang = [], "PASS" if so_ct > 1 else "-"
    for c in cap:
        tt, tom = danh_gia_cap(c, ng, an_khop)
        if NANG[tt] > NANG[nang]:
            nang = tt
        if c["khe_ho_mm"] is not None:
            ds.append({"a": c["a"], "b": c["b"], "trang_thai": tt, "tom_tat": tom,
                       "the_tich_mm3": round(c["the_tich_mm3"], 3), "khe_ho_mm": round(c["khe_ho_mm"], 3)})
    if nang == "PASS" and any(x["trang_thai"] == "INFO" for x in ds):
        nang = "INFO"  # chua co nguong khe ho -> khong ket luan PASS
    xau = [x for x in ds if x["trang_thai"] in ("FAIL", "WARN")]
    tom = "; ".join(f"{x['a']}~{x['b']}: {x['tom_tat']}" for x in xau[:3]) or (
        f"{len(cap)} cap, khong chong" if cap else "1 chi tiet")
    return kq(nang, tom, cap=ds), [c["giao"] for c in cap if c["giao"] is not None]


# ---------- 3.2 quet khop ----------

def tim_khop(doc, nhan):
    ks = [o for o in doc.Objects if o.Label == nhan and hasattr(o, "JointType")]
    if not ks:
        raise SystemExit(f"Khong tim thay khop '{nhan}'. Khop co: "
                         + ", ".join(o.Label for o in doc.Objects if hasattr(o, "JointType")))
    j = ks[0]
    asm = j
    while asm is not None and asm.TypeId != "Assembly::AssemblyObject":
        asm = next((p for p in asm.InList), None)
    if asm is None:
        raise SystemExit(f"Khop '{nhan}' khong nam trong Assembly")
    return j, asm


def quet_khop(doc, spec, ng, bo_cap, linh_kien_mau):
    p = spec.split(":")
    nhan, lo, hi = p[0], float(p[1]), float(p[2])
    j, asm = tim_khop(doc, nhan)
    quay = j.JointType in ("Revolute", "Cylindrical")
    if not quay and j.JointType != "Slider":
        raise SystemExit(f"Khop '{nhan}' loai {j.JointType}: chi quet Revolute/Cylindrical/Slider")
    buoc = float(p[3]) if len(p) > 3 else ng["sweep_step_deg" if quay else "sweep_step_mm"]
    goc = App.Placement(j.Offset2)
    cache, moi_buoc = {}, []
    n = int(round((hi - lo) / buoc))
    try:
        for k in range(n + 1):
            x = lo + k * buoc
            if quay:
                j.Offset2 = goc * App.Placement(App.Vector(), App.Rotation(App.Vector(0, 0, 1), x))
            else:
                j.Offset2 = goc * App.Placement(App.Vector(0, 0, x), App.Rotation())
            asm.solve()
            moi_buoc.append((x, va_cham_cap(chi_tiet_la(doc), ng, bo_cap, cache)))
    finally:
        j.Offset2 = goc
        asm.solve()

    # cap cham nhau (khe 0, khong chong) o MOI buoc = mat lap co dinh (vd. tay dat tren de) -> khong tinh khe min
    def cham(c):
        return c["khe_ho_mm"] is not None and c["khe_ho_mm"] < 1e-4 and not c["the_tich_mm3"] > 1e-3
    luon_cham = set.intersection(*[{(c["a"], c["b"]) for c in cap if cham(c)} for _, cap in moi_buoc])
    buoc_ds = []
    for x, cap in moi_buoc:
        v = sum(c["the_tich_mm3"] for c in cap if c["the_tich_mm3"] == c["the_tich_mm3"])
        ds = [c["khe_ho_mm"] for c in cap if c["khe_ho_mm"] is not None and (c["a"], c["b"]) not in luon_cham]
        buoc_ds.append({"gia_tri": round(x, 3), "chong_mm3": round(v, 3),
                        "khe_min_mm": round(min(ds), 3) if ds else None,
                        "cap_chong": [f"{c['a']}~{c['b']}" for c in cap if c["the_tich_mm3"] > 1e-3]})
    don_vi = "do" if quay else "mm"
    xau = [b for b in buoc_ds if b["chong_mm3"] > 1e-3]
    if xau:
        tt, tom = "FAIL", f"chong o {xau[0]['gia_tri']}..{xau[-1]['gia_tri']} {don_vi} ({len(xau)}/{len(buoc_ds)} buoc)"
    else:
        km = [b["khe_min_mm"] for b in buoc_ds if b["khe_min_mm"] is not None]
        kh = ng.get("min_clearance_mm")
        mn = min(km) if km else None
        if mn is not None and mn < 1e-4:
            tt, tom = "WARN", f"cham (khe 0 mm) trong {lo}..{hi} {don_vi}"
        elif mn is not None and khe_qua_nho(mn, ng):
            tt, tom = "FAIL", f"khe min {mn:.2f} mm < {kh} mm"
        else:
            tt = "PASS" if kh is not None or mn is None else "INFO"
            tom = f"khong chong trong {lo}..{hi} {don_vi}, buoc {buoc}"
            if mn is not None:
                tom += f", khe min {mn:.2f} mm"
    if quay and buoc > 5:
        tom += f" (buoc {buoc} do co the bo sot chi tiet manh)"
    ghi_chu = "gia tri = goc Offset2 cua khop; Revolute: yaw thuc cua chi tiet = -gia tri (3.2)" if quay else \
        "gia tri = Offset2.z cua khop (mm)"
    return kq(tt, tom, khop=nhan, loai=j.JointType, don_vi=don_vi, ghi_chu=ghi_chu,
              cap_luon_cham=[f"{a}~{b}" for a, b in sorted(luon_cham)], buoc=buoc_ds)


# ---------- anh ----------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


VIEWS = [(0, 1, "Nhìn từ trên (X, Y)"), (0, 2, "Nhìn trước (X, Z)"), (1, 2, "Nhìn cạnh (Y, Z)")]
ANH_VA_CHAM_PHIEN_BAN = 2   # doi cach ve collisions.png -> tang so nay de ve lai (anh cu giu theo .collisions.sig)


def _ve_luoi(ax, verts, tris, i, j, mau, alpha):
    from matplotlib.collections import PolyCollection
    polys = [[(verts[k][i], verts[k][j]) for k in t] for t in tris]
    ax.add_collection(PolyCollection(polys, facecolor=mau, edgecolor="none", alpha=alpha))


def _khung(ax, bb, i, j, lab):
    lo, hi = (bb.XMin, bb.YMin, bb.ZMin), (bb.XMax, bb.YMax, bb.ZMax)
    pad = max(2.0, 0.05 * bb.DiagonalLength)
    ax.set_xlim(lo[i] - pad, hi[i] + pad)
    ax.set_ylim(lo[j] - pad, hi[j] + pad)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.set_title(lab, fontsize=9)
    ax.set_xlabel("mm", fontsize=8)


def anh_chi_tiet(ct, png, ng):
    plt = _plt()
    s, m, r = ct["shape"], ct.get("luoi"), ct["ket_qua"]
    verts, tris = s.tessellate(0.2)
    oh = set(r.get("overhang", {}).get("facet", []))
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (i, j, lab) in zip(axs, VIEWS):
        _ve_luoi(ax, verts, tris, i, j, "#9ab", 0.35)
        if m is not None and oh:
            pts = m.Topology[0]
            ftris = [t for k, t in enumerate(m.Topology[1]) if k in oh]
            _ve_luoi(ax, [(p.x, p.y, p.z) for p in pts], ftris, i, j, "#e53935", 0.6)
        for d in r.get("do_day", {}).get("diem_mong", []):
            if r["do_day"]["trang_thai"] == "FAIL":
                ax.plot(d["xyz"][i], d["xyz"][j], "x", color="#b71c1c", ms=8, mew=2)
        _khung(ax, s.BoundBox, i, j, lab)
    b = s.BoundBox
    fig.suptitle(f"{ct['nhan']}   hộp bao {b.XLength:.1f} × {b.YLength:.1f} × {b.ZLength:.1f} mm", fontsize=11)
    for k, (ten, v) in enumerate(r.items()):
        fig.text(0.01 + 0.2 * k, 0.88, f"{TEN.get(ten, ten)}: {v['trang_thai']}\n{textwrap.fill(v['tom_tat'], 34)}",
                 fontsize=8, va="top", bbox={"facecolor": MAU[v["trang_thai"]], "alpha": 0.35, "edgecolor": "none"})
    fig.text(0.01, 0.01, "Đỏ: mặt overhang (theo hướng trong file)   ×: điểm thành mỏng", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.74))
    fig.savefig(png, dpi=100)
    plt.close(fig)


def anh_va_cham(cts, giao, png):
    plt = _plt()
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    bb = App.BoundBox()
    for ct in cts:
        bb.add(ct["shape"].BoundBox)
    # tessellate 1 lan / chi tiet cho ca 3 huong (truoc: trong vong lap huong = 3 lan); luoi 1,0 mm du de xem tong the
    # (profile 2026-10-26: anh nay 69/78 s cua lan kiem pushrod-arm du cache 100 %)
    nen = [ct["shape"].tessellate(1.0) for ct in cts]
    do = [([(p.x, p.y, p.z) for p in g.Topology[0]], g.Topology[1]) if hasattr(g, "Topology")  # Mesh (manifold3d)
          else g.tessellate(0.1) for g in giao]
    for ax, (i, j, lab) in zip(axs, VIEWS):
        for v, t in nen:
            _ve_luoi(ax, v, t, i, j, "#9ab", 0.25)
        for v, t in do:
            _ve_luoi(ax, v, t, i, j, "#e53935", 0.9)
        _khung(ax, bb, i, j, lab)
    fig.suptitle("Va chạm: vùng đỏ là phần thể tích chồng nhau", fontsize=10)
    fig.tight_layout()
    fig.savefig(png, dpi=100)
    plt.close(fig)


def anh_quet(q, png):
    plt = _plt()
    xs = [b["gia_tri"] for b in q["buoc"]]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(xs, [b["chong_mm3"] for b in q["buoc"]], width=(xs[1] - xs[0]) * 0.8 if len(xs) > 1 else 1,
           color="#e53935", label="thể tích chồng (mm³)")
    ax.set_xlabel(f"{q['khop']} ({q['don_vi']})")
    ax.set_ylabel("mm³")
    ax2 = ax.twinx()
    ax2.plot(xs, [b["khe_min_mm"] if b["khe_min_mm"] is not None else float("nan") for b in q["buoc"]],
             "o-", color="#1e88e5", ms=3, label="khe hở nhỏ nhất (mm)")
    ax2.set_ylabel("mm")
    fig.legend(loc="upper right", fontsize=8)
    ax.set_title(f"Quét khớp {q['khop']} – {q['trang_thai']}: {q['tom_tat']}", fontsize=9)
    fig.tight_layout()
    fig.savefig(png, dpi=100)
    plt.close(fig)


def anh_tong_quan(bc, png):
    plt = _plt()
    cot = ["hinh_hoc", "luoi", "do_day", "overhang", "khoi_luong"]
    hang = [(ct["nhan"] + ("\n(linh kiện)" if ct["linh_kien"] else ""), [ct["ket_qua"].get(c) for c in cot])
            for ct in bc["chi_tiet"]]
    tong = [("Va chạm", bc["va_cham"])] + [(f"Quét khớp {q['khop']}", q) for q in bc["quet_khop"]]
    cao = 0.62 * (len(hang) + 1) + 0.45 * len(tong) + 1.0
    fig = plt.figure(figsize=(18, cao))
    ax = fig.add_axes((0.01, 0.45 * len(tong) / cao + 0.02, 0.98, 1 - (0.45 * len(tong) + 0.6) / cao))
    ax.axis("off")
    cell, mau = [], []
    for ten, rs in hang:
        cell.append([ten] + [(f"{r['trang_thai']}: " + textwrap.shorten(r["tom_tat"], 60) if r else "–") for r in rs])
        mau.append(["#ffffff"] + [MAU[r["trang_thai"]] if r else MAU["-"] for r in rs])
    cell = [[textwrap.fill(x, 32) for x in row] for row in cell]
    t = ax.table(cellText=cell, cellColours=mau, colLabels=["Chi tiết"] + [TEN[c] for c in cot],
                 loc="upper left", cellLoc="left", colWidths=[0.15] + [0.17] * 5)
    t.auto_set_font_size(False)
    t.set_fontsize(8)
    for (r_, _), c in t.get_celld().items():
        c.set_height(0.9 / (len(hang) + 1))
    for k, (ten, r) in enumerate(tong):
        fig.text(0.015, (0.45 * (len(tong) - k) - 0.1) / cao, f" {r['trang_thai']} ", fontsize=10, weight="bold",
                 color="white", bbox={"facecolor": MAU[r["trang_thai"]], "edgecolor": "none"})
        fig.text(0.07, (0.45 * (len(tong) - k) - 0.1) / cao, f"{ten}: {textwrap.shorten(r['tom_tat'], 190)}",
                 fontsize=9)
    fig.suptitle(f"{bc['file']}  –  KẾT QUẢ: {bc['ket_luan']}   ({bc['thoi_gian']}, {bc['thoi_gian_chay_s']} s)",
                 fontsize=12, x=0.01, ha="left")
    fig.savefig(png, dpi=100)
    plt.close(fig)


# ---------- chinh ----------

def ten_file(s):
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in s)[:60]


# ---------- dieu phoi: cache + chay song song ----------

def khoa_ct(ct):
    """Dau van tay chi tiet: doi hinh dang / vi tri / loai thi doi khoa."""
    s = ct["shape"]
    bb = s.BoundBox
    v0 = s.Vertexes[0].Point if s.Vertexes else App.Vector()
    txt = (f"{ct['nhan']}|{ct['linh_kien']}|{s.Volume:.4f}|{s.Area:.4f}|{len(s.Faces)}|"
           f"{bb.XMin:.4f},{bb.YMin:.4f},{bb.ZMin:.4f},{bb.XMax:.4f},{bb.YMax:.4f},{bb.ZMax:.4f}|"
           f"{v0.x:.4f},{v0.y:.4f},{v0.z:.4f}")
    return hashlib.sha1(txt.encode("utf-8")).hexdigest()[:16]


def khoa_cap(ka, kb):
    return hashlib.sha1(f"{ka}|{kb}".encode()).hexdigest()[:16]


def doc_cache(cdir, ng, lam_lai, che_do):
    """Cache rieng tung che do; mat hieu luc khi doi script hoac nguong."""
    dau = hashlib.sha1(Path(__file__).read_bytes() + json.dumps(ng, sort_keys=True).encode()).hexdigest()[:16]
    f = cdir / f"cache-{che_do}.json"
    if not lam_lai and f.exists():
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
            if c.get("dau") == dau:
                return c
        except ValueError:
            pass
    for g in (*cdir.glob("*.brep"), *cdir.glob("*.stl")):
        g.unlink()
    return {"dau": dau, "p": {}, "c": {}}


def lam_viec(cts, ng, a, out, cdir, ds_ct, ds_cap, ten=""):
    """Kiem cac chi tiet ds_ct (chi so) + cac cap ds_cap; ve anh chi tiet; tra ket qua theo khoa."""
    kq_p, kq_c = {}, {}
    for n, i in enumerate(ds_ct, 1):
        ct, t0 = cts[i], time.time()
        s, r = ct["shape"], {}

        def do(muc, f):
            t1 = time.time()
            r[muc] = f()
            r[muc]["s"] = round(time.time() - t1, 2)

        nhieu = any(fnmatch.fnmatch(ct["nhan"], x.strip()) for x in a.multi_solid.split(",") if x.strip())
        day_du = a.mode == "full"
        do("hinh_hoc", lambda: kiem_hinh_hoc(s, ct["linh_kien"], nhieu, bop_kiem=day_du))
        if not ct["linh_kien"]:
            t1 = time.time()
            m = ct["luoi"] = tao_luoi(s, ng)
            t_luoi = time.time() - t1
            do("luoi", lambda: kiem_luoi(m))
            r["luoi"]["s"] = round(r["luoi"]["s"] + t_luoi, 2)
            rl = r["luoi"]
            if rl["trang_thai"] == "FAIL" and rl["tom_tat"] == "tu cat" and s.isValid():
                # chi "tu cat": thuong do chia luoi o mat gan tiep tuyen (da gap: Jaw_1, 3 cap tam giac) -> hoi B-rep
                try:
                    s.check(True)
                    rl["trang_thai"], rl["tom_tat"] = "WARN", "tu cat do chia luoi; B-rep hop le, BOP OK"
                except Exception:
                    pass
            if day_du:  # che do nhanh: do day / overhang / khoi luong de slicer xet (slice.py, dung huong in)
                do("do_day", lambda: kiem_do_day(m, ng))
                do("overhang", lambda: kiem_overhang(s, m, ng))
                do("khoi_luong", lambda: kiem_khoi_luong(s, ng))
            if a.export == "3mf":
                m.write(str(out / f"{ten_file(ct['nhan'])}.3mf"))
            elif a.export == "step":
                s.exportStep(str(out / f"{ten_file(ct['nhan'])}.step"))
            ct["ket_qua"] = r
            if day_du:
                anh_chi_tiet(ct, out / f"{ten_file(ct['nhan'])}.png", ng)
        kq_p[ct["khoa"]] = {k: {kk: vv for kk, vv in v.items() if kk != "facet"} for k, v in r.items()}
        print(f"{ten}[{n}/{len(ds_ct)}] {ct['nhan']} {time.time() - t0:.1f} s: "
              + ", ".join(f"{k}={v['trang_thai']}" for k, v in r.items()), flush=True)
    xa = ng.get("near_distance_mm", 5)
    t0 = time.time()
    for n, (i, j) in enumerate(ds_cap, 1):
        a, b, t1 = cts[i], cts[j], time.time()
        r = tinh_cap_ct(a, b, ng, xa)
        k = khoa_cap(a["khoa"], b["khoa"])
        g = r.pop("giao")
        r["giao"] = None
        if g is not None:
            r["giao"] = f"{k}.stl" if hasattr(g, "Topology") else f"{k}.brep"
            g.write(str(cdir / r["giao"])) if hasattr(g, "Topology") else g.exportBrep(str(cdir / r["giao"]))
        r["s"] = round(time.time() - t1, 2)
        kq_c[k] = r
        if n % 100 == 0 or n == len(ds_cap):
            print(f"{ten}cap {n}/{len(ds_cap)} ({time.time() - t0:.0f} s)", flush=True)
    return {"p": kq_p, "c": kq_c}


def chay_song_song(a, src, out, cdir, ds_ct, ds_cap, so_ct, n):
    """n tien trinh freecadcmd con, moi tien trinh lam ds[k::n]; doi xong roi gop."""
    tam = cdir / "tmp"
    tam.mkdir(exist_ok=True)
    for f in tam.glob("*"):
        f.unlink()
    (tam / "viec.json").write_text(json.dumps({"so_ct": so_ct, "ct": ds_ct, "cap": ds_cap}), encoding="utf-8")
    exe = Path(App.getHomePath()) / "bin" / "freecadcmd.exe"
    ps = []
    for k in range(n):
        cmd = [str(exe), str(Path(__file__).resolve()), "--pass", str(src), f"part={k}/{n}", f"tmp={tam}",
               f"out={out}", f"thresholds={a.thresholds}", f"components={a.components}", f"multi-solid={a.multi_solid}",
               f"mode={a.mode}"]
        cmd += [f"export={a.export}"] if a.export else []
        log = open(tam / f"log-{k}.txt", "w", encoding="utf-8")
        p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             creationflags=0x08000000 if os.name == "nt" else 0)  # CREATE_NO_WINDOW
        ps.append((p, log))
    t0, bao = time.time(), 0
    while any(p.poll() is None for p, _ in ps):
        time.sleep(2)
        if time.time() - t0 > bao + 30:
            bao = time.time() - t0
            xong = sum(1 for p, _ in ps if p.poll() is not None)
            print(f"  ... {bao:.0f} s, {xong}/{n} tien trinh xong", flush=True)
    gop = {"p": {}, "c": {}}
    for k, (p, log) in enumerate(ps):
        log.close()
        f = tam / f"phan-{k}.json"
        if p.returncode != 0 or not f.exists():
            raise SystemExit(f"Tien trinh con {k} loi (exit {p.returncode}), xem {tam / f'log-{k}.txt'}")
        r = json.loads(f.read_text(encoding="utf-8"))
        gop["p"].update(r["p"])
        gop["c"].update(r["c"])
    return gop


def mo_file(src):
    if src.suffix.lower() == ".fcstd":
        return App.openDocument(str(src))
    doc = App.newDocument("kiem_tra")
    s = Part.Shape()
    s.read(str(src))
    doc.addObject("Part::Feature", src.stem).Shape = s
    doc.recompute()
    return doc


def main():
    a = tham_so()
    t0 = time.time()
    src = Path(a.file).resolve()
    ng = yaml.safe_load(Path(a.thresholds).read_text(encoding="utf-8"))
    out = Path(a.out) if a.out else src.parent / "check" / src.stem
    cdir = out / ".cache"
    cdir.mkdir(parents=True, exist_ok=True)

    doc = mo_file(src)
    lk_mau = a.components.split(",")
    cts = chi_tiet_la(doc)
    if not cts:
        raise SystemExit("Khong tim thay chi tiet nao co solid")
    for ct in cts:
        ct["linh_kien"] = la_linh_kien(ct, lk_mau)
        ct["khoa"] = khoa_ct(ct)

    if a.part:  # tien trinh con
        k, n = (int(x) for x in a.part.split("/"))
        viec = json.loads((Path(a.tmp) / "viec.json").read_text(encoding="utf-8"))
        if viec["so_ct"] != len(cts):
            raise SystemExit(f"So chi tiet lech: cha {viec['so_ct']}, con {len(cts)}")
        r = lam_viec(cts, ng, a, out, cdir, viec["ct"][k::n], [tuple(x) for x in viec["cap"][k::n]], f"<{k}> ")
        (Path(a.tmp) / f"phan-{k}.json").write_text(json.dumps(r), encoding="utf-8")
        return 0

    cache = doc_cache(cdir, ng, a.rebuild, a.mode)
    tat_ca_cap = danh_sach_cap(cts, a.ignore_pair)
    ds_ct = [i for i, ct in enumerate(cts) if a.export or ct["khoa"] not in cache["p"]
             or (a.mode == "full" and not ct["linh_kien"]
                 and not (out / f"{ten_file(ct['nhan'])}.png").exists())]
    ds_cap = [(i, j) for i, j in tat_ca_cap if khoa_cap(cts[i]["khoa"], cts[j]["khoa"]) not in cache["c"]]
    n = min(a.jobs, max(1, len(ds_ct) + len(ds_cap) // 300))
    print(f"{len(cts)} chi tiet, {len(tat_ca_cap)} cap. Can kiem: {len(ds_ct)} chi tiet, {len(ds_cap)} cap "
          f"(con lai lay tu cache). Chay {n} tien trinh.", flush=True)
    if n > 1:
        moi = chay_song_song(a, src, out, cdir, ds_ct, ds_cap, len(cts), n)
    else:
        moi = lam_viec(cts, ng, a, out, cdir, ds_ct, ds_cap)
    cache["p"].update(moi["p"])
    cache["c"].update(moi["c"])

    # gop ket qua; bo muc cache khong con dung (chi tiet da sua / da xoa)
    dung_p = {ct["khoa"] for ct in cts}
    dung_c = {khoa_cap(cts[i]["khoa"], cts[j]["khoa"]) for i, j in tat_ca_cap}
    cache["p"] = {k: v for k, v in cache["p"].items() if k in dung_p}
    cache["c"] = {k: v for k, v in cache["c"].items() if k in dung_c}
    for g in (*cdir.glob("*.brep"), *cdir.glob("*.stl")):
        if g.stem not in dung_c:
            g.unlink()
    (cdir / f"cache-{a.mode}.json").write_text(json.dumps(cache), encoding="utf-8")
    for ct in cts:
        ct["ket_qua"] = cache["p"][ct["khoa"]]
    cap = []
    for i, j in tat_ca_cap:
        r = dict(cache["c"][khoa_cap(cts[i]["khoa"], cts[j]["khoa"])])
        if r["giao"]:
            f = str(cdir / r["giao"])
            if not Path(f).exists():  # file giao bi che do kia don mat -> chi thieu anh, so lieu van dung
                r["giao"] = None
            else:
                r["giao"] = __import__("Mesh").Mesh(f) if f.endswith(".stl") else Part.read(f)
        cap.append({"a": cts[i]["nhan"], "b": cts[j]["nhan"], **r})
    vc, giao = kiem_va_cham(cap, len(cts), ng, a.mesh_pair)
    qk = [quet_khop(doc, spec, ng, a.ignore_pair, lk_mau) for spec in a.sweep]

    tat_ca = [v["trang_thai"] for ct in cts for v in ct["ket_qua"].values()]
    tat_ca += [vc["trang_thai"]] + [q["trang_thai"] for q in qk]
    ket_luan = "FAIL" if "FAIL" in tat_ca else ("WARN" if "WARN" in tat_ca else "PASS")
    bc = {
        "file": src.name, "duong_dan": str(src), "thoi_gian": time.strftime("%Y-%m-%d %H:%M"),
        "freecad": ".".join(App.Version()[:3]), "nguong": ng, "ket_luan": ket_luan,
        "chi_tiet": [{"nhan": ct["nhan"], "linh_kien": ct["linh_kien"],
                      "hop_bao_mm": [round(ct["shape"].BoundBox.XLength, 2), round(ct["shape"].BoundBox.YLength, 2),
                                     round(ct["shape"].BoundBox.ZLength, 2)],
                      "ket_qua": {k: {kk: vv for kk, vv in v.items() if kk != "facet"}
                                  for k, v in ct["ket_qua"].items()}}
                     for ct in cts],
        "va_cham": vc, "quet_khop": qk,
        "chay": {"tien_trinh": n, "chi_tiet_kiem_moi": len(ds_ct), "cap_kiem_moi": len(ds_cap)},
    }

    # anh chi tiet da ve trong lam_viec (hoac con tu lan truoc neu lay tu cache); xoa anh khong con dung
    giu = {"overview.png"} | ({f"{ten_file(ct['nhan'])}.png" for ct in cts if not ct["linh_kien"]}
                              if a.mode == "full" else set())
    giu |= {f"sweep-{ten_file(q['khop'])}.png" for q in qk} | ({"collisions.png"} if giao else set())
    for f in out.glob("*.png"):
        if f.name not in giu:
            f.unlink()
    if giao:
        # chi ve lai khi chi tiet (khoa = hinh + vi tri) hoac cap chong nhau doi; khong doi -> giu anh cu
        ky = hashlib.sha1(json.dumps([sorted(ct["khoa"] for ct in cts),
                                      sorted((c["a"], c["b"], c.get("the_tich_mm3")) for c in cap if c["giao"]),
                                      ANH_VA_CHAM_PHIEN_BAN], default=str).encode()).hexdigest()
        png, f_ky = out / "collisions.png", out / ".collisions.sig"
        if not (png.exists() and f_ky.exists() and f_ky.read_text() == ky):
            anh_va_cham(cts, giao, png)
            f_ky.write_text(ky)
    for q in qk:
        anh_quet(q, out / f"sweep-{ten_file(q['khop'])}.png")
    bc["thoi_gian_chay_s"] = round(time.time() - t0, 1)
    anh_tong_quan(bc, out / "overview.png")
    (out / "report.json").write_text(json.dumps(bc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"KET LUAN: {ket_luan}  ({bc['thoi_gian_chay_s']} s)  -> {out}")
    App.closeDocument(doc.Name)
    return 1 if ket_luan == "FAIL" else 0


code = main()
if code:
    sys.exit(code)
