# Gate cong am luong GAN MIC (offline, khong goi Gemini). Chay: runtime\.venv\Scripts\python.exe -X utf8 test_vad_near.py
# Nen = giong khac doc lien tuc (gia nhac co loi) thap hon be 15 dB; be = 2 cau chen o giay 9 va 15 (spec ban dau 6 va 13: bo loc can ~3,5 s de nhan nen la giong lien tuc).
import asyncio, os, subprocess, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "live"))
import numpy as np, edge_tts
import vad_gate
from vad_gate import VadGate

SR, FR = 16000, 960
KID_DB, BG_DB = -20.0, -35.0
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


async def tts(text, voice):
    d = Path(tempfile.mkdtemp(prefix="stlab-vn-")); m, r = d / "a.mp3", d / "a.raw"
    await edge_tts.Communicate(text, voice).save(str(m))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(m), "-ac", "1", "-ar", str(SR), "-f", "s16le", str(r)], check=True)
    a = np.frombuffer(r.read_bytes(), dtype=np.int16).astype(np.float32) / 32768.0
    m.unlink(); r.unlink(); d.rmdir()
    return a


def trim(a):
    idx = np.where(np.abs(a) > 0.02)[0]
    return a[idx[0]:idx[-1] + 1] if len(idx) else a


def scale(a, db):
    rms = float(np.sqrt(np.mean(a * a))) + 1e-9
    return a * (10 ** (db / 20) / rms)


def dbfs(a):
    return 20 * np.log10(float(np.sqrt(np.mean(a * a))) + 1e-9)


def run(sig, **kw):
    g = VadGate(str(HERE), log=lambda s: lines.append(s))
    n = len(sig) // FR
    zero = np.zeros(n, bool); passed = np.zeros(n, bool); openrun = 0; maxopen = 0
    pcm16 = (np.clip(sig, -1, 1) * 32767).astype(np.int16)
    for i in range(n):
        ch, _ = g.process(pcm16[i * FR:(i + 1) * FR].tobytes())
        z = not any(b for b in ch[-1])
        zero[i] = z
        if not z:
            passed[i] = True
            for k in range(1, len(ch)):
                if i - k >= 0 and any(ch[-1 - k]):
                    passed[i - k] = True
            openrun += 1; maxopen = max(maxopen, openrun)
        else:
            openrun = 0
    return g, zero, passed, maxopen * FR / SR


def zero_runs(zero):
    runs, s = [], None
    for i, z in enumerate(list(zero) + [False]):
        if z and s is None: s = i
        if not z and s is not None: runs.append((s, i - s)); s = None
    return runs


def fr(t): return int(t * SR / FR)


async def main():
    kid1 = scale(trim(await tts("Con là bạn Thỏ.", "vi-VN-HoaiMyNeural")), KID_DB)
    kid2 = scale(trim(await tts("One.", "en-US-AnaNeural")), KID_DB)
    txt = ("The quick brown fox jumps over the lazy dog while the singer keeps on singing about love and the long road home. " * 6)
    bg = trim(await tts(txt, "en-US-GuyNeural"))
    w = bg[:len(bg) // 512 * 512].reshape(-1, 512)  # bo quang nghi (nhac that khong ngat): giu cua so >= dinh - 35 dB
    lv = 20 * np.log10(np.sqrt((w ** 2).mean(1)) + 1e-9)
    bg = w[lv >= lv.max() - 35].reshape(-1)
    bg = np.tile(bg, int(np.ceil(20 * SR / len(bg)) + 1))[:20 * SR]
    print(f"[dB] be: Thỏ {dbfs(kid1):.1f}, One {dbfs(kid2):.1f}; nen {BG_DB:.1f} dBFS")

    # A: nen + 2 cau be
    sig = scale(bg, BG_DB).copy()
    pos = []
    for t0, k in ((9.0, kid1), (15.0, kid2)):
        a = int(t0 * SR); sig[a:a + len(k)] = k + sig[a:a + len(k)] * 0.0 + scale(bg, BG_DB)[a:a + len(k)]
        pos.append((a, a + len(k)))
    g, zero, passed, _ = run(sig)
    base_only = zero[fr(5):fr(8.5)]
    ok(base_only.mean() >= 0.9, f"(a) chi nen sau 5 s (nen giong keo dai >3,5 s thi cong tu nhan ra la nen): {base_only.mean():.0%} khung bi zero (>=90%)")
    for n, (a, b) in enumerate(pos):
        f0, f1 = a // FR, b // FR + 1
        r = passed[f0:f1].mean()
        ok(r >= 0.8, f"(b) cau be {n + 1}: {r:.0%} duoc cho qua (>=80%)")
        win = zero[f1:f1 + fr(1.5)]
        longest = max([l for _, l in zero_runs(win)] or [0]) * FR / SR
        ok(longest >= 0.6, f"(c) sau cau be {n + 1}: zero lien tuc dai nhat {longest:.2f}s trong 1,5 s (>=0,6s)")
    print(f"[dB] nen uoc luong cuoi = {g.base_db:.1f} dBFS; bo_vi_nho={g.skipped}")

    # d: nen to bang giong be, 20 s lien tuc
    loud = scale(bg, KID_DB)
    g, zero, passed, mo = run(loud)
    mt = vad_gate.MAX_TURN_S
    zr = [s for s, l in zero_runs(zero) if l * FR / SR >= 0.8]
    ok(mo <= mt + 0.3, f"(d) nen to: doan mo lien tuc dai nhat {mo:.2f}s <= {mt}s+0,3")
    ok(bool(zr) and zr[0] * FR / SR <= mt + 1, f"(d) nen to: doan zero >=800ms dau tien o {zr[0] * FR / SR if zr else -1:.2f}s (<= {mt + 1}s)")
    # d2: ep tran luot that su (tat bo loc am luong, nen to lien tuc mo cong)
    old = (vad_gate.NEAR_MARGIN_DB, vad_gate.ABS_MIN_DBFS)
    vad_gate.NEAR_MARGIN_DB, vad_gate.ABS_MIN_DBFS = -200.0, -200.0
    g, zero, passed, mo = run(loud)
    vad_gate.NEAR_MARGIN_DB, vad_gate.ABS_MIN_DBFS = old
    zr = [s for s, l in zero_runs(zero) if l * FR / SR >= 0.8]
    ok(g.forced_n >= 1 and mo <= mt + 0.3, f"(d2) tran luot: ep_dong={g.forced_n}, mo dai nhat {mo:.2f}s")
    ok(bool(zr) and zr[0] * FR / SR <= mt + 1, f"(d2) zero >=800ms dau tien o {zr[0] * FR / SR if zr else -1:.2f}s (<= {mt + 1}s)")

    # e: phong yen
    quiet = np.zeros(16 * SR, np.float32)
    for t0, k in ((3.0, kid1), (9.0, kid2)):
        a = int(t0 * SR); quiet[a:a + len(k)] = k
    g, zero, passed, _ = run(quiet)
    for n, (t0, k) in enumerate(((3.0, kid1), (9.0, kid2))):
        a = int(t0 * SR); f0, f1 = a // FR, (a + len(k)) // FR + 1
        r = passed[f0:f1].mean()
        ok(r >= 0.9, f"(e) phong yen, cau be {n + 1}: {r:.0%} duoc cho qua (>=90%)")
    print("\n".join(lines))
    print("GATE " + ("FAIL: " + "; ".join(fails) if fails else "PASS"))
    sys.exit(1 if fails else 0)

lines = []
asyncio.run(main())
