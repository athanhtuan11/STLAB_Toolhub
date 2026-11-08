# Gate CHU DE TU CHON + KHONG GO BO (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_topic.py
# Tuan 2026-11-08: "ngoai bai hoc thi gemini can hieu va giao tiep nhung topic ngoai luong. toi khong muon go bo.
# vi du toi muon doi bai hoc cho be 2 tuoi chu de ve hoa".
# -> lo trinh = ke hoach MAC DINH (khong cam noi chuyen khac); cong cu change_topic(topic, words) do Gemini goi khi be/nguoi lon
#    xin chu de khac; tu cua chu de luu "extra" de on buoi sau; con tro lo trinh KHONG doi.
import datetime as dt, json, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H / "live"))
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


from curriculum import Curriculum, live_tools  # noqa: E402

LESSONS = H.parent / "lessons"
data = Path(tempfile.mkdtemp(prefix="stlab-tp-")) / "learners.json"
clock = [dt.datetime(2026, 11, 9, 8, 0)]
mk = lambda: Curriculum(data, LESSONS, now=lambda: clock[0])
cur = mk()

names = sorted(t["name"] for t in live_tools())
ok("change_topic" in names and {"mark_word", "finish_lesson"} <= set(names), f"co cong cu change_topic ({names})")
ct = next(t for t in live_tools() if t["name"] == "change_topic")
props = ct["parameters"]["properties"]
ok("topic" in props and "words" in props and props["words"].get("type") == "ARRAY", "change_topic(topic: STRING, words: ARRAY)")
ok(len(ct.get("description", "")) > 40, "mo ta change_topic du ro (khi nao goi)")

nick = "thỏ"
r = cur.start(nick)
ins = r["instructions"]
ok("do NOT teach any other new word" not in ins, "chi dan KHONG con lenh cam tu khac (khong go bo)")
ok("FLEXIBLE" in ins and "change_topic" in ins, "chi dan co muc FLEXIBLE: theo y be/nguoi lon, goi change_topic khi xin chu de khac")
ok(r.get("new") == ["one"], f"mac dinh van theo lo trinh ('one') ({r.get('new')})")

t = cur.set_topic(nick, topic="hoa", words=["Flower", "rose!!", "a b c d e f g h", "sun flower", "x" * 40, "red"])
ok(t.get("ok") is True, "set_topic ok")
w = t.get("words", [])
ok(1 <= len(w) <= 3 and w[0] == "flower" and all(len(x) <= 20 for x in w), f"lam sach tu: thuong, bo ky tu la, <= 3 tu, <= 20 ky tu ({w})")
ok(all(x.replace(" ", "").isalpha() for x in w), "tu chi gom chu cai/khoang trang")
ok("flower" in t.get("instructions", "") and "hoa" in t.get("instructions", ""), "chi dan chu de moi co chu de + tu")
ok("one at a time" in t.get("instructions", "").lower(), "chu de moi van day TUNG TU MOT")
bad = cur.set_topic(nick, topic="", words=[])
ok(bad.get("ok") is False, "chu de rong -> tu choi")
cur.end_session(nick, 200, 5)

d = json.loads(data.read_text(encoding="utf-8"))
L = d["learners"][nick]
ok("flower" in [x.get("word") if isinstance(x, dict) else x for x in L.get("extra", [])], f"luu tu chu de vao 'extra' ({L.get('extra')})")
ok(json.dumps(d, ensure_ascii=False).count("hoa") <= 3, "khong luu hoi thoai, chi chu de ngan")

clock[0] += dt.timedelta(hours=3)
cur = mk()
r = cur.start(nick)
ok(r.get("new") == ["two"], f"con tro lo trinh khong bi chu de lam lech: buoi sau 'two' ({r.get('new')})")
seen = "flower" in r.get("review", [])
cur.end_session(nick, 200, 5)
clock[0] = dt.datetime(2026, 11, 10, 8, 0)
r2 = cur.start(nick)
ok(seen or "flower" in r2.get("review", []), f"tu chu de 'flower' duoc on trong 2 buoi sau ({r.get('review')}, {r2.get('review')})")
# 2026-11-08 Tuan: bai so on dem tu one theo thu tu (khong gioi han) -> chi gioi han tu on ngoai day so
NUMS = ("one", "two", "three", "four", "five")
ok(len([w for w in r2.get("review", []) if w not in NUMS]) <= 2, f"on ngoai day so van <= 2 tu ({r2.get('review')})")
ok([w for w in r2.get("review", []) if w in NUMS] == [w for w in NUMS if w in r2.get("review", [])],
   f"bai so on dung thu tu dem ({r2.get('review')})")

# khong biet danh -> theo may
dev = "aa:bb:cc:dd:ee:01"
cur.start(None, device=dev)
t = cur.set_topic(None, device=dev, topic="xe cộ", words=["car"])
ok(t.get("ok") and t.get("words") == ["car"], "set_topic theo may")
print("\n%s test_topic (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
