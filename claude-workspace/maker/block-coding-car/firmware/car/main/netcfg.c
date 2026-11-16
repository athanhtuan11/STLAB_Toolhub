// Wi-Fi + ten xe + khoa OTA + lenh UART0. Theo mau esp32-s3-cam/main/wifi_nha.c (khong in mat khau/khoa).
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_system.h"
#include "nvs.h"
#include "driver/uart.h"
#include "mdns.h"

#include "netcfg.h"

#define SSID_MAX       32
#define PW_MAX         63
#define NAME_MAX_LEN   24
#define STA_WAIT_US    (20 * 1000000LL)   // PROTOCOL muc 5: 20 s khong noi duoc -> AP
#define RETRY_US       (10 * 1000000LL)
#define LINE_MAX_LEN   192
#define UART_PORT      UART_NUM_0
#define OTA_KEY_MIN    16
#define OTA_KEY_MAX    64

static const char *TAG = "netcfg";

static char s_ssid[SSID_MAX + 1];
static char s_pw[PW_MAX + 1];
static char s_name[NAME_MAX_LEN + 1] = "robot-do";
static char s_color[8] = "#E0453A";
static volatile bool s_enabled = false;     // co cau hinh STA
static volatile bool s_connected = false;
static volatile bool s_ap_on = false;
static char s_ip[16];
static esp_timer_handle_t s_retry_timer = NULL;
static esp_timer_handle_t s_ap_timer = NULL;

// ---------------------------------------------------------------------------
// NVS
// ---------------------------------------------------------------------------
static void load_cfg(void)
{
    nvs_handle_t h;
    if (nvs_open("wifi", NVS_READONLY, &h) == ESP_OK) {
        size_t len = sizeof(s_ssid);
        if (nvs_get_str(h, "ssid", s_ssid, &len) != ESP_OK) {
            s_ssid[0] = '\0';
        }
        len = sizeof(s_pw);
        if (nvs_get_str(h, "pass", s_pw, &len) != ESP_OK) {
            s_pw[0] = '\0';
        }
        nvs_close(h);
    }
    s_enabled = s_ssid[0] != '\0';
    if (nvs_open("car", NVS_READONLY, &h) == ESP_OK) {
        char tmp[NAME_MAX_LEN + 1];
        size_t len = sizeof(tmp);
        if (nvs_get_str(h, "name", tmp, &len) == ESP_OK && tmp[0] != '\0') {
            snprintf(s_name, sizeof(s_name), "%s", tmp);
        }
        char col[8];
        len = sizeof(col);
        if (nvs_get_str(h, "color", col, &len) == ESP_OK && col[0] == '#') {
            snprintf(s_color, sizeof(s_color), "%s", col);
        }
        nvs_close(h);
    }
}

static bool save_wifi(const char *ssid, const char *pw)
{
    nvs_handle_t h;
    if (nvs_open("wifi", NVS_READWRITE, &h) != ESP_OK) {
        return false;
    }
    esp_err_t e = nvs_set_str(h, "ssid", ssid);
    if (e == ESP_OK) {
        e = nvs_set_str(h, "pass", pw);
    }
    if (e == ESP_OK) {
        e = nvs_commit(h);
    }
    nvs_close(h);
    return e == ESP_OK;
}

static bool wipe_wifi(void)
{
    nvs_handle_t h;
    if (nvs_open("wifi", NVS_READWRITE, &h) != ESP_OK) {
        return false;
    }
    esp_err_t e = nvs_erase_all(h);
    if (e == ESP_OK) {
        e = nvs_commit(h);
    }
    nvs_close(h);
    return e == ESP_OK;
}

static bool save_name(const char *name, const char *color)
{
    nvs_handle_t h;
    if (nvs_open("car", NVS_READWRITE, &h) != ESP_OK) {
        return false;
    }
    esp_err_t e = nvs_set_str(h, "name", name);
    if (e == ESP_OK) {
        e = nvs_set_str(h, "color", color);
    }
    if (e == ESP_OK) {
        e = nvs_commit(h);
    }
    nvs_close(h);
    return e == ESP_OK;
}

// ---------------------------------------------------------------------------
// Khoa OTA (NVS "ota"/"key") – khong bao gio in ra
// ---------------------------------------------------------------------------
static bool ota_key_load(char *out, size_t n)
{
    nvs_handle_t h;
    memset(out, 0, n);
    if (nvs_open("ota", NVS_READONLY, &h) != ESP_OK) {
        return false;
    }
    size_t len = n;
    esp_err_t e = nvs_get_str(h, "key", out, &len);
    nvs_close(h);
    if (e != ESP_OK) {
        memset(out, 0, n);
        return false;
    }
    return out[0] != '\0';
}

