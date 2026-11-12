"""Tu chinh nguong ngat loi (barge) + AGC mic. Luu server/data/tuning.json (STLAB_TUNING_PATH), co history.
Khong phu thuoc gi ngoai thu vien chuan (audioop)."""
import audioop
import json
import math
import os
import time
from pathlib import Path

BOUNDS = {
    "barge_threshold": (0.6, 0.95),
    "barge_ms": (240, 1200),
    "agc_target_dbfs": (-24, -12),
    "agc_max_gain_db": (0, 24),
}
INT_PARAMS = {"barge_ms"}
AUTO_COOLDOWN_S = 20.0
HISTORY_MAX = 200


def _defaults():
    d = {"barge_threshold": 0.85, "barge_ms": 600, "agc_target_dbfs": -18, "agc_max_gain_db": 18}
    try:
        if os.environ.get("STLAB_BARGE_THRESHOLD"):
            d["barge_threshold"] = float(os.environ["STLAB_BARGE_THRESHOLD"])
        if os.environ.get("STLAB_BARGE_MS"):
            d["barge_ms"] = int(float(os.environ["STLAB_BARGE_MS"]))
    except ValueError:
        pass
    return d


def default_path():
    p = os.environ.get("STLAB_TUNING_PATH", "").strip()
    return Path(p) if p else Path(__file__).resolve().parent.parent / "data" / "tuning.json"


def _clamp(name, v):
    lo, hi = BOUNDS[name]
    v = max(lo, min(hi, float(v)))
    return int(round(v)) if name in INT_PARAMS else round(v, 4)


class Tuning:
    def __init__(self, path=None, now=time.time):
        self.path = Path(path) if path else default_path()
        self.now = now
        self.values = {k: _clamp(k, v) for k, v in _defaults().items()}
        self.history = []
        self._last_auto = -1e18
        self._load()

    def _load(self):
        try:
            j = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(j, dict):
            return
        for k, v in (j.get("values") or {}).items():
            if k in BOUNDS:
                try:
                    self.values[k] = _clamp(k, v)
                except (TypeError, ValueError):
                    pass
        h = j.get("history")
        if isinstance(h, list):
            self.history = [x for x in h if isinstance(x, dict)][-HISTORY_MAX:]

    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_name(self.path.name + ".tmp")
            tmp.write_text(json.dumps({"values": self.values, "history": self.history[-HISTORY_MAX:]},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, self.path)
        except OSError:
            pass

    def get(self, name):
        return self.values[name]

    def set(self, name, v, reason="manual"):
        if name not in BOUNDS:
            raise KeyError(name)
        new = _clamp(name, v)
        old = self.values[name]
        if new != old:
            self.values[name] = new
            self.history.append({"t": self.now(), "param": name, "old": old, "new": new, "reason": reason})
            self._save()
        return new

    def recent(self, n=3):
        return self.history[-n:]

    def on_barge_outcome(self, kind):
        """kind 'false' (ngat nham) / 'missed' (be phai cham nut). Tra True neu da chinh."""
        if kind not in ("false", "missed"):
            return False
        t = self.now()
        if t - self._last_auto < AUTO_COOLDOWN_S:
            return False
        self._last_auto = t
        sign = 1 if kind == "false" else -1
        th, ms = self.get("barge_threshold"), self.get("barge_ms")
        reason = "auto:" + kind
        self.set("barge_threshold", th + sign * (0.03 if kind == "false" else 0.02), reason)
        self.set("barge_ms", ms + sign * (80 if kind == "false" else 40), reason)
        return (self.get("barge_threshold"), self.get("barge_ms")) != (th, ms)


class Agc:
    """AGC theo khung PCM16 mono: gain mem (attack nhanh, release cham), co gioi han dinh, khong keo nen/im lang."""
    GATE_DBFS = -50.0
    RELEASE_DB_PER_60MS = 1.0

    def __init__(self, target_dbfs=-18, max_gain_db=18):
        self.target = float(target_dbfs)
        self.max_gain = float(max_gain_db)
        self.gain_db = 0.0

    def configure(self, target_dbfs, max_gain_db):
        self.target = float(target_dbfs)
        self.max_gain = float(max_gain_db)
        self.gain_db = min(self.gain_db, self.max_gain)

    def process(self, pcm):
        n = len(pcm) // 2
        if n == 0:
            return pcm
        body = pcm[: n * 2]
        rms = audioop.rms(body, 2)
        level = 20 * math.log10(rms / 32768.0) if rms > 0 else -120.0
        if level > self.GATE_DBFS:
            desired = max(0.0, min(self.max_gain, self.target - level))
            if desired < self.gain_db:
                self.gain_db = desired                        # attack: ha ngay khi qua to
            else:
                step = self.RELEASE_DB_PER_60MS * (n / 16000.0) / 0.06
                self.gain_db = min(desired, self.gain_db + step)   # release cham
        self.gain_db = min(self.gain_db, self.max_gain)
        g = 10 ** (self.gain_db / 20.0)
        peak = audioop.max(body, 2)
        if peak * g > 32000:                                   # gioi han dinh, khong bao gio tran
            g = 32000.0 / peak
            self.gain_db = 20 * math.log10(g) if g > 0 else 0.0
        if abs(g - 1.0) < 1e-6:
            return pcm
        out = audioop.mul(body, 2, g)
        return out + pcm[n * 2:]
