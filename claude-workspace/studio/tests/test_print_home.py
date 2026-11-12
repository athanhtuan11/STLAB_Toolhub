# Gate "Trang chinh = In 3D" (Claude viet 2026-11-12, executor KHONG sua). Tuan: "qua kho de tim file CAD de in; giao dien
# qua nhieu topic nhung khong huu dung" -> chon phuong an: trang chinh chi con o tim + luoi the BAN IN (anh, gio, gam,
# nut In / CAD / Thu muc), menu 4 muc: In 3D · Du an · Bao gia · Them. Muc cu (ung dung, mo phong, nhan su AI) -> /tools.
# Chay tu thu muc studio: .venv/Scripts/python.exe tests/test_print_home.py   (dung ban in that da cat trong maker/)
import os, re, sys
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
ROOT = STUDIO.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
os.environ["STLAB_DRY_OPEN"] = "1"          # mo file: khong chay ung dung that, tra duong dan se mo
H = {"X-Studio": "1"}
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


from toolhub import create_app  # noqa: E402

app = create_app()
c = app.test_client()
B = "http://127.0.0.1:5050"

# 1. API danh sach ban in: moi thu muc plates/<ban>/<ban>.3mf trong maker/*/ (bo _profile, _log)
r = c.get("/api/prints", base_url=B)
pj = r.get_json() or {}
items = pj.get("prints") or []
ok(r.status_code == 200 and len(items) >= 5, f"/api/prints tra >= 5 ban in ({len(items)})")
need = {"project", "plate", "minutes", "grams", "image_url", "mtime", "cad", "title", "source", "folder"}
ok(all(need <= set(x) for x in items), "moi ban in co project, plate, minutes, grams, image_url, mtime, cad")
ok(all(not x["plate"].startswith("_") for x in items), "bo thu muc _profile/_log")
ok([x["mtime"] for x in items] == sorted((x["mtime"] for x in items), reverse=True), "moi nhat truoc")
sh = next((x for x in items if x["project"] == "servo-horn-sg90" and x["plate"] == "p1-servo-horns"), None)
ok(sh is not None, "co ban p1-servo-horns cua servo-horn-sg90")
if sh:
    ok(13 <= (sh["minutes"] or 0) <= 15 and abs((sh["grams"] or 0) - 1.5) < 0.1, f"servo-horn: ~14 ph, ~1,5 g ({sh['minutes']}, {sh['grams']})")
    ok(any(Path(x).suffix.lower() == ".sc" for x in sh["cad"]) or any(str(x).endswith(".sc") for x in sh["cad"]), f"servo-horn: co file CAD .sc ({sh['cad']})")
    ok("sg90" in sh["title"].lower() and "cyberbrick" in sh["title"].lower(),
       f"title = tieu de README (tim 'SG90'/'CyberBrick' ra arm servo) ({sh['title']})")
    im = c.get(sh["image_url"], base_url=B)
    ok(im.status_code == 200 and im.data[:4] == b"\x89PNG", "anh xem truoc ban in")
esp = next((x for x in items if x["project"] == "esp32-s3-cam" and x["plate"] == "p2-enclosure"), None)
ok(esp is not None and esp["minutes"] and esp["minutes"] > 150, f"esp32-s3-cam p2-enclosure co thoi gian ({esp and esp['minutes']})")

# 2. Mo file: chi nhan (project, plate, what) - khong nhan duong dan tu web; POST can X-Studio
if sh:
    for what, ext in (("3mf", ".3mf"), ("cad", ".sc"), ("folder", "")):
        o = c.post("/api/prints/open", json={"project": "servo-horn-sg90", "plate": "p1-servo-horns", "what": what}, headers=H, base_url=B)
        oj = o.get_json() or {}
        ok(o.status_code == 200 and oj.get("ok") and oj.get("dry") and str(oj.get("path", "")).lower().endswith(ext)
           and "servo-horn-sg90" in str(oj.get("path", "")), f"mo {what} -> {oj.get('path')}")
    o = c.post("/api/prints/open", json={"project": "servo-horn-sg90", "plate": "p1-servo-horns", "what": "3mf"}, base_url=B)
    ok(o.status_code == 403, "POST thieu X-Studio -> 403")
bad = c.post("/api/prints/open", json={"project": "../../Windows", "plate": "x", "what": "folder"}, headers=H, base_url=B)
ok(bad.status_code in (400, 404), "project la -> 400/404 (khong mo duong dan tuy y)")

