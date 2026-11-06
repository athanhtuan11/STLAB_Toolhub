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
            last = list(L.get("last_activities", []))
            vocab = self.lessons[lid]["vocab"]
            if vocab and all(w in L["passed"] for w in vocab) and lid == self.order[-1]:
                # da hoc het bai cuoi -> che do on tu do (khong con tu moi)
                learned = [w for i in self.order for w in self.lessons[i]["vocab"]]
                instr += "\n" + self.review_plan(learned)
                self._save(d)
                return {"allowed": True, "learner": nick, "lesson_id": lid, "instructions": instr, "review": [],
                        "mode": "review"}
            if review:
                instr += "\n- Words to review first today: " + ", ".join(review) + "."
            plan, act = self.today_plan(lid, review, last)
            L["last_activities"] = (last + [act])[-3:]
            self._save(d)
            instr += "\n" + plan
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
        return lid, self.lessons[lid]["instructions"] + "\n" + self.today_plan(lid)[0]

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
