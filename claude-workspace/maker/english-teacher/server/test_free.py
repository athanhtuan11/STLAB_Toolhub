"""Gate bai tu do (free-lesson.on): co file -> Gemini tu len bai, khong ep tu; xoa file -> lo trinh nhu cu.
Chay: runtime\\.venv\\Scripts\\python.exe -X utf8 test_free.py  (du lieu tam, khong dung learners.json that)"""
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "live"))
from curriculum import Curriculum  # noqa: E402

err = 0


def ok(c, msg):
    global err
    print(("PASS " if c else "FAIL ") + msg)
    err += 0 if c else 1


tmp = Path(tempfile.mkdtemp())
data = tmp / "learners.json"
flag = tmp / "free-lesson.on"
cur = Curriculum(data, HERE.parent / "lessons")
cur.free_flag = flag

# 1. khong co file -> lo trinh (co tu moi, khong phai free)
r = cur.start("gấu")
ok(r.get("allowed") and r.get("mode") != "free" and r.get("new") == ["one"], f"khong co free-lesson.on -> lo trinh ({r.get('new')})")
cur.end_session("gấu", 10, 0)   # buoi ngan, khong tinh

# 2. co file -> free: khong ep tu, Gemini tu chon, phai goi change_topic, van doc mau + khong dong tac
flag.write_text("on", encoding="utf-8")
r = cur.start("mèo")
ins = r.get("instructions", "")
ok(r.get("allowed") and r.get("mode") == "free", "co free-lesson.on -> mode free")
ok(r.get("new") == [] and "Today's words, in EXACTLY this order" not in ins, "free: server khong ep danh sach tu")
ok("change_topic" in ins and "yourself" in ins, "free: Gemini tu chon chu de + luu qua change_topic")
ok("Toddler mode" not in ins and "at most 2 sentences" not in ins, "free: khong gan khung buoi / gioi han cau (khong rang buoc)")
ok("Hints from Tuan" in ins and "count numbers in order from one" in ins, "free: goi y cua Tuan chi la goi y")

# 2b. khong gioi han so buoi/ngay (Tuan 2026-11-08)
for k in range(4):
    cur.end_session("mèo", 300, 10)   # buoi that (>= 2 ph)
    r = cur.start("mèo")
    ok(r.get("allowed") is True, f"buoi that thu {k + 2} trong ngay van duoc hoc")

# 3. tu Gemini chon duoc luu de on, con tro lo trinh khong doi
s = cur.set_topic("mèo", topic="hoa", words=["flower", "red"])
si = s.get("instructions", "")
ok(s.get("ok") and "short action, story" not in si and "after you" in si, "set_topic luu tu + chi dan doc mau, khong dong tac")
L = json.loads(data.read_text(encoding="utf-8"))["learners"]["mèo"]
ok([e["word"] for e in L.get("extra", [])] == ["flower", "red"] and L.get("taught", []) == [], "tu tu chon vao extra, con tro khong doi")

# 4. tat file -> quay lai lo trinh
flag.unlink()
r = cur.start("thỏ")
ok(r.get("mode") != "free" and r.get("new") == ["one"], "xoa file -> quay lai lo trinh")

print(("PASS" if not err else "FAIL") + f" test_free ({err} loi)")
sys.exit(1 if err else 0)
