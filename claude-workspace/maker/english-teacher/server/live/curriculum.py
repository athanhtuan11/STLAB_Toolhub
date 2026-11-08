"""Giao trinh + ho so hoc sinh theo biet danh con vat (khong ten that, khong sinh trac hoc).
Chi luu: biet danh, bai hien tai, tu dat/chua dat, gio phien. Khong luu hoi thoai/am thanh. Thuan Python, khong goi mang."""
import json, os, random, re, threading, unicodedata
from datetime import datetime
from pathlib import Path

ALLOWED_NICKNAMES = ["thỏ", "mèo", "gấu", "cá", "chim", "voi", "khỉ", "cún",
                     "sóc", "vịt", "ếch", "rùa", "ong", "bướm", "hổ", "gà", "heo", "nai", "cú",
                     "kay"]   # 2026-11-08 Tuan: be dang thu ten "Kay" (con Tuan, Tuan dong y)
# cach nhan dang hay nghe nham -> quy ve biet danh chuan
NICK_ALIASES = {"kai": "kay", "key": "kay", "kei": "kay", "khay": "kay"}
MAX_SESSIONS_PER_DAY = None   # 2026-11-08 Tuan: 'khong gioi han buoi hoc' (truoc: 2 buoi/ngay)
# 2026-11-07: buoi chi DUOC TINH khi >= MIN_SESSION_S giay hoac be noi >= MIN_TURNS luot (lan bam thu ngan khong tinh -> khong bi tu choi 'hoc du roi' vo ly, khong day tuan hoc len)
MIN_SESSION_S, MIN_TURNS = 120, 3
REASON_LIMIT = "Hôm nay con học đủ rồi, mai mình học tiếp nhé!"
HEADING = "## Chỉ dẫn cho AI"
ACTIVITIES = ("repeat-after-me", "quiz", "rhyme-chant", "tiny-story", "guessing-game")   # bo touch-game (2026-11-08)


DEFAULT_AGE = 2   # chua dat -> doi tuong tre nhat (be 2 tuoi)
# 2026-11-06 Tuan: "phat am sai thi phai sua cho be" -> sua NHE kieu recast (khen co gang, noi lai mau dung cham, nhan am kho,
# moi thu lai), khong noi "sai", toi da 2 lan/tu roi khen va chuyen.
# Tuan chot (2026-11-06): "phat am sai thi sua lai cho be va VAN KHEN roi TIEP TUC; be con nho, tiep xuc dan se quen".
# -> recast: khen + noi lai mau dung 1 lan (cham, ro) + hoc tiep. KHONG bat be noi lai.
# 2026-11-08 Tuan: "be nho khong biet hanh dong, cu doc va bat be lap lai" -> doc mau + be noi theo, toi da 2 lan/tu.
PRONUNCIATION = ("Pronunciation: listen to HOW the child says the English word. If it is off (wrong or missing sound, "
                 "e.g. 'ed' for 'red', 'ello' for 'hello'), praise the try, say the correct word ONCE more slowly and clearly, "
                 "and invite the child to say it once more ('Con nói theo cô: Red!'); after at most 2 tries praise and go on. "
                 "Do NOT grade, do NOT say 'wrong' / 'sai'. "
                 "Call mark_word correct=true only when it was close to right; otherwise correct=false (the word comes back later). "
                 "You have NO camera: never say you see the child; praise effort in general ('Con giỏi quá!') or a sound you heard.")
FLEXIBLE = ("FLEXIBLE: the roadmap is the DEFAULT plan, not a fence. If the child or an adult talks about something else "
            "(child-safe), follow it briefly first (you may add ONE related simple English word); if they ask for another topic "
            "(e.g. 'dạy con về hoa') call change_topic with the topic and 1-3 simple English words, then teach it one word at a "
            "time. Never force the child back to the lesson. Flexibility never makes turns longer: every turn stays at most "
            "3 short pieces.")
