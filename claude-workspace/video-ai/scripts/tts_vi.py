"""Giong doc AI tieng Viet CHAY TREN MAY (VieNeu-TTS v3 Turbo, ONNX CPU, 48 kHz) - Tuan 2026-10-24: "ma nguon mo tu
them phu de + giong doc AI tieng Viet, khong giong Tuan". Khong gui van ban di dau (khac edge-tts).

Chay bang venv RIENG (vieneu keo gradio/librosa, khong tron vao video-ai/.venv):
    uv venv --python 3.12 %LOCALAPPDATA%/stlab-studio/venvs/vieneu
    uv pip install --python <venv>/Scripts/python.exe vieneu "onnxruntime==1.22.1"
    <venv>/Scripts/python.exe scripts/tts_vi.py <lines.json> <out_dir> [--voice "Mai Anh"]
onnxruntime >= 1.23 tu choi trong so ONNX (cache Hugging Face tren Windows dung symlink -> "External data path escapes
model directory") -> ghim 1.22.1 (da thu 2026-10-25).
lines.json: [{"id": "s01", "text": "..."}, ...] -> <out_dir>/<id>.wav + <out_dir>/durations.json {id: giay}.
Cache: <out_dir>/<id>.wav kem <id>.key (giong + cau) -> chay lai chi tong hop cau doi.
Giong co san (25, Apache-2.0): Vieneu().list_preset_voices(); goi theo MA (vd. "Mai Anh"), khong theo nhan.
KHONG clone giong nguoi that/hoc sinh (quyet dinh Tuan, docs/project-video-marketing-research.md).
"""
import hashlib
import json
import sys
from pathlib import Path

import soundfile as sf

VOICE = "Mai Anh"   # 2026-10-25: Whisper nghe lai dung nhat (cung Ngoc Huyen); Tuan nghe mau roi chot


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    voice = a[a.index("--voice") + 1] if "--voice" in a else VOICE
    lines = json.loads(Path(a[0]).read_text(encoding="utf-8"))
    out = Path(a[1])
    out.mkdir(parents=True, exist_ok=True)
    tts, dur = None, {}
    for ln in lines:
        wav, key = out / f"{ln['id']}.wav", out / f"{ln['id']}.key"
        k = hashlib.sha1(f"{voice}\n{ln['text']}".encode("utf-8")).hexdigest()
        if not (wav.exists() and key.exists() and key.read_text() == k):
            if tts is None:
                from vieneu import Vieneu
                tts = Vieneu()
            tts.save(tts.infer(ln["text"], voice=voice), str(wav))
            key.write_text(k)
        dur[ln["id"]] = sf.info(str(wav)).duration
    (out / "durations.json").write_text(json.dumps(dur, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"voice": voice, "n": len(dur), "seconds": round(sum(dur.values()), 2)}))


if __name__ == "__main__":
    main()
