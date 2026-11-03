# Gate tinh "Wi-Fi nha + mDNS + script cai Wi-Fi" (Claude viet, executor KHONG sua). Chay: python check_wifi.py
import re, sys
from pathlib import Path

H = Path(__file__).resolve().parent
fails = []


def need(cond, msg):
    if not cond:
        fails.append(msg)


src = "\n".join(p.read_text(encoding="utf-8") for p in (H / "main").glob("*.c"))
yml = (H / "main" / "idf_component.yml").read_text(encoding="utf-8")
need("espressif/mdns" in yml, "idf_component.yml phai them espressif/mdns")
need("WIFI_MODE_APSTA" in src, "phai chay AP + STA (giu AP du phong)")
need("nvs_set_str" in src and "nvs_get_str" in src, "luu/doc Wi-Fi nha trong NVS")
need("mdns_hostname_set" in src and '"stlab-cam"' in src, 'mDNS hostname "stlab-cam"')
need("mdns_service_add" in src and "_http" in src, "mDNS quang ba dich vu _http")
need("WIFI_CLEAR" in src or "WIFI-CLEAR" in src, "lenh xoa Wi-Fi nha")
need(re.search(r"uart_read_bytes|fgets|getchar", src) is not None, "doc lenh tu UART0 (cong COM CH340)")
need("STA IP" in src, 'phai in "[DO] STA IP=..." khi co IP')
# Siet 2026-11-03 (ban truoc chi co comment trong nhanh lenh van PASS): phai co ma that
for pat, msg in [
    (r'nvs_open\(\s*"wifi_nha"\s*,\s*NVS_READWRITE', 'mo NVS "wifi_nha" che do NVS_READWRITE khi luu/xoa'),
    (r"nvs_commit\(", "nvs_commit sau khi luu/xoa"),
    (r"nvs_erase_(all|key)\(", "WIFI_CLEAR phai xoa NVS (nvs_erase_all/nvs_erase_key)"),
    (r"esp_wifi_set_config\(\s*WIFI_IF_STA", "dat cau hinh STA (esp_wifi_set_config(WIFI_IF_STA, ...))"),
    (r"esp_wifi_connect\(", "esp_wifi_connect khi co Wi-Fi nha"),
    (r"esp_wifi_disconnect\(", "WIFI_CLEAR ngat STA (esp_wifi_disconnect)"),
    (r"IP_EVENT_STA_GOT_IP", "xu ly su kien IP_EVENT_STA_GOT_IP"),
    (r"WIFI_EVENT_STA_DISCONNECTED", "tu thu lai khi mat ket noi (WIFI_EVENT_STA_DISCONNECTED)"),
    (r"esp_wifi_sta_get_ap_info\(", "WIFI? / status in RSSI (esp_wifi_sta_get_ap_info)"),
    (r"uart_driver_install\(", "cai driver UART0 de doc lenh"),
    (r"strchr\([^)]*'\\t'\)|strtok[^;]*\\t|'\\t'", "tach SSID/mat khau bang dau tab"),
]:
    need(re.search(pat, src) is not None, msg)
need(re.search(r"nvs_set_str\(\s*NULL", src) is None, "nvs_set_str khong duoc dung handle NULL")
empty = re.findall(r"\{\s*(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/\s*|//[^\n]*\n\s*)*\}", src)
need(not empty, f"co {len(empty)} khoi lenh rong/chi co comment (phai viet ma that)")
# khong log mat khau: khong co dong ESP_LOG/printf nao co bien chua 'pass'
for line in src.splitlines():
    if re.search(r"(ESP_LOG[IWEDV]|printf)\s*\(", line) and re.search(r"\b\w*pass\w*\b", line, re.I) and "mat khau AP" not in line and "g_pass" not in line:
        fails.append("co the dang in mat khau Wi-Fi nha: " + line.strip()[:120])
need(not re.search(r'"VIETTEL[^"]*"', src, re.I), "KHONG ghi ten/mat khau mang nha trong ma")

ws = H / "wifi-setup.py"
need(ws.exists(), "thieu wifi-setup.py")
if ws.exists():
    w = ws.read_text(encoding="utf-8")
    need("netsh" in w and "key=clear" in w, "wifi-setup.py lay mat khau tu profile Windows (netsh ... key=clear)")
    need("getpass" in w, "wifi-setup.py co cach nhap tay an (getpass) khi khong doc duoc profile")
    need("serial" in w, "wifi-setup.py gui qua cong COM (pyserial)")
    for line in w.splitlines():
        if re.search(r"\bprint\s*\(", line) and re.search(r"\b(pw|pwd|password|key|matkhau)\b", line, re.I) and "***" not in line:
            fails.append("wifi-setup.py co the in mat khau: " + line.strip()[:120])
    need(not re.search(r"open\([^)]*['\"]w", w), "wifi-setup.py khong duoc ghi file")

if fails:
    print("FAIL", len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("PASS check_wifi")
