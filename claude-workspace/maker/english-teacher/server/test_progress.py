# Gate CON TRO TU (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_progress.py
# Tuan 2026-11-08 chon phuong an A (docs/research-notes/education/cu-bong-tung-tu-mot.md):
# - 2-3 tuoi: moi buoi 1 tu moi (tung tu mot) + toi da 2 tu on; toi da 2 tu moi / tuan lich ISO; thu tu = cot "new" cua ROADMAP.
# - "moi lan khoi dong ban dang quay lai tu dau" -> tien do theo CON TRO TU, luu file, khoi dong lai hoc TIEP (khong ve "one").
# - Tu duoc tinh "da day" khi buoi co y nghia (>= 120 s hoac >= 3 luot be) HOAC co mark_word cho tu do. Bam thu ngan: khong tien, khong lui.
# - Khong biet be nao (khong biet danh): nho theo MAY (device-id).
# - Be doi bai: lan 1 -> doi tro + tu ke tiep (neu con han muc tuan) / tro on, KHONG quay lai tu vua bo; lan 2+ -> tro on, khong tu moi.
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


from curriculum import Curriculum  # noqa: E402

LESSONS = H.parent / "lessons"
data = Path(tempfile.mkdtemp(prefix="stlab-pg-")) / "learners.json"
clock = [dt.datetime(2026, 11, 9, 8, 0)]          # thu Hai, tuan ISO 46
mk = lambda: Curriculum(data, LESSONS, now=lambda: clock[0])
cur = mk()

rm2 = cur.roadmap(2)
ok(rm2[0]["new"] == ["one", "two"] and rm2[1]["new"] == ["three", "four"], f"lich 2-3: 2 tu/tuan cung chu de ({rm2[0]['new']}, {rm2[1]['new']})")
seq = cur.word_sequence(2)
ok(seq[:6] == ["one", "two", "three", "four", "five", "hello"], f"thu tu tu = cot new noi lien ({seq[:6]})")

nick = "thỏ"
r = cur.start(nick)
ok(r["allowed"] and r.get("new") == ["one"], f"buoi dau: 1 tu moi 'one' ({r.get('new')})")
ok("ONLY NEW WORD(S): one." in r["instructions"] and "ONLY NEW WORD(S): one, two" not in r["instructions"],
   "chi dan: buoi nay CHI 1 tu moi")
cur.end_session(nick, 20, 0)                       # bam thu ngan
r = cur.start(nick)
ok(r.get("new") == ["one"], f"bam thu ngan -> khong tien, khong lui: van 'one' ({r.get('new')})")
cur.end_session(nick, 200, 5)                      # buoi that -> 'one' da day

clock[0] += dt.timedelta(hours=2)
cur = mk()                                         # KHOI DONG LAI may chu
r = cur.start(nick)
ok(r.get("new") == ["two"], f"khoi dong lai -> hoc TIEP 'two', khong ve dau ({r.get('new')})")
ok("one" in r.get("review", []) and len(r.get("review", [])) <= 2, f"on toi da 2 tu, co 'one' ({r.get('review')})")
cur.end_session(nick, 200, 5)

clock[0] = dt.datetime(2026, 11, 10, 8, 0)         # thu Ba cung tuan ISO: da 2 tu moi -> het han muc tuan
r = cur.start(nick)
ok(r.get("new") == [], f"tuan da 2 tu moi -> buoi on, khong tu moi ({r.get('new')})")
ok(r.get("review") and set(r["review"]) <= {"one", "two"}, f"buoi on dung tu da hoc ({r.get('review')})")
ok("one" not in r["instructions"].split("ONLY NEW WORD(S):")[-1][:20] if "ONLY NEW WORD(S):" in r["instructions"] else True,
   "buoi on khong ep tu moi")
cur.end_session(nick, 200, 5)

clock[0] = dt.datetime(2026, 11, 16, 8, 0)         # tuan ISO 47
r = cur.start(nick)
ok(r.get("new") == ["three"], f"tuan moi -> 'three' ({r.get('new')})")
ok("two" in r.get("review", []), f"on co tu gan nhat 'two' ({r.get('review')})")
cur.end_session(nick, 200, 5)
clock[0] += dt.timedelta(hours=3)
r = cur.start(nick)
ok(r.get("new") == ["four"], f"buoi 2 trong tuan -> 'four' ({r.get('new')})")
cur.mark(nick, "four", False)                      # co mark_word -> tinh da day du buoi ngan
cur.end_session(nick, 30, 1)

clock[0] = dt.datetime(2026, 11, 23, 8, 0)         # tuan ISO 48
r = cur.start(nick)
ok(r.get("new") == ["five"], f"mark_word tinh da day -> tuan sau 'five' ({r.get('new')})")
s1 = cur.switch(nick)
ok(s1.get("count") == 1 and s1.get("new") != ["one"] and "five" not in s1.get("new", []),
   f"doi bai lan 1: khong quay ve 'one', khong lap 'five' ({s1.get('new')})")
ok(s1.get("new") == ["hello"], f"doi bai lan 1: tu ke tiep 'hello' (con han muc tuan) ({s1.get('new')})")
ok(bool(s1.get("instructions")) and "hello" in s1["instructions"], "doi bai: co chi dan moi cho co")
s2 = cur.switch(nick)
ok(s2.get("count") == 2 and s2.get("new") == [] and s2.get("review"), f"doi bai lan 2: tro on, khong tu moi ({s2.get('new')}, {s2.get('review')})")
cur.end_session(nick, 200, 5)
clock[0] = dt.datetime(2026, 11, 30, 8, 0)
r = cur.start(nick)
ok(r.get("new") == ["goodbye"], f"sau khi doi sang 'hello' -> buoi sau 'goodbye' ({r.get('new')})")
cur.end_session(nick, 200, 5)

# ho so cu (truoc 2026-11-08, theo tuan lich) -> chuyen sang con tro, khong ve dau
d = json.loads(data.read_text(encoding="utf-8"))
d["learners"]["mèo"] = {"lesson": "03-numbers-1-5", "passed": ["one"], "failed": [], "sessions": [], "week": 1,
                        "wk_iso": "2026-W48", "wk_n": 3, "counted": []}
data.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
cur = mk()
r = cur.start("mèo")
ok(r.get("new") == ["two"], f"ho so cu da dat 'one' -> tiep 'two' ({r.get('new')})")

# khong biet danh -> nho theo MAY
dev = "aa:bb:cc:dd:ee:ff"
r = cur.start(None, device=dev)
ok(r.get("allowed") and r.get("new") == ["one"], f"may moi, khong biet danh -> 'one' ({r.get('new')})")
cur.end_session(None, 200, 5, device=dev)
clock[0] += dt.timedelta(hours=2)
cur = mk()
r = cur.start(None, device=dev)
ok(r.get("new") == ["two"], f"khoi dong lai, khong biet danh -> may nho, tiep 'two' ({r.get('new')})")
d = json.loads(data.read_text(encoding="utf-8"))
ok(dev not in d.get("learners", {}), "ho so may tach rieng, khong lan vao danh sach biet danh")

# 4-5 tuoi van chay (toi da 2 tu moi/buoi)
cur.start("gấu"); cur.set_age("gấu", 5)
clock[0] += dt.timedelta(hours=1)
r = cur.start("gấu")
rm4 = cur.roadmap(5)
ok(r.get("allowed") and r.get("new") and set(r["new"]) <= set(rm4[0]["new"]) and len(r["new"]) <= 2,
   f"be 5 tuoi: tu moi lich 4-5, <= 2/buoi ({r.get('new')})")

print("\n%s test_progress (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
