# Gate GHIM TUNG BUOI + BE XIN CHU DE -> NHAY BAI (Claude viet 2026-11-17, executor KHONG sua). Khong goi API, khong mang.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_session_pin.py
# Tuan 2026-11-17: (1) "chua co co che ghim buoi vao hoc sinh ... 8 buoi nhung khong chon buoi theo mong muon";
# (2) be/nguoi lon xin doi chu de bang giong -> neu chu de co trong giao trinh thi DAY BAI DO trong buoi (khong doi con tro
# lo trinh), web hien "dang day"; het buoi quay lai lo trinh.
import asyncio
import json
import re
import os
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
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def fresh():
    data = Path(tempfile.mkdtemp(prefix="stlab-spin-")) / "learners.json"
    return Curriculum(data, LESSONS), data


def learner(data, nick="kay"):
    return json.loads(data.read_text(encoding="utf-8"))["learners"][nick]


# ---------- A. Ghim tung buoi ----------
cur, data = fresh()
ok(hasattr(cur, "session_plan"), "Curriculum co session_plan(lesson_id, n)")
if not fails:
    sp = cur.session_plan("s2-u1-how-are-you", 3)
    ok(isinstance(sp, tuple) and len(sp) == 2 and sp[0].startswith("Buổi 3") and "If You're Happy" in sp[0] + sp[1],
       "session_plan doc dung muc '## Buoi 3' tu stlab/english-curriculum/seed/lesson-plans")
    ok(cur.session_plan("s2-u1-how-are-you", 9) is None and cur.session_plan("s9-u9-x", 1) is None,
       "buoi/bai khong co -> None")
    sp4 = cur.session_plan("s2-u1-how-are-you", 4)
    ok(sp4 and "Buổi 5" not in sp4[1] and "Sổ quan sát" not in sp4[1], "noi dung buoi 4 khong lan sang buoi 5 / so quan sat")

    for bad in (0, 9, "x", 2.5):
        try:
            cur.pin(DEV, "s2-u1-how-are-you", session=bad)
            ok(False, "pin session=%r phai ValueError" % (bad,))
        except ValueError:
            ok(True, "pin session=%r -> ValueError" % (bad,))
    cur.pin(DEV, "s2-u1-how-are-you", session=3)
    info = cur.pin_info(DEV)
    ok(info and info.get("lesson_id") == "s2-u1-how-are-you" and info.get("session") == 3, "pin_info co session=3")
    ok(Curriculum(data, LESSONS).pin_info(DEV).get("session") == 3, "session luu vao learners.json")

    r = cur.start("kay", device=DEV)
    ok(r.get("pinned") is True and r.get("lesson_id") == "s2-u1-how-are-you" and r.get("session") == 3,
       "start may ghim buoi -> pinned + session=3")
    ins = r.get("instructions", "")
    ok("If You're Happy" in ins and "Buổi 3" in ins, "instructions kem noi dung buoi 3 cua giao an")
    ok("Buổi 6" not in ins and "Buổi 1 –" not in ins, "instructions KHONG kem buoi khac")
    ok(len(ins) < 9000, "instructions khong qua dai (%d ky tu)" % len(ins))
    pi = cur.pinned_instructions("kay", device=DEV)
    ok(pi and "Buổi 3" in pi.get("instructions", ""), "pinned_instructions (day giua buoi) cung kem buoi 3")

    cur.pin(DEV, "s2-u1-how-are-you")
    ok("session" not in (cur.pin_info(DEV) or {}) or cur.pin_info(DEV).get("session") is None,
       "ghim lai ca bai (khong session) -> xoa session cu")
    r2 = cur.start("kay", device=DEV)
    ok(r2.get("pinned") and not r2.get("session") and "Buổi 3" not in r2.get("instructions", ""),
       "ghim ca bai -> day nhu cu, khong kem buoi")
    cur.unpin(DEV)

