"""Cau noi xiaozhi <-> Gemini Live cho ESP32-A1S (firmware xiaozhi v2.5.2, khong sua firmware).
CHI NGUOI LON THU NOI BO (dieu khoan Gemini API cam dich vu cho tre < 18 tuoi).
Bien: GOOGLE_API_KEY (bat buoc), STLAB_LIVE_WS_PORT (8000), STLAB_LIVE_HTTP_PORT (8003), STLAB_XIAOZHI_SERVER (IP LAN),
STLAB_LIVE_MODEL (gemini-3.8-live), STLAB_LIVE_VOICE (tuy chon).
"""
import asyncio
import unicodedata, audioop, json, os, re, socket, sys, time, uuid
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


DEBUG = bool(os.environ.get("STLAB_LIVE_DEBUG"))


def dbg(msg):
    if DEBUG:
        log("[dbg] " + msg)


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


from curriculum import Curriculum, ALLOWED_NICKNAMES, live_tools, find_nickname  # noqa: E402

SILENCE_MS = int(os.environ.get("STLAB_LIVE_SILENCE_MS", "600"))

CUR = Curriculum(os.environ.get("STLAB_LEARNERS_PATH") or (SERVER / "data" / "learners.json"), SERVER.parent / "lessons")
CURRICULUM_PROMPT = (
    "\n\nAt the start, ask in Vietnamese which animal friend is learning today (e.g. bạn thỏ, bạn mèo, bạn gấu). "
    "Then wait. The system will send a [lesson] message with the lesson to follow. Until then, do not start a lesson "
    "and do not call tools. After a [lesson] message: follow it; after the child repeats a vocabulary word call "
    "mark_word; at the end call finish_lesson then say a short goodbye. Never ask for real names."
)
PROMPT = load_prompt() + CURRICULUM_PROMPT


def live_config():
    kw = dict(
        response_modalities=["AUDIO"],
        system_instruction=PROMPT,
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        tools=[types.Tool(function_declarations=live_tools())],
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                silence_duration_ms=SILENCE_MS)),
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


STANDBY_MAX_S = 480.0      # phien du phong khong dung qua 8 phut -> dong, mo lai
HEDGE_AFTER_S = 2.0
OPEN_TOTAL_S = 10.0
MIC_BUF_MAX = 400          # khung 60 ms (~24 s) toi da dem truoc khi phien san sang


class LiveHandle:
    def __init__(self, cm, live):
        self.cm, self.live, self.born = cm, live, time.time()

    def alive(self):
        ws = getattr(self.live, "_ws", None) or getattr(getattr(self.live, "_session", None), "_ws", None)
        if ws is None:
            return True
        # websockets 14 (google-genai dung websockets.asyncio.client.ClientConnection): KHONG co .closed, dung .state
        st = getattr(ws, "state", None)
        if st is not None:
            from websockets.protocol import State
            return st is State.OPEN
        closed = getattr(ws, "closed", None)  # API cu
        return not closed if isinstance(closed, bool) else True

    async def close(self):
        try:
            await asyncio.wait_for(self.cm.__aexit__(None, None, None), 3)
        except BaseException:
            pass


async def open_live(client):
    cm = client.aio.live.connect(model=MODEL, config=live_config())
    live = await cm.__aenter__()
    return LiveHandle(cm, live)


async def close_late(task):
    """Phien mo xong sau khi da co phien khac -> dong."""
    try:
        h = await task
        await h.close()
    except BaseException:
        pass


class LivePool:
    def __init__(self, client):
        self.client = client
        self.standby = None
        self.taken = asyncio.Event()

    async def maintain(self):
        while True:
            if self.standby is None:
                t0 = time.time()
                try:
                    h = await asyncio.wait_for(open_live(self.client), OPEN_TOTAL_S)
                except asyncio.CancelledError:
                    raise
                except BaseException as e:
                    log(f"phien du phong loi: {type(e).__name__}: {str(e)[:120]}")
                    await asyncio.sleep(3)
                    continue
                self.standby = h
                self.taken.clear()
                log(f"phien du phong san sang ({int((time.time() - t0) * 1000)} ms)")
            try:
                await asyncio.wait_for(self.taken.wait(), timeout=5)
            except asyncio.TimeoutError:
                h = self.standby
                if h is not None and (time.time() - h.born >= STANDBY_MAX_S or not h.alive()):
                    log("phien du phong het han/dong, mo lai")
                    self.standby = None
                    await h.close()
                continue
            self.taken.clear()
            self.standby = None

    async def acquire(self):
        """Tra handle. Uu tien phien du phong; neu khong thi mo moi co hedge."""
        h = self.standby
        if h is not None:
            self.standby = None
            self.taken.set()
            if h.alive():
                log("dung phien du phong")
                return h
            asyncio.create_task(h.close())
        t0 = time.time()
        tasks = [asyncio.create_task(open_live(self.client))]
        hedge = 0
        try:
            done, _ = await asyncio.wait(tasks, timeout=HEDGE_AFTER_S)
            if not done:
                hedge = 1
                tasks.append(asyncio.create_task(open_live(self.client)))
            allt = list(tasks)
            while True:
                left = OPEN_TOTAL_S - (time.time() - t0)
                if left <= 0:
                    raise asyncio.TimeoutError("mo phien Live > 10 s")
                done, _ = await asyncio.wait(tasks, timeout=left, return_when=asyncio.FIRST_COMPLETED)
                if not done:
                    raise asyncio.TimeoutError("mo phien Live > 10 s")
                ok = None
                for d in done:
                    if not d.cancelled() and d.exception() is None:
                        ok = d
                        break
                if ok is not None:
                    for t in allt:
                        if t is not ok:
                            asyncio.create_task(close_late(t))
                    log(f"mo phien moi ({int((time.time() - t0) * 1000)} ms, hedge={hedge})")
                    return ok.result()
                tasks = [t for t in tasks if t not in done]
                if not tasks:
                    raise RuntimeError("mo phien Live loi: " + str(next(iter(done)).exception())[:150])
        except BaseException:
            for t in tasks:
                if not t.done():
                    t.cancel()
            raise


