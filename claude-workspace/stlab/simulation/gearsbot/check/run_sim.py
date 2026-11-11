"""Chay thu bai GearsBot tu dong: Edge headless + DevTools Protocol, ve quy dao len sa ban, bao PASS/FAIL.

Chay tu claude-workspace (can Python co `websocket-client` + Pillow, Edge co san tren Windows):
    python stlab/simulation/gearsbot/check/run_sim.py            # chay ca 4 bai
    python stlab/simulation/gearsbot/check/run_sim.py simple     # 1 bai: simple | sharp | obstacles
Script tu bat http.server (cong 8765) phuc vu GearsBot ghim o community/quirkycort-gears + file robot/world.
PASS = robot di toi cuoi sa ban (z >= 95 cm) ma khong ra ngoai mep (|x| <= 50 cm) truoc do.
Anh: stlab/simulation/gearsbot/review/trace-<bai>.png (+ sim-<bai>.png chup man hinh cuoi).
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket
from PIL import Image, ImageDraw

WS = Path(__file__).resolve().parents[4]          # claude-workspace
G = "stlab/simulation/gearsbot"
PUB = WS / "community/quirkycort-gears/public"
REVIEW = WS / G / "review"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
HTTP, CDP_PORT = 8765, 9333
BASE = f"http://127.0.0.1:{HTTP}"
CASES = {  # ten: (world, loi giai, giay chay, anh sa ban, vat can [(x, z)] 20x20, ky vong)
    "one": ("line-simple", "00-one-sensor.py", 240, "Simple.png", [], "PASS"),
    "simple": ("line-simple", "01-line-follow.py", 180, "Simple.png", [], "PASS"),
    "sharp": ("line-sharp", "01-line-follow.py", 180, "Sharp.png", [], "mo rong (co the FAIL)"),
    "obstacles": ("line-obstacles", "02-line-follow-avoid.py", 240, "Obstacles 1.png", [(0, -48), (0, 48)], "PASS"),
}


class Tab:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60)
        self.n = 0

    def cdp(self, method, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                return m.get("result", m)

    def js(self, expr):
        r = self.cdp("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:300])
        return r.get("result", {}).get("value")


def run_case(name):
    world, prog, secs, img, boxes, expect = CASES[name]
    v = int(time.time())
    url = (f"{BASE}/community/quirkycort-gears/public/index.html?worldJSON={BASE}/{G}/{world}.world.json%3Fv%3D{v}"
           f"&robotJSON={BASE}/{G}/stlab-line-bot.robot.json%3Fv%3D{v}")
    prof = Path(tempfile.gettempdir()) / "stlab-gearsbot-edge"
    edge = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={CDP_PORT}", f"--user-data-dir={prof}",
                             "--window-size=1400,900", "--enable-unsafe-swiftshader", "--use-angle=swiftshader",
                             "--no-first-run", "about:blank"])
    try:
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json"))
                break
            except OSError:
                time.sleep(0.2)
        t = Tab([x for x in tabs if x["type"] == "page"][0]["webSocketDebuggerUrl"])
        t.cdp("Page.enable")
        t.cdp("Page.navigate", url=url)
        t0 = time.time()
        while time.time() - t0 < 60:
            time.sleep(1)
            try:
                if t.js("typeof robot!='undefined' && robot.body!=null && robot.options.name") == "stlabLineBot" \
                        and t.js("babylon.world.options.image"):
                    break
            except RuntimeError:
                pass
        time.sleep(3)
        t.js("localStorage.setItem('whatsNew','99999999'); $('.dialog, .dialogBackground').remove(); main.tabClicked('navSim'); 1")
        time.sleep(3)
        code = (WS / G / "solutions" / prog).read_text(encoding="utf-8")
        t.js("filesManager.files['main.py'] = %s; filesManager.modified = true; simPanel.runSim(); "
             "babylon.setCameraMode('orthoTop'); 1" % json.dumps(code))
        trace = []
        t0 = time.time()
        while time.time() - t0 < secs:
            time.sleep(0.5)
            trace.append(t.js("[robot.body.position.x, robot.body.position.z]"))
            if trace[-1][1] > 110:      # da qua cuoi sa ban
                break
        shot = t.cdp("Page.captureScreenshot", format="png")
        (REVIEW / f"sim-{name}.png").write_bytes(base64.b64decode(shot["data"]))
    finally:
        edge.terminate()
    ok = False
    for x, z in trace:
        if abs(x) > 50:
            break
        if z >= 95:
            ok = True
            break
    plot(name, img, trace, boxes)
    return ok, expect, trace


def plot(name, img, trace, boxes):
    im = Image.open(PUB / "textures/maps/Line Following" / img).convert("RGB")
    W, H = im.size
    d = ImageDraw.Draw(im)
    pts = [((x + W / 20) * 10, H - (z + H / 20) * 10) for x, z in trace]
    pts = [p for p in pts if -50 < p[0] < W + 50 and -50 < p[1] < H + 50]
    for cx, cz in boxes:
        d.rectangle([(cx - 10 + W / 20) * 10, H - (cz + 10 + H / 20) * 10, (cx + 10 + W / 20) * 10, H - (cz - 10 + H / 20) * 10],
                    outline=(160, 0, 200), width=8)
    if len(pts) > 1:
        d.line(pts, fill=(255, 0, 0), width=8)
    if pts:
        d.ellipse([pts[0][0] - 15, pts[0][1] - 15, pts[0][0] + 15, pts[0][1] + 15], fill=(0, 160, 0))
    im.thumbnail((500, 1000))
    im.save(REVIEW / f"trace-{name}.png")


def main(argv):
    names = argv or list(CASES)
    REVIEW.mkdir(exist_ok=True)
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(HTTP), "--bind", "127.0.0.1"], cwd=WS,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(1)
        bad = 0
        for n in names:
            ok, expect, trace = run_case(n)
            print(f"{'PASS' if ok else 'FAIL'} {n} (ky vong: {expect}) - {len(trace)} mau, cuoi {[round(v) for v in trace[-1]]}")
            bad += (not ok) and expect == "PASS"
        print("Anh:", REVIEW)
        return 1 if bad else 0
    finally:
        srv.terminate()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.exit(main(sys.argv[1:]))
