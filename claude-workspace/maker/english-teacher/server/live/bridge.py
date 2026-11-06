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
LANG_CODE = os.environ.get("STLAB_LIVE_LANG", "vi-VN").strip()   # khoa ngon ngu noi; rong = tat
IN_RATE, OUT_RATE = 16000, 24000
RATE_BYTES = IN_RATE * 2              # 1 s PCM 16 kHz s16le
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


from curriculum import Curriculum, ALLOWED_NICKNAMES, live_tools, find_nickname, _fold  # noqa: E402
import voiceid  # noqa: E402


def _voice_enabled():
    """Nhan dien giong chi bat khi bo/me dong y (data/consent.json: parent_consent true) va co mo hinh."""
    try:
        c = json.loads((SERVER / "data" / "consent.json").read_text(encoding="utf-8"))
        if c.get("parent_consent") is not True:
            raise ValueError
    except Exception:
        print(time.strftime("%H:%M:%S ") + "[LIVE-VOICE] tat: khong co data/consent.json (parent_consent true)", flush=True)
        return None
    if not voiceid.MODEL.exists():
        print(time.strftime("%H:%M:%S ") + "[LIVE-VOICE] tat: chua co mo hinh (chay setup-voiceid.ps1)", flush=True)
        return None
    return voiceid.VoiceID(voiceid.default_store())


VOICE_ID = _voice_enabled()
VOICE_ENROLL = os.environ.get("VOICEID_ENROLL", "1") != "0"
ENROLL_TURNS = 3
ANON_LESSON = os.environ.get("STLAB_ANON_LESSON", "1") != "0"   # khong biet danh sau 2 luot be -> bai ngau nhien
NUDGE_S = float(os.environ.get("STLAB_NUDGE_S", "6"))   # be im bay nhieu giay sau luot co -> nhac
NUDGE_RMS = 400                       # nguong nang luong PCM: cung nguong 'dang noi' cua mic_rx (tieng be > ~1000, nen phong < 400)
BYE_WORDS = ("bye bye", "goodbye", "tam biet")
YES_WORDS = {"co", "dung", "vang", "u", "yes", "phai", "da"}
NO_WORDS = {"khong", "no", "sai"}

SILENCE_MS = int(os.environ.get("STLAB_LIVE_SILENCE_MS", "600"))

CUR = Curriculum(os.environ.get("STLAB_LEARNERS_PATH") or (SERVER / "data" / "learners.json"), SERVER.parent / "lessons")
CURRICULUM_PROMPT = (
    "\n\nAt the start, ask in Vietnamese which animal friend is learning today (e.g. bạn thỏ, bạn mèo, bạn gấu). "
    "Then wait. The system will send a [lesson] message with the lesson to follow. Until then, do not start a lesson "
    "and do not call tools. After a [lesson] message: treat it as goals and teach in your own fresh way; after the child repeats a vocabulary word call "
    "mark_word; at the end call finish_lesson then say a short goodbye. Never ask for real names. "
    "Listen carefully. If you are not sure what the child said, or the answer does not fit, do NOT guess: "
    "kindly ask again in Vietnamese ('Con nói lại cho cô nghe nhé?'), at most twice, then gently give the answer and move on."
)
LANG_LOCK = (
    "The child is a 2-5 year old Vietnamese child. They speak ONLY Vietnamese or a few English words, often mispronounced. "
    "If the speech sounds like any other language (Spanish, Japanese, Hindi...), it is unclear toddler speech - never answer "
    "in that language. Always reply ONLY in Vietnamese and simple English.\n"
    # 2026-11-06 Tuan: noi "da" co khong hieu; giong vung mien + giong con nit kho nghe
    "Vietnamese children answer with short polite words. Treat these as YES / 'I am here' / 'I am listening': "
    "dạ, dạ con, vâng, ừ, ờ, ừm, có, có ạ, có nè, nè, đây, ơi, dạ có, ok. Treat these as NO: không, hông, hổng, "
    "không ạ, hông có, chưa. Accents from the North, Central and South of Vietnam (e.g. 'dzạ', 'hông', 'zậy', 'hổng "
    "biết') and toddler pronunciation are normal Vietnamese - understand them kindly. Short sounds like 'dạ', 'ạ', "
    "'ơi' are answers, not noise: respond to them (e.g. continue the lesson). If you truly cannot tell what was said, "
    "guess the most likely simple meaning from the lesson context first; ask again only if it matters.\n\n")
