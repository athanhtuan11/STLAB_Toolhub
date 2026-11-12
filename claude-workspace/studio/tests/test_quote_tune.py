# Gate "Toi uu in" (Claude viet 2026-11-12, executor KHONG sua). Nguon: docs/reports/slicer-auto-tune-research.md muc 3 + 8.9.
# Chay tu thu muc studio (can Bambu Studio + FreeCAD 1.1 tren may):
#   .venv/Scripts/python.exe tests/test_quote_tune.py
# Phan A (khong can slicer): presets.json = dung 7 khoi JSON muc 8.9; geometry_profile + tune_rules tren luoi tu dung.
# Phan B (can slicer): quote_slice.py nhan overrides=<json>; trang /quote?mode=tune + /api/quote/tune/analyze + /api/quote/tune/slice.
import io, json, os, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
ROOT = STUDIO.parent
SCRIPTS = ROOT / "tools" / "print" / "scripts"
REPORT = ROOT / "docs" / "reports" / "slicer-auto-tune-research.md"
sys.path.insert(0, str(STUDIO))
sys.path.insert(0, str(SCRIPTS))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-tune-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
os.environ["STLAB_QUOTES_WORK"] = str(TMP / "work")
FCPY = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


def stl(path, boxes, cell=1.0):
    """Ghi STL ASCII KIN (1 than, mat chung) tu hop nguyen (x0,y0,z0,x1,y1,z1) theo luoi voxel 'cell' mm."""
    fill = set()
    for x0, y0, z0, x1, y1, z1 in boxes:
        for i in range(int(x0 / cell), int(x1 / cell)):
            for j in range(int(y0 / cell), int(y1 / cell)):
                for k in range(int(z0 / cell), int(z1 / cell)):
                    fill.add((i, j, k))
    out = ["solid t"]
    dirs = [((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]), ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
            ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]), ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
            ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]), ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)])]
    for (i, j, k) in fill:
        for (dx, dy, dz), q in dirs:
            if (i + dx, j + dy, k + dz) in fill:
                continue
            v = [((i + a) * cell, (j + b) * cell, (k + c) * cell) for a, b, c in q]
            for tri in ((v[0], v[1], v[2]), (v[0], v[2], v[3])):
                out += ["facet normal %d %d %d" % (dx, dy, dz), "outer loop"] + ["vertex %g %g %g" % p for p in tri] + ["endloop", "endfacet"]
    out.append("endsolid t")
    Path(path).write_text(chr(10).join(out), encoding="ascii")
    return Path(path)


def plate_with_holes(path, n_holes):
    """Tam 40x40x3 co n lo vuong 4x4 xuyen (luoi kin, genus = n)."""
    boxes = []
    edges = [0]
    for i in range(n_holes):
        edges += [6 + 8 * i, 10 + 8 * i]
    edges.append(40)
    for i in range(0, len(edges), 2):
        boxes.append((edges[i], 0, 0, edges[i + 1], 40, 3))
    for i in range(n_holes):
        x = 6 + 8 * i
        boxes += [(x, 0, 0, x + 4, 18, 3), (x, 22, 0, x + 4, 40, 3)]
    return stl(path, boxes)


# ---------------- A1. presets.json khop muc 8.9 ----------------
txt = REPORT.read_text(encoding="utf-8")
sec = txt.split("### 8.9", 1)[1] if "### 8.9" in txt else ""
names = re.findall(r"^#### `([a-z_]+)`", sec, re.M)
blocks = [json.loads(b) for b in re.findall(r"```json\n(.*?)\n```", sec, re.S)]
want = dict(zip(names, blocks))
PJ = SCRIPTS / "tune" / "presets.json"
try:
    presets = json.loads(PJ.read_text(encoding="utf-8"))
except Exception as e:  # noqa: BLE001
    presets = {}
    ok(False, f"doc {PJ}: {e!r}")
ok(len(want) == 7, f"bao cao co 7 preset ({sorted(want)})")
for k, v in want.items():
    p = presets.get(k, {})
    ok(p.get("process") == v["process"] and p.get("filament") == v["filament"], f"preset {k} = khoi JSON muc 8.9")

# ---------------- A2. geometry_profile ----------------
import geometry_profile as gp  # noqa: E402
import tune_rules as tr  # noqa: E402

