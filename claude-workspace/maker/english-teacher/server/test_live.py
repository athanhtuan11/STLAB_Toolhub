# Gate cau noi Gemini Live (Claude viet, executor KHONG sua). Cau noi phai dang chay (run-live.ps1).
# Chay:  runtime\.venv\Scripts\python.exe -X utf8 test_live.py
# Gia lap bo A1S che do TU DONG (mode auto, khong gui listen stop): OTA -> WebSocket xiaozhi v1 -> 2 luot noi trong CUNG
# 1 phien, Opus 16 kHz 60 ms theo thoi gian thuc + im lang; may chu (VAD cua Gemini) tu chot cau, tra tts start/stop + Opus 24 kHz.
import asyncio, json, os, re, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts, opuslib_next, websockets

HOST = os.environ.get("STLAB_XIAOZHI_SERVER", "127.0.0.1")
HTTP_PORT = int(os.environ.get("STLAB_LIVE_HTTP_PORT", "8003"))  # thu song song may chu cu: dat 8103
SR, FRAME = 16000, 960            # 60 ms
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


async def speech_pcm(text, voice):
    d = Path(tempfile.mkdtemp(prefix="stlab-live-"))
    mp3, raw = d / "a.mp3", d / "a.raw"
    await edge_tts.Communicate(text, voice).save(str(mp3))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), "-f", "s16le", str(raw)], check=True)
    pcm = raw.read_bytes()
    mp3.unlink(); raw.unlink(); d.rmdir()
    return pcm


def ota():
    req = urllib.request.Request(f"http://{HOST}:{HTTP_PORT}/xiaozhi/ota/", method="POST",
                                 data=json.dumps({"application": {"version": "2.5.2"}, "board": {"type": "stlab-a1s"}}).encode(),
                                 headers={"Device-Id": "e2:00:00:00:00:02", "Client-Id": "stlab-live-gate", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


async def say_and_wait(ws, enc, dec, pcm, tag):
    """Gui 1 cau theo thoi gian thuc roi im lang lien tuc (nhu micro that) toi khi nhan tts stop."""
    silence = b"\x00" * (FRAME * 2)
    for i in range(0, len(pcm), FRAME * 2):
        await ws.send(enc.encode(pcm[i:i + FRAME * 2].ljust(FRAME * 2, b"\x00"), FRAME))
        await asyncio.sleep(0.06)
    t_end = time.time()
    got_start, got_stop, t_first, samples, texts = False, False, None, 0, []
    deadline = time.time() + 25
    speaking = False

    async def feeder():  # micro van gui im lang khi chua toi luot co noi (bo khong AEC: dung gui khi co noi)
        while not got_stop and time.time() < deadline:
            if not speaking:
                await ws.send(enc.encode(silence, FRAME))
            await asyncio.sleep(0.06)

    task = asyncio.create_task(feeder())
    try:
        while time.time() < deadline:
            try:
                m = await asyncio.wait_for(ws.recv(), max(0.1, deadline - time.time()))
            except asyncio.TimeoutError:
                break
            if isinstance(m, bytes):
                t_first = t_first or time.time()
                try:
                    samples += len(dec.decode(m, 2880)) // 2
                except Exception:
                    pass
                continue
            j = json.loads(m)
            if j.get("type") == "tts":
                if j.get("state") == "start":
                    got_start, speaking = True, True
                elif j.get("state") == "sentence_start" and j.get("text"):
                    texts.append(j["text"])
                elif j.get("state") == "stop":
                    got_stop = True
                    break
    finally:
        got_stop = True
        task.cancel()
    lat = (t_first - t_end) if t_first else None
    audio_s = samples / 24000
    print(f"[LIVE-{tag}] tre={lat if lat is None else round(lat, 2)}s am_thanh={audio_s:.1f}s chu='{' '.join(texts)[:80]}'")
    return got_start, got_stop, lat, audio_s


async def main():
    o = ota()
    ws_url = (o.get("websocket") or {}).get("url", "")
    ok(ws_url.startswith("ws://") and ws_url.rstrip("/").endswith("/xiaozhi/v1"), f"OTA tra websocket.url ({ws_url})")
    ok("firmware" in o and "server_time" in o, "OTA co firmware + server_time")
    ws_url = ws_url.replace(ws_url.split("/")[2].split(":")[0], HOST) if ws_url else f"ws://{HOST}:8000/xiaozhi/v1/"
    enc = opuslib_next.Encoder(SR, 1, opuslib_next.APPLICATION_VOIP)
    dec = opuslib_next.Decoder(24000, 1)
    hdr = {"device-id": "e2:00:00:00:00:02", "client-id": "stlab-live-gate", "protocol-version": "1", "authorization": "Bearer gate"}
    vi = await speech_pcm("Cô ơi, con mèo tiếng Anh là gì?", "vi-VN-HoaiMyNeural")
    en = await speech_pcm("What color is an apple?", "en-US-AnaNeural")
    async with websockets.connect(ws_url, additional_headers=hdr, max_size=None) as ws:
        await ws.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket", "features": {"mcp": True},
                                  "audio_params": {"format": "opus", "sample_rate": SR, "channels": 1, "frame_duration": 60}}))
        hello = None
        t = time.time() + 10
        while time.time() < t and hello is None:
            m = await asyncio.wait_for(ws.recv(), 10)
            if isinstance(m, str) and json.loads(m).get("type") == "hello":
                hello = json.loads(m)
        ok(hello is not None and hello.get("transport") == "websocket", "hello tu may chu")
        ap = (hello or {}).get("audio_params", {})
        ok(ap.get("format") == "opus" and ap.get("sample_rate") == 24000, f"hello audio_params opus 24000 ({ap})")
        sid = (hello or {}).get("session_id", "")
        await ws.send(json.dumps({"session_id": sid, "type": "listen", "state": "start", "mode": "auto"}))
        for tag, pcm in (("VI", vi), ("EN", en)):
            s, st, lat, a = await say_and_wait(ws, enc, dec, pcm, tag)
            ok(s and st, f"{tag}: co tts start + stop")
            ok(a > 0.8, f"{tag}: am thanh tra ve > 0,8 s ({a:.1f})")
            ok(lat is not None and lat < 2.5, f"{tag}: het tieng noi -> tieng dau tien < 2,5 s ({lat})")
            if tag == "VI":  # thiet bi AutoStop: sau tts stop thi nghe tiep, gui lai listen start nhu firmware
                await ws.send(json.dumps({"session_id": sid, "type": "listen", "state": "start", "mode": "auto"}))
    print("\n%s test_live (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
