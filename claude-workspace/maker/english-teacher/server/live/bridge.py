"""Cau noi xiaozhi <-> Gemini Live cho ESP32-A1S (firmware xiaozhi v2.5.2, khong sua firmware).
CHI NGUOI LON THU NOI BO (dieu khoan Gemini API cam dich vu cho tre < 18 tuoi).
Bien: GOOGLE_API_KEY (bat buoc), STLAB_LIVE_WS_PORT (8000), STLAB_LIVE_HTTP_PORT (8003), STLAB_XIAOZHI_SERVER (IP LAN),
STLAB_LIVE_MODEL (gemini-3.8-live), STLAB_LIVE_VOICE (tuy chon).
"""
import asyncio
import unicodedata, audioop, json, os, random, re, socket, sys, time, uuid
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
IDLE_S = float(os.environ.get("STLAB_IDLE_S", "300"))   # 2026-11-07 Tuan: co chao tam biet som qua -> chi tam dung sau 5 ph khong noi


DEBUG = bool(os.environ.get("STLAB_LIVE_DEBUG"))


def dbg(msg):
    if DEBUG:
        log("[dbg] " + msg)


def log(msg):
    print(time.strftime("%H:%M:%S ") + msg, flush=True)


# ---- Truy cap tu internet qua VPS (Tuan 2026-11-11): domain -> Caddy (VPS) -> frp -> may lab ----
# STLAB_PUBLIC_HOST   : vd teacher.example.vn -> OTA tra wss://<host>/xiaozhi/v1/ (rong = LAN nhu cu)
# STLAB_DEVICE_TOKEN  : bi mat dung chung (bien moi truong, KHONG ghi file); bat buoc khi co PUBLIC_HOST
# STLAB_ALLOWED_DEVICES: MAC cac bo duoc phep, cach nhau dau phay (vd e0:8c:fe:64:20:a4)
import hmac  # noqa: E402


def _allowed_devices():
    return {x.strip().lower() for x in os.environ.get("STLAB_ALLOWED_DEVICES", "").split(",") if x.strip()}


def check_public_config():
    """Bat domain ma thieu token/danh sach bo -> dung han (khong chay cong khai khong khoa)."""
    if os.environ.get("STLAB_PUBLIC_HOST", "").strip():
        if len(os.environ.get("STLAB_DEVICE_TOKEN", "").strip()) < 24 or not _allowed_devices():
            raise SystemExit("STLAB_PUBLIC_HOST da dat nhung thieu STLAB_DEVICE_TOKEN (>= 24 ky tu) "
                             "hoac STLAB_ALLOWED_DEVICES -> khong chay.")


def device_allowed(device_id):
    allow = _allowed_devices()
    return not allow or (device_id or "").strip().lower() in allow


def authorize(headers):
    """WebSocket: co token thi bat buoc 'Authorization: Bearer <token>' + device-id trong danh sach."""
    token = os.environ.get("STLAB_DEVICE_TOKEN", "").strip()
    dev = headers.get("device-id") or headers.get("Device-Id") or ""
    if not device_allowed(dev):
        return False
    if not token:
        return True
    got = (headers.get("authorization") or headers.get("Authorization") or "").strip()
    if got.lower().startswith("bearer "):
        got = got[7:].strip()
    return hmac.compare_digest(got.encode(), token.encode())


def public_ws_url():
    host = os.environ.get("STLAB_PUBLIC_HOST", "").strip()
    return f"wss://{host}/xiaozhi/v1/" if host else f"ws://{lan_ip()}:{WS_PORT}/xiaozhi/v1/"


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


from curriculum import Curriculum, ALLOWED_NICKNAMES, live_tools, find_nickname, _fold, wants_switch  # noqa: E402
import voiceid  # noqa: E402
from duplex import BargeGate  # noqa: E402
import music  # noqa: E402
from intent import parse_volume_intent, music_requested  # noqa: E402
from tuning import Tuning, Agc, BOUNDS  # noqa: E402


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
NUDGE_S = float(os.environ.get("STLAB_NUDGE_S", "6"))   # be im bay nhieu giay sau luot co -> nhac (lan 1)
NUDGE_GAPS = (NUDGE_S, 12.0, 20.0, 40.0)   # nhac gian dan
NUDGE_RMS = 400                       # nguong nang luong PCM: cung nguong 'dang noi' cua mic_rx (tieng be > ~1000, nen phong < 400)
BYE_WORDS = ("bye bye", "goodbye", "tam biet")
YES_WORDS = {"co", "dung", "vang", "u", "yes", "phai", "da"}
NO_WORDS = {"khong", "no", "sai"}

SILENCE_MS = int(os.environ.get("STLAB_LIVE_SILENCE_MS", "600"))
START_SENS = os.environ.get("STLAB_LIVE_START_SENS", "low").strip().lower()   # low = kho bi nhac/nen kich hoat
PREFIX_PAD_MS = int(os.environ.get("STLAB_LIVE_PREFIX_MS", "300"))
VAD_GATE = os.environ.get("STLAB_VAD_GATE", "1") != "0"           # cong loc giong nguoi (Silero) truoc Gemini
VAD_THRESHOLD = float(os.environ.get("STLAB_VAD_THRESHOLD", "0.5"))
# Nguong ngat loi (barge_threshold/barge_ms) + AGC nam o tuning.py (data/tuning.json, tu chinh khi dung that + chinh bang giong);
# STLAB_BARGE_THRESHOLD/STLAB_BARGE_MS chi la gia tri khoi dau khi chua co file. Mac dinh 0.85/600 ms (2026-11-12, tieng vong cua co).
TUNING = Tuning()
TECH_PHRASE = "che do ky thuat"       # nguoi lon noi "che do ky thuat" -> mo tech_mode
TECH_MODE_S = 600.0
DUMP_WAV = os.environ.get("STLAB_DUMP_WAV", "1") != "0"   # 2026-11-12 Tuan dong y: thu am chan doan (am thanh tho may chu nhan), luu runtime/dump, tu xoa sau 1 ngay
DUMP_DIR = RUNTIME / "dump"
DUMP_MAX_S = 90