// So sanh khong ro ri thoi gian: chay du OTA_KEY_MAX ky tu
bool ota_key_check(const char *given)
{
    char k[OTA_KEY_MAX + 1];
    if (given == NULL || !ota_key_load(k, sizeof(k))) {
        memset(k, 0, sizeof(k));
        return false;
    }
    size_t gl = strlen(given);
    unsigned diff = (unsigned)(strlen(k) != gl);
    for (size_t i = 0; i < OTA_KEY_MAX; i++) {
        unsigned a = (unsigned char)k[i];
        unsigned b = i < gl ? (unsigned char)given[i] : 0;
        diff |= a ^ b;
    }
    memset(k, 0, sizeof(k));
    return diff == 0;
}

// ---------------------------------------------------------------------------
// Wi-Fi
// ---------------------------------------------------------------------------
static void sta_set_config(void)
{
    wifi_config_t wc;
    memset(&wc, 0, sizeof(wc));
    size_t sl = strlen(s_ssid);
    size_t pl = strlen(s_pw);
    memcpy(wc.sta.ssid, s_ssid, sl);
    memcpy(wc.sta.password, s_pw, pl);
    wc.sta.scan_method = WIFI_ALL_CHANNEL_SCAN;
    wc.sta.sort_method = WIFI_CONNECT_AP_BY_SIGNAL;
    wc.sta.threshold.authmode = pl > 0 ? WIFI_AUTH_WPA2_PSK : WIFI_AUTH_OPEN;
    wc.sta.pmf_cfg.capable = true;
    wc.sta.pmf_cfg.required = false;
    esp_err_t e = esp_wifi_set_config(WIFI_IF_STA, &wc);
    memset(&wc, 0, sizeof(wc));
    if (e != ESP_OK) {
        ESP_LOGE(TAG, "khong dat duoc cau hinh STA: %s", esp_err_to_name(e));
    }
}

static void start_ap(void)
{
    if (s_ap_on) {
        return;
    }
    wifi_config_t wc;
    memset(&wc, 0, sizeof(wc));
    size_t nl = strlen(s_name);
    memcpy(wc.ap.ssid, s_name, nl);
    wc.ap.ssid_len = (uint8_t)nl;
    wc.ap.channel = 1;
    wc.ap.max_connection = 4;
    wc.ap.authmode = WIFI_AUTH_OPEN;   // PROTOCOL muc 5: khong mat khau, de day khong can mang lab
    ESP_ERROR_CHECK(esp_wifi_set_mode(s_enabled ? WIFI_MODE_APSTA : WIFI_MODE_AP));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wc));
    s_ap_on = true;
    if (s_enabled) {
        sta_set_config();
        esp_wifi_connect();
    }
    ESP_LOGW(TAG, "che do diem phat: SSID=%s, http://192.168.4.1", s_name);
}

static void ap_timer_cb(void *arg)
{
    (void)arg;
    if (!s_connected) {
        start_ap();
    }
}

static void retry_cb(void *arg)
{
    (void)arg;
    if (s_enabled && !s_connected) {
        esp_wifi_connect();
    }
}

static void on_wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    (void)arg;
    (void)base;
    (void)data;
    if (id == WIFI_EVENT_STA_START) {
        if (s_enabled) {
            esp_wifi_connect();
        }
    } else if (id == WIFI_EVENT_STA_DISCONNECTED) {
        s_connected = false;
        s_ip[0] = '\0';
        if (s_enabled) {
            esp_timer_stop(s_retry_timer);
            esp_timer_start_once(s_retry_timer, RETRY_US);
        }
    }
}

static void on_ip_event(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    (void)arg;
    (void)base;
    if (id != IP_EVENT_STA_GOT_IP) {
        return;
    }
    const ip_event_got_ip_t *ev = (const ip_event_got_ip_t *)data;
    snprintf(s_ip, sizeof(s_ip), IPSTR, IP2STR(&ev->ip_info.ip));
    s_connected = true;
    esp_timer_stop(s_retry_timer);
    ESP_LOGI(TAG, "STA IP=%s - mo http://%s.local", s_ip, s_name);
}

// Ap dung cau hinh STA moi (lenh WIFI)
static void sta_apply(void)
{
    esp_timer_stop(s_retry_timer);
    wifi_mode_t mode = WIFI_MODE_NULL;
    esp_wifi_get_mode(&mode);
    if (mode == WIFI_MODE_AP) {
        esp_wifi_set_mode(WIFI_MODE_APSTA);
    }
    s_connected = false;
    s_ip[0] = '\0';
    sta_set_config();
    esp_wifi_disconnect();
    esp_wifi_connect();
    if (!s_ap_on) {
        esp_timer_stop(s_ap_timer);
        esp_timer_start_once(s_ap_timer, STA_WAIT_US);
    }
}

