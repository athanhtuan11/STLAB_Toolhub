"""Giao trinh + ho so hoc sinh theo biet danh con vat (khong ten that, khong sinh trac hoc).
Chi luu: biet danh, bai hien tai, tu dat/chua dat, gio phien. Khong luu hoi thoai/am thanh. Thuan Python, khong goi mang."""
import json, os, random, re, threading, unicodedata
from datetime import datetime
from pathlib import Path

ALLOWED_NICKNAMES = ["thỏ", "mèo", "gấu", "cá", "chim", "voi", "khỉ", "cún"]
MAX_SESSIONS_PER_DAY = 2
REASON_LIMIT = "Hôm nay con học đủ rồi, mai mình học tiếp nhé!"
HEADING = "## Chỉ dẫn cho AI"
ACTIVITIES = ("repeat-after-me", "quiz", "touch-game", "rhyme-chant", "tiny-story", "guessing-game")


DEFAULT_AGE = 2   # chua dat -> doi tuong tre nhat (be 2 tuoi)
TODDLER_MODE = ("Toddler mode: speak very slowly, 3-5 words per sentence; teach only 3-4 words this session; "
                "you model the word many times, the child repeating is a bonus; accept ANY attempt that sounds roughly "
                "similar as correct (call mark_word correct=true) and praise the effort; never ask to repeat more than "
                "once; use songs, sounds, and 'show me' actions; lots of Vietnamese support.")


def normalize(nick):
    s = re.sub(r"[^\w\s]", " ", str(nick or "").lower())
    words = [w for w in s.split() if w not in ("bạn", "ban")]
    return " ".join(words)


def _fold(t):
    t = unicodedata.normalize("NFD", str(t or "").lower()).replace("đ", "d")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return " ".join("".join(c if c.isalnum() else " " for c in t).split())


def find_nickname(text):
    """Chi nhan cum 'ban <ten>' (khong dau/co dau) voi ten trong ALLOWED_NICKNAMES; 'con meo', ten nguoi -> None."""
    by_fold = {_fold(n): n for n in ALLOWED_NICKNAMES}
    w = _fold(text).split()
    for i in range(len(w) - 1):
        if w[i] == "ban" and w[i + 1] in by_fold:
            return by_fold[w[i + 1]]
    return None


