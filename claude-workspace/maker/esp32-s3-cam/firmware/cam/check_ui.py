# Gate tinh giao dien web v0.2 (Claude viet, executor KHONG sua). Chay: python check_ui.py
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

H = Path(__file__).resolve().parent
fails = []


def need(cond, msg):
    if not cond:
        fails.append(msg)


html_p = H / "main" / "index.html"
html = html_p.read_text(encoding="utf-8") if html_p.exists() else ""
src = "\n".join(p.read_text(encoding="utf-8") for p in (H / "main").glob("*.c"))

need(0 < len(html.encode("utf-8")) <= 40 * 1024, "index.html phai co va <= 40 KB (%d B)" % len(html.encode("utf-8")))
need(re.search(r"(src|href)\s*=\s*[\"']https?://", html) is None and "@import" not in html, "khong tai tai nguyen ngoai")
need("prefers-color-scheme" in html, "che do sang/toi (prefers-color-scheme)")
need(re.search(r"location\.hostname", html) is not None and ":81/stream" in html, "video tu http://<hostname>:81/stream")
need('id="video"' in html, '<img id="video">')
for ep in ["/status", "/capture", "/control"]:
    need(ep in html, "trang goi " + ep)
for var in ["framesize", "vflip", "hmirror", "brightness", "contrast", "fps", "rotate"]:
    need(re.search(r"var=%s|['\"]%s['\"]" % (var, var), html) is not None, "dieu khien " + var)
for k in ["sta_ssid", "sta_rssi", "sta_ip", "nhiet_do_chip", "nong", "fps_thuc", "so_nguoi_xem"]:
    need(k in html, "hien thi truong " + k)
for txt in ["Chụp ảnh", "Tải ảnh", "Lật 180°", "Xoay 90°", "stlab-cam.local", "Mất kết nối", "2 người xem"]:
    need(txt in html, "thieu chu: " + txt)
need(re.search(r"setInterval\([^)]*2000|2000\s*\)", html) is not None, "cap nhat /status moi 2 s")
need("canvas" in html, "tai anh da xoay bang canvas")
need(re.search(r"rotate\(", html) is not None, "xoay hien thi bang CSS transform rotate()")
need(re.search(r"TODO", html) is not None, "nguong nhiet ghi TODO")
need(re.search(r"<svg[^>]*>.*?(sky|desk|wall)", html, re.S) is None and 'id="sky"' not in html, "bo hinh minh hoa SVG mockup")
need(re.search(r"password|mat khau|mật khẩu", html, re.I) is None, "khong co form/mat khau")

need('"0.2.0"' in src, 'version "0.2.0"')
need(re.search(r'"rotate"', src) is not None, "/control + /status co rotate")
need(re.search(r"\b270\b", src) is not None, "rotate nhan 0/90/180/270")

if fails:
    print("FAIL check_ui:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS check_ui")