// ---------------------------------------------------------------------------
// Truy van
// ---------------------------------------------------------------------------
const char *netcfg_name(void)
{
    return s_name;
}

const char *netcfg_color(void)
{
    return s_color;
}

bool netcfg_sta_connected(void)
{
    return s_connected;
}

bool netcfg_ap_on(void)
{
    return s_ap_on;
}

void netcfg_ip(char *buf, size_t n)
{
    if (s_connected) {
        snprintf(buf, n, "%s", s_ip);
    } else if (s_ap_on) {
        snprintf(buf, n, "192.168.4.1");
    } else {
        snprintf(buf, n, "%s", "");
    }
}

eyes_status_t netcfg_eye_status(void)
{
    if (s_connected) {
        return EYES_ST_WIFI_OK;
    }
    return s_ap_on ? EYES_ST_AP : EYES_ST_CONNECTING;
}

// ---------------------------------------------------------------------------
// Lenh UART0
// ---------------------------------------------------------------------------
static void uart_reply(const char *s)
{
    uart_write_bytes(UART_PORT, s, strlen(s));
}

static void cmd_wifi_set(char *args)
{
    char *tab = strchr(args, '\t');
    if (tab == NULL) {
        uart_reply("WIFI ERR dinh dang: WIFI <ssid><TAB><mat khau>\r\n");
        return;
    }
    *tab = '\0';
    const char *ssid = args;
    const char *pw = tab + 1;
    size_t sl = strlen(ssid);
    size_t pl = strlen(pw);
    if (sl < 1 || sl > SSID_MAX || pl > PW_MAX) {
        uart_reply("WIFI ERR SSID/mat khau qua dai\r\n");
        return;
    }
    if (!save_wifi(ssid, pw)) {
        uart_reply("WIFI ERR khong luu duoc NVS\r\n");
        return;
    }
    snprintf(s_ssid, sizeof(s_ssid), "%s", ssid);
    snprintf(s_pw, sizeof(s_pw), "%s", pw);
    s_enabled = true;
    sta_apply();
    uart_reply("WIFI OK\r\n");
}

static void cmd_wifi_status(void)
{
    char line[120];
    snprintf(line, sizeof(line), "WIFI ssid=%s connected=%d ap=%d ip=%s\r\n", s_ssid, s_connected ? 1 : 0,
             s_ap_on ? 1 : 0, s_ip);
    uart_reply(line);
}

static void cmd_wifi_clear(void)
{
    if (!wipe_wifi()) {
        uart_reply("WIFI ERR\r\n");
        return;
    }
    s_enabled = false;
    memset(s_ssid, 0, sizeof(s_ssid));
    memset(s_pw, 0, sizeof(s_pw));
    esp_wifi_disconnect();
    start_ap();
    uart_reply("WIFI_CLEAR OK\r\n");
}

static void cmd_otakey_set(const char *k)
{
    size_t n = strlen(k);
    bool ok = n >= OTA_KEY_MIN && n <= OTA_KEY_MAX;
    for (size_t i = 0; ok && i < n; i++) {
        ok = (unsigned char)k[i] > 0x20 && (unsigned char)k[i] < 0x7F;
    }
    if (!ok) {
        uart_reply("OTAKEY ERR\r\n");
        return;
    }
    nvs_handle_t h;
    esp_err_t e = nvs_open("ota", NVS_READWRITE, &h);
    if (e == ESP_OK) {
        e = nvs_set_str(h, "key", k);
        if (e == ESP_OK) {
            e = nvs_commit(h);
        }
        nvs_close(h);
    }
    uart_reply(e == ESP_OK ? "OTAKEY OK\r\n" : "OTAKEY ERR\r\n");
}

