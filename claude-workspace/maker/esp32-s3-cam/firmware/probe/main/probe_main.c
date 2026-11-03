// Firmware do phan cung ESP32-S3-CAM N16R8 + OV3660.
// - In thong tin chip/flash/PSRAM/MAC ra UART0 (moi dong bat dau bang [DO]).
// - Thu tung bo chan camera (XCLK 20 MHz roi 10 MHz), doc PID cam bien, chup thu 5 khung.
// - That bai het: quet I2C (SCCB) tren SIOD/SIOC de tim dia chi cam bien.
// - Luon bat Wi-Fi SoftAP + HTTP server de xem hinh / bao loi.
// Khong ghi mat khau co dinh: SSID/mat khau sinh tu MAC luc chay.

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "esp_log.h"
#include "esp_system.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_psram.h"
#include "esp_mac.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "esp_http_server.h"

#include "wifi_nha.h"

#include "driver/i2c.h"
#include "driver/temperature_sensor.h"

#include "esp_camera.h"

extern const uint8_t index_html_start[] asm("_binary_index_html_start");
extern const uint8_t index_html_end[] asm("_binary_index_html_end");

static const char *TAG = "probe";

// ---------------------------------------------------------------------------
// Bang bo chan camera. Moi bo la mot dong trong mang; them bo moi khi co nguon.
// ---------------------------------------------------------------------------
typedef struct {
    const char *name;
    int xclk, siod, sioc;
    int d0, d1, d2, d3, d4, d5, d6, d7;
    int vsync, href, pclk;
    int pwdn, reset;
} cam_pin_set_t;

static const cam_pin_set_t s_pin_sets[] = {
    {
        .name = "FREENOVE_GOOUUU",
        .xclk = 15, .siod = 4, .sioc = 5,
        .d0 = 11, .d1 = 9, .d2 = 8, .d3 = 10,
        .d4 = 12, .d5 = 18, .d6 = 17, .d7 = 16,
        .vsync = 6, .href = 7, .pclk = 13,
        .pwdn = -1, .reset = -1,
    },
    // TODO: them bo chan moi o day khi co nguon xac nhan (khong tu doan chan).
    // Dinh dang moi dong giong bo FREENOVE_GOOUUU o tren (name, xclk, siod, sioc, d0..d7, vsync, href, pclk, pwdn, reset).
};
#define PIN_SET_COUNT (sizeof(s_pin_sets) / sizeof(s_pin_sets[0]))

typedef struct {
    const char *name;
    framesize_t fs;
} fs_item_t;

static const fs_item_t s_fs_items[] = {
    {"QVGA", FRAMESIZE_QVGA},
    {"VGA",  FRAMESIZE_VGA},
    {"SVGA", FRAMESIZE_SVGA},
    {"XGA",  FRAMESIZE_XGA},
    {"UXGA", FRAMESIZE_UXGA},
    {"QXGA", FRAMESIZE_QXGA},
};
#define FS_COUNT (sizeof(s_fs_items) / sizeof(s_fs_items[0]))

typedef struct {
    bool cam_ok;
    char bo_chan[32];
    int xclk_mhz;
    int pid;
    char ten_cam_bien[24];
    framesize_t framesize;
    int quality;
    char loi[96];
    char chip[16];
    volatile uint32_t frame_count;
    volatile float fps;
    int64_t boot_us;
} probe_state_t;

static probe_state_t g;
static sensor_t *g_sensor = NULL;
static temperature_sensor_handle_t g_tsens = NULL;
static char g_ssid[32];
static char g_pass[16];

#define STREAM_BOUNDARY "stlabboundary"

// ---------------------------------------------------------------------------
// Tien ich
// ---------------------------------------------------------------------------
static const char *chip_model_name(esp_chip_model_t model)
{
    switch (model) {
    case CHIP_ESP32:    return "ESP32";
    case CHIP_ESP32S2:  return "ESP32-S2";
    case CHIP_ESP32S3:  return "ESP32-S3";
    case CHIP_ESP32C2:  return "ESP32-C2";
    case CHIP_ESP32C3:  return "ESP32-C3";
    case CHIP_ESP32C6:  return "ESP32-C6";
    case CHIP_ESP32H2:  return "ESP32-H2";
    case CHIP_ESP32P4:  return "ESP32-P4";
    default:            return "KHONG_RO";
    }
}

