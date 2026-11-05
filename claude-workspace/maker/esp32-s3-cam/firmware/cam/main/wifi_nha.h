// Wi-Fi nha (STA) + mDNS + lenh cai Wi-Fi qua UART0 cho firmware do ESP32-S3-CAM.
#pragma once

#include <stddef.h>
#include <stdbool.h>

// Goi sau esp_wifi_init + esp_netif_create_default_wifi_ap, mode da la WIFI_MODE_APSTA, truoc esp_wifi_start.
void wifi_nha_init(void);

// Goi sau esp_wifi_start: bat mDNS va task doc lenh UART0.
void wifi_nha_start(void);

// Ghi cac truong JSON (khong co dau ngoac nhon): "sta_ssid","sta_ip","sta_rssi","sta_connected","mdns".
void wifi_nha_status_json(char *buf, size_t n);

// Khoa OTA luu NVS namespace "ota" (cai bang lenh UART0 OTAKEY). Khong bao gio in khoa.
bool ota_key_is_set(void);
// So sanh thoi gian hang so; false neu chua cai khoa hoac sai.
bool ota_key_check(const char *given);

// Da co IP tu Wi-Fi nha chua.
bool wifi_nha_sta_connected(void);
// Da cai Wi-Fi nha (muon ket noi) chua.
bool wifi_nha_configured(void);
