# Gate: project 3MF gop nhieu plate (Tuan 2026-11-26 "ban in gom lai 1 file, nhieu plates").
# Chay: python tools/print/tests/test_multi_plate.py [--run]   (--run: cat lai that 2 print.yaml cua english-teacher qua memjob)
# Kiem: file gop <plates_dir>/<yaml-stem>.3mf ton tai, so plate = so ban, moi plate dung so object + dung mau yaml,
# object plate i dung filament slot i, toa do object nam trong o plate i, khong doi ket qua cat tung ban.
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

WS = Path(__file__).resolve().parents[3]
PY = sys.executable
YAMLS = ["maker/english-teacher/print/print-s3-screen.yaml", "maker/english-teacher/print/print-s3-test.yaml"]
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg, flush=True)
    if not cond:
        fails.append(msg)


def check(yml):
    import yaml
    y = WS / yml
    cfg = yaml.safe_load(y.read_text(encoding="utf-8"))
    plates_dir = (y.parent / cfg.get("data_dir", ".") / cfg["plates_dir"]).resolve()
    rep = json.loads((plates_dir / "print-report.json").read_text(encoding="utf-8"))
    merged = plates_dir / f"{y.stem}.3mf"
    ok(merged.exists(), f"{y.stem}: file gop ton tai")
    if not merged.exists():
        return
    bans = [b for b in rep["ban"] if (plates_dir / b["ban"]).exists() and list((plates_dir / b["ban"]).glob("*.3mf"))]
    z = zipfile.ZipFile(merged)
    ms = z.read("Metadata/model_settings.config").decode("utf-8")
    plates = re.findall(r"<plate>.*?</plate>", ms, re.S)
    ok(len(plates) == len(bans) == rep["project_gop"]["so_plate"], f"{y.stem}: {len(plates)} plate = {len(bans)} ban")
    ps = json.loads(z.read("Metadata/project_settings.config"))
    ok(len(ps["filament_colour"]) == len(bans), f"{y.stem}: {len(bans)} filament slot")
    obj_ext = {m.group(1): int(m.group(3)) for m in re.finditer(
        r'<object id="(\d+)">(.*?)<metadata key="extruder" value="(\d+)"', ms, re.S)}
    model = z.read("3D/3dmodel.model").decode("utf-8")
    items = {m.group(1): [float(t) for t in m.group(2).split()] for m in re.finditer(
        r'<item objectid="(\d+)"[^>]*transform="([^"]+)"', model)}
    for i, (pl, b) in enumerate(zip(plates, bans), 1):
        ids = re.findall(r'key="object_id" value="(\d+)"', pl)
        ok(len(ids) == b["so_chi_tiet"], f"{y.stem} plate {i} ({b['ban']}): {len(ids)} object = {b['so_chi_tiet']}")
        if b.get("mau"):
            ok(ps["filament_colour"][i - 1].upper() == b["mau"].upper(), f"{y.stem} plate {i}: mau {b['mau']}")
        ok(all(obj_ext[o] == i for o in ids), f"{y.stem} plate {i}: object dung filament slot {i}")
        ncol = max(1, int(len(bans) ** 0.5 + 0.999))
        x0 = ((i - 1) % ncol) * 256 * 1.2
        okx = all(x0 - 1 <= items[o][9] <= x0 + 257 for o in ids)
        ok(okx, f"{y.stem} plate {i}: toa do nam trong o plate")
        ok(f'value="{b["ban"]}"' in pl, f"{y.stem} plate {i}: ten plate = ten ban")
    for b in bans:
        ok(next((plates_dir / b["ban"]).glob("*.3mf")).exists(), f"{y.stem}: file ban {b['ban']} con nguyen")
    # 2026-11-26 loi that (Tuan: "5 plates nhung cung 1 mau"): Bambu Studio tra luoi theo objectid component ->
    # objectid component phai DUY NHAT va khop <object id> trong dung file con; moi plate phai co luoi rieng.
    mdl = z.read("3D/3dmodel.model").decode("utf-8")
    comps = re.findall(r'<component p:path="([^"]+)" objectid="(\d+)"', mdl)
    ids = [c[1] for c in comps]
    ok(len(ids) == len(set(ids)), f"{y.stem}: objectid component trung {sorted(ids)}")
    for p, oid in comps:
        ok(f'<object id="{oid}"' in z.read(p.lstrip("/")).decode("utf-8"), f"{y.stem}: {p} khong co object id {oid}")
    if len(bans) > 1:
        pngs = [z.read(f"Metadata/plate_{i}_small.png") for i in range(1, len(bans) + 1) if f"Metadata/plate_{i}_small.png" in z.namelist()]
        ok(len(set(pngs)) == len(pngs), f"{y.stem}: anh plate giong nhau (cung 1 mau?)")


if "--run" in sys.argv:
    for yml in YAMLS:
        r = subprocess.run([PY, "tools/print/scripts/memjob.py", "3", "--", PY, "tools/print/scripts/slice.py", yml],
                           cwd=WS, capture_output=True, text=True, errors="replace")
        ok(r.returncode in (0,) or "KET LUAN" in r.stdout, f"cat lop {yml} (exit {r.returncode})")
for yml in YAMLS:
    check(yml)
print("FAIL" if fails else "ALL PASS")
sys.exit(1 if fails else 0)
