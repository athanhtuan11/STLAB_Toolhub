// Wi-Fi nha (STA) cho firmware do. Cau hinh luu NVS namespace "wifi_nha" (khoa "ssid", "pass").
// Lenh UART0 (dong ket thuc xuong dong):
//   WIFI <ssid>TAB<mat khau>   luu + ket noi
//   WIFI?                      xem trang thai
//   WIFI_CLEAR                 xoa cau hinh, ngat STA
//   OTAKEY <khoa>              luu khoa OTA (16-64 ky tu in duoc) vao NVS namespace "ota", tra "OTAKEY OK"
//   OTAKEY?                    tra "OTAKEY SET" hoac "OTAKEY NONE"
// Mat khau va khoa OTA khong bao gio duoc in ra log/UART.

#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <inttypes.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

#include "esp_log.h"
#include "esp_err.h"
#include "esp_timer.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "nvs.h"
#include "driver/uart.h"
#include "mdns.h"

#include "wifi_nha.h"

#define NVS_NS        "wifi_nha"
#define SSID_MAX      32
#define PW_MAX        63
#define RETRY_US      (10 * 1000000LL)
#define LINE_MAX_LEN  192
#define UART_PORT     UART_NUM_0

static const char *TAG = "wifi_nha";

static SemaphoreHandle_t s_mutex = NULL;
static esp_timer_handle_t s_retry_timer = NULL;
static esp_netif_t *s_sta_netif = NULL;

// Trang thai dung chung (bao ve bang s_mutex)
static char s_ssid[SSID_MAX + 1];
static char s_pw[PW_MAX + 1];
static bool s_enabled = false;      // co cau hinh va dang muon ket noi
static bool s_connected = false;    // da co IP
static bool s_intentional = false;  // ngat chu dong, bo qua mot su kien DISCONNECTED
static char s_ip[16];

static void lock(void)
{
    xSemaphoreTake(s_mutex, portMAX_DELAY);
}

static void unlock(void)
{
    xSemaphoreGive(s_mutex);
}

// ---------------------------------------------------------------------------
// NVS
// ---------------------------------------------------------------------------
static void nvs_report(const char *what, esp_err_t err)
{
    ESP_LOGE(TAG, "[DO] Loi luu NVS: %s (%s)", esp_err_to_name(err), what);
}

static bool nvs_save(const char *ssid, const char *pw)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open("wifi_nha", NVS_READWRITE, &h);
    if (err != ESP_OK) {
        nvs_report("open", err);
        return false;
    }
    err = nvs_set_str(h, "ssid", ssid);
    if (err == ESP_OK) {
        err = nvs_set_str(h, "pass", pw);
    }
    if (err == ESP_OK) {
        err = nvs_commit(h);
    }
    nvs_close(h);
    if (err != ESP_OK) {
        nvs_report("set/commit", err);
        return false;
    }
    return true;
}

static bool nvs_wipe(void)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open("wifi_nha", NVS_READWRITE, &h);
    if (err != ESP_OK) {
        nvs_report("open", err);
        return false;
    }
    err = nvs_erase_all(h);
    if (err == ESP_OK) {
        err = nvs_commit(h);
    }
    nvs_close(h);
    if (err != ESP_OK) {
        nvs_report("erase/commit", err);
        return false;
    }
    return true;
}

// Doc cau hinh vao s_ssid/s_pw; tra true neu co SSID.
static bool nvs_load(void)
{
    nvs_handle_t h;
    s_ssid[0] = '\0';
    s_pw[0] = '\0';
    if (nvs_open(NVS_NS, NVS_READONLY, &h) != ESP_OK) {
        return false;
    }
    size_t len = sizeof(s_ssid);
    if (nvs_get_str(h, "ssid", s_ssid, &len) != ESP_OK) {
        s_ssid[0] = '\0';
    }
    len = sizeof(s_pw);
    if (nvs_get_str(h, "pass", s_pw, &len) != ESP_OK) {
        s_pw[0] = '\0';
    }
    nvs_close(h);
    return s_ssid[0] != '\0';
}

