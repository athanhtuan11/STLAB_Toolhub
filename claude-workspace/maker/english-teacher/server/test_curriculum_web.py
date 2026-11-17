# Gate GIAO TRINH TREN WEB + GHIM BAI (Claude viet 2026-11-15, executor KHONG sua). Khong goi API, khong mang ngoai.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_curriculum_web.py
# Tuan 2026-11-15: "xay dung giao trinh tieng anh tren giao dien web ... len web chon bai hoc de eng teacher focus vo do day".
# Chot: trang tren server Cu Bong (/curriculum, qua engteacher.mamnoncaynho.com, co PIN o bien moi truong);
# GHIM bai theo MAY toi khi bo ghim (doi ngay neu dang trong buoi); xem bai + giao an. Mockup docs/reports/english-curriculum-web/.
import asyncio
import json
import os
import re
import sys
import tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
WS = H.parent.parent.parent
sys.path.insert(0, str(H / "live"))
from curriculum import Curriculum  # noqa: E402

LESSONS = H.parent / "lessons-seed"
SEED = WS / "stlab" / "english-curriculum" / "seed"
DEV = "e0:8c:fe:64:20:a4"
DEV2 = "aa:bb:cc:dd:ee:02"
COLOURS = ["red", "blue", "yellow", "green"]
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def fresh():
    data = Path(tempfile.mkdtemp(prefix="stlab-cweb-")) / "learners.json"
    return Curriculum(data, LESSONS), data


# ---------- A. Curriculum: ghim theo may ----------
cur, data = fresh()
ok(hasattr(cur, "pin") and hasattr(cur, "unpin") and hasattr(cur, "pin_info") and hasattr(cur, "progress"),
   "Curriculum co pin/unpin/pin_info/progress")
if not fails:
    try:
        cur.pin(DEV, "s9-u9-nothing")
        ok(False, "pin bai la phai ValueError")
    except ValueError:
        ok(True, "pin bai la -> ValueError")
    cur.pin(DEV, "s1-u3-colours")
    info = cur.pin_info(DEV)
    ok(isinstance(info, dict) and info.get("lesson_id") == "s1-u3-colours" and info.get("at"), "pin_info tra lesson_id + at")
    ok(cur.pin_info(DEV2) is None, "may khac khong bi ghim")
    cur2 = Curriculum(data, LESSONS)
    ok((cur2.pin_info(DEV) or {}).get("lesson_id") == "s1-u3-colours", "ghim luu vao learners.json (nap lai van con)")

    r = cur.start("kay", device=DEV)
    ok(r.get("allowed") and r.get("lesson_id") == "s1-u3-colours", "start(biet danh, may bi ghim) -> day bai ghim")
    ok(r.get("pinned") is True, "ket qua start co pinned=True")
    ok(r.get("new") and set(r["new"]) <= set(COLOURS), "tu moi lay trong bai ghim (%s)" % r.get("new"))
    ok("Colours" in r.get("instructions", ""), "instructions co chi dan bai Colours")

    r0 = cur.start("kay")
    ok(r0.get("lesson_id") != "s1-u3-colours" and not r0.get("pinned"), "start khong kem may -> khong ap ghim")

    rd = cur.start(None, device=DEV)
    ok(rd.get("allowed") and rd.get("lesson_id") == "s1-u3-colours" and rd.get("pinned") is True,
       "hoc theo may (khong biet danh) cung theo bai ghim")

    d = json.loads(data.read_text(encoding="utf-8"))
    d["learners"]["kay"]["taught"] = list(dict.fromkeys(d["learners"]["kay"].get("taught", []) + COLOURS))
    data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    r2 = cur.start("kay", device=DEV)
    ok(r2.get("lesson_id") == "s1-u3-colours" and r2.get("new") == [] and r2.get("mode") == "review"
       and r2.get("review") and set(r2["review"]) <= set(COLOURS),
       "het tu bai ghim -> on lai tu bai ghim, khong nhay bai khac")

    pr = cur.progress("kay")
    ok(isinstance(pr, dict) and pr.get("s1-u3-colours", {}).get("taught") == 4 and pr["s1-u3-colours"].get("total") >= 4,
       "progress(biet danh) dem tu da day theo bai")
    ok(isinstance(cur.progress(None, device=DEV2), dict), "progress theo may chua co ho so -> dict rong, khong loi")

    cur.unpin(DEV)
    ok(cur.pin_info(DEV) is None, "unpin xoa ghim")
    r3 = cur.start("kay", device=DEV)
    ok(not r3.get("pinned"), "bo ghim -> ve lo trinh con tro")
    cf, _ = fresh()
    ok(cf.start("kay", device=DEV).get("lesson_id") == "s1-u1-hello", "ho so moi khong ghim -> bai dau lo trinh")


