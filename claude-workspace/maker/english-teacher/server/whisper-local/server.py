"""Whisper tai may (faster-whisper CPU int8), API tuong thich OpenAI: POST /v1/audio/transcriptions.
Chi nghe 127.0.0.1:8010. Khong luu am thanh: file tam bi xoa ngay sau khi nhan dang."""
import os, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import no_ecoqos  # noqa: E402  Windows 11 day tien trinh an sang che do tiet kiem -> Whisper cham 2,5 lan
print('EcoQoS off:', no_ecoqos.disable(), flush=True)
from fastapi import FastAPI, File, Form, UploadFile
from faster_whisper import WhisperModel

MODEL = os.environ.get("STLAB_WHISPER_MODEL", "small")
PROMPT = os.environ.get("STLAB_WHISPER_PROMPT",
    "Màu sắc, con vật: red, blue, yellow, green, apple, cat, dog. Con mèo màu vàng. Con nói: cat!")
LANGS = ("vi", "en")  # chi chon giua tieng Viet va tieng Anh

model = WhisperModel(MODEL, device="cpu", compute_type="int8", cpu_threads=int(os.environ.get('STLAB_WHISPER_THREADS', '8')))
# lam nong: lan nhan dang dau tien sau khi bat khong bi cham
import numpy as np
list(model.transcribe(np.zeros(16000, dtype=np.float32), language="en", beam_size=1)[0])
app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}


@app.post("/v1/audio/transcriptions")
async def transcribe(file: UploadFile = File(...), model_name: str = Form("", alias="model"),
                     language: str = Form("")):
    suffix = os.path.splitext(file.filename or "a.wav")[1] or ".wav"
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(await file.read())
        t = time.time()
        # language=None: Whisper tu do (1 luot ma hoa); neu ra ngon ngu khac vi/en thi lam lai voi "en"
        segs, info = model.transcribe(path, language=language if language in LANGS else None, initial_prompt=PROMPT,
                                      beam_size=1, vad_filter=False, condition_on_previous_text=False)
        lang = info.language
        if lang not in LANGS:
            lang = "en"
            segs, info = model.transcribe(path, language=lang, initial_prompt=PROMPT, beam_size=1,
                                          vad_filter=False, condition_on_previous_text=False)
        text = " ".join(s.text.strip() for s in segs).strip()
        print(f"[whisper] {MODEL} {lang} {time.time()-t:.2f}s", flush=True)  # khong in noi dung
        return {"text": text}
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8010, log_level="warning")
