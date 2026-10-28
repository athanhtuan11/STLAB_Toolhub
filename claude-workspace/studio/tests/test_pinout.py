# Gate "So do chan" trang Thu vien linh kien (Claude viet, executor KHONG sua). Chay tu thu muc studio:
#   .venv/Scripts/python.exe tests/test_pinout.py
import re, sys, xml.dom.minidom
from pathlib import Path

STUDIO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(STUDIO))
from toolhub import create_app, pinout  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


CHAN = [
    {"ten": "VCC", "ben": "trai", "muc": "5v", "mo_ta": "nguồn"},
    {"ten": "GND", "ben": "trai", "muc": "gnd"},
    {"ten": "IN<1>", "ben": "trai", "muc": "3v3"},
    {"ten": "NO", "ben": "phai", "muc": "ac220", "mo_ta": "thường hở"},
    {"ten": "COM", "ben": "phai", "muc": "ac220"},
]
SO_DO = {"du_an": "demo", "tieu_de": "Thử & kiểm",
         "noi": [["VCC", "ESP32 5V", "5 V"], ["IN<1>", "GPIO26 \"x\"", ""], ["COM", "L 220 V", "nguy hiểm"],
                 ["KHONG-CO", "đâu đó", ""]]}

# 1. Chi co chan (khong so do): SVG hop le, du ten chan, escape ky tu dac biet
svg = pinout.render_svg("Relay <test>", CHAN)
check(isinstance(svg, str) and svg.lstrip().startswith("<svg"), "render_svg phai tra chuoi bat dau bang <svg")
try:
    xml.dom.minidom.parseString(svg)
except Exception as e:  # noqa: BLE001
    fails.append(f"SVG khong phai XML hop le: {e}")
for p in ("VCC", "GND", "NO", "COM", "IN&lt;1&gt;", "Relay &lt;test&gt;"):
    check(p in svg, f"thieu/khong escape: {p}")
check("<1>" not in svg and "<test>" not in svg, "ky tu < > chua escape")
check("viewBox" in svg, "SVG phai co viewBox (co gian theo the card)")
check(not re.search(r"#[0-9a-fA-F]{3,6}\b", svg), "khong dung mau hex – chi var(--...) theo DESIGN.md")
check("var(--err)" in svg, "chan ac220 phai to var(--err)")

# 2. Co so do: du dich noi, ghi chu; chan khong ton tai khong lam vo, duoc bao
svg2 = pinout.render_svg("Relay", CHAN, SO_DO)
xml.dom.minidom.parseString(svg2)
for p in ("ESP32 5V", "GPIO26 &quot;x&quot;", "L 220 V", "nguy hiểm", "Thử &amp; kiểm"):
    check(p in svg2, f"so do thieu: {p}")
check(svg2.count("<line") + svg2.count("<path") >= 3, "moi day noi phai ve 1 duong (line/path), >= 3")
check("KHONG-CO" in svg2, "chan khong co trong danh sach van phai hien (danh dau loi), khong bi bo")
check("220 VAC" in svg2 or "220 V" in svg2, "chu thich muc dien ap phai co")

# 3. Rong / thieu truong
check(pinout.render_svg("X", []) == "", "khong co chan -> chuoi rong")
xml.dom.minidom.parseString(pinout.render_svg("X", [{"ten": "A"}]))  # thieu ben/muc -> mac dinh, khong loi

# 4. Trang /library: relay co so do chan that tu components.yaml
c = create_app().test_client()
r = c.get("/library/relay-module-2ch-srd-05vdc", headers={"Host": "127.0.0.1:5050"})
check(r.status_code == 200, f"/library/<id> status {r.status_code}")
html = r.get_data(as_text=True)
check("Sơ đồ chân" in html, "trang thieu muc 'Sơ đồ chân'")
check(html.count("<svg") >= 1 and "ESP32 GPIO26" in html, "card relay thieu SVG so do pump-control")
check("pump-control" in html, "thieu ten du an cua so do")
check("COM1" in html and "NO1" in html, "thieu chan COM1/NO1 cua relay")
check("&lt;svg" not in html, "SVG bi escape thanh text (thieu |safe)")
r2 = c.get("/library/relay-module-2ch-srd-05vdc", headers={"Host": "127.0.0.1:5050"})
check(r2.get_data(as_text=True).count("<svg") == html.count("<svg"), "goi lai /library khong duoc nhan doi SVG")

if fails:
    print("FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS test_pinout")
