# Gate "Bao gia v3: keo file bat ky -> tu cat lop -> chon nhua -> gia cuoi" (Claude viet, executor KHONG sua).
# Chay tu thu muc studio (can Bambu Studio + FreeCAD 1.1 tren may):
#   .venv/Scripts/python.exe tests/test_quote_slice.py
import io, json, os, sqlite3, subprocess, sys, tempfile, time, zipfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
ROOT = STUDIO.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
TMP = Path(tempfile.mkdtemp(prefix="stlab-quote-slice-"))
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")
os.environ["STLAB_QUOTES_WORK"] = str(TMP / "work")  # upload + ket qua cat lop (mac dinh %LOCALAPPDATA%\stlab-quotes)

FCPY = Path(r"C:\Program Files\FreeCAD 1.1\bin\python.exe")
QS = ROOT / "tools" / "robotics-cad" / "scripts" / "quote_slice.py"
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def cube_stl(a=20.0):
    v = [(x, y, z) for x in (0, a) for y in (0, a) for z in (0, a)]
    f = [(0, 2, 3), (0, 3, 1), (4, 5, 7), (4, 7, 6), (0, 1, 5), (0, 5, 4),
         (2, 6, 7), (2, 7, 3), (0, 4, 6), (0, 6, 2), (1, 3, 7), (1, 7, 5)]
    s = ["solid cube"]
    for t in f:
        s += ["facet normal 0 0 0", "outer loop"] + [f"vertex {v[i][0]} {v[i][1]} {v[i][2]}" for i in t]
        s += ["endloop", "endfacet"]
    return ("\n".join(s + ["endsolid cube"]) + "\n").encode(), v, f


STL, V, F = cube_stl()
OBJ = ("".join(f"v {x} {y} {z}\n" for x, y, z in V) + "".join(f"f {a+1} {b+1} {c+1}\n" for a, b, c in F)).encode()
(TMP / "cube.stl").write_bytes(STL)
(TMP / "cube.obj").write_bytes(OBJ)
STEP = ROOT / "community/boards-official/models/arduino-modulino-buttons/arduino-modulino-buttons.step"


def run_qs(*args, timeout=300):
    r = subprocess.run([str(FCPY), str(QS), *map(str, args)], capture_output=True, text=True, encoding="utf-8",
                       timeout=timeout)
    line = (r.stdout.strip().splitlines() or ["{}"])[-1]
    try:
        return json.loads(line)
    except ValueError:
        return {"_raw": r.stdout[-500:] + r.stderr[-500:]}


# 0. slice.py import duoc (khong tu chay main khi import)
r = subprocess.run([str(FCPY), "-c", "import sys; sys.argv=['x']; sys.path.insert(0, r'%s'); import slice; "
                    "print(hasattr(slice, 'cat'))" % (ROOT / "tools/robotics-cad/scripts")],
                   capture_output=True, text=True, timeout=60)
check(r.stdout.strip().endswith("True"), f"slice.py phai co guard __main__ (import khong chay main): {r.stderr[-300:]}")

# 1. quote_slice.py (Python FreeCAD)
lst = run_qs("--list-filaments")
names = lst.get("filaments", [])
for n in ("Bambu PETG Basic @BBL A1", "Bambu PLA Basic @BBL A1", "Generic PETG @BBL A1"):
    check(n in names, f"--list-filaments thieu {n}")
check(all("A1M" not in n and "A1 mini" not in n for n in names), "chi profile hop may A1 (khong A1 mini)")
check("0.20mm Standard @BBL A1" in lst.get("processes", []), "--list-filaments tra ca processes cua A1")

res = {}
for tag, f, fil in (("stl_petg", TMP / "cube.stl", "Bambu PETG Basic @BBL A1"),
                    ("stl_pla", TMP / "cube.stl", "Bambu PLA Basic @BBL A1"),
                    ("obj", TMP / "cube.obj", "Bambu PETG Basic @BBL A1")):
    t = time.time()
    res[tag] = r = run_qs(TMP / f"out_{tag}", f"filament={fil}", f)
    check(r.get("status") in ("ok", "warn"), f"{tag}: status {r.get('status')} {r}")
    g = sum((r.get("grams") or {}).values())
    check(1 < g < 15, f"{tag}: khoi 20 mm ~ vai gam, co {g}")
    check((r.get("seconds") or 0) > 60, f"{tag}: thoi gian in > 60 s")
    check(r.get("gcode_3mf") and Path(r["gcode_3mf"]).exists(), f"{tag}: co file .3mf da cat lop")
    check(time.time() - t < 120, f"{tag}: cat lop < 120 s")
