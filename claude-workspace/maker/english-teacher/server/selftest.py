"""Tu kiem vong TTS -> ASR -> LLM bang chinh provider cua server. Chay: runtime\.venv\Scripts\python.exe selftest.py"""
import asyncio, os, subprocess, sys, tempfile, time
from pathlib import Path

H = Path(__file__).resolve().parent
RT = H / "runtime"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(RT)
os.environ["PATH"] = str(RT) + os.pathsep + os.environ.get("PATH", "")
sys.path.insert(0, str(RT))
sys.path.append(str(H))

from config.config_loader import read_config, merge_configs  # noqa: E402

from core.utils.modules_initialize import initialize_tts, initialize_asr  # noqa: E402
from core.utils import llm as llm_utils  # noqa: E402


def load_cfg():
    cfg = merge_configs(read_config("config.yaml"), read_config("data/.config.yaml"))
    key = os.environ.get("GOOGLE_API_KEY", "")
    if len(key) < 20:
        sys.exit("LOI: thieu GOOGLE_API_KEY")
    for p in cfg["LLM"].values():
        if isinstance(p, dict) and p.get("type") == "gemini":
            p["api_key"] = key
    return cfg


async def main():
    cfg = load_cfg()
    sel = cfg["selected_module"]

    # TTS
    tts = initialize_tts(cfg)
    t = time.time()
    audio = await tts.text_to_speak("Apple. Red apple.", None)
    print(f"[TTS] ok {len(audio)} bytes"); print(f"[time] TTS {time.time()-t:.2f} s")

    asr = initialize_asr(cfg)
    wav_dir = Path(tempfile.mkdtemp())

    async def recognize(mp3_bytes, tag):
        # mp3 -> wav 16 kHz mono (provider openai doc file_path); xoa ngay sau khi dung
        mp3 = wav_dir / f"{tag}.mp3"
        wav = wav_dir / f"{tag}.wav"
        mp3.write_bytes(mp3_bytes)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "16000", "-ac", "1", str(wav)], check=True)
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "s16le", "-ar", "16000", "-ac", "1", "-"],
                             capture_output=True, check=True).stdout
        art = type(asr).AudioArtifacts(pcm_frames=[pcm], pcm_bytes=pcm, file_path=str(wav), temp_path=None)
        t = time.time()
        res, _ = await asr.speech_to_text([pcm], "selftest", art)
        text = res.get("content", "") if isinstance(res, dict) else str(res)
        dt = time.time() - t
        for f in (mp3, wav):
            f.unlink(missing_ok=True)
        return text, dt

    # ASR tieng Anh
    text, dt = await recognize(audio, "en")
    print(f"[ASR] text={text}"); print(f"[time] ASR {dt:.2f} s")

    # TTS + ASR tieng Viet
    audio_vi = await tts.text_to_speak("Con mèo màu vàng.", None)
    text, dt = await recognize(audio_vi, "vi")
    print(f"[ASR-VI] text={text}"); print(f"[time] ASR-VI {dt:.2f} s")

    # LLM
    lc = cfg["LLM"][sel["LLM"]]
    llm = llm_utils.create_instance(lc.get("type", sel["LLM"]), lc)
    t = time.time()
    out = "".join(llm.response("selftest", [
        {"role": "system", "content": cfg["prompt"]},
        {"role": "user", "content": "What color is an apple?"}]))
    out = " ".join(out.split())
    print(f"[LLM] text={out}"); print(f"[time] LLM {time.time()-t:.2f} s")

    t = time.time()
    out = "".join(llm.response("selftest", [
        {"role": "system", "content": cfg["prompt"]},
        {"role": "user", "content": "Con mèo tiếng Anh là gì?"}]))
    out = " ".join(out.split())
    print(f"[LLM-VI] text={out}"); print(f"[time] LLM-VI {time.time()-t:.2f} s")


import run  # noqa: E402
run.patch_gemini_timeout()
asyncio.run(main())
