# Test tren mach v0.4.0 (ghi clip AVI). python test_v04.py --host stlab-cam.local
# Khong co the TF: clip_rec luon false, khong loi, stream van chay. Phan co the: SKIP + huong dan thu tay.
import argparse, json, socket, sys, time, urllib.request, urllib.error
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
def ctl(v, val):
    return get("/control?var=%s&val=%s" % (v, val))[0]

s0 = st()
ok(s0.get("version") == "0.4.0", "version 0.4.0 (dang %s)" % s0.get("version"))
for k, t in [("clip", int), ("clip_rec", bool), ("clip_count", int), ("clip_drop", int)]:
    ok(k in s0 and isinstance(s0[k], t), "/status co truong %s (=%s)" % (k, s0.get(k)))
orig = {k: s0.get(k) for k in ("clip", "clip_fps", "pre_s", "post_s", "motion")}
count0 = s0.get("clip_count", 0)

# /control hop le
ok(ctl("clip", 1) == 200 and st().get("clip") == 1, "/control?var=clip&val=1 OK, /status clip=1")
ok(ctl("clip_fps", 8) == 200 and st().get("clip_fps") == 8, "clip_fps=8 OK")
ok(ctl("pre_s", 0) == 200 and ctl("pre_s", 5) == 200 and st().get("pre_s") == 5, "pre_s 0 va 5 OK")
ok(ctl("post_s", 2) == 200 and ctl("post_s", 30) == 200 and st().get("post_s") == 30, "post_s 2 va 30 OK")
# ngoai khoang -> 400, gia tri cu giu nguyen
bad = [("clip", 2), ("clip", -1), ("clip_fps", 0), ("clip_fps", 11), ("pre_s", 6), ("pre_s", -1), ("post_s", 1), ("post_s", 31)]
for v, x in bad:
    ok(ctl(v, x) == 400, "/control?var=%s&val=%s -> 400" % (v, x))
s1 = st()
ok((s1["clip_fps"], s1["pre_s"], s1["post_s"], s1["clip"]) == (8, 5, 30, 1), "gia tri sai khong lam doi cau hinh")

# /events: truong clip, /sd?f=...avi
c, b = get("/events")
ok(c == 200 and isinstance(json.loads(b), list), "/events tra danh sach")
for e in json.loads(b):
    ok("clip" in e, "su kien %s co truong clip (=%s)" % (e.get("t"), e.get("clip")))
    if not s1.get("sd_ok"):
        ok(e.get("clip") is None, "khong the TF: su kien khong co clip")
c, _ = get("/sd?f=stlab-cam/20000101/000000.avi")
ok(c in (404, 503), "/sd?f=...avi khong co file -> 404/503 (%d)" % c)
ok(get("/sd?f=../../x.avi")[0] == 400, "/sd chan '..' (.avi)")
ok(get("/sd?f=stlab-cam%5Cx.avi")[0] == 400, "/sd chan '\\'")

# khong the TF: bat motion + clip, clip_rec luon false, stream van chay
if not s1.get("sd_ok"):
    ctl("motion", 1)
    sk = socket.create_connection((a.host, 81), timeout=10)
    sk.sendall(b"GET /stream HTTP/1.1\r\nHost: x\r\n\r\n")
    buf, t0, rec_seen = b"", time.time(), False
    while time.time() - t0 < 15:
        sk.settimeout(2)
        try:
            buf += sk.recv(65536)
        except socket.timeout:
            pass
        if st().get("clip_rec"):
            rec_seen = True
    sk.close()
    ss = st()
    ok(buf.count(b"\xff\xd8") >= 20, "khong the: stream van chay, >= 20 khung / 15 s (%d)" % buf.count(b"\xff\xd8"))
    ok(not rec_seen and ss.get("clip_rec") is False, "khong the TF: clip_rec luon false")
    ok(ss.get("clip_count") == count0 and ss.get("sd_ok") is False, "khong the TF: clip_count khong doi, khong loi (sd_ok=false)")
    ok(get("/capture", timeout=10)[1][:2] == b"\xff\xd8", "/capture van tra JPEG")
    ok(get("/")[0] == 200, "trang / van mo")
else:
    print("SKIP nhanh khong the (mach dang co the TF)")

# khoi phuc cau hinh
for k in ("clip", "clip_fps", "pre_s", "post_s", "motion"):
    if orig.get(k) is not None: ctl(k, orig[k])

print("\nSKIP phan co the TF (Tuan chua co the). Thu tay khi co the FAT32 (the do dung luong <= 32 GB, ghi chu: KHONG format):")
print("  1. Cam the, doi ~30 s: /status sd_ok=true. /control?var=motion&val=1 va /control?var=clip&val=1")
print("  2. Vay tay truoc camera -> /status clip_rec=true; im lang pre_s + post_s giay -> clip_rec=false, clip_count tang 1")
print("  3. /events muc moi co \"clip\":\"stlab-cam/YYYYMMDD/HHMMSS.avi\"; mo link 'xem clip' tren trang, hoac")
print("     curl -o t.avi http://%s/sd?f=<duong dan>  roi  ffprobe t.avi  (ky vong mjpeg, ~clip_fps fps, so khung > 0)" % a.host)
print("  4. Rut the luc dang ghi: khong treo, sd_ok=false, log '[SD] Bo the'; cam lai the -> tu gan lai sau <= 30 s")
print("  5. Xem file tren may tinh: VLC/ffplay/Windows Media Player phai tua duoc (co idx1)")
print("\n%s test_v04 (%d loi)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)
