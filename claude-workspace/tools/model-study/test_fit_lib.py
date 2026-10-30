# Gate cho fit-library/fit_lib.py (Claude viet 2026-10-30, executor KHONG sua file nay).
#   .venv\Scripts\python.exe test_fit_lib.py        (chay trong tools/model-study)
# Kho thong so lap ghep: kiem schema, tra cuu (uu tien verified), them muc tu ket qua measure_features.
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "fit-library")
OUT = os.path.join(HERE, "_out", "_fitlib_test")
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
sys.path.insert(0, LIB)
import fit_lib as fl  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1) Kho that hop le
real = fl.load()
check(len(real) >= 5, f"kho that co >= 5 muc: {len(real)}")
check(fl.validate(real) == [], f"kho that phai hop le: {fl.validate(real)}")

# 2) validate bat loi
E = dict(id="x/a", interface="rotate-joint-5mm", fit="rotate", hole_mm=5.4, shaft_mm=5.0, clearance_mm=0.4,
         nominal_mm=None, source={"model": "m", "method": "stl-fit"}, print={}, confidence=0.9, verified=False, note="")
bad = [
    ({**E, "fit": "lung-tung"}, "fit"),
    ({**E, "clearance_mm": 0.3}, "clearance"),          # 5.4 - 5.0 = 0.4, lech > 0.005
    ({**E, "confidence": 1.5}, "confidence"),
    ({k: v for k, v in E.items() if k != "interface"}, "interface"),
    ({**E, "source": {"model": "m"}}, "method"),
    ({**E, "hole_mm": None, "shaft_mm": None}, "hole_mm"),  # phai co it nhat 1 kich thuoc
]
for entry, word in bad:
    errs = fl.validate([entry])
    check(errs and any(word in e for e in errs), f"validate phai bao loi '{word}': {errs}")
dup = fl.validate([E, dict(E)])
check(dup and any("id" in e for e in dup), f"id trung phai bao loi: {dup}")
check(fl.validate([E]) == [], f"muc dung khong loi: {fl.validate([E])}")

# 3) Tra cuu + khuyen nghi: verified thang community
path = os.path.join(OUT, "fits.json")
entries = [
    {**E, "id": "c/1", "hole_mm": 5.40, "shaft_mm": 5.00, "clearance_mm": 0.40, "confidence": 0.8},
    {**E, "id": "c/2", "hole_mm": 5.50, "shaft_mm": 5.00, "clearance_mm": 0.50, "confidence": 0.9},
    {**E, "id": "c/3", "hole_mm": 5.30, "shaft_mm": 5.00, "clearance_mm": 0.30, "confidence": 0.7},
    {**E, "id": "v/1", "hole_mm": 5.35, "shaft_mm": 5.00, "clearance_mm": 0.35, "confidence": 1.0, "verified": True,
     "source": {"model": "stlab", "method": "print-test"}},
    {**E, "id": "o/1", "interface": "screw-M3", "fit": "clearance", "hole_mm": 3.4, "shaft_mm": None,
     "clearance_mm": None, "nominal_mm": 3.0},
]
json.dump({"about": "test", "entries": entries}, open(path, "w", encoding="utf-8"))
lib = fl.load(path)
got = fl.lookup(lib, "rotate-joint-5mm")
check([e["id"] for e in got][:1] == ["v/1"], f"lookup: verified dung dau: {[e['id'] for e in got]}")
check([e["id"] for e in got][1:] == ["c/2", "c/1", "c/3"], f"lookup: sau do confidence giam dan: {[e['id'] for e in got]}")
check(fl.lookup(lib, "khong-co") == [], "interface khong co -> []")
rec = fl.recommend(lib, "rotate-joint-5mm")
check(rec and rec.get("basis") == "verified" and abs(rec.get("clearance_mm", -1) - 0.35) < 1e-9
      and rec.get("ids") == ["v/1"], f"recommend: co verified -> chi dung verified: {rec}")
