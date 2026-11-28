"""Man tuong tac chu viet Cu Bong: ham thuan cho cau noi (khong I/O). Spec: firmware/xiaozhi-s3/spec-literacy.md muc 0 + 2."""
import re
import time

RECENT_S = 10.0
WORD_RE = re.compile(r"^[a-z][a-z \-']{0,30}$")
SCREENS = ("word", "pick", "letter", "sticker")


def clean_word(w):
    """Chuan hoa 1 tu gui xuong bo: chu thuong a-z, cach, '-', '''; sai dang -> None."""
    if not isinstance(w, str):
        return None
    w = " ".join(w.lower().split())
    return w if WORD_RE.match(w) else None


def find_lesson_word(text, words, recent, now=None):
    """Tu cua buoi xuat hien SOM NHAT trong text (khop nguyen tu, khong phan biet hoa thuong, cum 2 tu OK),
    bo tu da hien trong RECENT_S giay (recent: word -> epoch). Khong co -> None."""
    if not text or not words:
        return None
    now = time.time() if now is None else now
    low = " ".join(text.lower().split())
    best, best_pos = None, None
    for w in words:
        w = clean_word(w)
        if not w:
            continue
        t = (recent or {}).get(w)
        if t is not None and now - t < RECENT_S:
            continue
        m = re.search(r"(?<![a-z'\-])" + re.escape(w) + r"(?![a-z'\-])", low)
        if m and (best_pos is None or m.start() < best_pos or (m.start() == best_pos and len(w) > len(best))):
            best, best_pos = w, m.start()
    return best


def touch_to_prompt(params, word_list, older):
    """Cau chen cho Gemini khi be cham man; None neu tham so la/khong thuoc tu cua buoi."""
    if not isinstance(params, dict):
        return None
    scr = params.get("screen")
    if scr not in SCREENS:
        return None
    word = clean_word(params.get("word"))
    allowed = {clean_word(w) for w in (word_list or [])}
    if not word or word not in allowed:
        return None
    if scr == "word":
        return f"[touch] The child tapped the card '{word}'. Say '{word}' again slowly, once."
    if scr == "pick":
        if params.get("correct") is True:
            return f"[touch] The child chose '{word}' - correct! Praise in one short sentence."
        return (f"[touch] The child chose '{word}' - not this one. Give a kind hint in one short sentence "
                "and let the child try the other card.")
    if scr == "letter":
        return (f"[touch] The child tapped the first letter '{word[0]}' of '{word}'. "
                f"Say the letter sound of '{word[0]}', then say '{word}' once.")
    return f"[touch] The child tapped the sticker '{word}'. Say '{word}' once, cheerfully."
