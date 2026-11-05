# Gate may chu xiaozhi tu chay (Claude viet, executor KHONG sua). Chay khi server DANG CHAY: python test_server.py
# Kiem: cong 8000/8003, OTA tra websocket LAN, khoa khong nam tren dia, ASR/LLM/TTS chay vong kin bang chinh server.
import json, os, re, socket, subprocess, sys, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
WS = H.parents[2]
SRC = WS / "community" / "xinnan-tech-xiaozhi-esp32-server"
fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

host = os.environ.get("STLAB_XIAOZHI_SERVER", "192.168.1.47")
for port in (8000, 8003):
    s = socket.socket(); s.settimeout(3)
    ok(s.connect_ex((host, port)) == 0, f"cong {port} mo tren {host}"); s.close()
try:
    body = json.dumps({"application": {"version": "2.5.2"}, "board": {"type": "stlab-a1s"}}).encode()
    req = urllib.request.Request(f"http://{host}:8003/xiaozhi/ota/", data=body,
                                 headers={"Content-Type": "application/json", "Device-Id": "e0:8c:fe:64:20:a4",
                                          "Client-Id": "stlab-test"})
    r = json.loads(urllib.request.urlopen(req, timeout=8).read())
    url = (r.get("websocket") or {}).get("url", "")
    ok(url.startswith(f"ws://{host}:8000/xiaozhi/v1"), f"OTA tra websocket LAN ({url})")
except Exception as e:
    ok(False, f"OTA /xiaozhi/ota/ loi: {e}")

# khoa API khong duoc nam tren dia (chi bien moi truong)
key = os.environ.get("GOOGLE_API_KEY", "")
ok(len(key) > 20, "co bien moi truong GOOGLE_API_KEY")
if key:
    hit = []
    for root in (H, ):
        for p in root.rglob("*"):
            if p.is_file() and p.stat().st_size < 5_000_000 and p.suffix in (".yaml", ".yml", ".json", ".py", ".ps1", ".txt", ".log", ".env", ".md"):
                try:
                    if key in p.read_text(encoding="utf-8", errors="ignore"):
                        hit.append(str(p))
                except OSError:
                    pass
    ok(not hit, "khoa khong xuat hien trong file nao duoi server/ " + (str(hit[:3]) if hit else ""))
r = subprocess.run(["git", "-C", str(SRC), "status", "--porcelain"], capture_output=True, text=True)
ok(r.returncode == 0 and r.stdout.strip() == "", "community/xinnan-tech-xiaozhi-esp32-server nguyen ven")

cfg = H / "stlab.config.yaml"
t = cfg.read_text(encoding="utf-8") if cfg.exists() else ""
ok("GeminiLLM" in t and "EdgeTTS" in t, "stlab.config.yaml chon GeminiLLM + EdgeTTS")
ok(re.search(r"delete_audio:\s*true", t) is not None, "delete_audio: true (khong luu giong be)")
ok(re.search(r"base_url:\s*http://127\.0\.0\.1:\d+/v1/audio/transcriptions", t) is not None, "ASR tieng Viet + Anh: Whisper chay tai may (127.0.0.1), khong gui giong ra ngoai")
ok(re.search(r"voice:\s*\S*Multilingual\S*Neural", t) is not None, "giong TTS da ngon ngu (doc ca Viet + Anh)")
ok("2" in t and re.search(r"(2|3|4|5)\s*(-|–|den|to)\s*5|2-5|2–5", t) is not None, "prompt co do tuoi 2-5")

# vong kin: TTS -> wav -> ASR -> LLM (script cua executor, phai in dung cac dong nay)
r = subprocess.run([str(H / "runtime" / ".venv" / "Scripts" / "python.exe"), str(H / "selftest.py")],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
out = r.stdout + r.stderr
print(out[-1500:])
m = re.search(r"\[TTS\] ok (\d+) bytes", out); ok(m is not None and int(m.group(1)) > 5000, "selftest: TTS tao am thanh")
m = re.search(r"\[ASR\] text=(.*)", out); ok(m is not None and re.search(r"apple", m.group(1), re.I), "selftest: ASR nghe ra 'apple'")
m = re.search(r"\[ASR-VI\] text=(.*)", out); ok(m is not None and re.search(r"m[eè]o", m.group(1), re.I), "selftest: ASR nghe tieng Viet 'con meo' ")
m = re.search(r"\[LLM-VI\] text=(.*)", out); ok(m is not None and re.search(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", m.group(1), re.I) is not None, "selftest: be noi tieng Viet -> co giao tra loi co tieng Viet")
m = re.search(r"\[LLM\] text=(.*)", out); ok(m is not None and 0 < len(m.group(1).split()) <= 25, "selftest: LLM tra loi ngan (<= 25 tu)")
ok(key not in out if key else True, "selftest khong in khoa")
print("\n%s test_server (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
