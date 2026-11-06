"""Cau noi xiaozhi <-> Gemini Live cho ESP32-A1S (firmware xiaozhi v2.5.2, khong sua firmware).
CHI NGUOI LON THU NOI BO (dieu khoan Gemini API cam dich vu cho tre < 18 tuoi).
Bien: GOOGLE_API_KEY (bat buoc), STLAB_LIVE_WS_PORT (8000), STLAB_LIVE_HTTP_PORT (8003), STLAB_XIAOZHI_SERVER (IP LAN),
STLAB_LIVE_MODEL (gemini-3.8-live), STLAB_LIVE_VOICE (tuy chon).
"""
import asyncio, audioop, json, os, re, socket, sys, time, uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = HERE.parent
RUNTIME = SERVER / "runtime"
os.environ["PATH"] = str(RUNTIME) + os.pathsep + os.environ.get("PATH", "")
if hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(str(RUNTIME))
    except OSError:
        pass
sys.path.insert(0, str(SERVER))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import opuslib_next
import websockets
from aiohttp import web
from google import genai
from google.genai import types

BANNER = "GEMINI LIVE - CHI NGUOI LON THU NOI BO, KHONG CHO BE DUNG (dieu khoan Gemini API)"
WS_PORT = int(os.environ.get("STLAB_LIVE_WS_PORT", "8000"))
HTTP_PORT = int(os.environ.get("STLAB_LIVE_HTTP_PORT", "8003"))
MODEL = os.environ.get("STLAB_LIVE_MODEL", "gemini-3.8-live")
VOICE = os.environ.get("STLAB_LIVE_VOICE", "").strip()
IN_RATE, OUT_RATE = 16000, 24000
IN_FRAME, OUT_FRAME = 960, 1440      # 60 ms
FRAME_S = 0.06
PRE_BUFFER = 5                        # nhu sendAudioHandle cua xinnan
IDLE_S = 60.0


def log(msg):
    print(time.strftime("%H:%M:%S ") + msg, flush=True)


def lan_ip():
    ip = os.environ.get("STLAB_XIAOZHI_SERVER", "").strip()
    if ip:
        return ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def load_prompt():
    txt = (SERVER / "prompt-teacher.md").read_text(encoding="utf-8")
    parts = re.split(r"(?m)^-----\s*$", txt, maxsplit=1)
    return (parts[1] if len(parts) > 1 else txt).strip()


PROMPT = load_prompt()


def live_config():
    kw = dict(
        response_modalities=["AUDIO"],
        system_instruction=PROMPT,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    if VOICE:
        kw["speech_config"] = types.SpeechConfig(
            voice_config=types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)))
    return types.LiveConnectConfig(**kw)


async def ota_handler(request):
    ver = ""
    try:
        data = await request.json() if request.method == "POST" else {}
        ver = (data.get("application") or {}).get("version", "")
    except Exception:
        pass
    ver = request.headers.get("device-version", ver) or ver or "0.0.0"
    body = {
        "server_time": {"timestamp": int(round(time.time() * 1000)), "timezone_offset": 7 * 60},
        "firmware": {"version": ver, "url": ""},
        "websocket": {"url": f"ws://{lan_ip()}:{WS_PORT}/xiaozhi/v1/", "token": ""},
    }
    return web.json_response(body)


