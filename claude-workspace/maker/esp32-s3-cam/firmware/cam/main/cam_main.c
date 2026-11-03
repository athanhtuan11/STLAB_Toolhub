// Firmware chinh v0.2.0: camera giam sat ESP32-S3-CAM N16R8 + OV3660.
// - Chi MOT task camera goi esp_camera_fb_get, copy JPEG sang "khung moi nhat" (PSRAM, dem tham chieu).
// - Server cong 80: /, /capture, /status, /control. Server cong 81: /stream (MJPEG, moi nguoi xem 1 task rieng).
// - Khong ai giu camera_fb_t ngoai task camera, va task camera tra ngay sau khi copy.
// Mat khau khong duoc ghi vao ma/log (AP sinh tu MAC luc chay).

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <inttypes.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

#include "esp_log.h"
#include "esp_system.h"
#include "esp_psram.h"
#include "esp_mac.h"
#include "esp_timer.h"
#include "esp_heap_caps.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_http_server.h"
#include "driver/temperature_sensor.h"
#include "esp_camera.h"

#include "wifi_nha.h"

#define CAM_VERSION "0.2.0"

// Nguong nhiet: TODO chua co nguon datasheet (xem README), dat theo yeu cau spec.
#define TEMP_HOT_C 70.0f
#define TEMP_OK_C 62.0f
#define HOT_FPS 5

#define MAX_VIEWERS 2
#define N_SLOTS 5
#define JPEG_BUF_BYTES (768 * 1024)
#define CAPTURE_WAIT_MS 3000
#define CAPTURE_MAX_AGE_US 300000
#define STREAM_STALL_MS 5000
#define NULL_RESET_US 3000000
#define BOUNDARY "stlabboundary"

static const char *TAG = "[CAM]";

extern const uint8_t index_html_start[] asm("_binary_index_html_start");
extern const uint8_t index_html_end[] asm("_binary_index_html_end");

// ---------------------------------------------------------------------------
// Cau hinh (luu NVS namespace "cam_cfg")
// ---------------------------------------------------------------------------
typedef struct {
    int framesize;
    int quality;
    int vflip;
    int hmirror;
    int brightness;
    int contrast;
    int saturation;
    int fps;
    int aec;
    int ae_level;
    int rotate;  // 0/90/180/270: chi luu, trang web tu xoay hien thi
} cam_cfg_t;

static cam_cfg_t g_cfg = {
    .framesize = FRAMESIZE_SVGA, .quality = 12, .vflip = 1, .hmirror = 1,
    .brightness = 0, .contrast = 0, .saturation = 0, .fps = 10, .aec = 1, .ae_level = 0,
    .rotate = 0,
};

typedef struct {
    const char *name;
    int fs;
} fs_item_t;

static const fs_item_t s_fs_items[] = {
    {"QVGA", FRAMESIZE_QVGA}, {"VGA", FRAMESIZE_VGA}, {"SVGA", FRAMESIZE_SVGA},
    {"XGA", FRAMESIZE_XGA}, {"HD", FRAMESIZE_HD}, {"UXGA", FRAMESIZE_UXGA},
    {"QXGA", FRAMESIZE_QXGA},
};
#define FS_COUNT (sizeof(s_fs_items) / sizeof(s_fs_items[0]))

static const char *fs_name(int fs)
{
    for (size_t i = 0; i < FS_COUNT; i++) {
        if (s_fs_items[i].fs == fs) {
            return s_fs_items[i].name;
        }
    }
    return "KHAC";
}

static bool fs_valid(int fs)
{
    for (size_t i = 0; i < FS_COUNT; i++) {
        if (s_fs_items[i].fs == fs) {
            return true;
        }
    }
    return false;
}

static bool cfg_valid(const cam_cfg_t *c)
{
    return fs_valid(c->framesize) && c->quality >= 10 && c->quality <= 40 &&
           (c->vflip == 0 || c->vflip == 1) && (c->hmirror == 0 || c->hmirror == 1) &&
           c->brightness >= -2 && c->brightness <= 2 && c->contrast >= -2 && c->contrast <= 2 &&
           c->saturation >= -2 && c->saturation <= 2 && c->fps >= 1 && c->fps <= 25 &&
           (c->aec == 0 || c->aec == 1) && c->ae_level >= -2 && c->ae_level <= 2 &&
           (c->rotate == 0 || c->rotate == 90 || c->rotate == 180 || c->rotate == 270);
}

