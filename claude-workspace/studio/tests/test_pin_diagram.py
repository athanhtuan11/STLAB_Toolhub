# Gate "So do chan tren anh that + so do dau WireViz" (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_pin_diagram.py
import re, sys, xml.dom.minidom
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
sys.stdout.reconfigure(encoding="utf-8")
import yaml  # noqa: E402
from toolhub import create_app, pin_diagram  # noqa: E402

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


LIB = STUDIO.parent / "tools" / "robotics-cad" / "library" / "components.yaml"
comps = {c["id"]: c for c in yaml.safe_load(LIB.read_text(encoding="utf-8"))["components"]}
relay = comps["relay-module-2ch-srd-05vdc"]
IMG_URL = "/library/img/images/relay-module-2ch-srd-05vdc.png"

# 1. So do chan tren anh that (j0ono0/pinout)
svg = pin_diagram.photo_svg(relay)
check(isinstance(svg, str) and "<svg" in svg[:400], "photo_svg phai tra SVG")
if svg and valid_xml(svg, "photo_svg"):
    check(IMG_URL in svg, f"photo_svg phai tham chieu anh qua route {IMG_URL} (khong duong dan o dia, khong base64)")
    check("data:image" not in svg and "D:/" not in svg and "D:\\" not in svg, "khong nhung base64 / duong dan o dia")
    for p in ("DC+", "IN1", "IN2", "S1/S2"):
        check(p in svg, f"photo_svg thieu nhan chan {p}")
    check("COM1?" in svg and "NO1?" in svg, "chan xac_nhan:false phai hien kem '?' (vd 'COM1?')")
    check("DC+?" not in svg, "chan da xac nhan khong duoc co '?'")
    check("var(--err)" in svg, "nhan chan ac220 phai to var(--err) (dung bien CSS Toolhub)")
    check("viewBox" in svg, "SVG can viewBox de co gian")
    check("<script" not in svg.lower(), "khong co script trong SVG")
check(pin_diagram.photo_svg({"ten": "x", "chan": [{"ten": "A"}]}) == "", "khong co anh_chan -> chuoi rong")

# 2. So do dau theo du an (WireViz + Graphviz)
w = pin_diagram.wiring_svg(relay, relay["so_do"][0])
check(isinstance(w, str) and "<svg" in w[:2000], "wiring_svg phai tra SVG")
if w and valid_xml(w[w.index("<svg"):] if "<svg" in w else w, "wiring_svg"):
    for p in ("ESP32 GPIO26", "ESP32 5V", "A1 cuộn hút contactor", "DC+", "IN1", "COM1", "NO1"):
        check(p in w, f"wiring_svg thieu {p}")
    check(IMG_URL in w, "khoi relay trong so do dau phai co anh that (qua route)")
    check("<?xml" not in w and "<!DOCTYPE" not in w, "bo khai bao <?xml/<!DOCTYPE de chen inline vao HTML")
    check("D:/" not in w and "D:\\" not in w and "file:" not in w, "khong de lo duong dan o dia trong SVG")
    check(re.search(r"220\s*VAC", w) is not None, "day 220 VAC phai ghi chu")

# 3. Trang + route anh
c = create_app().test_client()
H = {"Host": "127.0.0.1:5050"}
r = c.get("/library", headers=H)
check(r.status_code == 200, f"/library status {r.status_code}")
html = r.get_data(as_text=True)
check("Sơ đồ chân" in html, "trang thieu muc 'Sơ đồ chân'")
check(IMG_URL in html, "trang thieu so do chan anh that cua relay")
check("ESP32 GPIO26" in html and "pump-control" in html, "trang thieu so do dau pump-control")
check("&lt;svg" not in html, "SVG bi escape thanh text")
ri = c.get(IMG_URL, headers=H)
check(ri.status_code == 200 and ri.mimetype == "image/png", f"route anh: {ri.status_code} {ri.mimetype}")
for bad in ("/library/img/../components.yaml", "/library/img/..%2Fcomponents.yaml", "/library/img/images/../../library/components.yaml"):
    rb = c.get(bad, headers=H)
    check(rb.status_code in (400, 403, 404), f"route anh khong duoc lo file ngoai images/: {bad} -> {rb.status_code}")

# 4. Ban cu (hop chu) van dung cho linh kien co chan nhung chua co anh
from toolhub import pinout as box  # noqa: E402
check(box.render_svg("X", [{"ten": "A"}]).startswith("<svg"), "pinout.render_svg cu bi hong")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_pin_diagram")
