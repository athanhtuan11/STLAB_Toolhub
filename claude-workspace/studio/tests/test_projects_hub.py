# Gate "Trang Du an gop /robotics + Huong dan lam + So do dau day WireViz" (Claude viet 2026-11-14, executor KHONG sua).
# Chay tu thu muc studio:  .venv\Scripts\python.exe tests\test_projects_hub.py
# Mockup Tuan duyet: docs/reports/projects-merge/mockup-list.png, mockup-guide.png; de xuat docs/reports/projects-merge.md
import json, os, re, sys, tempfile, time, xml.dom.minidom
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
WS = STUDIO.parent
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(STUDIO))

MANIFEST = json.loads((STUDIO / "toolhub" / "robotics.json").read_text(encoding="utf-8"))
WIRING = WS / "maker" / "english-teacher" / "hardware" / "wiring-s3.yaml"
GUIDE = WS / "maker" / "english-teacher" / "GUIDE.md"
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def valid_xml(s, what):
    try:
        xml.dom.minidom.parseString(s)
        return True
    except Exception as e:  # noqa: BLE001
        fails.append(f"{what}: SVG khong phai XML hop le: {e}")
        return False


from toolhub import create_app, robotics, wiring  # noqa: E402
from toolhub import workspace as ws  # noqa: E402

c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}
COLOR_VN = {"RD": "đỏ", "OG": "cam", "BK": "đen", "YE": "vàng", "GN": "xanh lá", "BU": "xanh dương", "VT": "tím",
            "TQ": "xanh ngọc", "WH": "trắng", "PK": "hồng", "GY": "xám", "BN": "nâu"}

# ---- 1. wiring.load: doc + kiem file so do ----
w = wiring.load(WIRING)
check(w.get("title") == "Cú Bông S3 – sơ đồ đấu dây", "wiring.load: title")
check(set(w.get("groups", {})) == {"nguon", "mic", "ampli", "nut"}, "wiring.load: groups")
check(set(w.get("parts", {})) == {"esp", "mic", "amp", "cap", "spk", "btn"}, "wiring.load: parts")
wires = w.get("wires", [])
check(len(wires) == 17, f"wiring.load: 17 day (co {len(wires)})")
WKEYS = {"from_part", "from_pin", "to_part", "to_pin", "from_label", "to_label", "level", "color", "color_name",
         "group", "group_label", "note"}
for i, x in enumerate(wires):
    miss = WKEYS - set(x)
    check(not miss, f"day {i + 1}: thieu khoa {sorted(miss)}")
    if not miss:
        check(x["color_name"] == COLOR_VN.get(x["color"]), f"day {i + 1}: color_name sai ({x['color']} -> {x['color_name']})")
if len(wires) == 17 and not (WKEYS - set(wires[0])):
    a = wires[0]
    check((a["from_part"], a["from_pin"], a["to_part"], a["to_pin"]) == ("mic", "VDD", "esp", "3V3"), "day 1 = mic.VDD -> esp.3V3")
    check(a["from_label"] == "INMP441 (mic)" and a["to_label"] == "ESP32-S3 N16R8", "day 1: nhan linh kien")
    check(a["group_label"] == "Dây nguồn" and a["note"].startswith("CHỈ 3,3 V"), "day 1: group_label + note")
    lr = wires[2]
    check((lr["from_part"], lr["from_pin"]) == ("mic", "L/R"), "tach 'mic.L/R' theo dau cham DAU TIEN")
    cap = wires[11]
    check((cap["from_part"], cap["from_pin"]) == ("cap", "+ (chân dài)"), "tach 'cap.+ (chân dài)' dung")
    check(wires[16]["note"] == "", "note thieu -> chuoi rong")

TMP = Path(tempfile.mkdtemp(prefix="hub-test-"))
base = WIRING.read_text(encoding="utf-8")
for old, new, why in [
    ("to: esp.GPIO4,", "to: esp.GPIO99,", "chan khong co trong part"),
    ("from: mic.WS,", "from: mix.WS,", "part khong co"),
    ("color: YE, group: mic}", "color: XX, group: mic}", "ma mau la"),
    ("color: GN, group: mic}", "color: GN, group: abc}", "group khong co"),
    ("level: tin-hieu, color: BU", "level: 12v, color: BU", "level la"),
    ("to: esp.GPIO6,", "to: esp,", "thieu dau cham part.pin"),
]:
    check(old in base, f"(gate) chuoi mau khong co trong wiring-s3.yaml: {old}")
    f = TMP / "bad.yaml"
    f.write_text(base.replace(old, new, 1), encoding="utf-8")
    try:
        wiring.load(f)
        check(False, f"wiring.load {why}: phai raise ValueError")
    except ValueError:
        pass

# ---- 2. wiring.svg: WireViz, toan bo + tung nhom ----
t0 = time.time()
svg = wiring.svg(WIRING)
check(isinstance(svg, str) and svg.lstrip().startswith("<svg"), "wiring.svg: phai tra chuoi bat dau <svg (bo <?xml/DOCTYPE)")
if svg and valid_xml(svg, "wiring.svg"):
    for s in ["INMP441", "MAX98357A", "ESP32-S3 N16R8", "GPIO4", "GPIO16", "GPIO1", "L/R", "3V3", "5V"]:
        check(s in svg, f"wiring.svg thieu '{s}'")
