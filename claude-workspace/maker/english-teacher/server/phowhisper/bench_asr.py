"""Do Whisper small (hien tai) vs PhoWhisper small/medium tren CPU. Chay: .venv/Scripts\python.exe bench_asr.py
Am thanh = Edge TTS (GIA LAP, KHONG phai giong tre that). Tao tam, xoa sau khi do. Can mang de goi Edge TTS."""
import asyncio, os, re, shutil, subprocess, statistics, sys, tempfile, time, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent
sys.path.insert(0, str(SERVER))
import no_ecoqos
no_ecoqos.disable()

import edge_tts
from faster_whisper import WhisperModel

SENTS = ["Dạ.", "Dạ con.", "Vâng ạ.", "Có nè.", "Hông.", "Con hổng biết.", "Con là bạn thỏ.", "Bạn mèo.",
         "Màu đỏ.", "Con mèo.", "Cô ơi.", "Nói lại đi cô.", "Cô nói to lên.", "Một, hai, ba.", "Red.", "Blue.",
         "Cat.", "Apple.", "Hello cô.", "Con muốn học con vật.", "Con chó màu vàng.", "Con thích màu xanh.",
         "Cô cho con chơi nữa.", "Tạm biệt cô."]
SHORT = {"Dạ.", "Vâng ạ.", "Có nè.", "Hông."}
# Giong vi-VN cua Edge TTS tu choi tham so rate/pitch (NoAudioReceived, do 2026-11-06) -> tao ban goc roi doi toc do/cao do bang ffmpeg.
# (nhan, giong, bo loc ffmpeg). Toc do: atempo=1.25. Cao do: x1.25 (~ +40 Hz cho giong nu ~200 Hz) giu nguyen toc do.
PITCH = "asetrate=24000*1.25,aresample=24000,atempo=0.8"
VOICES = {"HM": "vi-VN-HoaiMyNeural", "NM": "vi-VN-NamMinhNeural"}
FILTERS = {"+0": "anull", "+25": "atempo=1.25", "pitch": PITCH}
VARIANTS = [(f"{v}{k}", v, f) for v in VOICES for k, f in FILTERS.items()]
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


def whisper_prompt():
    t = (SERVER / "whisper-local" / "server.py").read_text(encoding="utf-8")
    m = re.search(r'"STLAB_WHISPER_PROMPT",\s*\n?\s*"([^"]+)"', t)
    return m.group(1)


def norm(s):
    s = unicodedata.normalize("NFC", s).lower()
    s = "".join(c if (c.isalnum() or c.isspace()) else " " for c in s)
    return " ".join(s.split())


def edit(a, b):
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[-1]


async def synth(tmp):
    base = {}
    sem = asyncio.Semaphore(1)

    async def one(v, i, s):
        f = tmp / f"base_{v}_{i}.mp3"
        async with sem:
            for k in range(20):
                try:
                    # Edge TTS tu choi ngau nhien vai chuoi (vd 'Red.'); thu bien the dau cau, am doc nhu nhau
                    await edge_tts.Communicate([s, s.rstrip('.'), s.rstrip('.') + ' ', s.rstrip('.') + ','][k % 4], VOICES[v]).save(str(f)); break
                except Exception:
                    if k == 19: print("TTS loi:", v, repr(s), flush=True); raise
                    await asyncio.sleep(min(20, 2 * (k + 1)))
        base[(v, i)] = f
    await asyncio.gather(*[one(v, i, s) for v in VOICES for i, s in enumerate(SENTS)])
    clips = []
    for vn, v, flt in VARIANTS:
        for i, s in enumerate(SENTS):
            out = tmp / f"{vn}_{i}.wav"
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(base[(v, i)]), "-af", flt, "-ar", "16000", "-ac", "1", str(out)], check=True)
            clips.append((vn, s, out))
    return clips


