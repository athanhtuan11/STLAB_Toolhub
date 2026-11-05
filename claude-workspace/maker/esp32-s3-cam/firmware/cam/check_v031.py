# Gate tinh v0.3.1: giam nhiet (Claude viet, executor KHONG sua). Chay sau check_cam.py + check_v03.py.
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
src = "\n".join(p.read_text(encoding="utf-8") for p in sorted((H / "main").glob("*.c")))
sdk = (H / "sdkconfig.defaults").read_text(encoding="utf-8")
html = (H / "main" / "index.html").read_text(encoding="utf-8")
fails = []
def need(c, m):
    if not c: fails.append(m)

need(re.search(r'CAM_VERSION\s+"0\.3\.1"', src) is not None, 'CAM_VERSION "0.3.1"')
# 1. camera ngu that khi khong ai xem + motion tat
need(len(re.findall(r"esp_camera_deinit\(", src)) >= 2, "esp_camera_deinit dung ca cho watchdog lan cho camera ngu (>= 2 cho)")
need(re.search(r"CAM_IDLE_SLEEP_S", src) is not None, "hang so CAM_IDLE_SLEEP_S (giay khong ai dung truoc khi camera ngu)")
need(re.search(r"\[CAM\][^\n]*(ngu|Ngu)", src) is not None, "log [CAM] ... ngu")
# 2. Wi-Fi: tat AP khi da vao Wi-Fi nha, bat lai khi mat; tiet kiem dien khi khong ai xem
need(re.search(r"esp_wifi_set_mode\(\s*WIFI_MODE_STA\s*\)", src) is not None, "chuyen sang WIFI_MODE_STA khi da co IP Wi-Fi nha")
need(re.search(r"esp_wifi_set_mode\(\s*WIFI_MODE_APSTA\s*\)", src) is not None, "van bat lai APSTA khi mat Wi-Fi nha / chua cai")
need(re.search(r"esp_wifi_set_ps\(\s*WIFI_PS_MIN_MODEM", src) is not None, "esp_wifi_set_ps(WIFI_PS_MIN_MODEM) khi khong ai xem")
need(re.search(r"esp_wifi_set_ps\(\s*WIFI_PS_NONE", src) is not None, "esp_wifi_set_ps(WIFI_PS_NONE) khi dang stream")
need(re.search(r"AP_OFF_DELAY_S", src) is not None and re.search(r"AP_BACK_DELAY_S", src) is not None,
     "hang so AP_OFF_DELAY_S / AP_BACK_DELAY_S")
# 3. quan ly dien nang (DFS, khong light sleep)
need("CONFIG_PM_ENABLE=y" in sdk, "sdkconfig.defaults: CONFIG_PM_ENABLE=y")
need(re.search(r"esp_pm_configure\(", src) is not None, "esp_pm_configure (max 240, min 80)")
need(re.search(r"light_sleep_enable\s*=\s*false", src) is not None, "light_sleep_enable = false (camera/HTTP)")
# /status + UI
for k in ["cam_sleep", "ap_on", "wifi_ps"]:
    need(('\\"%s\\"' % k) in src or ('"%s"' % k) in src, "/status thieu truong " + k)
need("cam_sleep" in html, "trang / hien camera dang ngu")
need(re.search(r"max-width\s*:\s*100%|overflow-x\s*:\s*hidden|minmax\(0", html) is not None,
     "trang / khong tran ngang tren dien thoai (max-width:100% / minmax(0,...) / overflow-x)")
empty = re.findall(r"\)\s*\{\s*\}", src)
need(not empty, "co %d khoi lenh rong" % len(empty))
for f in ["thermal_log.py", "test_v031.py"]:
    need((H / f).exists(), f + " (Claude viet) phai con nguyen")
if fails:
    print("FAIL check_v031:"); [print(" -", f) for f in fails]; sys.exit(1)
print("PASS check_v031")