class Session:
    def __init__(self, ws, client):
        self.ws = ws
        self.client = client
        self.dec = opuslib_next.Decoder(IN_RATE, 1)
        self.enc = opuslib_next.Encoder(OUT_RATE, 1, opuslib_next.APPLICATION_AUDIO)
        self.sid = uuid.uuid4().hex
        self.out_q = asyncio.Queue()       # bytes Opus | "STOP" marker
        self.pcm_buf = b""
        self.tts_on = False
        self.aborted = False               # bo am thanh toi het luot hien tai
        self.last_active = time.time()
        self.t_user_end = None
        self.user_txt, self.reply_txt = "", ""
        self.first_ms = None
        self.live = None
        self.closed = False

    async def send_json(self, obj):
        await self.ws.send(json.dumps(obj, ensure_ascii=False))

    async def tts_start(self):
        if not self.tts_on:
            self.tts_on = True
            if self.first_ms is None and self.t_user_end:
                self.first_ms = int((time.time() - self.t_user_end) * 1000)
            await self.send_json({"type": "tts", "state": "start", "session_id": self.sid})
            if self.user_txt:
                await self.send_json({"type": "stt", "text": self.user_txt, "session_id": self.sid})

    def clear_out(self):
        self.pcm_buf = b""
        while not self.out_q.empty():
            try:
                self.out_q.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def pacer(self):
        """Gui Opus xuong thiet bi: PRE_BUFFER khung dau gui ngay, sau do giu nhip 60 ms/khung."""
        n, t0 = 0, 0.0
        while True:
            item = await self.out_q.get()
            if isinstance(item, str):  # "STOP"
                await asyncio.sleep(PRE_BUFFER * FRAME_S if n else 0)
                n = 0
                if self.tts_on:
                    self.tts_on = False
                    await self.send_json({"type": "tts", "state": "stop", "session_id": self.sid})
                    self.log_turn()
                continue
            if n == 0:
                t0 = time.time()
            elif n >= PRE_BUFFER:
                delay = t0 + (n - PRE_BUFFER) * FRAME_S - time.time()
                if delay > 0:
                    await asyncio.sleep(delay)
            await self.ws.send(item)
            n += 1

    def log_turn(self):
        if self.first_ms is not None:
            log(f"[LIVE-T] first_audio={self.first_ms}ms user='{self.user_txt.strip()}' reply='{self.reply_txt.strip()}'")
        self.first_ms, self.user_txt, self.reply_txt, self.t_user_end = None, "", "", None

    def push_pcm(self, pcm):
        self.pcm_buf += pcm
        step = OUT_FRAME * 2
        while len(self.pcm_buf) >= step:
            chunk, self.pcm_buf = self.pcm_buf[:step], self.pcm_buf[step:]
            self.out_q.put_nowait(self.enc.encode(chunk, OUT_FRAME))

    def end_turn(self):
        if self.pcm_buf and not self.aborted:
            self.push_pcm(b"\x00" * (OUT_FRAME * 2 - len(self.pcm_buf)))
        self.pcm_buf = b""
        self.out_q.put_nowait("STOP")
        self.aborted = False

    async def gemini_rx(self):
        while not self.closed:
            async for msg in self.live.receive():
                sc = msg.server_content
                if sc is None:
                    continue
                self.last_active = time.time()
                if sc.input_transcription and sc.input_transcription.text:
                    self.user_txt += sc.input_transcription.text
                if sc.interrupted:
                    self.clear_out()
                    self.aborted = False
                    if self.tts_on:
                        self.end_turn()
                    continue
                if sc.output_transcription and sc.output_transcription.text and not self.aborted:
                    self.reply_txt += sc.output_transcription.text
                    if self.tts_on:
                        await self.send_json({"type": "tts", "state": "sentence_start",
                                              "text": self.reply_txt.strip(), "session_id": self.sid})
                if sc.model_turn and not self.aborted:
                    for p in sc.model_turn.parts or []:
                        if p.inline_data and p.inline_data.data:
                            await self.tts_start()
                            self.push_pcm(p.inline_data.data)
                if sc.turn_complete:
                    if self.tts_on or self.pcm_buf:
                        self.end_turn()
                    else:
                        self.aborted = False
                        self.user_txt, self.reply_txt, self.t_user_end = "", "", None

    async def mic_rx(self):
        async for m in self.ws:
            if isinstance(m, bytes):
                if self.tts_on or self.live is None:
                    continue
                try:
                    pcm = self.dec.decode(m, IN_FRAME)
                except Exception:
                    continue
                if audioop.rms(pcm, 2) > 400:  # tieng noi gan nhat -> moc do do tre
                    self.t_user_end = time.time()
                await self.live.send_realtime_input(audio=types.Blob(data=pcm, mime_type=f"audio/pcm;rate={IN_RATE}"))
                continue
            try:
                j = json.loads(m)
            except ValueError:
                continue
            t = j.get("type")
            if t == "listen" and j.get("state") == "start":
                self.last_active = time.time()
            elif t == "abort":
                self.clear_out()
                if self.tts_on:
                    self.aborted = True
                    self.out_q.put_nowait("STOP")
            # hello trung / mcp / listen stop: bo qua

    async def idle_watch(self):
        while True:
            await asyncio.sleep(2)
            if not self.tts_on and time.time() - self.last_active > IDLE_S:
                log("im lang > 60 s, dong ket noi")
                await self.ws.close()
                return

    async def run(self):
        while True:
            m = await asyncio.wait_for(self.ws.recv(), 15)
            if isinstance(m, str) and json.loads(m).get("type") == "hello":
                break
        await self.send_json({"type": "hello", "transport": "websocket", "session_id": self.sid,
                              "audio_params": {"format": "opus", "sample_rate": OUT_RATE, "channels": 1, "frame_duration": 60}})
        async with self.client.aio.live.connect(model=MODEL, config=live_config()) as live:
            self.live = live
            log(f"phien Live mo ({MODEL})")
            tasks = [asyncio.create_task(c()) for c in (self.gemini_rx, self.mic_rx, self.pacer, self.idle_watch)]
            try:
                done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for d in done:
                    if not d.cancelled() and d.exception():
                        log(f"loi phien: {type(d.exception()).__name__}: {str(d.exception())[:200]}")
            finally:
                self.closed = True
                for t in tasks:
                    t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)


async def ws_handler(ws, client):
    log("thiet bi ket noi")
    try:
        await Session(ws, client).run()
    except Exception as e:
        log(f"ket noi dong: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            await ws.close()
        except Exception:
            pass
        log("thiet bi ngat")


async def main():
    print("=" * 78 + "\n" + BANNER + "\n" + "=" * 78, flush=True)
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("Thieu GOOGLE_API_KEY")
    try:
        import no_ecoqos
        no_ecoqos.disable()
    except Exception as e:
        log(f"no_ecoqos: {e}")
    client = genai.Client(api_key=key)
    app = web.Application()
    app.router.add_route("*", "/xiaozhi/ota/", ota_handler)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", HTTP_PORT).start()
    async with websockets.serve(lambda ws: ws_handler(ws, client), "0.0.0.0", WS_PORT, max_size=None,
                                ping_interval=None):
        log(f"Cau noi san sang: ws://{lan_ip()}:{WS_PORT}/xiaozhi/v1/  OTA: http://{lan_ip()}:{HTTP_PORT}/xiaozhi/ota/")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
