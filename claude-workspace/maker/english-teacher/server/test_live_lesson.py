# Gate HOI THOAI GIAO TRINH that qua cau noi Live (Claude viet, executor KHONG sua). Goi API that.
# Cau noi chay voi bien STLAB_LEARNERS_PATH=<file tam> (gate doc cung bien) va cong STLAB_LIVE_HTTP_PORT/WS (vd 8103/8100).
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_live_lesson.py
# Kich ban: chao -> co hoi biet danh (KHONG duoc tu tao ho so) -> be noi "Con la ban Tho" -> ho so 'tho' bai 01, co day mau
# -> be noi "Red" -> co tiep tuc bai (co am thanh day du, khong lap lai cau hoi biet danh).
import asyncio, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts, opuslib_next, websockets

HOST = os.environ.get("STLAB_XIAOZHI_SERVER", "127.0.0.1")
WS = int(os.environ.get("STLAB_LIVE_WS_PORT", "8000"))
DATA = Path(os.environ.get("STLAB_LEARNERS_PATH", ""))
SR, FR = 16000, 960
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


def learners():
    try:
        return json.loads(DATA.read_text(encoding="utf-8")).get("learners", {})
    except Exception:
        return {}


async def pcm(text, voice="vi-VN-HoaiMyNeural"):
    d = Path(tempfile.mkdtemp(prefix="stlab-les-")); m, r = d / "a.mp3", d / "a.raw"
    await edge_tts.Communicate(text, voice).save(str(m))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(m), "-ac", "1", "-ar", str(SR), "-f", "s16le", str(r)], check=True)
    b = r.read_bytes(); m.unlink(); r.unlink(); d.rmdir()
    return b


async def turn(ws, enc, dec, data, tag):
    """noi 1 cau roi micro gui im lang toi khi co noi xong (tts stop) VA im them 2,5 s khong co am thanh moi."""
    sil = b"\x00" * (FR * 2)
    early = 0  # am thanh nam san trong socket TRUOC khi bat dau noi = am thanh sot cua luot truoc
    while True:
        try:
            m0 = await asyncio.wait_for(ws.recv(), 0.05)
            if isinstance(m0, bytes):
                early += 1
        except asyncio.TimeoutError:
            break
    t_start = time.time()
    for i in range(0, len(data), FR * 2):
        await ws.send(enc.encode(data[i:i + FR * 2].ljust(FR * 2, b"\x00"), FR)); await asyncio.sleep(0.06)
    t_end = time.time(); first = None; first_s = None; texts = []; samples = 0; state = {"speaking": False, "done": False}; last_rx = time.time()

    async def feed():
        while not state["done"]:
            if not state["speaking"]:
                await ws.send(enc.encode(sil, FR))
            await asyncio.sleep(0.06)
    ft = asyncio.create_task(feed())
    stopped = False
    try:
        while time.time() - t_end < 30:
            try:
                m = await asyncio.wait_for(ws.recv(), 2.5 if stopped else 30)
            except asyncio.TimeoutError:
                break  # da tts stop va im 2,5 s
            if isinstance(m, bytes):
                first = first or time.time() - t_end; first_s = first_s or time.time() - t_start; last_rx = time.time()
                try:
                    samples += len(dec.decode(m, 2880)) // 2
                except Exception:
                    pass
                continue
            j = json.loads(m)
            if j.get("type") == "tts":
                if j.get("state") == "start":
                    state["speaking"] = True
                elif j.get("state") == "sentence_start" and j.get("text"):
                    texts.append(j["text"])
                elif j.get("state") == "stop":
                    state["speaking"] = False; stopped = True
                    await ws.send(json.dumps({"type": "listen", "state": "start", "mode": "auto"}))
    finally:
        state["done"] = True; ft.cancel()
    txt = texts[-1] if texts else ""
    print(f"[{tag}] tre={first and round(first, 2)} am_thanh={samples / 24000:.1f}s co: {txt[:120]}")
    return first, samples / 24000, txt, first_s, early


