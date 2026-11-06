# Gate nhan dien giong TAI MAY (Claude viet, executor KHONG sua). Khong goi Gemini; can mang de tao giong thu bang Edge TTS.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_voiceid.py
# Module: server/live/voiceid.py, lop VoiceID(store_dir, threshold=None). Mo hinh tai bang setup-voiceid.ps1 vao server/models/ (khong git).
# Tuan dong y 2026-11-06 (bo cua be). Chi luu DAC TRUNG giong (embedding), khong luu am thanh; xoa duoc.
import asyncio, json, os, subprocess, sys, tempfile, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H / "live"))
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


async def pcm(text, voice, rate="+0%"):
    d = Path(tempfile.mkdtemp(prefix="stlab-vid-")); m, r = d / "a.mp3", d / "a.raw"
    for k in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(m)); break
        except Exception:
            await asyncio.sleep(5)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(m), "-ac", "1", "-ar", "16000", "-f", "s16le", str(r)], check=True)
    b = r.read_bytes(); m.unlink(); r.unlink(); d.rmdir()
    return b


from voiceid import VoiceID  # noqa: E402

store = Path(tempfile.mkdtemp(prefix="stlab-vp-"))
vid = VoiceID(store)
A, B, C = "vi-VN-HoaiMyNeural", "vi-VN-NamMinhNeural", "en-US-AnaNeural"   # "be" A, "be" B, nguoi la C
enroll = ["Con là bạn Thỏ.", "Red. Red apple.", "Con thích màu xanh."]
test = ["Blue sky, blue.", "Cô ơi con muốn học số."]


async def main():
    for t in enroll:
        vid.enroll("thỏ", await pcm(t, A))
        vid.enroll("gấu", await pcm(t, B))
    ok(sorted(vid.list()) == ["gấu", "thỏ"], f"da ghi 2 ho so giong ({vid.list()})")
    files = [p.name for p in store.rglob("*") if p.is_file()]
    ok(files and not any(p.endswith((".wav", ".pcm", ".mp3", ".raw", ".opus")) for p in files), f"chi luu dac trung, khong luu am thanh ({files})")
    t0 = time.time(); n = 0; right = 0
    for t in test:
        for voice, want in ((A, "thỏ"), (B, "gấu")):
            nick, score = vid.identify(await pcm(t, voice, rate="+5%")); n += 1
            print(f"  {want}: nhan={nick} diem={score:.3f}")
            right += nick == want
    ok(right == n, f"nhan dung {right}/{n} cau moi cua 2 'be'")
    for t in test:
        nick, score = vid.identify(await pcm(t, C))
        print(f"  nguoi la: nhan={nick} diem={score:.3f}")
        ok(nick is None, "nguoi la (giong chua ghi) -> None")
    one = await pcm("Xin chào cô.", A)
    t1 = time.time(); vid.identify(one); dt = time.time() - t1
    ok(dt < 0.5, f"nhan 1 cau ~1 s trong < 0,5 s CPU ({dt:.2f} s)")
    vid.delete("thỏ")
    ok(vid.list() == ["gấu"] and not any("thỏ" in p.name or "tho" in p.name for p in store.rglob("*") if p.is_file()), "xoa ho so giong 'tho' sach")
    print("\n%s test_voiceid (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