check(sum(res["stl_petg"]["grams"].values()) != sum(res["stl_pla"]["grams"].values()),
      "PETG va PLA khac ty trong -> so gam khac nhau (dung profile nhua da chon)")
check(list(res["stl_pla"]["grams"]) == ["PLA"], f"grams theo loai nhua profile: {res['stl_pla'].get('grams')}")
if STEP.exists():
    r = run_qs(TMP / "out_step", "filament=Bambu PETG Basic @BBL A1", STEP)
    check(r.get("status") in ("ok", "warn") and sum((r.get("grams") or {}).values()) > 0,
          f"STEP: doi sang STL bang FreeCAD roi cat lop: {r}")
r = run_qs(TMP / "out_bad", "filament=Bambu PETG Basic @BBL A1", TMP / "khong-co.stl")
check(r.get("status") == "fail" and r.get("errors"), "file khong ton tai -> status fail + errors")
r = run_qs(TMP / "out_opt", "filament=Bambu PETG Basic @BBL A1", "process=0.28mm Extra Draft @BBL A1",
           "infill=50", "support=off", TMP / "cube.stl")
check(r.get("status") in ("ok", "warn") and sum(r["grams"].values()) > sum(res["stl_petg"]["grams"].values()),
      "infill 50 % ton nhua hon 15 % mac dinh")

from toolhub import create_app, quote  # noqa: E402

# 2. Bang gia: nhua gan profile cat lop; DB cu duoc nang cap
old = TMP / "old.db"
c = sqlite3.connect(old)
c.execute("CREATE TABLE materials(name TEXT PRIMARY KEY, spool_price_vnd REAL, spool_weight_g REAL, updated_at TEXT)")
c.execute("INSERT INTO materials VALUES('PETG_Non_Bambu', 100000, 1000, '')")
c.commit()
c.close()
os.environ["STLAB_QUOTES_DB"] = str(old)
conn = quote.connect()
m = quote.get_pricing(conn)["materials"]
check(m["PETG_Non_Bambu"]["spool_price_vnd"] == 100000, "giu nhua Tuan tu them khi nang cap DB")
check(m["PETG_Non_Bambu"].get("type") == "PETG", f"suy loai tu ten: {m['PETG_Non_Bambu']}")
check(m["PETG_Non_Bambu"].get("slicer_profile") == "Generic PETG @BBL A1",
      f"nhua tu them chua co profile -> Generic <loai> @BBL A1: {m['PETG_Non_Bambu']}")
check(m["PETG"].get("slicer_profile") == "Bambu PETG Basic @BBL A1", "nhua mac dinh PETG -> profile Bambu PETG Basic")
quote.save_material(conn, "PETG_Non_Bambu", spool_price_vnd=100000, spool_weight_g=1000,
                    slicer_profile="KINGROON-Basic PETG Basic @Bambu Lab A1 0.4 nozzle")
check(quote.get_pricing(conn)["materials"]["PETG_Non_Bambu"]["slicer_profile"].startswith("KINGROON"),
      "doi profile cat lop cho nhua")
conn.close()
os.environ["STLAB_QUOTES_DB"] = str(TMP / "quotes.db")

# 3. Web: keo file -> chon nhua -> gia cuoi
H = {"Host": "127.0.0.1:5050"}
HP = {**H, "X-Studio": "1"}
cl = create_app().test_client()
html = cl.get("/quote", headers=H).get_data(as_text=True)
for need in ('id="material"', 'id="final-price"', 'id="print-options"', ".stl", ".step", ".obj", "multiple"):
    check(need in html, f"/quote thieu {need}")

r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(STL), "cube.stl")}, headers=HP,
            content_type="multipart/form-data")