cube = stl(TMP / "cube.stl", [(0, 0, 0, 30, 30, 10)], cell=2.0)                       # chan 900 mm2, thap, khong nho ra
tall = stl(TMP / "tall.stl", [(0, 0, 0, 6, 6, 30)], cell=2.0)                          # chan 36 mm2, cao/manh 5
tee = stl(TMP / "tee.stl", [(10, 10, 0, 20, 20, 20), (0, 0, 20, 30, 30, 23)])   # mai nho ra 30x30 tren cot 10x10
holes = plate_with_holes(TMP / "holes.stl", 4)
small = stl(TMP / "small.stl", [(0, 0, 0, 8, 8, 4)])

fc, ft, fe, fh, fs = (gp.features(p) for p in (cube, tall, tee, holes, small))
for f, n in ((fc, "cube"), (ft, "tall"), (fe, "tee"), (fh, "holes"), (fs, "small")):
    ok(all(k in f for k in ("can_support", "contact_mm2", "height_mm", "aspect", "max_overhang_mm2", "curved_frac",
                            "top_flat_mm2", "holes", "bbox_mm", "small")), f"features {n} du truong")
ok(not fc["can_support"] and abs(fc["contact_mm2"] - 900) < 5 and fc["holes"] == 0, f"cube: khong support, chan 900, 0 lo ({fc['contact_mm2']}, {fc['holes']})")
ok(abs(fc["top_flat_mm2"] - 900) < 5, f"cube: mat tren phang 900 ({fc['top_flat_mm2']})")
ok(ft["aspect"] >= 2.5 and ft["contact_mm2"] < 120, f"tall: cao/manh ({ft['aspect']}, {ft['contact_mm2']})")
ok(fe["can_support"] and fe["max_overhang_mm2"] > 100, f"tee: can support, mang nho ra > 100 mm2 ({fe['max_overhang_mm2']})")
ok(fh["holes"] == 4, f"tam 4 lo: holes = 4 ({fh['holes']})")
ok(fs["small"] and not fc["small"], "small: bbox < 20 mm")
ok(fc["curved_frac"] < 0.05, f"cube: khong mat cong ({fc['curved_frac']})")

# ---------------- A3. tune_rules ----------------
def S(f, goals=()):
    r = tr.suggest(f, goals=list(goals))
    ok(set(r) >= {"process", "filament", "items"} and all(set(i) >= {"key", "value", "pack", "reason", "level"} for i in r["items"]),
       "suggest tra process/filament/items (key,value,pack,reason,level)")
    return r

rc, rt, re_, rh, rs = S(fc), S(ft), S(fe), S(fh), S(fs)
ok(rc["process"].get("enable_support") == "0" and rc["process"].get("brim_type") == "no_brim", f"cube: tat support, khong brim ({rc['process'].get('enable_support')}, {rc['process'].get('brim_type')})")
ok(rt["process"].get("brim_type") == "outer_only" and all(rt["process"].get(k) == v for k, v in presets["tall_thin"]["process"].items()),
   "tall: brim outer_only + preset tall_thin")
ok(re_["process"].get("enable_support") == "1" and re_["process"].get("support_type") == "normal(auto)", f"tee: bat support, mang lon -> normal(auto) ({re_['process'].get('support_type')})")
ok(all(re_["process"].get(k) == v for k, v in presets["support_easy"]["process"].items() if k != "support_type" and k != "support_style"),
   "tee mac dinh: preset support_easy")
rp = S(fe, ["support_pretty"])
ok(all(rp["process"].get(k) == v for k, v in presets["support_pretty"]["process"].items()), "muc tieu support_pretty -> preset support_pretty")
ok(all(rh["process"].get(k) == v for k, v in presets["petg_stringing"]["process"].items())
   and all(rh["filament"].get(k) == v for k, v in presets["petg_stringing"]["filament"].items()), "4 lo -> preset petg_stringing (process + filament)")
ok(all(rs["process"].get(k) == v for k, v in presets["small_parts"]["process"].items()), "chi tiet nho -> preset small_parts")
rsp = S(fc, ["surface_pretty"])
ok(all(rsp["process"].get(k) == v for k, v in presets["surface_pretty"]["process"].items()), "muc tieu surface_pretty -> preset surface_pretty")
ok(all(i["level"] in ("S", "P") for r in (rc, rt, re_, rh, rs, rp, rsp) for i in r["items"]), "moi muc co muc nguon S/P")
ok(any(i["key"] == "enable_support" for i in re_["items"]) and all(i["reason"] for i in re_["items"]), "moi muc co ly do")

