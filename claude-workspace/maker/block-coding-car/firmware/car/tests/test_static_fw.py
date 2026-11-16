"""Gate tinh firmware block-coding-car: chan so lieu sai/ma gia truoc khi build that (build.ps1 chay sau)."""
import re
from pathlib import Path

import yaml

CAR = Path(__file__).resolve().parents[1]
MAIN = CAR / "main"
WIRING = CAR.parents[1] / "hardware" / "wiring.yaml"


def read(p):
    return (CAR / p).read_text(encoding="utf-8")


def all_c():
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(MAIN.glob("*.[ch]")))


def strip_comments(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"//[^\n]*", "", s)


def test_files_exist():
    for p in ["CMakeLists.txt", "main/CMakeLists.txt", "main/idf_component.yml", "sdkconfig.defaults",
              "partitions.csv", "build.ps1", "main/pins.h", "main/prog.c", "main/prog.h", "main/main.c",
              "main/stepper.c", "main/stepper.h", "tests/run_golden.c", "README.md"]:
        assert (CAR / p).exists(), p


def wiring_gpio():
    w = yaml.safe_load(WIRING.read_text(encoding="utf-8"))
    m = {}
    for wire in w["wires"]:
        a, b = wire["from"], wire["to"]
        if b.startswith("esp.GPIO"):
            m[a] = int(b[len("esp.GPIO"):])
        elif a.startswith("esp.GPIO"):
            m[b] = int(a[len("esp.GPIO"):])
    return m


def test_pins_match_wiring():
    g = wiring_gpio()
    want = {
        "PIN_ML_IN1": g["ml.IN1"], "PIN_ML_IN2": g["ml.IN2"], "PIN_ML_IN3": g["ml.IN3"], "PIN_ML_IN4": g["ml.IN4"],
        "PIN_MR_IN1": g["mr.IN1"], "PIN_MR_IN2": g["mr.IN2"], "PIN_MR_IN3": g["mr.IN3"], "PIN_MR_IN4": g["mr.IN4"],
        "PIN_LED": g["buf.1A"], "PIN_I2S_BCLK": g["amp.BCLK"], "PIN_I2S_LRC": g["amp.LRC"],
        "PIN_I2S_DIN": g["amp.DIN"], "PIN_BTN_STOP": g["btn.1"], "PIN_BATT_ADC": g["div.Giữa"],
    }
    pins = strip_comments(read("main/pins.h"))
    for name, gpio in want.items():
        m = re.search(rf"#define\s+{name}\s+(?:GPIO_NUM_)?(\d+)\b", pins)
        assert m, f"pins.h thieu {name}"
        assert int(m.group(1)) == gpio, f"{name}={m.group(1)} nhung wiring.yaml = GPIO{gpio}"
    for bad in (0, 3, 19, 20, 35, 36, 37, 45, 46, 43, 44):
        assert not re.search(rf"#define\s+PIN_\w+\s+(?:GPIO_NUM_)?{bad}\b", pins), f"dung chan cam GPIO{bad}"


def test_protocol_constants():
    src = strip_comments(all_c())
    for k in ("4054", "1698"):  # steps_cell, steps_90 mac dinh (PROTOCOL.md muc 5)
        assert k in src, f"thieu hang so mac dinh {k}"
    for n in ("200", "500", "300"):
        assert re.search(rf"\b{n}\b", src), f"thieu so toc do/nghi {n}"
    for mv in ("4400", "4200"):
        assert mv in src, f"thieu nguong pin {mv} mV"
    for code in ("busy", "batt_low", "bad_msg", "bad_json", "bad_version", "empty", "bad_op", "bad_arg", "dup_id",
                 "nested_repeat", "empty_repeat", "too_many_blocks"):
        assert f'"{code}"' in src, f"thieu ma loi {code}"
    for t in ("hello", "run", "stop", "dry", "cal", "started", "step", "done", "stopped", "err", "batt"):
        assert f'"{t}"' in src, f"thieu loai thong diep {t}"
    for why in ("client", "button", "batt"):
        assert f'"{why}"' in src


def test_no_stub_and_real_calls():
    src = strip_comments(all_c())
    assert not re.search(r"\)\s*\{\s*\}", src), "co ham/khoi rong"
    assert "TODO_IMPLEMENT" not in src
    for call in ("gpio_set_level", "httpd_ws_send_frame_async", "httpd_ws_recv_frame", "mdns_hostname_set",
                 "nvs_set_i32", "esp_ota_begin", "esp_ota_mark_app_valid_cancel_rollback", "i2s_channel_write",
                 "led_strip_set_pixel", "adc_oneshot_read", "adc_cali", "cJSON_Parse", "prog_expand",
                 "esp_wifi_set_mode", "WIFI_MODE_AP"):
        assert call in src, f"khong goi {call}"


def test_prog_is_pure_c():
    p = strip_comments(read("main/prog.c"))
    for inc in re.findall(r'#include\s*[<"]([^>"]+)', p):
        assert not inc.startswith(("esp_", "freertos", "driver")), f"prog.c phai thuan C (host test), co {inc}"


def test_coils_released():
    s = strip_comments(read("main/stepper.c"))
    assert re.search(r"stepper_release", s), "thieu stepper_release"
    assert len(re.findall(r"stepper_release\s*\(", strip_comments(all_c()))) >= 3, "nha cuon it nhat o xong/dung/loi"


def test_sound_and_led_limits():
    src = strip_comments(all_c())
    m = re.search(r"#define\s+SOUND_MAX_PCT\s+(\d+)", src)
    assert m and int(m.group(1)) <= 30, "SOUND_MAX_PCT <= 30"
    m = re.search(r"#define\s+LED_MAX_PCT\s+(\d+)", src)
    assert m and int(m.group(1)) <= 25, "LED_MAX_PCT <= 25"


def test_sdkconfig_partitions():
    d = read("sdkconfig.defaults")
    for k in ("CONFIG_IDF_TARGET=\"esp32s3\"", "CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y", "CONFIG_PARTITION_TABLE_CUSTOM=y",
              "CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE=y", "CONFIG_HTTPD_WS_SUPPORT=y", "CONFIG_SPIRAM_MODE_OCT=y"):
        assert k in d, k
    p = read("partitions.csv")
    assert "ota_0" in p and "ota_1" in p and "otadata" in p


def test_app_embedded():
    cm = read("main/CMakeLists.txt")
    assert "www/index.html.gz" in cm and "EMBED_FILES" in cm
    b = read("build.ps1")
    assert "app" in b and "build.py" in b and "--out" in b, "build.ps1 phai goi app/build.py --out main/www/index.html.gz"
    assert "Content-Encoding" in all_c() and "gzip" in all_c()


def test_no_secrets():
    for p in list(MAIN.glob("*")) + [CAR / "sdkconfig.defaults"]:
        if p.is_file():
            t = p.read_text(encoding="utf-8", errors="ignore")
            assert not re.search(r'(?i)(password|pass|ssid)\s*=\s*"[^"]{3,}"', t), f"nghi co mat khau trong {p.name}"
