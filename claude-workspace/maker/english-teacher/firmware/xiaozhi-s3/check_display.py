# Gate mat Cu Bong tren man MSP2807 (Claude viet 2026-11-28, executor KHONG sua). Spec: spec-display.md
# Chay: python check_display.py   (sau sync.ps1 + build.ps1)
import re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
B = H / "boards" / "stlab-s3"
fails = []
def need(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
def read(p):
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

cfg = read(B / "config.h")
eyes = read(B / "owl_eyes_display.cc") + "\n" + read(B / "owl_eyes_display.h")
board = read(B / "stlab_s3.cc")
need(bool(read(B / "owl_eyes_display.cc")) and bool(read(B / "owl_eyes_display.h")), "co owl_eyes_display.h + .cc")

# 1. Chan (spec muc 1) + khong trung chan am thanh/nut
PINS = {"DISPLAY_SCK_PIN": 12, "DISPLAY_MOSI_PIN": 11, "DISPLAY_CS_PIN": 10, "DISPLAY_DC_PIN": 9, "DISPLAY_RST_PIN": 8,
        "DISPLAY_BACKLIGHT_PIN": 14, "TOUCH_MISO_PIN": 13, "TOUCH_CS_PIN": 17, "TOUCH_IRQ_PIN": 18}
for n, p in PINS.items():
    need(re.search(r"#define\s+%s\s+GPIO_NUM_%d\b" % (n, p), cfg) is not None, "%s = GPIO%d" % (n, p))
defs = dict((k, int(v)) for k, v in re.findall(r"#define\s+(\w+)\s+GPIO_NUM_(\d+)\b", cfg))
audio = {k: v for k, v in defs.items() if k.startswith(("AUDIO_I2S", "TALK_BUTTON", "BOOT_BUTTON"))}
need(set(audio.values()).isdisjoint(PINS.values()), "chan man/touch khong trung mic/loa/nut (%s)" % sorted(audio.values()))
need(len(set(audio.values())) == len(audio), "chan am thanh/nut khong trung nhau")
need(not any(p in (35, 36, 37) for p in defs.values()), "khong dung GPIO35-37 (PSRAM)")
need("VOLUME_UP_BUTTON_GPIO" not in cfg and "VOLUME_DOWN_BUTTON_GPIO" not in cfg and "volume_up_button_" not in board,
     "bo nut am luong GPIO39/40 (vo khong co nut)")
need(re.search(r"#define\s+DISPLAY_WIDTH\s+320\b", cfg) and re.search(r"#define\s+DISPLAY_HEIGHT\s+240\b", cfg),
     "DISPLAY_WIDTH 320 / HEIGHT 240 (ngang)")
need(re.search(r"#define\s+DISPLAY_SPI_HZ\s+(20000000|20 \* 1000 \* 1000)\b", cfg) is not None, "DISPLAY_SPI_HZ 20 MHz")
need(re.search(r"#define\s+STLAB_LCD_ST7789\s+[01]\b", cfg) is not None, "STLAB_LCD_ST7789 0/1 chon chip")
need("esp_lcd_new_panel_ili9341" in board + eyes and "esp_lcd_new_panel_st7789" in board + eyes, "tao panel ILI9341 + ST7789 (theo co)")
need(re.search(r"xpt2046", board + eyes, re.I) is not None, "dung XPT2046")

# 2. Den nen (mat be): tran 60 %
bl = {k: int(v) for k, v in re.findall(r"#define\s+(STLAB_BL_\w+)\s+(\d+)", cfg)}
need(bl.get("STLAB_BL_ACTIVE") == 40 and bl.get("STLAB_BL_IDLE") == 25 and bl.get("STLAB_BL_SLEEP") == 8,
     "den nen 40/25/8 %% (co %s)" % bl)
need(all(v <= 60 for v in bl.values()), "moi muc den nen <= 60 %")
lit = [int(x) for x in re.findall(r"SetBrightness\s*\(\s*(\d+)", board + eyes)]
need(all(v <= 60 for v in lit), "SetBrightness so cung <= 60 (%s)" % lit)

# 3. Mat: mau + hinh hoc (spec 2.1) – so phai co trong ma, khong anh/GIF
for c in ("0A0F18", "4FC3F7", "FFC83D", "FF7FB0", "A99BE0", "14203A", "7A8699"):
    need(re.search(c, eyes, re.I) is not None, "mau #" + c)
for n in ("77", "243", "120", "72", "84", "62", "82", "36"):
    need(re.search(r"\b%s\b" % n, eyes) is not None, "so hinh hoc %s px" % n)
for st in ("Listening", "Speaking", "Idle", "Connecting", "WifiConfiguring", "FatalError"):
    need(("kDeviceState" + st) in eyes + board, "xu ly kDeviceState" + st)
for e in ("happy", "laughing", "loving"):
    need('"%s"' % e in eyes, 'SetEmotion "%s" -> Khen' % e)
for f in ("SetupUI", "SetEmotion", "SetStatus", "SetChatMessage"):
    need(re.search(r"\b%s\s*\([^)]*\)\s*(const\s*)?override" % f, eyes) is not None, "override " + f)
need("lv_anim" in eyes, "co hoat anh lv_anim (tho/chop)")
need("DisplayLockGuard" in eyes + board, "LVGL trong DisplayLockGuard")
need(re.search(r"lv_image_set_src|\.gif\b|LV_IMAGE_DECLARE|lv_gif", eyes) is None, "khong dung anh/GIF")
need(re.search(r"\b2500\b", eyes) is not None and re.search(r"\b150\b", eyes) is not None, "Khen tu ve sau 2500 ms, chop 150 ms")

# 4. Cham (spec 4): ngu -> thuc, noi -> KHONG ngat loi
touch = board + eyes
need("WakeUp()" in touch, "cham khi ngu goi power_save_timer WakeUp")
need(re.search(r"\b400\b", touch) is not None, "chong doi 400 ms")
tf = re.search(r"(?is)(on_?touch|touch_?task|Touch\w*\s*\()[\s\S]{0,3000}", touch)
need(tf is not None and "AbortSpeaking" not in tf.group(0) and "ToggleChatState" not in tf.group(0),
     "xu ly cham khong AbortSpeaking/ToggleChatState")

# 5. Khong co man van chay: khong ESP_ERROR_CHECK tren touch
need(re.search(r"ESP_ERROR_CHECK\s*\(\s*esp_lcd_touch_new", touch) is None, "touch khong ESP_ERROR_CHECK (khong man van chay)")

# 6. Ma that, patch, build moi
need(re.search(r"\)\s*(const\s*)?(override\s*)?\{\s*\}", eyes) is None, "khong co khoi lenh rong")
need(re.search(r"\bFIXME\b", eyes) is None, "khong FIXME")
need(len(read(B / "owl_eyes_display.cc").splitlines()) >= 150, "owl_eyes_display.cc >= 150 dong (ma that)")
pat = "\n".join(read(p) for p in sorted((H / "patches").glob("*.patch")))
need("esp_lcd_touch_xpt2046" in pat, "patch them esp_lcd_touch_xpt2046 vao idf_component.yml")
need(re.search(r"0003", read(H / "sync.ps1")) is not None or "*.patch" in read(H / "sync.ps1"), "sync.ps1 ap patch 0003")
bin_ = H / "build-src" / "build" / "xiaozhi.bin"
srcs = [B / "owl_eyes_display.cc", B / "stlab_s3.cc", B / "config.h"]
need(bin_.exists() and all(s.exists() and bin_.stat().st_mtime > s.stat().st_mtime for s in srcs), "xiaozhi.bin moi hon ma nguon")
blog = read(H / "build.log")
need(bool(blog) and "error:" not in blog, "build.log khong loi bien dich (build tang dan co the khong bien dich lai owl_eyes_display)")

r = subprocess.run([sys.executable, str(H / "check_s3.py")], capture_output=True, text=True, encoding="utf-8", errors="replace")
need(r.returncode == 0, "check_s3.py PASS" + ("" if r.returncode == 0 else ": " + " | ".join(l for l in r.stdout.splitlines() if l.startswith("FAIL"))[:400]))

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
