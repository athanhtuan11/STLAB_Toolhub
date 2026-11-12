# Gate "hoc theo Seed nhung lam theo yeu cau khac" + mo nhac (offline, khong goi Gemini). Claude viet, executor KHONG sua.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_detour.py
# Tuan 2026-11-12: "teacher dang ep hoc ... tim cach chay seed bai va cung co the yeu cau khac nhu mo nhac".
import os, re, subprocess, sys, tempfile, shutil
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "live"))
fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

# 1) module nhac
import music  # noqa: E402
d = Path(tempfile.mkdtemp(prefix="stlab-music-"))
try:
    names = ["Baby Shark.mp3", "Twinkle Twinkle Little Star.mp3", "Con cò bé bé.mp3", "ghi-chu.txt"]
    for n in names[:3]:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1.5",
                        "-ac", "1", str(d / n)], check=True)
    (d / names[3]).write_text("khong phai nhac", encoding="utf-8")
    titles = music.list_tracks(d)
    ok(titles == sorted(["Baby Shark", "Twinkle Twinkle Little Star", "Con cò bé bé"], key=str.lower),
       f"list_tracks: chi file nhac, ten khong duoi, sap xep ({titles})")
    def nm(q):
        p = music.find_track(q, d)
        return p.stem if p else None
    ok(nm("baby shark") == "Baby Shark", "find_track 'baby shark'")
    ok(nm("BABY  shark song") == "Baby Shark", "find_track khong phan biet hoa thuong, thua chu")
    ok(nm("con co be be") == "Con cò bé bé", "find_track bo dau tieng Viet")
    ok(nm("twinkle") == "Twinkle Twinkle Little Star", "find_track mot phan ten")
    ok(nm("xyz khung long") is None, "find_track khong khop -> None")
    ok(music.find_track("", d) is not None, "find_track rong -> 1 bai bat ky (be noi 'mo nhac di')")
    pcm = music.decode_pcm(d / "Baby Shark.mp3", 24000)
    ok(isinstance(pcm, (bytes, bytearray)) and abs(len(pcm) - 24000 * 2 * 1.5) < 24000 * 2 * 0.2,
       f"decode_pcm: PCM s16le mono 24 kHz ~1,5 s ({len(pcm) if pcm else 0} byte)")
    ok(music.list_tracks(d / "khong-co") == [], "thu muc khong co -> danh sach rong, khong loi")
finally:
    shutil.rmtree(d, ignore_errors=True)

# 2) cong cu cho Gemini
br = (HERE / "live" / "bridge.py").read_text(encoding="utf-8")
cur = (HERE / "live" / "curriculum.py").read_text(encoding="utf-8")
src = br + cur
for t in ("play_music", "stop_music", "list_music"):
    ok(re.search(r'name\s*=\s*["\']%s["\']' % t, src) is not None, f"khai bao cong cu {t}")
    ok(re.search(r'fc\.name\s*(==|in)[^\n]*%s' % t, br) is not None, f"bridge xu ly {t}")
ok("STLAB_MUSIC_DIR" in br or "STLAB_MUSIC_DIR" in (HERE / "live" / "music.py").read_text(encoding="utf-8"),
   "thu muc nhac cau hinh qua STLAB_MUSIC_DIR (mac dinh server/music)")
ok("[music ended]" in br, "het bai bridge bao Gemini '[music ended]' de co quay lai")
ok(re.search(r"music/", (HERE.parents[2] / ".gitignore").read_text(encoding="utf-8")) is not None
   or (HERE / ".gitignore").exists() and "music" in (HERE / ".gitignore").read_text(encoding="utf-8"),
   ".gitignore loai server/music (nhac khong len git)")

# 3) loi day: Seed la xuong song, yeu cau khac duoc lam theo roi quay lai
pt = (HERE / "prompt-teacher.md").read_text(encoding="utf-8")
ok("DETOUR" in pt, "prompt-teacher.md co muc DETOUR")
sec = pt[pt.find("DETOUR"):pt.find("DETOUR") + 2500] if "DETOUR" in pt else ""
for kw, m in (("play_music", "nhac cong cu play_music"), ("story", "ke chuyen"), ("song", "hat"),
              ("return", "quay lai bai"), ("lesson word", "long tu cua bai vao")):
    ok(kw.lower() in sec.lower(), f"DETOUR {m} ('{kw}')")
ok(re.search(r"never refuse|do not refuse|don't refuse", sec, re.I) is not None, "DETOUR: khong tu choi yeu cau cua be")

# 4) bridge khong con tu dong ep sang tu ke tiep khi be xin viec khac (che do lo trinh)
m_ = re.search(r"wants_switch\([^)]*\)[^\n]*\n((?:[ \t]+[^\n]*\n){0,6})", br)
ok(m_ is None or "DETOUR" in br, "bridge: wants_switch khong ep doi bai (hoac co nhanh DETOUR)")

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
