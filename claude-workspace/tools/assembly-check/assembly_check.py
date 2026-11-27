# -*- coding: utf-8 -*-
"""Kiem lap rap that (assembly check) cho Blender 5.2.

Chay:
  blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- <assembly.json>
  blender -b --factory-startup --python-exit-code 1 -P assembly_check.py -- --auto <asm_dir> [--report <file.json>]

Chi dung bpy / bmesh / mathutils + thu vien chuan.
"""

import itertools
import json
import os
import sys

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree


DEFAULT_TOL = {
    "penetration": 0.2,
    "contact": 0.05,
    "path_step": 0.5,
    "seat_stop": 0.5,
    "probe": 2.0,
}

VALID_JOINT_TYPES = {"screw", "bayonet", "snap", "press", "pin", "glue"}
VALID_BLOCKS = {"+x", "-x", "+y", "-y", "+z", "-z", "*"}
DIRS = [
    ("+x", (1.0, 0.0, 0.0)),
    ("-x", (-1.0, 0.0, 0.0)),
    ("+y", (0.0, 1.0, 0.0)),
    ("-y", (0.0, -1.0, 0.0)),
    ("+z", (0.0, 0.0, 1.0)),
    ("-z", (0.0, 0.0, -1.0)),
]

TOL = dict(DEFAULT_TOL)
_OFF_CACHE = {}
_TREE_CACHE = {}


# ---------------------------------------------------------------- STL / bmesh
def load_stl(path):
    """Nap 1 STL thanh bmesh, recalc phap tuyen. KHONG remove_doubles."""
    before = set(bpy.data.objects.keys())
    bpy.ops.wm.stl_import(filepath=path)
    new_names = [n for n in bpy.data.objects.keys() if n not in before]
    if not new_names:
        return None
    ob = bpy.data.objects[new_names[0]]
    mesh = ob.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    try:
        bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.meshes.remove(mesh)
    except Exception:
        pass
    return bm


def bbox_of(bm):
    mn = None
    mx = None
    for v in bm.verts:
        c = v.co
        if mn is None:
            mn = Vector((c.x, c.y, c.z))
            mx = Vector((c.x, c.y, c.z))
            continue
        if c.x < mn.x:
            mn.x = c.x
        if c.y < mn.y:
            mn.y = c.y
        if c.z < mn.z:
            mn.z = c.z
        if c.x > mx.x:
            mx.x = c.x
        if c.y > mx.y:
            mx.y = c.y
        if c.z > mx.z:
            mx.z = c.z
    if mn is None:
        return None
    return (mn, mx)


# ---------------------------------------------------------------- offset tree
def _offset_base(bm, d):
    """Vertices moved along their (averaged) normal by `d`, mesh kept connected.

    Keeping vertices shared (instead of moving each triangle on its own) gives a
    proper shrunk/expanded closed surface. Moving triangles independently makes
    coincident seam faces cross each other and reports false penetration.
    """
    key = (id(bm), round(float(d), 6))
    base = _OFF_CACHE.get(key)
    if base is not None:
        return base
    bm.normal_update()
    index = {}
    verts = []
    for v in bm.verts:
        index[v] = len(verts)
        verts.append(v.co + v.normal * float(d))
    polys = []
    cents = []
    for f in bm.faces:
        idxs = tuple(index[v] for v in f.verts)
        polys.append(idxs)
        c = Vector((0.0, 0.0, 0.0))
        for i in idxs:
            c = c + verts[i]
        cents.append(c / float(len(idxs)))
    base = (verts, polys, cents)
    _OFF_CACHE[key] = base
    return base


def offset_tree(bm, d, move=None):
    """BVH cua be mat da dich theo phap tuyen `d`, roi tinh tien `move`.

    Tra ve (tree, centroids).
    """
    if move is None:
        move = Vector((0.0, 0.0, 0.0))
    verts0, polys, cents0 = _offset_base(bm, d)
    if move.length_squared < 1e-12:
        tree = BVHTree.FromPolygons(verts0, polys)
        return tree, cents0
    verts = [v + move for v in verts0]
    cents = [c + move for c in cents0]
    tree = BVHTree.FromPolygons(verts, polys)
    return tree, cents


def _static(bm, d):
    key = (id(bm), round(float(d), 6))
    t = _TREE_CACHE.get(key)
    if t is None:
        t = offset_tree(bm, d)
        _TREE_CACHE[key] = t
    return t


def pen_tree(p, move=None):
    d = -TOL["penetration"] / 2.0
    if move is None or move.length_squared < 1e-12:
        return _static(p["bm"], d)
    return offset_tree(p["bm"], d, move)


def contact_tree(p):
    return _static(p["bm"], TOL["contact"] / 2.0)


