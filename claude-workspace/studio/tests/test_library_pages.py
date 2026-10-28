# Gate "Linh kien: danh sach gon + trang chi tiet" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_library_pages.py
import re, sys
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
import yaml  # noqa: E402
from toolhub import create_app  # noqa: E402

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


LIB = STUDIO.parent / "tools" / "robotics-cad" / "library" / "components.yaml"
comps = yaml.safe_load(LIB.read_text(encoding="utf-8"))["components"]
ids = [c["id"] for c in comps]
RID = "relay-module-2ch-srd-05vdc"
H = {"Host": "127.0.0.1:5050"}
c = create_app().test_client()

# 1. Danh sach gon
r = c.get("/library", headers=H)
check(r.status_code == 200, f"/library status {r.status_code}")
html = r.get_data(as_text=True)
for i in ids:
    check(f'href="/library/{i}"' in html, f"the {i} thieu link toi /library/{i}")
check(html.count('class="card') >= len(ids), "moi linh kien 1 the")
check("S1/S2" not in html and "COM1?" not in html,
      "danh sach KHONG ve so do chan/so do dau (chi o trang chi tiet)")
check("ESP32 GPIO26" not in html, "so do dau pump-control khong duoc o danh sach")
check("TODO: " not in html, "danh sach chi hien so luong TODO, khong liet ke tung TODO")
check(re.search(r"\d+\s*TODO", html) is not None, "the phai hien so luong TODO (vd '4 TODO')")
check("Sơ đồ chân" in html, "the relay phai co nhan 'Sơ đồ chân' (bao co so do)")
check("/library/img/images/relay-module-2ch-srd-05vdc.png" in html, "the co anh_chan phai co anh nho (thumbnail)")
check("Module relay 2 kênh" in html and "Servo SG90" in html, "the phai co ten linh kien")
check('data-type="relay"' in html, "giu bo loc theo loai (data-type)")
check('id="q"' in html, "co o tim kiem id=q (loc theo ten, JS thuan)")
check(len(html) < 200_000, f"danh sach phai nhe (<200 KB), hien {len(html)//1000} KB")

# 2. Trang chi tiet
d = c.get(f"/library/{RID}", headers=H)
check(d.status_code == 200, f"/library/{RID} status {d.status_code}")
dh = d.get_data(as_text=True)
for s in ("Module relay 2 kênh", "Tiếp điểm", "TODO: ", "Sơ đồ chân", "ESP32 GPIO26",
          "/library/img/images/relay-module-2ch-srd-05vdc.png", 'href="/library"'):
    check(s in dh, f"trang chi tiet thieu: {s}")
s = c.get("/library/sg90", headers=H)
check(s.status_code == 200 and "Servo SG90" in s.get_data(as_text=True), "chi tiet sg90 loi")
check("towerpro.com.tw" in s.get_data(as_text=True), "chi tiet phai co link nguon")
check(c.get("/library/khong-co-linh-kien-nay", headers=H).status_code == 404, "id khong ton tai -> 404")
check(c.get("/library/img/images/relay-module-2ch-srd-05vdc.png", headers=H).status_code == 200, "route anh van chay")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_library_pages")
