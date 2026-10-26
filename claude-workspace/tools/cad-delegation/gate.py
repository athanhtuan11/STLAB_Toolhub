# Cong kiem (gate) cho viec giao dung chi tiet CAD: doc spec.yaml, kiem file chi tiet nguoi thuc thi xuat ra,
# ghi gate.json (PASS/FAIL tung muc + so do) de nguoi thuc thi tu sua. Khong can mo GUI.
#   "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" gate.py <thu muc chua spec.yaml>
# Ket qua: gate.json {passed, summary, checks[], warnings[]}; "vuon ra" theo lop chi la canh bao (slicer in duoc).
# Spec (xem pilot/*/spec.yaml):
#   output: part.step                  file nguoi thuc thi xuat (STEP 1 solid, he toa do cua spec)
#   context: context.FCStd             chi tiet lan can (KHONG co chi tiet mau), cung he toa do
#   bbox: {min: [..], max: [..], tol: 0.3}
#   empty:  [{name, cyl|box}]          vung phai RONG (lo, khe, rang): giao voi chi tiet < 0.01 mm3
#   filled: [{name, cyl|box, min_frac}]  vung phai DAC (thanh, vong quanh lo): ti le nam trong chi tiet >= min_frac
#   neighbors: [{label, min_gap, max_gap?}]   khoang cach toi lan can (0 = cho cham, nhung khong chong)
#   motions: [{name, kind: translate|rotate, vector|axis+point, total, step, against: [labels], move: part|<label>}]
#   print: {down: [nx, ny, nz]}        mat co phap tuyen nay up xuong ban in; kiem support + kiem lop
#   cyl: {base: [x,y,z], axis: [..], r, h}   box: {min: [..], max: [..]}
import json, math, os, sys, tempfile
import FreeCAD as App, Part, MeshPart
import yaml

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "robotics-cad", "scripts"))

run = [a for a in sys.argv[1:] if not a.endswith(".py")][0]
spec = yaml.safe_load(open(os.path.join(run, "spec.yaml"), encoding="utf-8"))
G = spec["gate"]
out = dict(spec=spec.get("part"), checks=[], warnings=[], passed=False)


def chk(name, ok, **info):
    out["checks"].append(dict(name=name, ok=bool(ok), **info))
    return ok


def solid(d):
    if "cyl" in d:
        c = d["cyl"]
        return Part.makeCylinder(c["r"], c["h"], V(*c["base"]), V(*c["axis"]))
    b = d["box"]
    lo, hi = V(*b["min"]), V(*b["max"])
    return Part.makeBox(hi.x - lo.x, hi.y - lo.y, hi.z - lo.z, lo)


def finish():
    out["passed"] = all(c["ok"] for c in out["checks"])
    out["summary"] = "%d/%d PASS" % (sum(c["ok"] for c in out["checks"]), len(out["checks"]))
    json.dump(out, open(os.path.join(run, "gate.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("GATE", "PASS" if out["passed"] else "FAIL", out["summary"], "- chi tiet: gate.json", flush=True)
    for c in out["checks"]:
        if not c["ok"]:
            print("  FAIL", json.dumps(c, ensure_ascii=False), flush=True)
    sys.exit(0)


# ---- 1. doc chi tiet ----
p = os.path.join(run, G["output"])
if not chk("output ton tai", os.path.exists(p), path=G["output"]):
    finish()
s = Part.read(p)
sol = s.Solids
chk("hop le + 1 solid", s.isValid() and len(sol) == 1 and sol[0].Volume > 0, valid=s.isValid(), solids=len(sol),
    volume=round(s.Volume, 1))
if not sol:
    finish()
part = sol[0] if len(sol) == 1 else s
bb = part.BoundBox
if "bbox" in G:
    t = G["bbox"].get("tol", 0.3)
    got = [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]
    want = G["bbox"]["min"] + G["bbox"]["max"]
    err = [round(g - w, 2) for g, w in zip(got, want)]
    chk("bao ngoai", max(abs(e) for e in err) <= t, got=[round(x, 2) for x in got], want=want, err=err, tol=t)

# ---- 2. vung rong / dac ----
for e in G.get("empty", []):
    v = part.common(solid(e)).Volume
    chk("rong: " + e["name"], v < 0.01, overlap_mm3=round(v, 3))
for f in G.get("filled", []):
    sh = solid(f)
    frac = part.common(sh).Volume / sh.Volume
    chk("dac: " + f["name"], frac >= f.get("min_frac", 0.98), frac=round(frac, 3), min_frac=f.get("min_frac", 0.98))

# ---- 3. lan can ----
ctx = {}
if G.get("context"):
    d = App.openDocument(os.path.join(run, G["context"]))
    ctx = {o.Label: o.Shape for o in d.Objects if hasattr(o, "Shape") and o.Shape.Solids}
for n in G.get("neighbors", []):
    o = ctx[n["label"]]
    ov = part.common(o).Volume
    gap = part.distToShape(o)[0] if ov < 0.01 else 0.0
    ok = ov < 0.01 and gap >= n.get("min_gap", 0) - 0.01 and gap <= n.get("max_gap", 1e9) + 0.01
    chk("lan can: " + n["label"], ok, overlap_mm3=round(ov, 3), gap=round(gap, 3), min_gap=n.get("min_gap", 0),
        max_gap=n.get("max_gap"))

# ---- 4. chuyen dong lap/thao ----
for m in G.get("motions", []):
    mv = part if m.get("move", "part") == "part" else ctx[m["move"]]
    others = [part if a == "part" else ctx[a] for a in m["against"]]
    n_ = int(math.ceil(m["total"] / m["step"]))
    bad = None
    for k in range(0, n_ + 1):
        x = min(k * m["step"], m["total"])
        c = mv.copy()
        if m["kind"] == "translate":
            c.translate(V(*m["vector"]).normalize() * x)
        else:
            c.rotate(V(*m["point"]), V(*m["axis"]), x)
        for a, o in zip(m["against"], others):
            v = c.common(o).Volume
            if v > 0.01:
                bad = dict(at=round(x, 2), against=a, overlap_mm3=round(v, 3))
                break
        if bad:
            break
    chk("chuyen dong: " + m["name"], bad is None, **(bad or {"total": m["total"]}))

# ---- 5. in duoc (khong support, khong roi lop) ----
if "print" in G:
    import printability as pr
    c = part.copy()
    down = V(*G["print"]["down"]).normalize()
    rot = App.Rotation(down, V(0, 0, -1))
    c.Placement = App.Placement(V(), rot).multiply(c.Placement)
    stl = os.path.join(tempfile.gettempdir(), "gate_print.stl")
    MeshPart.meshFromShape(Shape=c, LinearDeflection=0.03, AngularDeflection=0.2618).write(stl)
    r = pr.phan_tich(stl)
    chk("in: khong can support", not r["can_support"], vung=r["cum_nho"][:3])
    lop = pr.kiem_lop(stl)
    # "vuon ra" (bo canh sat ban, dinh lo ngang, cau noi ngan) = CANH BAO nhu quy trinh du an; roi lop = FAIL
    chk("in: kiem lop (khong co cum roi)", not [x for x in lop if x.get("loai") != "vuon ra"],
        loi=[x for x in lop if x.get("loai") != "vuon ra"][:5])
    out["warnings"] += [dict(name="in: vuon ra theo lop (xem, khong bat buoc sua)", **x) for x in lop if x.get("loai") == "vuon ra"][:5]
finish()