# ---------- B. Web /curriculum ----------
try:
    import curriculum_web  # noqa: E402
    from aiohttp import web
    from aiohttp.test_utils import TestClient, TestServer
except Exception as e:  # noqa: BLE001
    curriculum_web = None
    ok(False, "import live/curriculum_web.py (%s)" % e)


class FakeSession:
    def __init__(self):
        self.sent = []

    async def send_lesson(self, text):
        self.sent.append(text)


async def web_tests():
    cur, _ = fresh()
    sess = FakeSession()
    devices = {DEV: "kay", DEV2: "<b>x</b>"}

    def make_app():
        app = web.Application()
        curriculum_web.setup(app, cur=cur, seed_dir=SEED, devices=lambda: dict(devices),
                             active=lambda dev: sess if dev == DEV else None)
        return app

    # khong co PIN -> trang tat
    os.environ.pop("STLAB_CURRICULUM_PIN", None)
    async with TestClient(TestServer(make_app())) as c:
        r = await c.get("/curriculum")
        ok(r.status == 503, "khong dat STLAB_CURRICULUM_PIN -> 503 (%s)" % r.status)

    os.environ["STLAB_CURRICULUM_PIN"] = "4826"
    async with TestClient(TestServer(make_app())) as c:
        origin = {"Origin": str(c.make_url("")).rstrip("/")}
        r = await c.get("/curriculum")
        t = await r.text()
        ok(r.status == 200 and 'name="pin"' in t and 'data-unit=' not in t, "chua dang nhap -> form PIN, khong lo danh sach")
        # 2026-11-17: no-referrer lam trinh duyet gui "Origin: null" khi POST form -> dang nhap luon 403 du PIN dung
        ok(r.headers.get("Referrer-Policy", "") not in ("no-referrer", ""), "Referrer-Policy khong duoc la no-referrer (Origin: null)")
        ok('inputmode="numeric"' not in t, "o PIN khong ep ban phim so (PIN co chu)")
        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s1-u3-colours"}, headers=origin)
        ok(r.status in (401, 403), "API ghim khi chua dang nhap -> 401/403")
        r = await c.post("/curriculum/login", data={"pin": "0000"}, headers=origin, allow_redirects=False)
        ok(r.status == 401, "sai PIN -> 401 (%s)" % r.status)
        r = await c.post("/curriculum/login", data={"pin": "4826"}, headers=origin, allow_redirects=False)
        sc = r.headers.get("Set-Cookie", "")
        ok(r.status in (200, 302, 303) and "HttpOnly" in sc and "SameSite=Strict" in sc,
           "dung PIN -> cookie HttpOnly SameSite=Strict")
        ok("4826" not in sc, "cookie khong chua PIN tho")

        r = await c.get("/curriculum")
        t = await r.text()
        units = set(re.findall(r'data-unit="(s[1-3]-u\d{1,2})"', t))
        ok(len(units) == 36, "danh sach du 36 unit (24 Core + 12 mo rong 2026-11-17) (co %d)" % len(units))
        ok(all(f'data-level="{lv}"' in t for lv in ("s1", "s2", "s3")), "3 tab data-level s1/s2/s3")
        ok(f'data-device="{DEV}"' in t, "o may data-device")
        ok("<b>x</b>" not in t and "&lt;b&gt;x&lt;/b&gt;" in t, "ten may duoc escape HTML")
        ok("Colours" in t and "Màu sắc" in t and "red" in t, "unit hien theme + theme_vi + tu Core tu units.yaml")

        r = await c.get("/curriculum/s1-u3")
        t = await r.text()
        ok(r.status == 200 and "Colours" in t and ("It&#39;s red." in t or "It's red." in t), "trang bai: theme + mau cau")
        ok("circle" in t and "Phân loại khối" in t, "trang bai: tu Plus + Make & Tell")
        ok("data-pin" in t, "trang bai co nut ghim data-pin")
        ok("data-session" in t and "Chuẩn bị cho cả chủ đề" in t, "giao an render tu lesson-plans (muc data-session)")
        for bad in ("/curriculum/s9-u9", "/curriculum/..%2f..%2fsecret", "/curriculum/s1-u3..%5c"):
            r = await c.get(bad)
            ok(r.status == 404, "bai la/duong dan la %s -> 404 (%s)" % (bad, r.status))

        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s1-u3-colours"})
        ok(r.status == 403, "POST khong co Origin cung host -> 403")
        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s1-u3-colours"},
                         headers={"Origin": "https://evil.example"})
        ok(r.status == 403, "POST Origin la -> 403")
        r = await c.post("/curriculum/api/pin", json={"device": "ff:ff:ff:ff:ff:ff", "lesson": "s1-u3-colours"}, headers=origin)
        ok(r.status == 400, "may khong biet -> 400")
        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s9-u9"}, headers=origin)
        ok(r.status == 400, "bai khong co -> 400")
        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s1-u3-colours"}, headers=origin)
        ok(r.status == 200 and (cur.pin_info(DEV) or {}).get("lesson_id") == "s1-u3-colours", "ghim OK -> luu pin")
        ok(sess.sent and "[lesson]" in sess.sent[-1] and "Colours" in sess.sent[-1],
           "may dang trong buoi -> gui ngay chi dan [lesson] bai ghim")
        r = await c.post("/curriculum/api/pin", json={"device": DEV2, "lesson": "s1-u1"}, headers=origin)
        ok(r.status == 200 and (cur.pin_info(DEV2) or {}).get("lesson_id", "").startswith("s1-u1"),
           "nhan ca id unit ngan (s1-u1) -> anh xa sang bai lessons-seed")
        r = await c.get("/curriculum")
        t = await r.text()
        ok("data-pinned" in t, "o may hien trang thai ghim (data-pinned)")
        r = await c.post("/curriculum/api/unpin", json={"device": DEV}, headers=origin)
        ok(r.status == 200 and cur.pin_info(DEV) is None, "bo ghim qua API")

    # khoa sau nhieu lan sai PIN
    async with TestClient(TestServer(make_app())) as c:
        origin = {"Origin": str(c.make_url("")).rstrip("/")}
        for _ in range(10):
            await c.post("/curriculum/login", data={"pin": "1111"}, headers=origin, allow_redirects=False)
        r = await c.post("/curriculum/login", data={"pin": "4826"}, headers=origin, allow_redirects=False)
        ok(r.status == 429, "10 lan sai PIN -> khoa tam (429) ke ca PIN dung (%s)" % r.status)
    os.environ.pop("STLAB_CURRICULUM_PIN", None)