static void cfg_load(void)
{
    nvs_handle_t h;
    if (nvs_open("cam_cfg", NVS_READONLY, &h) != ESP_OK) {
        return;
    }
    cam_cfg_t c;
    size_t n = sizeof(c);
    if (nvs_get_blob(h, "cfg", &c, &n) == ESP_OK && n == sizeof(c) && cfg_valid(&c)) {
        g_cfg = c;
    } else {
        ESP_LOGW(TAG, "Cau hinh NVS khong hop le/khong co - dung mac dinh");
    }
    nvs_close(h);
}

static void cfg_save(void)
{
    nvs_handle_t h;
    if (nvs_open("cam_cfg", NVS_READWRITE, &h) != ESP_OK) {
        ESP_LOGW(TAG, "Khong mo duoc NVS cam_cfg");
        return;
    }
    if (nvs_set_blob(h, "cfg", &g_cfg, sizeof(g_cfg)) != ESP_OK || nvs_commit(h) != ESP_OK) {
        ESP_LOGW(TAG, "Khong ghi duoc NVS cam_cfg");
    }
    nvs_close(h);
}

// ---------------------------------------------------------------------------
// Trang thai chung
// ---------------------------------------------------------------------------
static SemaphoreHandle_t s_cam_mtx;    // giu khi fb_get/return hoac khi doi cam bien/khoi dong lai
static SemaphoreHandle_t s_store_mtx;  // bao ve kho khung + dem nguoi xem
static TaskHandle_t s_cam_task;
static temperature_sensor_handle_t s_tsens;

static volatile int s_viewers;
static volatile int s_cap_waiters;
static volatile int s_skip_frames;
static volatile bool s_cam_ok;
static volatile bool s_nong;
static volatile uint32_t s_frame_loi;
static volatile uint32_t s_cam_reinit;
static volatile uint32_t s_frames_pub;
static volatile float s_fps_thuc;
static volatile float s_temp = -999.0f;
static int64_t s_boot_us;
static char s_ap_ssid[32];

// ---------------------------------------------------------------------------
// Kho khung JPEG moi nhat (PSRAM, dem tham chieu)
// ---------------------------------------------------------------------------
typedef struct {
    uint8_t *buf;
    size_t cap;
    size_t len;
    uint32_t seq;
    int refs;
    int64_t t_us;
} slot_t;

static slot_t s_slots[N_SLOTS];
static int s_latest = -1;
static uint32_t s_seq;

