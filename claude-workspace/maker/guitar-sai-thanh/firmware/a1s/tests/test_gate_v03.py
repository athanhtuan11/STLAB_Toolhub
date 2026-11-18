# Gate firmware A1S guitar v0.3 - A2DP sink + Bluedroid (Claude viet 2026-11-18, executor KHONG sua).
# Chay tu firmware/a1s:  ..\..\..\block-coding-car\firmware\.venv-host\Scripts\python.exe tests\test_gate_v03.py
# 1) host v0.1 (umi_proto + dsp) + host v0.3 (mix) bang zig; 2) kiem tinh; 3) build that bang build.ps1.
import os, re, subprocess, sys
from pathlib import Path

H = Path(__file__).resolve().parent.parent
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


def host(name, srcs):
    exe = H / "tests" / f"{name}.exe"
    exe.unlink(missing_ok=True)
    cmd = [sys.executable, "-m", "ziglang", "cc", "-std=c11", "-O1", "-Wall", "-Werror", "-I", str(H / "main"),
           str(H / "tests" / f"{name}.c")] + [str(H / "main" / s) for s in srcs] + ["-o", str(exe)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok(r.returncode == 0, f"bien dich {name} (zig cc -Wall -Werror)" + ("" if r.returncode == 0 else ": " + r.stderr[-600:]))
    if r.returncode == 0:
        r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=120)
        print(r.stdout[-2500:])
        ok(r.returncode == 0, f"{name} PASS")


# 1. host
host("run_host", ["umi_proto.c", "dsp.c"])          # v0.1 khong duoc hong

host("run_host_v03", ["mix.c"])

# 2. tinh
main_dir = H / "main"
src = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in main_dir.glob("*.[ch]"))
mixc = (main_dir / "mix.c").read_text(encoding="utf-8", errors="replace") if (main_dir / "mix.c").exists() else ""
for u in ("0x2B00", "0x2B12", "0x2B10", "0x2B16"):
    ok(re.search(u, src, re.I) is not None, f"GATT co UUID {u}")
ok("GUITAR UMI" in src, "ten GUITAR UMI (app Umi tim theo ten)")
sd = (H / "sdkconfig.defaults").read_text(encoding="utf-8") if (H / "sdkconfig.defaults").exists() else ""
for k in ("CONFIG_BT_BLUEDROID_ENABLED=y", "CONFIG_BT_CLASSIC_ENABLED=y", "CONFIG_BT_A2DP_ENABLE=y",
          "CONFIG_BTDM_CTRL_MODE_BTDM=y", "CONFIG_BT_BLE_ENABLED=y"):
    ok(k in sd, f"sdkconfig.defaults {k}")
ok("CONFIG_BT_NIMBLE_ENABLED=y" not in sd, "NimBLE da tat")
ok("nimble" not in src.lower() and "ble_hs_" not in src, "khong con ma NimBLE")
ok("esp_ble_gatts_create_attr_tab" in src or "esp_ble_gatts_create_service" in src, "BLE bang Bluedroid GATTS")
ok("esp_a2d_sink_init" in src, "khoi tao A2DP sink")
ok("esp_a2d_sink_register_audio_data_callback" in src or "esp_a2d_sink_register_data_callback" in src
   or "esp_a2d_register_data_callback" in src, "dang ky callback du lieu A2DP")
ok("ESP_A2D_AUDIO_CFG_EVT" in src and "mix_set_src_rate" in src, "doc tan so mau tu AUDIO_CFG -> mix_set_src_rate")
ok("ESP_BT_IO_CAP_NONE" in src and "ESP_BT_GAP_CFM_REQ_EVT" in src, "SSP Just Works (khong PIN)")
ok("esp_bt_gap_set_scan_mode" in src, "dat che do connectable/discoverable")
ok(all(f in src for f in ("mix_push_pcm", "mix_pop", "mix_add", "mix_reset")), "main goi mix that")
ok(re.search(r"GUITAR_MUSIC_MIX\s+0\.6", src) is not None, "GUITAR_MUSIC_MIX 0.6")
ok('"BT"' in src and '"MUSIC' in src, "lenh UART BT + MUSIC")
ok("umi_handle_write" in src and "umi_build_status" in src and "dsp_process" in src, "van goi giao thuc + DSP v0.1")
ok("i2s_channel_init_std_mode" in src and "44100" in src, "I2S std 44100 Hz")
ok("nvs_" in src, "van luu NVS")
ok(re.search(r"\b(malloc|calloc|realloc|printf)\s*\(", mixc) is None, "mix.c: khong cap phat dong / printf")
ok("esp_" not in mixc and "freertos" not in mixc.lower(), "mix.c C thuan (khong phu thuoc ESP-IDF)")
empty = re.findall(r"\)\s*\{\s*(?://[^\n]*\s*)*\}", src)
ok(not empty, f"khong co ham rong ({len(empty)})")

# 3. build that
if os.environ.get("GATE_NO_BUILD") != "1":
    b = H / "build" / "guitar_a1s.bin"
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(H / "build.ps1")],
                       capture_output=True, text=True, timeout=1800)
    print(r.stdout[-1200:])
    ok(r.returncode == 0 and b.exists(), "build.ps1 -> build/guitar_a1s.bin")
    if b.exists():
        ok(b.stat().st_size < 0x1F0000, f"bin {b.stat().st_size} byte vua phan vung app (< 1,94 MB)")
    cfg = (H / "sdkconfig").read_text(encoding="utf-8") if (H / "sdkconfig").exists() else ""
    ok("CONFIG_BT_A2DP_ENABLE=y" in cfg and "CONFIG_BT_NIMBLE_ENABLED=y" not in cfg, "sdkconfig that da la Bluedroid + A2DP")

print(f"\n{'PASS' if not fails else 'FAIL'} test_gate_v03 ({len(fails)} loi)")
sys.exit(1 if fails else 0)
