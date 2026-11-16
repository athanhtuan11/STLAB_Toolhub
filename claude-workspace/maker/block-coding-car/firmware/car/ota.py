#!/usr/bin/env python3
"""Phat hanh firmware xe qua Wi-Fi: python ota.py [--host robot-do.local] [--bin build/block_coding_car.bin]

Khoa lay tu bien moi truong STLAB_CAR_OTA_KEY (cung khoa da nap vao xe bang lenh UART OTAKEY). Khong in khoa.
Exit 0 neu xe len lai voi version + phan vung OTA moi, 1 neu loi.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV = "STLAB_CAR_OTA_KEY"


def get_key():
    key = os.environ.get(ENV, "")
    if not key and sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                key = winreg.QueryValueEx(k, ENV)[0]
        except OSError:
            key = ""
    return key


def info(host):
    try:
        with urllib.request.urlopen("http://%s/info" % host, timeout=5) as f:
            return json.loads(f.read())
    except Exception:
        return {}


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="robot-do.local")
    ap.add_argument("--bin", default=str(here / "build" / "block_coding_car.bin"))
    a = ap.parse_args()

    key = get_key()
    if not key:
        print("Chua co bien moi truong %s (dat bang setx, mo terminal moi)." % ENV)
        return 1
    binf = Path(a.bin)
    if not binf.exists():
        print("Khong thay file " + str(binf))
        return 1
    data = binf.read_bytes()
    want_ver = None
    m = re.search(rb"\d+\.\d+\.\d+", data[48:48 + 32])  # esp_app_desc_t.version
    if m:
        want_ver = m.group(0).decode()

    before = info(a.host)
    if not before:
        print("Khong ket noi duoc " + a.host)
        return 1
    print("Truoc: fw %s" % before.get("fw"))
    if before.get("busy"):
        print("Xe dang chay chuong trinh - doi xe dung roi thu lai.")
        return 1
    print("Gui %d byte ..." % len(data))
    req = urllib.request.Request("http://%s/ota" % a.host, data=data, method="POST",
                                 headers={"X-OTA-Key": key, "Content-Type": "application/octet-stream"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as f:
            print("Xe tra %d: %s" % (f.status, f.read(80).decode("utf-8", "replace")))
    except urllib.error.HTTPError as e:
        print("Xe tu choi %d: %s" % (e.code, e.read(80).decode("utf-8", "replace")))
        return 1
    except Exception as e:
        print("Loi gui: %s" % e)
        return 1
    print("Da gui trong %.1f s, cho xe khoi dong lai ..." % (time.time() - t0))

    time.sleep(3)
    after = {}
    for i in range(40):
        after = info(a.host)
        if after:
            break
        time.sleep(2)
        print("  cho ... %d" % (i + 1))
    if not after:
        print("Xe khong len lai sau 80 s.")
        return 1
    print("Sau: fw %s" % after.get("fw"))
    if want_ver and after.get("fw") != want_ver:
        print("LOI: fw %s khac ban gui %s (co the da tu quay ve ban cu)." % (after.get("fw"), want_ver))
        return 1
    print("OTA OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