// Copy mot khung vao slot trong. Chi task camera goi.
static bool store_publish(const uint8_t *src, size_t len)
{
    int idx = -1;
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    for (int i = 0; i < N_SLOTS; i++) {
        if (i != s_latest && s_slots[i].refs == 0) {
            idx = i;
            break;
        }
    }
    xSemaphoreGive(s_store_mtx);
    if (idx < 0) {
        return false;
    }
    slot_t *s = &s_slots[idx];  // refs == 0 va khong phai latest: chi task camera ghi
    if (s->cap < len) {
        size_t ncap = len + len / 8 + 1024;
        uint8_t *nb = heap_caps_malloc(ncap, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (nb == NULL) {
            return false;
        }
        heap_caps_free(s->buf);
        s->buf = nb;
        s->cap = ncap;
    }
    memcpy(s->buf, src, len);
    s->len = len;
    int64_t now = esp_timer_get_time();
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    s->seq = ++s_seq;
    s->t_us = now;
    s_latest = idx;
    xSemaphoreGive(s_store_mtx);
    return true;
}

// Lay khung moi nhat neu seq > min_seq va t_us >= min_t_us. Phai goi store_release sau do.
static bool store_acquire(uint32_t min_seq, int64_t min_t_us, int *idx)
{
    bool ok = false;
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    if (s_latest >= 0 && s_slots[s_latest].seq > min_seq && s_slots[s_latest].t_us >= min_t_us) {
        s_slots[s_latest].refs++;
        *idx = s_latest;
        ok = true;
    }
    xSemaphoreGive(s_store_mtx);
    return ok;
}

static void store_release(int idx)
{
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    if (s_slots[idx].refs > 0) {
        s_slots[idx].refs--;
    }
    xSemaphoreGive(s_store_mtx);
}

// Cong/tru bo dem dung chung (nguoi xem, cho chup)
static void counter_add(volatile int *c, int d)
{
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    *c += d;
    if (*c < 0) {
        *c = 0;
    }
    xSemaphoreGive(s_store_mtx);
}

static void cam_wake(void)
{
    if (s_cam_task != NULL) {
        xTaskNotifyGive(s_cam_task);
    }
}

// ---------------------------------------------------------------------------
// Camera
// ---------------------------------------------------------------------------
static esp_err_t camera_init_hw(void)
{
    camera_config_t cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.ledc_channel = LEDC_CHANNEL_0;
    cfg.ledc_timer = LEDC_TIMER_0;
    cfg.pin_pwdn = -1;
    cfg.pin_reset = -1;
    cfg.pin_xclk = 15;
    cfg.pin_sccb_sda = 4;
    cfg.pin_sccb_scl = 5;
    cfg.pin_d0 = 11;
    cfg.pin_d1 = 9;
    cfg.pin_d2 = 8;
    cfg.pin_d3 = 10;
    cfg.pin_d4 = 12;
    cfg.pin_d5 = 18;
    cfg.pin_d6 = 17;
    cfg.pin_d7 = 16;
    cfg.pin_vsync = 6;
    cfg.pin_href = 7;
    cfg.pin_pclk = 13;
    cfg.xclk_freq_hz = 20 * 1000000;
    cfg.pixel_format = PIXFORMAT_JPEG;
    cfg.frame_size = FRAMESIZE_SVGA;
    cfg.jpeg_quality = g_cfg.quality;
    cfg.fb_count = 2;
    cfg.fb_location = CAMERA_FB_IN_PSRAM;
    cfg.grab_mode = CAMERA_GRAB_LATEST;
    // Bo dem JPEG co dinh du lon cho moi do phan giai (mac dinh = rong*cao/5 theo luc khoi tao,
    // doi framesize len cao hon se tran bo dem).
    cfg.jpeg_buffer_size = JPEG_BUF_BYTES;
    return esp_camera_init(&cfg);
}

// Ap cau hinh len cam bien. Goi khi giu s_cam_mtx (hoac truoc khi task camera chay).
static void sensor_apply(void)
{
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return;
    }
    if (s->set_framesize) {
        s->set_framesize(s, (framesize_t)g_cfg.framesize);
    }
    if (s->set_quality) {
        s->set_quality(s, g_cfg.quality);
    }
    if (s->set_vflip) {
        s->set_vflip(s, g_cfg.vflip);
    }
    if (s->set_hmirror) {
        s->set_hmirror(s, g_cfg.hmirror);
    }
    if (s->set_brightness) {
        s->set_brightness(s, g_cfg.brightness);
    }
    if (s->set_contrast) {
        s->set_contrast(s, g_cfg.contrast);
    }
    if (s->set_saturation) {
        s->set_saturation(s, g_cfg.saturation);
    }
    if (s->set_exposure_ctrl) {
        s->set_exposure_ctrl(s, g_cfg.aec);
    }
    if (s->set_ae_level) {
        s->set_ae_level(s, g_cfg.ae_level);
    }
    s_skip_frames = 3;  // bo vai khung dau: khung cu con trong hang doi / cam bien dang on dinh
}

static int effective_fps(void)
{
    int f = g_cfg.fps;
    if (s_nong && f > HOT_FPS) {
        f = HOT_FPS;
    }
    return f;
}

static void camera_reinit(void)
{
    ESP_LOGW(TAG, "Khoi dong lai camera");
    esp_camera_deinit();
    vTaskDelay(pdMS_TO_TICKS(200));
    esp_err_t e = camera_init_hw();
    if (e == ESP_OK) {
        sensor_apply();
        s_cam_ok = true;
    } else {
        s_cam_ok = false;
        ESP_LOGE(TAG, "Khoi dong lai camera that bai: 0x%x", (unsigned)e);
    }
    s_cam_reinit++;
}