# ---------------------------------------------------------------- helpers
def _segments(ins):
    segs = []
    if not isinstance(ins, dict):
        return segs
    moves = ins.get("moves")
    if moves:
        for m in moves:
            segs.append(Vector((float(m[0]), float(m[1]), float(m[2]))))
        return segs
    if "dir" in ins and "from" in ins:
        d = Vector((float(ins["dir"][0]), float(ins["dir"][1]), float(ins["dir"][2])))
        if d.length > 1e-12:
            segs.append(d.normalized() * float(ins["from"]))
    return segs


def _sample_offset(pts, cum, s):
    if len(pts) == 1:
        return pts[0].copy()
    for i in range(1, len(pts)):
        if s <= cum[i] + 1e-12:
            seg_len = cum[i] - cum[i - 1]
            if seg_len < 1e-12:
                return pts[i].copy()
            t = (s - cum[i - 1]) / seg_len
            return pts[i - 1].lerp(pts[i], t)
    return pts[-1].copy()


def _bbox_maybe(ba, bb, pad):
    if ba is None or bb is None:
        return False
    (amn, amx) = ba
    (bmn, bmx) = bb
    if amx.x + pad < bmn.x or bmx.x + pad < amn.x:
        return False
    if amx.y + pad < bmn.y or bmx.y + pad < amn.y:
        return False
    if amx.z + pad < bmn.z or bmx.z + pad < amn.z:
        return False
    return True


def _issue(level, check, parts, msg, **extra):
    d = {"level": level, "check": check, "parts": list(parts), "msg": msg}
    d.update(extra)
    return d


# ---------------------------------------------------------------- 1. config
def check_config(cfg, stl_names):
    issues = []
    parts = cfg.get("parts", {}) or {}
    names = set(parts.keys())
    stl = set(stl_names)

    for n in sorted(stl - names):
        issues.append(_issue("FAIL", "config", [n],
                             "STL '%s' co trong thu muc nhung khong khai bao trong parts" % n))
    for n in sorted(names - stl):
        issues.append(_issue("FAIL", "config", [n],
                             "part '%s' khai bao nhung thieu file STL" % n))

    order = cfg.get("order", []) or []
    oset = set(order)
    for n in sorted(names - oset):
        issues.append(_issue("FAIL", "config", [n],
                             "part '%s' khong co trong order" % n))
    for n in order:
        if n not in names:
            issues.append(_issue("FAIL", "config", [n],
                                 "order co '%s' nhung khong khai bao trong parts" % n))

    for n, p in parts.items():
        if p.get("fixed"):
            continue
        ins = p.get("insert")
        ok = isinstance(ins, dict) and (
            ("dir" in ins and "from" in ins) or bool(ins.get("moves"))
        )
        if not ok:
            issues.append(_issue("FAIL", "config", [n],
                                 "part '%s' khong fixed nhung thieu insert (dir+from hoac moves)" % n))
        if isinstance(ins, dict) and ins.get("with"):
            for m in ins.get("with") or []:
                if m not in names:
                    issues.append(_issue("FAIL", "config", [n], "insert.with cua '%s' tro toi part '%s' khong ton tai" % (n, m)))
                elif m in order and n in order and order.index(m) > order.index(n):
                    issues.append(_issue("FAIL", "config", [n], "insert.with: '%s' phai dung truoc '%s' trong order" % (m, n)))
        if isinstance(ins, dict) and "flex" in ins:
            fx = ins.get("flex")
            snap = any(j.get("type") == "snap" and (j.get("parts") or [None])[0] == n
                       for j in cfg.get("joints", []) or [])
            if not isinstance(fx, (int, float)) or not 0.0 < float(fx) <= 1.0:
                issues.append(_issue("FAIL", "config", [n],
                                     "insert.flex cua '%s' phai trong (0; 1,0] mm" % n))
            elif not snap:
                issues.append(_issue("FAIL", "config", [n],
                                     "insert.flex chi dung cho part co joint snap (parts[0] = '%s')" % n))

    for j in cfg.get("joints", []) or []:
        jtype = j.get("type")
        if jtype not in VALID_JOINT_TYPES:
            issues.append(_issue("FAIL", "config", list(j.get("parts", [])),
                                 "joint type '%s' khong hop le" % jtype))
        if jtype == "pin":
            pp = j.get("pin_part")
            if not pp or pp not in names:
                issues.append(_issue("FAIL", "config", list(j.get("parts", [])),
                                     "joint pin thieu pin_part hop le ('%s' chua duoc ve)" % pp))
        for bl in j.get("blocks", []) or []:
            if bl not in VALID_BLOCKS:
                issues.append(_issue("FAIL", "config", list(j.get("parts", [])),
                                     "joint blocks co gia tri '%s' khong hop le" % bl))
        for pn in j.get("parts", []) or []:
            if pn not in names:
                issues.append(_issue("FAIL", "config", [pn],
                                     "joint tro toi part '%s' khong ton tai" % pn))
        if not j.get("note"):
            issues.append(_issue("FAIL", "config", list(j.get("parts", [])),
                                 "joint thieu note"))
    return issues