# ---------- B. Be xin chu de -> nhay bai co trong giao trinh ----------
cur, data = fresh()
r = cur.start("kay", device=DEV)
start_lesson = r.get("lesson_id")
L0 = learner(data)
week0, lesson0 = L0.get("week"), L0.get("lesson")
ok(hasattr(cur, "detour_info"), "Curriculum co detour_info(nickname=None, device=None)")
res = cur.set_topic("kay", topic="con vật", words=["dog"])
ok(res.get("ok") and res.get("jump") is True and res.get("lesson_id") == "s1-u5-animals",
   "chu de 'con vat' + tu dog -> nhay s1-u5-animals (%s)" % res.get("lesson_id"))
ok("Animals" in res.get("instructions", "") and "mark_word" in res.get("instructions", ""),
   "chi dan nhay bai co bai Animals va cho goi mark_word")
ok(res.get("words") and set(res["words"]) <= {"cat", "dog", "bird", "fish"}, "tu day lay trong bai Animals (%s)" % res.get("words"))
L1 = learner(data)
ok(L1.get("week") == week0 and L1.get("lesson") == lesson0, "KHONG doi con tro lo trinh (week/lesson giu nguyen)")
di = cur.detour_info("kay")
ok(di and di.get("lesson_id") == "s1-u5-animals" and di.get("at"), "detour_info tra bai dang nhay + at")
ok(cur.mark("kay", "dog", True).get("ok") is not False, "mark_word tu bai nhay van ghi tien do")

res2 = cur.set_topic("kay", topic="animals", words=[])
ok(res2.get("jump") is True and res2.get("lesson_id") == "s1-u5-animals", "khop theo ten chu de tieng Anh (khong can tu)")
res3 = cur.set_topic("kay", topic="Màu sắc", words=[])
ok(res3.get("jump") is True and res3.get("lesson_id") == "s1-u3-colours", "khop theo ten tieng Viet co dau 'Màu sắc'")
res4 = cur.set_topic("kay", topic="khủng long", words=["dinosaur"])
ok(res4.get("ok") and not res4.get("jump") and res4.get("words") == ["dinosaur"],
   "chu de ngoai giao trinh -> duong vong nhu cu (khong jump)")

cur.end_session("kay", 600, 10)
ok(cur.detour_info("kay") is None, "het buoi (end_session) -> xoa detour")
r5 = cur.start("kay", device=DEV)
ok(r5.get("lesson_id") == start_lesson, "buoi sau quay lai lo trinh (%s)" % r5.get("lesson_id"))
cur.set_topic("kay", topic="animals", words=[])
cur.finish("kay", 600, 10)
ok(cur.detour_info("kay") is None, "finish -> xoa detour")
cur.set_topic("kay", topic="animals", words=[])
cur.start("kay", device=DEV)
ok(cur.detour_info("kay") is None, "start buoi moi -> xoa detour cu")

# be 4-5 tuoi -> uu tien bai Seed 2/3
co, dat = fresh()
co.start("kay", device=DEV)
co.set_age("kay", 4)
r6 = co.set_topic("kay", topic="con vật", words=["cow"])
ok(r6.get("jump") and r6.get("lesson_id", "").startswith(("s2-", "s3-")), "be 4 tuoi -> nhay bai Seed 2/3 (%s)" % r6.get("lesson_id"))

# ---------- C. Web ----------
try:
    import curriculum_web  # noqa: E402
    from aiohttp import web
    from aiohttp.test_utils import TestClient, TestServer
except Exception as e:  # noqa: BLE001
    curriculum_web = None
    ok(False, "import curriculum_web (%s)" % e)


class FakeSession:
    def __init__(self):
        self.sent = []

    async def send_lesson(self, text):
        self.sent.append(text)


