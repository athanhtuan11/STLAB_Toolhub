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
NEAR_MARGIN_DB = float(os.environ.get("STLAB_NEAR_MARGIN_DB", "10"))   # giong be phai to hon nen >= ngan nay
ABS_MIN_DBFS = float(os.environ.get("STLAB_ABS_MIN_DBFS", "-50"))      # va to hon muc tuyet doi nay
MAX_TURN_S = float(os.environ.get("STLAB_VAD_MAX_TURN_S", "8"))        # cong mo lien tuc qua ngan nay -> ep dong
FORCE_CLOSE_S = 0.84                                                    # ep dong >= 800 ms de Gemini chot luot
BASE_WIN_S = 5.0
BASE_PCTL = 20
VOICED_RUN_S = 3.5                                                      # ...va giong da lien tuc >= ngan nay (be noi thuong ngan hon; nhac co loi thi keo dai)
VOICED_FRAC = 0.6                                                       # >60 % cua so 5 s deu la giong -> do la nen (nhac co loi), khong phai be
BASE_WARMUP = 8                                                         # so cua so toi thieu truoc khi tin uoc luong nen


def _find_model(server):
    cands = [Path(server) / "runtime" / "models" / "snakers4_silero-vad" / "src" / "silero_vad" / "data" / "silero_vad.onnx",
             Path(server) / "runtime" / ".venv" / "Lib" / "site-packages" / "silero_vad" / "data" / "silero_vad.onnx"]
    for c in cands:
        if c.is_file():
            return c
    raise FileNotFoundError("khong thay silero_vad.onnx")


class VadGate:
    def __init__(self, server, threshold=0.5, pre_ms=300, hang_ms=600, log=None):
        self.log = log
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
        self.max_prob = 0.0             # xac suat Silero lon nhat trong lan process() gan nhat (cho BargeGate)
        self.n = 0
        self.tot_ms = 0.0
        self.max_ms = 0.0
        self.levels = collections.deque(maxlen=int(BASE_WIN_S * 16000 / WIN))
        self.voiced = collections.deque(maxlen=int(BASE_WIN_S * 16000 / WIN))   # muc cac cua so Silero cho la giong (khong xet am luong)
        self.base_db = -100.0
        self.open_since = None
        self.v_start = -1.0             # bat dau doan giong lien tuc (khe < 0,5 s coi nhu lien tuc)
        self.v_last = -100.0
        self.force_until = -1.0
        self.forced_n = 0
        self.skipped = 0                # so luot giong bi bo vi nho (be hon nen + margin)
        self._skip_flag = False
        self._turn_levels = []
        self._turn_forced = False
        self._turn_base = -100.0
        self._turn_start = 0.0

    @staticmethod
    def _db(x):
        return 20.0 * float(np.log10(float(np.sqrt(np.mean(x * x))) + 1e-9))

    def _end_turn(self):
        if self.log and self._turn_levels:
            v = sum(self._turn_levels) / len(self._turn_levels)
            self.log(f"[LIVE-LEVEL] nen={self._turn_base:.1f}dBFS giong={v:.1f}dBFS dai={self.t - self._turn_start:.1f}s ep_dong={int(self._turn_forced)}")
        self._turn_levels = []
        self._turn_forced = False

    def _prob(self, x):
        inp = np.concatenate([self.ctx, x.reshape(1, WIN)], axis=1)
        out, self.state = self.sess.run(None, {"input": inp, "state": self.state, "sr": np.array(16000, dtype=np.int64)})
        self.ctx = inp[:, -CTX:]
        return float(out[0][0])

    def process(self, pcm):
        t0 = time.perf_counter()
        a = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
        buf = np.concatenate([self.rest, a])
        hot = False
        hot_lv = []
        self.max_prob = 0.0
        tw = self.t
        while len(buf) >= WIN:
            w = buf[:WIN]
            tw += WIN / 16000.0
            p = self._prob(w)
            self.prob = p
            self.max_prob = max(self.max_prob, p)
            lv = self._db(w)
            self.levels.append(lv)
            self.voiced.append(lv if p >= self.thr else None)
            if p >= self.thr:
                if tw - self.v_last > 0.5:
                    self.v_start = tw
                self.v_last = tw
            if len(self.levels) >= BASE_WARMUP:
                self.base_db = float(np.percentile(self.levels, BASE_PCTL))
                # nen la giong lien tuc (loi bai hat): phan vi thap qua thap so voi dinh cua giong -> lay trung vi cua cac cua so giong
                vv = [x for x in self.voiced if x is not None]
                if len(vv) >= VOICED_FRAC * len(self.levels) and tw - self.v_last <= 0.5 and self.v_last - self.v_start >= VOICED_RUN_S:
                    self.base_db = max(self.base_db, float(np.median(vv)))
            gate = max(self.base_db + NEAR_MARGIN_DB, ABS_MIN_DBFS)
            if p >= self.thr:
                if lv >= gate:
                    hot = True
                    hot_lv.append(lv)
                elif not self.open and not self._skip_flag:
                    self.skipped += 1
                    self._skip_flag = True
            buf = buf[WIN:]
        self.rest = buf
        self.t += len(a) / 16000.0
        if self.t < self.force_until:
            hot = False
        if hot:
            if not self.open and not self._turn_levels:
                self._turn_start = self.t
                self._turn_base = self.base_db
            self._skip_flag = False
            self.hot_until = self.t + self.hang_s
            self._turn_levels.extend(hot_lv)
        speaking = self.t <= self.hot_until
        if speaking and self.t < self.force_until:
            speaking = False
        if speaking and self.open_since is not None and self.t - self.open_since > MAX_TURN_S:
            speaking = False                # tran luot: ep dong, tra khung 0 de Gemini chot luot
            self.force_until = self.t + FORCE_CLOSE_S
            self.hot_until = -1.0
            self.forced_n += 1
            self._turn_forced = True
            hot = False
        if speaking:
            chunks = list(self.pre) + [pcm] if not self.open else [pcm]
            self.pre.clear()
            if not self.open:
                self.open_since = self.t - len(a) / 16000.0
            self.open = True
        else:
            if self.open:
                self._end_turn()
            self.open = False
            self.open_since = None
            self.pre.append(pcm)
            chunks = [bytes(len(pcm))]
        ms = (time.perf_counter() - t0) * 1000
        self.n += 1
        self.tot_ms += ms
        self.max_ms = max(self.max_ms, ms)
        return chunks, hot

    def stats(self):
        return (self.tot_ms / self.n if self.n else 0.0, self.max_ms, self.n)