// Task DUY NHAT lay khung tu camera.
static void cam_task(void *arg)
{
    (void)arg;
    bool was_idle = true;
    int64_t next_us = 0;
    int64_t null_since = 0;

    for (;;) {
        if (s_viewers <= 0 && s_cap_waiters <= 0) {
            was_idle = true;
            null_since = 0;
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(200));
            continue;
        }
        int64_t now = esp_timer_get_time();
        if (!was_idle && now < next_us && s_skip_frames <= 0) {
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS((next_us - now) / 1000 + 1));
            continue;
        }
        if (was_idle) {
            if (s_skip_frames < 1) {
                s_skip_frames = 1;  // khung dang cho trong hang doi co the cu
            }
            was_idle = false;
        }
        int64_t start = esp_timer_get_time();

        xSemaphoreTake(s_cam_mtx, portMAX_DELAY);
        camera_fb_t *fb = s_cam_ok ? esp_camera_fb_get() : NULL;
        if (fb != NULL) {
            null_since = 0;
            if (s_skip_frames > 0) {
                s_skip_frames--;
            } else if (fb->format == PIXFORMAT_JPEG && fb->len > 0) {
                if (store_publish(fb->buf, fb->len)) {
                    s_frames_pub++;
                }
            }
            esp_camera_fb_return(fb);  // tra ngay, khong ai khac giu khung camera
        } else {
            s_frame_loi++;
            if (null_since == 0) {
                null_since = start;
            }
            if (start - null_since > NULL_RESET_US) {
                camera_reinit();
                null_since = 0;
            }
        }
        xSemaphoreGive(s_cam_mtx);

        if (fb == NULL) {
            vTaskDelay(pdMS_TO_TICKS(100));
        }
        next_us = start + 1000000 / effective_fps();
    }
}

// ---------------------------------------------------------------------------
// Nhiet do + log + fps thuc
// ---------------------------------------------------------------------------
static void monitor_task(void *arg)
{
    (void)arg;
    uint32_t last = s_frames_pub;
    int64_t last_us = esp_timer_get_time();
    int tick = 0;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(2000));
        float t = -999.0f;
        if (s_tsens != NULL && temperature_sensor_get_celsius(s_tsens, &t) != ESP_OK) {
            t = -999.0f;
        }
        s_temp = t;
        if (!s_nong && t > TEMP_HOT_C) {
            s_nong = true;
            ESP_LOGW(TAG, "Nong %.1f C - ha fps", (double)t);
        } else if (s_nong && t < TEMP_OK_C) {
            s_nong = false;
            ESP_LOGI(TAG, "Het nong %.1f C - tra fps", (double)t);
        }

        int64_t now = esp_timer_get_time();
        uint32_t cnt = s_frames_pub;
        float dt = (float)(now - last_us) / 1e6f;
        s_fps_thuc = (dt > 0) ? (float)(cnt - last) / dt : 0.0f;
        last = cnt;
        last_us = now;

        if (++tick % 5 == 0) {
            ESP_LOGI(TAG, "fps_thuc=%.1f nguoi_xem=%d nhiet=%.1f C heap=%u psram=%u frame_loi=%u",
                     (double)s_fps_thuc, (int)s_viewers, (double)t,
                     (unsigned)esp_get_free_heap_size(),
                     (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM), (unsigned)s_frame_loi);
        }
    }
}

// ---------------------------------------------------------------------------
// HTTP cong 80
// ---------------------------------------------------------------------------
static esp_err_t root_get(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    return httpd_resp_send(req, (const char *)index_html_start, index_html_end - index_html_start - 1);
}

static esp_err_t status_get(httpd_req_t *req)
{
    char nha[320];
    wifi_nha_status_json(nha, sizeof(nha));
    static char buf[1536];  // chi 1 handler cong 80 chay 1 luc (server don luong)
    int n = snprintf(buf, sizeof(buf),
        "{\"version\":\"" CAM_VERSION "\",\"uptime_s\":%" PRId64 ",\"nhiet_do_chip\":%.1f,\"nong\":%s,"
        "\"fps_cai\":%d,\"fps_thuc\":%.1f,\"so_nguoi_xem\":%d,\"framesize\":\"%s\",\"quality\":%d,"
        "\"vflip\":%d,\"hmirror\":%d,\"brightness\":%d,\"contrast\":%d,\"saturation\":%d,"
        "\"aec\":%d,\"ae_level\":%d,\"rotate\":%d,\"heap_free\":%u,\"psram_free\":%u,\"frame_loi\":%u,"
        "\"cam_reinit\":%u,\"cam_ok\":%s,%s,\"ap_ssid\":\"%s\"}",
        (esp_timer_get_time() - s_boot_us) / 1000000, (double)s_temp, s_nong ? "true" : "false",
        g_cfg.fps, (double)s_fps_thuc, (int)s_viewers, fs_name(g_cfg.framesize), g_cfg.quality,
        g_cfg.vflip, g_cfg.hmirror, g_cfg.brightness, g_cfg.contrast, g_cfg.saturation,
        g_cfg.aec, g_cfg.ae_level, g_cfg.rotate, (unsigned)esp_get_free_heap_size(),
        (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM), (unsigned)s_frame_loi,
        (unsigned)s_cam_reinit, s_cam_ok ? "true" : "false", nha, s_ap_ssid);
    if (n < 0 || n >= (int)sizeof(buf)) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "loi tao JSON");
    }
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, buf, n);
}

