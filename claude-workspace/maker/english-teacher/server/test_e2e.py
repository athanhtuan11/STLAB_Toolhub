# Kiem dau cuoi GIA LAP THIET BI (Claude viet, executor KHONG sua). May chu phai dang chay (run.ps1).
# Chay bang venv may chu:  runtime\.venv\Scripts\python.exe test_e2e.py
# Lam dung nhu bo A1S: WebSocket xiaozhi v1, gui giong Opus 16 kHz 60 ms (giu nut noi), nhan STT + cau tra loi + am thanh Opus.
import asyncio, json, os, re, subprocess, sys, tempfile, time
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import edge_tts, opuslib_next, websockets

HOST = os.environ.get("STLAB_XIAOZHI_SERVER", "192.168.1.47")
URL = f"ws://{HOST}:8000/xiaozhi/v1/"
SR, FRAME = 16000, 960            # 60 ms
CJK = re.compile(r"[぀-ヿ㐀-鿿]")
VI = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", re.I)
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


async def speech_pcm(text, voice):
    d = Path(tempfile.mkdtemp(prefix="stlab-e2e-"))
    mp3, raw = d / "a.mp3", d / "a.raw"
    await edge_tts.Communicate(text, voice).save(str(mp3))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp3), "-ac", "1", "-ar", str(SR), "-f", "s16le", str(raw)], check=True)
    pcm = raw.read_bytes()
    mp3.unlink(); raw.unlink(); d.rmdir()
    return pcm


async def turn(tag, text, voice):
    pcm = await speech_pcm(text, voice)
    enc = opuslib_next.Encoder(SR, 1, opuslib_next.APPLICATION_VOIP)
    dec = opuslib_next.Decoder(24000, 1)
    hdr = {"device-id": "e2e:00:00:00:00:01", "client-id": "stlab-e2e", "protocol-version": "1", "authorization": "Bearer e2e"}
    stt, replies, frames, samples, t_stop, t_first = "", [], 0, 0, None, None
    async with websockets.connect(URL, additional_headers=hdr, max_size=None) as ws:
        await ws.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket",
                                  "audio_params": {"format": "opus", "sample_rate": SR, "channels": 1, "frame_duration": 60}}))
        hello = json.loads(await asyncio.wait_for(ws.recv(), 10))
        sid = hello.get("session_id", "")
        await ws.send(json.dumps({"session_id": sid, "type": "listen", "state": "start", "mode": "manual"}))
        silence = b"\x00" * (FRAME * 2)
        chunks = [silence] * 3 + [pcm[i:i + FRAME * 2].ljust(FRAME * 2, b"\x00") for i in range(0, len(pcm), FRAME * 2)] + [silence] * 5
        for c in chunks:
            await ws.send(enc.encode(c, FRAME))
            await asyncio.sleep(0.06)
        await ws.send(json.dumps({"session_id": sid, "type": "listen", "state": "stop"}))
        t_stop = time.time()
        end = time.time() + 45
        while time.time() < end:
            try:
                m = await asyncio.wait_for(ws.recv(), max(0.1, end - time.time()))
            except asyncio.TimeoutError:
                break
            if isinstance(m, bytes):
                frames += 1
                t_first = t_first or time.time()
                try:
                    samples += len(dec.decode(m, 2880))
                except Exception:
                    pass
                continue
            j = json.loads(m)
            if j.get("type") == "stt":
                stt = j.get("text", "")
            elif j.get("type") == "tts" and j.get("state") == "sentence_start":
                replies.append(j.get("text", ""))
            elif j.get("type") == "tts" and j.get("state") == "stop":
                break
    reply = " ".join(replies)
    audio_s = samples / 2 / 24000 if samples else frames * 0.06
    lat = (t_first - t_stop) if t_first else None
    print(f"[E2E-{tag}] noi='{text}' stt='{stt}' tra_loi='{reply}' am_thanh={audio_s:.1f}s tre={lat if lat is None else round(lat, 2)}s")
    return stt, reply, audio_s, lat


async def main():
    voice = os.environ.get("STLAB_E2E_VOICE", "vi-VN-HoaiMyNeural")
    stt, reply, a, lat = await turn("VI", "Con mèo tiếng Anh là gì?", voice)
    ok(re.search(r"m[eè]o", stt, re.I) is not None, "VI: may chu nghe ra 'meo'")
    ok(bool(reply) and VI.search(reply) is not None, "VI: tra loi co tieng Viet")
    ok(re.search(r"\bcat\b", reply, re.I) is not None, "VI: day tu 'cat'")
    ok(a > 0.8, "VI: co am thanh tra ve (> 0,8 s)")
    ok(not CJK.search(reply), "VI: khong co chu Trung/Nhat")
    stt, reply, a, lat2 = await turn("EN", "What color is an apple?", "en-US-AnaNeural")
    ok(re.search(r"apple", stt, re.I) is not None, "EN: may chu nghe ra 'apple'")
    ok(re.search(r"\bred\b", reply, re.I) is not None, "EN: tra loi 'red'")
    ok(a > 0.8, "EN: co am thanh tra ve (> 0,8 s)")
    ok(not CJK.search(reply), "EN: khong co chu Trung/Nhat")
    for lab, l in (("VI", lat), ("EN", lat2)):
        ok(l is not None and l < 8.0, f"{lab}: tu luc tha nut toi tieng dau tien < 8 s ({l})")
    print("\n%s test_e2e (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
    sys.exit(1 if fails else 0)


asyncio.run(main())
