# Gate firmware xiaozhi ESP32-S3 + INMP441 + MAX98357A, tro chuyen truc tiep (Claude viet, executor KHONG sua).
# Chay: python check_s3.py   (sau sync.ps1 + build.ps1)
# Huong AEC (Claude chot 2026-11-12): khong co codec tra tham chieu loa -> AEC tren bo bang THAM CHIEU PHAN MEM
# (mau PCM vua ghi ra MAX98357A duoc chep vao vong dem, tre co dinh, tra ve kenh 2 cua Read()) -> esp-sr AFE "MR".
import json, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = Path(__file__).resolve().parent
WS = H.parents[3]                      # claude-workspace
SRC = WS / "community" / "78-xiaozhi-esp32"
B = H / "boards" / "stlab-s3"
fails = []
def need(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
def read(p):
    return p.read_text(encoding="utf-8") if p.exists() else ""

cfg = read(B / "config.h")
src = "\n".join(p.read_text(encoding="utf-8") for p in sorted(B.glob("*.cc")) + sorted(B.glob("*.h")) if p.name != "config.h")
cj = read(B / "config.json")
need(bool(cfg) and bool(src) and bool(cj), "boards/stlab-s3/ co config.h + config.json + *.cc")
try:
    j = json.loads(cj or "{}")
    need(j.get("target") == "esp32s3", 'config.json target "esp32s3"')
except ValueError:
    fails.append("config.json khong phai JSON")

# Chan = bread-compact-wifi cua xiaozhi (Tuan noi day theo so do cong dong pho bien)
for name, pin in [("AUDIO_I2S_MIC_GPIO_WS", 4), ("AUDIO_I2S_MIC_GPIO_SCK", 5), ("AUDIO_I2S_MIC_GPIO_DIN", 6),
                  ("AUDIO_I2S_SPK_GPIO_DOUT", 7), ("AUDIO_I2S_SPK_GPIO_BCLK", 15), ("AUDIO_I2S_SPK_GPIO_LRCK", 16)]:
    need(re.search(r"#define\s+%s\s+GPIO_NUM_%d\b" % (name, pin), cfg) is not None, "%s = GPIO%d" % (name, pin))
# N16R8 PSRAM octal chiem GPIO35..37 -> khong dung
used = [int(x) for x in re.findall(r"GPIO_NUM_(\d+)", cfg)]
need(not any(p in (35, 36, 37) for p in used), "khong dung GPIO35-37 (PSRAM octal N16R8)")
# Tham chieu = mau ra loa nguyen ven -> vao/ra cung 16 kHz, khong can doi tan so
need(re.search(r"#define\s+AUDIO_INPUT_SAMPLE_RATE\s+16000\b", cfg) is not None, "AUDIO_INPUT_SAMPLE_RATE 16000")
need(re.search(r"#define\s+AUDIO_OUTPUT_SAMPLE_RATE\s+16000\b", cfg) is not None, "AUDIO_OUTPUT_SAMPLE_RATE 16000 (tham chieu cung tan so mic)")
m = re.search(r"#define\s+STLAB_AEC_REF_DELAY_MS\s+(\d+)", cfg)
need(m is not None and 0 <= int(m.group(1)) <= 200, "STLAB_AEC_REF_DELAY_MS 0..200 (tre tham chieu, chinh khi do)")
m = re.search(r"#define\s+AUDIO_DEFAULT_OUTPUT_VOLUME\s+(\d+)", cfg)
need(m is not None and 0 <= int(m.group(1)) <= 100, "AUDIO_DEFAULT_OUTPUT_VOLUME 0..100")
m = re.search(r"#define\s+TALK_BUTTON_GPIO\s+GPIO_NUM_(\d+)", cfg)
need(m is not None, "TALK_BUTTON_GPIO co dinh nghia (cham = mo/dong phien, cham luc co noi = ngat)")

# Codec tham chieu phan mem
need(re.search(r"input_reference_\s*=\s*true", src) is not None, "codec dat input_reference_ = true")
need(re.search(r"input_channels_\s*=\s*2", src) is not None, "codec dat input_channels_ = 2 (mic + ref)")
need("STLAB_AEC_REF_DELAY_MS" in src, "codec dung STLAB_AEC_REF_DELAY_MS")
need(re.search(r"\bWrite\s*\(", src) is not None and re.search(r"\bRead\s*\(", src) is not None,
     "codec override Read() + Write()")
need(re.search(r"(MALLOC_CAP_SPIRAM|heap_caps_malloc|ring|Ring)", src) is not None, "vong dem tham chieu (PSRAM/ring)")
need(re.search(r"\)\s*(const\s*)?(override\s*)?\{\s*\}", src) is None, "khong co khoi lenh rong")
need(re.search(r"\bTODO\b|\bFIXME\b", src) is None, "khong de TODO/FIXME trong ma bo")

# Dang ky bo + mo khoa USE_DEVICE_AEC cho bo nay (sua ban chep, khong sua community)
pat = "\n".join(p.read_text(encoding="utf-8") for p in sorted((H / "patches").glob("*"))) if (H / "patches").exists() else ""
need("BOARD_TYPE_STLAB_S3" in pat and "stlab-s3" in pat, "patches/ dang ky BOARD_TYPE_STLAB_S3 -> boards/stlab-s3")
need(re.search(r"USE_DEVICE_AEC[\s\S]*BOARD_TYPE_STLAB_S3", pat) is not None, "patches/ them BOARD_TYPE_STLAB_S3 vao depends USE_DEVICE_AEC")

sync = read(H / "sync.ps1"); build = read(H / "build.ps1")
need("78-xiaozhi-esp32" in sync and "49b4380" in sync, "sync.ps1 chep tu community/78-xiaozhi-esp32, kiem ban ghim 49b4380")
need("C:\\xzb\\s3" in sync and "C:\\xzb\\s3" in build, "thu muc that ngan C:\\xzb\\s3 (khong dung chung C:\\xzb\\a1s)")
need("build-src" in read(H / ".gitignore"), ".gitignore co build-src")
need("tools-v6.1" in build and "esp-idf-v6.1" in build and "MSYSTEM" in build, "build.ps1: IDF 6.1 + xoa bien MSYS")
need("set-target esp32s3" in build, "build.ps1 set-target esp32s3")
need(re.search(r"Remove-Item[^\n]*xiaozhi\.bin", build) is not None, "build.ps1 xoa .bin cu truoc khi build")
need("STLAB_XIAOZHI_SERVER" in sync, "dia chi may chu tu bien STLAB_XIAOZHI_SERVER")

sdk = read(H / "build-src" / "sdkconfig")
for k in ("CONFIG_BOARD_TYPE_STLAB_S3=y", "CONFIG_USE_AUDIO_PROCESSOR=y", "CONFIG_USE_DEVICE_AEC=y",
          "CONFIG_SPIRAM=y", "CONFIG_SPIRAM_MODE_OCT=y", "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y", "CONFIG_LANGUAGE_VI_VN=y"):
    need(k in sdk, "sdkconfig: " + k)
need("CONFIG_USE_SERVER_AEC=y" not in sdk, "sdkconfig: KHONG bat USE_SERVER_AEC")
need('CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions/v2/16m.csv"' in sdk, "phan vung v2/16m.csv")
need("tenclass" not in sdk and re.search(r'CONFIG_OTA_URL="http://(192\.168|10\.|172\.)', sdk) is not None,
     "CONFIG_OTA_URL tro ve may chu LAN")
need((H / "build-src" / "build" / "xiaozhi.bin").exists(), "build-src/build/xiaozhi.bin")

r = subprocess.run(["git", "-C", str(SRC), "status", "--porcelain"], capture_output=True, text=True)
need(r.returncode == 0 and r.stdout.strip() == "", "community/78-xiaozhi-esp32 nguyen ven")
a1s = subprocess.run(["git", "-C", str(H.parent), "status", "--porcelain", "xiaozhi-a1s"], capture_output=True, text=True)
need(a1s.stdout.strip() == "" or all(l[3:].startswith("xiaozhi-a1s/build") or "gate.out" in l for l in a1s.stdout.splitlines()),
     "khong sua firmware/xiaozhi-a1s")

print("\nKET QUA:", "PASS" if not fails else "FAIL (%d)" % len(fails))
sys.exit(1 if fails else 0)