# ---------------------------------------------------------------- 2. pairs
def check_pairs(parts, allowed):
    issues = []
    allowed_set = set()
    for pair in allowed or []:
        if len(pair) == 2:
            allowed_set.add(frozenset((pair[0], pair[1])))
    names = sorted(parts.keys())
    pad = TOL["contact"]
    for a, b in itertools.combinations(names, 2):
        pa = parts[a]
        pb = parts[b]
        if not _bbox_maybe(pa.get("bbox"), pb.get("bbox"), pad):
            continue
        ta, ca = pen_tree(pa)
        tb, cb = pen_tree(pb)
        ov = ta.overlap(tb)
        if ov:
            sx = sy = sz = 0.0
            for i, j in ov:
                mid = (ca[i] + cb[j]) / 2.0
                sx += mid.x
                sy += mid.y
                sz += mid.z
            m = float(len(ov))
            where = [round(sx / m, 1), round(sy / m, 1), round(sz / m, 1)]
            issues.append(_issue("FAIL", "pair", [a, b],
                                 "'%s' va '%s' chong vat lieu" % (a, b),
                                 where=where, n=len(ov)))
            continue
        ca_tree, _ = contact_tree(pa)
        cb_tree, _ = contact_tree(pb)
        if ca_tree.overlap(cb_tree):
            if frozenset((a, b)) not in allowed_set:
                issues.append(_issue("WARN", "contact", [a, b],
                                     "'%s' va '%s' cham nhau (khong trong allowed_contacts)" % (a, b)))
    return issues


# ---------------------------------------------------------------- 3. paths
def check_paths(cfg, parts):
    issues = []
    order = cfg.get("order", []) or []
    pen = TOL["penetration"]
    step = TOL["path_step"]
    stop = TOL["seat_stop"]
    if step <= 0:
        step = 0.5
    pinfo = cfg.get("parts", {}) or {}
    for idx, name in enumerate(order):
        if name not in parts:
            continue
        p = parts[name]
        info = pinfo.get(name, {})
        if info.get("fixed"):
            continue
        ins = info.get("insert")
        if not ins:
            continue
        segs = _segments(ins)
        if not segs:
            continue
        k = len(segs)
        qs = [None] * (k + 1)
        qs[k] = Vector((0.0, 0.0, 0.0))
        for i in range(k - 1, -1, -1):
            qs[i] = qs[i + 1] - segs[i]
        cum = [0.0]
        for i in range(1, k + 1):
            cum.append(cum[-1] + (qs[i] - qs[i - 1]).length)
        total = cum[-1]
        if total <= 1e-9:
            continue
        flex = float(ins.get("flex", 0.0) or 0.0) if isinstance(ins, dict) else 0.0
        flex = min(max(flex, 0.0), 1.0)
        # cum lap san (vd. vong ep da xoay khoa tren vanh loa): part trong insert.with di cung, khong la vat can
        mates = set(ins.get("with", []) or []) if isinstance(ins, dict) else set()
        obstacles = [parts[o] for o in order[:idx] if o in parts and o not in mates]
        if not obstacles:
            continue
        s = 0.0
        blocked = None
        guard = 0
        while True:
            remaining = total - s
            if remaining < stop - 1e-9:
                break
            off = _sample_offset(qs, cum, s)
            # lay snap bien dang khi ep: part co insert.flex duoc co them flex mm tren duong lap (khong ap dung o vi tri lap)
            mt, _ = offset_tree(p["bm"], -pen / 2.0 - flex, off)
            for ob in obstacles:
                ot, _ = _static(ob["bm"], -pen / 2.0)
                if mt.overlap(ot):
                    blocked = (ob["name"], round(remaining, 1))
                    break
            if blocked:
                break
            s += step
            guard += 1
            if guard > 2000000:
                break
        if blocked:
            issues.append(_issue("FAIL", "path", [name, blocked[0]],
                                 "duong lap cua '%s' bi '%s' chan" % (name, blocked[0]),
                                 at=blocked[1]))
    return issues