lib2 = [e for e in lib if e["id"] != "v/1"]
rec2 = fl.recommend(lib2, "rotate-joint-5mm")
check(rec2 and rec2.get("basis") == "community" and abs(rec2.get("clearance_mm", -1) - 0.40) < 1e-9
      and abs(rec2.get("hole_mm", -1) - 5.40) < 1e-9 and rec2.get("n") == 3,
      f"recommend: khong verified -> trung vi cong dong (0.40 / 5.40, n=3): {rec2}")
rec3 = fl.recommend(lib, "screw-M3")
check(rec3 and rec3.get("hole_mm") == 3.4 and rec3.get("clearance_mm") is None, f"recommend screw-M3: {rec3}")
check(fl.recommend(lib, "khong-co") is None, "recommend interface khong co -> None")

# 4) Them muc tu ket qua measure_features
feats = {"file": "parts/03.stl", "units": "mm", "features": [
    {"id": 4, "type": "hole", "d_mm": 2.412, "axis": [0, 0, 1], "center": [0, 0, 0], "length_mm": 6,
     "coverage_deg": 360, "rms_mm": 0.004, "confidence": 0.93, "n_faces": 64, "through": True},
    {"id": 5, "type": "boss", "d_mm": 5.071, "axis": [0, 0, 1], "center": [5, 0, 0], "length_mm": 4,
     "coverage_deg": 360, "rms_mm": 0.003, "confidence": 0.95, "n_faces": 64}], "groups": []}
fjs = os.path.join(OUT, "feat.json")
json.dump(feats, open(fjs, "w", encoding="utf-8"))
n0 = len(fl.load(path))
e1 = fl.add_from_features(path, fjs, feature_id=4, entry_id="t/m25", interface="screw-M2.5", fit="self-tap",
                          model="makerworld-x", nominal_mm=2.5)
e2 = fl.add_from_features(path, fjs, feature_id=5, entry_id="t/pin", interface="rotate-joint-5mm", fit="rotate",
                          model="makerworld-x")
lib3 = fl.load(path)
check(len(lib3) == n0 + 2 and fl.validate(lib3) == [], f"them 2 muc, kho van hop le: {fl.validate(lib3)}")
check(e1["hole_mm"] == 2.412 and e1["shaft_mm"] is None and e1["source"]["method"] == "stl-fit"
      and e1["confidence"] == 0.93 and e1["verified"] is False and e1["source"]["model"] == "makerworld-x"
      and "03.stl" in e1["source"].get("parts", ""), f"muc tu lo: {e1}")
check(e2["shaft_mm"] == 5.071 and e2["hole_mm"] is None, f"muc tu boss -> shaft_mm: {e2}")
try:
    fl.add_from_features(path, fjs, feature_id=4, entry_id="t/m25", interface="screw-M2.5", fit="self-tap",
                         model="makerworld-x")
    check(False, "them id trung phai raise ValueError")
except ValueError:
    pass
try:
    fl.add_from_features(path, fjs, feature_id=99, entry_id="t/x", interface="a", fit="rotate", model="m")
    check(False, "feature_id khong co phai raise ValueError")
except ValueError:
    pass
check(len(fl.load(path)) == n0 + 2, "loi thi khong ghi gi")

# 5) CLI
py = sys.executable
r = subprocess.run([py, os.path.join(LIB, "fit_lib.py"), "check"], capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 0, f"CLI check kho that: {r.stdout[-300:]} {r.stderr[-300:]}")
r = subprocess.run([py, os.path.join(LIB, "fit_lib.py"), "recommend", "rotate-joint-5mm", "--file", path],
                   capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 0 and json.loads(r.stdout).get("basis") == "verified", f"CLI recommend: {r.stdout[-300:]}")
r = subprocess.run([py, os.path.join(LIB, "fit_lib.py"), "lookup", "screw-M3", "--file", path],
                   capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 0 and [e["id"] for e in json.loads(r.stdout)] == ["o/1"], f"CLI lookup: {r.stdout[-300:]}")
r = subprocess.run([py, os.path.join(LIB, "fit_lib.py"), "recommend", "khong-co", "--file", path],
                   capture_output=True, text=True, encoding="utf-8")
check(r.returncode == 1, "CLI recommend khong co -> exit 1")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_fit_lib")