// ---------------------------------------------------------------------------
// STA
// ---------------------------------------------------------------------------
// Dat cau hinh STA tu s_ssid/s_pw (goi khi dang giu lock hoac truoc khi co task khac).
static esp_err_t sta_set_config_locked(void)
{
    wifi_config_t wc;
    memset(&wc, 0, sizeof(wc));
    size_t sl = strlen(s_ssid);
    size_t pl = strlen(s_pw);
    memcpy(wc.sta.ssid, s_ssid, sl);
    memcpy(wc.sta.password, s_pw, pl);
    wc.sta.scan_method = WIFI_ALL_CHANNEL_SCAN;
    wc.sta.sort_method = WIFI_CONNECT_AP_BY_SIGNAL;
    wc.sta.threshold.authmode = (pl > 0) ? WIFI_AUTH_WPA2_PSK : WIFI_AUTH_OPEN;
    wc.sta.pmf_cfg.capable = true;
    wc.sta.pmf_cfg.required = false;
    esp_err_t err = esp_wifi_set_config(WIFI_IF_STA, &wc);
    memset(&wc, 0, sizeof(wc));
    return err;
}

static void retry_timer_cb(void *arg)
{
    (void)arg;
    lock();
    bool want = s_enabled && !s_connected;
    unlock();
    if (want) {
        esp_err_t err = esp_wifi_connect();
        if (err != ESP_OK) {
            ESP_LOGW(TAG, "[DO] esp_wifi_connect: %s", esp_err_to_name(err));
        }
    }
}

static void schedule_retry(void)
{
    esp_timer_stop(s_retry_timer);
    esp_timer_start_once(s_retry_timer, RETRY_US);
}

static void on_wifi_event(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    (void)arg;
    (void)base;
    if (id == WIFI_EVENT_STA_START) {
        lock();
        bool want = s_enabled;
        unlock();
        if (want) {
            esp_wifi_connect();
        }
    } else if (id == WIFI_EVENT_STA_DISCONNECTED) {
        const wifi_event_sta_disconnected_t *ev = (const wifi_event_sta_disconnected_t *)data;
        lock();
        s_connected = false;
        s_ip[0] = '\0';
        bool skip = s_intentional;
        s_intentional = false;
        bool want = s_enabled;
        unlock();
        if (skip || !want) {
            return;
        }
        ESP_LOGW(TAG, "[DO] STA chua ket noi duoc (ly do %d) - thu lai sau 10 s",
                 ev != NULL ? (int)ev->reason : -1);
        schedule_retry();
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
    char ip[16];
    snprintf(ip, sizeof(ip), IPSTR, IP2STR(&ev->ip_info.ip));
    lock();
    s_connected = true;
    snprintf(s_ip, sizeof(s_ip), "%s", ip);
    unlock();
    esp_timer_stop(s_retry_timer);

    wifi_ap_record_t ap;
    int rssi = 0;
    if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK) {
        rssi = ap.rssi;
    }
    ESP_LOGI(TAG, "[DO] STA IP=%s – mo http://stlab-cam.local hoac http://%s (RSSI %d dBm)",
             ip, ip, rssi);
}

// Ap dung cau hinh moi: ngat chu dong roi ket noi lai.
static void sta_reconnect(void)
{
    esp_timer_stop(s_retry_timer);
    lock();
    s_intentional = s_connected;
    s_connected = false;
    s_ip[0] = '\0';
    s_enabled = true;
    esp_err_t err = sta_set_config_locked();
    unlock();
    esp_wifi_disconnect();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "[DO] Loi: khong dat duoc cau hinh STA: %s", esp_err_to_name(err));
        return;
    }
    err = esp_wifi_connect();
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "[DO] esp_wifi_connect: %s", esp_err_to_name(err));
        schedule_retry();
    }
}

static void sta_clear(void)
{
    esp_timer_stop(s_retry_timer);
    lock();
    s_enabled = false;
    s_intentional = false;
    s_connected = false;
    s_ip[0] = '\0';
    memset(s_ssid, 0, sizeof(s_ssid));
    memset(s_pw, 0, sizeof(s_pw));
    unlock();
    esp_wifi_disconnect();
}

// ---------------------------------------------------------------------------
// Trang thai
// ---------------------------------------------------------------------------
static int sta_rssi_now(bool connected)
{
    wifi_ap_record_t ap;
    if (connected && esp_wifi_sta_get_ap_info(&ap) == ESP_OK) {
        return ap.rssi;
    }
    return 0;
}