LIMIT_PROMPT = (
    "\n\nRepeat limits: ask the child to repeat the SAME word at most 2 times in total; after that say a warm "
    "'Con giỏi lắm!' and move to a different word. Say 'nói lại nhé' at most once per turn. "
    "If the child or an adult says to speak louder/softer (to lên, nói lớn lên, nhỏ lại), call set_volume "
    "(or volume_change with +20 / -20 if you do not know the level).")
PROMPT = LANG_LOCK + load_prompt() + CURRICULUM_PROMPT + LIMIT_PROMPT
VOLUME_TOOLS = [
    {"name": "set_volume",
     "description": "Set the speaker volume of the toy, 0-100 (e.g. 80 = loud, 40 = quiet).",
     "parameters": {"type": "OBJECT", "properties": {"level": {"type": "INTEGER", "description": "0-100"}},
                    "required": ["level"]}},
    {"name": "volume_change",
     "description": "Change the speaker volume by a delta, e.g. +20 louder, -20 softer.",
     "parameters": {"type": "OBJECT", "properties": {"delta": {"type": "INTEGER", "description": "-50..50"}},
                    "required": ["delta"]}},
]
MCP_TIMEOUT_S = 4.0


# 2026-11-06 Tuan: co khong hieu "da", giong vung mien/con nit. Gemini Live transcription co language_codes + custom_vocabulary
# (ai.google.dev/gemini-api/docs/live-api/live-transcribe, toi da 1000 muc). Chi chac giup CHU NHAN DANG (bien danh, mark_word),
# khong chac giup phan hieu am thanh cua model -> do tren thiet bi that. Tat bang STLAB_ASR_HINTS=0.
ANSWER_WORDS = ["dạ", "dạ con", "vâng", "ừ", "ờ", "có", "có ạ", "có nè", "không", "hông", "hổng", "không ạ", "chưa",
                "ơi", "cô ơi", "con biết", "con không biết", "hổng biết", "nữa", "lại", "to lên", "nói lớn lên", "nhỏ lại"]


def asr_vocab():
    v = list(ANSWER_WORDS) + ["bạn " + n for n in ALLOWED_NICKNAMES]
    try:
        for lid in CUR.lesson_ids():
            v += CUR.vocabulary(lid)
    except Exception:
        pass
    seen, out = set(), []
    for w in v:
        if w and w not in seen:
            seen.add(w); out.append(w)
    return out[:1000]


def in_transcription():
    if os.environ.get("STLAB_ASR_HINTS", "1") == "0":
        return types.AudioTranscriptionConfig()
    try:
        return types.AudioTranscriptionConfig(language_codes=["vi-VN", "en-US"], custom_vocabulary=asr_vocab())
    except Exception as e:
        log(f"ASR hints khong dung duoc: {e}")
        return types.AudioTranscriptionConfig()


def live_config():
    kw = dict(
        response_modalities=["AUDIO"],
        system_instruction=PROMPT,
        input_audio_transcription=in_transcription(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        tools=[types.Tool(function_declarations=live_tools() + VOLUME_TOOLS)],
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                end_of_speech_sensitivity=types.EndSensitivity.END_SENSITIVITY_HIGH,
                silence_duration_ms=SILENCE_MS)),
    )
    sp = {}
    if VOICE:
        sp["voice_config"] = types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE))
    if LANG_CODE:
        sp["language_code"] = LANG_CODE
    if sp:
        kw["speech_config"] = types.SpeechConfig(**sp)
    return types.LiveConnectConfig(**kw)


POOL = None


async def ota_handler(request):
    if POOL is not None:
        POOL.touch()   # bo vua khoi dong / goi OTA -> giu phien du phong san cho lan bam dau
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


