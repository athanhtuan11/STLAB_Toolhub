#!/usr/bin/env python3
"""Cai Wi-Fi nha cho mach ESP32-S3-CAM qua cong COM (pyserial).

Chay: python wifi-setup.py --port COM6 [--ssid TEN] [--ask] [--clear] [--status]
Khong reset mach khi mo cong. Mat khau chi nam trong bien, khong in, khong ghi file.
"""
import argparse
import getpass
import re
import subprocess
import sys
import time

import serial

WAIT_IP_S = 30
WAIT_CLEAR_S = 5
WAIT_STATUS_S = 5


def run_netsh(args):
    try:
        raw = subprocess.run(["netsh"] + args, capture_output=True, timeout=15).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    for enc in ("oem", "mbcs"):
        try:
            return raw.decode(enc, errors="replace")
        except LookupError:
            continue
    return raw.decode("utf-8", errors="replace")


def current_ssid():
    for line in run_netsh(["wlan", "show", "interfaces"]).splitlines():
        m = re.match(r"^\s*SSID\s*:\s*(.+?)\s*$", line)
        if m and not line.strip().upper().startswith("BSSID"):
            return m.group(1)
    return ""


def profile_key(ssid):
    out = run_netsh(["wlan", "show", "profile", "name=" + ssid, "key=clear"])
    for line in out.splitlines():
        low = line.lower()
        if "key content" in low or "nội dung khóa" in low or "noi dung khoa" in low:
            if ":" in line:
                return line.split(":", 1)[1].strip()
    return None


def open_port(port):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = 115200
    ser.timeout = 1
    ser.dtr = False
    ser.rts = False
    ser.open()
    return ser


def send_line(ser, text):
    ser.write(text.encode("utf-8") + b"\n")
    ser.flush()


def read_lines(ser, seconds):
    """Sinh tung dong log (da giai ma) trong toi da `seconds` giay."""
    end = time.time() + seconds
    buf = b""
    while time.time() < end:
        chunk = ser.read(256)
        if not chunk:
            continue
        buf += chunk
        while b"\n" in buf:
            raw, buf = buf.split(b"\n", 1)
            yield raw.decode("utf-8", errors="replace").rstrip("\r")


def wait_ip(ser):
    for line in read_lines(ser, WAIT_IP_S):
        m = re.search(r"STA IP=(\d+\.\d+\.\d+\.\d+)", line)
        if m:
            print("Mo: http://stlab-cam.local  (IP: %s)" % m.group(1))
            return 0
        if "[DO] Loi" in line:
            print(line.strip())
            return 1
    print("Het %d s ma mach chua co IP. Kiem tra: sai mat khau? mach xa router? "
          "Router phai co Wi-Fi 2,4 GHz." % WAIT_IP_S)
    return 1


def wait_for(ser, needle, seconds):
    for line in read_lines(ser, seconds):
        if needle in line:
            return line.strip()
    return None


def main():
    ap = argparse.ArgumentParser(description="Cai Wi-Fi nha cho ESP32-S3-CAM")
    ap.add_argument("--port", required=True, help="cong COM, vi du COM6")
    ap.add_argument("--ssid", help="ten Wi-Fi (mac dinh: mang Windows dang ket noi)")
    ap.add_argument("--ask", action="store_true", help="tu nhap mat khau (an)")
    ap.add_argument("--clear", action="store_true", help="xoa Wi-Fi nha da luu")
    ap.add_argument("--status", action="store_true", help="xem trang thai Wi-Fi nha")
    args = ap.parse_args()

    try:
        ser = open_port(args.port)
    except (serial.SerialException, OSError) as e:
        print("Khong mo duoc %s: %s" % (args.port, e))
        return 1

    with ser:
        if args.clear:
            send_line(ser, "WIFI_CLEAR")
            if wait_for(ser, "Da xoa Wi-Fi nha", WAIT_CLEAR_S):
                print("Da xoa Wi-Fi nha.")
                return 0
            print("Khong thay mach xac nhan xoa.")
            return 1

        if args.status:
            send_line(ser, "WIFI?")
            line = wait_for(ser, "WIFI ssid=", WAIT_STATUS_S)
            if line:
                print(line)
                return 0
            print("Khong thay mach tra loi.")
            return 1

        ssid = args.ssid or current_ssid()
        if not ssid:
            ssid = input("Ten Wi-Fi (SSID): ").strip()
        if not ssid:
            print("Thieu SSID.")
            return 1
        if len(ssid.encode("utf-8")) > 32:
            print("SSID dai qua 32 byte.")
            return 1

        pw = None if args.ask else profile_key(ssid)
        if pw is None:
            pw = getpass.getpass("Mat khau Wi-Fi '%s' (khong hien khi go): " % ssid)
        if len(pw.encode("utf-8")) > 63:
            pw = ""
            print("Mat khau dai qua 63 byte.")
            return 1

        print("Cai Wi-Fi '%s' cho mach (mat khau: ***)..." % ssid)
        ser.reset_input_buffer()
        send_line(ser, "WIFI " + ssid + "\t" + pw)
        pw = ""
        del pw
        return wait_ip(ser)


if __name__ == "__main__":
    sys.exit(main())
