# Gate tu chinh nguong + AGC + chinh bang giong (offline, khong goi Gemini). Claude viet, executor KHONG sua.
# Chay: runtime\.venv\Scripts\python.exe -X utf8 test_tuning.py
# Tuan 2026-11-12: "nguong testing realtime bang voice duoc khong? khi testing thuc te server tu update nguong?" -> dong y + agent voice-tuner.
import json, math, re, struct, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "live"))
fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

import tuning  # noqa: E402
from tuning import Tuning, Agc, BOUNDS  # noqa: E402

# ---- 1) Tuning: gia tri mac dinh, gioi han, luu file
tmp = Path(tempfile.mkdtemp(prefix="stlab-tune-")) / "tuning.json"
t = Tuning(tmp)
ok(abs(t.get("barge_threshold") - 0.85) < 1e-9 and t.get("barge_ms") == 600, "mac dinh barge 0.85 / 600 ms")
ok(abs(t.get("agc_target_dbfs") + 18) < 1e-9, "mac dinh AGC muc tieu -18 dBFS")
ok(BOUNDS["barge_threshold"] == (0.6, 0.95) and BOUNDS["barge_ms"] == (240, 1200), "gioi han barge 0.6-0.95 / 240-1200 ms")
ok(BOUNDS["agc_target_dbfs"] == (-24, -12) and BOUNDS["agc_max_gain_db"] == (0, 24), "gioi han AGC")
ok(t.set("barge_threshold", 2.0) == 0.95 and t.set("barge_ms", 10) == 240, "set() kep trong gioi han")
t.set("barge_threshold", 0.8); t.set("barge_ms", 500)
t2 = Tuning(tmp)
ok(abs(t2.get("barge_threshold") - 0.8) < 1e-9 and t2.get("barge_ms") == 500, "luu tuning.json, mo lai giu gia tri")
j = json.loads(tmp.read_text(encoding="utf-8"))
ok(isinstance(j.get("history"), list) and len(j["history"]) >= 2 and all("t" in h and "param" in h and "new" in h for h in j["history"]),
   "tuning.json co history (t, param, new) cho moi lan doi")
try:
    t.set("khong_co", 1); ok(False, "set() tham so la phai bao loi")
except (KeyError, ValueError):
    ok(True, "set() tham so la -> KeyError/ValueError")

# ---- 2) Tu hoc nguong ngat loi
t = Tuning(tmp.with_name("t2.json"), now=lambda: T[0])
T = [1000.0]
b0, m0 = t.get("barge_threshold"), t.get("barge_ms")
t.on_barge_outcome("false");
ok(t.get("barge_threshold") > b0 and t.get("barge_ms") > m0, "ngat nham (false) -> nang nguong + keo dai")
b1, m1 = t.get("barge_threshold"), t.get("barge_ms")
T[0] += 5; t.on_barge_outcome("false")
ok(t.get("barge_threshold") == b1 and t.get("barge_ms") == m1, "cooldown: 2 su kien trong < 20 s chi chinh 1 lan")
T[0] += 25; t.on_barge_outcome("missed")
ok(t.get("barge_threshold") < b1 and t.get("barge_ms") < m1, "be phai bam nut moi dung (missed) -> ha nguong + rut ngan")
for _ in range(60):
    T[0] += 30; t.on_barge_outcome("false")
ok(t.get("barge_threshold") <= 0.95 and t.get("barge_ms") <= 1200, "tu hoc khong vuot gioi han tren")
for _ in range(80):
    T[0] += 30; t.on_barge_outcome("missed")
ok(t.get("barge_threshold") >= 0.6 and t.get("barge_ms") >= 240, "tu hoc khong vuot gioi han duoi")
ok(any(h.get("reason") for h in json.loads(tmp.with_name("t2.json").read_text(encoding="utf-8"))["history"]),
   "history ghi ly do (reason) khi tu hoc")

# ---- 3) AGC
SR = 16000
def tone(dbfs, sec=0.06, f=300):
    a = 32767 * 10 ** (dbfs / 20) * math.sqrt(2)
    n = int(SR * sec)
    return struct.pack("<%dh" % n, *[int(max(-32767, min(32767, a * math.sin(2 * math.pi * f * i / SR)))) for i in range(n)])
def rms_db(b):
    n = len(b) // 2
    v = struct.unpack("<%dh" % n, b)
    r = math.sqrt(sum(x * x for x in v) / n) if n else 0
    return 20 * math.log10(r / 32767) if r > 0 else -120
def peak(b):
    n = len(b) // 2
    return max(abs(x) for x in struct.unpack("<%dh" % n, b))

