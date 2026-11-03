# Gate tinh firmware do (Claude viet, executor KHONG sua). Chay sau build.ps1: python check_probe.py
import re, sys
from pathlib import Path

H = Path(__file__).resolve().parent
fails = []


def need(cond, msg):
    if not cond:
        fails.append(msg)


sd = (H / "sdkconfig.defaults").read_text(encoding="utf-8") if (H / "sdkconfig.defaults").exists() else ""
for k in ["CONFIG_IDF_TARGET=\"esp32s3\"", "CONFIG_SPIRAM=y", "CONFIG_SPIRAM_MODE_OCT=y",
          "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y", "CONFIG_SPIRAM_USE_MALLOC=y"]:
    need(k in sd, f"sdkconfig.defaults thieu {k}")
yml = (H / "main" / "idf_component.yml")
need(yml.exists() and "espressif/esp32-camera" in yml.read_text(encoding="utf-8"), "main/idf_component.yml phai khai espressif/esp32-camera")

src = "\n".join(p.read_text(encoding="utf-8") for p in (H / "main").glob("*.c"))
need(src != "", "khong co main/*.c")
# bo chan Freenove/GOOUUU (nguon: Freenove camera_pins.h CAMERA_MODEL_ESP32S3_EYE)
pins = {"xclk": 15, "siod": 4, "sioc": 5, "d0": 11, "d1": 9, "d2": 8, "d3": 10, "d4": 12, "d5": 18,
        "d6": 17, "d7": 16, "vsync": 6, "href": 7, "pclk": 13}
for name, gpio in pins.items():
    need(re.search(rf"\b{gpio}\b", src) is not None, f"thieu GPIO {gpio} ({name}) trong bang chan")
need("0x3660" in src.lower() or "OV3660_PID" in src, "phai nhan dien PID OV3660 (0x3660)")
need("esp_psram_get_size" in src, "phai in dung luong PSRAM (esp_psram_get_size)")
need("esp_flash_get_size" in src or "spi_flash_get_chip_size" in src, "phai in dung luong flash")
need("/stream" in src and "/capture" in src and "/status" in src, "web phai co /stream, /capture, /status")
need("WIFI_MODE_AP" in src, "phai phat Wi-Fi AP")
need("esp_read_mac" in src or "esp_efuse_mac_get_default" in src, "mat khau AP phai sinh tu MAC")
for m in re.finditer(r'\.password\s*=\s*"([^"]+)"', src):
    fails.append(f"KHONG duoc ghi mat khau co dinh trong ma: {m.group(1)!r}")
need((H / "build" / "probe.bin").exists() or any((H / "build").glob("*.bin")), "chua build ra .bin")

if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS check_probe")
