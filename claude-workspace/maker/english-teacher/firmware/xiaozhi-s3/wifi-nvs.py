"""Nap Wi-Fi cho xiaozhi tren bo ESP32-S3 (ban sao wifi-nvs.py cua A1S, chi doi --chip esp32s3): SSID + mat khau Windows da luu -> anh NVS -> ghi vao 0x9000.
Chay (PowerShell da kich hoat ESP-IDF 6.1):  python wifi-nvs.py --port COM6 [--ssid TEN] [--server IP]
Kem khoa "ota_url" -> doi IP may chu (DHCP doi) chi can chay lai lenh nay, khong build lai firmware.
xiaozhi (78/esp-wifi-connect ssid_manager.cc): namespace "wifi", khoa "ssid" / "password" (muc 0).
Bang phan vung partitions/v2/16m.csv: nvs 0x9000, 0x4000 (giong 4m.csv). Mat khau khong in ra, file tam xoa ngay sau khi nap.
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
ap.add_argument("--port", default="COM6")
ap.add_argument("--ssid")
ap.add_argument("--ota-url", help="URL OTA day du, vd https://teacher.<domain>/xiaozhi/ota/ (qua VPS, bo dung moi noi)")
ap.add_argument("--server", help="IP may chu lab (mac dinh: STLAB_XIAOZHI_SERVER hoac IPv4 LAN may nay)")
a = ap.parse_args()


def lan_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # khong gui goi tin, chi chon card mang ra ngoai
        return s.getsockname()[0]
    finally:
        s.close()


server = a.server or os.environ.get("STLAB_XIAOZHI_SERVER") or lan_ip()
ota_url = a.ota_url or f"http://{server}:8003/xiaozhi/ota/"  # ota.cc doc khoa "ota_url" (namespace wifi) truoc CONFIG_OTA_URL
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
        f.write(f'ota_url,data,string,"{ota_url}"\n')
    subprocess.run([sys.executable, str(gen), "generate", str(csv), str(img), "0x4000"], check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32s3", "--port", a.port, "write_flash", "0x9000", str(img)],
                   check=True)
    print(f"Da nap Wi-Fi '{ssid}' + ota_url={ota_url} vao NVS (mat khau khong in ra).")
finally:
    for p in (csv, img):
        p.unlink(missing_ok=True)
    tmp.rmdir()
