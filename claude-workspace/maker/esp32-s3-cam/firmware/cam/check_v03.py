# Gate tinh v0.3.0: OTA + phat hien chuyen dong + the TF (Claude viet, executor KHONG sua). Chay: python check_v03.py
# Chay kem check_cam.py (gate cu van phai PASS).
import re, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

H = Path(__file__).resolve().parent
fails = []


def need(cond, msg):
    if not cond:
        fails.append(msg)


def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""


m = H / "main"
src = "\n".join(p.read_text(encoding="utf-8") for p in sorted(m.glob("*.c")))
html = read(m / "index.html")
sdk = read(H / "sdkconfig.defaults")
cmake = read(m / "CMakeLists.txt")

need(re.search(r'CAM_VERSION\s+"0\.3\.0"', src) is not None, 'CAM_VERSION "0.3.0"')
need((H / "build" / "stlab_cam.bin").exists(), "build/stlab_cam.bin chua co (build.ps1)")

# --- OTA ---
need("CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y" in sdk, "sdkconfig.defaults: CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y")
for pat, msg in [
    (r'"/ota"', "endpoint /ota"),
    (r"HTTP_POST", "/ota la POST"),
    (r"esp_ota_begin\(", "esp_ota_begin"),
    (r"esp_ota_write\(", "esp_ota_write"),
    (r"esp_ota_end\(", "esp_ota_end (kiem anh)"),
    (r"esp_ota_set_boot_partition\(", "esp_ota_set_boot_partition"),
    (r"esp_ota_mark_app_valid_cancel_rollback\(", "danh dau ban moi hop le (rollback)"),
    (r"X-OTA-Key", "khoa OTA qua header X-OTA-Key"),
    (r"OTAKEY", "lenh UART OTAKEY luu khoa vao NVS"),
    (r"403", "sai/thieu khoa -> 403"),
    (r"\[OTA\]", "log [OTA]"),
]:
    need(re.search(pat, src) is not None, msg)
need(re.search(r"(printf|ESP_LOG\w)\([^;]*\b(ota_?key|otakey)\b[^;]*\);", src, re.I) is None, "khong in khoa OTA ra log")

# --- the TF (SDMMC 1-bit, chan theo Prusa module_ESP32-S3-CAM.h) ---
for pat, msg in [
    (r"esp_vfs_fat_sdmmc_mount\(", "mount the TF bang esp_vfs_fat_sdmmc_mount"),
    (r"\.width\s*=\s*1\b", "SDMMC 1-bit (slot.width = 1)"),
    (r"\.clk\s*=\s*(GPIO_NUM_)?39\b", "SD CLK = GPIO39"),
    (r"\.cmd\s*=\s*(GPIO_NUM_)?38\b", "SD CMD = GPIO38"),
    (r"\.d0\s*=\s*(GPIO_NUM_)?40\b", "SD D0 = GPIO40"),
    (r"format_if_mount_failed\s*=\s*false", "KHONG format the cua Tuan (format_if_mount_failed = false)"),
    (r"stlab-cam", "chi ghi/xoa trong thu muc stlab-cam tren the"),
    (r"\[SD\]", "log [SD]"),
]:
    need(re.search(pat, src) is not None, msg)
need(re.search(r"format_if_mount_failed\s*=\s*true", src) is None, "cam format the")
need("sdmmc" in cmake or "fatfs" in cmake or "REQUIRES" not in cmake, "CMakeLists: them fatfs/sdmmc neu dung REQUIRES")

# --- chuyen dong ---
for pat, msg in [
    (r"jpg2rgb565\(|fmt2rgb888\(|jpg2rgb888|esp_jpeg_decode|jpeg_dec", "giai ma JPEG nho de so sanh khung"),
    (r'"/events"', "endpoint /events"),
    (r'"/event\.jpg"', "endpoint /event.jpg (anh su kien gan nhat trong PSRAM, chay khi khong co the)"),
    (r'"/sd"', "endpoint /sd?f= tai file tren the"),
    (r"\.\.", "chan duong dan '..' o /sd"),
    (r"esp_sntp|esp_netif_sntp", "dong bo gio SNTP"),
    (r"ICT-7|Asia/Ho_Chi_Minh", "mui gio Viet Nam"),
    (r"\[MOTION\]", "log [MOTION]"),
    (r"xQueue|xRingbuffer|xStreamBuffer", "ghi the o task rieng qua queue (khong chan task camera)"),
]:
    need(re.search(pat, src) is not None, msg)
for v in ["motion", "motion_thr", "motion_pct"]:
    need(re.search(r'"%s"' % v, src) is not None, "/control thieu var " + v)
for k in ["motion", "motion_count", "motion_last_s", "sd_ok", "sd_free_mb", "ota_partition", "time_ok"]:
    need(('\\"%s\\"' % k) in src or ('"%s"' % k) in src, "/status thieu truong " + k)

# --- giao dien ---
need(len(html.encode("utf-8")) <= 40 * 1024, "index.html <= 40 KB")
need("/events" in html and "/event.jpg" in html, "trang / hien danh sach su kien + anh su kien")
need("motion" in html, "trang / co nut bat/tat phat hien chuyen dong")
need("sd_ok" in html, "trang / hien trang thai the TF")
need(re.search(r"Chuyển động|chuyển động", html) is not None, "nhan tieng Viet 'chuyển động'")

# --- cong cu may tinh ---
for f in ["ota.py", "ota-setup.py"]:
    t = read(H / f)
    need(bool(t), f + " chua co")
    need("STLAB_CAM_OTA_KEY" in t, f + ": dung bien moi truong STLAB_CAM_OTA_KEY (khong ghi khoa vao file)")
need("secrets" in read(H / "ota-setup.py"), "ota-setup.py: sinh khoa bang module secrets")
need("setx" in read(H / "ota-setup.py"), "ota-setup.py: luu khoa vao bien moi truong nguoi dung Windows (setx)")
need("X-OTA-Key" in read(H / "ota.py"), "ota.py gui header X-OTA-Key")

# --- chong ma gia ---
empty = re.findall(r"\)\s*\{\s*\}", src)
need(not empty, "co %d ham/khoi lenh rong" % len(empty))
need(re.search(r"TODO\s*:?\s*(implement|lam sau|viet sau)", src, re.I) is None, "con TODO chua lam")

if fails:
    print("FAIL check_v03:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS check_v03")