static esp_err_t capture_get(httpd_req_t *req)
{
    int64_t req_us = esp_timer_get_time();
    counter_add(&s_cap_waiters, 1);
    cam_wake();

    int idx = -1;
    bool got = false;
    while ((esp_timer_get_time() - req_us) / 1000 < CAPTURE_WAIT_MS) {
        if (store_acquire(0, req_us - CAPTURE_MAX_AGE_US, &idx)) {
            got = true;
            break;
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
    counter_add(&s_cap_waiters, -1);

    if (!got) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "khong lay duoc khung hinh");
    }
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Content-Disposition", "inline; filename=capture.jpg");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    esp_err_t r = httpd_resp_send(req, (const char *)s_slots[idx].buf, s_slots[idx].len);
    store_release(idx);
    return r;
}

static bool parse_int(const char *s, int *out)
{
    char *end = NULL;
    long v = strtol(s, &end, 10);
    if (end == s || *end != '\0') {
        return false;
    }
    *out = (int)v;
    return true;
}

static esp_err_t control_get(httpd_req_t *req)
{
    char query[96];
    char var[24];
    char sval[16];
    int val = 0;
    if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK ||
        httpd_query_key_value(query, "var", var, sizeof(var)) != ESP_OK ||
        httpd_query_key_value(query, "val", sval, sizeof(sval)) != ESP_OK ||
        !parse_int(sval, &val)) {
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "can var=<ten>&val=<so>");
    }

    cam_cfg_t n = g_cfg;
    bool is_fs = false;
    if (strcmp(var, "framesize") == 0) {
        n.framesize = val;
        is_fs = true;
    } else if (strcmp(var, "quality") == 0) {
        n.quality = val;
    } else if (strcmp(var, "vflip") == 0) {
        n.vflip = val;
    } else if (strcmp(var, "hmirror") == 0) {
        n.hmirror = val;
    } else if (strcmp(var, "brightness") == 0) {
        n.brightness = val;
    } else if (strcmp(var, "contrast") == 0) {
        n.contrast = val;
    } else if (strcmp(var, "saturation") == 0) {
        n.saturation = val;
    } else if (strcmp(var, "fps") == 0) {
        n.fps = val;
    } else if (strcmp(var, "aec") == 0) {
        n.aec = val;
    } else if (strcmp(var, "ae_level") == 0) {
        n.ae_level = val;
    } else if (strcmp(var, "rotate") == 0) {
        n.rotate = val;
    } else {
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "var khong hop le");
    }
    if (!cfg_valid(&n)) {
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "gia tri ngoai khoang cho phep");
    }

    // Giu s_cam_mtx: task camera dung lay khung trong luc doi cam bien.
    if (xSemaphoreTake(s_cam_mtx, pdMS_TO_TICKS(6000)) != pdTRUE) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "camera ban");
    }
    g_cfg = n;
    if (s_cam_ok) {
        if (is_fs) {
            sensor_apply();
        } else {
            sensor_t *s = esp_camera_sensor_get();
            if (s != NULL) {
                if (strcmp(var, "quality") == 0 && s->set_quality) {
                    s->set_quality(s, n.quality);
                } else if (strcmp(var, "vflip") == 0 && s->set_vflip) {
                    s->set_vflip(s, n.vflip);
                } else if (strcmp(var, "hmirror") == 0 && s->set_hmirror) {
                    s->set_hmirror(s, n.hmirror);
                } else if (strcmp(var, "brightness") == 0 && s->set_brightness) {
                    s->set_brightness(s, n.brightness);
                } else if (strcmp(var, "contrast") == 0 && s->set_contrast) {
                    s->set_contrast(s, n.contrast);
                } else if (strcmp(var, "saturation") == 0 && s->set_saturation) {
                    s->set_saturation(s, n.saturation);
                } else if (strcmp(var, "aec") == 0 && s->set_exposure_ctrl) {
                    s->set_exposure_ctrl(s, n.aec);
                } else if (strcmp(var, "ae_level") == 0 && s->set_ae_level) {
                    s->set_ae_level(s, n.ae_level);
                }
            }
        }
    }
    xSemaphoreGive(s_cam_mtx);
    cfg_save();

    httpd_resp_set_type(req, "application/json");
    return httpd_resp_sendstr(req, "{\"ok\":1}");
}

