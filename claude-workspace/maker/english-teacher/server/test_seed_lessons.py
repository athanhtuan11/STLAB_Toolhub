# Gate LO TRINH SEED (Claude viet 2026-11-12, executor KHONG sua). Khong goi API.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_seed_lessons.py
# Nguon: stlab/english-curriculum/seed/units.yaml -> export_device.py -> maker/english-teacher/lessons-seed/ (24 bai + ROADMAP.md).
# Lich 2-3 tuoi = Seed 1 (s1-u1..u8); lich 4-5 tuoi = Seed 2 roi Seed 3 (s2-u1..u8, s3-u1..u8). Tu moi = tu Core theo thu tu.
import datetime as dt, json, re, subprocess, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
WS = H.parents[2]                                   # claude-workspace
sys.path.insert(0, str(H / "live"))
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


import yaml  # noqa: E402
from curriculum import Curriculum, ALLOWED_NICKNAMES, HEADING  # noqa: E402

SEED = WS / "stlab" / "english-curriculum" / "seed"
LS = H.parent / "lessons-seed"
units = {lv["id"]: lv["units"] for lv in yaml.safe_load((SEED / "units.yaml").read_text(encoding="utf-8"))["levels"]}

# 1. export_device.py --check: lessons-seed/ khop units.yaml (sinh lai khong doi gi)
r = subprocess.run([sys.executable, "-X", "utf8", str(SEED / "export_device.py"), "--check"], capture_output=True, text=True)
ok(r.returncode == 0, "export_device.py --check: lessons-seed/ dung voi units.yaml" + ("" if r.returncode == 0 else " | " + (r.stdout + r.stderr)[-300:]))

clock = [dt.datetime(2026, 11, 16, 8, 0)]
data = Path(tempfile.mkdtemp(prefix="stlab-seed-")) / "learners.json"
cur = Curriculum(data, LS, now=lambda: clock[0])

# 2. du 24 bai, ten file bat dau bang id chu de, vocab = core dung thu tu
ids = cur.lesson_ids()
ok(len(ids) == 24, f"24 bai co '{HEADING}' ({len(ids)})")
for lv, us in units.items():
    for u in us:
        lid = next((i for i in ids if i.startswith(u["id"] + "-")), None)
        if lid is None:
            ok(False, f"thieu file bai {u['id']}")
            continue
        voc = cur.vocabulary(lid)
        ok(voc == [str(w).lower() for w in u["core"]], f"{lid}: Vocabulary = core ({len(voc)}/{len(u['core'])})")
        txt = (LS / (lid + ".md")).read_text(encoding="utf-8")
        ok(all(str(p).lower() in txt.lower() for p in u["plus"]), f"{lid}: co tu Plus (tu mo rong, sau tu Core)")
        ok(u["patterns"][0].split("–")[0].split("/")[0].strip()[:12].lower() in txt.lower(), f"{lid}: co mau cau")

# 3. lich: 2-3 tuoi = Seed 1, 4-5 tuoi = Seed 2 + Seed 3; moi lesson_id co file; tu 'new' nam trong vocab bai do
def seq(levels):
    out = []
    for lv in levels:
        for u in units[lv]:
            for w in u["core"]:
                w = str(w).lower()
                if w not in out:
                    out.append(w)
    return out

rm2, rm4 = cur.roadmap(2), cur.roadmap(4)
ok(cur.word_sequence(2) == seq(["s1"]), f"thu tu tu 2-3 tuoi = core Seed 1 ({len(cur.word_sequence(2))}/{len(seq(['s1']))})")
ok(cur.word_sequence(4) == seq(["s2", "s3"]), f"thu tu tu 4-5 tuoi = core Seed 2 + 3 ({len(cur.word_sequence(4))}/{len(seq(['s2', 's3']))})")
ok(cur.roadmap(5) == rm4, "5 tuoi dung chung lich 4-5")
ok(all(r["lesson_id"] in ids for r in rm2 + rm4), "moi lesson_id trong lich co file")
ok(all(w in cur.vocabulary(r["lesson_id"]) for r in rm2 + rm4 for w in r["new"]), "tu 'new' thuoc Vocabulary cua bai trong hang")
ok(all(1 <= len(r["new"]) <= 2 for r in rm2 + rm4), "moi hang 1-2 tu moi")
ok([r["week"] for r in rm4] == list(range(1, len(rm4) + 1)), "Week danh so lien 1..N (lich 4-5)")
ok("Chỉ dẫn cho AI" not in (LS / "ROADMAP.md").read_text(encoding="utf-8"), "ROADMAP.md khong chua tieu de bai")

# 4. buoi dau: be moi (mac dinh 2 tuoi) -> s1-u1, tu dau 'hello'; be 4 tuoi -> s2-u1
nick, nick4 = ALLOWED_NICKNAMES[0], ALLOWED_NICKNAMES[1]
s = cur.start(nick)
ok(s["allowed"] and s["lesson_id"].startswith("s1-u1-") and s.get("new") == ["hello"], f"be moi: s1-u1, tu moi hello ({s.get('lesson_id')}, {s.get('new')})")
cur.start(nick4); cur.set_age(nick4, 4)
clock[0] += dt.timedelta(days=1)
s4 = cur.start(nick4)
ok(s4["lesson_id"].startswith("s2-u1-") and s4.get("new") and s4["new"][0] == seq(["s2"])[0], f"be 4 tuoi: s2-u1 ({s4.get('lesson_id')}, {s4.get('new')})")
ok("Vocabulary:" in s4["instructions"] and "Seed 2" in s4["instructions"], "chi dan gui Gemini co bai Seed 2")

# 5. ho so cu (bai 01-colors, da hoc red/blue) khong vo; tu da hoc khong day lai
old = Path(tempfile.mkdtemp(prefix="stlab-seed-old-")) / "learners.json"
old.write_text(json.dumps({"learners": {nick: {"lesson": "01-colors", "passed": ["red", "blue"], "failed": [], "sessions": [],
                                                "age_band": 4, "taught": ["hello", "goodbye", "red", "blue"]}}}), encoding="utf-8")
cur_o = Curriculum(old, LS, now=lambda: clock[0])
try:
    so = cur_o.start(nick)
    ok(so["allowed"] and so["lesson_id"] in ids, f"ho so cu chay duoc ({so['lesson_id']})")
    ok(not set(so.get("new") or []) & {"hello", "red", "blue"}, f"khong day lai tu da hoc ({so.get('new')})")
except Exception as e:  # noqa: BLE001
    ok(False, f"ho so cu loi: {e!r}")

# 6. bridge.py chon lessons-seed mac dinh, STLAB_LESSONS_DIR doi lai duoc
b = (H / "live" / "bridge.py").read_text(encoding="utf-8")
ok(re.search(r"STLAB_LESSONS_DIR", b) and "lessons-seed" in b, "bridge.py: mac dinh lessons-seed, doi bang STLAB_LESSONS_DIR")

print(("GATE FAIL (%d)" % len(fails)) if fails else "GATE PASS")
sys.exit(1 if fails else 0)