class Session:
    def __init__(self, ws, pool):
        self.ws = ws
        self.pool = pool
        self.handle = None
        self.mic_buf = []
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
        self.nick = None                   # biet danh cua ket noi nay
        self.in_buf = ""                   # loi be cua luot hien tai (tim biet danh)
        self.pending_lesson = None         # tin [lesson] cho gui khi luot hien tai xong
        self.gen_open = False              # Gemini dang sinh am thanh cua 1 luot (chua turn_complete)
        self.dev_on = False                # thiet bi da nhan tts start (chua stop)

    async def handle_tool_call(self, tc):
        resps = []
        for fc in tc.function_calls or []:
            a = dict(fc.args or {})
            try:
                if fc.name == "mark_word":
                    res = CUR.mark(self.nick, a.get("word", ""), bool(a.get("correct"))) if self.nick else {"ok": False}
                    log(f"[LIVE-TOOL] mark_word {a.get('word', '')} {bool(a.get('correct'))}")
                elif fc.name == "finish_lesson":
                    res = CUR.finish(self.nick) if self.nick else {"next_lesson": None}
                    log(f"[LIVE-TOOL] finish_lesson -> {res.get('next_lesson')}")
                else:
                    res = {"error": "unknown tool"}
            except Exception as e:
                res = {"error": type(e).__name__}
            resps.append(types.FunctionResponse(id=fc.id, name=fc.name, response=res))
        if resps:
            await self.live.send_tool_response(function_responses=resps)

    async def send_json(self, obj):
        await self.ws.send(json.dumps(obj, ensure_ascii=False))

    def tts_start(self):
        """Phia Gemini: am thanh dau tien cua luot -> chen marker START vao hang doi (dung thu tu voi STOP)."""
        if not self.gen_open:
            self.gen_open = True
            self.tts_on = True
            if self.first_ms is None and self.t_user_end:
                self.first_ms = int((time.time() - self.t_user_end) * 1000)
            self.out_q.put_nowait("START")

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
            if item == "START":
                if not self.dev_on:
                    self.dev_on = True
                    dbg("tts start")
                    await self.send_json({"type": "tts", "state": "start", "session_id": self.sid})
                    if self.user_txt:
                        await self.send_json({"type": "stt", "text": self.user_txt, "session_id": self.sid})
                continue
            if isinstance(item, str):  # "STOP": chi sau khi da xa het khung truoc no
                await asyncio.sleep(PRE_BUFFER * FRAME_S if n else 0)
                n = 0
                if self.dev_on:
                    self.dev_on = False
                    dbg("tts stop")
                    await self.send_json({"type": "tts", "state": "stop", "session_id": self.sid})
                    self.log_turn()
                if not self.gen_open and self.out_q.empty():
                    self.tts_on = False
                continue
            if n == 0:
                t0 = time.time()
            elif n >= PRE_BUFFER:
                delay = t0 + (n - PRE_BUFFER) * FRAME_S - time.time()
                if delay > 0:
                    await asyncio.sleep(delay)
            if self.dev_on:
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
        self.gen_open = False
        self.aborted = False

    async def lesson_timeout(self):
        """Gemini khong ket thuc luot cua be nhanh -> sau 1,5 s van gui [lesson] (khong cho 15 s)."""
        await asyncio.sleep(1.5)
        if self.pending_lesson:
            txt, self.pending_lesson = self.pending_lesson, None
            self.aborted = False
            await self.send_lesson(txt)

    async def send_lesson(self, text):
        try:
            await self.live.send_client_content(
                turns=types.Content(role="user", parts=[types.Part(text=text)]), turn_complete=True)
        except Exception as e:
            log(f"send_client_content loi ({type(e).__name__}), dung send_realtime_input")
            await self.live.send_realtime_input(text=text)

    def check_nick(self):
        """Be nhan biet danh: cau noi tu goi Curriculum.start va nho Gemini bat dau bai."""
        if self.nick or self.pending_lesson:
            return
        nick = find_nickname(self.in_buf)
        if not nick:
            return
        res = CUR.start(nick)
        if res.get("allowed"):
            self.nick = res["learner"]
            log(f"[LIVE-TOOL] nick {nick} -> {res.get('lesson_id')}")
            self.pending_lesson = (f"[lesson] Learner: bạn {nick}. {res['instructions']} "
                                   "Greet the learner by this animal name and start the lesson now.")
        else:
            log(f"[LIVE-TOOL] nick {nick} -> refused")
            self.pending_lesson = (f"[lesson] Learner: bạn {nick}. Not allowed: {res.get('reason', '')} "
                                   "Say this reason kindly in Vietnamese, then say a short goodbye. Do not start a lesson.")
        self.mute_current_turn()
        asyncio.create_task(self.lesson_timeout())

    def mute_current_turn(self):
        """Tra loi tu sinh cua Gemini cho cau biet danh bi bo (chi phat luot [lesson] sau do)."""
        self.clear_out()
        if self.gen_open or self.dev_on:
            self.out_q.put_nowait("STOP")
        self.gen_open = False
        self.aborted = True

    async def gemini_rx(self):
        while not self.closed:
            async for msg in self.live.receive():
                if getattr(msg, "tool_call", None):
                    dbg("tool_call")
                    self.last_active = time.time()
                    await self.handle_tool_call(msg.tool_call)
                    continue
                sc = msg.server_content
                if sc is None:
                    continue
                self.last_active = time.time()
                if sc.input_transcription and sc.input_transcription.text:
                    self.user_txt += sc.input_transcription.text
                    self.in_buf += sc.input_transcription.text
                    self.check_nick()
                if sc.interrupted:
                    self.clear_out()
                    self.aborted = False
                    self.in_buf = ""
                    if self.gen_open or self.pcm_buf:
                        self.end_turn()
                    self.gen_open = False
                    continue
                if sc.output_transcription and sc.output_transcription.text and not self.aborted:
                    self.reply_txt += sc.output_transcription.text
                    if self.tts_on:
                        await self.send_json({"type": "tts", "state": "sentence_start",
                                              "text": self.reply_txt.strip(), "session_id": self.sid})
                if sc.model_turn and not self.aborted:
                    for p in sc.model_turn.parts or []:
                        if p.inline_data and p.inline_data.data:
                            self.tts_start()
                            self.push_pcm(p.inline_data.data)
                if sc.turn_complete:
                    dbg(f"turn_complete gen_open={self.gen_open} dev_on={self.dev_on}")
                    if self.gen_open or self.pcm_buf:
                        self.end_turn()
                    else:
                        self.aborted = False
                        if not self.dev_on and self.out_q.empty():
                            self.user_txt, self.reply_txt, self.t_user_end = "", "", None
                    self.in_buf = ""
                    if self.pending_lesson:
                        txt, self.pending_lesson = self.pending_lesson, None
                        self.aborted = False
                        await self.send_lesson(txt)

    async def mic_rx(self):
        async for m in self.ws:
            if isinstance(m, bytes):
                if self.tts_on:
                    continue
                try:
                    pcm = self.dec.decode(m, IN_FRAME)
                except Exception:
                    continue
                if audioop.rms(pcm, 2) > 400:  # tieng noi gan nhat -> moc do do tre
                    self.t_user_end = time.time()
                if self.live is None:              # phien chua san sang -> dem
                    self.mic_buf.append(pcm)
                    if len(self.mic_buf) > MIC_BUF_MAX:
                        self.mic_buf.pop(0)
                    continue
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
                if self.gen_open or self.dev_on:
                    self.aborted = True
                    self.gen_open = False
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
        tasks = [asyncio.create_task(c()) for c in (self.live_main, self.mic_rx, self.pacer, self.idle_watch)]
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
            if self.handle is not None:
                await self.handle.close()

    async def live_main(self):
        self.handle = await self.pool.acquire()
        live = self.handle.live
        log(f"phien Live mo ({MODEL})")
        while self.mic_buf:                        # gui phan micro da dem, giu thu tu
            pcm = self.mic_buf.pop(0)
            await live.send_realtime_input(audio=types.Blob(data=pcm, mime_type=f"audio/pcm;rate={IN_RATE}"))
        self.live = live                           # khong await giua kiem tra rong va gan
        await self.gemini_rx()


async def ws_handler(ws, pool):
    log("thiet bi ket noi")
    try:
        await Session(ws, pool).run()
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
    pool = LivePool(client)
    asyncio.create_task(pool.maintain())
    app = web.Application()
    app.router.add_route("*", "/xiaozhi/ota/", ota_handler)
    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", HTTP_PORT).start()
    async with websockets.serve(lambda ws: ws_handler(ws, pool), "0.0.0.0", WS_PORT, max_size=None,
                                ping_interval=None):
        log(f"Cau noi san sang: ws://{lan_ip()}:{WS_PORT}/xiaozhi/v1/  OTA: http://{lan_ip()}:{HTTP_PORT}/xiaozhi/ota/")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