// ---------------------------------------------------------------------------
// HTTP cong 81: /stream, moi nguoi xem 1 task rieng (handler tra ve ngay)
// ---------------------------------------------------------------------------
static void stream_task(void *arg)
{
    httpd_req_t *req = (httpd_req_t *)arg;
    char head[128];
    uint32_t last_seq = 0;
    int64_t last_frame_us = esp_timer_get_time();
    int64_t t_min = last_frame_us - CAPTURE_MAX_AGE_US;  // bo khung cu luc moi ket noi
    esp_err_t res = httpd_resp_set_type(req, "multipart/x-mixed-replace;boundary=" BOUNDARY);
    if (res == ESP_OK) {
        httpd_resp_set_hdr(req, "Cache-Control", "no-store");
        cam_wake();
    }

    while (res == ESP_OK) {
        int idx = -1;
        if (!store_acquire(last_seq, t_min, &idx)) {
            if ((esp_timer_get_time() - last_frame_us) / 1000 > STREAM_STALL_MS) {
                break;  // camera dung qua lau: dong ket noi de giai phong nguoi xem
            }
            vTaskDelay(pdMS_TO_TICKS(10));
            continue;
        }
        last_seq = s_slots[idx].seq;
        int hlen = snprintf(head, sizeof(head),
                            "\r\n--" BOUNDARY "\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
                            (unsigned)s_slots[idx].len);
        res = httpd_resp_send_chunk(req, head, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)s_slots[idx].buf, s_slots[idx].len);
        }
        store_release(idx);  // moi duong thoat deu tra tham chieu
        last_frame_us = esp_timer_get_time();
    }

    httpd_resp_send_chunk(req, NULL, 0);
    httpd_req_async_handler_complete(req);
    counter_add(&s_viewers, -1);  // moi duong thoat (loi gui, timeout, dong socket) deu giam dem
    vTaskDelete(NULL);
}

static esp_err_t stream_get(httpd_req_t *req)
{
    xSemaphoreTake(s_store_mtx, portMAX_DELAY);
    bool ok = s_viewers < MAX_VIEWERS;
    if (ok) {
        s_viewers++;
    }
    xSemaphoreGive(s_store_mtx);
    if (!ok) {
        httpd_resp_set_status(req, "503 Service Unavailable");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Toi da 2 nguoi xem");
    }

    httpd_req_t *areq = NULL;
    if (httpd_req_async_handler_begin(req, &areq) != ESP_OK) {
        counter_add(&s_viewers, -1);
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "khong tao duoc luong xem");
    }
    if (xTaskCreate(stream_task, "stream", 6144, areq, 5, NULL) != pdPASS) {
        counter_add(&s_viewers, -1);
        httpd_resp_send_err(areq, HTTPD_500_INTERNAL_SERVER_ERROR, "het bo nho");
        httpd_req_async_handler_complete(areq);
        return ESP_OK;
    }
    return ESP_OK;
}

static httpd_handle_t start_server(httpd_config_t cfg, const httpd_uri_t *uris, size_t n_uris)
{
    cfg.max_open_sockets = 4;
    cfg.max_uri_handlers = 8;
    cfg.stack_size = 6144;
    cfg.lru_purge_enable = true;
    cfg.recv_wait_timeout = 5;
    cfg.send_wait_timeout = 5;

    httpd_handle_t h = NULL;
    if (httpd_start(&h, &cfg) != ESP_OK) {
        return NULL;
    }
    for (size_t i = 0; i < n_uris; i++) {
        httpd_register_uri_handler(h, &uris[i]);
    }
    return h;
}