# 2026-11-07 bao cao cu-bong-cach-day-tot-hon.md (a)(b): 8 quy tac + khung buoi
TODDLER_MODE = ("Toddler mode (ages 2-3), session frame about 3-4 minutes, READ AND REPEAT (Tuan 2026-11-08): "
                "(1) very short greeting, (2) review words first, one at a time IN THE GIVEN ORDER: say the word slowly, "
                "'Con nói theo cô: <word>!', wait, praise, (3) the new word the same way, a few times, "
                "(4) you never end the session yourself: the server decides; afterwards keep reviewing the words the same way. "
                "NO ACTIONS: never ask the child to clap, wave, touch, show fingers, point or look for things - small children "
                "cannot follow actions; only listen and say the word. "
                "SINGLE WORDS (Tuan 2026-11-08): for ages 2-3 say English as SINGLE WORDS only, one word at a time "
                "(e.g. 'One!', 'One finger!' is too long -> 'One!'), never English sentences or phrases; the Vietnamese around "
                "it stays very short (e.g. 'Số một là One! Con nói theo cô: One!'). "
                "Rules: at most 2 short sentences per turn; answer what the child said FIRST, teach after; ONE request per "
                "turn (say the word after you, no open questions); after inviting STOP and wait; teach only the goal words. "
                + PRONUNCIATION + " Warm, slow, sing-song voice; Vietnamese support is fine.")
OLDER_MODE = ("Age 4-5, session frame about 5 minutes: opening, 2 new words inside a short story, a choice riddle "
              "('Hello or goodbye?', 'Happy or sad?'), one 2-word phrase, then keep playing; never end the session yourself. "
              "Rules: English sentences at most 6 words, at most 2 sentences per turn (+ at most 1 short Vietnamese sentence); "
              "answer what the child said FIRST, teach after; ONE request per turn; after a question STOP and wait; say "
              "'Đến lượt con!' before inviting the child to speak; no drilling (a new word at most 2 times per turn). "
              + PRONUNCIATION + " If the child wants, you may add one simple mouth tip in Vietnamese "
              "(e.g. 'uốn lưỡi', 'chu môi', 'cắn nhẹ môi dưới' for f/v).")


def normalize(nick):
    s = re.sub(r"[^\w\s]", " ", str(nick or "").lower())
    words = [w for w in s.split() if w not in ("bạn", "ban")]
    n = " ".join(words)
    return NICK_ALIASES.get(n, n)


def _fold(t):
    t = unicodedata.normalize("NFD", str(t or "").lower()).replace("đ", "d")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return " ".join("".join(c if c.isalnum() else " " for c in t).split())


_SWITCH_RE = (r"\bdoi (bai|tro|cai)\b", r"\b(bai|tro|cai) khac\b")


def wants_switch(text):
    """Be xin doi bai/tro ('doi bai di co', 'hoc bai khac', 'choi tro khac'). Cau thuong, tu tieng Anh -> False."""
    t = _fold(text)
    if not t:
        return False
    return any(re.search(r, t) for r in _SWITCH_RE)


def find_nickname(text):
    """Chi nhan cum 'ban <ten>' (khong dau/co dau) voi ten trong ALLOWED_NICKNAMES; 'con meo', ten nguoi -> None."""
    by_fold = {_fold(n): n for n in ALLOWED_NICKNAMES}
    by_fold.update({_fold(a): n for a, n in NICK_ALIASES.items()})
    w = _fold(text).split()
    for i in range(len(w) - 1):
        if w[i] == "ban" and w[i + 1] in by_fold:
            return by_fold[w[i + 1]]
    return None


