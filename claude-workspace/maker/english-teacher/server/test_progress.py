# Gate CON TRO TU (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_progress.py
# Tuan 2026-11-08 chon phuong an A (docs/research-notes/education/cu-bong-tung-tu-mot.md):
# - 2-3 tuoi: moi buoi 1 tu moi (tung tu mot) + toi da 2 tu on; KHONG han muc tuan (Tuan 2026-11-12: hoc it nhieu tuy thoi gian cua be), hoc xong tu thi mark() dua tu ke tiep; thu tu = cot "new" cua ROADMAP.
# - "moi lan khoi dong ban dang quay lai tu dau" -> tien do theo CON TRO TU, luu file, khoi dong lai hoc TIEP (khong ve "one").
# - Tu duoc tinh "da day" khi buoi co y nghia (>= 120 s hoac >= 3 luot be) HOAC co mark_word cho tu do. Bam thu ngan: khong tien, khong lui.
# - Khong biet be nao (khong biet danh): nho theo MAY (device-id).
# - Be doi bai: lan 1 -> doi tro + tu ke tiep / tro on, KHONG quay lai tu vua bo; lan 2+ -> tro on, khong tu moi.
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

clock[0] = dt.datetime(2026, 11, 10, 8, 0)         # thu Ba cung tuan: 2026-11-12 BO han muc tuan -> van co tu moi
r = cur.start(nick)
ok(r.get("new") == ["three"], f"khong han muc tuan: cung tuan van hoc tiep 'three' ({r.get('new')})")
m = cur.mark(nick, "three", True)                  # hoc xong tu moi -> may dua tu ke tiep NGAY trong buoi
ok(m.get("next_words") == ["four"] and "four" in m.get("instructions", ""), f"mark xong -> tu ke tiep 'four' trong buoi ({m.get('next_words')})")
m = cur.mark(nick, "four", False)                  # sai van tinh da day -> tiep 'five'
ok(m.get("next_words") == ["five"], f"mark (sai) xong -> tiep 'five' ({m.get('next_words')})")
ok(cur.mark(nick, "one", True).get("next_words") is None, "mark tu on khong day tu moi")
cur.end_session(nick, 200, 5)                      # 'five' dua giua buoi nhung CHUA mark -> khong tinh da day

clock[0] = dt.datetime(2026, 11, 10, 17, 0)
r = cur.start(nick)
ok(r.get("new") == ["five"], f"tu dua giua buoi chua hoc -> buoi sau day lai 'five', khong bo qua ({r.get('new')})")
cur.end_session(nick, 200, 5)                      # buoi dai -> 'five' (tu dau buoi) tinh da day
r = cur.start(nick)
ok(r.get("new") == ["hello"], f"buoi sau hoc tiep 'hello' ({r.get('new')})")
ok("five" in r.get("review", []), f"on co tu gan nhat 'five' ({r.get('review')})")
s1 = cur.switch(nick)
ok(s1.get("count") == 1 and s1.get("new") == ["goodbye"], f"doi bai lan 1: tu ke tiep 'goodbye', khong lap 'hello' ({s1.get('new')})")
ok(bool(s1.get("instructions")) and "goodbye" in s1["instructions"], "doi bai: co chi dan moi cho co")
s2 = cur.switch(nick)
ok(s2.get("count") == 2 and s2.get("new") == [] and s2.get("review"), f"doi bai lan 2: tro on, khong tu moi ({s2.get('new')}, {s2.get('review')})")
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