async def web_tests():
    cur, data = fresh()
    sess = FakeSession()
    devices = {DEV: "kay", DEV2: "bo"}

    def make_app():
        app = web.Application()
        curriculum_web.setup(app, cur=cur, seed_dir=SEED, devices=lambda: dict(devices),
                             active=lambda dev: sess if dev == DEV else None)
        return app

    os.environ["STLAB_CURRICULUM_PIN"] = "4826"
    async with TestClient(TestServer(make_app())) as c:
        origin = {"Origin": str(c.make_url("")).rstrip("/")}
        r = await c.post("/curriculum/login", data={"pin": "4826"}, headers=origin, allow_redirects=False)
        ok(r.status in (200, 302, 303), "dang nhap")

        r = await c.get("/curriculum/s2-u1")
        t = await r.text()
        btn = sorted(set(int(x) for x in re.findall(r'data-pin-session="(\d)"', t)))
        ok(btn == list(range(1, 9)), "trang bai co nut ghim cho 8 buoi data-pin-session=1..8 (%s)" % btn)
        r = await c.get("/curriculum/s2-u13")   # 2026-11-17: chu de mo rong u9..u13 phai mo duoc (UNIT_RE)
        t = await r.text()
        ok(r.status == 200 and len(set(re.findall(r'data-pin-session="(\d)"', t))) == 8,
           "chu de mo rong s2-u13 mo duoc + 8 nut buoi (%s)" % r.status)

        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s2-u1", "session": 9}, headers=origin)
        ok(r.status == 400, "API ghim session=9 -> 400")
        r = await c.post("/curriculum/api/pin", json={"device": DEV, "lesson": "s2-u1", "session": 5}, headers=origin)
        j = await r.json()
        ok(r.status == 200 and (cur.pin_info(DEV) or {}).get("session") == 5 and j.get("session") == 5,
           "API ghim buoi 5 -> luu session=5")
        ok(sess.sent and "Buổi 5" in sess.sent[-1], "may dang hoc -> gui ngay noi dung buoi 5")
        # 2026-11-17 Tuan: "chua thay nut ghim tren tung buoi thay doi icon" -> trang bai danh dau buoi dang ghim
        r = await c.get("/curriculum/s2-u1")
        t = await r.text()
        ok('data-pinned-session="5"' in t and "Đang dạy buổi này" in t and "kay" in t.split('data-pinned-session="5"', 1)[-1][:200],
           "trang bai danh dau buoi 5 dang ghim + ten may")
        ok('data-pinned-session="3"' not in t, "buoi khac khong bi danh dau")
        js = (H / "live" / "static" / "curriculum.js").read_text(encoding="utf-8")
        ok("location.reload()" in js.split("api/pin", 1)[-1][:400], "ghim xong o lai trang bai (reload), khong ve trang chinh")
        r = await c.get("/curriculum")
        t = await r.text()
        ok("Buổi 5" in t, "trang chinh hien may dang ghim Buoi 5")
        await c.post("/curriculum/api/unpin", json={"device": DEV}, headers=origin)

        cur.start("kay", device=DEV)
        cur.set_topic("kay", topic="con vật", words=["dog"])
        r = await c.get("/curriculum")
        t = await r.text()
        dev_card = t.split('data-device="%s"' % DEV, 1)[-1][:700] if 'data-device="%s"' % DEV in t else ""
        ok("Animals" in dev_card and "bé xin" in dev_card, "o may hien 'Dang day: Animals' + nhan 'be xin' khi nhay bai")
        ok(re.search(r'data-unit="s1-u5"[^>]*>', t) and "unit-on" in t.split('data-unit="s1-u5"', 1)[0][-80:],
           "the unit s1-u5 duoc danh dau dang day (unit-on)")
    os.environ.pop("STLAB_CURRICULUM_PIN", None)


if curriculum_web is not None:
    asyncio.run(web_tests())

# ---------- D. Bridge van goi set_topic voi device + gate cu ----------
src = (H / "live" / "bridge.py").read_text(encoding="utf-8")
ok("change_topic" in src and "CUR.set_topic(" in src, "bridge van noi change_topic -> CUR.set_topic")
js = (H / "live" / "static" / "curriculum.js").read_text(encoding="utf-8")
ok("data-pin-session" in js and "session" in js, "curriculum.js gui session khi bam ghim buoi")

print("\n%s test_session_pin (%d loi)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
