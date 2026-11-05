"""Nap Wi-Fi cho xiaozhi tren bo A1S giong may tinh: lay SSID + mat khau Windows da luu -> anh NVS -> ghi vao 0x9000.
Chay (PowerShell da kich hoat ESP-IDF 6.1):  python wifi-nvs.py --port COM5 [--ssid TEN]
xiaozhi (78/esp-wifi-connect ssid_manager.cc): namespace "wifi", khoa "ssid" / "password" (muc 0).
Bang phan vung partitions/v2/4m.csv: nvs 0x9000, 0x4000. Mat khau khong in ra, file tam xoa ngay sau khi nap.
"""
import argparse, importlib.util, os, subprocess, sys, tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
WS = H.parents[3]
spec = importlib.util.spec_from_file_location(
    "wifi_setup", WS / "maker" / "esp32-s3-cam" / "firmware" / "probe" / "wifi-setup.py")
ws = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ws)  # dung lai current_ssid() / profile_key() (netsh)

ap = argparse.ArgumentParser()
ap.add_argument("--port", default="COM5")
ap.add_argument("--ssid")
a = ap.parse_args()
ssid = a.ssid or ws.current_ssid()
if not ssid:
    sys.exit("Khong thay Wi-Fi dang ket noi - dung --ssid")
pw = ws.profile_key(ssid)
if pw is None:
    sys.exit(f"Windows khong luu mat khau cho '{ssid}'")
idf = os.environ.get("IDF_PATH")
if not idf:
    sys.exit("Chua kich hoat ESP-IDF 6.1 (IDF_PATH)")
gen = Path(idf) / "components" / "nvs_flash" / "nvs_partition_generator" / "nvs_partition_gen.py"
tmp = Path(tempfile.mkdtemp(prefix="stlab-nvs-"))
csv, img = tmp / "wifi.csv", tmp / "nvs.bin"
try:
    with open(csv, "w", encoding="utf-8", newline="\n") as f:
        f.write("key,type,encoding,value\nwifi,namespace,,\n")
        f.write(f'ssid,data,string,"{ssid}"\n')
        f.write(f'password,data,string,"{pw}"\n')
    subprocess.run([sys.executable, str(gen), "generate", str(csv), str(img), "0x4000"], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", a.port, "write_flash", "0x9000", str(img)],
                   check=True)
    print(f"Da nap Wi-Fi '{ssid}' vao NVS (mat khau khong in ra).")
finally:
    for p in (csv, img):
        p.unlink(missing_ok=True)
    tmp.rmdir()
