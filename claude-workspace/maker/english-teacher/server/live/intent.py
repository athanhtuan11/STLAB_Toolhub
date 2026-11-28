"""Y dinh thuan tu transcript (2026-11-13): lenh am luong + xin nhac. Khong mang, de test."""
import re
import unicodedata


def norm_words(s):
    s = unicodedata.normalize("NFD", (s or "").lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def _has(t, phrase):
    """phrase (da bo dau) la day tu lien tiep trong t (chuoi ' a b c ')."""
    return f" {phrase} " in t


_MAX = ("toi da", "het co", "lon nhat", "to nhat", "max", "maximum")
_UP = ("to len", "lon len", "mo to", "mo lon", "to nua", "lon nua", "tang am luong", "tang volume", "noi to", "noi lon")
_DOWN = ("nho lai", "nho xuong", "be lai", "giam am luong", "giam volume", "noi nho", "nho nua", "nho di")
_VOLISH = ("to", "lon", "nho", "am luong", "volume", "toi da", "het co", "max", "maximum", "be")


def parse_volume_intent(text):
    """-> ("set", 100) | ("delta", +20) | ("delta", -20) | None. Chu 'mo' mot minh khong phai lenh."""
    t = " " + " ".join(norm_words(text)) + " "
    if t.strip() == "":
        return None
    if not any(_has(t, w) for w in _VOLISH):
        return None
    if any(_has(t, p) for p in _MAX):
        return ("set", 100)
    if any(_has(t, p) for p in _DOWN):
        return ("delta", -20)
    if any(_has(t, p) for p in _UP):
        return ("delta", 20)
    return None


_MUSIC_WORDS = ("nhac", "hat", "bai", "song", "music", "sing", "nghe")


def music_requested(texts, titles):
    """True neu transcript (danh sach doan) co tu xin nhac hoac tu trong ten bai. Lenh am luong -> False."""
    joined = " ".join(x for x in texts if x)
    words = norm_words(joined)
    if not words:
        return False
    if parse_volume_intent(joined) is not None:
        return False
    if any(w in _MUSIC_WORDS for w in words):
        return True
    ws = set(words)
    for ti in titles or []:
        for w in norm_words(ti):
            if len(w) >= 4 and w in ws:
                return True
    return False


def words_said(text, vocab):
    """Tu vung (co the la tu ghep) xuat hien trong loi be noi; khong phan biet hoa thuong/dau cau, chap nhan so nhieu (s/es)."""
    t = " " + " ".join(norm_words(text)) + " "
    out = []
    for w in vocab or []:
        k = " ".join(norm_words(w))
        if k and w not in out and any(f" {k}{suf} " in t for suf in ("", "s", "es")):
            out.append(w)
    return out


# Khen (2026-11-28, mat Cu Bong tren man): co noi cau khen -> bridge gui {"type":"llm","emotion":"happy"} -> bo hien mat Khen 2,5 s
_PRAISE = ("good job", "great job", "well done", "excellent", "awesome", "amazing", "perfect", "wonderful", "fantastic",
           "bravo", "yay", "hooray", "high five", "you did it", "very good", "so good", "good boy", "good girl",
           "gioi qua", "gioi lam", "gioi ghe", "gioi thiet", "con gioi", "tuyet voi", "tuyet qua", "hoan ho", "xuat sac",
           "dung roi", "chinh xac")


def praise_said(text):
    """Doan loi co (transcript) co cau khen khong."""
    t = " " + " ".join(norm_words(text)) + " "
    return any(_has(t, p) for p in _PRAISE)