async def main():
    ok(bool(DATA.name), "can bien STLAB_LEARNERS_PATH (file tam, giong cau noi)")
    if DATA.name and DATA.exists():
        DATA.unlink()
    enc = opuslib_next.Encoder(SR, 1, opuslib_next.APPLICATION_VOIP); dec = opuslib_next.Decoder(24000, 1)
    # 2026-11-06: bai do lo trinh tuan quyet dinh (ROADMAP.md) - lay bai/tu tuan 1 cua lich 2-3 tuoi
    sys.path.insert(0, str(Path(__file__).resolve().parent / "live"))
    from curriculum import Curriculum
    w1 = Curriculum(Path(tempfile.mkdtemp()) / "x.json", Path(__file__).resolve().parent.parent / "lessons").roadmap(2)[0]
    word1 = w1["new"][0]
    a = await pcm("Xin chào cô."); b = await pcm("Con là bạn Thỏ."); c = await pcm(word1.capitalize() + ".", "en-US-AnaNeural")
    hdr = {"device-id": "e2:00:00:00:00:04", "client-id": "lesson-gate", "protocol-version": "1"}
    async with websockets.connect(f"ws://{HOST}:{WS}/xiaozhi/v1/", additional_headers=hdr, max_size=None) as ws:
        await ws.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket",
                                  "audio_params": {"format": "opus", "sample_rate": SR, "channels": 1, "frame_duration": 60}}))
        h = json.loads(await asyncio.wait_for(ws.recv(), 5))
        await ws.send(json.dumps({"session_id": h.get("session_id"), "type": "listen", "state": "start", "mode": "auto"}))
        f1, a1, t1, _, _ = await turn(ws, enc, dec, a, "chao")
        ok(a1 > 0.8 and re.search(r"th[ỏo]|m[èe]o|g[ấa]u|b[ạa]n", t1, re.I) is not None, "co hoi biet danh con vat")
        ok(learners() == {}, f"chua tao ho so truoc khi be noi biet danh ({list(learners())})")
        f2, a2, t2, _, _ = await turn(ws, enc, dec, b, "biet-danh")
        L = learners()
        ok(list(L) == ["thỏ"] and L["thỏ"].get("lesson") == w1["lesson_id"], f"ho so 'tho' bai tuan 1 {w1['lesson_id']} ({ {k: v.get('lesson') for k, v in L.items()} })")
        # 2026-11-07 Tuan: "be tra loi ban meo nhung lau moi phan hoi" -> co phai chao lai NGAY (khong chan cau dau de cho [lesson])
        ok(a2 > 1.0 and f2 is not None and f2 < 1.8, f"co tra loi NHANH sau biet danh < 1,8 s (am thanh {a2:.1f} s, tre {f2})")
        ok(any(re.search(r"\b" + re.escape(w) + r"\b", t2, re.I) for w in list(w1["new"]) + list(w1.get("daily", []))),
           f"co bat dau bai tuan 1 (co tu {w1['new']})")
        f3, a3, t3, fs3, early3 = await turn(ws, enc, dec, c, "red")
        # 2026-11-06: do tu LUC BAT DAU NOI (file giong co duoi im lang, Gemini chot cau truoc khi gui het -> tre tinh tu cuoi file ~0)
        ok(early3 == 0, f"khong co am thanh sot cua luot truoc truoc khi noi 'Red' ({early3} khung)")
        ok(a3 > 0.8 and fs3 is not None and fs3 > 0.3, f"luot 'Red' co tra loi rieng sau khi bat dau noi (am thanh {a3:.1f} s, tu luc noi {fs3})")
        ok(re.search(r"bạn nào|thỏ, mèo|chọn bạn", t3, re.I) is None, "khong hoi lai biet danh")
    print("\n%s test_live_lesson (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
