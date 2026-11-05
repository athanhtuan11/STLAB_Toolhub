# Gate tinh firmware do ESP32-A1S (Claude viet, executor KHONG sua). Chay sau build: python check_probe.py
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
fails = []
def need(c, m):
    if not c: fails.append(m)
def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""
src = "\n".join(p.read_text(encoding="utf-8") for p in (H / "main").glob("*.c")) if (H / "main").exists() else ""
sdk = read(H / "sdkconfig.defaults")
need((H / "build" / "probe_a1s.bin").exists(), "build/probe_a1s.bin chua co (build.ps1)")
need('CONFIG_IDF_TARGET="esp32"' in sdk, 'sdkconfig.defaults: CONFIG_IDF_TARGET="esp32"')
need("CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y" in sdk, "flash 4 MB")
need("CONFIG_SPIRAM=y" in sdk and "CONFIG_SPIRAM_IGNORE_NOTFOUND=y" in sdk, "bat PSRAM + SPIRAM_IGNORE_NOTFOUND (khong co PSRAM van chay)")
for pat, msg in [
    (r"esp_psram_get_size|heap_caps_get_total_size\(\s*MALLOC_CAP_SPIRAM", "in dung luong PSRAM"),
    (r"esp_flash_get_size|esp_flash_get_physical_size", "in dung luong flash"),
    (r"i2c_master_probe|i2c_master_cmd_begin", "quet I2C"),
    (r"0x10", "tim ES8388 0x10"), (r"0x11", "tim ES8388 0x11"), (r"0x1[aA]", "tim AC101 0x1A"),
    (r"\b32\b[\s\S]*\b33\b", "bo chan I2C 32/33"), (r"\b23\b[\s\S]*\b18\b", "bo chan I2C 23/18"),
    (r"\b27\b", "BCK 27"), (r"\b25\b", "WS/DOUT 25"), (r"\b26\b", "DOUT/WS 26"), (r"\b35\b", "DIN 35"),
    (r"\b21\b", "chan PA 21"),
    (r"i2s_channel_write|i2s_write", "phat am thanh I2S"),
    (r"i2s_channel_read|i2s_read", "thu micro I2S"),
    (r"1000", "tieng bip 1 kHz"),
    (r"\[DO\]", "log [DO]"),
    (r"\[KQ\]", "dong ket qua [KQ] tom tat"),
    (r"VOL_MAX|VOLUME_MAX|MAX_VOL", "hang so am luong tran"),
    (r"gpio_get_level", "doc nut bam"),
]:
    need(re.search(pat, src) is not None, msg)
need(re.search(r"\)\s*\{\s*\}", src) is None, "co khoi lenh rong")
need("menuconfig" not in read(H / "build.ps1"), "build.ps1 khong mo menuconfig")
for f in ["build.ps1", "flash.bat", "README.md"]:
    need((H / f).exists(), f + " chua co")
if fails:
    print("FAIL check_probe:"); [print(" -", f) for f in fails]; sys.exit(1)
print("PASS check_probe")