class Curriculum:
    def __init__(self, data_path, lessons_dir, now=datetime.now):
        self.path = Path(data_path)
        self.now = now
        self.lock = threading.Lock()
        self.lessons = {}
        self.order = []
        for f in sorted(Path(lessons_dir).glob("*.md"), key=lambda p: p.name):
            if f.name.lower() == "readme.md":
                continue
            txt = f.read_text(encoding="utf-8")
            if HEADING not in txt:
                continue
            instr = txt.split(HEADING, 1)[1]
            instr = re.split(r"(?m)^## ", instr, maxsplit=1)[0].strip()
            vocab = []
            m = re.search(r"Vocabulary:\s*(.*?)(?:\.\s|\.$|\n)", instr)
            if m:
                for item in re.split(r",\s*", m.group(1)):
                    w = re.sub(r"\(.*?\)", "", item).strip().lower()
                    if w:
                        vocab.append(w)
            self.order.append(f.stem)
            mt = re.match(r"#[^\n]*?[–-]\s*(.+)", txt)
            self.lessons[f.stem] = {"instructions": instr, "vocab": vocab,
                                    "title": re.sub(r"\s*\(.*?\)", "", mt.group(1)).strip() if mt else f.stem}

    def age_band(self, nickname):
        """Tuoi (2-5) do phu huynh dat; chua dat/khong biet danh -> DEFAULT_AGE."""
        try:
            a = int(self._load()["learners"].get(normalize(nickname), {}).get("age_band", DEFAULT_AGE))
        except (TypeError, ValueError):
            a = DEFAULT_AGE
        return a if 2 <= a <= 5 else DEFAULT_AGE

    def set_age(self, nickname, age):
        nick = normalize(nickname)
        if nick not in ALLOWED_NICKNAMES or int(age) not in (2, 3, 4, 5):
            return False
        with self.lock:
            d = self._load()
            L = d["learners"].setdefault(nick, {"lesson": self.order[0], "passed": [], "failed": [], "sessions": []})
            L["age_band"] = int(age)
            self._save(d)
        return True

    def lesson_ids(self):
        return list(self.order)

    def vocabulary(self, lesson_id):
        return list(self.lessons[lesson_id]["vocab"])

    def _load(self):
        try:
            d = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(d.get("learners"), dict):
                return d
        except (OSError, ValueError):
            pass
        return {"version": 1, "learners": {}}

    def _save(self, d):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, self.path)

    def start(self, nickname):
        nick = normalize(nickname)
        if nick not in ALLOWED_NICKNAMES:
            return {"allowed": False, "nicknames": list(ALLOWED_NICKNAMES),
                    "reason": "Con chọn một biệt danh con vật trong danh sách nhé, không dùng tên thật."}
        with self.lock:
            d = self._load()
            now = self.now()
            L = d["learners"].setdefault(nick, {"lesson": self.order[0], "passed": [], "failed": [], "sessions": []})
            today = now.date().isoformat()
            if sum(1 for s in L["sessions"] if s[:10] == today) >= MAX_SESSIONS_PER_DAY:
                return {"allowed": False, "reason": REASON_LIMIT}
            L["sessions"].append(now.isoformat(timespec="minutes"))
            L["sessions"] = L["sessions"][-50:]
            self._save(d)
            lid = L["lesson"]
            review = [w for w in L["failed"] if w in self.lessons[lid]["vocab"] and w not in L["passed"]]
            instr = self.lessons[lid]["instructions"]
            toddler = int(L.get("age_band", DEFAULT_AGE)) <= 3
            last = list(L.get("last_activities", []))
            vocab = self.lessons[lid]["vocab"]
            if vocab and all(w in L["passed"] for w in vocab) and lid == self.order[-1]:
                # da hoc het bai cuoi -> che do on tu do (khong con tu moi)
                learned = [w for i in self.order for w in self.lessons[i]["vocab"]]
                instr += "\n" + self.review_plan(learned)
                if toddler:
                    instr += "\n" + TODDLER_MODE
                self._save(d)
                return {"allowed": True, "learner": nick, "lesson_id": lid, "instructions": instr, "review": [],
                        "mode": "review"}
            if review:
                instr += "\n- Words to review first today: " + ", ".join(review) + "."
            plan, act = self.today_plan(lid, review, last)
            L["last_activities"] = (last + [act])[-3:]
            self._save(d)
            instr += "\n" + plan
            if toddler:
                instr += "\n" + TODDLER_MODE
            return {"allowed": True, "learner": nick, "lesson_id": lid, "instructions": instr, "review": review}

    def review_plan(self, learned):
        words = list(dict.fromkeys(learned))
        random.shuffle(words)
        return ("Review mode: the child has learned every lesson. Have a free, warm chat on a safe topic "
                "(animals, colors, numbers, family, toys) and weave in these learned words at random: "
                + ", ".join(words[:8]) + ". Invent fresh games, short stories or chants. Keep each turn short.")

    def today_plan(self, lid, review=(), last=()):
        """Muc tieu buoi hoc: tu xao thu tu (tu on len dau), goi y 1 kieu hoat dong khac lan truoc;
        Gemini tu sang tao cach day, khong dung lai <last_activities>. Tra (van ban, nhan hoat dong)."""
        vocab = list(self.lessons[lid]["vocab"])
        rest = [w for w in vocab if w not in review]
        random.shuffle(rest)
        order = [w for w in vocab if w in review] + rest
        pool = [a for a in ACTIVITIES if a not in last] or list(ACTIVITIES)
        act = random.choice(pool)
        title = self.lessons[lid].get("title", lid)
        avoid = ", ".join(last) if last else "none"
        return (f"Today's goal words, in this order: {', '.join(order)}. Suggested activity type: {act}. "
                "These are GOALS, not a script. Invent fresh ways to teach them this session: new example sentences "
                "(<= 5 words), a tiny story, a guessing game, a made-up song or chant, a touch-something game. "
                f"Do NOT reuse these from last time: {avoid}. Keep each turn short. First, say in Vietnamese what we "
                f"learn today (\"Hôm nay mình học {title.lower()} nhé\"), then teach the first word '{order[0]}' in English.", act)

    def anonymous_lesson(self):
        """Ket noi khong co biet danh: chon NGAU NHIEN 1 bai (khong ghi ho so). Tra (lesson_id, instructions)."""
        lid = random.choice(self.order)
        return lid, self.lessons[lid]["instructions"] + "\n" + self.today_plan(lid)[0] + "\n" + TODDLER_MODE

    def mark(self, nickname, word, correct):
        nick = normalize(nickname)
        w = str(word or "").strip().lower()
        with self.lock:
            d = self._load()
            L = d["learners"].get(nick)
            if L is None or w not in self.lessons[L["lesson"]]["vocab"]:
                return {"ok": False}
            if correct:
                if w not in L["passed"]:
                    L["passed"].append(w)
                L["failed"] = [x for x in L["failed"] if x != w]
            else:
                if w not in L["passed"] and w not in L["failed"]:
                    L["failed"].append(w)
            self._save(d)
            return {"ok": True}

    def finish(self, nickname):
        nick = normalize(nickname)
        with self.lock:
            d = self._load()
            L = d["learners"].get(nick)
            if L is None:
                return {"next_lesson": self.order[0]}
            vocab = self.lessons[L["lesson"]]["vocab"]
            if all(w in L["passed"] for w in vocab):
                i = self.order.index(L["lesson"])
                if i + 1 < len(self.order):
                    L["lesson"] = self.order[i + 1]
                    L["passed"], L["failed"] = [], []
            self._save(d)
            return {"next_lesson": L["lesson"]}