class Curriculum:
    def __init__(self, data_path, lessons_dir, now=datetime.now):
        self.path = Path(data_path)
        self.now = now
        self.free_flag = None   # duong dan file free-lesson.on (bridge dat); co file -> bai tu do do Gemini tu len
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
        self.rm_young, self.rm_old = self._parse_roadmap(Path(lessons_dir) / "ROADMAP.md")

    WEEK_RE = re.compile(r"^Week (\d+): (\S+) \| new: (.*?) \| review: (.*?) \| daily: (.*?) \| song: (\S+)\s*$")

    def _parse_roadmap(self, path):
        """Doc 2 bang tuan tu ROADMAP.md: (2-3 tuoi, 4-5 tuoi). Khong co file -> ([], [])."""
        try:
            txt = path.read_text(encoding="utf-8")
        except OSError:
            return [], []
        young, old = [], []
        target = None
        split = lambda v: [x.strip().lower() for x in v.split(",") if x.strip() and x.strip() != "-"]
        for line in txt.splitlines():
            if line.startswith("## "):
                h = line.replace("–", "-")
                if "Lịch tuần" in h:
                    target = young if re.search(r"2\s*-\s*3", h) else old
                else:
                    target = None
                continue
            m = self.WEEK_RE.match(line)
            if m and target is not None:
                lid, song = m.group(2), m.group(6)
                is_review = lid == "review"
                if is_review or lid not in self.lessons:
                    lid = song
                if lid not in self.lessons:
                    continue
                target.append({"week": int(m.group(1)), "lesson_id": lid, "new": split(m.group(3)),
                               "review": split(m.group(4)), "daily": split(m.group(5)), "song": song,
                               "review_week": is_review})
        return young, old

    def roadmap(self, age_band):
        return [dict(r) for r in (self.rm_young if int(age_band) <= 3 else self.rm_old)]

    def roadmap_week(self, age_band, n):
        rm = self.rm_young if int(age_band) <= 3 else self.rm_old
        if not rm:
            return None
        return dict(rm[(max(int(n), 1) - 1) % len(rm)])

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
                if "devices" in d and not isinstance(d["devices"], dict):
                    d["devices"] = {}
                return d
        except (OSError, ValueError):
            pass
        return {"version": 1, "learners": {}}

    def _save(self, d):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, self.path)

    def _prof(self, d, nickname, device, create=False):
        """Ho so theo biet danh (learners) hoac, khong biet danh, theo MAY (devices). Tra (L, key, la_biet_danh) hoac None."""
        nick = normalize(nickname)
        if nick in ALLOWED_NICKNAMES:
            tbl, key, is_nick = d["learners"], nick, True
        elif device and not nick:
            tbl, key, is_nick = d.setdefault("devices", {}), str(device), False
        else:
            return None
        L = tbl.get(key)
        if L is None:
            if not create:
                return None
            L = tbl[key] = {}
        L.setdefault("lesson", self.order[0])
        for k in ("passed", "failed", "sessions"):
            L.setdefault(k, [])
        return L, key, is_nick

    def start(self, nickname, device=None):
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device, create=True)
            if p is None:
                return {"allowed": False, "nicknames": list(ALLOWED_NICKNAMES),
                        "reason": "Con chọn một biệt danh con vật trong danh sách nhé, không dùng tên thật."}
            L, key, is_nick = p
            learner = key if is_nick else "device"
            now = self.now()
            today = now.date().isoformat()
            if MAX_SESSIONS_PER_DAY and sum(1 for s in L.get("counted", []) if s[:10] == today) >= MAX_SESSIONS_PER_DAY:
                return {"allowed": False, "reason": REASON_LIMIT}
            L["sessions"].append(now.isoformat(timespec="minutes"))
            L["cur"], L["cur_counted"] = now.isoformat(timespec="minutes"), False
            L["sessions"] = L["sessions"][-50:]
            L["switch_n"] = 0
            age = self._age(L)
            if self.roadmap(age):
                return self._start_roadmap(d, L, learner, now, age)
            self._save(d)
            lid = L["lesson"]
            review = [w for w in L["failed"] if w in self.lessons[lid]["vocab"] and w not in L["passed"]]
            instr = self.lessons[lid]["instructions"]
            toddler = age <= 3
            last = list(L.get("last_activities", []))
            vocab = self.lessons[lid]["vocab"]
            if vocab and all(w in L["passed"] for w in vocab) and lid == self.order[-1]:
                # da hoc het bai cuoi -> che do on tu do (khong con tu moi)
                learned = [w for i in self.order for w in self.lessons[i]["vocab"]]
                instr += "\n" + self.review_plan(learned)
                instr += "\n" + (TODDLER_MODE if toddler else OLDER_MODE)
                self._save(d)
                return {"allowed": True, "learner": learner, "lesson_id": lid, "instructions": instr, "review": [],
                        "mode": "review"}
            if review:
                instr += "\n- Words to review first today: " + ", ".join(review) + "."
            plan, act = self.today_plan(lid, review, last)
            L["last_activities"] = (last + [act])[-3:]
            self._save(d)
            instr += "\n" + plan
            instr += "\n" + FLEXIBLE
            instr += "\n" + (TODDLER_MODE if toddler else OLDER_MODE)
            return {"allowed": True, "learner": learner, "lesson_id": lid, "instructions": instr, "review": review}

    @staticmethod
    def _age(L):
        try:
            a = int(L.get("age_band", DEFAULT_AGE))
        except (TypeError, ValueError):
            a = DEFAULT_AGE
        return a if 2 <= a <= 5 else DEFAULT_AGE

    def word_sequence(self, age_band):
        """Cot 'new' cua lich tuan noi lien theo thu tu, bo trung lap = thu tu day tung tu."""
        seq = []
        for r in self.roadmap(age_band):
            for w in r["new"]:
                if w not in seq:
                    seq.append(w)
        return seq

    def _word_row(self, age, word):
        """(tuan 1-based, lesson_id) cua tuan lich co chua tu nay; khong thay -> tuan dau."""
        rm = self.roadmap(age)
        for r in rm:
            if word in r["new"]:
                return r["week"], r["lesson_id"]
        return (rm[0]["week"], rm[0]["lesson_id"]) if rm else (1, self.order[0])

    def _migrate(self, L, age):
        """Ho so cu (chua co 'taught', tien do theo tuan lich) -> con tro tu: tu da dat + tu cua cac tuan truoc."""
        if "taught" in L:
            return
        seq = self.word_sequence(age)
        prev = set()
        for r in self.roadmap(age)[:max(int(L.get("week", 1)), 1) - 1]:
            prev.update(r["new"])
        passed = set(L.get("passed", []))
        L["taught"] = [w for w in seq if w in passed or w in prev]

    def _roll_week(self, L):
        iso = "%d-W%02d" % self.now().isocalendar()[:2]
        if L.get("nw_iso") != iso:
            L["nw_iso"], L["nw_n"] = iso, 0

    def _teach(self, L, words):
        """Them tu vao 'taught' (khong trung), dem vao han muc tuan."""
        self._migrate(L, self._age(L))
        self._roll_week(L)
        for w in words:
            if w not in L["taught"]:
                L["taught"].append(w)
                L["nw_n"] = int(L.get("nw_n", 0)) + 1

    def _next_new(self, L, age):
        """Tu moi: tu dau trong word_sequence chua day, theo han muc buoi + tuan."""
        self._migrate(L, age)
        self._roll_week(L)
        per_session, per_week = (1, 2) if age <= 3 else (2, 4)
        room = min(per_session, per_week - int(L.get("nw_n", 0)))
        rest = [w for w in self.word_sequence(age) if w not in L["taught"]]
        return rest[:max(room, 0)]

    def _pick_review(self, L, new):
        """Toi da 2 tu on: failed chua passed -> tu day gan nhat -> 1 tu cu hon (cach quang)."""
        taught = list(L.get("taught", []))
        res = []

        def add(w):
            if w not in res and w not in new and len(res) < 2:
                res.append(w)
        for w in L.get("failed", []):
            if w in taught and w not in L.get("passed", []):
                add(w)
        rec = [w for w in reversed(taught) if w not in new]
        for w in rec[:1]:
            add(w)
        ex = [e for e in L.get("extra", []) if isinstance(e, dict) and e.get("word") and e["word"] not in new
              and e["word"] not in res]
        if ex and len(res) < 2:
            e = min(ex, key=lambda x: int(x.get("rv", 0)))      # tu chu de it duoc on nhat; toi da 1 tu extra/buoi
            e["rv"] = int(e.get("rv", 0)) + 1
            add(e["word"])
        for w in rec[3:] + rec[1:3]:
            add(w)
        return res

    def _guide_new(self, new, review, dropped=()):
        if new:
            s = (f"THIS SESSION'S ONLY NEW WORD(S): {', '.join(new)}. This is the default plan for today: even if the lesson above "
                 "lists more words, teach just these, one at a time. Review words only briefly, one at a time. "
                 "Each of your turns has at most 3 short pieces in total (e.g. 'Con giỏi quá! One! Đến lượt con!').")
        else:
            s = ("There is NO new roadmap word in this session. Default plan: only play and gently review these words, "
                 f"one at a time: {', '.join(review) or 'none'}. Keep each turn to at most 3 short pieces.")
        if dropped:
            s += f" Do NOT go back to the word(s) the child just skipped: {', '.join(dropped)}."
        return s + " " + FLEXIBLE

    def _start_free(self, d, L, learner, age):
        """Bai tu do (Tuan 2026-11-08 'mo khoa de Gemini tu len bai hoc'): bat bang file free-lesson.on. Server chi dua
        lich su tu da hoc + goi y lo trinh; Gemini tu chon chu de + 1-3 tu, luu qua change_topic (L['extra']) de on."""
        known = [e["word"] for e in L.get("extra", []) if isinstance(e, dict) and e.get("word")]
        learned = list(dict.fromkeys(L.get("taught", []) + known))
        idea = [w for w in self.word_sequence(age) if w not in L.get("taught", [])][:3]
        L["cur_new"] = []
        self._save(d)
        instr = ("[FREE LESSON] You plan today's lesson yourself - you are free to choose. "
                 f"The child is about {age} years old. Words the child already met: {', '.join(learned[-12:]) or 'none'}. "
                 f"Roadmap idea (only a suggestion, use it or pick something better): {', '.join(idea) or 'free choice'}. "
                 "Design the whole lesson for this age as you think best: topic, how many words, games, songs, stories, pace "
                 "and sentence length; vary between sessions and weave in known words for review. To save new words for later "
                 "review, call change_topic with your topic and words (up to 3 per call). "
                 "Hints from Tuan (not rules): ages 2-3 learn well by hearing a word and saying it after you, they cannot "
                 "follow actions yet; count numbers in order from one. Stay child-safe; never end the session yourself.\n")
        # 2026-11-08 Tuan 'khong rang buoc': bai tu do KHONG gan TODDLER_MODE/OLDER_MODE (khung buoi + gioi han cau)
        return {"allowed": True, "learner": learner, "lesson_id": L.get("lesson"), "instructions": instr, "review": [],
                "week": L.get("week"), "new": [], "daily": [], "song": None, "mode": "free"}

    def _start_roadmap(self, d, L, learner, now, age):
        """Tien do = CON TRO TU (L['taught']), khong theo tuan lich: khoi dong lai hoc tiep, bam thu ngan khong tien/lui."""
        rm = self.roadmap(age)
        self._migrate(L, age)
        if self.free_flag and Path(self.free_flag).exists():
            return self._start_free(d, L, learner, age)
        new = self._next_new(L, age)
        done = not [w for w in self.word_sequence(age) if w not in L["taught"]]
        review = self._pick_review(L, new)
        if new:
            week, lid = self._word_row(age, new[0])
        elif L["taught"]:
            week, lid = self._word_row(age, L["taught"][-1])
        else:
            week, lid = rm[0]["week"], rm[0]["lesson_id"]
        L["cur_new"] = list(new)
        L["week"], L["lesson"] = week, lid
        if "number" in lid:
            # 2026-11-08 Tuan: "hoc 1 toi 5 sao hoc so 3 truoc" -> bai so: on dem tu one theo thu tu roi moi toi so moi
            vocab = self.lessons[lid]["vocab"]
            review = ([v for v in vocab if v in L["taught"] and v not in new]
                      + [x for x in review if x not in vocab])   # giu tu chu de rieng (extra) de on
        w = next((r for r in rm if r["week"] == week), rm[0])
        last = list(L.get("last_activities", []))
        goals = list(dict.fromkeys(review + new))
        instr = self.lessons[lid]["instructions"]
        instr += (f"\nWeek {week}. New words: {', '.join(new) or 'none (review session)'}. Review: {', '.join(review) or 'none'}. "
                  f"Daily English to use all session: {', '.join(w['daily'])} "
                  "(exposure: say them naturally many times).")
        instr += "\n" + self._guide_new(new, review)
        plan = ""
        if done:
            instr += "\n" + self.review_plan(L["taught"])
        else:
            plan, act = self.today_plan(lid, review, last, words=goals, toddler=age <= 3)
            L["last_activities"] = (last + [act])[-3:]
        self._save(d)
        if plan:
            instr += "\n" + plan
        instr += "\n" + (TODDLER_MODE if age <= 3 else OLDER_MODE)
        out = {"allowed": True, "learner": learner, "lesson_id": lid, "instructions": instr, "review": review,
               "week": week, "new": list(new), "daily": w["daily"], "song": w["song"]}
        if done:
            out["mode"] = "review"
        return out

    def switch(self, nickname=None, device=None):
        """Be xin doi bai giua buoi. Lan 1: tu moi hien tai coi nhu da day, sang tu ke tiep (neu con han muc tuan), doi
        hoat dong; khong quay lai tu vua bo. Lan 2+: tro on, khong tu moi. Tra {count,new,review,instructions}."""
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device)
            if p is None:
                return {"count": 0, "new": [], "review": [], "instructions": ""}
            L = p[0]
            age = self._age(L)
            n = int(L.get("switch_n", 0)) + 1
            L["switch_n"] = n
            dropped = list(L.get("cur_new", []))
            self._teach(L, dropped)
            new = self._next_new(L, age) if n == 1 else []
            review = self._pick_review(L, new)
            L["cur_new"] = list(new)
            last = list(L.get("last_activities", []))
            pool = [a for a in ACTIVITIES if a not in last] or list(ACTIVITIES)
            act = random.choice(pool)
            L["last_activities"] = (last + [act])[-3:]
            if new:
                L["week"], L["lesson"] = self._word_row(age, new[0])
            ins = ("The child asked to change what we are doing. Switch right now, warmly, to a different activity "
                   f"(suggested type: {act}); never say anything was wrong. ")
            ins += self._guide_new(new, review, dropped if n == 1 else ())
            if not new:
                ins += (" Offer the child a choice between two toys or two animals to play with, and wait for the answer "
                        "(e.g. 'Cat or dog?').")
            ins += " Keep speaking in the same short toddler style."
            self._save(d)
            return {"count": n, "new": list(new), "review": review, "instructions": ins}

    def review_plan(self, learned):
        words = list(dict.fromkeys(learned))
        random.shuffle(words)
        return ("Review mode: the child has learned every lesson. Have a free, warm chat on a safe topic "
                "(animals, colors, numbers, family, toys) and weave in these learned words at random: "
                + ", ".join(words[:8]) + ". Invent fresh games, short stories or chants. Keep each turn short.")

    def today_plan(self, lid, review=(), last=(), words=None, toddler=False):
        """Muc tieu buoi hoc: tu xao thu tu (tu on len dau), goi y 1 kieu hoat dong khac lan truoc;
        Gemini tu sang tao cach day, khong dung lai <last_activities>. Tra (van ban, nhan hoat dong).
        toddler (2026-11-08 Tuan): giu dung thu tu (so dem tu one), chi doc mau + be noi theo, khong hanh dong."""
        if toddler:
            order = list(words) if words else list(self.lessons[lid]["vocab"])
            title = self.lessons[lid].get("title", lid)
            return (f"Today's words, in EXACTLY this order: {', '.join(order)}. Activity: repeat-after-me only. "
                    "For each word: say it slowly and clearly, then 'Con nói theo cô: <word>!' and wait; praise any try "
                    "(at most 2 tries per word), then the next word in order. No actions, no gestures, no games that need "
                    "the child to move. When the list is done, go through it again from the first word "
                    "(the server ends the session, never you). First, say in Vietnamese what we learn today "
                    f"(\"Hôm nay mình học {title.lower()} nhé\"), then start with '{order[0]}'.", "repeat-after-me")
        vocab = list(words) if words else list(self.lessons[lid]["vocab"])
        rest = [w for w in vocab if w not in review]
        random.shuffle(rest)
        order = [w for w in vocab if w in review] + rest
        pool = [a for a in ACTIVITIES if a not in last] or list(ACTIVITIES)
        act = random.choice(pool)
        title = self.lessons[lid].get("title", lid)
        avoid = ", ".join(last) if last else "none"
        return (f"Today's goal words, in this order: {', '.join(order)}. Suggested activity type: {act}. "
                "These are GOALS, not a script. Frame: short opening ritual -> ONE new word through an action -> a 2-3 sentence "
                "story with a character (Bear or the child's animal) -> a one-line chant with an action each time; then keep "
                "playing or reviewing gently (the server ends the session, never you). Vary the activities and examples "
                "(short English sentences, see the mode limits): a tiny story, a choice game, a made-up chant, a touch-something game. "
                f"Do NOT reuse these from last time: {avoid}. One request per turn, then wait. First, say in Vietnamese what we "
                f"learn today (\"Hôm nay mình học {title.lower()} nhé\"), then teach the first word '{order[0]}' in English.", act)

    @staticmethod
    def _clean_words(words):
        out = []
        for w in words or []:
            w = re.sub(r"\s+", " ", re.sub(r"[^a-z ]", "", str(w or "").lower())).strip()
            if w and len(w) <= 20 and w not in out:
                out.append(w)
            if len(out) >= 3:
                break
        return out

    def set_topic(self, nickname=None, device=None, topic="", words=None):
        """Be/nguoi lon xin chu de khac: luu 1-3 tu vao L['extra'] (on 2 buoi sau), tra chi dan day tung tu mot.
        Con tro lo trinh KHONG doi; khong luu hoi thoai."""
        topic = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", str(topic or ""))).strip()[:40]
        ws = self._clean_words(words)
        if not topic or not ws:
            return {"ok": False, "words": [], "instructions": ""}
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device)
            if p is None:
                return {"ok": False, "words": [], "instructions": ""}
            L = p[0]
            ex = [e for e in L.get("extra", []) if isinstance(e, dict) and e.get("word") not in ws]
            for i, w in enumerate(ws):
                ex.append({"word": w, "topic": topic, "rv": 0} if i == 0 else {"word": w, "rv": 0})
            L["extra"] = ex[-30:]
            age = self._age(L)
            self._save(d)
        ins = (f"[topic] The child (or an adult) asked for a new topic: '{topic}'. Pause the roadmap for the rest of this session "
               f"and happily follow this topic instead. Words: {', '.join(ws)}. Teach them ONE AT A TIME (one at a time, never "
               "two in one turn): say the word slowly, then the child says it after you ('Con nói theo cô: ...!'); no actions or gestures. "
               "Keep everything child-safe. Do not call mark_word for these words. ")
        ins += TODDLER_MODE if age <= 3 else OLDER_MODE
        return {"ok": True, "words": ws, "instructions": ins}

    def anonymous_lesson(self):
        """Ket noi khong co biet danh: chon NGAU NHIEN 1 bai (khong ghi ho so). Tra (lesson_id, instructions)."""
        lid = random.choice(self.order)
        return lid, self.lessons[lid]["instructions"] + "\n" + self.today_plan(lid)[0] + "\n" + TODDLER_MODE

    def _known_words(self):
        k = set()
        for v in self.lessons.values():
            k.update(v["vocab"])
        for r in self.rm_young + self.rm_old:
            k.update(r["new"] + r["review"] + r["daily"])
        return k

    def mark(self, nickname, word, correct, device=None):
        w = str(word or "").strip().lower()
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device)
            if p is None or w not in self._known_words():
                return {"ok": False}
            L = p[0]
            if correct:
                if w not in L["passed"]:
                    L["passed"].append(w)
                L["last_words"] = [x for x in L.get("last_words", []) if x != w][-4:] + [w]   # chi tu vung, toi da 5
                L["failed"] = [x for x in L["failed"] if x != w]
            else:
                if w not in L["passed"] and w not in L["failed"]:
                    L["failed"].append(w)
            if w in L.get("cur_new", []):
                self._teach(L, [w])       # dung hay sai deu tinh la da day (sai thi van o failed de on)
            self._save(d)
            return {"ok": True}

    def last_words(self, nickname):
        """Vai tu be dat gan nhat (chi tu vung) - de nhac lai dau buoi sau."""
        L = self._load()["learners"].get(normalize(nickname)) or {}
        return list(L.get("last_words", []))[-5:]

    def _count(self, L):
        """Tinh buoi hien tai (1 lan/buoi): vao gioi han ngay + dem tuan hoc."""
        if L.get("cur_counted"):
            return
        L.setdefault("counted", []).append(L.get("cur") or self.now().isoformat(timespec="minutes"))
        L["counted"] = L["counted"][-50:]
        L["wk_n"] = int(L.get("wk_n", 0)) + 1
        L["cur_counted"] = True

    @staticmethod
    def _meaningful(seconds, turns):
        return seconds is None or seconds >= MIN_SESSION_S or (turns or 0) >= MIN_TURNS

    def end_session(self, nickname, seconds, turns, device=None):
        """Cau noi goi khi het ket noi: buoi du dai/du luot moi duoc tinh (va moi tinh tu moi cua buoi la da day)."""
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device)
            if p is None:
                return {"counted": False}
            L = p[0]
            ok = self._meaningful(seconds, turns)
            if ok:
                self._count(L)
                if self.roadmap(self._age(L)):
                    self._teach(L, L.get("cur_new", []))
                self._save(d)
            return {"counted": ok}

    def finish(self, nickname, seconds=None, turns=None, device=None):
        with self.lock:
            d = self._load()
            p = self._prof(d, nickname, device)
            if p is None:
                return {"next_lesson": self.order[0]}
            L = p[0]
            age = self._age(L)
            if self._meaningful(seconds, turns):
                self._count(L)
                if self.roadmap(age):
                    self._teach(L, L.get("cur_new", []))
            if self.roadmap(age):
                self._migrate(L, age)
                rest = [w for w in self.word_sequence(age) if w not in L["taught"]]
                week, lid = self._word_row(age, rest[0] if rest else (L["taught"][-1] if L["taught"] else ""))
                L["week"], L["lesson"] = week, lid
                self._save(d)
                return {"next_lesson": lid, "week": week}
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
        {"name": "change_topic",
         "description": ("Call when the child OR an adult asks to learn or talk about a different topic (e.g. 'dạy con về hoa', "
                         "'học về xe', 'hôm nay học con vật'). Choose 1-3 very simple English words for that topic. "
                         "Do NOT call it for a short off-topic remark; just answer that naturally."),
         "parameters": {"type": "OBJECT",
                        "properties": {"topic": {"type": "STRING", "description": "the requested topic (Vietnamese or English)"},
                                       "words": {"type": "ARRAY", "items": {"type": "STRING"},
                                                 "description": "1-3 simple English words you choose for the topic, e.g. flower"}},
                        "required": ["topic", "words"]}},
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
