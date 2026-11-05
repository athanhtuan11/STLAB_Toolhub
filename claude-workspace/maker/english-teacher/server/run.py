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


def patch_gemini_timeout():
    """1) google-generativeai 0.8.6 khong nhan tham so timeout (provider v0.9.8 truyen vao): doi sang request_options.
    2) Gemini mien phi thinh thoang tre 5-30 s o chunk dau: gui them yeu cau song song sau moi HEDGE_S giay chua co chunk
       (toi da 4), lay luong nao ra chunk dau tien (be khong phai cho lau)."""
    import queue
    import threading
    from google.generativeai import GenerativeModel

    orig = GenerativeModel.generate_content
    if getattr(orig, "_stlab", False):
        return
    HEDGE_S, MAX_TRY = 1.2, 4

    def hedged(self, a, k):
        q = queue.Queue()

        def worker(i):
            try:
                first = True
                for chunk in orig(self, *a, **k):
                    q.put((i, "chunk", chunk))
                    first = False
                q.put((i, "end", None))
            except Exception as e:  # noqa: BLE001
                q.put((i, "err", e))

        started, errors, winner = 0, 0, None

        def start():
            nonlocal started
            threading.Thread(target=worker, args=(started,), daemon=True).start()
            started += 1

        start()
        while winner is None:
            try:
                i, kind, val = q.get(timeout=HEDGE_S if started < MAX_TRY else None)
            except queue.Empty:
                start()
                continue
            if kind == "chunk":
                winner = i
                yield val
            elif kind == "err":
                errors += 1
                if errors >= started:
                    if started < MAX_TRY:
                        start()
                    else:
                        raise val
            else:  # end khong co chunk
                return
        while True:
            i, kind, val = q.get()
            if i != winner:
                continue
            if kind == "chunk":
                yield val
            elif kind == "err":
                raise val
            else:
                return

    def generate_content(self, *a, timeout=None, **k):
        if timeout is not None:
            k.setdefault("request_options", {"timeout": timeout})
        if k.get("stream"):
            return hedged(self, a, k)
        return orig(self, *a, **k)

    generate_content._stlab = True
    GenerativeModel.generate_content = generate_content


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
    key = get_key()
    os.chdir(RT)
    os.environ["PATH"] = str(RT) + os.pathsep + os.environ.get("PATH", "")  # opus.dll
    sys.path.insert(0, str(RT))
    patch_loader(key)
    patch_gemini_timeout()
    try:
        runpy.run_path(str(RT / "app.py"), run_name="__main__")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
