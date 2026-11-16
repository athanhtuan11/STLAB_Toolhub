#!/usr/bin/env python3
"""Cai Wi-Fi / ten / khoa OTA cho xe qua UART0 (115200). Chi chay khi xe dang dung USB va PIN DA TAT.

python wifi-setup.py --port COM7                      # hoi SSID, mat khau (getpass) -> lenh WIFI
python wifi-setup.py --port COM7 --name robot-xanh --color "#2A7DE1"   # lenh NAME (xe tu khoi dong lai)
python wifi-setup.py --port COM7 --ota-key            # nap khoa OTA tu bien moi truong STLAB_CAR_OTA_KEY
python wifi-setup.py --port COM7 --clear              # WIFI_CLEAR

Mat khau nhap bang getpass, khong ghi file, khong in. Khoa OTA khong in.
"""
import argparse
import getpass
import os
import sys
import time


def user_env(name):
    val = os.environ.get(name, "")
    if val or sys.platform != "win32":
        return val
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return ""


def send(ser, line, expect, secret=False):
    """Gui 1 dong, cho dong tra loi chua `expect`. Tra True neu thay."""
    ser.reset_input_buffer()
    ser.write((line + "\n").encode("utf-8"))
    end = time.time() + 6
    buf = b""
    while time.time() < end:
        buf += ser.read(256)
        if expect.encode() in buf:
            return True
        if b" ERR" in buf:
            break
    shown = buf.decode("utf-8", "replace").strip().splitlines()
    print("Xe tra loi: %s" % (shown[-1] if shown else "(khong co)"))
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="cong COM cua xe, vd COM7")
    ap.add_argument("--name", help="ten xe, vd robot-xanh (a-z 0-9 -)")
    ap.add_argument("--color", default="#E0453A", help="mau than #RRGGBB (di cung --name)")
    ap.add_argument("--ota-key", action="store_true", help="nap khoa OTA tu STLAB_CAR_OTA_KEY")
    ap.add_argument("--clear", action="store_true", help="xoa Wi-Fi da luu")
    a = ap.parse_args()
    try:
        import serial
    except ImportError:
        print("Thieu pyserial: pip install pyserial")
        return 1

    with serial.Serial(a.port, 115200, timeout=0.3) as ser:
        time.sleep(1.5)  # mo cong co the reset mach
        if a.ota_key:
            key = user_env("STLAB_CAR_OTA_KEY")
            if not key:
                print("Chua co bien moi truong STLAB_CAR_OTA_KEY.")
                return 1
            ok = send(ser, "OTAKEY " + key, "OTAKEY OK", secret=True)
            print("Khoa OTA: " + ("da nap" if ok else "LOI"))
            return 0 if ok else 1
        if a.clear:
            ok = send(ser, "WIFI_CLEAR", "WIFI_CLEAR OK")
            print("Xoa Wi-Fi: " + ("OK" if ok else "LOI"))
            return 0 if ok else 1
        if a.name:
            ok = send(ser, "NAME %s %s" % (a.name, a.color), "NAME OK")
            print("Dat ten: " + ("OK, xe khoi dong lai" if ok else "LOI"))
            return 0 if ok else 1
        ssid = input("Ten Wi-Fi (SSID): ").strip()
        pw = getpass.getpass("Mat khau Wi-Fi (khong hien): ")
        ok = send(ser, "WIFI %s\t%s" % (ssid, pw), "WIFI OK", secret=True)
        pw = ""
        print("Wi-Fi: " + ("da luu, xe dang ket noi" if ok else "LOI"))
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