def write_dump(pcm, tag):
    """Ghi PCM 16 kHz mono ra runtime/dump/<gio>-<tag>.wav; xoa file > 1 ngay. Khong gui di dau."""
    import wave
    try:
        DUMP_DIR.mkdir(parents=True, exist_ok=True)
        for f in DUMP_DIR.glob("*.wav"):
            if time.time() - f.stat().st_mtime > 86400:
                f.unlink()
        if len(pcm) < RATE_BYTES:      # < 1 s: bo
            return None
        p = DUMP_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{tag}.wav"
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(IN_RATE); w.writeframes(bytes(pcm))
        return p
    except Exception as e:
        log(f"[DUMP] loi {type(e).__name__}: {e}")
        return None


S3_SIMPLE = os.environ.get("STLAB_S3_SIMPLE", "1") != "0"   # 2026-11-12 Tuan "dua ve goc": bo S3 chi Silero VAD + BargeGate, bo cong muc/AGC/tu hoc
BARGE_CHECK_S = 6.0                   # sau [BARGE] cho bay nhieu giay de phan loai ngat nham (2026-11-12: 3 -> 6 s vi chu Gemini den tre)

CUR = Curriculum(os.environ.get("STLAB_LEARNERS_PATH") or (SERVER / "data" / "learners.json"),
                 Path(os.environ["STLAB_LESSONS_DIR"]) if os.environ.get("STLAB_LESSONS_DIR") else (SERVER.parent / "lessons-seed"))
CUR.free_flag = os.environ.get("STLAB_FREE_FLAG") or (SERVER / "free-lesson.on")   # co file -> Gemini tu len bai (2026-11-08)
CURRICULUM_PROMPT = (
    "\n\nAt the start, ask in Vietnamese which animal friend is learning today (offer 2-3 different animal names each time, as the system tells you). "
    "When the child tells their animal name (bạn …), immediately greet them warmly by that name in ONE short sentence "
    "(e.g. 'Chào bạn Mèo! Cô vui quá!') and wait for the [lesson] message; do not start teaching before it. "
    "Then wait. The system will send a [lesson] message with the lesson to follow. Until then, do not start a lesson "
    "and do not call tools. After a [lesson] message: treat it as goals and teach in your own fresh way; after the child repeats a vocabulary word call "
    "mark_word; when the lesson goals are done call finish_lesson, then keep playing and reviewing words in a fun way. The lesson is only the DEFAULT plan, never a fence: you can talk with the child and adults about anything child-safe "
    "(answer warmly and briefly, you may slip in one related simple English word), and when they ask to learn or talk about "
    "another topic (e.g. 'dạy con về hoa') call change_topic with the topic and 1-3 simple English words, then follow the "
    "instructions it returns. NEVER say goodbye or end the session on your own - only when you receive an [end] message. Teaching the WORD 'goodbye' is fine. Never ask for real names. "
    "You are free to teach in your own way, adapted to the child's age (see HOW YOU TEACH at the top). If you are not sure "
    "what the child said, you may say 'Cô chưa nghe rõ, con nói lại cho cô nhé!'."
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
    "guess the meaning from the lesson context when answering a lesson question, but NEVER call a tool (play_music, "
    "finish_lesson, change_topic...) when you did not hear clearly - ask again: 'Cô chưa nghe rõ, con nói lại nhé!'.\n\n")
LIMIT_PROMPT = (
    "\n\nIf the child or an adult says to speak louder/softer (to lên, nói lớn lên, nhỏ lại), call set_volume "
    "(or volume_change with +20 / -20 if you do not know the level). Vietnamese volume phrases: mở to, mở lớn, to nữa, "
    "tối đa, hết cỡ, lớn nhất, âm lượng -> set_volume (tối đa / hết cỡ = 100). The word 'mở' alone, without nhạc/bài/hát, "
    "is NOT play_music.")
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
MUSIC_TOOLS = [
    dict(name="play_music",
         description=("Play a song/music file stored on the server for the child. query = song name or words from it "
                      "(empty string = any song). Only when someone asked for music. The song plays by itself; stay silent until it ends. "
                      "If someone speaks during the song, the music stops; answer them."),
         parameters={"type": "OBJECT", "properties": {"query": {"type": "STRING", "description": "song name, may be empty"}}}),
    dict(name="stop_music", description="Stop the music that is playing.", parameters={"type": "OBJECT", "properties": {}}),
    dict(name="list_music", description="List the song titles that can be played.", parameters={"type": "OBJECT", "properties": {}}),
]
TECH_TOOLS = [
    dict(name="tech_tune",
         description=("TECH MODE only (an adult opened it). Adjust a setting. param: 'mic' (microphone loudness target), "
                      "'barge' (how hard it is for the voice to interrupt you), 'gain' (max mic boost). "
                      "action: 'up', 'down' or a number. Returns the new values."),
         parameters={"type": "OBJECT", "properties": {"param": {"type": "STRING", "description": "mic | barge | gain"},
                                                      "action": {"type": "STRING", "description": "up | down | number"}},
                     "required": ["param", "action"]}),
    dict(name="tech_report",
         description="TECH MODE only. Read the current tuning values and the last 3 changes.",
         parameters={"type": "OBJECT", "properties": {}}),
]
MCP_TIMEOUT_S = 4.0
FORCE_SWITCH = os.environ.get("STLAB_FORCE_SWITCH", "0").strip() == "1"
LOCK_DEVICE_NICK = os.environ.get("STLAB_LOCK_DEVICE_NICK", "1").strip() != "0"   # bo da co biet danh trong devices.json -> khoa


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
        tools=[types.Tool(function_declarations=live_tools() + VOLUME_TOOLS + MUSIC_TOOLS + TECH_TOOLS)],
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                start_of_speech_sensitivity=(types.StartSensitivity.START_SENSITIVITY_HIGH if START_SENS == "high"
                                             else types.StartSensitivity.START_SENSITIVITY_LOW),
                prefix_padding_ms=PREFIX_PAD_MS,
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
    dev = request.headers.get("device-id") or request.headers.get("Device-Id") or ""
    if not device_allowed(dev):
        log(f"OTA tu choi thiet bi la {dev[:20]!r}")
        return web.json_response({"error": "device not allowed"}, status=403)
    body = {
        "server_time": {"timestamp": int(round(time.time() * 1000)), "timezone_offset": 7 * 60},
        "firmware": {"version": ver, "url": ""},
        "websocket": {"url": public_ws_url(), "token": os.environ.get("STLAB_DEVICE_TOKEN", "").strip()},
    }
    return web.json_response(body)


