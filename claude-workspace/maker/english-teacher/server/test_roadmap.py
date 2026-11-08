# Gate LO TRINH TUAN (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_roadmap.py
# 2026-11-08: bo luat "tuan ISO >= 2 buoi" (Tuan: khoi dong lai khong duoc quay ve dau) - tien do kiem o test_progress.py.
# Lich doc tu lessons/ROADMAP.md: muc "## Lich tuan (may doc)" (4-5 tuoi) va "## Lich tuan 2-3 tuoi (may doc)" (age_band <= 3),
# dong "Week N: <lesson_id> | new: a, b | review: c | daily: d, e | song: <id>".
import datetime as dt, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H / "live"))
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


from curriculum import Curriculum, ALLOWED_NICKNAMES  # noqa: E402

LESSONS = H.parent / "lessons"
data = Path(tempfile.mkdtemp(prefix="stlab-rm-")) / "learners.json"
clock = [dt.datetime(2026, 11, 9, 8, 0)]          # thu Hai, tuan ISO 46
cur = Curriculum(data, LESSONS, now=lambda: clock[0])
nick = ALLOWED_NICKNAMES[0]

rm2, rm4 = cur.roadmap(2), cur.roadmap(5)
ok(len(rm2) >= 12 and len(rm4) >= 12, f"doc >= 12 tuan cho ca 2 lich ({len(rm2)}, {len(rm4)})")
w1 = rm2[0]
ok(set(w1) >= {"week", "lesson_id", "new", "review", "daily"} and w1["week"] == 1, f"tuan 1 du truong ({sorted(w1)})")
ok(w1["lesson_id"] in cur.lesson_ids(), f"bai tuan 1 co that ({w1['lesson_id']})")
ok(all(r["lesson_id"] in cur.lesson_ids() for r in rm2 + rm4), "moi bai trong lich deu co file trong lessons/")

# 2026-11-08 Tuan chon phuong an A: tien do theo CON TRO TU (khong theo tuan lich ISO) -> kiem o test_progress.py.
# be 5 tuoi -> lich 4-5
nick2 = ALLOWED_NICKNAMES[1]
cur.start(nick2); cur.finish(nick2)
cur.set_age(nick2, 5)
clock[0] += dt.timedelta(hours=3)
r = cur.start(nick2)
ok(r.get("week") == 1 and r["lesson_id"] == rm4[0]["lesson_id"] and all(w in r["instructions"] for w in rm4[0]["new"]),
   "be 5 tuoi dung lich 4-5 tuoi")

# het lich -> quay vong, khong loi
cur2 = Curriculum(data, LESSONS, now=lambda: clock[0])
last = len(rm2)
ok(cur2.roadmap_week(2, last + 3)["lesson_id"] in cur.lesson_ids(), "qua tuan cuoi -> quay vong ra bai hop le")
print("\n%s test_roadmap (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