static const char *fs_name(framesize_t fs)
{
    for (size_t i = 0; i < FS_COUNT; i++) {
        if (s_fs_items[i].fs == fs) {
            return s_fs_items[i].name;
        }
    }
    return "KHAC";
}

static bool fs_parse(const char *s, framesize_t *out)
{
    for (size_t i = 0; i < FS_COUNT; i++) {
        if (strcmp(s, s_fs_items[i].name) == 0) {
            *out = s_fs_items[i].fs;
            return true;
        }
    }
    return false;
}

static void pid_name(int pid, char *out, size_t n)
{
    switch (pid) {
    case 0x3660: snprintf(out, n, "OV3660"); break;
    case 0x26:   snprintf(out, n, "OV2640"); break;
    case 0x5640: snprintf(out, n, "OV5640"); break;
    default:     snprintf(out, n, "KHONG_RO"); break;
    }
}

static float chip_temperature(void)
{
    float t = -999.0f;
    if (g_tsens != NULL) {
        if (temperature_sensor_get_celsius(g_tsens, &t) != ESP_OK) {
            t = -999.0f;
        }
    }
    return t;
}

// ---------------------------------------------------------------------------
// Thong tin chip
// ---------------------------------------------------------------------------
static void print_board_info(void)
{
    esp_chip_info_t ci;
    esp_chip_info(&ci);
    snprintf(g.chip, sizeof(g.chip), "%s", chip_model_name(ci.model));

    uint32_t flash_size = 0;
    esp_flash_get_size(NULL, &flash_size);
    size_t psram_size = esp_psram_get_size();

    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_STA);

    ESP_LOGI(TAG, "[DO] Chip: %s, so loi: %d, revision: %d", g.chip, ci.cores, ci.revision);
    ESP_LOGI(TAG, "[DO] Flash: %" PRIu32 " byte (%" PRIu32 " MB)", flash_size, flash_size / (1024U * 1024U));
    ESP_LOGI(TAG, "[DO] PSRAM: %u byte (%u MB)", (unsigned)psram_size, (unsigned)(psram_size / (1024U * 1024U)));
    ESP_LOGI(TAG, "[DO] MAC STA: %02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// ---------------------------------------------------------------------------
// Thu mot bo chan voi mot tan so XCLK
// ---------------------------------------------------------------------------
static bool camera_try(const cam_pin_set_t *ps, int xclk_mhz)
{
    camera_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.ledc_channel = LEDC_CHANNEL_0;
    cfg.ledc_timer = LEDC_TIMER_0;
    cfg.pin_pwdn = ps->pwdn;
    cfg.pin_reset = ps->reset;
    cfg.pin_xclk = ps->xclk;
    cfg.pin_sccb_sda = ps->siod;
    cfg.pin_sccb_scl = ps->sioc;
    cfg.pin_d0 = ps->d0;
    cfg.pin_d1 = ps->d1;
    cfg.pin_d2 = ps->d2;
    cfg.pin_d3 = ps->d3;
    cfg.pin_d4 = ps->d4;
    cfg.pin_d5 = ps->d5;
    cfg.pin_d6 = ps->d6;
    cfg.pin_d7 = ps->d7;
    cfg.pin_vsync = ps->vsync;
    cfg.pin_href = ps->href;
    cfg.pin_pclk = ps->pclk;
    cfg.xclk_freq_hz = xclk_mhz * 1000000;
    cfg.pixel_format = PIXFORMAT_JPEG;
    cfg.frame_size = FRAMESIZE_SVGA;
    cfg.jpeg_quality = 12;
    cfg.fb_count = 2;
    cfg.fb_location = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode = CAMERA_GRAB_LATEST;

    ESP_LOGI(TAG, "[DO] Thu bo chan %s, XCLK %d MHz", ps->name, xclk_mhz);

    esp_err_t err = esp_camera_init(&cfg);
    if (err != ESP_OK) {
        snprintf(g.loi, sizeof(g.loi), "esp_camera_init loi 0x%x", err);
        ESP_LOGW(TAG, "[DO]   that bai: %s", g.loi);
        return false;
    }

    sensor_t *s = esp_camera_sensor_get();
    int pid = (s != NULL) ? s->id.PID : 0;
    char nm[24];
    pid_name(pid, nm, sizeof(nm));

    ESP_LOGI(TAG, "[DO]   OK: bo chan %s, XCLK %d MHz, PID=0x%04X (%s)",
             ps->name, xclk_mhz, pid, nm);

    g_sensor = s;
    g.pid = pid;
    snprintf(g.ten_cam_bien, sizeof(g.ten_cam_bien), "%s", nm);
    snprintf(g.bo_chan, sizeof(g.bo_chan), "%s", ps->name);
    g.xclk_mhz = xclk_mhz;
    g.framesize = FRAMESIZE_SVGA;
    g.quality = 12;
    g.cam_ok = true;
    g.loi[0] = '\0';

    for (int i = 0; i < 5; i++) {
        int64_t t0 = esp_timer_get_time();
        camera_fb_t *fb = esp_camera_fb_get();
        int64_t dt_ms = (esp_timer_get_time() - t0) / 1000;
        if (fb != NULL) {
            ESP_LOGI(TAG, "[DO]   khung %d: %u byte, %" PRId64 " ms",
                     i + 1, (unsigned)fb->len, dt_ms);
            esp_camera_fb_return(fb);
        } else {
            ESP_LOGW(TAG, "[DO]   khung %d: KHONG lay duoc", i + 1);
        }
    }
    return true;
}

// ---------------------------------------------------------------------------
// Quet I2C (SCCB) tren chan SIOD/SIOC cua mot bo chan
// ---------------------------------------------------------------------------
static void i2c_scan_set(const cam_pin_set_t *ps)
{
    if (ps->siod < 0 || ps->sioc < 0) {
        return;
    }

    i2c_config_t conf;
    memset(&conf, 0, sizeof(conf));
    conf.mode = I2C_MODE_MASTER;
    conf.sda_io_num = ps->siod;
    conf.scl_io_num = ps->sioc;
    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
    conf.master.clk_speed = 100000;

    if (i2c_param_config(I2C_NUM_0, &conf) != ESP_OK) {
        ESP_LOGW(TAG, "[DO] I2C %s: khong cau hinh duoc chan", ps->name);
        return;
    }
    if (i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0) != ESP_OK) {
        ESP_LOGW(TAG, "[DO] I2C %s: khong cai duoc driver", ps->name);
        return;
    }

    ESP_LOGI(TAG, "[DO] Quet I2C tren %s (SDA=%d, SCL=%d); OV3660 thuong o 0x3C (chua chac)",
             ps->name, ps->siod, ps->sioc);

    int found = 0;
    for (int addr = 1; addr < 128; addr++) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (addr << 1) | I2C_MASTER_WRITE, true);
        i2c_master_stop(cmd);
        esp_err_t r = i2c_master_cmd_begin(I2C_NUM_0, cmd, pdMS_TO_TICKS(50));
        i2c_cmd_link_delete(cmd);
        if (r == ESP_OK) {
            found++;
            ESP_LOGI(TAG, "[DO]   I2C %s: thiet bi tra loi 0x%02X", ps->name, addr);
        }
    }
    if (found == 0) {
        ESP_LOGW(TAG, "[DO]   I2C %s: khong co thiet bi nao tra loi", ps->name);
    }

    i2c_driver_delete(I2C_NUM_0);
}