t1 = time.time()
svg2 = wiring.svg(WIRING)
check(svg2 == svg and time.time() - t1 < 0.2, "wiring.svg: lan 2 phai lay cache (< 0,2 s)")
mic = wiring.svg(WIRING, group="mic")
if mic and valid_xml(mic, "wiring.svg(group=mic)"):
    check("GPIO4" in mic and "GPIO16" not in mic, "svg nhom mic: co GPIO4, khong co GPIO16 (day ampli)")
check(mic != svg, "svg nhom khac svg toan bo")
try:
    wiring.svg(WIRING, group="khong-co")
    check(False, "wiring.svg group la: phai raise ValueError")
except ValueError:
    pass
src = (STUDIO / "toolhub" / "wiring.py").read_text(encoding="utf-8")
check("wireviz" in src, "wiring.py phai dung WireViz (nhu pin_diagram.py)")
check(re.search(r"^\s*pass\s*$", src, re.M) is None and "NotImplemented" not in src, "wiring.py khong ma gia")

# ---- 3. Du lieu du an ----
groups = MANIFEST["groups"]
d = robotics.data()
rows = {p["rel"]: p for p in d["projects"]}
for p in d["projects"]:
    for k in ("group", "group_label", "works", "works_note", "difficulty", "duration", "guide_url"):
        check(k in p, f"{p['rel']}: thieu khoa {k}")
    check(p.get("group_label") == groups.get(p.get("group")), f"{p['rel']}: group_label sai")
et = rows.get("maker/english-teacher", {})
check(et.get("works") is True and et.get("guide_url") == "/projects/maker--english-teacher/guide",
      "english-teacher: works + guide_url")
check(et.get("cover", "").endswith("/cad/out-s3/owl-front.png"), "english-teacher: cover theo manifest")
cam = rows.get("maker/esp32-s3-cam", {})
check(cam.get("works") is True and cam.get("guide_url") in ("", None), "esp32-s3-cam: works, chua co guide -> guide_url rong")
check(rows.get("maker/line-bot", {}).get("works") is False, "works mac dinh False")

for bad, why in [
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "group": "bay-ba"}]}, "group la"),
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "guide": "../../x.md"}]}, "guide ngoai thu muc du an"),
    ({**MANIFEST, "projects": [{**MANIFEST["projects"][0], "wiring": "../x.yaml"}]}, "wiring ngoai thu muc du an"),
]:
    f = TMP / "bad.json"
    f.write_text(json.dumps(bad, ensure_ascii=False), encoding="utf-8")
    os.environ["STLAB_ROBOTICS_MANIFEST"] = str(f)
    try:
        robotics.data()
        check(False, f"manifest {why}: phai raise ValueError")
    except ValueError:
        pass
os.environ.pop("STLAB_ROBOTICS_MANIFEST", None)

# ---- 4. Trang /projects gop ----
r = c.get("/projects", headers=H)
check(r.status_code == 200, f"/projects -> {r.status_code}")
html = r.get_data(as_text=True)
nav = html[html.find("<nav"):html.find("</nav>")]
check('href="/robotics"' not in nav, "menu khong con Robotics (da gop vao Du an)")
check(re.search(r'href="/projects"[^>]*class="on"|class="on"[^>]*href="/projects"', nav) is not None, "muc Du an sang (on)")
all_slugs = {p["slug"]: p for p in ws.projects()}
for p in MANIFEST["projects"]:
    all_slugs.setdefault(p["rel"].replace("/", "--"), p)
main_grid = html
for slug in all_slugs:
    n = main_grid.count(f'data-project="{slug}"')
    check(n == 1, f"the du an {slug}: data-project phai dung 1 lan (co {n})")
want_group = {p["rel"].replace("/", "--"): p["group"] for p in MANIFEST["projects"]}
for slug in all_slugs:
    g = want_group.get(slug) or ("khac" if slug.startswith("maker--") else "tools")
    check(re.search(rf'data-project="{re.escape(slug)}"[^>]*data-group="{g}"|data-group="{g}"[^>]*data-project="{re.escape(slug)}"',
                    html) is not None, f"{slug}: data-group phai = {g}")
used = set(want_group.values()) | {"tools"}
check('data-filter="all"' in html, "chip Tat ca data-filter=all")
for g in used:
    check(f'data-filter="{g}"' in html and groups[g] in html, f"chip nhom {g} ({groups[g]})")
works = [p for p in MANIFEST["projects"] if p.get("works")]
check(html.count("data-works=") == len(works), f"muc Chay duoc: {len(works)} the data-works")
check('href="/projects/maker--english-teacher/guide"' in html, "the Cu Bong co nut Huong dan lam")
check("Chạy được" in html, "co muc 'Chạy được'")
check("Mẫu in" in html, "giu khu 'Mẫu in' (san pham theo doi)")
check(html.count("data-sim=") == 2, "giu 2 the mo phong data-sim")
check('data-post="/api/open/maker--english-teacher"' in html, "dong dev: nut mo VS Code")
check('href="/projects/maker--english-teacher"' in html, "dong dev: link CLAUDE.md (trang chi tiet)")
for p in MANIFEST["projects"]:
    check(p["summary"].replace("&", "&amp;") in html or p["summary"] in html, f"thieu mo ta {p['rel']}")