if curriculum_web is not None:
    asyncio.run(web_tests())

# ---------- C. Noi vao bridge + nginx (tinh) ----------
src = (H / "live" / "bridge.py").read_text(encoding="utf-8")
ok("curriculum_web" in src and re.search(r"curriculum_web\.setup\(\s*app", src) is not None, "bridge goi curriculum_web.setup(app, ...)")
ok(re.search(r"CUR\.start\(\s*nick\s*,\s*device\s*=", src) is not None, "begin_nick truyen device vao CUR.start")
ok(re.search(r"ACTIVE\w*\s*[:=]", src) is not None, "bridge co so phien dang mo theo may (ACTIVE...)")
ng = (H / "deploy" / "nginx-engteacher.conf").read_text(encoding="utf-8")
ok(re.search(r"location\s+/curriculum\b[^{]*\{[^}]*proxy_pass\s+http://127\.0\.0\.1:18003", ng) is not None,
   "nginx: location /curriculum -> 127.0.0.1:18003")
web_src = (H / "live" / "curriculum_web.py").read_text(encoding="utf-8") if (H / "live" / "curriculum_web.py").exists() else ""
ok("4826" not in web_src and not re.search(r"PIN\s*=\s*['\"]\d", web_src), "khong dat PIN cung trong ma")
ok("compare_digest" in web_src, "so PIN/chu ky bang hmac.compare_digest")

print("\n%s test_curriculum_web (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
