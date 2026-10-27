# Gate cho measure_step.py (Claude viet, executor KHONG sua file nay).
#   python test_step.py      (chay tu tools/model-study)
import csv, os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FC = "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe"
FIX = os.path.join(HERE, "_out", "step-fixture")
OUT = os.path.join(HERE, "_out", "step-measure")
for d in (FIX, OUT):
    shutil.rmtree(d, ignore_errors=True)
subprocess.run([FC, os.path.join(HERE, "make_step_fixture.py"), FIX], check=True, capture_output=True)
step = os.path.join(FIX, "fixture.step")
assert os.path.exists(step), "make_step_fixture.py khong tao duoc fixture.step"

r = subprocess.run([FC, os.path.join(HERE, "measure_step.py"), step, OUT], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print(r.stdout[-1500:], r.stderr[-800:])
csv_path = os.path.join(OUT, "step_features.csv")
assert os.path.exists(csv_path), "thieu step_features.csv"
rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
need = {"idx", "part", "kind", "diameter", "axis", "cx", "cy", "cz", "length", "sweep_deg", "faces"}
assert rows and need <= set(rows[0]), f"thieu cot: {need - set(rows[0] if rows else {})}"


def find(kind, axis, d, tol=0.001):
    return [x for x in rows if x["kind"] == kind and x["axis"] == axis and abs(float(x["diameter"]) - d) <= tol]


holes_z = find("hole", "z", 3.2)
assert len(holes_z) == 2, f"phai co DUNG 2 lo D3.200 truc z (gop nua mat cung truc, tach khac tam), co {len(holes_z)}"
xs = sorted(round(float(h["cx"]), 2) for h in holes_z)
assert xs == [-12.0, 12.0], f"tam x 2 lo phai -12/12, co {xs}"
for h in holes_z:
    assert abs(float(h["length"]) - 6.0) <= 0.01, f"lo xuyen dai 6, co {h['length']}"
    assert abs(float(h["cz"]) - 3.0) <= 0.01, f"tam lo (giua chieu dai) z=3, co {h['cz']}"
    assert abs(float(h["sweep_deg"]) - 360) <= 0.5, h

blind = find("hole", "y", 5.0)
assert len(blind) == 1 and abs(float(blind[0]["length"]) - 8.0) <= 0.01, f"lo mu D5.000 truc y sau 8: {blind}"
pin = find("pin", "x", 3.0)
assert len(pin) == 1 and abs(float(pin[0]["length"]) - 10.0) <= 0.01, f"chot D3.000 truc x dai 10: {pin}"
assert abs(float(pin[0]["cx"]) - 25.0) <= 0.01, f"tam chot x=25, co {pin[0]['cx']}"
arc = [x for x in rows if x["kind"] == "arc"]
assert len(arc) == 1 and abs(float(arc[0]["diameter"]) - 4.0) <= 0.001 and abs(float(arc[0]["sweep_deg"]) - 90) <= 0.5, \
    f"bo canh R2 phai la 1 'arc' D4 quet 90 do: {arc}"
assert not [x for x in rows if x["kind"] in ("hole", "pin") and abs(float(x["diameter"]) - 4.0) < 0.01], \
    "bo canh bi bao nham la hole/pin"
assert os.path.exists(os.path.join(OUT, "step_features.md")), "thieu step_features.md"
print("gate OK", len(rows), "dac trung")
