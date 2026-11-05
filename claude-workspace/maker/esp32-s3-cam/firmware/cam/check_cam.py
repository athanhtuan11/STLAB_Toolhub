# Gate tinh firmware chinh cam (Claude viet, executor KHONG sua). Chay: python check_cam.py
import re, sys
from pathlib import Path

H = Path(__file__).resolve().parent
fails = []


def need(cond, msg):
    if not cond:
        fails.append(msg)


def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


m = H / "main"
src = "\n".join(p.read_text(encoding="utf-8") for p in m.glob("*.c"))
need((H / "build" / "stlab_cam.bin").exists(), "build/stlab_cam.bin chua co (build.ps1)")
need((m / "wifi_nha.c").exists() and (m / "wifi_nha.h").exists(), "copy wifi_nha.c/.h tu probe")
yml = read(m / "idf_component.yml")
need("esp32-camera" in yml and "espressif/mdns" in yml, "idf_component.yml: esp32-camera + mdns")
part = read(H / "partitions.csv")
need("ota_0" in part and "ota_1" in part, "partitions.csv: ota_0 + ota_1")
html = read(m / "index.html")
need(bool(html), "main/index.html (trang /)")
need("81" in html and "/stream" in html, "trang / lay video tu cong 81")
need(re.search(r"(src|href)\s*=\s*[\"']https?://", html) is None, "trang / khong tai tai nguyen ngoai")
need(any(ch in html for ch in "ằảệụốờ"), "trang / tieng Viet co dau")

for pat, msg in [
    (r"server_port\s*=\s*80\b", "server cong 80"),
    (r"server_port\s*=\s*81\b", "server cong 81 cho stream"),
    (r"lru_purge_enable\s*=\s*true", "lru_purge_enable = true"),
    (r"send_wait_timeout", "dat send_wait_timeout"),
    (r'"/control"', "endpoint /control"),
    (r'"/capture"', "endpoint /capture"),
    (r'"/status"', "endpoint /status"),
    (r'"/stream"', "endpoint /stream"),
    (r"set_vflip", "lat doc vflip"),
    (r"set_hmirror", "lat ngang hmirror"),
    (r'nvs_open\(\s*"cam_cfg"', 'luu cau hinh NVS "cam_cfg"'),
    (r"temperature_sensor_get_celsius", "doc nhiet chip"),
    (r"esp_camera_deinit", "watchdog init lai camera"),
    (r"503", "nguoi xem thu 3 -> 503"),
    (r"HTTPD_400|400", "/control sai -> 400"),
    (r'"0\.[123]\.0"', 'version 0.1-0.3'),
    (r"\[CAM\]", "log [CAM]"),
    (r"WIFI_MODE_APSTA", "giu Wi-Fi APSTA"),
]:
    need(re.search(pat, src) is not None, msg)

for k in ["nong", "fps_cai", "fps_thuc", "so_nguoi_xem", "frame_loi", "cam_reinit", "sta_ip", "ap_ssid", "vflip", "hmirror"]:
    need(('\\"%s\\"' % k) in src or ('"%s"' % k) in src, "/status thieu truong " + k)
# chi task camera duoc lay khung (cho phep them 1 lan khi khoi dong)
n_get = len(re.findall(r"esp_camera_fb_get\(", src))
need(1 <= n_get <= 2, "esp_camera_fb_get goi %d cho (chi task camera duoc lay khung)" % n_get)
need(re.search(r"(printf|ESP_LOG\w)\([^;]*\b(pass|password)\b[^;]*\);", src, re.I) is None, "khong in mat khau ra log")
empty = re.findall(r"\)\s*\{\s*\}", src)
need(not empty, "co %d ham/khoi lenh rong" % len(empty))

if fails:
    print("FAIL check_cam:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS check_cam")