static bool name_ok(const char *s)
{
    size_t n = strlen(s);
    if (n < 1 || n > NAME_MAX_LEN) {
        return false;
    }
    for (size_t i = 0; i < n; i++) {
        char c = s[i];
        bool ok = (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-';
        if (!ok) {
            return false;
        }
    }
    return true;
}

static bool color_ok(const char *s)
{
    if (strlen(s) != 7 || s[0] != '#') {
        return false;
    }
    for (int i = 1; i < 7; i++) {
        char c = s[i];
        bool ok = (c >= '0' && c <= '9') || (c >= 'A' && c <= 'F') || (c >= 'a' && c <= 'f');
        if (!ok) {
            return false;
        }
    }
    return true;
}

// NAME <ten> <#mau>
static void cmd_name(char *args)
{
    char *sp = strchr(args, ' ');
    if (sp == NULL) {
        uart_reply("NAME ERR dinh dang: NAME <ten> <#RRGGBB>\r\n");
        return;
    }
    *sp = '\0';
    const char *name = args;
    const char *color = sp + 1;
    if (!name_ok(name) || !color_ok(color)) {
        uart_reply("NAME ERR ten a-z 0-9 - (toi da 24), mau #RRGGBB\r\n");
        return;
    }
    if (!save_name(name, color)) {
        uart_reply("NAME ERR khong luu duoc NVS\r\n");
        return;
    }
    uart_reply("NAME OK - khoi dong lai\r\n");
    vTaskDelay(pdMS_TO_TICKS(300));
    esp_restart();
}

static void handle_line(char *line)
{
    if (strcmp(line, "WIFI?") == 0) {
        cmd_wifi_status();
    } else if (strcmp(line, "WIFI_CLEAR") == 0) {
        cmd_wifi_clear();
    } else if (strncmp(line, "WIFI ", 5) == 0) {
        cmd_wifi_set(line + 5);
    } else if (strcmp(line, "OTAKEY?") == 0) {
        char k[OTA_KEY_MAX + 1];
        bool set = ota_key_load(k, sizeof(k));
        memset(k, 0, sizeof(k));
        uart_reply(set ? "OTAKEY SET\r\n" : "OTAKEY NONE\r\n");
    } else if (strncmp(line, "OTAKEY ", 7) == 0) {
        cmd_otakey_set(line + 7);
    } else if (strncmp(line, "NAME ", 5) == 0) {
        cmd_name(line + 5);
    }
}

static void uart_cmd_task(void *arg)
{
    (void)arg;
    static char line[LINE_MAX_LEN];
    size_t len = 0;
    bool overflow = false;
    uint8_t c;
    while (true) {
        int r = uart_read_bytes(UART_PORT, &c, 1, pdMS_TO_TICKS(200));
        if (r != 1 || c == '\r') {
            continue;
        }
        if (c != '\n') {
            if (len < sizeof(line) - 1) {
                line[len++] = (char)c;
            } else {
                overflow = true;
            }
            continue;
        }
        line[len] = '\0';
        if (overflow) {
            uart_reply("ERR dong qua dai\r\n");
        } else {
            handle_line(line);
        }
        memset(line, 0, sizeof(line));
        len = 0;
        overflow = false;
    }
}

// ---------------------------------------------------------------------------
// Khoi dong
// ---------------------------------------------------------------------------
void netcfg_start(void)
{
    load_cfg();

    const esp_timer_create_args_t ra = {.callback = retry_cb, .arg = NULL, .dispatch_method = ESP_TIMER_TASK, .name = "sta_retry"};
    ESP_ERROR_CHECK(esp_timer_create(&ra, &s_retry_timer));
    const esp_timer_create_args_t aa = {.callback = ap_timer_cb, .arg = NULL, .dispatch_method = ESP_TIMER_TASK, .name = "ap_wait"};
    ESP_ERROR_CHECK(esp_timer_create(&aa, &s_ap_timer));

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_t *sta = esp_netif_create_default_wifi_sta();
    esp_netif_create_default_wifi_ap();
    esp_netif_set_hostname(sta, s_name);
    wifi_init_config_t ic = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&ic));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_ip_event, NULL));

    if (!uart_is_driver_installed(UART_PORT)) {
        ESP_ERROR_CHECK(uart_driver_install(UART_PORT, 1024, 0, 0, NULL, 0));
    }
    xTaskCreate(uart_cmd_task, "uart_cmd", 4096, NULL, 4, NULL);

    if (s_enabled) {
        ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
        sta_set_config();
        ESP_ERROR_CHECK(esp_wifi_start());
        esp_timer_start_once(s_ap_timer, STA_WAIT_US);
        ESP_LOGI(TAG, "dang noi Wi-Fi da luu: %s (toi da 20 s roi bat AP)", s_ssid);
    } else {
        ESP_ERROR_CHECK(esp_wifi_start());
        start_ap();
        ESP_LOGW(TAG, "chua cai Wi-Fi - chay wifi-setup.py hoac dung AP %s", s_name);
    }

    ESP_ERROR_CHECK(mdns_init());
    ESP_ERROR_CHECK(mdns_hostname_set(s_name));
    ESP_ERROR_CHECK(mdns_instance_name_set("STLab block-coding-car"));
    ESP_ERROR_CHECK(mdns_service_add(NULL, "_http", "_tcp", 80, NULL, 0));
}