# ---------------------------------------------------------------- 4. retention
def check_retention(cfg, parts):
    issues = []
    probe = TOL["probe"]
    pen = TOL["penetration"]
    pinfo = cfg.get("parts", {}) or {}
    joints = cfg.get("joints", []) or []
    for name, p in parts.items():
        info = pinfo.get(name, {})
        if info.get("fixed"):
            continue
        others = [q for n2, q in parts.items() if n2 != name]
        free = []
        for label, vec in DIRS:
            move = Vector(vec) * probe
            mt, _ = offset_tree(p["bm"], -pen / 2.0, move)
            blocked = False
            for ob in others:
                ot, _ = _static(ob["bm"], -pen / 2.0)
                if mt.overlap(ot):
                    blocked = True
                    break
            if not blocked:
                free.append(label)
        covered = set()
        for j in joints:
            jp = j.get("parts", []) or []
            if jp and jp[0] == name:
                for bl in j.get("blocks", []) or []:
                    if bl == "*":
                        covered.update(lbl for lbl, _ in DIRS)
                    else:
                        covered.add(bl)
        uncovered = [lbl for lbl in free if lbl not in covered]
        if uncovered:
            issues.append(_issue("FAIL", "retention", [name],
                                 "'%s' khong duoc giu theo huong: %s" % (name, ", ".join(uncovered)),
                                 free_dirs=uncovered))
    for j in joints:
        if j.get("type") == "glue":
            issues.append(_issue("WARN", "joint", list(j.get("parts", [])),
                                 "joint glue: da dan keo, khong thao duoc"))
    return issues


# ---------------------------------------------------------------- report
def write_report(path, names, issues, tol):
    fail = sum(1 for i in issues if i["level"] == "FAIL")
    warn = sum(1 for i in issues if i["level"] == "WARN")
    verdict = "FAIL" if fail else "PASS"
    rep = {
        "verdict": verdict,
        "parts": sorted(names),
        "issues": issues,
        "tol": tol,
    }
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    for i in issues:
        print("ASM %s %s %s %s" % (i["level"], i["check"], i["parts"], i["msg"]))
    print("ASSEMBLY %s fail=%d warn=%d" % (verdict, fail, warn))
    return verdict


def resolve_tol(cfg):
    tol = dict(DEFAULT_TOL)
    user = cfg.get("tol", {}) or {}
    for k in DEFAULT_TOL:
        if k in user:
            try:
                tol[k] = float(user[k])
            except (TypeError, ValueError):
                pass
    return tol


def list_stl(asm_dir):
    mapping = {}
    if not os.path.isdir(asm_dir):
        return mapping
    for fn in os.listdir(asm_dir):
        low = fn.lower()
        if low.endswith(".stl"):
            mapping[fn[:-4]] = os.path.join(asm_dir, fn)
    return mapping


def build_parts(mapping, names):
    parts = {}
    for n in names:
        path = mapping.get(n)
        if not path:
            continue
        bm = load_stl(path)
        if bm is None:
            continue
        parts[n] = {"name": n, "bm": bm, "bbox": bbox_of(bm)}
    return parts


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []

    if not args:
        print("ASSEMBLY FAIL fail=1 warn=0")
        print("ASM FAIL config [] thieu doi so (assembly.json hoac --auto <asm_dir>)")
        sys.exit(1)

    auto = args[0] == "--auto"
    if auto:
        if len(args) < 2:
            print("ASSEMBLY FAIL fail=1 warn=0")
            print("ASM FAIL config [] --auto can <asm_dir>")
            sys.exit(1)
        asm_dir = os.path.abspath(args[1])
        report_path = None
        if "--report" in args:
            k = args.index("--report")
            if k + 1 < len(args):
                report_path = os.path.abspath(args[k + 1])
        if not report_path:
            report_path = os.path.join(asm_dir, "assembly-report.json")
        tol = dict(DEFAULT_TOL)
        TOL.update(tol)
        mapping = list_stl(asm_dir)
        parts = build_parts(mapping, sorted(mapping.keys()))
        issues = check_pairs(parts, [])
        verdict = write_report(report_path, sorted(mapping.keys()), issues, tol)
        sys.exit(1 if verdict == "FAIL" else 0)

    cfg_path = os.path.abspath(args[0])
    base_dir = os.path.dirname(cfg_path)
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    tol = resolve_tol(cfg)
    TOL.update(tol)
    asm_dir = cfg.get("asm_dir", "asm")
    if not os.path.isabs(asm_dir):
        asm_dir = os.path.normpath(os.path.join(base_dir, asm_dir))
    mapping = list_stl(asm_dir)
    stl_names = sorted(mapping.keys())
    declared = sorted((cfg.get("parts", {}) or {}).keys())
    parts = build_parts(mapping, declared)

    issues = []
    issues += check_config(cfg, stl_names)
    issues += check_pairs(parts, cfg.get("allowed_contacts", []) or [])
    issues += check_paths(cfg, parts)
    issues += check_retention(cfg, parts)

    report_path = os.path.join(base_dir, "assembly-report.json")
    verdict = write_report(report_path, declared, issues, tol)
    sys.exit(1 if verdict == "FAIL" else 0)


if __name__ == "__main__":
    main()
