"""Chay xiaozhi-server trong runtime/, dien api_key Gemini tu bien moi truong GOOGLE_API_KEY (chi trong bo nho)."""
import os
import runpy
import sys
from pathlib import Path

RT = Path(__file__).resolve().parent / "runtime"


def get_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if len(key) < 20:
        sys.exit("LOI: thieu bien moi truong GOOGLE_API_KEY (khoa Gemini). Dat bien nguoi dung roi mo lai terminal.")
    return key


def patch_llm(key: str):
    """Thay LLMProvider._generate (khi tools=None) bang goi REST SSE truc tiep + hedge:
    sau HEDGE_S giay chua co chu thi mo them yeu cau moi (toi da MAX_TRY), luong ra chu dau tien thang.
    Loi/het gio -> cau du phong, khong raise. Khoa khong bao gio duoc log."""
    import json
    import queue
    import threading
    import time

    import requests

    os.environ["PATH"] = str(RT) + os.pathsep + os.environ.get("PATH", "")  # opus.dll cho import provider
    from config.logger import setup_logging
    from core.providers.llm.gemini.gemini import LLMProvider

    orig = LLMProvider._generate
    if getattr(orig, "_stlab", False):
        return
    logger = setup_logging()
    # Gemini free gioi han so yeu cau/phut (429): hedge 1,5 s (TTFT thuong 0,6-1 s nen it khi phai gui them), toi da 2;
    # gap 429 thi KHONG gui them (chi lam can quota nhanh hon), tra cau du phong ngay.
    HEDGE_S, MAX_TRY, FIRST_DEADLINE_S = 1.5, 2, 12.0
    FALLBACK = "Cô chưa nghe rõ, con nói lại nhé!"

    def build_body(dialogue):
        sys_parts, contents = [], []
        for m in dialogue:
            text = str(m.get("content", "") or "").strip()
            if not text:
                continue
            r = m.get("role")
            if r == "system":
                sys_parts.append({"text": text})
            else:
                contents.append({"role": "model" if r == "assistant" else "user", "parts": [{"text": text}]})
        body = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
                "maxOutputTokens": 512,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        if sys_parts:
            body["systemInstruction"] = {"parts": sys_parts}
        return body

    def _generate(self, dialogue, tools):
        if tools is not None:
            yield from orig(self, dialogue, tools)
            return
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model_name}:streamGenerateContent?alt=sse"
        )
        headers = {"x-goog-api-key": key or self.api_key, "Content-Type": "application/json"}
        body = build_body(dialogue)
        q = queue.Queue()
        resps = {}
        stop = threading.Event()

        def worker(i):
            r = None
            try:
                r = requests.post(url, headers=headers, json=body, stream=True, timeout=(3, 10))
                resps[i] = r
                if r.status_code != 200:
                    q.put((i, "err", r.status_code))
                    return
                for line in r.iter_lines(decode_unicode=False):
                    if not line or not line.startswith(b"data:"):
                        continue
                    try:
                        obj = json.loads(line[5:].decode("utf-8").strip())
                        parts = obj["candidates"][0]["content"]["parts"]
                    except (ValueError, KeyError, IndexError, TypeError):
                        continue
                    for p in parts:
                        t = p.get("text")
                        if t and not p.get("thought"):
                            q.put((i, "text", t))
                q.put((i, "end", None))
            except Exception as e:  # noqa: BLE001
                q.put((i, "err", type(e).__name__))
            finally:
                if r is not None and (stop.is_set() or r.status_code != 200):
                    try:
                        r.close()
                    except Exception:  # noqa: BLE001
                        pass

        t0 = time.monotonic()
        started, errors, winner = 0, 0, None
        ttft_ms = None

        def start():
            nonlocal started
            threading.Thread(target=worker, args=(started,), daemon=True).start()
            started += 1

        def log_line():
            total = int((time.monotonic() - t0) * 1000)
            tt = "none" if ttft_ms is None else f"{ttft_ms}ms"
            logger.bind(tag="stlab").info(f"[STLAB-T] llm_ttft={tt} tries={started} total={total}ms")

        def close_others():
            for j, rr in list(resps.items()):
                if j != winner:
                    try:
                        rr.close()
                    except Exception:  # noqa: BLE001
                        pass

        quota_hit = False
        start()
        pending = []  # (kind, val) tu luong thang
        try:
            while winner is None:
                left = FIRST_DEADLINE_S - (time.monotonic() - t0)
                if left <= 0:
                    break
                wait = min(HEDGE_S, left) if started < MAX_TRY else left
                try:
                    i, kind, val = q.get(timeout=wait)
                except queue.Empty:
                    if started < MAX_TRY and not quota_hit and (time.monotonic() - t0) < FIRST_DEADLINE_S:
                        start()
                    continue
                if kind == "text":
                    winner = i
                    ttft_ms = int((time.monotonic() - t0) * 1000)
                    yield val
                elif kind == "err":
                    errors += 1
                    if val == 429:
                        quota_hit = True
                    if started < MAX_TRY and not quota_hit:
                        start()
                    elif errors >= started:
                        break
                else:  # end khong chu
                    errors += 1
                    if errors >= started and started >= MAX_TRY:
                        break
                    if started < MAX_TRY:
                        start()
            if winner is None:
                stop.set()
                for rr in list(resps.values()):
                    try:
                        rr.close()
                    except Exception:  # noqa: BLE001
                        pass
                yield FALLBACK
                return
            stop.set()
            close_others()
            while True:
                try:
                    i, kind, val = q.get(timeout=15)
                except queue.Empty:
                    return
                if i != winner:
                    continue
                if kind == "text":
                    yield val
                else:
                    return
        finally:
            stop.set()
            close_others()
            log_line()

    _generate._stlab = True
    LLMProvider._generate = _generate


def patch_tts_split():
    """xinnan chi cat cau TTS theo dau Trung (。：) va ? ! ; -> cau Viet/Anh dung "." khong duoc cat, ca cau tra loi
    thanh 1 doan, phai cho tao giong ca doan (do 2026-11-06: 6 s). Them "." va ":" ASCII de doc cau dau som."""
    from core.providers.tts.base import TTSProviderBase

    orig = TTSProviderBase.__init__
    if getattr(orig, "_stlab", False):
        return

    def __init__(self, *a, **k):
        orig(self, *a, **k)
        self.punctuations = tuple(self.punctuations) + (".", ":")
        self.first_sentence_punctuations = tuple(self.first_sentence_punctuations) + (".", ":")

    __init__._stlab = True
    TTSProviderBase.__init__ = __init__


def patch_loader(key: str):
    import config.config_loader as cl

    orig = cl.load_config

    async def load_config():
        cfg = await orig()
        for prov in (cfg.get("LLM") or {}).values():
            if isinstance(prov, dict) and prov.get("type") == "gemini":
                prov["api_key"] = key
        return cfg

    cl.load_config = load_config  # phai va truoc khi config.settings / app duoc nap


def main():
    import no_ecoqos  # tien trinh an bi Windows 11 ha toc (EcoQoS) -> tat cho chinh minh
    no_ecoqos.disable()
    key = get_key()
    os.chdir(RT)
    os.environ["PATH"] = str(RT) + os.pathsep + os.environ.get("PATH", "")  # opus.dll
    sys.path.insert(0, str(RT))
    patch_loader(key)
    patch_llm(key)
    patch_tts_split()
    try:
        runpy.run_path(str(RT / "app.py"), run_name="__main__")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
