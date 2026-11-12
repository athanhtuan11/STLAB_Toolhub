"""Cong ngat loi cho che do tro chuyen truc tiep (bo S3, AEC tren bo).
Luc co dang noi (tts_on) mic van duoc nghe, nhung tieng vong con sot sau AEC khong duoc lam co tu ngat.
Quy tac: luc co noi chi coi la be ngat loi khi xac suat giong nguoi (Silero) >= threshold LIEN TUC >= hold_ms.
Trong luc cho, gui so 0 (giu dong thoi gian cho Gemini) va giu lai cac khung that; du hold_ms thi tra ca cac khung da giu
(Gemini nghe tron dau cau) va bao barge dung 1 lan. Co khong noi (tts_on=False) -> qua thang."""


class BargeGate:
    def __init__(self, threshold=0.7, hold_ms=240, frame_ms=60):
        self.threshold = float(threshold)
        self.hold_ms = float(hold_ms)
        self.frame_ms = float(frame_ms)
        self.reset()

    def reset(self):
        self.held = []          # cac khung pcm that dang giu (prob >= nguong lien tuc)
        self.held_ms = 0.0
        self.barged = False     # da ngat trong luot noi nay -> qua thang toi khi co ngung noi

    def _ms(self, pcm):
        # 16 kHz s16le = 32 byte / ms; khung rong thi dung frame_ms
        return len(pcm) / 32.0 if pcm else self.frame_ms

    def feed(self, pcm, prob, tts_on):
        """-> (out_bytes, barge_bool)."""
        if not tts_on:
            # Co ngung noi: khung dang giu (neu co) khong mat, di truoc khung moi
            out = b"".join(self.held) + pcm
            self.held = []
            self.held_ms = 0.0
            self.barged = False
            return out, False
        if self.barged:
            return pcm, False
        if prob >= self.threshold:
            self.held.append(pcm)
            self.held_ms += self._ms(pcm)
            if self.held_ms >= self.hold_ms:
                out = b"".join(self.held)
                self.held = []
                self.held_ms = 0.0
                self.barged = True
                return out, True
        else:
            self.held = []
            self.held_ms = 0.0
        return bytes(len(pcm)), False
