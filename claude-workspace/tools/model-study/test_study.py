# Gate cho study_3mf.py – Claude viet, executor KHONG sua file nay.
#   python test_study.py
import csv, os, shutil, struct, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "_out", "arm")
shutil.rmtree(OUT, ignore_errors=True)
r = subprocess.run([sys.executable, os.path.join(HERE, "study_3mf.py"), os.path.join(HERE, "_sample", "arm.3mf"), OUT],
                   capture_output=True, text=True)
print(r.stdout[-1500:], r.stderr[-1500:])
assert r.returncode == 0, "study_3mf.py exit != 0"

rows = list(csv.DictReader(open(os.path.join(OUT, "parts.csv"), encoding="utf-8")))
need = {"idx", "name", "plate", "file", "triangles", "size_x", "size_y", "size_z", "volume_mm3", "watertight"}
assert need <= set(rows[0]), f"parts.csv thieu cot: {need - set(rows[0])}"
assert len(rows) == 33, f"can 33 chi tiet (33 build item), co {len(rows)}"
assert {r["plate"] for r in rows} == {"1", "2", "3"}, "plate phai la 1/2/3 theo Metadata/model_settings.config"
for row in rows:
    p = os.path.join(OUT, row["file"])
    assert os.path.exists(p), p
    data = open(p, "rb").read()
    n = struct.unpack("<I", data[80:84])[0]
    assert len(data) == 84 + 50 * n and n == int(row["triangles"]) and n > 0, f"STL nhi phan sai: {p}"
    sx, sy, sz = (float(row[k]) for k in ("size_x", "size_y", "size_z"))
    assert 0.5 < sx < 260 and 0.5 < sy < 260 and 0.5 < sz < 260, f"kich thuoc bat thuong {row['name']}: {sx} {sy} {sz}"
    assert float(row["volume_mm3"]) > 0, f"the tich <= 0: {row['name']}"
    # dat tren ban in: z min ~ 0 (theo huong in trong 3MF)
    assert abs(float(row["z_min"])) < 0.6, f"chi tiet khong nam tren ban: {row['name']} z_min={row['z_min']}"

for f in ("contact-sheet.png", "summary.md"):
    p = os.path.join(OUT, f)
    assert os.path.exists(p) and os.path.getsize(p) > 2000, f"thieu {f}"
print("gate OK", len(rows), "parts")