def live_tools():
    return [
        {"name": "mark_word",
         "description": "Record whether the child repeated a vocabulary word correctly.",
         "parameters": {"type": "OBJECT",
                        "properties": {"word": {"type": "STRING", "description": "English vocabulary word"},
                                       "correct": {"type": "BOOLEAN", "description": "true if said correctly"}},
                        "required": ["word", "correct"]}},
        {"name": "finish_lesson",
         "description": "Call at the end of the session to save progress and pick the next lesson.",
         "parameters": {"type": "OBJECT", "properties": {}}},
    ]


def _cli(argv):
    import argparse
    ap = argparse.ArgumentParser(description="Dat/xem do tuoi (2-5) theo biet danh, chi so tuoi, khong ngay sinh")
    ap.add_argument("--set-age", nargs=2, metavar=("BIET_DANH", "TUOI"))
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--path", default=os.environ.get("STLAB_LEARNERS_PATH") or str(Path(__file__).resolve().parent.parent / "data" / "learners.json"))
    a = ap.parse_args(argv)
    cur = Curriculum(a.path, Path(__file__).resolve().parent.parent.parent / "lessons")
    if a.set_age:
        try:
            ok = cur.set_age(a.set_age[0], int(a.set_age[1]))
        except ValueError:
            ok = False
        print(("da dat" if ok else "loi: biet danh phai thuoc " + ",".join(ALLOWED_NICKNAMES) + ", tuoi 2|3|4|5"))
        return 0 if ok else 1
    d = cur._load()
    print(f"mac dinh (chua dat) = {DEFAULT_AGE}")
    for n, L in d["learners"].items():
        print(f"{n}: age_band={L.get('age_band', DEFAULT_AGE)}{'' if 'age_band' in L else ' (mac dinh)'} bai={L.get('lesson')}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_cli(sys.argv[1:]))
