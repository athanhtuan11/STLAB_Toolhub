# Gate giao trinh + ho so hoc sinh (Claude viet, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_curriculum.py
# Module can co: server/live/curriculum.py, lop Curriculum(data_path, lessons_dir, now=callable->datetime).
import datetime as dt, json, os, re, sys, tempfile
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
tmp = Path(tempfile.mkdtemp(prefix="stlab-cur-"))
data = tmp / "learners.json"  # gate dung file tam, khong dung server/data
clock = [dt.datetime(2026, 11, 7, 8, 0)]
cur = Curriculum(data, LESSONS, now=lambda: clock[0])

# bai hoc doc tu lessons/*.md (phan "Chi dan cho AI", dong "Vocabulary:")
ids = cur.lesson_ids()
ok(ids[:3] == ["01-colors", "02-animals", "03-numbers-1-5"], f"doc 3 bai theo thu tu ({ids})")
ok(cur.vocabulary("01-colors") == ["red", "blue", "yellow", "green", "pink", "orange"], f"tu bai 01 ({cur.vocabulary('01-colors')})")
ok(len(cur.vocabulary("02-animals")) >= 5, "bai 02 co >= 5 tu")

# biet danh: chi nhan biet danh con vat trong danh sach (khong ten that)
ok(len(ALLOWED_NICKNAMES) >= 6 and all(re.fullmatch(r"[a-zà-ỹđ ]+", n) for n in ALLOWED_NICKNAMES), "danh sach biet danh con vat (chu thuong)")
r = cur.start("Nguyễn Văn An")
ok(r["allowed"] is False and r.get("nicknames"), "tu choi ten that / ngoai danh sach, tra lai danh sach biet danh")
ok(not data.exists() or "An" not in data.read_text(encoding="utf-8"), "khong luu ten ngoai danh sach")
nick = ALLOWED_NICKNAMES[0]
r = cur.start("Bạn " + nick.title())
ok(r["allowed"] is True and r["learner"] == nick, f"nhan 'Ban {nick.title()}' -> {nick}")
ok(r["lesson_id"] == "01-colors", "hoc sinh moi bat dau bai 01")
ok("red" in r["instructions"] and len(r["instructions"]) > 200, "tra chi dan bai hoc cho AI")

# danh dau tu; xong bai khi moi tu dung >= 1 lan + finish
for w in ["red", "blue", "yellow", "green", "pink"]:
    cur.mark(nick, w, True)
cur.mark(nick, "orange", False)
f = cur.finish(nick)
ok(f["next_lesson"] == "01-colors", "chua noi dung 'orange' -> hoc lai bai 01")
clock[0] += dt.timedelta(hours=2)
r = cur.start(nick)
ok(r["lesson_id"] == "01-colors" and "orange" in r.get("review", []), "phien sau on lai tu chua dat (orange)")
cur.mark(nick, "orange", True)
f = cur.finish(nick)
ok(f["next_lesson"] == "02-animals", "dat het tu -> bai 02")

# gioi han 2 phien/ngay (README bai hoc)
clock[0] += dt.timedelta(hours=2)
r = cur.start(nick)
ok(r["allowed"] is False, "phien thu 3 trong ngay bi tu choi (toi da 2)")
ok(re.search(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", r.get("reason", "")) is not None, "ly do tu choi bang tieng Viet")
clock[0] = dt.datetime(2026, 11, 8, 8, 0)
r = cur.start(nick)
ok(r["allowed"] is True and r["lesson_id"] == "02-animals", "ngay moi: hoc tiep bai 02")

# luu file: chi biet danh + tien do, khong ghi am / ten / chu hoi thoai
cur2 = Curriculum(data, LESSONS, now=lambda: clock[0])
ok(cur2.start(nick)["lesson_id"] == "02-animals", "tien do giu sau khi khoi dong lai")
txt = data.read_text(encoding="utf-8")
j = json.loads(txt)
ok(set(j.keys()) <= {"version", "learners"} and nick in j["learners"], "learners.json chi co version + learners")
bad = [k for k in json.dumps(j) .split('"') if k.lower() in ("name", "audio", "transcript", "address", "school", "phone")]
ok(not bad, f"khong co truong du lieu ca nhan ({bad})")

# tool cho Gemini Live: khai bao 3 ham
from curriculum import live_tools  # noqa: E402
names = sorted(fd["name"] for fd in live_tools())
# 2026-11-06: biet danh do CAU NOI tu nhan tu loi be ("ban <con vat>"), Gemini khong goi start_learner (tung tu goi truoc khi be noi)
ok(names == ["finish_lesson", "mark_word"], f"khai bao tool Live chi mark_word + finish_lesson ({names})")
from curriculum import find_nickname  # noqa: E402
ok(find_nickname("Con là bạn Thỏ.") == "thỏ", "nhan 'Con la ban Tho' -> tho")
ok(find_nickname("Cô ơi, con mèo tiếng Anh là gì?") is None, "KHONG nhan 'con meo' (tu vung, khong phai 'ban meo')")
ok(find_nickname("ban gau a") == "gấu", "nhan khong dau 'ban gau'")
ok(find_nickname("Con tên là An") is None, "khong nhan ten that")
print("\n%s test_curriculum (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
