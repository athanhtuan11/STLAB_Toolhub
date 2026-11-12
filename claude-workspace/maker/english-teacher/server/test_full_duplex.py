# Gate tro chuyen truc tiep (offline, khong goi Gemini). Claude viet, executor KHONG sua.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_full_duplex.py
# Bo S3 (AEC tren bo) nghe ca luc co noi -> cau noi phai cho mic qua de be ngat loi bang giong,
# nhung tieng vong con sot khong duoc lam co tu ngat: luc co noi chi coi la "ngat loi" khi giong nguoi
# (xac suat Silero >= nguong) keo dai >= hold_ms; truoc do gui so 0 (giu dong thoi gian cho Gemini).
# Bo A1S (auto mode) giu nguyen: luc co noi bo mic.
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "live"))
fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

from duplex import BargeGate   # noqa: E402

FR = 960 * 2                                   # 60 ms PCM 16 kHz s16le
def frame(v):
    return (int(v) & 0xFFFF).to_bytes(2, "little", signed=False) * (FR // 2)
Z = bytes(FR)

g = BargeGate(threshold=0.7, hold_ms=240, frame_ms=60)

# 1) co khong noi -> qua thang
out, barge = g.feed(frame(1000), 0.1, tts_on=False)
ok(out == frame(1000) and barge is False, "tts_on=False: tra nguyen pcm, khong barge")

# 2) co dang noi, vong sot (prob thap) -> so 0, khong barge
g.reset()
res = [g.feed(frame(500), 0.3, tts_on=True) for _ in range(20)]
ok(all(o == Z and b is False for o, b in res), "tts_on, prob thap 1,2 s: toan so 0, khong barge")

# 3) gai ngan < hold roi tat -> khong barge, bo dem reset
g.reset()
r1 = [g.feed(frame(2000), 0.9, tts_on=True) for _ in range(3)]       # 180 ms
r2 = [g.feed(frame(500), 0.2, tts_on=True) for _ in range(2)]
r3 = [g.feed(frame(2000), 0.9, tts_on=True) for _ in range(3)]       # lai 180 ms -> chua du (da reset)
ok(not any(b for _, b in r1 + r2 + r3), "gai 180 ms ngat quang: khong barge (dem reset khi prob tut)")
ok(all(o == Z for o, _ in r1 + r2 + r3), "trong luc cho: gui so 0, khong lot vong")

# 4) giong nguoi lien tuc >= 240 ms -> barge dung 1 lan, tra kem cac khung da giu (Gemini nghe tron dau cau)
g.reset()
outs = []
for i in range(6):
    outs.append(g.feed(frame(3000 + i), 0.85, tts_on=True))
flags = [b for _, b in outs]
ok(flags.count(True) == 1, "barge dung 1 lan")
k = flags.index(True) if True in flags else -1
ok(k == 3, "barge o khung thu 4 (4 x 60 = 240 ms)")
if k >= 0:
    exp = b"".join(frame(3000 + i) for i in range(k + 1))
    ok(outs[k][0] == exp, "khung barge tra ca 4 khung da giu (pcm that, dung thu tu)")
    ok(all(o == frame(3000 + i) for i, (o, _) in enumerate(outs) if i > k), "sau barge: qua thang")

# 5) sau barge, cau noi tat tts -> qua thang; reset() -> lai chan
out, b = g.feed(frame(1234), 0.1, tts_on=False)
ok(out == frame(1234) and b is False, "sau barge + tts tat: qua thang")
g.reset()
out, b = g.feed(frame(1234), 0.2, tts_on=True)
ok(out == Z and b is False, "reset roi tts lai bat: chan lai")

# 6) chuyen tts_on True->False giua chung: khung dang giu khong mat
g.reset()
g.feed(frame(4000), 0.9, tts_on=True); g.feed(frame(4001), 0.9, tts_on=True)
out, b = g.feed(frame(4002), 0.9, tts_on=False)
ok(b is False and out.endswith(frame(4002)), "tts tat giua chung: khung moi qua thang")

# 7) cau noi dung BargeGate cho bo realtime, A1S giu nguyen
br = (HERE / "live" / "bridge.py").read_text(encoding="utf-8")
ok("from duplex import BargeGate" in br or "import duplex" in br, "bridge.py dung BargeGate")
ok(re.search(r"[\"']realtime[\"']", br) is not None, "bridge.py nhan listen mode realtime")
ok(re.search(r"if self\.tts_on[^\n]*:\s*\n\s*continue", br) is None or "full_duplex" in br,
   "bridge.py: luc co noi khong bo mic voi bo full duplex")
ok("full_duplex" in br, "bridge.py co co full_duplex (A1S = False)")
ok("STLAB_BARGE_THRESHOLD" in br and "STLAB_BARGE_MS" in br, "nguong barge chinh qua bien moi truong")
d = (HERE / "live" / "duplex.py").read_text(encoding="utf-8")
ok(re.search(r":\s*\n\s*pass\b", d) is None, "duplex.py khong co khoi pass rong")

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