STANDBY_MAX_S = 480.0      # phien du phong khong dung qua 8 phut -> dong, mo lai
HEDGE_AFTER_S = 2.0
OPEN_TOTAL_S = 10.0
SESSION_START_LAST = {}
NICK_SET_LAST = {}         # device-id -> bo biet danh lan truoc (de doi bo moi)
_lp = os.environ.get("STLAB_LEARNERS_PATH")
DEVICES_PATH = (Path(_lp).with_name(Path(_lp).stem + "-devices.json") if _lp else SERVER / "data" / "devices.json")
DEVICE_NICK = {}


def _devices_load():
    try:
        d = json.loads(DEVICES_PATH.read_text(encoding="utf-8"))
        DEVICE_NICK.update({k: v for k, v in d.items() if isinstance(v, str) and v in ALLOWED_NICKNAMES})
    except Exception:
        pass


def device_nick_save(dev, nick):
    """Nho biet danh gan nhat theo device-id (chi device-id -> biet danh)."""
    if not dev or DEVICE_NICK.get(dev) == nick:
        return
    DEVICE_NICK[dev] = nick
    try:
        DEVICES_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEVICES_PATH.write_text(json.dumps(DEVICE_NICK, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"devices.json loi {type(e).__name__}")


_devices_load()    # device-id -> kieu mo dau lan truoc
MUSIC_BARGE_MS = float(os.environ.get("STLAB_MUSIC_BARGE_MS", "500"))   # giong lien tuc luc nhac -> dung nhac
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
        self.vad = None
        if VAD_GATE:
            try:
                from vad_gate import VadGate
                self.vad = VadGate(SERVER, VAD_THRESHOLD, log=log)
            except Exception as e:
                log(f"[LIVE-VAD] khong bat duoc ({type(e).__name__}: {str(e)[:100]}), dung micro tho")
        self.device_id = ""
        self.dev_mode = False              # hoc theo MAY (khong biet danh): ho so luu theo device-id
        self.switches = 0
        self.enc = opuslib_next.Encoder(OUT_RATE, 1, opuslib_next.APPLICATION_AUDIO)
        self.sid = uuid.uuid4().hex
        self.out_q = asyncio.Queue()       # bytes Opus | "STOP" marker
        self.pcm_buf = b""
        self.tts_on = False
        self.full_duplex = False           # bo S3 realtime (listen mode "realtime"): luc co noi van nghe mic; A1S = False
        self.barge = BargeGate(TUNING.get("barge_threshold"), TUNING.get("barge_ms"), 60)
        self.dump_pcm = bytearray()        # am thanh tho may chu nhan (STLAB_DUMP_WAV)
        self.agc = Agc(TUNING.get("agc_target_dbfs"), TUNING.get("agc_max_gain_db"))
        self.tech_until = 0.0              # che do ky thuat (nguoi lon): het han luc nay
        self.barge_pending = None          # {"t", "reply", "acc"} sau [BARGE], cho phan loai false
        self.voice_seen_t = 0.0            # lan cuoi VadGate thay giong nguoi luc co dang noi (phat hien 'missed')
        self.aborted = False               # bo am thanh toi het luot hien tai
        self.last_active = time.time()
        self.t_user_end = None
        self.user_txt, self.reply_txt = "", ""
        self.prev_user_txt = ""            # loi nguoi luot truoc (cho chan play_music)
        self.vol_local_t = 0.0             # luc VOL-LOCAL gan nhat (chong ap am luong 2 lan)
        self.vol_local_done = False        # luot nay da xu ly lenh am luong
        self.music_voice_ms = 0.0          # giong lien tuc luc phat nhac (full_duplex)
        self.music_held = []
        self.music_pass_until = 0.0
        self.first_ms = None
        self.live = None
        self.closed = False
        self.nick = None                   # biet danh cua ket noi nay
        self.t_open, self.child_turns = time.time(), 0   # tinh buoi: thoi luong + luot be noi
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
        self.prefilled = False             # biet danh lay tu bo nho thiet bi (be co the doi bang 'ban <khac>')
        self.nick_log = None               # (biet danh, ms sau het tieng be) cho log do tre
        self.m_replies = []                # loi co theo luot (chi de dem chi so, khong ghi ra log)
        self.m_silence = 0                 # so lan nhac be im
        self.ending = False                # be bam KEY4 xin ket thuc (abort luc co khong noi)
        self.music_task = None             # tac vu phat nhac (play_music); None = khong phat

    async def handle_tool_call(self, tc):
        resps = []
        for fc in tc.function_calls or []:
            a = dict(fc.args or {})
            try:
                if fc.name == "mark_word":
                    res = CUR.mark(self.nick, a.get("word", ""), bool(a.get("correct")), device=self.device_id or None) if (self.nick or self.dev_mode) else {"ok": False}
                    log(f"[LIVE-TOOL] mark_word {a.get('word', '')} {bool(a.get('correct'))}")
                elif fc.name == "finish_lesson":
                    res = CUR.finish(self.nick, time.time() - self.t_open, self.child_turns, device=self.device_id or None) if (self.nick or self.dev_mode) else {"next_lesson": None}
                    self.finishing = True
                    log(f"[LIVE-TOOL] finish_lesson -> {res.get('next_lesson')}")
                elif fc.name == "change_topic":
                    res = CUR.set_topic(self.nick, device=(self.device_id or None) if self.dev_mode else None,
                                        topic=a.get("topic", ""), words=list(a.get("words") or []))
                    log(f"[LIVE-TOOL] doi chu de '{str(a.get('topic', ''))[:40]}' -> {res.get('words')}")
                elif fc.name in ("set_volume", "volume_change"):
                    res = await self.do_volume(fc.name, a)
                elif fc.name == "play_music":
                    res = await self.do_play_music(str(a.get("query") or ""))
                elif fc.name == "stop_music":
                    res = {"ok": True, "was_playing": self.stop_music("gemini stop_music")}
                elif fc.name == "list_music":
                    res = {"songs": music.list_tracks()[:50]}
                elif fc.name == "tech_tune":
                    res = self.do_tech_tune(str(a.get("param") or ""), str(a.get("action") or ""))
                elif fc.name == "tech_report":
                    res = self.do_tech_report()
                else:
                    res = {"error": "unknown tool"}
            except Exception as e:
                res = {"error": type(e).__name__}
            resps.append(types.FunctionResponse(id=fc.id, name=fc.name, response=res))
        if resps:
            await self.live.send_tool_response(function_responses=resps)

    # ---- Tu chinh nguong: chinh bang giong (tech_mode) + phan loai ngat nham/bo sot ----
    @property
    def tech_mode(self):
        return time.time() < self.tech_until

    def tech_values(self):
        return {k: TUNING.get(k) for k in BOUNDS}

    def do_tech_tune(self, param, action):
        if not self.tech_mode:
            return {"error": "chua mo che do ky thuat"}
        param, action = param.strip().lower(), action.strip().lower()
        try:
            num = float(action.replace(",", "."))
        except ValueError:
            num = None
        if action not in ("up", "down") and num is None:
            return {"error": "action phai la up/down/so"}
        sign = 1 if action == "up" else -1
        reason = "voice"
        if param == "mic":
            TUNING.set("agc_target_dbfs", TUNING.get("agc_target_dbfs") + 2 * sign if num is None else num, reason)
        elif param == "gain":
            TUNING.set("agc_max_gain_db", TUNING.get("agc_max_gain_db") + 3 * sign if num is None else num, reason)
        elif param == "barge":
            if num is None:
                TUNING.set("barge_threshold", TUNING.get("barge_threshold") + 0.03 * sign, reason)
                TUNING.set("barge_ms", TUNING.get("barge_ms") + 80 * sign, reason)
            elif num <= 1.0:
                TUNING.set("barge_threshold", num, reason)
            else:
                TUNING.set("barge_ms", num, reason)
        else:
            return {"error": "param phai la mic/barge/gain"}
        self.apply_tuning()
        vals = self.tech_values()
        log(f"[TUNE] voice {param} {action} -> {vals}")
        return {"ok": True, "values": vals}

    def do_tech_report(self):
        if not self.tech_mode:
            return {"error": "chua mo che do ky thuat"}
        return {"values": self.tech_values(),
                "last_changes": [{k: h.get(k) for k in ("param", "old", "new", "reason")} for h in TUNING.recent(3)]}

    def apply_tuning(self):
        """Nap gia tri Tuning moi nhat vao BargeGate + Agc cua phien nay (goi moi khung mic, re)."""
        self.barge.threshold = float(TUNING.get("barge_threshold"))
        self.barge.hold_ms = float(TUNING.get("barge_ms"))
        self.agc.configure(TUNING.get("agc_target_dbfs"), TUNING.get("agc_max_gain_db"))

    @staticmethod
    def _norm_txt(s):
        s = unicodedata.normalize("NFD", (s or "").lower().replace("đ", "d"))
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return re.sub(r"[^a-z0-9 ]+", " ", s).split()

    def echo_like(self, heard, reply):
        """Loi 'nghe duoc' sau barge giong cau co vua noi (>= 0,6) -> tieng vong bi nhan thanh loi."""
        import difflib
        a, b = " ".join(self._norm_txt(heard)), " ".join(self._norm_txt(reply))
        if not a or not b:
            return False
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        matched = sum(m.size for m in sm.get_matching_blocks())
        return matched / len(a) >= 0.6

    def barge_started(self, reply):
        self.barge_pending = p = {"t": time.time(), "reply": reply, "acc": ""}
        asyncio.create_task(self.barge_judge(p))

    def barge_heard(self, text):
        p = self.barge_pending
        if p is None:
            return
        if time.time() - p["t"] > BARGE_CHECK_S:
            return
        p["acc"] += text
        if self.echo_like(p["acc"], p["reply"]):
            self.barge_pending = None
            self.tune_outcome_false()

    async def barge_judge(self, p):
        await asyncio.sleep(BARGE_CHECK_S)
        if self.barge_pending is not p:
            return
        self.barge_pending = None
        if not p["acc"].strip() or self.echo_like(p["acc"], p["reply"]):
            self.tune_outcome_false()          # khong ai noi that sau khi ngat (hoac chi la vong) -> ngat nham

    def tune_outcome_false(self):
        if (not S3_SIMPLE and TUNING.on_barge_outcome("false")):
            log(f"[TUNE] barge false -> barge_threshold {TUNING.get('barge_threshold')} barge_ms {TUNING.get('barge_ms')}")

    def tune_outcome_missed(self):
        if (not S3_SIMPLE and TUNING.on_barge_outcome("missed")):
            log(f"[TUNE] barge missed -> barge_threshold {TUNING.get('barge_threshold')} barge_ms {TUNING.get('barge_ms')}")

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
        if time.time() - self.vol_local_t < 4.0:
            log("[VOL-LOCAL] Gemini cung goi volume -> bo qua (da ap)")
            return {"ok": True, "note": "already applied"}
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

    async def vol_local(self):
        """Lenh am luong bat tai cau noi (tu transcript), khong cho Gemini; 1 lan moi luot."""
        if self.vol_local_done:
            return
        it = parse_volume_intent(self.in_buf)
        if it is None:
            return
        self.vol_local_done = True
        if it[0] == "set":
            r = await self.do_volume("set_volume", {"level": it[1]})
        else:
            r = await self.do_volume("volume_change", {"delta": it[1]})
        log(f"[VOL-LOCAL] {self.in_buf.strip()[:40]} -> {r.get('volume')}")
        self.vol_local_t = time.time()
        if r.get("ok") and self.live is not None:
            try:
                await self.live.send_client_content(
                    turns=types.Content(role="user", parts=[types.Part(
                        text=f"[volume] Volume is now {r.get('volume')}. Say one very short sentence (Vietnamese) then continue.")]),
                    turn_complete=False)
            except Exception as e:
                dbg(f"vol_local loi {type(e).__name__}")

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

    # ---- Phat nhac tu thu muc may chu (play_music): dung lai out_q/pacer nhu tieng co ----
    async def do_play_music(self, query):
        if not music_requested([self.user_txt + " " + self.in_buf, self.prev_user_txt], music.list_tracks()):
            log("[MUSIC] chan: khong ai xin nhac")
            return {"ok": False, "error": "nobody asked for music; if unsure what they said, ask again"}
        path = music.find_track(query)
        if path is None:
            titles = music.list_tracks()
            log(f"[MUSIC] khong thay '{query[:40]}' ({len(titles)} bai)")
            return {"ok": False, "error": "no such song" if titles else "no music files on the server",
                    "available": titles[:30]}
        self.stop_music("bai moi")
        self.music_task = asyncio.create_task(self.music_run(path))
        return {"ok": True, "title": path.stem, "note": "Say at most one very short sentence, then stay silent while it plays. If someone speaks during the song, the music stops; answer them."}

    def stop_music(self, reason):
        """Dung nhac dang phat (neu co). Tra True neu co dang phat."""
        t, self.music_task = self.music_task, None
        if t is None or t.done():
            return False
        t.cancel()
        log(f"[MUSIC] stop {reason}")
        self.clear_out()
        self.fast_stop = True
        self.out_q.put_nowait("STOP")
        return True

    async def music_run(self, path):
        me = asyncio.current_task()
        try:
            # cho Gemini noi xong cau bao ('Dang mo bai ...') roi moi phat
            await asyncio.sleep(1.0)
            for _ in range(80):
                if not (self.gen_open or not self.out_q.empty()):
                    break
                await asyncio.sleep(0.1)
            pcm = await asyncio.to_thread(music.decode_pcm, path, OUT_RATE)
            log(f"[MUSIC] play {path.stem} ({len(pcm) / (OUT_RATE * 2):.0f} s)")
            # 2026-11-12: lan ngat loi truoc do (be noi 'mo nhac') de lai aborted/fast_stop -> nhac + loi co bi bo
            self.aborted = False
            self.fast_stop = False
            self.tts_on = True
            self.out_q.put_nowait("START")
            step = OUT_FRAME * 2
            for i in range(0, len(pcm), step):
                chunk = pcm[i:i + step]
                if len(chunk) < step:
                    chunk += b"\x00" * (step - len(chunk))
                self.out_q.put_nowait(self.enc.encode(chunk, OUT_FRAME))
                while self.out_q.qsize() > 40:
                    await asyncio.sleep(0.1)
            self.out_q.put_nowait("STOP")
            while not self.out_q.empty() or self.dev_on:
                await asyncio.sleep(0.2)
            if self.music_task is not me or self.closed:
                return
            self.music_task = None
            log("[MUSIC] end")
            # tra trang thai ve 'dang nghe' de loi be sau nhac khong bi chan, cau co noi sau nhac khong bi bo
            self.aborted = False
            self.gen_open = False
            self.tts_on = False
            self.last_active = time.time()
            if self.live is not None:
                await self.live.send_client_content(
                    turns=types.Content(role="user", parts=[types.Part(
                        text="[music ended] The song finished. Talk briefly about it, then return to the lesson.")]),
                    turn_complete=True)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log(f"[MUSIC] loi {type(e).__name__}: {str(e)[:120]}")
            if self.music_task is me:
                self.music_task = None

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
                    else:
                        # 2026-11-07: KHONG tu dong khi co noi 'goodbye/bye bye' (bai chao hoi DAY tu goodbye -> phien bi dong som).
                        # Chi dong khi be xin ket thuc ([end]) hoac im qua IDLE_S.
                        if self.nudge_task:
                            self.nudge_task.cancel()
                        self.nudge_task = asyncio.create_task(self.nudge_watch(time.time()))
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
        """Sau luot co, be im -> nhac gian dan (6, 12, 20, 40 s). Lan 4 cho biet co van o day roi IM CHO (khong tam biet);
        chi tam dung khi im qua IDLE_S (idle_watch). Tuan 2026-11-07: chao tam biet som qua."""
        await asyncio.sleep(NUDGE_GAPS[min(self.silent_n, len(NUDGE_GAPS) - 1)])
        if (self.closed or self.ending or self.finishing or self.tts_on or self.gen_open or self.dev_on
                or self.last_speech > stop_t or self.heard_at > stop_t or self.live is None):
            return
        self.silent_n += 1
        n = self.silent_n
        self.m_silence += 1
        log(f"[LIVE-T] nhac be (lan {n})")
        if n <= 2:
            await self.send_lesson("[silence] The child has not answered. Gently encourage in Vietnamese and make it easier: "
                                   "say the current word once more slowly and invite 'Con nói theo cô: <word>!', then wait; "
                                   "do not ask a second question and never ask for an action or gesture. "
                                   "You have no camera: do not say you see the child.")
        elif n == 3:
            await self.send_lesson("[silence] Still no answer. Do NOT ask again. Praise warmly ('Không sao, con giỏi lắm!'), say the word yourself once slowly, and go on to the next word.")
        elif n == 4:
            await self.send_lesson("[silence] The child is quiet. Say ONE short warm sentence in Vietnamese that you are still "
                                   "here and they can talk to you anytime (e.g. 'Cô vẫn ở đây, khi nào con muốn chơi tiếp thì "
                                   "gọi cô nhé!'). Do NOT say goodbye. Then wait quietly.")
            return
        else:
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
        if self.nick or self.dev_mode:
            try:
                res = CUR.finish(self.nick, time.time() - self.t_open, self.child_turns, device=self.device_id or None)
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
        if self.user_txt.strip():
            self.child_turns = getattr(self, "child_turns", 0) + 1   # dem luot be noi (tinh buoi hoc)
        if self.reply_txt.strip():
            self.m_replies.append(self.reply_txt.strip())
        if self.first_ms is not None:
            log(f"[LIVE-T] first_audio={self.first_ms}ms user='{self.user_txt.strip()}' reply='{self.reply_txt.strip()}'")
        if self.user_txt.strip():
            self.prev_user_txt = self.user_txt
        self.vol_local_done = False
        self.first_ms, self.user_txt, self.reply_txt, self.t_user_end = None, "", "", None

    def metric_line(self):
        """Chi so buoi hoc (1 dong, chi la so, khong chu hoi thoai): luot be, luot co, tu TB moi cau co, cau dai nhat, so lan nhac im."""
        if self.reply_txt.strip():
            self.m_replies.append(self.reply_txt.strip())
            self.reply_txt = ""
        lens = [len(s.split()) for r in self.m_replies for ln in r.splitlines()
                for s in re.split(r"[.!?\u2026]+", ln) if s.strip()]
        avg = sum(lens) / len(lens) if lens else 0.0
        return (f"[LIVE-METRIC] luot_be={self.child_turns} luot_co={len(self.m_replies)} tu_tb_cau_co={avg:.1f} "
                f"cau_dai_nhat={max(lens, default=0)} im_lang_nhac={self.m_silence}")

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
                if VOICE_ENROLL and self.enrolled < ENROLL_TURNS and not self.prefilled:
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
        if self.pending_lesson:
            return
        if LOCK_DEVICE_NICK and self.nick and self.device_id and DEVICE_NICK.get(self.device_id):
            return                          # bo da gan biet danh (devices.json): khong doi khi nghe ten con vat khac
        if self.nick:
            if not (self.prefilled and self.child_turns < 3):
                return
            nk = find_nickname(self.in_buf)
            if not nk or nk == self.nick:
                return
            log(f"[LIVE-TOOL] be doi biet danh {self.nick} -> {nk}")
            self.nick, self.prefilled = None, False
        nick = find_nickname(self.in_buf)
        if not nick and self.guess:
            w = set(_fold(self.in_buf).split())
            if w & NO_WORDS:
                log(f"[LIVE-VOICE] be noi khong ({self.guess})")
                self.guess = None
                self.pending_lesson = ("[lesson] The child said no. Say sorry kindly in Vietnamese and ask which animal friend "
                                       f"is learning today ({self.ask_names()}). Do not call tools yet.")
                self.mute_current_turn()
                asyncio.create_task(self.lesson_timeout())
                return
            if w & YES_WORDS:
                nick = self.guess
        if not nick:
            return
        self.guess = None
        self.begin_nick(nick)
        ms = int((time.time() - (self.last_speech or time.time())) * 1000)
        self.nick_log = (nick, ms)
        asyncio.create_task(self.soft_lesson_wait())

    def begin_nick(self, nick):
        """Curriculum.start + chuan bi [lesson] (gui sau cau chao ngan, khong chan cau chao tu nhien)."""
        res = CUR.start(nick)
        if res.get("allowed"):
            self.nick = res["learner"]
            device_nick_save(self.device_id, self.nick)
            log(f"[LIVE-TOOL] nick {nick} -> {res.get('lesson_id')}")
            lw = CUR.last_words(self.nick)
            recall = (f" Last time you learned: {', '.join(lw)}. Start by recalling one of them playfully "
                      "(do not quiz hard), then continue.") if lw else ""
            self.pending_lesson = (f"[lesson] Learner: bạn {nick}. {res['instructions']}{recall} "
                                   "Vary your opening sentence and your first activity every session; never reuse the exact "
                                   "sentences from earlier sessions. "
                                   "Greet the learner by this animal name and start the lesson now.")
        else:
            log(f"[LIVE-TOOL] nick {nick} -> refused")
            self.pending_lesson = (f"[lesson] Learner: bạn {nick}. Not allowed: {res.get('reason', '')} "
                                   "Say this reason kindly in Vietnamese, then say a short goodbye. Do not start a lesson.")

    def ask_names(self, k=3):
        """Chon ngau nhien k biet danh khac bo lan truoc tren thiet bi."""
        last = set(NICK_SET_LAST.get(self.device_id or "-", ()))
        pool = [n for n in ALLOWED_NICKNAMES if n not in last]
        if len(pool) < k:
            pool = list(ALLOWED_NICKNAMES)
        pick = random.sample(pool, k)
        NICK_SET_LAST[self.device_id or "-"] = tuple(pick)
        return ", ".join("bạn " + n for n in pick)

    def ask_text(self):
        a, b, c = self.ask_names().split(", ")
        forms = [f"'Hôm nay con muốn làm bạn nào: {a}, {b} hay {c}?'",
                 f"'Con là bạn gì nè?' and then offer {a}, {b} or {c}",
                 f"'Ai đang học với cô đây nhỉ, {a}, {b} hay {c}?'",
                 f"'Con chọn bạn thú nào hôm nay: {a}, {b} hay {c}?'",
                 f"'Cô đoán xem, con là {a}, {b} hay {c} nhỉ?'"]
        return random.choice(forms) + " (any similar fresh sentence is fine; it must name those 3 animals)."

    # 2026-11-07: KHONG chan cau chao tu nhien cua Gemini; [lesson] gui ngay khi cau chao ngan xong (turn_complete)
    # hoac sau khi be het noi ma Gemini khong sinh loi
    async def soft_lesson_wait(self):
        t0 = time.time()
        while self.pending_lesson and not self.closed and time.time() - t0 < 12:
            await asyncio.sleep(0.1)
            if self.gen_open or self.dev_on:
                continue                          # dang chao: turn_complete se gui [lesson]
            if time.time() - max(self.last_speech, self.heard_at) >= 1.5:
                await self.flush_lesson()
                return

    async def flush_lesson(self):
        if not self.pending_lesson:
            return
        txt, self.pending_lesson = self.pending_lesson, None
        self.aborted = False
        if self.nick_log and txt.startswith("[lesson] Learner"):
            nick, ms = self.nick_log
            self.nick_log = None
            log(f"[LIVE-T] nick {nick} luc +{ms} ms sau het tieng be; lesson gui luc "
                f"+{int((time.time() - (self.last_speech or time.time())) * 1000)} ms")
        await self.send_lesson(txt)

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
                    self.barge_heard(sc.input_transcription.text)
                    if not self.tech_mode and TECH_PHRASE in " ".join(self._norm_txt(self.in_buf)):
                        self.tech_until = time.time() + TECH_MODE_S
                        log("[TUNE] che do ky thuat BAT (10 phut)")
                        msg = ("[tech mode on] An adult opened TECH MODE for 10 minutes. You may call tech_tune / tech_report when they ask "
                               "to change or read mic, barge or gain settings. Answer in one short sentence with the new number, "
                               "then go back to the lesson.")
                        self.pending_lesson = (self.pending_lesson + "\n" + msg) if self.pending_lesson else msg
                    self.check_nick()
                    asyncio.create_task(self.vol_local())   # khong chan vong nhan Gemini khi cho thiet bi tra loi MCP
                if sc.interrupted:
                    self.stop_music("Gemini bao be noi chen")
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
                            if self.user_txt.strip():
                                self.prev_user_txt = self.user_txt
                            self.vol_local_done = False
                            self.user_txt, self.reply_txt, self.t_user_end = "", "", None
                    # DETOUR (2026-11-12): che do lo trinh KHONG con tu CUR.switch khi be xin doi/viec khac -
                    # Gemini lam theo yeu cau theo muc DETOUR cua prompt roi quay lai bai. Chi ep lai khi STLAB_FORCE_SWITCH=1.
                    if (FORCE_SWITCH and self.in_buf.strip() and (self.nick or self.dev_mode) and not self.ending
                            and wants_switch(self.in_buf)):
                        try:
                            sw = CUR.switch(self.nick, device=self.device_id or None)
                            if sw.get("instructions"):
                                self.switches += 1
                                log(f"[LIVE-TOOL] doi bai lan {sw['count']} -> new={sw['new']} review={sw['review']}")
                                self.pending_lesson = "[switch] The child asked to change. " + sw["instructions"]
                        except Exception as e:
                            log(f"switch loi {type(e).__name__}")
                    if self.in_buf.strip() and not (self.nick or self.dev_mode or self.guess or self.pending_lesson or self.ending):
                        self.anon_turns += 1
                        if self.anon_turns >= 2 and not self.anon_sent and ANON_LESSON:
                            self.anon_sent = True
                            res = CUR.start(None, device=self.device_id) if self.device_id else {"allowed": None}
                            if res.get("allowed"):
                                self.dev_mode = True
                                log(f"[LIVE-TOOL] khong co biet danh sau 2 luot -> hoc theo may {self.device_id} {res.get('lesson_id')}")
                                self.pending_lesson = ("[lesson] No nickname was given. Say kindly that today we learn together, "
                                                       f"and start this lesson now. {res['instructions']}")
                            elif res.get("allowed") is False:
                                log("[LIVE-TOOL] hoc theo may -> gioi han ngay")
                                self.pending_lesson = (f"[lesson] No nickname. Not allowed: {res.get('reason', '')} "
                                                       "Say this reason kindly in Vietnamese, then say a short goodbye. Do not start a lesson.")
                            else:
                                lid, instr = CUR.anonymous_lesson()
                                log(f"[LIVE-TOOL] khong co biet danh sau 2 luot -> bai ngau nhien {lid}")
                                self.pending_lesson = ("[lesson] No nickname was given. Say kindly that today we learn together, "
                                                       f"and start this lesson now (do not call mark_word/finish_lesson). {instr}")
                    self.in_buf = ""
                    await self.flush_lesson()

    def interrupt_now(self):
        """Be ngat loi (nut abort hoac giong qua BargeGate): dung phat ngay, bo phan Gemini con sinh, cho be noi tiep."""
        self.stop_music("be cham/noi chen")
        self.clear_out()
        if self.gen_open or self.dev_on or self.tts_on:
            self.fast_stop = True
            self.aborted = True
            self.gen_open = False
            self.out_q.put_nowait("STOP")
            if self.live is not None:
                asyncio.create_task(self.tell_interrupted())

    async def mic_rx(self):
        async for m in self.ws:
            if isinstance(m, bytes):
                if self.tts_on and not self.full_duplex:
                    continue
                try:
                    pcm = self.dec.decode(m, IN_FRAME)
                except Exception:
                    continue
                if DUMP_WAV:
                    self.dump_pcm += pcm
                    if len(self.dump_pcm) > RATE_BYTES * DUMP_MAX_S:
                        del self.dump_pcm[:len(self.dump_pcm) - RATE_BYTES * DUMP_MAX_S]
                barged = False
                self.apply_tuning()
                if self.full_duplex and self.music_task is not None and not self.music_task.done():
                    # Dang phat nhac (S3): giong nguoi >= MUSIC_BARGE_MS lien tuc -> dung nhac, tra khung da giu qua Gemini
                    if self.vad is not None:
                        self.vad.process(pcm)
                        prob = self.vad.max_prob
                    else:
                        prob = 1.0 if audioop.rms(pcm, 2) > 1500 else 0.0
                    if prob >= 0.5:
                        self.voice_seen_t = time.time()
                        self.music_held.append(pcm)
                        self.music_voice_ms += len(pcm) / 2 * 1000.0 / IN_RATE
                    else:
                        self.music_held, self.music_voice_ms = [], 0.0
                    if self.music_voice_ms >= MUSIC_BARGE_MS:
                        log(f"[MUSIC] nguoi noi luc nhac ({self.music_voice_ms:.0f} ms) -> dung nhac")
                        chunks, hot = [b"".join(self.music_held)], True
                        self.music_held, self.music_voice_ms = [], 0.0
                        self.music_pass_until = time.time() + 1.5
                        self.stop_music("nguoi noi luc nhac")
                    else:
                        chunks, hot = [bytes(len(pcm))], False
                elif self.full_duplex and self.tts_on and time.time() < self.music_pass_until:
                    chunks, hot = [pcm], True      # vua dung nhac: cho mic qua, BargeGate khong chan
                elif self.full_duplex and self.tts_on:
                    # Bo S3 (AEC tren bo): luc co noi van giai ma mic, lay xac suat giong nguoi Silero, qua BargeGate:
                    # so 0 cho toi khi giong lien tuc >= STLAB_BARGE_MS; luc do tra cac khung da giu + bao ngat loi
                    if self.vad is not None:
                        self.vad.process(pcm)
                        prob = self.vad.max_prob
                    else:
                        prob = 1.0 if audioop.rms(pcm, 2) > 1500 else 0.0
                    if prob >= 0.5:
                        self.voice_seen_t = time.time()
                    out, barged = self.barge.feed(pcm, prob, True)
                    chunks, hot = [out], barged
                else:
                    if self.full_duplex:
                        self.barge.reset()
                    if self.vad is not None:
                        chunks, hot = self.vad.process(pcm)       # chi giong nguoi qua cong; nhac/nen -> so 0
                    else:
                        chunks, hot = [pcm], audioop.rms(pcm, 2) > 400
                if barged:
                    log(f"[BARGE] be ngat loi bang giong (prob>={self.barge.threshold:g} lien tuc {self.barge.hold_ms:g} ms) -> dung phat")
                    self.barge_started(self.reply_txt)
                    self.interrupt_now()
                if hot:  # tieng noi gan nhat -> moc do do tre
                    self.t_user_end = self.last_speech = time.time()
                    self.silent_n = 0
                for pcm in chunks:
                    if VOICE_ID is not None:
                        self.turn_pcm += pcm
                        if len(self.turn_pcm) > RATE_BYTES * 20:
                            del self.turn_pcm[:-RATE_BYTES * 20]
                    if not (self.full_duplex and S3_SIMPLE):
                        pcm = self.agc.process(pcm)    # AGC mic (A1S); bo S3 've goc' khong AGC
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
                self.full_duplex = j.get("mode") == "realtime"     # S3 realtime; A1S gui "auto" -> giu hanh vi cu
                if self.vad is not None:
                    self.vad.simple = self.full_duplex and S3_SIMPLE
                self.barge.reset()
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
                if (self.full_duplex and self.tts_on and not self.barge.barged
                        and time.time() - self.voice_seen_t <= 2.0):
                    self.tune_outcome_missed()      # be da noi (VadGate thay giong) ma BargeGate chua ngat -> be phai cham nut
                self.interrupt_now()
            # hello trung / mcp / listen stop: bo qua

    async def idle_watch(self):
        while True:
            await asyncio.sleep(2)
            if not self.tts_on and time.time() - self.last_active > IDLE_S:
                log(f"im lang > {int(IDLE_S)} s -> chao ngan roi tam dung")
                await self.end_request()
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
            if DUMP_WAV:
                dp = write_dump(self.dump_pcm, 'full' if self.full_duplex else 'auto')
                if dp:
                    log(f"[DUMP] {dp.name} ({len(self.dump_pcm) / RATE_BYTES:.0f} s am thanh tho tu bo)")
            if self.music_task is not None:
                self.music_task.cancel()
            if self.vad is not None and self.vad.n:
                av, mx, n = self.vad.stats()
                log(f"[LIVE-VAD] {n} khung, TB {av:.2f} ms, max {mx:.2f} ms / khung")
                log(f"[LIVE-LEVEL] het phien: bo_vi_nho={self.vad.skipped} luot, ep_dong={self.vad.forced_n} luot")
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            if self.handle is not None:
                await self.handle.close()

    def session_start_text(self):
        """Mo dau buoi hoc: ngau nhien 1 trong nhieu kieu, khong trung kieu lan truoc cua cung thiet bi."""
        hour = time.localtime().tm_hour
        part = "morning" if hour < 11 else ("noon" if hour < 14 else ("afternoon" if hour < 18 else "evening"))
        styles = [
            "Sing ONE very short made-up greeting song line (cheerful), then greet the child.",
            "Open with a tiny animal-sound riddle: make an animal sound and let the child guess the animal in one short sentence, then greet.",
            "Greet the child and ask in one short sentence if they feel happy or sad today, with a big smile in your voice.",
            f"Greet according to the time of day (it is {part} on the clock) in Vietnamese, with a fresh phrase.",
            "Tell a tiny two-sentence story about a little animal waking up, then greet the child.",
            "Greet in the voice of Lily the owl, with 'hoo hoo' sounds, then greet the child in Vietnamese.",
        ]
        key = self.device_id or "-"
        last = SESSION_START_LAST.get(key, -1)
        i = random.choice([k for k in range(len(styles)) if k != last])
        SESSION_START_LAST[key] = i
        log(f"[LIVE-T] mo dau kieu {i}")
        return ("[session start] " + styles[i] + " Keep the opening to 1-2 short sentences, in Vietnamese. Then ask which "
                "animal friend is learning today, using this fresh wording: " + self.ask_text() + " Vary your wording every session; "
                "never reuse the exact sentences from earlier sessions.")

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
        known = DEVICE_NICK.get(self.device_id) if self.device_id else None
        if known:
            self.prefilled = True
            self.begin_nick(known)
            self.nick_log = None
            log(f"[LIVE-T] thiet bi quen biet danh {known} -> chao thang, khong hoi")
            await self.send_lesson("[session start] This device's child is bạn " + known + ". Greet them directly by that animal "
                                   "name in ONE short fresh sentence in Vietnamese (e.g. 'Chào bạn " + known.capitalize() +
                                   "! Hôm nay mình chơi gì nhỉ?'). Do NOT ask which animal they are. Then wait for the [lesson] message.")
        else:
            await self.send_lesson(self.session_start_text())
        await self.gemini_rx()


def ws_device_id(ws):
    try:
        h = getattr(getattr(ws, "request", None), "headers", None) or getattr(ws, "request_headers", None)
        return (h.get("device-id") or h.get("Device-Id") or "") if h is not None else ""
    except Exception:
        return ""


async def ws_handler(ws, pool):
    log("thiet bi ket noi")
    t_conn, ses = time.time(), None
    h = getattr(getattr(ws, "request", None), "headers", None) or getattr(ws, "request_headers", None) or {}
    if not authorize(h):
        log("tu choi ket noi: sai token hoac thiet bi la")
        await ws.close(code=4401, reason="unauthorized")
        return
    try:
        ses = Session(ws, pool)
        ses.device_id = ws_device_id(ws)
        await ses.run()
    except Exception as e:
        log(f"ket noi dong: {type(e).__name__}: {str(e)[:200]}")
    finally:
        try:
            await ws.close()
        except Exception:
            pass
        log("thiet bi ngat")
        try:
            if ses is not None:
                log(ses.metric_line())
        except Exception as e:
            log(f"metric loi {type(e).__name__}")
        pool.touch()
        # 2026-11-07: chi tinh buoi khi du dai (>= 2 ph) hoac be noi >= 3 luot (curriculum.end_session)
        nick = getattr(ses, "nick", None) if ses is not None else None
        dev_mode = bool(getattr(ses, "dev_mode", False)) if ses is not None else False
        if nick or dev_mode:
            try:
                secs, turns = time.time() - t_conn, getattr(ses, "child_turns", 0)
                r = CUR.end_session(nick, secs, turns, device=getattr(ses, "device_id", "") or None)
                log(f"[LIVE-TOOL] ket thuc buoi {nick or 'may'}: {int(secs)} s, {turns} luot be -> {'tinh' if r.get('counted') else 'khong tinh'}")
            except Exception as e:
                log(f"end_session loi {type(e).__name__}")


async def main():
    print("=" * 78 + "\n" + BANNER + "\n" + "=" * 78, flush=True)
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("Thieu GOOGLE_API_KEY")
    check_public_config()
    if os.environ.get("STLAB_PUBLIC_HOST", "").strip():
        log(f"[PUBLIC] OTA tra {public_ws_url()} ; {len(_allowed_devices())} bo duoc phep, co token")
    if VAD_GATE:
        try:
            from vad_gate import VadGate
            VadGate(SERVER, VAD_THRESHOLD)
            log(f"[LIVE-VAD] bat (nguong {VAD_THRESHOLD:g})")
        except Exception as e:
            log(f"[LIVE-VAD] tat: {type(e).__name__}: {str(e)[:100]}")
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
