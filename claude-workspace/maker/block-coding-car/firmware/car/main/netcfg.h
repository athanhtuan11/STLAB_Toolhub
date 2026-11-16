// Wi-Fi (STA theo NVS, AP du phong), mDNS, ten/mau xe, khoa OTA, lenh UART0.
// Lenh UART (ket thuc xuong dong): WIFI <ssid><TAB><mat khau> · WIFI? · WIFI_CLEAR · OTAKEY <khoa> · OTAKEY? · NAME <ten> <#mau>
// Mat khau va khoa OTA khong bao gio in ra log/UART.
#pragma once

#include <stdbool.h>
#include <stddef.h>

#include "eyes.h"

// Goi sau nvs_flash_init(). Khoi dong Wi-Fi (khong chan), mDNS, task lenh UART; 20 s chua noi duoc -> bat AP.
void netcfg_start(void);

const char *netcfg_name(void);    // vd "robot-do"
const char *netcfg_color(void);   // vd "#E0453A"
bool netcfg_sta_connected(void);
bool netcfg_ap_on(void);
void netcfg_ip(char *buf, size_t n);          // IP STA neu co, khong thi 192.168.4.1 khi AP
eyes_status_t netcfg_eye_status(void);

bool ota_key_check(const char *given);
