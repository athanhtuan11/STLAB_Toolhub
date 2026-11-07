"""Cong loc giong nguoi cho duong micro (Silero VAD ONNX, 16 kHz, cua so 512 mau).
Silero VAD: MIT License (github.com/snakers4/silero-vad). Chay bang onnxruntime (CPU, 1 luong).
Dung: g = VadGate(); chunks, speaking = g.process(pcm_s16le) -> chunks: list PCM gui cho Gemini (luon >= 1 khung:
khung im lang = so 0 khi khong co giong; khi bat dau co giong, tra kem dem truoc 300 ms)."""
import collections, os, time
from pathlib import Path
import numpy as np

WIN = 512
CTX = 64
FRAME_MS = 60


def _find_model(server):
    cands = [Path(server) / "runtime" / "models" / "snakers4_silero-vad" / "src" / "silero_vad" / "data" / "silero_vad.onnx",
             Path(server) / "runtime" / ".venv" / "Lib" / "site-packages" / "silero_vad" / "data" / "silero_vad.onnx"]
    for c in cands:
        if c.is_file():
            return c
    raise FileNotFoundError("khong thay silero_vad.onnx")


class VadGate:
    def __init__(self, server, threshold=0.5, pre_ms=300, hang_ms=600):
        import onnxruntime as ort
        o = ort.SessionOptions()
        o.inter_op_num_threads = 1
        o.intra_op_num_threads = 1
        self.sess = ort.InferenceSession(str(_find_model(server)), providers=["CPUExecutionProvider"], sess_options=o)
        self.thr = threshold
        self.pre_frames = max(1, pre_ms // FRAME_MS)
        self.hang_s = hang_ms / 1000.0
        self.reset()

    def reset(self):
        self.state = np.zeros((2, 1, 128), dtype=np.float32)
        self.ctx = np.zeros((1, CTX), dtype=np.float32)
        self.rest = np.zeros(0, dtype=np.float32)
        self.pre = collections.deque(maxlen=self.pre_frames)
        self.t = 0.0                    # dong ho theo mau (s), khong theo thoi gian that -> kiem thu duoc
        self.hot_until = -1.0
        self.open = False
        self.prob = 0.0
        self.n = 0
        self.tot_ms = 0.0
        self.max_ms = 0.0

    def _prob(self, x):
        inp = np.concatenate([self.ctx, x.reshape(1, WIN)], axis=1)
        out, self.state = self.sess.run(None, {"input": inp, "state": self.state, "sr": np.array(16000, dtype=np.int64)})
        self.ctx = inp[:, -CTX:]
        return float(out[0][0])

    def process(self, pcm):
        t0 = time.perf_counter()
        a = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        buf = np.concatenate([self.rest, a])
        pmax = None
        while len(buf) >= WIN:
            p = self._prob(buf[:WIN])
            pmax = p if pmax is None else max(pmax, p)
            buf = buf[WIN:]
        self.rest = buf
        if pmax is not None:
            self.prob = pmax
        self.t += len(a) / 16000.0
        hot = self.prob >= self.thr
        if hot:
            self.hot_until = self.t + self.hang_s
        speaking = self.t <= self.hot_until
        if speaking:
            chunks = list(self.pre) + [pcm] if not self.open else [pcm]
            self.pre.clear()
            self.open = True
        else:
            self.open = False
            self.pre.append(pcm)
            chunks = [bytes(len(pcm))]
        ms = (time.perf_counter() - t0) * 1000
        self.n += 1
        self.tot_ms += ms
        self.max_ms = max(self.max_ms, ms)
        return chunks, hot

    def stats(self):
        return (self.tot_ms / self.n if self.n else 0.0, self.max_ms, self.n)
