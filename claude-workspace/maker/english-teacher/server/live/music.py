"""Mo nhac tu thu muc tren may chu (Cu Bong: be xin 'mo nhac', 'hat bai Baby Shark').
Khong tai nhac tu mang; chi phat file Tuan tu chep vao STLAB_MUSIC_DIR (mac dinh server/music)."""
import os
import random
import re
import subprocess
import unicodedata
from pathlib import Path

MUSIC_DIR = Path(os.environ.get("STLAB_MUSIC_DIR") or (Path(__file__).resolve().parent.parent / "music"))
EXTS = {".mp3", ".m4a", ".ogg", ".wav", ".flac"}
MAX_SECONDS = 360                      # bai dai hon chi phat 6 phut dau
STOP_WORDS = {"song", "songs", "music", "play", "the", "a", "bai", "nhac", "hat", "mo", "cho", "con", "nghe", "di", "nhe",
              "ca", "khuc", "ban", "bai hat"}


def _fold(s):
    s = unicodedata.normalize("NFD", str(s).replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _files(folder):
    try:
        p = Path(folder)
        fs = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in EXTS]
    except OSError:
        return []
    return sorted(fs, key=lambda f: f.stem.lower())


def list_tracks(folder=None):
    return [f.stem for f in _files(folder or MUSIC_DIR)]


def find_track(query, folder=None):
    fs = _files(folder or MUSIC_DIR)
    if not fs:
        return None
    toks = [t for t in _fold(query or "").split() if t not in STOP_WORDS]
    if not toks:
        return random.choice(fs)
    q = " ".join(toks)
    best, best_score = None, 0.0
    for f in fs:
        name = _fold(f.stem)
        if q == name:
            return f
        if q in name:
            score = 100 + len(q) / max(len(name), 1)
        else:
            words = set(name.split())
            hit = sum(1 for t in toks if t in words or t in name)
            if hit < len(toks):
                continue
            score = 50 + hit
        if score > best_score:
            best, best_score = f, score
    return best


def decode_pcm(path, rate, max_seconds=MAX_SECONDS):
    """ffmpeg -> PCM s16le mono `rate` Hz (toi da max_seconds giay dau)."""
    cmd = ["ffmpeg", "-loglevel", "error", "-nostdin", "-i", str(path), "-t", str(max_seconds),
           "-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", str(int(rate)), "-"]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("ffmpeg: " + r.stderr.decode("utf-8", "replace")[:200])
    return r.stdout