static void json_escape(char *dst, size_t n, const char *src)
{
    size_t o = 0;
    for (; *src != '\0' && o + 7 < n; src++) {
        unsigned char c = (unsigned char)*src;
        if (c == '"' || c == '\\') {
            dst[o++] = '\\';
            dst[o++] = (char)c;
        } else if (c < 0x20) {
            o += (size_t)snprintf(dst + o, n - o, "\\u%04x", c);
        } else {
            dst[o++] = (char)c;
        }
    }
    dst[o] = '\0';
}

bool wifi_nha_sta_connected(void)
{
    lock();
    bool c = s_connected;
    unlock();
    return c;
}

bool wifi_nha_configured(void)
{
    lock();
    bool e = s_enabled;
    unlock();
    return e;
}

void wifi_nha_status_json(char *buf, size_t n)
{
    char ssid[SSID_MAX + 1];
    char ip[16];
    lock();
    snprintf(ssid, sizeof(ssid), "%s", s_ssid);
    snprintf(ip, sizeof(ip), "%s", s_ip);
    bool connected = s_connected;
    unlock();

    char esc[SSID_MAX * 6 + 1];
    json_escape(esc, sizeof(esc), ssid);
    snprintf(buf, n,
             "\"sta_ssid\":\"%s\",\"sta_ip\":\"%s\",\"sta_rssi\":%d,"
             "\"sta_connected\":%s,\"mdns\":\"stlab-cam.local\"",
             esc, ip, sta_rssi_now(connected), connected ? "true" : "false");
}

static void print_status(void)
{
    char ssid[SSID_MAX + 1];
    char ip[16];
    lock();
    snprintf(ssid, sizeof(ssid), "%s", s_ssid);
    snprintf(ip, sizeof(ip), "%s", s_ip);
    bool connected = s_connected;
    unlock();
    ESP_LOGI(TAG, "[DO] WIFI ssid=%s connected=%d ip=%s rssi=%d",
             ssid, connected ? 1 : 0, ip, sta_rssi_now(connected));
}

// ---------------------------------------------------------------------------
// Khoa OTA (NVS namespace "ota", khoa "key"). Khong bao gio in ra.
// ---------------------------------------------------------------------------
#define OTA_KEY_MIN 16
#define OTA_KEY_MAX 64

static bool ota_key_load(char *out, size_t n)
{
    nvs_handle_t h;
    out[0] = '\0';
    if (nvs_open("ota", NVS_READONLY, &h) != ESP_OK) {
        return false;
    }
    memset(out, 0, n);
    size_t len = n;
    esp_err_t err = nvs_get_str(h, "key", out, &len);
    nvs_close(h);
    if (err != ESP_OK) {
        out[0] = '\0';
        return false;
    }
    return out[0] != '\0';
}

bool ota_key_is_set(void)
{
    char k[OTA_KEY_MAX + 1];
    bool r = ota_key_load(k, sizeof(k));
    memset(k, 0, sizeof(k));
    return r;
}

// So sanh thoi gian hang so (chay het do dai toi da).
bool ota_key_check(const char *given)
{
    char k[OTA_KEY_MAX + 1] = {0};
    if (given == NULL || !ota_key_load(k, sizeof(k))) {
        memset(k, 0, sizeof(k));
        return false;
    }
    unsigned diff = (unsigned)(strlen(k) != strlen(given));
    for (size_t i = 0; i < OTA_KEY_MAX; i++) {
        unsigned a = (unsigned char)k[i];
        unsigned b = (i < strlen(given) && i <= OTA_KEY_MAX) ? (unsigned char)given[i] : 0;
        diff |= a ^ b;
    }
    memset(k, 0, sizeof(k));
    return diff == 0;
}

static void uart_reply(const char *s)
{
    uart_write_bytes(UART_PORT, s, strlen(s));
}

static void handle_ota_set(const char *k)
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
    esp_err_t err = nvs_open("ota", NVS_READWRITE, &h);
    if (err == ESP_OK) {
        err = nvs_set_str(h, "key", k);
        if (err == ESP_OK) {
            err = nvs_commit(h);
        }
        nvs_close(h);
    }
    uart_reply(err == ESP_OK ? "OTAKEY OK\r\n" : "OTAKEY ERR\r\n");
}