def run_model(name, model, clips, lang, prompt):
    def tr(path):
        kw = dict(initial_prompt=prompt, beam_size=1, vad_filter=False, condition_on_previous_text=False)
        segs, info = model.transcribe(str(path), language=lang, **kw)
        txt = " ".join(s.text.strip() for s in segs)
        if lang is None and info.language not in ("vi", "en"):  # giong whisper-local/server.py
            segs, info = model.transcribe(str(path), language="en", **kw)
            txt = " ".join(s.text.strip() for s in segs)
        return txt
    tr(clips[0][2])  # lam nong
    ms, wers, cers, short_ok, short_n, hyp_ok, ref_words, ref_chars, e_w, e_c = [], [], [], 0, 0, 0, 0, 0, 0, 0
    for vn, s, f in clips:
        t = time.perf_counter(); h = tr(f); ms.append((time.perf_counter() - t) * 1000)
        r, hh = norm(s), norm(h)
        ew, ec = edit(r.split(), hh.split()), edit(r, hh)
        wers.append(ew / len(r.split())); cers.append(ec / len(r))
        e_w += ew; e_c += ec; ref_words += len(r.split()); ref_chars += len(r)
        hyp_ok += (r == hh)
        if s in SHORT:
            short_n += 1; short_ok += (r == hh)
    ms.sort()
    return dict(name=name, mean=statistics.mean(ms), p95=ms[min(len(ms) - 1, int(len(ms) * 0.95))],
                wer=100 * e_w / ref_words, cer=100 * e_c / ref_chars, exact=100 * hyp_ok / len(clips),
                short=f"{short_ok}/{short_n}", short_pct=100 * short_ok / short_n, n=len(clips))


def main():
    prompt = whisper_prompt()
    tmp = Path(tempfile.mkdtemp(prefix="asrbench_"))
    try:
        print("Tao am thanh Edge TTS (gia lap)...", flush=True)
        clips = asyncio.run(synth(tmp))
        clips.sort(key=lambda c: (c[0], SENTS.index(c[1])))
        print(f"{len(clips)} clip", flush=True)
        res = []
        specs = [("Whisper small (hien tai, lang tu do)", lambda: WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8), None),
                 ("PhoWhisper-small", lambda: WhisperModel(str(SERVER / "models" / "phowhisper-small-ct2"), device="cpu", compute_type="int8", cpu_threads=8), "vi"),
                 ("PhoWhisper-medium", lambda: WhisperModel(str(SERVER / "models" / "phowhisper-medium-ct2"), device="cpu", compute_type="int8", cpu_threads=8), "vi")]
        for name, mk, lang in specs:
            try:
                m = mk()
            except Exception as e:
                print(f"Bo qua {name}: {type(e).__name__}: {str(e)[:100]}"); continue
            print("Do", name, flush=True)
            res.append(run_model(name, m, clips, lang, prompt)); del m
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lines = ["| Mo hinh | ms TB/cau | ms p95 | WER % | CER % | dung nguyen cau % | cau ngan dung (Da/Vang a/Co ne/Hong) | n |",
             "|---|---|---|---|---|---|---|---|"]
    for r in res:
        lines.append(f"| {r['name']} | {r['mean']:.0f} | {r['p95']:.0f} | {r['wer']:.1f} | {r['cer']:.1f} | {r['exact']:.1f} | {r['short']} ({r['short_pct']:.0f}%) | {r['n']} |")
    tbl = "\n".join(lines)
    print(tbl)
    (HERE / "bench-result.md").write_text(
        f"# Ket qua do ASR ({time.strftime('%Y-%m-%d')})\n\nCPU i5-13400F, cpu_threads=8, int8, beam 1, initial_prompt cua whisper-local, sau 1 lan lam nong.\n"
        f"Am thanh = Edge TTS (HoaiMy, NamMinh; toc do x1.25 va cao do x1.25 doi bang ffmpeg vi giong vi-VN tu choi rate/pitch) - GIA LAP, KHONG phai giong tre that. "
        f"{len(SENTS)} cau x {len(VARIANTS)} bien the.\n\n{tbl}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
