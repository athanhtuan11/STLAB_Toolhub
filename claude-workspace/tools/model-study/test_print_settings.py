# Gate: study_3mf.py doc cau hinh in theo object cua tac gia (Claude viet, executor KHONG sua).
#   python test_print_settings.py      (chay tu tools/model-study)
import csv, json, os, shutil, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "study_3mf.py")
raw = open(SRC, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf"), "study_3mf.py phai UTF-8 KHONG BOM"
raw.decode("utf-8")
OUT = os.path.join(HERE, "_out", "print-settings")
shutil.rmtree(OUT, ignore_errors=True)
r = subprocess.run([sys.executable, SRC, os.path.join(HERE, "_sample", "arm.3mf"), OUT], capture_output=True, text=True)
print(r.stdout[-800:], r.stderr[-800:])
assert r.returncode == 0
rows = list(csv.DictReader(open(os.path.join(OUT, "parts.csv"), encoding="utf-8")))
assert len(rows) == 33 and {"support", "support_type", "print_settings"} <= set(rows[0]), rows[0].keys()

# Dap an doc doc lap tu model_settings.config: object nao bat support
import xml.etree.ElementTree as ET
cfg = ET.fromstring(zipfile.ZipFile(os.path.join(HERE, "_sample", "arm.3mf")).read("Metadata/model_settings.config"))
want = {}
for o in cfg.findall("object"):
    md = {m.get("key"): m.get("value") for m in o.findall("metadata") if m.get("key")}
    want.setdefault(md.get("name"), set()).add(md.get("enable_support", ""))
for row in rows:
    assert row["support"] in ("0", "1", ""), row["support"]
    assert row["support"] in want.get(row["name"], {row["support"]}), f"{row['name']}: support {row['support']} != {want.get(row['name'])}"
    ps = json.loads(row["print_settings"] or "{}")
    assert isinstance(ps, dict) and "name" not in ps
    if row["support"] == "1":
        assert row["support_type"], f"{row['name']} bat support nhung thieu support_type"
assert any(x["support"] == "1" for x in rows), "mau co it nhat 1 chi tiet tac gia bat support"
assert "support" in open(os.path.join(OUT, "summary.md"), encoding="utf-8").read().lower(), "summary.md phai liet ke chi tiet bat support"
shutil.rmtree(OUT, ignore_errors=True)
print("gate OK")