static void camera_probe_all(void)
{
    for (size_t i = 0; i < PIN_SET_COUNT; i++) {
        const int xclks[2] = {20, 10};
        for (int k = 0; k < 2; k++) {
            if (camera_try(&s_pin_sets[i], xclks[k])) {
                return;
            }
            esp_camera_deinit();
        }
    }

    g.cam_ok = false;
    g_sensor = NULL;
    g.pid = 0;
    snprintf(g.bo_chan, sizeof(g.bo_chan), "khong co");
    snprintf(g.ten_cam_bien, sizeof(g.ten_cam_bien), "KHONG_RO");
    snprintf(g.loi, sizeof(g.loi), "tat ca bo chan deu khoi tao that bai");
    ESP_LOGE(TAG, "[DO] Tat ca bo chan deu that bai - chuyen sang quet I2C");

    for (size_t i = 0; i < PIN_SET_COUNT; i++) {
        i2c_scan_set(&s_pin_sets[i]);
    }
}

// ---------------------------------------------------------------------------
// Nhiet do chip
// ---------------------------------------------------------------------------
static void tsens_init(void)
{
    temperature_sensor_config_t cfg = TEMPERATURE_SENSOR_CONFIG_DEFAULT(-10, 80);
    if (temperature_sensor_install(&cfg, &g_tsens) != ESP_OK) {
        g_tsens = NULL;
        ESP_LOGW(TAG, "[DO] Khong cai duoc temperature_sensor");
        return;
    }
    if (temperature_sensor_enable(g_tsens) != ESP_OK) {
        ESP_LOGW(TAG, "[DO] Khong bat duoc temperature_sensor");
    }
}