// ---------------------------------------------------------------------------
// Lenh UART0
// ---------------------------------------------------------------------------
static void handle_set(char *args)
{
    char *tab = strchr(args, '\t');
    if (tab == NULL) {
        ESP_LOGE(TAG, "[DO] Loi: dinh dang WIFI <ssid><TAB><mat khau>");
        return;
    }
    *tab = '\0';
    const char *ssid = args;
    const char *pw = tab + 1;
    size_t sl = strlen(ssid);
    size_t pl = strlen(pw);
    if (sl < 1 || sl > SSID_MAX || pl > PW_MAX) {
        ESP_LOGE(TAG, "[DO] Loi: SSID/mat khau qua dai");
        return;
    }
    if (!nvs_save(ssid, pw)) {
        return;
    }
    lock();
    snprintf(s_ssid, sizeof(s_ssid), "%s", ssid);
    snprintf(s_pw, sizeof(s_pw), "%s", pw);
    unlock();
    ESP_LOGI(TAG, "[DO] Da luu Wi-Fi nha: %s", ssid);
    sta_reconnect();
}

static void handle_line(char *line)
{
    if (strcmp(line, "WIFI?") == 0) {
        print_status();
    } else if (strcmp(line, "WIFI_CLEAR") == 0) {
        if (nvs_wipe()) {
            sta_clear();
            ESP_LOGI(TAG, "[DO] Da xoa Wi-Fi nha");
        }
    } else if (strncmp(line, "WIFI ", 5) == 0) {
        handle_set(line + 5);
    } else if (strcmp(line, "OTAKEY?") == 0) {
        uart_reply(ota_key_is_set() ? "OTAKEY SET\r\n" : "OTAKEY NONE\r\n");
    } else if (strncmp(line, "OTAKEY ", 7) == 0) {
        handle_ota_set(line + 7);
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
            if (strncmp(line, "WIFI", 4) == 0) {
                ESP_LOGE(TAG, "[DO] Loi: SSID/mat khau qua dai");
            } else if (strncmp(line, "OTAKEY", 6) == 0) {
                uart_reply("OTAKEY ERR\r\n");
            }
        } else {
            handle_line(line);
        }
        memset(line, 0, sizeof(line));
        len = 0;
        overflow = false;
    }
}

// ---------------------------------------------------------------------------
// Khoi tao
// ---------------------------------------------------------------------------
void wifi_nha_init(void)
{
    s_mutex = xSemaphoreCreateMutex();
    const esp_timer_create_args_t targs = {
        .callback = retry_timer_cb,
        .arg = NULL,
        .dispatch_method = ESP_TIMER_TASK,
        .name = "wifi_nha_retry",
    };
    ESP_ERROR_CHECK(esp_timer_create(&targs, &s_retry_timer));

    s_sta_netif = esp_netif_create_default_wifi_sta();
    esp_netif_set_hostname(s_sta_netif, "stlab-cam");

    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, on_wifi_event, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_ip_event, NULL));

    bool has = nvs_load();
    char ssid[SSID_MAX + 1];
    lock();
    s_enabled = has;
    if (has) {
        esp_err_t err = sta_set_config_locked();
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "[DO] Loi: khong dat duoc cau hinh STA: %s", esp_err_to_name(err));
            s_enabled = false;
        }
    }
    bool ok = s_enabled;
    snprintf(ssid, sizeof(ssid), "%s", s_ssid);
    unlock();
    if (!ok) {
        ESP_LOGW(TAG, "[DO] Chua cai Wi-Fi nha – chay wifi-setup.py");
    } else {
        ESP_LOGI(TAG, "[DO] Wi-Fi nha da luu: %s - dang ket noi", ssid);
    }
}

void wifi_nha_start(void)
{
    ESP_ERROR_CHECK(mdns_init());
    ESP_ERROR_CHECK(mdns_hostname_set("stlab-cam"));
    ESP_ERROR_CHECK(mdns_instance_name_set("STLab ESP32-S3-CAM"));
    ESP_ERROR_CHECK(mdns_service_add(NULL, "_http", "_tcp", 80, NULL, 0));

    if (!uart_is_driver_installed(UART_PORT)) {
        esp_err_t err = uart_driver_install(UART_PORT, 1024, 0, 0, NULL, 0);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "[DO] Loi: khong cai duoc driver UART0: %s", esp_err_to_name(err));
            return;
        }
    }
    xTaskCreate(uart_cmd_task, "wifi_cmd", 4096, NULL, 4, NULL);
}
