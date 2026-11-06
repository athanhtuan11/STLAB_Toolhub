"""Giao trinh + ho so hoc sinh theo biet danh con vat (khong ten that, khong sinh trac hoc).
Chi luu: biet danh, bai hien tai, tu dat/chua dat, gio phien. Khong luu hoi thoai/am thanh. Thuan Python, khong goi mang."""
import json, os, re, threading, unicodedata
from datetime import datetime
from pathlib import Path

ALLOWED_NICKNAMES = ["thỏ", "mèo", "gấu", "cá", "chim", "voi", "khỉ", "cún"]
MAX_SESSIONS_PER_DAY = 2
REASON_LIMIT = "Hôm nay con học đủ rồi, mai mình học tiếp nhé!"
HEADING = "## Chỉ dẫn cho AI"


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
            self.lessons[f.stem] = {"instructions": instr, "vocab": vocab}

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
            if review:
                instr += "\n- Words to review first today: " + ", ".join(review) + "."
            return {"allowed": True, "learner": nick, "lesson_id": lid, "instructions": instr, "review": review}

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