// ---------------------------------------------------------------------------
// Wi-Fi SoftAP: SSID/mat khau sinh tu MAC luc chay
// ---------------------------------------------------------------------------
static void wifi_start_ap(void)
{
    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP);

    snprintf(g_ssid, sizeof(g_ssid), "STLAB-CAM-%02X%02X", mac[4], mac[5]);
    snprintf(g_pass, sizeof(g_pass), "%02X%02X%02X%02X", mac[2], mac[3], mac[4], mac[5]);

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init_cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));

    wifi_config_t wc;
    memset(&wc, 0, sizeof(wc));
    memcpy(wc.ap.ssid, g_ssid, strlen(g_ssid));
    wc.ap.ssid_len = (uint8_t)strlen(g_ssid);
    memcpy(wc.ap.password, g_pass, strlen(g_pass));
    wc.ap.channel = 1;
    wc.ap.max_connection = 4;
    wc.ap.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
    wifi_nha_init();
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wc));
    ESP_ERROR_CHECK(esp_wifi_start());
    wifi_nha_start();

    ESP_LOGI(TAG, "[DO] Wi-Fi AP: SSID=%s, mat khau=%s, dia chi=http://192.168.4.1",
             g_ssid, g_pass);
}

// ---------------------------------------------------------------------------
// HTTP server
// ---------------------------------------------------------------------------
static esp_err_t root_get(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, (const char *)index_html_start,
                           index_html_end - index_html_start);
}

static esp_err_t status_get(httpd_req_t *req)
{
    uint32_t flash_size = 0;
    esp_flash_get_size(NULL, &flash_size);
    size_t psram_size = esp_psram_get_size();
    float temp = chip_temperature();
    int64_t uptime_s = (esp_timer_get_time() - g.boot_us) / 1000000;

    char pidbuf[8];
    snprintf(pidbuf, sizeof(pidbuf), "0x%04X", g.pid);

    char nha[320];
    wifi_nha_status_json(nha, sizeof(nha));

    char buf[1400];
    int n = snprintf(buf, sizeof(buf),
        "{\"chip\":\"%s\",\"flash\":%" PRIu32 ",\"psram\":%u,"
        "\"bo_chan\":\"%s\",\"xclk_mhz\":%d,\"pid\":\"%s\","
        "\"ten_cam_bien\":\"%s\",\"framesize\":\"%s\","
        "\"fps_do_duoc\":%.1f,\"heap_free\":%u,\"psram_free\":%u,"
        "\"nhiet_do_chip\":%.1f,\"uptime_s\":%" PRId64 ",\"loi\":\"%s\",%s}",
        g.chip, flash_size, (unsigned)psram_size,
        g.bo_chan, g.xclk_mhz, pidbuf,
        g.ten_cam_bien, fs_name(g.framesize),
        (double)g.fps,
        (unsigned)esp_get_free_heap_size(),
        (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM),
        (double)temp, uptime_s, g.loi, nha);

    if (n < 0) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "loi tao JSON");
    }
    if (n >= (int)sizeof(buf)) {
        n = sizeof(buf) - 1;
    }

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, buf, n);
}

static esp_err_t capture_get(httpd_req_t *req)
{
    if (!g.cam_ok) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "camera chua san sang");
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (fb == NULL) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "khong lay duoc khung hinh");
    }

    g.frame_count++;
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
    return res;
}

static esp_err_t stream_get(httpd_req_t *req)
{
    if (!g.cam_ok) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR,
                                   "camera chua san sang");
    }

    esp_err_t res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=" STREAM_BOUNDARY);
    if (res != ESP_OK) {
        return res;
    }
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");

    char head[112];
    while (true) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb == NULL) {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        g.frame_count++;
        int hlen = snprintf(head, sizeof(head),
            "\r\n--" STREAM_BOUNDARY "\r\n"
            "Content-Type: image/jpeg\r\n"
            "Content-Length: %u\r\n\r\n",
            (unsigned)fb->len);

        res = httpd_resp_send_chunk(req, head, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, "\r\n", 2);
        }
        esp_camera_fb_return(fb);

        if (res != ESP_OK) {
            break;
        }
    }
    return ESP_FAIL;
}

