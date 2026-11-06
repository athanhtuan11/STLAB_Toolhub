"""Nhan dien giong TAI MAY cho ho so hoc sinh (english-teacher). Tuan (bo cua be) dong y 2026-11-06.
Chi luu DAC TRUNG giong (embedding 192-512 so), KHONG luu am thanh; luu tai may lab; xoa duoc; khong gui di dau.
Thu vien: sherpa-onnx (Apache-2.0). Mo hinh: 3D-Speaker CAM++ zh_en 16k advanced
(3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx, chay CPU, tai bang setup-voiceid.ps1).
License trong so: 3D-Speaker cong bo Apache-2.0; trang release k2-fsa khong ghi rieng -> TODO xac minh tren the mo hinh ModelScope.
Dung: VoiceID(store_dir, threshold=None): enroll(nick, pcm), identify(pcm) -> (nick|None, score), delete(nick), list().
pcm = 16 kHz mono s16le bytes. CLI: python live\voiceid.py --list | --delete <bietdanh> | --delete-all
Nguong cosine mac dinh DEFAULT_THRESHOLD: xem ghi chu ben duoi.
"""
import hashlib, json, os, sys
from pathlib import Path

import numpy as np

SERVER = Path(__file__).resolve().parent.parent
MODEL = SERVER / "models" / "3dspeaker_speech_campplus_sv_zh_en_16k-common_advanced.onnx"
RATE = 16000
FRAME = 320                 # 20 ms
MIN_SPEECH_S = 0.8          # it hon -> (None, 0)
MAX_EMB = 10                # giu toi da 10 embedding gan nhat moi ho so
# Nguong 0.35: do tren giong Edge TTS - cung giong 0.41-0.64, khac giong <=0.27, nguoi la <=0.13. TODO chinh lai khi co giong be that (VOICEID_THRESHOLD).
DEFAULT_THRESHOLD = float(os.environ.get("VOICEID_THRESHOLD", "0.35"))

_extractor = None


def _get_extractor():
    global _extractor
    if _extractor is None:
        import sherpa_onnx
        cfg = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=str(MODEL), num_threads=2, debug=False, provider="cpu")
        _extractor = sherpa_onnx.SpeakerEmbeddingExtractor(cfg)
    return _extractor


def trim_speech(pcm):
    """Cat im lang dau/cuoi. Tra (float32 [-1,1], so giay tieng noi)."""
    a = np.frombuffer(pcm[: len(pcm) // 2 * 2], dtype="<i2").astype(np.float32) / 32768.0
    n = len(a) // FRAME
    if n == 0:
        return a[:0], 0.0
    rms = np.sqrt((a[: n * FRAME].reshape(n, FRAME) ** 2).mean(axis=1))
    thr = max(0.008, float(np.percentile(rms, 95)) * 0.1)
    idx = np.nonzero(rms > thr)[0]
    if len(idx) == 0:
        return a[:0], 0.0
    seg = a[idx[0] * FRAME:(idx[-1] + 1) * FRAME]
    return seg, float((rms > thr).sum() * FRAME / RATE)


def embed(pcm):
    """Embedding chuan hoa (np.float32) hoac None neu < 0,8 s tieng noi."""
    seg, speech_s = trim_speech(pcm)
    if speech_s < MIN_SPEECH_S:
        return None
    ex = _get_extractor()
    st = ex.create_stream()
    st.accept_waveform(sample_rate=RATE, waveform=seg)
    st.input_finished()
    if not ex.is_ready(st):
        return None
    v = np.array(ex.compute(st), dtype=np.float32)
    n = np.linalg.norm(v)
    return v / n if n > 0 else None


class VoiceID:
    def __init__(self, store_dir, threshold=None):
        self.dir = Path(store_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.threshold = DEFAULT_THRESHOLD if threshold is None else float(threshold)

    def _file(self, nick):
        return self.dir / (hashlib.sha256(nick.strip().lower().encode("utf-8")).hexdigest()[:16] + ".json")

    def _load(self, f):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            return d["nick"], np.array(d["embs"], dtype=np.float32)
        except Exception:
            return None, None

    def enroll(self, nick, pcm):
        """Them 1 lan noi vao ho so. True neu trich duoc dac trung."""
        e = embed(pcm)
        if e is None:
            return False
        f = self._file(nick)
        embs = self._load(f)[1] if f.exists() else None
        embs = e[None, :] if embs is None else np.vstack([embs, e])[-MAX_EMB:]
        self.dir.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp")
        tmp.write_text(json.dumps({"nick": nick, "embs": embs.tolist()}), encoding="utf-8")
        tmp.replace(f)
        return True

    def count(self, nick):
        f = self._file(nick)
        return len(self._load(f)[1]) if f.exists() and self._load(f)[1] is not None else 0

    def identify(self, pcm):
        e = embed(pcm)
        if e is None:
            return None, 0.0
        best, score = None, -1.0
        for f in self.dir.glob("*.json"):
            nick, embs = self._load(f)
            if nick is None:
                continue
            m = embs.mean(axis=0)
            m /= np.linalg.norm(m) or 1.0
            s = float(np.dot(m, e))
            if s > score:
                best, score = nick, s
        if best is None:
            return None, 0.0
        return (best if score >= self.threshold else None), score

    def delete(self, nick):
        f = self._file(nick)
        if f.exists():
            f.unlink()
            return True
        return False

    def delete_all(self):
        n = 0
        for f in list(self.dir.glob("*.json")) + list(self.dir.glob("*.tmp")):
            f.unlink()
            n += 1
        return n

    def list(self):
        return sorted(n for n in (self._load(f)[0] for f in self.dir.glob("*.json")) if n)


def default_store():
    return Path(os.environ.get("STLAB_VOICEPRINTS_PATH") or (SERVER / "data" / "voiceprints"))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    v = VoiceID(default_store())
    a = sys.argv[1:]
    if a == ["--list"]:
        print("\n".join(v.list()) or "(trong)")
    elif a == ["--delete-all"]:
        print(f"da xoa {v.delete_all()} ho so giong")
    elif len(a) == 2 and a[0] == "--delete":
        print("da xoa" if v.delete(a[1]) else "khong co ho so")
    else:
        print("dung: python live\voiceid.py --list | --delete <bietdanh> | --delete-all")
        sys.exit(2)
