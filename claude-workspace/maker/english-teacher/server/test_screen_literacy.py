# Gate man chu viet phan MAY CHU (Claude viet 2026-11-28, executor KHONG sua). Spec: firmware/xiaozhi-s3/spec-literacy.md
# Chay: python -m pytest test_screen_literacy.py -q
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "live"))
import screen  # noqa: E402

WORDS = ["cat", "dog", "thank you", "red"]


def test_find_word_basic():
    assert screen.find_lesson_word("Look! A cat. Say cat!", WORDS, {}) == "cat"
    assert screen.find_lesson_word("CAT", WORDS, {}) == "cat"
    assert screen.find_lesson_word("Say thank you to mummy", WORDS, {}) == "thank you"


def test_find_word_whole_word_only():
    assert screen.find_lesson_word("category and dogma", WORDS, {}) is None
    assert screen.find_lesson_word("credit", WORDS, {}) is None
    assert screen.find_lesson_word("", WORDS, {}) is None


def test_find_word_recent_10s():
    import time
    now = time.time()
    assert screen.find_lesson_word("cat", WORDS, {"cat": now - 3}) is None
    assert screen.find_lesson_word("cat", WORDS, {"cat": now - 11}) == "cat"


def test_touch_prompts():
    p = screen.touch_to_prompt({"screen": "word", "word": "cat"}, WORDS, older=False)
    assert "cat" in p and p.startswith("[touch]")
    ok = screen.touch_to_prompt({"screen": "pick", "word": "cat", "correct": True}, WORDS, older=True)
    bad = screen.touch_to_prompt({"screen": "pick", "word": "dog", "correct": False}, WORDS, older=True)
    assert "correct" in ok.lower() and "cat" in ok
    assert ok != bad and "dog" in bad and "wrong" not in bad.lower()     # khong che be
    let = screen.touch_to_prompt({"screen": "letter", "word": "cat"}, WORDS, older=True)
    assert "c" in let and "cat" in let


def test_touch_prompt_rejects_unknown():
    assert screen.touch_to_prompt({"screen": "word", "word": "<script>"}, WORDS, older=False) is None
    assert screen.touch_to_prompt({"screen": "hack"}, WORDS, older=False) is None


def test_bridge_wired():
    s = (HERE / "live" / "bridge.py").read_text(encoding="utf-8")
    for k in ("self.screen.show_word", "self.screen.show_pick", "self.screen.show_letter", "self.screen.show_stickers",
              "notifications/stlab_touch", "find_lesson_word", "touch_to_prompt"):
        assert k in s, k
    c = (HERE / "live" / "curriculum.py").read_text(encoding="utf-8") + s
    assert "show_pick" in c and "show_letter" in c
