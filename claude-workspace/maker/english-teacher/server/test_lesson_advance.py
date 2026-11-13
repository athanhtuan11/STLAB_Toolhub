# Gate chuyen bai theo tu be that su noi (2026-11-13). Chay: python -m pytest test_lesson_advance.py -q
import json
import sys
import tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
sys.path.insert(0, str(H / "live"))
from curriculum import Curriculum  # noqa: E402
from intent import words_said  # noqa: E402

FAM = ["mummy", "daddy", "baby", "grandma"]


def make():
    data = Path(tempfile.mkdtemp(prefix="stlab-adv-")) / "learners.json"
    cur = Curriculum(data, H.parent / "lessons-seed")
    # dua be den bai s1-u2 (taught = het s1-u1)
    cur.start("kay")
    d = json.loads(data.read_text(encoding="utf-8"))
    L = d["learners"]["kay"]
    L["taught"] = ["hello", "bye-bye", "yes", "no", "thank you"]
    L["cur_new"] = ["mummy"]
    L["cur_from_mark"] = False
    data.write_text(json.dumps(d), encoding="utf-8")
    return cur, data


def lesson_of(data):
    return json.loads(data.read_text(encoding="utf-8"))["learners"]["kay"]["lesson"]


def test_long_session_without_marks_stays():
    cur, data = make()
    assert cur.finish("kay", 627, 9)["next_lesson"] == "s1-u2-my-family"
    assert lesson_of(data) == "s1-u2-my-family"


def test_all_marked_advances():
    cur, data = make()
    for w in FAM:
        cur.mark("kay", w, True)
    assert cur.finish("kay", 627, 9)["next_lesson"] == "s1-u3-colours"


def test_words_said():
    assert words_said("Daddy!", FAM) == ["daddy"]
    assert words_said("dạ không ạ", FAM) == []
    assert words_said("police officers", ["police officer"]) == ["police officer"]
