# Test tren mach v0.3.1 (Claude viet, executor KHONG sua). python test_v031.py --host stlab-cam.local
# Yeu cau: khong ai mo trang xem camera trong luc test.
import argparse, json, sys, time, urllib.request, urllib.error, socket
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser(); ap.add_argument("--host", required=True); a = ap.parse_args()
fails = []
def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
def get(path, port=80, timeout=8):
    try:
        with urllib.request.urlopen("http://%s:%d%s" % (a.host, port, path), timeout=timeout) as f:
            return f.status, f.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
def st():
    return json.loads(get("/status")[1])
s = st()
ok(s.get("version") in ("0.3.1",) or str(s.get("version", "")).startswith("0.4."), "version >= 0.3.1 (dang %s)" % s.get("version"))
ok(s.get("so_nguoi_xem", 0) == 0, "khong co nguoi xem luc test (dong tab camera neu FAIL)")
ok(s.get("sta_connected") is True and s.get("ap_on") is False, "da vao Wi-Fi nha -> AP tat (ap_on=%s)" % s.get("ap_on"))
ok(s.get("wifi_ps") not in (None, "none", 0), "khong ai xem -> Wi-Fi tiet kiem dien (wifi_ps=%s)" % s.get("wifi_ps"))
print("  cho camera ngu (toi da 40 s) ...")
slept = False
for _ in range(40):
    if st().get("cam_sleep") is True: slept = True; break
    time.sleep(1)
ok(slept, "khong ai dung -> cam_sleep = true")
t = time.time(); c, b = get("/capture", timeout=10); dt = time.time() - t
ok(c == 200 and b[:2] == b"\xff\xd8", "/capture danh thuc camera tu luc ngu -> JPEG")
ok(dt < 3.0, "danh thuc + chup < 3 s (%.2f s)" % dt)
# stream tu luc ngu
for _ in range(40):
    if st().get("cam_sleep") is True: break
    time.sleep(1)
sk = socket.create_connection((a.host, 81), timeout=10)
sk.sendall(b"GET /stream HTTP/1.1\r\nHost: x\r\n\r\n")
buf, t = b"", time.time()
while time.time() - t < 6 and buf.count(b"\xff\xd8") < 5:
    try:
        buf += sk.recv(65536)
    except socket.timeout:
        break
s2 = st()
ok(buf.count(b"\xff\xd8") >= 5, "stream tu luc ngu ra >= 5 khung trong 6 s (%d)" % buf.count(b"\xff\xd8"))
ok(s2.get("wifi_ps") in ("none", 0), "dang stream -> Wi-Fi khong tiet kiem dien (wifi_ps=%s)" % s2.get("wifi_ps"))
sk.close()
# motion bat -> camera khong ngu
get("/control?var=motion&val=1"); time.sleep(35)
ok(st().get("cam_sleep") is False, "motion bat -> camera khong ngu")
get("/control?var=motion&val=0")
print("\n%s test_v031 (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
