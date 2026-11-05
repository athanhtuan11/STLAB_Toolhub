#!/usr/bin/env python3
"""Cai khoa OTA cho mach STLab Cam (chay 1 lan moi mach).

python ota-setup.py --port COM7

- Khoa lay tu bien moi truong nguoi dung STLAB_CAM_OTA_KEY neu da co (de nhieu mach dung chung 1 khoa),
  neu chua co thi sinh bang secrets.token_urlsafe(24) va luu bang `setx` (khong ghi file, khong in khoa).
- Gui lenh `OTAKEY <khoa>` qua UART0 (115200), cho `OTAKEY OK`.
Sau setx, phai mo cua so terminal MOI de bien co hieu luc.
"""
import argparse
import os
import secrets
import subprocess
import sys
import time

ENV = "STLAB_CAM_OTA_KEY"


def user_env_key():
    """Doc bien nguoi dung tu registry (setx khong ap vao shell dang chay)."""
    key = os.environ.get(ENV, "")
    if key or sys.platform != "win32":
        return key
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, ENV)[0]
    except OSError:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="cong COM cua mach, vd COM7")
    a = ap.parse_args()
    try:
        import serial
    except ImportError:
        print("Thieu pyserial: pip install pyserial")
        return 1

    key = user_env_key()
    is_new = not key
    if is_new:
        key = secrets.token_urlsafe(24)

    with serial.Serial(a.port, 115200, timeout=0.5) as ser:
        # Mo cong co the reset mach (DTR/RTS): gui lai moi giay toi 20 s cho toi khi mach chay xong va tra loi.
        ok = False
        buf = b""
        t_end = time.time() + 20
        while time.time() < t_end and not ok:
            ser.write(("OTAKEY " + key + "\n").encode("ascii"))
            ser.flush()
            t_wait = time.time() + 1
            while time.time() < t_wait and not ok:
                buf += ser.read(256)
                ok = b"OTAKEY OK" in buf
        if not ok:
            print("Mach khong tra OTAKEY OK (kiem tra cong COM / firmware >= 0.3.0).")
            return 1
        ser.write(b"OTAKEY?\n")
        ser.flush()
        buf = b""
        t_end = time.time() + 3
        while time.time() < t_end and b"OTAKEY SET" not in buf:
            buf += ser.read(256)
        print("Mach bao: " + ("OTAKEY SET" if b"OTAKEY SET" in buf else "(khong doc lai duoc)"))

    if is_new:
        r = subprocess.run(["setx", ENV, key], capture_output=True)
        if r.returncode != 0:
            print("setx loi - khoa da nap vao mach nhung KHONG luu duoc vao bien moi truong!")
            return 1
        print("Da sinh khoa moi, luu vao bien nguoi dung %s (mo terminal moi de dung)." % ENV)
    else:
        print("Dung lai khoa trong bien %s." % ENV)
    return 0


if __name__ == "__main__":
    sys.exit(main())