u = r.get_json() or {}
check(r.status_code == 200 and u.get("token") and u.get("kind") == "model", f"upload stl: {r.status_code} {u}")
t = time.time()
r = cl.post("/api/quote/price", json={"token": u.get("token"), "material": "PETG", "quantity": 1}, headers=HP)
p1 = r.get_json() or {}
check(r.status_code == 200 and p1.get("total", 0) > 0 and p1.get("total_text", "").endswith("đ"), f"price: {p1}")
check(p1.get("grams") and p1.get("hours", 0) > 0, "price tra gam + gio tu lan cat lop")
check(p1.get("plates") and str(p1["plates"][0].get("image", "")).startswith("data:image/png"), "anh ban in sau cat lop")
t1 = time.time() - t
t = time.time()
r = cl.post("/api/quote/price", json={"token": u.get("token"), "material": "PETG", "quantity": 3}, headers=HP)
check(time.time() - t < 1.0, f"cung file + nhua + tuy chon -> dung ket qua cat lop da luu (lan dau {t1:.1f} s)")
check(r.get_json()["total"] > p1["total"], "so luong 3 dat hon 1")
r = cl.post("/api/quote/price", json={"token": u.get("token"), "material": "PLA", "quantity": 1}, headers=HP)
p2 = r.get_json() or {}
check(r.status_code == 200 and p2.get("grams") != p1.get("grams"), "doi nhua -> cat lai theo profile nhua moi")
r = cl.post("/api/quote/price", json={"token": u.get("token"), "material": "PETG", "quantity": 1,
                                      "options": {"infill": 50, "support": "off",
                                                  "process": "0.28mm Extra Draft @BBL A1"}}, headers=HP)
check(r.status_code == 200 and r.get_json()["total"] > p1["total"], "tuy chon in (infill 50) doi gia")
r = cl.post("/api/quote/price", json={"token": u.get("token"), "material": "ABS-khong-co", "quantity": 1},
            headers=HP)
check(r.status_code == 400 and "error" in (r.get_json() or {}), "nhua khong co trong bang gia -> 400")

# file da cat lop: doc thang, khong cat lai
b = io.BytesIO()
with zipfile.ZipFile(b, "w") as z:
    z.writestr("Metadata/slice_info.config", '<?xml version="1.0"?><config><plate><metadata key="index" value="1"/>'
               '<metadata key="prediction" value="3600"/><filament id="1" type="PETG" used_g="100"/></plate></config>')
r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(b.getvalue()), "a.gcode.3mf")}, headers=HP,
            content_type="multipart/form-data")
s = r.get_json() or {}
check(s.get("kind") == "sliced", f"gcode.3mf -> kind sliced: {s}")
t = time.time()
r = cl.post("/api/quote/price", json={"token": s.get("token"), "material": "PETG", "quantity": 1}, headers=HP)
check(r.status_code == 200 and time.time() - t < 1.0, "file da cat lop: tinh ngay, khong goi slicer")
check(abs(r.get_json()["grams"]["PETG"] - 100) < 0.01, "file da cat lop: gam lay tu file")

r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(b"hello"), "a.txt")}, headers=HP,
            content_type="multipart/form-data")
check(r.status_code == 400, "duoi file khong ho tro -> 400")
r = cl.post("/api/quote/upload", data={"file": (io.BytesIO(STL), "a.stl")}, headers=H,
            content_type="multipart/form-data")
check(r.status_code == 403, "upload khong X-Studio -> 403")

r = cl.post("/api/quote/save", json={"token": u.get("token"), "material": "PETG", "quantity": 2,
                                     "customer_name": "Khách Thử", "customer_phone": "", "title": "Khối 20 mm",
                                     "note": ""}, headers=HP)
sid = (r.get_json() or {}).get("id")
check(r.status_code == 200 and sid, f"luu bao gia tu file model: {r.get_json()}")
t = cl.get(f"/quote/{sid}", headers=H).get_data(as_text=True)
check("Khối 20 mm" in t and "PETG" in t, "phieu khach: tieu de + nhua")
prof = cl.get("/api/quote/slicer-profiles", headers=H).get_json() or {}
check("Bambu PETG Basic @BBL A1" in prof.get("filaments", []), "API danh sach profile cat lop (cho o chon trong bang gia)")
check(str(TMP) in str(quote.work_dir()), "thu muc upload/cat lop theo STLAB_QUOTES_WORK (ngoai repo)")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_quote_slice")