static void start_servers(void)
{
    static const httpd_uri_t main_uris[] = {
        {.uri = "/", .method = HTTP_GET, .handler = root_get, .user_ctx = NULL},
        {.uri = "/status", .method = HTTP_GET, .handler = status_get, .user_ctx = NULL},
        {.uri = "/capture", .method = HTTP_GET, .handler = capture_get, .user_ctx = NULL},
        {.uri = "/control", .method = HTTP_GET, .handler = control_get, .user_ctx = NULL},
    };
    static const httpd_uri_t stream_uris[] = {
        {.uri = "/stream", .method = HTTP_GET, .handler = stream_get, .user_ctx = NULL},
    };
    httpd_config_t c80 = HTTPD_DEFAULT_CONFIG();
    c80.server_port = 80;
    c80.ctrl_port = 32768;
    httpd_config_t c81 = HTTPD_DEFAULT_CONFIG();
    c81.server_port = 81;
    c81.ctrl_port = 32769;  // phai khac cong 80 (mac dinh 32768 trung)
    if (start_server(c80, main_uris, 4) == NULL) {
        ESP_LOGE(TAG, "Khong mo duoc server cong 80");
    }
    if (start_server(c81, stream_uris, 1) == NULL) {
        ESP_LOGE(TAG, "Khong mo duoc server cong 81");
    }
}

// ---------------------------------------------------------------------------
// Wi-Fi: AP du phong (SSID/mat khau sinh tu MAC) + STA nha (wifi_nha)
// ---------------------------------------------------------------------------
static void wifi_start(void)
{
    uint8_t mac[6] = {0};
    esp_read_mac(mac, ESP_MAC_WIFI_SOFTAP);
    char ap_pw[16];
    snprintf(s_ap_ssid, sizeof(s_ap_ssid), "STLAB-CAM-%02X%02X", mac[4], mac[5]);
    snprintf(ap_pw, sizeof(ap_pw), "%02X%02X%02X%02X", mac[2], mac[3], mac[4], mac[5]);

    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_ap();

    wifi_init_config_t init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&init_cfg));
    ESP_ERROR_CHECK(esp_wifi_set_storage(WIFI_STORAGE_RAM));

    wifi_config_t wc;
    memset(&wc, 0, sizeof(wc));
    memcpy(wc.ap.ssid, s_ap_ssid, strlen(s_ap_ssid));
    wc.ap.ssid_len = (uint8_t)strlen(s_ap_ssid);
    memcpy(wc.ap.password, ap_pw, strlen(ap_pw));
    wc.ap.channel = 1;
    wc.ap.max_connection = 4;
    wc.ap.authmode = WIFI_AUTH_WPA2_PSK;

    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_APSTA));
    wifi_nha_init();
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_AP, &wc));
    ESP_ERROR_CHECK(esp_wifi_start());
    wifi_nha_start();
    ESP_LOGI(TAG, "Wi-Fi AP du phong: SSID=%s, dia chi http://192.168.4.1", s_ap_ssid);
}

void app_main(void)
{
    s_boot_us = esp_timer_get_time();
    s_cam_mtx = xSemaphoreCreateMutex();
    s_store_mtx = xSemaphoreCreateMutex();

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    cfg_load();

    temperature_sensor_config_t tc = TEMPERATURE_SENSOR_CONFIG_DEFAULT(-10, 80);
    if (temperature_sensor_install(&tc, &s_tsens) != ESP_OK || temperature_sensor_enable(s_tsens) != ESP_OK) {
        s_tsens = NULL;
        ESP_LOGW(TAG, "Khong doc duoc nhiet do chip");
    }

    // Khoi dong camera TRUOC Wi-Fi (giong probe, tranh GDMA treo khi STA len)
    err = camera_init_hw();
    if (err == ESP_OK) {
        sensor_apply();
        s_cam_ok = true;
        ESP_LOGI(TAG, "Camera san sang, %s, fps %d", fs_name(g_cfg.framesize), g_cfg.fps);
    } else {
        ESP_LOGE(TAG, "esp_camera_init loi 0x%x - se thu lai khi co nguoi xem", (unsigned)err);
    }

    wifi_start();
    start_servers();

    xTaskCreate(cam_task, "cam", 4096, NULL, 6, &s_cam_task);
    xTaskCreate(monitor_task, "monitor", 3072, NULL, 3, NULL);
    ESP_LOGI(TAG, "STLab Cam " CAM_VERSION " chay");
}
