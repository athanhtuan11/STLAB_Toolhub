# Gate firmware xiaozhi cho ESP32-A1S (Claude viet, executor KHONG sua). Chay: python check_a1s.py
import json, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
WS = H.parents[3]                      # claude-workspace
SRC = WS / "community" / "78-xiaozhi-esp32"
B = H / "boards" / "stlab-a1s"
fails = []
def need(c, m):
    if not c: fails.append(m)
def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""

cfg = read(B / "config.h")
cc = "\n".join(p.read_text(encoding="utf-8") for p in B.glob("*.cc"))
cj = read(B / "config.json")
need(bool(cfg) and bool(cc) and bool(cj), "boards/stlab-a1s/ can config.h + config.json + *.cc")
try:
    j = json.loads(cj or "{}")
    need(j.get("target") == "esp32", 'config.json target "esp32"')
    need(j.get("type") == "stlab-a1s", 'config.json type "stlab-a1s"')
except ValueError:
    fails.append("config.json khong phai JSON")
# chan theo ket qua do (maker/english-teacher/CLAUDE.md "Ket qua do")
for name, pin in [("AUDIO_CODEC_I2C_SCL_PIN", 32), ("AUDIO_CODEC_I2C_SDA_PIN", 33), ("AUDIO_I2S_GPIO_MCLK", 0),
                  ("AUDIO_I2S_GPIO_BCLK", 27), ("AUDIO_I2S_GPIO_WS", 25), ("AUDIO_I2S_GPIO_DOUT", 26),
                  ("AUDIO_I2S_GPIO_DIN", 35), ("AUDIO_CODEC_PA_PIN", 21)]:
    need(re.search(r"#define\s+%s\s+GPIO_NUM_%d\b" % (name, pin), cfg) is not None, "%s = GPIO%d" % (name, pin))
need("Es8388AudioCodec" in cc, "dung Es8388AudioCodec")
need(re.search(r"BOOT_BUTTON_GPIO\s+GPIO_NUM_0\b", cfg) is None, "GPIO0 la MCLK - khong dung lam nut")
m = re.search(r"#define\s+AUDIO_DEFAULT_OUTPUT_VOLUME\s+(\d+)", cfg)
# 2026-11-06 Tuan bo tran am luong (tu chinh KEY5/KEY6); gate chi kiem trong 0..100. Nho: cho be dung thi chinh nho lai.
need(m is not None and 0 <= int(m.group(1)) <= 100, "AUDIO_DEFAULT_OUTPUT_VOLUME 0..100")
m = re.search(r"#define\s+STLAB_MAX_VOLUME\s+(\d+)", cfg)
need(m is not None and 0 < int(m.group(1)) <= 100, "STLAB_MAX_VOLUME 1..100")
need("STLAB_MAX_VOLUME" in cc, "board .cc kep am luong theo STLAB_MAX_VOLUME")
# dang ky bo + may chu trong lab
pat = "\n".join(p.read_text(encoding="utf-8") for p in (H / "patches").glob("*")) if (H / "patches").exists() else ""
need("BOARD_TYPE_STLAB_A1S" in pat and "stlab-a1s" in pat, "patches/ dang ky BOARD_TYPE_STLAB_A1S -> boards/stlab-a1s")
sync = read(H / "sync.ps1"); build = read(H / "build.ps1")
need("78-xiaozhi-esp32" in sync and "49b4380" in sync, "sync.ps1 chep tu community/78-xiaozhi-esp32 va kiem dung ban ghim 49b4380")
need("build-src" in sync and "build-src" in read(H / ".gitignore"), "build-src/ (ban chep) + .gitignore")
need("tools-v6.1" in build and "esp-idf-v6.1" in build and "MSYSTEM" in build, "build.ps1: IDF 6.1 + xoa bien MSYS")
need(re.search(r"Remove-Item[^\n]*xiaozhi\.bin", build) is not None, "build.ps1 xoa .bin cu truoc khi build")
need("STLAB_XIAOZHI_SERVER" in build or "STLAB_XIAOZHI_SERVER" in sync, "dia chi may chu lay tu bien STLAB_XIAOZHI_SERVER")
sdk = read(H / "build-src" / "sdkconfig")
need("CONFIG_BOARD_TYPE_STLAB_A1S=y" in sdk, "sdkconfig: CONFIG_BOARD_TYPE_STLAB_A1S=y")
need("tenclass" not in sdk and re.search(r'CONFIG_OTA_URL="http://(192\.168|10\.|172\.)', sdk) is not None,
     "CONFIG_OTA_URL tro ve may chu trong LAN (khong dung api.tenclass.net)")
need('CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions/v2/4m.csv"' in sdk, "phan vung 4m.csv")
need((H / "build-src" / "build" / "xiaozhi.bin").exists(), "build-src/build/xiaozhi.bin")
r = subprocess.run(["git", "-C", str(SRC), "status", "--porcelain"], capture_output=True, text=True)
need(r.returncode == 0 and r.stdout.strip() == "", "community/78-xiaozhi-esp32 phai nguyen (khong sua ban ghim)")
need(re.search(r"\)\s*\{\s*\}", cc) is None, "co khoi lenh rong")
# 2026-11-06 Tuan: cham KEY4 = noi chuyen ngay; giu KEY4 5 s = ngu; lau khong noi chuyen = tu ngu
need("talk_button_.OnPressDown" not in cc and "talk_button_.OnPressUp" not in cc, "KEY4 khong con giu-nha (OnPressDown/OnPressUp)")
need("talk_button_.OnClick" in cc and "talk_button_.OnLongPress" in cc, "KEY4 co OnClick + OnLongPress")
need(re.search(r"talk_button_\s*\(\s*TALK_BUTTON_GPIO\s*,\s*false\s*,\s*(5000|STLAB_TALK_LONG_MS)", cc) is not None
     and ("STLAB_TALK_LONG_MS" not in cc or re.search(r"#define\s+STLAB_TALK_LONG_MS\s+5000", cfg) is not None),
     "KEY4 giu 5000 ms (Button long_press_time)")
need("PowerSaveTimer" in cc and re.search(r"OnEnterSleepMode|OnShutdownRequest", cc) is not None, "tu ngu bang PowerSaveTimer")
m = re.search(r"#define\s+STLAB_IDLE_SLEEP_S\s+(\d+)", cfg)
need(m is not None and 30 <= int(m.group(1)) <= 300, "STLAB_IDLE_SLEEP_S 30..300 s trong config.h")
if fails:
    print("FAIL check_a1s:"); [print(" -", f) for f in fails]; sys.exit(1)
print("PASS check_a1s")