# ---------------- B1. quote_slice.py overrides= ----------------
ov = TMP / "ov.json"
ov.write_text(json.dumps({"process": {"layer_height": "0.16", "brim_type": "outer_only", "brim_object_gap": "0.15"},
                          "filament": {"filament_retraction_length": ["0.6"]}}), encoding="utf-8")
out = TMP / "qs"
r = subprocess.run([str(FCPY), str(SCRIPTS / "quote_slice.py"), str(out), 'filament=Bambu PETG Basic @BBL A1',
                    "support=off", f"overrides={ov}", str(cube)], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
last = (r.stdout.strip().splitlines() or ["{}"])[-1]
try:
    res = json.loads(last)
except ValueError:
    res = {}
ok(res.get("status") in ("ok", "warn"), f"quote_slice overrides= chay duoc ({res.get('status')}, {res.get('errors')})")
cfg = {}
q3 = out / "quote.3mf"
if q3.exists():
    with zipfile.ZipFile(q3) as z:
        n = [x for x in z.namelist() if x.endswith("project_settings.config")]
        cfg = json.loads(z.read(n[0])) if n else {}
ok(str(cfg.get("layer_height")) == "0.16" and cfg.get("brim_object_gap") == "0.15", f"3mf mang ghi de process ({cfg.get('layer_height')}, {cfg.get('brim_object_gap')})")
ok(cfg.get("filament_retraction_length") == ["0.6"], f"3mf mang ghi de filament ({cfg.get('filament_retraction_length')})")

# ---------------- B2. Toolhub ----------------
from toolhub import create_app  # noqa: E402
app = create_app()
c = app.test_client()
B = "http://127.0.0.1:5050"
H = {"X-Studio": "1"}
h = c.get("/quote?mode=tune", base_url=B)
ok(h.status_code == 200 and "Tối ưu in" in h.get_data(as_text=True), "trang /quote?mode=tune co 'Tối ưu in'")
up = c.post("/api/quote/upload", data={"file": (io.BytesIO(tee.read_bytes()), "tee.stl")}, content_type="multipart/form-data", headers=H, base_url=B)
tok = (up.get_json() or {}).get("token")
a = c.post("/api/quote/tune/analyze", json={"token": tok, "goals": ["support_pretty"]}, headers=H, base_url=B)
aj = a.get_json() or {}
ok(a.status_code == 200 and aj.get("features", {}).get("can_support") is True and aj.get("items"), f"analyze: features + items ({a.status_code})")
ok((aj.get("process") or {}).get("enable_support_ironing") == "1", "analyze theo muc tieu support_pretty")
edited = dict(aj.get("process") or {}, layer_height="0.16")
s = c.post("/api/quote/tune/slice", json={"token": tok, "material": "PETG", "process": edited, "filament": aj.get("filament") or {}}, headers=H, base_url=B)
sj = s.get_json() or {}
ok(s.status_code == 200 and set(sj) >= {"default", "tuned"}, f"slice: tra 2 phuong an default + tuned ({s.status_code}, {sj.get('error')})")
for k in ("default", "tuned"):
    v = sj.get(k) or {}
    ok(v.get("image_url") and v.get("download_url") and v.get("hours") is not None and v.get("grams") is not None, f"slice {k}: anh, file 3mf, gio, gam")
if sj.get("tuned", {}).get("download_url"):
    d = c.get(sj["tuned"]["download_url"], base_url=B)
    ok(d.status_code == 200 and d.data[:2] == b"PK", "tai .3mf phuong an toi uu")
    try:
        with zipfile.ZipFile(io.BytesIO(d.data)) as z:
            n = [x for x in z.namelist() if x.endswith("project_settings.config")]
            cf = json.loads(z.read(n[0]))
        ok(str(cf.get("layer_height")) == "0.16" and cf.get("enable_support_ironing") == "1", "3mf toi uu mang thong so da chinh")
    except Exception as e:  # noqa: BLE001
        ok(False, f"doc 3mf toi uu: {e!r}")

bad = c.post("/api/quote/tune/analyze", json={"token": tok}, base_url=B)
ok(bad.status_code == 403, "POST tune thieu X-Studio -> 403 (khong noi long bao ve)")
print(("GATE FAIL (%d)" % len(fails)) if fails else "GATE PASS")
sys.exit(1 if fails else 0)
