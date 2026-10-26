# Kiem LAP DUOC (Tuan 2026-10-26: pushrod-arm Housing_Elbow + Piston_rod_Elbow in rieng KHONG lap vao nhau duoc,
# trong khi mo phong + test va cham deu PASS - mo phong chi DAT san chi tiet vao cho, khong hoi "dua vao duong nao").
#
# Moi cap chi tiet dang cham nhau (khe < --near mm) o tu the goc: thu TINH TIEN chi tiet A theo 6 huong truc (he toa do
# rieng cua A + he chung) tu vi tri lap ra xa, buoc --step mm. Huong nao di het ma khong giao B (> --min mm3) = duong
# thao/lap. Khong huong nao -> cap BI KET: hai khoi cung, in rieng thi khong lap duoc (thuyen trong chai).
# Dieu kien CAN, chua phai du: chua xet thu tu lap nhieu chi tiet, xoay, uon (snap-fit), ren. Chi tiet in-tai-cho/
# tha dai oc giua luc in/dan thi khai trong --allow (kem ly do trong print.yaml hoac test).
#
#   "C:/Program Files/FreeCAD 1.1/bin/FreeCADCmd.exe" --safe-mode fc_cli.py --pass assembly_paths.py <file.FCStd>
#       [only=Housing_Elbow,Piston_rod_Elbow] [near=0.5] [step=0.2] [allow="A|B,C|D"] [json=out.json]
#   hoac import: assembly_paths.trapped(doc_objs, pairs=None, ...) -> list
import json
import sys
from fnmatch import fnmatch
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fast_collide  # noqa: E402

AXES = [np.array(v, dtype=float) for v in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]


def _bb(m):
    lo, hi = np.split(np.array(m.bounding_box()), 2)
    return lo, hi


def _dirs(obj):
    """6 huong truc cua he chung + 6 huong truc rieng cua chi tiet (bo trung)."""
    out = list(AXES)
    r = obj.Placement.Rotation
    for v in AXES:
        w = r.multVec(type(obj.Placement.Base)(*v))
        w = np.array([w.x, w.y, w.z])
        if all(np.linalg.norm(w - u) > 1e-6 for u in out):
            out.append(w)
    return out


def free_direction(col, a, b, obj_a, step=0.2, min_mm3=0.5):
    """Huong (np.array) dua a ra khoi b khong va cham, hoac None. col: fast_collide.Collider o tu the hien tai."""
    ma, mb = col._now(a), col._now(b)
    lo_b, hi_b = _bb(mb)
    for d in _dirs(obj_a):
        lo_a, hi_a = _bb(ma)
        # quang duong toi khi hop bao cua a roi han hop bao cua b theo huong d
        span = float(np.dot(np.abs(d), (hi_a - lo_a) + (hi_b - lo_b))) + 1.0
        n = int(span / step) + 1
        ok = True
        for k in range(1, n + 1):
            t = d * (k * step)
            mt = ma.translate(tuple(t))
            lo, hi = lo_a + t, hi_a + t
            if np.any(hi < lo_b) or np.any(hi_b < lo):
                break                                     # da roi hop bao -> thoat
            if (mt ^ mb).volume() > min_mm3:
                ok = False
                break
        if ok:
            return d
    return None


def neighbor_pairs(col, labels, near=0.5):
    out = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            if a not in col.base or b not in col.base:
                continue
            lo_a, hi_a = _bb(col._now(a))
            lo_b, hi_b = _bb(col._now(b))
            if np.any(hi_a + near < lo_b) or np.any(hi_b + near < lo_a):
                continue
            g = col._now(a).min_gap(col._now(b), near + 0.01)
            if g <= near:
                out.append((a, b))
    return out


def allowed(a, b, allow):
    """allow: [(mau_a, mau_b)] kieu fnmatch ("M2_5x*", "*"), khop ca 2 chieu."""
    return any((fnmatch(a, pa) and fnmatch(b, pb)) or (fnmatch(b, pa) and fnmatch(a, pb)) for pa, pb in allow)


def trapped(objs, pairs=None, near=0.5, step=0.2, min_mm3=0.5, allow=(), log=None):
    """objs: {label: obj}. Tra ([(a, b, ghi_chu)] cap bi ket/chong san, cac cap da xet) - thu a ra khoi b lan nguoc lai."""
    col = fast_collide.Collider(objs, min_mm3=min_mm3)
    labels = sorted(col.base)
    pairs = pairs or neighbor_pairs(col, labels, near)
    res = []
    for a, b in pairs:
        if allowed(a, b, allow):
            continue
        note = " (bao loi - co the bao gia)" if a in col.hull or b in col.hull else ""
        v0 = col.volume(a, b)
        if v0 > min_mm3:   # chong san o tu the goc: moi huong deu "va" ngay -> bao rieng, khong goi la ket
            if log:
                print("%-40s %-40s CHONG SAN %.1f mm3%s" % (a, b, v0, note), file=log, flush=True)
            res.append((a, b, ("chong san %.1f mm3" % v0) + note))
            continue
        d = free_direction(col, a, b, objs[a], step, min_mm3)
        if d is None:
            d = free_direction(col, b, a, objs[b], step, min_mm3)
        if log:
            how = "KET" if d is None else "thao theo %s" % np.round(d, 3)
            print("%-40s %-40s %s%s" % (a, b, how, note), file=log, flush=True)
        if d is None:
            res.append((a, b, "ket" + note))
    return res, pairs


def main(argv):
    import FreeCAD as App
    path = argv[0]
    opt = {"only": "", "near": "0.5", "step": "0.2", "allow": "", "json": ""}
    opt.update(a.split("=", 1) for a in argv[1:])   # khoa=gia_tri nhu check.py (freecadcmd tu doc tham so "--x")
    doc = App.openDocument(path)
    objs = {o.Label: o for o in doc.Objects
            if o.isDerivedFrom("Part::Feature") and o.Shape.Solids and not o.Label.startswith("_")}
    only = [s for s in opt["only"].split(",") if s]
    if only:
        objs = {k: v for k, v in objs.items() if any(k.startswith(p) for p in only)}
    allow = [tuple(p.split("|")) for p in opt["allow"].split(",") if "|" in p]
    res, pairs = trapped(objs, None, float(opt["near"]), float(opt["step"]), allow=allow, log=sys.stdout)
    print("\n%d cap dang cham, %d cap BI KET" % (len(pairs), len(res)))
    for a, b, note in res:
        print("KET: %s | %s %s" % (a, b, note))
    if opt["json"]:
        json.dump({"pairs": len(pairs), "trapped": [list(r) for r in res]}, open(opt["json"], "w"), indent=1)
    App.closeDocument(doc.Name)
    return 1 if res else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))   # chay qua fc_cli.py --pass: sys.argv = [script, args...]