WARM_WINDOW_S = int(os.environ.get("STLAB_WARM_WINDOW_S", "600"))   # giu phien du phong 10 ph sau hoat dong cuoi


class LivePool:
    def __init__(self, client):
        self.client = client
        self.standby = None
        self.taken = asyncio.Event()
        self.last_activity = time.time()   # bo hoat dong gan nhat (khoi dong may chu, OTA, ket noi, het phien)
        self.paused = False
        self.fail = 0

    def touch(self):
        self.last_activity = time.time()

    def warm(self):
        # 2026-11-06 Tuan duyet: chi giu phien du phong WARM_WINDOW_S sau lan bo hoat dong cuoi (Google dong phien ranh ~2 ph
        # -> mo lai ~30 phien/gio du khong ai noi, ton han muc mien phi)
        return time.time() - self.last_activity < WARM_WINDOW_S

    async def maintain(self):
        while True:
            if self.standby is None:
                if not self.warm():
                    if not self.paused:
                        log(f"tam dung phien du phong (bo khong hoat dong > {WARM_WINDOW_S} s)")
                        self.paused = True
                    await asyncio.sleep(2)
                    continue
                self.paused = False
                t0 = time.time()
                try:
                    h = await asyncio.wait_for(open_live(self.client), OPEN_TOTAL_S)
                except asyncio.CancelledError:
                    raise
                except BaseException as e:
                    self.fail += 1
                    wait = min(60, 3 * 2 ** (self.fail - 1))   # loi (vd het han muc 1011): cho tang dan, khong thu moi 3 s mai
                    log(f"phien du phong loi ({self.fail}): {type(e).__name__}: {str(e)[:120]} - thu lai sau {wait} s")
                    await asyncio.sleep(wait)
                    continue
                self.fail = 0
                self.standby = h
                self.taken.clear()
                log(f"phien du phong san sang ({int((time.time() - t0) * 1000)} ms)")
            try:
                await asyncio.wait_for(self.taken.wait(), timeout=5)
            except asyncio.TimeoutError:
                h = self.standby
                if h is not None and not self.warm():
                    log("dong phien du phong (het cua so hoat dong)")
                    self.standby = None
                    await h.close()
                elif h is not None and (time.time() - h.born >= STANDBY_MAX_S or not h.alive()):
                    log("phien du phong het han/dong, mo lai")
                    self.standby = None
                    await h.close()
                continue
            self.taken.clear()
            self.standby = None

    async def acquire(self):
        """Tra handle. Uu tien phien du phong; neu khong thi mo moi co hedge."""
        self.touch()
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
        self.turn_pcm = bytearray()        # PCM 16 kHz luot be dang noi (chi trong bo nho, bo sau khi dung)
        self.guess = None                  # biet danh doan tu giong, cho be xac nhan
        self.voice_tried = False
        self.enrolled = 0
        self.finishing = False             # da goi finish_lesson
        self.last_speech = 0.0
        self.bye_task = None
        self.end_done = False
        self.fast_stop = False
        self.anon_turns = 0
        self.anon_sent = False
        self.heard_at = 0.0
        self.silent_n = 0                  # so lan nhac lien tiep ma be van im
        self.nudge_task = None
        self.mcp_id = 100
        self.mcp_wait = {}                 # id -> Future (phan hoi MCP cua thiet bi)
        self.ending = False                # be bam KEY4 xin ket thuc (abort luc co khong noi)

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
                    self.finishing = True
                    log(f"[LIVE-TOOL] finish_lesson -> {res.get('next_lesson')}")
                elif fc.name in ("set_volume", "volume_change"):
                    res = await self.do_volume(fc.name, a)
                else:
                    res = {"error": "unknown tool"}
            except Exception as e:
                res = {"error": type(e).__name__}
            resps.append(types.FunctionResponse(id=fc.id, name=fc.name, response=res))
        if resps:
            await self.live.send_tool_response(function_responses=resps)

    async def mcp_call(self, method, params=None):
        """JSON-RPC toi thiet bi qua {"type":"mcp","payload":...}; doi phan hoi MCP_TIMEOUT_S giay."""
        self.mcp_id += 1
        mid = self.mcp_id
        fut = asyncio.get_running_loop().create_future()
        self.mcp_wait[mid] = fut
        msg = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        try:
            await self.send_json({"type": "mcp", "session_id": self.sid, "payload": msg})
            return await asyncio.wait_for(fut, MCP_TIMEOUT_S)
        finally:
            self.mcp_wait.pop(mid, None)

    async def do_volume(self, name, a):
        try:
            if name == "set_volume":
                level = int(a.get("level"))
            else:
                st = await self.mcp_call("tools/call", {"name": "self.get_device_status", "arguments": {}})
                txt = "".join(c.get("text", "") for c in (st.get("result") or {}).get("content", []))
                cur = int(json.loads(txt)["audio_speaker"]["volume"])
                level = cur + int(a.get("delta"))
            level = max(0, min(100, level))
            r = await self.mcp_call("tools/call", {"name": "self.audio_speaker.set_volume", "arguments": {"volume": level}})
            if "error" in r:
                log(f"[LIVE-TOOL] volume {level} loi thiet bi: {str(r['error'])[:80]}")
                return {"ok": False, "error": "device refused"}
            log(f"[LIVE-TOOL] volume {level}")
            return {"ok": True, "volume": level}
        except Exception as e:
            log(f"[LIVE-TOOL] volume loi {type(e).__name__}: {str(e)[:80]}")
            return {"ok": False, "error": type(e).__name__}

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
                await asyncio.sleep(PRE_BUFFER * FRAME_S if n and not self.fast_stop else 0)
                self.fast_stop = False
                n = 0
                if self.dev_on:
                    self.dev_on = False
                    dbg("tts stop")
                    await self.send_json({"type": "tts", "state": "stop", "session_id": self.sid})
                    if self.ending:
                        asyncio.create_task(self.end_close(0.4))
                    elif not self.finishing and not any(w in _fold(self.reply_txt)[-40:] for w in BYE_WORDS):
                        if self.nudge_task:
                            self.nudge_task.cancel()
                        self.nudge_task = asyncio.create_task(self.nudge_watch(time.time()))
                    tail = _fold(self.reply_txt)[-40:]
                    if not self.ending and self.finishing or any(w in tail for w in BYE_WORDS):
                        if self.bye_task:
                            self.bye_task.cancel()
                        self.bye_task = asyncio.create_task(self.bye_close(time.time()))
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

    async def tell_interrupted(self):
        try:
            await self.live.send_client_content(
                turns=types.Content(role="user", parts=[types.Part(text="[interrupted] The child interrupted you. Stop and listen.")]),
                turn_complete=False)
        except Exception as e:
            dbg(f"interrupted loi {type(e).__name__}")

    async def nudge_watch(self, stop_t):
        """Sau luot co, be im NUDGE_S giay -> nhac be (toi da 2 lan nhac, lan 3 chuyen tu, lan 4 tam biet + dong)."""
        await asyncio.sleep(NUDGE_S)
        if (self.closed or self.ending or self.finishing or self.tts_on or self.gen_open or self.dev_on
                or self.last_speech > stop_t or self.heard_at > stop_t or self.live is None):
            return
        self.silent_n += 1
        n = self.silent_n
        log(f"[LIVE-T] nhac be (lan {n})")
        if n <= 2:
            await self.send_lesson("[silence] The child has not answered. Gently encourage in Vietnamese and make it easier: "
                                   "repeat the question more simply, or say the answer and ask the child to repeat it "
                                   "(e.g. 'Con nói theo cô nhé: red!') ONLY if you have not asked for that word twice already. "
                                   "One or two short sentences.")
        elif n == 3:
            await self.send_lesson("[silence] Still no answer. Move on to the next word kindly.")
        else:
            await self.end_request()
            return
        await asyncio.sleep(5)                 # Gemini khong tra loi loi nhac -> van nhac tiep (khong dung giua chung)
        if not (self.closed or self.tts_on or self.gen_open or self.dev_on):
            self.nudge_task = asyncio.create_task(self.nudge_watch(time.time()))

    async def end_close(self, delay):
        await asyncio.sleep(delay)
        if self.closed or self.end_done:
            return
        self.end_done = True
        log("[LIVE-T] be xin ket thuc -> tam biet -> dong")
        await self.ws.close()

    async def end_request(self):
        """Be cham KEY4 luc thiet bi dang nghe (abort khi co khong noi): luu tien do, co chao tam biet roi dong."""
        if self.ending or self.live is None:
            if self.live is None:
                await self.end_close(0)
            return
        self.ending = True
        self.pending_lesson = None
        self.aborted = False
        if self.nick:
            try:
                res = CUR.finish(self.nick)
                log(f"[LIVE-TOOL] finish_lesson (be xin ket thuc) -> {res.get('next_lesson')}")
            except Exception as e:
                log(f"finish loi {type(e).__name__}")
        await self.send_lesson("[end] The child wants to stop now. Say one short warm goodbye "
                               "(Vietnamese + 'bye bye'), no questions.")
        await asyncio.sleep(3)
        if not (self.gen_open or self.dev_on or self.tts_on):
            await self.end_close(0)

    async def bye_close(self, stop_t):
        """Sau cau tam biet, be im 4 s -> dong ket noi de thiet bi ve nghi."""
        await asyncio.sleep(4)
        if self.tts_on or self.last_speech > stop_t or self.closed:
            self.finishing = False
            return
        log("[LIVE-T] ket thuc phien sau tam biet")
        await self.ws.close()

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

    async def after_turn(self):
        """Het luot be noi: ghi giong (da co biet danh) hoac doan be tu giong (chua co). PCM bo ngay sau do."""
        pcm, self.turn_pcm = bytes(self.turn_pcm), bytearray()
        if VOICE_ID is None or len(pcm) < RATE_BYTES:
            return
        loop = asyncio.get_running_loop()
        try:
            if self.nick:
                if VOICE_ENROLL and self.enrolled < ENROLL_TURNS:
                    if await loop.run_in_executor(None, VOICE_ID.enroll, self.nick, pcm):
                        self.enrolled += 1
                        log(f"[LIVE-VOICE] ghi giong {self.nick} ({self.enrolled}/{ENROLL_TURNS})")
            elif not self.voice_tried and not self.guess and not self.pending_lesson:
                nick, score = await loop.run_in_executor(None, VOICE_ID.identify, pcm)
                if score > 0:
                    self.voice_tried = True
                if nick and nick in ALLOWED_NICKNAMES and not self.pending_lesson:
                    log(f"[LIVE-VOICE] nhan {nick} ({score:.2f})")
                    self.guess = nick
                    self.pending_lesson = (f"[lesson] The child's voice sounds like bạn {nick}, but you are not sure. "
                                           f"Ask in Vietnamese, one short sentence: \"Có phải bạn {nick} không?\" and wait. "
                                           "Do not start a lesson and do not call tools yet.")
                    self.mute_current_turn()
                    asyncio.create_task(self.lesson_timeout())
        except Exception as e:
            log(f"[LIVE-VOICE] loi {type(e).__name__}")

    def check_nick(self):
        """Be nhan biet danh: cau noi tu goi Curriculum.start va nho Gemini bat dau bai."""
        if self.nick or self.pending_lesson:
            return
        nick = find_nickname(self.in_buf)
        if not nick and self.guess:
            w = set(_fold(self.in_buf).split())
            if w & NO_WORDS:
                log(f"[LIVE-VOICE] be noi khong ({self.guess})")
                self.guess = None
                self.pending_lesson = ("[lesson] The child said no. Say sorry kindly in Vietnamese and ask which animal friend "
                                       "is learning today (bạn thỏ, bạn mèo, bạn gấu…). Do not call tools yet.")
                self.mute_current_turn()
                asyncio.create_task(self.lesson_timeout())
                return
            if w & YES_WORDS:
                nick = self.guess
        if not nick:
            return
        self.guess = None
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
                    self.heard_at = time.time()
                    self.silent_n = 0
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
                if (sc.model_turn and not self.aborted and not self.gen_open and VOICE_ID is not None
                        and any(p.inline_data and p.inline_data.data for p in sc.model_turn.parts or [])):
                    await self.after_turn()
                if sc.model_turn and not self.aborted:
                    for p in sc.model_turn.parts or []:
                        if p.inline_data and p.inline_data.data:
                            self.tts_start()
                            self.push_pcm(p.inline_data.data)
                if sc.turn_complete:
                    await self.after_turn()
                    dbg(f"turn_complete gen_open={self.gen_open} dev_on={self.dev_on}")
                    if self.gen_open or self.pcm_buf:
                        self.end_turn()
                    else:
                        self.aborted = False
                        if not self.dev_on and self.out_q.empty():
                            self.user_txt, self.reply_txt, self.t_user_end = "", "", None
                    if self.in_buf.strip() and not (self.nick or self.guess or self.pending_lesson or self.ending):
                        self.anon_turns += 1
                        if self.anon_turns >= 2 and not self.anon_sent and ANON_LESSON:
                            self.anon_sent = True
                            lid, instr = CUR.anonymous_lesson()
                            log(f"[LIVE-TOOL] khong co biet danh sau 2 luot -> bai ngau nhien {lid}")
                            self.pending_lesson = ("[lesson] No nickname was given. Say kindly that today we learn together, "
                                                   f"and start this lesson now (do not call mark_word/finish_lesson). {instr}")
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
                    self.t_user_end = self.last_speech = time.time()
                    self.silent_n = 0
                if VOICE_ID is not None:
                    self.turn_pcm += pcm
                    if len(self.turn_pcm) > RATE_BYTES * 20:
                        del self.turn_pcm[:-RATE_BYTES * 20]
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
            elif t == "mcp":
                pl = j.get("payload") or {}
                fut = self.mcp_wait.get(pl.get("id")) if isinstance(pl, dict) else None
                if fut is not None and not fut.done():
                    fut.set_result(pl)
            elif t == "abort":
                if j.get("reason") == "wake_word_detected":      # be cham KEY4 luc thiet bi nghe -> xin ket thuc
                    asyncio.create_task(self.end_request())
                    continue
                # abort khong reason = be ngat loi: dung phat, bo phan Gemini con sinh, cho be noi tiep
                self.clear_out()
                if self.gen_open or self.dev_on or self.tts_on:
                    self.fast_stop = True
                    self.aborted = True
                    self.gen_open = False
                    self.out_q.put_nowait("STOP")
                    if self.live is not None:
                        asyncio.create_task(self.tell_interrupted())
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
        asyncio.create_task(self.mcp_init())
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

    async def mcp_init(self):
        try:
            await self.mcp_call("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                               "clientInfo": {"name": "stlab-live-bridge", "version": "1"}})
            await self.mcp_call("tools/list", {})
        except Exception as e:
            dbg(f"mcp init {type(e).__name__}")   # thiet bi khong co MCP: bo qua

    async def live_main(self):
        self.handle = await self.pool.acquire()
        live = self.handle.live
        log(f"phien Live mo ({MODEL})")
        while self.mic_buf:                        # gui phan micro da dem, giu thu tu
            pcm = self.mic_buf.pop(0)
            await live.send_realtime_input(audio=types.Blob(data=pcm, mime_type=f"audio/pcm;rate={IN_RATE}"))
        self.live = live                           # khong await giua kiem tra rong va gan
        await self.send_lesson("[session start] Greet the child warmly in Vietnamese in one short sentence and ask which "
                               "animal friend is learning today (bạn thỏ, bạn mèo, bạn gấu…).")
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
        pool.touch()


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
    global POOL
    pool = POOL = LivePool(client)
    if VOICE_ID is not None:
        await asyncio.get_running_loop().run_in_executor(None, voiceid._get_extractor)
        log(f"[LIVE-VOICE] bat (ho so: {len(VOICE_ID.list())}, ghi giong: {'bat' if VOICE_ENROLL else 'tat'})")
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
