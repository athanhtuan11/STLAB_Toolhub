# Gate firmware A1S guitar (Claude viet 2026-11-17, executor KHONG sua).
# Chay tu firmware/a1s:  ..\..\..\block-coding-car\firmware\.venv-host\Scripts\python.exe tests\test_gate.py
# 1) bien dich + chay tests/run_host.c tren may tinh bang zig; 2) kiem tinh ma nguon; 3) build that bang build.ps1.
import os, re, subprocess, sys
from pathlib import Path

H = Path(__file__).resolve().parent.parent
fails = []


def ok(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c:
        fails.append(m)


# 1. host
exe = H / "tests" / "run_host.exe"
exe.unlink(missing_ok=True)
cmd = [sys.executable, "-m", "ziglang", "cc", "-std=c11", "-O1", "-Wall", "-Werror", "-I", str(H / "main"),
       str(H / "tests" / "run_host.c"), str(H / "main" / "umi_proto.c"), str(H / "main" / "dsp.c"), "-o", str(exe)]
r = subprocess.run(cmd, capture_output=True, text=True)
ok(r.returncode == 0, "bien dich host (zig cc -Wall -Werror)" + ("" if r.returncode == 0 else ": " + r.stderr[-600:]))
if r.returncode == 0:
    r = subprocess.run([str(exe)], capture_output=True, text=True, timeout=120)
    print(r.stdout[-2500:])
    ok(r.returncode == 0, "run_host PASS")

# 2. tinh
src = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in (H / "main").glob("*.[ch]"))
for u in ("0x2B00", "0x2B12", "0x2B10", "0x2B16"):
    ok(re.search(u, src, re.I) is not None, f"GATT co UUID {u}")
ok("GUITAR UMI" in src, "ten quang ba GUITAR UMI (app Umi tim theo ten)")
sd = (H / "sdkconfig.defaults").read_text(encoding="utf-8") if (H / "sdkconfig.defaults").exists() else ""
ok("CONFIG_BT_NIMBLE_ENABLED=y" in sd, "sdkconfig.defaults bat NimBLE")
ok("i2s_channel_init_std_mode" in src and "44100" in src, "I2S std 44100 Hz")
ok(re.search(r"\b21\b", src) and "PA" in src.upper(), "bat ampli GPIO21")
ok("nvs_" in src, "luu cai dat vao NVS")
ok("umi_handle_write" in src and "umi_build_status" in src and "dsp_process" in src, "main goi giao thuc + DSP that")
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

print(f"\n{'PASS' if not fails else 'FAIL'} test_gate ({len(fails)} loi)")
sys.exit(1 if fails else 0)
