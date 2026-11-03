# Test phan cung firmware cam tren mach that (Claude viet + chay, executor KHONG sua).
# python test_cam.py --host 192.168.1.127 [--soak-min 20]
import argparse, json, socket, struct, sys, threading, time, urllib.request, urllib.error

ap = argparse.ArgumentParser()
ap.add_argument("--host", required=True)
ap.add_argument("--soak-min", type=float, default=0)
a = ap.parse_args()
H = a.host
fails = []


def ok(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def get(path, port=80, timeout=5):
    t0 = time.time()
    try:
        r = urllib.request.urlopen("http://%s:%d%s" % (H, port, path), timeout=timeout)
        return r.status, r.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read(), time.time() - t0
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0


def status():
    c, b, _ = get("/status")
    try:
        return json.loads(b) if c == 200 else None
    except ValueError:
        return None


def jpeg_size(b):
    if not b or b[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(b) - 9:
        if b[i] != 0xFF:
            i += 1
            continue
        mk = b[i + 1]
        if mk in (0xC0, 0xC1, 0xC2):
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return w, h
        ln = struct.unpack(">H", b[i + 2:i + 4])[0]
        i += 2 + ln
    return None


def capture_ok(tag, maxt=3.0):
    c, b, t = get("/capture", timeout=maxt + 2)
    good = c == 200 and b[:2] == b"\xff\xd8" and len(b) > 3000 and t <= maxt
    ok(good, "%s: /capture %s %d B %.2f s" % (tag, c, len(b), t))
    return b if good else None


class Viewer(threading.Thread):
    """Mo /stream cong 81, dem khung JPEG, roi dong socket dot ngot (nhu tat tab)."""

    def __init__(self, secs):
        super().__init__(daemon=True)
        self.secs, self.frames, self.code = secs, 0, None

    def run(self):
        try:
            s = socket.create_connection((H, 81), timeout=5)
            s.sendall(("GET /stream HTTP/1.1\r\nHost: %s\r\n\r\n" % H).encode())
            buf, t0 = b"", time.time()
            while time.time() - t0 < self.secs:
                d = s.recv(65536)
                if not d:
                    break
                buf += d
                if self.code is None and b"\r\n" in buf:
                    try:
                        self.code = int(buf.split(b" ")[1])
                    except (IndexError, ValueError):
                        self.code = -1
                n = buf.count(b"\xff\xd8\xff")
                if n:
                    self.frames += n
                    buf = buf[buf.rfind(b"\xff\xd8\xff") + 3:]
            s.close()
        except OSError:
            if self.code is None:
                self.code = 0


print("1. Trang thai + chup")
st = status()
ok(st is not None, "/status JSON")
if not st:
    sys.exit(1)
ok(st.get("version") == "0.1.0", "version %s" % st.get("version"))
ok(st.get("vflip") == 1 and st.get("hmirror") == 1, "mac dinh vflip=1 hmirror=1")
c, b, t = get("/")
ok(c == 200 and b"81" in b, "trang / %s" % c)
capture_ok("chup khi khong ai xem")

print("2. Xem video + chup cung luc")
v = Viewer(12)
v.start()
time.sleep(1.5)
for i in range(3):
    capture_ok("chup khi dang xem #%d" % (i + 1))
    c, _, t = get("/status")
    ok(c == 200 and t < 2, "/status khi dang xem %.2f s" % t)
    time.sleep(1)
v.join()
fps = v.frames / 12.0
st = status() or {}
ok(v.code == 200 and 4 <= fps <= st.get("fps_cai", 10) + 2,
   "stream %d khung/12 s = %.1f fps (cai %s)" % (v.frames, fps, st.get("fps_cai")))

print("3. Dong tab dot ngot x5 roi chup lai")
for i in range(5):
    v = Viewer(2)
    v.start()
    v.join()
    time.sleep(1)
    capture_ok("sau dong stream lan %d" % (i + 1))
time.sleep(2)
st = status() or {}
ok(st.get("so_nguoi_xem") == 0, "so_nguoi_xem ve 0 (%s)" % st.get("so_nguoi_xem"))

print("4. Toi da 2 nguoi xem")
v1, v2 = Viewer(6), Viewer(6)
v1.start()
v2.start()
time.sleep(1.5)
v3 = Viewer(2)
v3.start()
v3.join()
ok(v3.code == 503, "nguoi thu 3 nhan %s" % v3.code)
v1.join()
v2.join()
ok(v1.code == 200 and v2.code == 200 and v1.frames > 5 and v2.frames > 5,
   "2 nguoi xem: %d, %d khung" % (v1.frames, v2.frames))
time.sleep(2)

print("5. /control")
get("/control?var=framesize&val=10")  # FRAMESIZE_VGA = 10 (esp32-camera 2.1 sensor.h)
time.sleep(1)
b = capture_ok("chup sau doi VGA")
ok(jpeg_size(b) == (640, 480), "kich thuoc VGA %s" % (jpeg_size(b),))
get("/control?var=framesize&val=11")  # FRAMESIZE_SVGA = 11
time.sleep(1)
b = capture_ok("chup sau tra SVGA")
ok(jpeg_size(b) == (800, 600), "kich thuoc SVGA %s" % (jpeg_size(b),))
c, _, _ = get("/control?var=khongco&val=1")
ok(c == 400, "var sai -> %s" % c)
c, _, _ = get("/control?var=quality&val=99")
ok(c == 400, "quality 99 -> %s" % c)
st = status() or {}
ok(st.get("cam_reinit") == 0, "cam_reinit %s (frame_loi %s)" % (st.get("cam_reinit"), st.get("frame_loi")))
print("   nhiet %s C, nong %s, heap %s, psram %s" % (st.get("nhiet_do_chip"), st.get("nong"),
                                                  st.get("heap_free"), st.get("psram_free")))

if a.soak_min > 0:
    print("6. Chay video lien tuc %.0f phut" % a.soak_min)
    end = time.time() + a.soak_min * 60
    tmax, nloi = 0.0, 0
    while time.time() < end:
        v = Viewer(30)
        v.start()
        v.join()
        st = status() or {}
        tmax = max(tmax, st.get("nhiet_do_chip") or 0)
        if capture_ok("soak con %.0f phut, %.1f fps, %s C, nong %s" % (
                max(0, end - time.time()) / 60, v.frames / 30.0, st.get("nhiet_do_chip"), st.get("nong"))) is None:
            nloi += 1
    ok(nloi == 0, "soak: %d lan chup loi, nhiet cao nhat %.1f C, cam_reinit %s" % (nloi, tmax, st.get("cam_reinit")))

print("PASS test_cam" if not fails else "FAIL test_cam (%d)" % len(fails))
sys.exit(1 if fails else 0)