# 3. Trang chinh = In 3D
home = c.get("/", base_url=B).get_data(as_text=True)
ok("In 3D" in home and re.search(r'<input[^>]+(type="search"|id="print-search")', home), "trang chinh: tieu de In 3D + o tim")
ok("/api/prints" in home, "trang chinh nap danh sach ban in tu /api/prints")
for gone in ("Nhân sự AI", "data-sim-shortcut=", "Mô phỏng robotics"):
    ok(gone not in home, f"trang chinh khong con '{gone}'")
nav = re.search(r"<nav[^>]*>(.*?)</nav>", home, re.S)
navh = nav.group(1) if nav else ""
top = re.sub(r"<details.*?</details>|<div[^>]*class=\"[^\"]*(dropdown|menu-more)[^\"]*\".*?</div>", "", navh, flags=re.S)
labels = [re.sub(r"<[^>]+>", "", m).strip() for m in re.findall(r"<a[^>]*>(.*?)</a>", top, re.S)]
labels = [x for x in labels if x and x not in ("STLAB", "Toolhub", "STLAB Toolhub")]
ok(labels[:3] == ["In 3D", "Dự án", "Báo giá"] and len(labels) == 3, f"menu chinh chi: In 3D · Dự án · Báo giá (+ Thêm) ({labels})")
ok("Thêm" in navh and all(f'href="{u}"' in home for u in ("/tools", "/robotics", "/quote")),
   "menu Thêm con lien ket: Cong cu, Robotics")
# Tuan 2026-11-12: "Nghien cuu khong can vi co README roi, bo phan nay tren giao dien" -> bo khoi menu (route cu van giu)
ok("Nghiên cứu" not in navh and 'href="/research"' not in navh and 'href="/reports"' not in navh, "menu khong con muc Nghien cuu / Bao cao nghien cuu")

# 4. Trang Cong cu /tools giu cac muc cu
t = c.get("/tools", base_url=B)
th = t.get_data(as_text=True)
ok(t.status_code == 200 and "Nhân sự AI" in th and "data-sim-shortcut=" in th and "FreeCAD" in th, "/tools: ung dung + mo phong + nhan su AI")

# 5. Phu kien in cua LINH KIEN (Tuan 2026-11-12: "trong library, tung linh kien se co ban CAD de in neu co custom") -
#    components.yaml truong in_3d -> tools/parts-library/printables/<ten>/; trang /library/<id> hien ban in + CAD dau trang.
if sh:
    ok(sh.get("source") == "linh-kien" and "parts-library/printables/servo-horn-sg90" in sh.get("folder", "").replace("\\", "/"),
       f"servo-horn la phu kien linh kien (source=linh-kien, folder printables) ({sh.get('source')}, {sh.get('folder')})")
for cid in ("sg90", "cb-pg001-servo-9g"):
    d = c.get(f"/library/{cid}", base_url=B).get_data(as_text=True)
    ok("p1-servo-horns" in d and "servo-horn.sc" in d and ("In 3D" in d or "CAD để in" in d), f"/library/{cid}: khoi CAD de in co ban p1-servo-horns + servo-horn.sc")
lib = c.get("/library", base_url=B).get_data(as_text=True)
ok("data-printables=" in lib, "trang /library danh dau linh kien co phu kien in (data-printables)")
d = c.get("/projects/maker--esp32-s3-cam", base_url=B).get_data(as_text=True)
i_print, i_note = d.find("p2-enclosure"), d.find("Mục tiêu")
ok(i_print != -1 and (i_note == -1 or i_print < i_note), "trang du an: ban in truoc ghi chu")
ok(i_note == -1 or re.search(r"<details[^>]*>.*?Mục tiêu", d, re.S) is not None, "ghi chu ky thuat (CLAUDE.md) nam trong <details> gap lai")

# 6. Khong ma hex trong template moi
for name in ("prints.html", "tools.html"):
    p = STUDIO / "toolhub" / "templates" / name
    ok(p.exists() and not re.search(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"&#\d+;", "", p.read_text(encoding="utf-8"))), f"{name} co, khong dat ma hex")

print(("GATE FAIL (%d)" % len(fails)) if fails else "GATE PASS")
sys.exit(1 if fails else 0)