static esp_err_t control_get(httpd_req_t *req)
{
    char query[96];
    if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK) {
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "thieu tham so");
    }

    char val[16];
    if (httpd_query_key_value(query, "framesize", val, sizeof(val)) == ESP_OK) {
        framesize_t fs;
        if (fs_parse(val, &fs)) {
            if (g_sensor != NULL) {
                g_sensor->set_framesize(g_sensor, fs);
            }
            g.framesize = fs;
        }
    }
    if (httpd_query_key_value(query, "quality", val, sizeof(val)) == ESP_OK) {
        int q = atoi(val);
        if (q < 0) {
            q = 0;
        }
        if (q > 63) {
            q = 63;
        }
        if (g_sensor != NULL) {
            g_sensor->set_quality(g_sensor, q);
        }
        g.quality = q;
    }

    char buf[96];
    snprintf(buf, sizeof(buf), "{\"framesize\":\"%s\",\"quality\":%d}",
             fs_name(g.framesize), g.quality);
    httpd_resp_set_type(req, "application/json");
    return httpd_resp_send(req, buf, strlen(buf));
}

static httpd_handle_t start_http_server(void)
{
    httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
    cfg.max_uri_handlers = 12;
    cfg.stack_size = 8192;
    cfg.lru_purge_enable = true;

    httpd_handle_t server = NULL;
    if (httpd_start(&server, &cfg) != ESP_OK) {
        return NULL;
    }

    httpd_uri_t uri_root = {
        .uri = "/", .method = HTTP_GET, .handler = root_get, .user_ctx = NULL,
    };
    httpd_uri_t uri_status = {
        .uri = "/status", .method = HTTP_GET, .handler = status_get, .user_ctx = NULL,
    };
    httpd_uri_t uri_capture = {
        .uri = "/capture", .method = HTTP_GET, .handler = capture_get, .user_ctx = NULL,
    };
    httpd_uri_t uri_stream = {
        .uri = "/stream", .method = HTTP_GET, .handler = stream_get, .user_ctx = NULL,
    };
    httpd_uri_t uri_control = {
        .uri = "/control", .method = HTTP_GET, .handler = control_get, .user_ctx = NULL,
    };

    httpd_register_uri_handler(server, &uri_root);
    httpd_register_uri_handler(server, &uri_status);
    httpd_register_uri_handler(server, &uri_capture);
    httpd_register_uri_handler(server, &uri_stream);
    httpd_register_uri_handler(server, &uri_control);
    return server;
}

// ---------------------------------------------------------------------------
// Task in trang thai moi 10 giay, tinh FPS trung binh 5 giay
// ---------------------------------------------------------------------------
static void monitor_task(void *arg)
{
    (void)arg;
    uint32_t last_count = g.frame_count;
    int ticks = 0;

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(5000));
        uint32_t now = g.frame_count;
        g.fps = (float)(now - last_count) / 5.0f;
        last_count = now;
        ticks++;

        if ((ticks % 2) == 0) {
            ESP_LOGI(TAG, "[DO] fps=%.1f heap=%u psram_free=%u nhiet=%.1f C",
                     (double)g.fps,
                     (unsigned)esp_get_free_heap_size(),
                     (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM),
                     (double)chip_temperature());
        }
    }
}

// ---------------------------------------------------------------------------
void app_main(void)
{
    g.boot_us = esp_timer_get_time();
    g.framesize = FRAMESIZE_SVGA;
    g.quality = 12;
    snprintf(g.bo_chan, sizeof(g.bo_chan), "chua thu");
    snprintf(g.ten_cam_bien, sizeof(g.ten_cam_bien), "KHONG_RO");

    ESP_LOGI(TAG, "[DO] Bat dau do phan cung ESP32-S3-CAM N16R8 + OV3660");
    print_board_info();
    tsens_init();
    camera_probe_all();

    if (!g.cam_ok) {
        ESP_LOGW(TAG, "[DO] Khong bo chan nao khoi tao duoc - van bat Wi-Fi de bao loi");
    }

    wifi_start_ap();

    if (start_http_server() == NULL) {
        ESP_LOGE(TAG, "[DO] Khong khoi dong duoc HTTP server");
    } else {
        ESP_LOGI(TAG, "[DO] HTTP server san sang: http://192.168.4.1");
    }

    xTaskCreate(monitor_task, "monitor", 4096, NULL, 3, NULL);
}
