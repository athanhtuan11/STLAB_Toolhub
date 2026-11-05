# Test tren mach that v0.3.0 (Claude viet, executor KHONG sua).
# Chay: python test_v03.py --host stlab-cam.local [--ota]   (--ota can bien moi truong STLAB_CAM_OTA_KEY)
# Khong co the TF van phai PASS (sd_ok=false, su kien van ghi vao RAM + /event.jpg).
import argparse, json, os, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--host", required=True)
ap.add_argument("--ota", action="store_true", help="nap lai chinh build/stlab_cam.bin qua OTA")
a = ap.parse_args()
fails = []


def ok(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


def req(path, port=80, data=None, headers=None, timeout=8):
    r = urllib.request.Request("http://%s:%d%s" % (a.host, port, path), data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as f:
            return f.status, f.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def status():
    c, b = req("/status")
    return json.loads(b) if c == 200 else {}


s = status()
ok(str(s.get("version","")).startswith("0.3."), "version 0.3.x (dang %s)" % s.get("version"))
for k in ["motion", "motion_count", "motion_last_s", "sd_ok", "sd_free_mb", "ota_partition", "time_ok"]:
    ok(k in s, "/status co " + k)
ok(s.get("time_ok") is True, "da dong bo gio SNTP")
print("  sd_ok=%s sd_free_mb=%s ota_partition=%s" % (s.get("sd_ok"), s.get("sd_free_mb"), s.get("ota_partition")))

# /control chuyen dong
ok(req("/control?var=motion_thr&val=500")[0] == 400, "motion_thr ngoai khoang -> 400")
ok(req("/control?var=motion_pct&val=0")[0] == 400, "motion_pct ngoai khoang -> 400")
ok(req("/control?var=motion_thr&val=5")[0] == 200, "motion_thr=5 (rat nhay, de test)")
ok(req("/control?var=motion_pct&val=1")[0] == 200, "motion_pct=1")
ok(req("/control?var=motion&val=1")[0] == 200, "bat motion")
c, b = req("/events")
ok(c == 200 and isinstance(json.loads(b), list), "/events tra JSON list")

print("  >> Vay tay truoc camera trong 20 s ...")
n0 = status().get("motion_count", 0)
t_end = time.time() + 20
got = False
while time.time() < t_end:
    if status().get("motion_count", 0) > n0:
        got = True
        break
    time.sleep(1)
ok(got, "phat hien chuyen dong (motion_count tang)")
if got:
    c, b = req("/event.jpg")
    ok(c == 200 and b[:2] == b"\xff\xd8", "/event.jpg la JPEG (%d byte)" % len(b))
    ev = json.loads(req("/events")[1])
    ok(len(ev) >= 1, "/events co su kien")
    print("  su kien moi nhat:", ev[-1] if ev else None)
# stream + capture van chay khi motion bat
c, b = req("/capture")
ok(c == 200 and b[:2] == b"\xff\xd8", "/capture van chay khi motion bat")
ok(req("/sd?f=../../etc")[0] in (400, 403, 404), "/sd chan duong dan ..")
if not s.get("sd_ok"):
    ok(req("/sd?f=stlab-cam/x.jpg")[0] in (404, 503), "khong co the: /sd tra 404/503, khong treo")
req("/control?var=motion_thr&val=25")
req("/control?var=motion_pct&val=3")
req("/control?var=motion&val=0")

# OTA
ok(req("/ota", data=b"x" * 64, headers={"X-OTA-Key": "sai-khoa"})[0] == 403, "OTA sai khoa -> 403")
ok(req("/ota", data=b"x" * 64)[0] == 403, "OTA thieu khoa -> 403")
if a.ota:
    key = os.environ.get("STLAB_CAM_OTA_KEY", "")
    ok(bool(key), "co bien moi truong STLAB_CAM_OTA_KEY")
    binf = Path(__file__).resolve().parent / "build" / "stlab_cam.bin"
    part0 = s.get("ota_partition")
    ok(req("/ota", data=b"\x00" * 4096, headers={"X-OTA-Key": key}, timeout=30)[0] in (400, 500),
       "OTA anh rac -> loi, khong doi ban")
    time.sleep(2)
    ok(status().get("ota_partition") == part0, "anh rac khong lam doi phan vung")
    c, b = req("/ota", data=binf.read_bytes(), headers={"X-OTA-Key": key,
               "Content-Type": "application/octet-stream"}, timeout=120)
    ok(c == 200, "OTA that tra 200 (%s)" % b[:80])
    s2 = {}
    for _ in range(40):
        time.sleep(2)
        try:
            s2 = status()
            if s2:
                break
        except Exception:
            pass
    ok(s2.get("version") == s.get("version"), "mach len lai sau OTA")
    ok(s2.get("ota_partition") not in (None, part0), "doi phan vung %s -> %s" % (part0, s2.get("ota_partition")))
    c, b = req("/capture")
    ok(c == 200 and b[:2] == b"\xff\xd8", "camera chay sau OTA")

print("\n%s test_v03 (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