g = Agc(target_dbfs=-18, max_gain_db=18)
out = b""
for _ in range(40):                       # 2,4 s giong nho -36 dBFS
    out = g.process(tone(-36))
ok(abs(rms_db(out) - (-18)) <= 3, f"AGC: giong nho -36 dBFS -> ~-18 sau hoi tu ({rms_db(out):.1f})")
g = Agc(target_dbfs=-18, max_gain_db=18)
for _ in range(40):
    out = g.process(tone(-6))
ok(rms_db(out) <= -5 and peak(out) <= 32767, f"AGC: giong to -6 dBFS khong khuech dai them, khong tran ({rms_db(out):.1f})")
g = Agc(target_dbfs=-18, max_gain_db=18)
for _ in range(40):
    out = g.process(tone(-60))
ok(rms_db(out) < -50, f"AGC: im lang/nen -60 dBFS khong bi keo len thanh on ({rms_db(out):.1f})")
g = Agc(target_dbfs=-18, max_gain_db=6)
for _ in range(40):
    out = g.process(tone(-40))
ok(rms_db(out) <= -40 + 6 + 1, "AGC ton trong max_gain_db")
ok(len(g.process(tone(-30))) == len(tone(-30)), "AGC giu nguyen do dai khung")

# ---- 4) bridge noi day
br = (HERE / "live" / "bridge.py").read_text(encoding="utf-8")
ok("from tuning import" in br or "import tuning" in br, "bridge dung module tuning")
ok(re.search(r"\.on_barge_outcome\(\s*[\"']false[\"']", br) and re.search(r"\.on_barge_outcome\(\s*[\"']missed[\"']", br),
   "bridge bao ca 'false' va 'missed'")
ok("Agc(" in br, "bridge chay AGC tren mic truoc khi gui Gemini")
ok("[TUNE]" in br, "bridge log [TUNE] khi doi nguong")
ok(re.search(r"ch[eế]\s*đ?[oộ]\s*k[yỹ]\s*thu[aậ]t|che do ky thuat", br, re.I) is not None, "bridge nhan cau mo 'che do ky thuat'")
for tname in ("tech_tune", "tech_report"):
    ok(re.search(r'name\s*=\s*["\']%s["\']' % tname, br) is not None, f"khai bao cong cu {tname}")
ok(re.search(r"tech_mode|tech_on", br) is not None, "co co che do ky thuat (tech_mode) chan tech_tune khi chua mo")
ok("STLAB_TUNING_PATH" in br or "STLAB_TUNING_PATH" in (HERE / "live" / "tuning.py").read_text(encoding="utf-8"),
   "duong dan tuning.json qua STLAB_TUNING_PATH (mac dinh server/data/tuning.json)")

# ---- 5) script phan tich cho agent voice-tuner
an = HERE / "tune" / "analyze.py"
ok(an.exists(), "co server/tune/analyze.py")
if an.exists():
    log = Path(tempfile.mkdtemp(prefix="stlab-log-")) / "live.log"
    log.write_text("\n".join([
        "17:41:04 [LIVE-T] thiet bi quen biet danh kay -> chao thang, khong hoi",
        "17:41:11 [LIVE-LEVEL] nen=-29.9dBFS giong=-13.8dBFS dai=0.9s ep_dong=0",
        "17:41:14 [BARGE] be ngat loi bang giong (prob>=0.85 lien tuc 600 ms) -> dung phat",
        "17:41:15 [TUNE] barge false -> barge_threshold 0.88 barge_ms 680",
        "17:41:17 [MUSIC] play Baa Baa Black Sheep (17 s)",
        "17:41:35 [MUSIC] end",
        "17:42:00 [LIVE-METRIC] luot_be=3 luot_co=17 tu_tb_cau_co=6.5 cau_dai_nhat=14 im_lang_nhac=9",
    ]) + "\n", encoding="utf-8")
    import subprocess
    r = subprocess.run([sys.executable, "-X", "utf8", str(an), "--log", str(log), "--json"], capture_output=True, text=True, encoding="utf-8")
    try:
        rep = json.loads(r.stdout)
    except ValueError:
        rep = {}
    ok(r.returncode == 0 and rep.get("barges") == 1 and rep.get("tune_changes") == 1 and rep.get("music_plays") == 1,
       f"analyze.py --json dem barges/tune_changes/music_plays ({r.stdout[:200]} {r.stderr[:200]})")
    ok(isinstance(rep.get("levels"), dict) and "voice_dbfs_median" in rep["levels"], "analyze.py tom tat muc giong (voice_dbfs_median)")
    ok(isinstance(rep.get("suggestions"), list), "analyze.py co danh sach goi y (suggestions)")

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