check(html.count('loading="lazy"') >= 8, "anh bia loading=lazy")
r = c.get("/projects?nhom=robotics", headers=H)
check(r.status_code == 200 and 'data-active-filter="robotics"' in r.get_data(as_text=True), "?nhom=robotics -> chon san chip")
r = c.get("/projects?nhom=<script>", headers=H)
check(r.status_code == 200 and "<script>" not in r.get_data(as_text=True).split("</nav>", 1)[-1].split("<script", 1)[0]
      and 'data-active-filter="all"' in r.get_data(as_text=True), "?nhom la -> all, khong phan chieu")

# ---- 5. /robotics chuyen huong ----
r = c.get("/robotics", headers=H)
check(r.status_code in (301, 302, 308) and r.headers.get("Location", "").endswith("/projects?nhom=robotics"),
      f"/robotics -> chuyen huong /projects?nhom=robotics ({r.status_code} {r.headers.get('Location')})")
check(c.get("/robotics/sim/gearsbot/readme", headers=H).status_code == 200, "route /robotics/sim/... giu nguyen")

# ---- 6. Trang huong dan ----
check(GUIDE.is_file() and "<!-- wiring -->" in GUIDE.read_text(encoding="utf-8"), "(du lieu) GUIDE.md co dong <!-- wiring -->")
r = c.get("/projects/maker--english-teacher/guide", headers=H)
check(r.status_code == 200, f"guide -> {r.status_code}")
g = r.get_data(as_text=True)
check("<h1" in g and "Cú Bông" in g, "guide: h1 tieu de")
toc = re.search(r'data-toc[^>]*>(.*?)</(nav|div|ol|ul)>', g, re.S)
check(toc is not None, "guide: muc luc data-toc")
heads = re.findall(r'<h2[^>]*id="([^"]+)"', g)
check(len(heads) == 7, f"guide: 7 buoc h2 co id (co {len(heads)})")
if toc:
    for h in heads:
        check(f'href="#{h}"' in toc.group(1), f"muc luc thieu #{h}")
check(g.count("data-step-done") == len(heads), "moi buoc 1 o 'Em lam xong' data-step-done")
check(re.search(r'class="[^"]*guide-safe[^"]*"', g) is not None, "buoc An toan co khung guide-safe")
check(g.find("guide-safe") < g.find("data-wiring") if "data-wiring" in g else False, "An toan dung TRUOC so do")
check("<!-- wiring -->" not in g, "dong <!-- wiring --> phai duoc thay")
blk = g[g.find("data-wiring"):]
check("<svg" in blk, "khoi so do co SVG")
check('data-wire-group="all"' in blk and all(f'data-wire-group="{k}"' in blk for k in ("nguon", "mic", "ampli", "nut")),
      "nut loc: all + 4 nhom")
check(all(f'data-wire-svg="{k}"' in blk for k in ("mic", "ampli", "nguon", "nut")), "SVG tung nhom data-wire-svg")
check(blk.count("data-wire=") == 17, f"bang day: 17 dong data-wire (co {blk.count('data-wire=')})")
check(blk.count('type="checkbox"') >= 17, "moi dong day co o tich")
for s in ["cam", "đỏ", "xám", "CHỈ 3,3 V", "KHÔNG nối GND", "GPIO16", "Dây nguồn"]:
    check(s in blk, f"bang day thieu '{s}'")
check("Có hàn" in g and "thử thật trên mạch 2026-11-12" in g, "guide: the thong tin nhanh (do kho, works_note)")
check(c.get("/projects/maker--esp32-s3-cam/guide", headers=H).status_code == 404, "khong guide -> 404")
check(c.get("/projects/maker--khong-co/guide", headers=H).status_code == 404, "slug la -> 404")
check(c.get("/projects/maker--english-teacher/guide", headers={"Host": "evil.com"}).status_code == 403, "Host la -> 403")

# ---- 7. JS/CSS ----
static = STUDIO / "toolhub" / "static"
js = "".join(p.read_text(encoding="utf-8") for p in static.glob("*.js"))
check("localStorage" in js, "luu o tich bang localStorage")
for m in re.finditer(r"localStorage", js):
    before = js[max(0, m.start() - 400):m.start()]
    if "try" not in before:
        fails.append("moi lan dung localStorage phai nam trong try/catch")
        break
check("data-filter" in js and "data-wire-group" in js, "JS xu ly chip loc + nut loc day")
css = (static / "style.css").read_text(encoding="utf-8")
check(re.search(r"\.(guide|wiring|hub)[-\w]*[^{]*\{[^}]*#[0-9a-fA-F]{3,6}", css) is None, "style.css: lop moi khong dat hex (dung token)")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_projects_hub")
