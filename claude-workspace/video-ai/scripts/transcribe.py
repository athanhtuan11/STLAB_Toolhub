"""Chep loi tieng Viet theo tung tu bang faster-whisper (chay tren may, khong gui am thanh di dau).

    uv run python scripts/transcribe.py <clip> <out.json> [--device cpu|cuda|auto] [--model large-v3-turbo]

Do tren may STLab (i5-13400F, GTX 1660 SUPER, 2026-10-21): CPU int8 ~0.8x thoi luong clip; GPU cham hon
(int8 2x, float32 15x) -> mac dinh CPU.

FilmCraft ban phat hanh khong co Whisper -> ket qua nay duoc nap vao FilmCraft bang transcript.set (build.py).
Model tai 1 lan vao %LOCALAPPDATA%/stlab-video-ai/models (Hugging Face).
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

MODEL_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "stlab-video-ai" / "models"


def _add_cuda_dlls():
    """Goi pip nvidia-cublas/cudnn dat DLL trong site-packages/nvidia/*/bin: them vao duong tim DLL."""
    import site
    for sp in site.getsitepackages():
        for sub in ("cublas", "cudnn", "cuda_runtime"):
            d = Path(sp) / "nvidia" / sub / "bin"
            if d.is_dir():
                os.add_dll_directory(str(d))
                os.environ["PATH"] = str(d) + os.pathsep + os.environ["PATH"]


def load_model(name, device):
    from faster_whisper import WhisperModel
    if device in ("auto", "cuda"):
        _add_cuda_dlls()
        try:
            return WhisperModel(name, device="cuda", compute_type=os.environ.get("VIDEO_AI_CUDA_COMPUTE", "int8"), download_root=str(MODEL_DIR)), "cuda"
        except Exception as e:  # khong co GPU/thu vien CUDA -> CPU
            if device == "cuda":
                raise
            print(f"[canh bao] GPU khong dung duoc ({str(e)[:120]}), chuyen sang CPU", file=sys.stderr)
    return WhisperModel(name, device="cpu", compute_type="int8", download_root=str(MODEL_DIR)), "cpu"


VOCAB_FILE = Path(__file__).resolve().parent.parent / "vocabulary.txt"


def vocab():
    """Tu vung rieng (ten rieng, thuat ngu) de Whisper uu tien nhan dung, vd. STLab, ESP32, in 3D."""
    if not VOCAB_FILE.exists():
        return None
    words = [ln.strip() for ln in VOCAB_FILE.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.startswith("#")]
    return " ".join(words) or None


def transcribe(media, model_name="large-v3-turbo", device="cpu"):
    model, used = load_model(model_name, device)
    t0 = time.time()
    segments, info = model.transcribe(str(media), language="vi", word_timestamps=True, vad_filter=False,
                                      beam_size=5, condition_on_previous_text=False, hotwords=vocab())
    words, segs = [], []
    for s in segments:
        segs.append({"start": round(s.start, 3), "end": round(s.end, 3), "text": s.text.strip()})
        for w in s.words or []:
            words.append({"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3),
                          "prob": round(w.probability, 3)})
    return {"media": str(Path(media).resolve()), "language": info.language, "duration": round(info.duration, 3),
            "model": model_name, "device": used, "seconds": round(time.time() - t0, 1),
            "segments": segs, "words": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("out")
    ap.add_argument("--model", default="large-v3-turbo")
    ap.add_argument("--device", default="cpu", choices=["auto", "cuda", "cpu"])
    a = ap.parse_args()
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    r = transcribe(a.media, a.model, a.device)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] {Path(a.media).name}: {len(r['words'])} tu, {r['duration']} s audio, "
          f"{r['seconds']} s xu ly ({r['device']}, {r['model']})")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
