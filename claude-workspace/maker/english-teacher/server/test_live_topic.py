# Gate CHU DE TU CHON qua cau noi Live THAT (Claude viet, executor KHONG sua). Goi API that.
# Chay nhu test_live_lesson.py: bridge voi STLAB_LEARNERS_PATH=<file tam> + cong test (vd 8100/8103), gate doc cung bien.
# Tuan 2026-11-08: khong go bo - doi chu de bat ky (vd hoa cho be 2 tuoi) + noi chuyen ngoai luong.
# Kich ban: chao -> "Con la ban Tho" -> "Co oi hom nay day con ve hoa di" (co day 'flower', goi change_topic -> extra co flower)
# -> "Hom nay con di so thu" (co dap dung chuyen, khong hoi lai biet danh, khong ep quay ve bai).
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
    a = await pcm("Xin chào cô."); b = await pcm("Con là bạn Thỏ.")
    c = await pcm("Cô ơi, hôm nay dạy con về hoa đi."); e = await pcm("Hôm nay con đi sở thú.")
    hdr = {"device-id": "e2:00:00:00:00:07", "client-id": "topic-gate", "protocol-version": "1"}
    async with websockets.connect(f"ws://{HOST}:{WS}/xiaozhi/v1/", additional_headers=hdr, max_size=None) as ws:
        await ws.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket",
                                  "audio_params": {"format": "opus", "sample_rate": SR, "channels": 1, "frame_duration": 60}}))
        h = json.loads(await asyncio.wait_for(ws.recv(), 5))
        await ws.send(json.dumps({"session_id": h.get("session_id"), "type": "listen", "state": "start", "mode": "auto"}))
        await turn(ws, enc, dec, a, "chao")
        await turn(ws, enc, dec, b, "biet-danh")
        ok(list(learners()) == ["thỏ"], f"ho so tho ({list(learners())})")
        f3, a3, t3, _, _ = await turn(ws, enc, dec, c, "hoa")
        ok(a3 > 0.8 and re.search(r"\bflowers?\b", t3, re.I) is not None, f"xin chu de hoa -> co day 'flower': '{t3[:100]}'")
        ex = [x.get("word") if isinstance(x, dict) else x for x in learners().get("thỏ", {}).get("extra", [])]
        ok("flower" in ex, f"Gemini goi change_topic -> extra co 'flower' ({ex})")
        f4, a4, t4, _, _ = await turn(ws, enc, dec, e, "so-thu")
        ok(a4 > 0.8 and re.search(r"sở thú|zoo|con vật|animal|voi|khỉ|hổ|elephant|monkey|lion", t4, re.I) is not None,
           f"chuyen ngoai luong (so thu) -> co dap dung chuyen: '{t4[:100]}'")
        ok(re.search(r"bạn nào|chọn bạn", t4, re.I) is None, "khong hoi lai biet danh")
    print("\n%s test_live_topic (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())