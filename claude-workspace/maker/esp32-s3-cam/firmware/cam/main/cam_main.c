// Firmware chinh v0.4.0 (OTA, the TF, phat hien chuyen dong, ghi clip AVI MJPEG khi co chuyen dong): camera giam sat ESP32-S3-CAM N16R8 + OV3660.
// - Chi MOT task camera goi esp_camera_fb_get, copy JPEG sang "khung moi nhat" (PSRAM, dem tham chieu).
// - Server cong 80: /, /capture, /status, /control. Server cong 81: /stream (MJPEG, moi nguoi xem 1 task rieng).
// - Khong ai giu camera_fb_t ngoai task camera, va task camera tra ngay sau khi copy.
// Mat khau khong duoc ghi vao ma/log (AP sinh tu MAC luc chay).

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <inttypes.h>
#include <time.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>
#include <unistd.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

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
#include "img_converters.h"
#include "jpeg_decoder.h"
#include "esp_ota_ops.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"
#include "driver/sdmmc_host.h"
#include "driver/gpio.h"
#include "esp_netif_sntp.h"
#include "esp_pm.h"

#include "wifi_nha.h"
#include "avi_mjpeg.h"

#define CAM_VERSION "0.4.0"

// Giam nhiet (0.3.1): camera ngu that, tat AP khi da vao Wi-Fi nha, modem sleep khi khong ai xem
#define CAM_IDLE_SLEEP_S 15
#define AP_OFF_DELAY_S 60
#define AP_BACK_DELAY_S 60

// Nguong nhiet: TODO chua co nguon datasheet (xem README), dat theo yeu cau spec.
#define TEMP_HOT_C 70.0f
#define TEMP_OK_C 62.0f
#define HOT_FPS 5

#define MAX_VIEWERS 2
#define N_SLOTS 5
#define JPEG_BUF_BYTES (768 * 1024)
#define CAPTURE_WAIT_MS 5000
#define CAPTURE_MAX_AGE_US 300000
#define STREAM_STALL_MS 5000
#define NULL_RESET_US 3000000
#define BOUNDARY "stlabboundary"

#define MOTION_FPS 2
#define MOTION_PERIOD_MS 500
#define MOTION_COOLDOWN_US (10 * 1000000LL)
#define MOT_PIX_MAX (320 * 240)
#define N_EVENTS 20
#define OTA_MAX_BYTES (4 * 1024 * 1024)
#define SD_MOUNT "/sdcard"
#define SD_DIR "stlab-cam"
#define SD_RETRY_US (30 * 1000000LL)
#define SD_MIN_FREE_MB 200
#define SD_MIN_FREE_PCT 10

// Ghi clip AVI (0.4.0)
#define CLIP_RING_MAX 64                  // so khung toi da trong bo dem truoc su kien
#define CLIP_RING_BYTES (2 * 1024 * 1024) // bo dem truoc su kien <= 2 MB PSRAM
#define CLIP_MAX_S 60                     // toi da 60 s / clip
#define CLIP_IDX_MAX 2048                 // so muc idx1 toi da / clip
#define CLIP_WBUF 16384                   // dem ghi >= 16 KB
#define SD_Q_LEN 32

static const char *TAG = "[CAM]";
static const char *TAG_OTA = "[OTA]";
static const char *TAG_SD = "[SD]";
static const char *TAG_MOT = "[MOTION]";

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
    int motion;      // 0/1 phat hien chuyen dong
    int motion_thr;  // 5..80 nguong lech do sang 1 diem anh
    int motion_pct;  // 1..50 % diem anh doi
} cam_cfg_t;

// Tham so ghi clip (luu NVS cam_cfg/"clip", tach khoi blob cam_cfg_t de khong mat cau hinh cu)
typedef struct {
    int clip;      // 0/1
    int clip_fps;  // 1..10
    int pre_s;     // 0..5
    int post_s;    // 2..30
} clip_cfg_t;

static clip_cfg_t g_clip = {.clip = 0, .clip_fps = 5, .pre_s = 3, .post_s = 5};

static bool clip_valid(const clip_cfg_t *c)
{
    return (c->clip == 0 || c->clip == 1) && c->clip_fps >= 1 && c->clip_fps <= 10 && c->pre_s >= 0 &&
           c->pre_s <= 5 && c->post_s >= 2 && c->post_s <= 30;
}

static cam_cfg_t g_cfg = {
    .framesize = FRAMESIZE_SVGA, .quality = 12, .vflip = 1, .hmirror = 1,
    .brightness = 0, .contrast = 0, .saturation = 0, .fps = 10, .aec = 1, .ae_level = 0,
    .rotate = 0, .motion = 0, .motion_thr = 25, .motion_pct = 3,
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
           (c->rotate == 0 || c->rotate == 90 || c->rotate == 180 || c->rotate == 270) &&
           (c->motion == 0 || c->motion == 1) && c->motion_thr >= 5 && c->motion_thr <= 80 &&
           c->motion_pct >= 1 && c->motion_pct <= 50;
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

static void clip_load(void)
{
    nvs_handle_t h;
    if (nvs_open("cam_cfg", NVS_READONLY, &h) != ESP_OK) {
        return;
    }
    clip_cfg_t c;
    size_t n = sizeof(c);
    if (nvs_get_blob(h, "clip", &c, &n) == ESP_OK && n == sizeof(c) && clip_valid(&c)) {
        g_clip = c;
    }
    nvs_close(h);
}

static void clip_save(void)
{
    nvs_handle_t h;
    if (nvs_open("cam_cfg", NVS_READWRITE, &h) != ESP_OK) {
        ESP_LOGW(TAG, "Khong mo duoc NVS cam_cfg");
        return;
    }
    if (nvs_set_blob(h, "clip", &g_clip, sizeof(g_clip)) != ESP_OK || nvs_commit(h) != ESP_OK) {
        ESP_LOGW(TAG, "Khong ghi duoc NVS clip");
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
static volatile bool s_cam_sleep;  // camera da esp_camera_deinit (khong XCLK, khong DMA)
static volatile bool s_ap_on = true;
static volatile bool s_ps_none = true;  // true = khong tiet kiem dien (hoac dang APSTA)
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
// Gio (SNTP) + trang thai OTA / the TF / chuyen dong
// ---------------------------------------------------------------------------
static volatile bool s_ota_busy;
static volatile bool s_sd_ok;
static volatile uint32_t s_sd_free_mb;
static volatile uint32_t s_motion_count;
static volatile int64_t s_motion_last_us = -1;
static volatile bool s_clip_rec;        // dang co file AVI mo de ghi
static volatile bool s_clip_err;        // task ghi bao: clip hien tai that bai/bi huy
static volatile uint32_t s_clip_count;  // so clip da ghi xong
static volatile uint32_t s_clip_drop;   // so khung bi bo (queue day / loi)

static bool time_ok(void)
{
    return time(NULL) > 1700000000;
}

static void on_got_ip(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    (void)arg;
    (void)base;
    (void)id;
    (void)data;
    static bool started = false;
    if (!started) {
        esp_sntp_config_t sc = ESP_NETIF_SNTP_DEFAULT_CONFIG("pool.ntp.org");
        esp_err_t se = esp_netif_sntp_init(&sc);
        if (se == ESP_OK) {
            started = true;
        }
        ESP_LOGI(TAG, "SNTP pool.ntp.org: %s", esp_err_to_name(se));
    }
}

// ---------------------------------------------------------------------------
// The TF (SDMMC 1-bit). Tuan chua co the: moi thu phai chay khi khong the.
// ---------------------------------------------------------------------------
enum { JOB_JPEG = 0, JOB_CLIP_OPEN, JOB_CLIP_FRAME, JOB_CLIP_CLOSE };

typedef struct {
    uint8_t kind;     // JOB_*
    int idx;          // JOB_JPEG: slot khung dang giu tham chieu
    char path[56];    // duong dan tuong doi trong /sdcard, vd stlab-cam/20261105/140322.jpg (.avi cho clip)
    uint8_t *buf;     // JOB_CLIP_FRAME: ban sao JPEG (PSRAM), task ghi se free
    uint32_t len;
    int64_t t_us;     // thoi diem khung (clip)
    uint32_t w, h;    // JOB_CLIP_OPEN: kich thuoc anh
    uint32_t fps;     // JOB_CLIP_OPEN: fps danh dinh
} sd_job_t;

static QueueHandle_t s_sd_q;
static sdmmc_card_t *s_card;
static int64_t s_sd_next_try_us;

// ---- Bo ghi AVI (chi task sd dung) ----
typedef struct {
    bool open;
    FILE *f;
    uint8_t *wbuf;       // dem ghi CLIP_WBUF byte
    size_t wlen;
    uint32_t *idx_off;   // muc idx1: offset + size moi khung
    uint32_t *idx_len;
    uint32_t frames;
    uint32_t max_chunk;
    uint32_t chunk_bytes;  // tong byte cac chunk trong movi
    uint32_t w, h, fps;
    int64_t t_first, t_last;
    int64_t space_chk_us;
    char path[56];
    char dir[24];          // ten thu muc ngay dang ghi (khong cho don dep xoa)
} avi_t;

static avi_t s_avi;

static bool sd_mount(void)
{
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    host.flags = SDMMC_HOST_FLAG_1BIT;
    host.max_freq_khz = SDMMC_FREQ_DEFAULT;
    sdmmc_slot_config_t slot = SDMMC_SLOT_CONFIG_DEFAULT();
    slot.width = 1;
    slot.clk = GPIO_NUM_39;
    slot.cmd = GPIO_NUM_38;
    slot.d0 = GPIO_NUM_40;
    slot.flags |= SDMMC_SLOT_FLAG_INTERNAL_PULLUP;
    esp_vfs_fat_mount_config_t mc = {
        .format_if_mount_failed = false,  // KHONG BAO GIO format the cua nguoi dung
        .max_files = 4,
        .allocation_unit_size = 16 * 1024,
    };
    s_card = NULL;
    return esp_vfs_fat_sdmmc_mount(SD_MOUNT, &host, &slot, &mc, &s_card) == ESP_OK;
}

static void avi_abort(void);

static void sd_drop(const char *why)
{
    ESP_LOGW(TAG_SD, "Bo the (%s) - thu lai moi 30 s", why);
    avi_abort();
    esp_vfs_fat_sdcard_unmount(SD_MOUNT, s_card);
    s_card = NULL;
    s_sd_ok = false;
    s_sd_free_mb = 0;
    s_sd_next_try_us = esp_timer_get_time() + SD_RETRY_US;
}

static bool sd_info(uint64_t *total, uint64_t *freeb)
{
    return esp_vfs_fat_info(SD_MOUNT, total, freeb) == ESP_OK && *total > 0;
}

// Xoa thu muc ngay cu nhat trong stlab-cam ("boot" coi la cu nhat).
static bool sd_prune_oldest(void)
{
    DIR *d = opendir(SD_MOUNT "/" SD_DIR);
    if (d == NULL) {
        return false;
    }
    char best[32] = "";
    struct dirent *e;
    while ((e = readdir(d)) != NULL) {
        if (e->d_type != DT_DIR || e->d_name[0] == '.' || strlen(e->d_name) >= sizeof(best)) {
            continue;
        }
        if (best[0] == '\0' || strcmp(e->d_name, "boot") == 0 ||
            (strcmp(best, "boot") != 0 && strcmp(e->d_name, best) < 0)) {
            strcpy(best, e->d_name);
        }
    }
    closedir(d);
    if (best[0] == '\0') {
        return false;
    }
    if (s_avi.open && strcmp(best, s_avi.dir) == 0) {
        return false;  // khong xoa thu muc co file AVI dang ghi
    }
    char dir[96];
    snprintf(dir, sizeof(dir), SD_MOUNT "/" SD_DIR "/%s", best);
    d = opendir(dir);
    if (d != NULL) {
        char fp[400];
        while ((e = readdir(d)) != NULL) {
            if (e->d_name[0] != '.') {
                snprintf(fp, sizeof(fp), "%s/%s", dir, e->d_name);
                unlink(fp);
            }
        }
        closedir(d);
    }
    ESP_LOGI(TAG_SD, "Day the - xoa thu muc cu %s", best);
    return rmdir(dir) == 0;
}

// Cap nhat dung luong trong; xoa ngay cu khi sap day. false = khong con cho ghi.
static bool sd_ensure_space(void)
{
    uint64_t total = 0, freeb = 0;
    for (int i = 0; i < 10; i++) {
        if (!sd_info(&total, &freeb)) {
            return false;
        }
        s_sd_free_mb = (uint32_t)(freeb / (1024 * 1024));
        bool low = freeb * 100 < total * SD_MIN_FREE_PCT || (freeb / (1024 * 1024)) < SD_MIN_FREE_MB;
        if (!low) {
            return true;
        }
        if (!sd_prune_oldest()) {
            break;
        }
    }
    return sd_info(&total, &freeb) && (freeb / (1024 * 1024)) >= 5;
}

static bool sd_write_job(const sd_job_t *j)
{
    if (!sd_ensure_space()) {
        return true;  // day va khong xoa duoc: bo qua, khong coi la loi the
    }
    char full[96];
    snprintf(full, sizeof(full), SD_MOUNT "/%s", j->path);
    char dir[96];
    snprintf(dir, sizeof(dir), "%s", full);
    char *slash = strrchr(dir, '/');
    if (slash == NULL) {
        return false;
    }
    *slash = '\0';
    mkdir(SD_MOUNT "/" SD_DIR, 0775);
    mkdir(dir, 0775);
    FILE *f = fopen(full, "wb");
    if (f == NULL) {
        return false;
    }
    size_t w = fwrite(s_slots[j->idx].buf, 1, s_slots[j->idx].len, f);
    int c = fclose(f);
    return w == s_slots[j->idx].len && c == 0;
}

// ---------------------------------------------------------------------------
// Ghi clip AVI MJPEG (task sd). Dinh dang: avi_mjpeg.h.
// ---------------------------------------------------------------------------
static bool avi_flush(void)
{
    if (s_avi.wlen == 0) {
        return true;
    }
    size_t w = fwrite(s_avi.wbuf, 1, s_avi.wlen, s_avi.f);
    bool ok = (w == s_avi.wlen);
    s_avi.wlen = 0;
    return ok;
}

static bool avi_write(const void *d, size_t n)
{
    const uint8_t *p = (const uint8_t *)d;
    if (s_avi.wlen == 0 && n >= CLIP_WBUF) {
        return fwrite(p, 1, n, s_avi.f) == n;  // khoi lon: ghi thang
    }
    while (n > 0) {
        size_t room = CLIP_WBUF - s_avi.wlen;
        size_t c = n < room ? n : room;
        memcpy(s_avi.wbuf + s_avi.wlen, p, c);
        s_avi.wlen += c;
        p += c;
        n -= c;
        if (s_avi.wlen == CLIP_WBUF && !avi_flush()) {
            return false;
        }
    }
    return true;
}

static void avi_release(void)
{
    heap_caps_free(s_avi.wbuf);
    heap_caps_free(s_avi.idx_off);
    heap_caps_free(s_avi.idx_len);
    s_avi.wbuf = NULL;
    s_avi.idx_off = NULL;
    s_avi.idx_len = NULL;
    s_avi.f = NULL;
    s_avi.open = false;
    s_clip_rec = false;
}

// Huy clip khi mat the: dong file neu duoc, khong cap nhat header.
static void avi_abort(void)
{
    s_clip_err = true;
    if (!s_avi.open) {
        return;
    }
    if (s_avi.f != NULL) {
        fclose(s_avi.f);
    }
    ESP_LOGW(TAG_SD, "Clip bi huy: %s", s_avi.path);
    avi_release();
}

// Dong clip: ghi idx1, ghi lai header voi so khung/kich thuoc/fps that. false = loi ghi.
static bool avi_close(void)
{
    if (!s_avi.open) {
        return true;
    }
    uint32_t n = s_avi.frames;
    bool ok = avi_flush();
    if (ok && n > 0) {
        uint8_t ih[8];
        avi_tag(ih, "idx1");
        avi_p32(ih + 4, n * AVI_IDX_ENTRY);
        ok = avi_write(ih, 8);
        for (uint32_t i = 0; ok && i < n; i++) {
            uint8_t e[AVI_IDX_ENTRY];
            avi_idx_entry(e, s_avi.idx_off[i], s_avi.idx_len[i]);
            ok = avi_write(e, AVI_IDX_ENTRY);
        }
        ok = ok && avi_flush();
    }
    if (ok && n > 0) {
        uint32_t fps_milli = s_avi.fps * 1000;
        if (n >= 2 && s_avi.t_last > s_avi.t_first) {
            uint64_t m = ((uint64_t)(n - 1) * 1000000000ULL) / (uint64_t)(s_avi.t_last - s_avi.t_first);
            if (m >= 500 && m <= 30000) {
                fps_milli = (uint32_t)m;
            }
        }
        uint8_t hdr[AVI_HDR_BYTES];
        avi_build_header(hdr, s_avi.w, s_avi.h, fps_milli, n, s_avi.max_chunk, s_avi.chunk_bytes,
                         n * AVI_IDX_ENTRY);
        ok = fseek(s_avi.f, 0, SEEK_SET) == 0 && fwrite(hdr, 1, AVI_HDR_BYTES, s_avi.f) == AVI_HDR_BYTES;
    }
    int c = (s_avi.f != NULL) ? fclose(s_avi.f) : -1;
    ok = ok && c == 0;
    char full[96];
    snprintf(full, sizeof(full), SD_MOUNT "/%s", s_avi.path);
    if (n == 0) {
        unlink(full);
    } else if (ok) {
        s_clip_count++;
        ESP_LOGI(TAG_SD, "Clip xong %s: %u khung", s_avi.path, (unsigned)n);
    }
    avi_release();
    return ok;
}

// Mo clip moi. false = loi the (goi sd_drop). Het cho/khong du dung luong: bo clip, the van tot.
static bool avi_open(const sd_job_t *j)
{
    avi_close();
    memset(&s_avi, 0, sizeof(s_avi));
    if (!sd_ensure_space()) {
        s_clip_err = true;
        return true;
    }
    snprintf(s_avi.path, sizeof(s_avi.path), "%s", j->path);
    const char *day = s_avi.path + strlen(SD_DIR) + 1;
    const char *sl = strchr(day, '/');
    if (strncmp(s_avi.path, SD_DIR "/", strlen(SD_DIR) + 1) != 0 || sl == NULL ||
        (size_t)(sl - day) >= sizeof(s_avi.dir)) {
        s_clip_err = true;
        return true;
    }
    memcpy(s_avi.dir, day, (size_t)(sl - day));
    s_avi.wbuf = heap_caps_malloc(CLIP_WBUF, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    s_avi.idx_off = heap_caps_malloc(CLIP_IDX_MAX * sizeof(uint32_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    s_avi.idx_len = heap_caps_malloc(CLIP_IDX_MAX * sizeof(uint32_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (s_avi.wbuf == NULL || s_avi.idx_off == NULL || s_avi.idx_len == NULL) {
        ESP_LOGW(TAG_SD, "Het PSRAM - bo clip");
        avi_release();
        s_clip_err = true;
        return true;
    }
    char full[96];
    snprintf(full, sizeof(full), SD_MOUNT "/%s", s_avi.path);
    char dirp[96];
    snprintf(dirp, sizeof(dirp), "%s", full);
    char *slash = strrchr(dirp, '/');
    *slash = '\0';
    mkdir(SD_MOUNT "/" SD_DIR, 0775);
    mkdir(dirp, 0775);
    s_avi.f = fopen(full, "wb");
    if (s_avi.f == NULL) {
        avi_release();
        return false;
    }
    s_avi.open = true;
    s_avi.w = j->w;
    s_avi.h = j->h;
    s_avi.fps = j->fps;
    s_avi.space_chk_us = esp_timer_get_time();
    uint8_t hdr[AVI_HDR_BYTES];
    avi_build_header(hdr, j->w, j->h, j->fps * 1000, 0, 0, 0, 0);  // giu cho, ghi lai luc dong
    if (!avi_write(hdr, AVI_HDR_BYTES)) {
        return false;  // sd_drop se avi_abort
    }
    s_clip_rec = true;
    ESP_LOGI(TAG_SD, "Mo clip %s (%ux%u, %u fps)", s_avi.path, (unsigned)j->w, (unsigned)j->h, (unsigned)j->fps);
    return true;
}

// Ghi 1 khung. false = loi the.
static bool avi_frame(const sd_job_t *j)
{
    if (!s_avi.open || s_avi.frames >= CLIP_IDX_MAX || j->len == 0) {
        s_clip_drop++;
        return true;
    }
    int64_t now = esp_timer_get_time();
    if (now - s_avi.space_chk_us > 10000000LL) {
        s_avi.space_chk_us = now;
        if (!sd_ensure_space()) {
            uint64_t total = 0, freeb = 0;
            if (!sd_info(&total, &freeb)) {
                return false;  // mat the
            }
            s_clip_err = true;  // day the: dong clip, giu phan da ghi
            return avi_close();
        }
    }
    uint8_t ch[AVI_CHUNK_HDR];
    avi_tag(ch, "00dc");
    avi_p32(ch + 4, j->len);
    uint32_t off = 4 + s_avi.chunk_bytes;  // tinh tu chu 'movi'
    bool ok = avi_write(ch, AVI_CHUNK_HDR) && avi_write(j->buf, j->len);
    if (ok && (j->len & 1u)) {
        uint8_t z = 0;
        ok = avi_write(&z, 1);
    }
    if (!ok) {
        return false;
    }
    s_avi.idx_off[s_avi.frames] = off;
    s_avi.idx_len[s_avi.frames] = j->len;
    if (s_avi.frames == 0) {
        s_avi.t_first = j->t_us;
    }
    s_avi.t_last = j->t_us;
    s_avi.frames++;
    s_avi.chunk_bytes += avi_chunk_size(j->len);
    if (j->len > s_avi.max_chunk) {
        s_avi.max_chunk = j->len;
    }
    return true;
}

static void sd_task(void *arg)
{
    (void)arg;
    bool warned = false;
    int64_t last_free_us = 0;
    for (;;) {
        sd_job_t j;
        if (xQueueReceive(s_sd_q, &j, pdMS_TO_TICKS(1000)) == pdTRUE) {
            switch (j.kind) {
            case JOB_CLIP_OPEN:
                if (!s_sd_ok) {
                    s_clip_err = true;
                } else if (!avi_open(&j)) {
                    avi_close();
                    sd_drop("loi mo clip");
                }
                break;
            case JOB_CLIP_FRAME:
                if (!s_sd_ok) {
                    s_clip_drop++;
                } else if (!avi_frame(&j)) {
                    avi_close();
                    sd_drop("loi ghi clip");
                }
                heap_caps_free(j.buf);
                break;
            case JOB_CLIP_CLOSE:
                if (!avi_close() && s_sd_ok) {
                    sd_drop("loi dong clip");
                }
                break;
            default:
                if (s_sd_ok && !sd_write_job(&j)) {
                    sd_drop("loi ghi");
                }
                store_release(j.idx);
                break;
            }
        }
        int64_t now = esp_timer_get_time();
        if (!s_sd_ok) {
            if (now >= s_sd_next_try_us) {
                if (sd_mount()) {
                    s_sd_ok = true;
                    warned = false;
                    sd_ensure_space();
                    ESP_LOGI(TAG_SD, "Da gan the TF, con %u MB", (unsigned)s_sd_free_mb);
                } else {
                    if (!warned) {
                        ESP_LOGW(TAG_SD, "Khong co the - thu lai moi 30 s");
                        warned = true;
                    }
                    s_sd_next_try_us = now + SD_RETRY_US;
                }
            }
        } else if (now - last_free_us > 10000000LL) {
            last_free_us = now;
            uint64_t total = 0, freeb = 0;
            if (sd_info(&total, &freeb)) {
                s_sd_free_mb = (uint32_t)(freeb / (1024 * 1024));
            } else {
                sd_drop("mat the");
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Chuyen dong: doc khung da copy (khong goi esp_camera_fb_get)
// ---------------------------------------------------------------------------
typedef struct {
    int64_t boot_s;
    time_t wall;  // 0 neu chua co gio
    float pct;
    char file[56];  // rong neu khong luu the
    char clip[56];  // file .avi cua su kien (rong = khong co clip)
} event_t;

static event_t s_events[N_EVENTS];
static int s_ev_n;      // so su kien dang luu (<= N_EVENTS)
static int s_ev_head;   // vi tri ghi tiep theo
static SemaphoreHandle_t s_ev_mtx;
// Yeu cau ghi clip tu motion_task -> clip_task (bao ve boi s_ev_mtx)
static bool s_clip_pending;
static bool s_clip_active;          // clip_task dang ghi
static char s_clip_req_path[56];    // ten file clip cho yeu cau dang cho
static char s_clip_cur_path[56];    // ten file clip dang ghi
static uint8_t *s_ev_jpg;
static size_t s_ev_cap, s_ev_len;

static void event_record(int idx, float pct)
{
    int64_t boot_s = (esp_timer_get_time() - s_boot_us) / 1000000;
    time_t now = time(NULL);
    bool tok = time_ok();
    event_t ev;
    memset(&ev, 0, sizeof(ev));
    ev.boot_s = boot_s;
    ev.wall = tok ? now : 0;
    ev.pct = pct;

    char path[56] = "";
    char cpath[56] = "";
    if (tok) {
        struct tm tmv;
        localtime_r(&now, &tmv);
        strftime(path, sizeof(path), SD_DIR "/%Y%m%d/%H%M%S.jpg", &tmv);
        strftime(cpath, sizeof(cpath), SD_DIR "/%Y%m%d/%H%M%S.avi", &tmv);
    } else {
        snprintf(path, sizeof(path), SD_DIR "/boot/%" PRId64 ".jpg", boot_s);
        snprintf(cpath, sizeof(cpath), SD_DIR "/boot/%" PRId64 ".avi", boot_s);
    }
    if (g_clip.clip && s_sd_ok) {  // yeu cau ghi clip (moi) hoac keo dai clip dang ghi
        xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
        snprintf(s_clip_req_path, sizeof(s_clip_req_path), "%s", cpath);
        snprintf(ev.clip, sizeof(ev.clip), "%s", s_clip_active ? s_clip_cur_path : s_clip_req_path);
        s_clip_pending = true;
        xSemaphoreGive(s_ev_mtx);
    }

    // ban sao JPEG cua su kien (PSRAM, thay ban cu)
    xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
    if (s_ev_cap < s_slots[idx].len) {
        size_t ncap = s_slots[idx].len + s_slots[idx].len / 8 + 1024;
        uint8_t *nb = heap_caps_malloc(ncap, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (nb != NULL) {
            heap_caps_free(s_ev_jpg);
            s_ev_jpg = nb;
            s_ev_cap = ncap;
        }
    }
    if (s_ev_cap >= s_slots[idx].len) {
        memcpy(s_ev_jpg, s_slots[idx].buf, s_slots[idx].len);
        s_ev_len = s_slots[idx].len;
    }
    xSemaphoreGive(s_ev_mtx);

    // gui task ghi the (giu them 1 tham chieu khung, task the se nha)
    bool queued = false;
    if (s_sd_ok) {
        sd_job_t j;
        memset(&j, 0, sizeof(j));
        j.kind = JOB_JPEG;
        j.idx = idx;
        snprintf(j.path, sizeof(j.path), "%s", path);
        xSemaphoreTake(s_store_mtx, portMAX_DELAY);
        s_slots[idx].refs++;
        xSemaphoreGive(s_store_mtx);
        if (xQueueSend(s_sd_q, &j, 0) == pdTRUE) {
            queued = true;
        } else {
            store_release(idx);
        }
    }
    if (queued) {
        snprintf(ev.file, sizeof(ev.file), "%s", path);
    }

    xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
    s_events[s_ev_head] = ev;
    s_ev_head = (s_ev_head + 1) % N_EVENTS;
    if (s_ev_n < N_EVENTS) {
        s_ev_n++;
    }
    xSemaphoreGive(s_ev_mtx);
    s_motion_last_us = esp_timer_get_time();
    s_motion_count++;
}

static inline int gray565(uint16_t v)
{
    return (((v >> 11) & 31) * 8 * 77 + ((v >> 5) & 63) * 4 * 150 + (v & 31) * 8 * 29) >> 8;
}

static void motion_task(void *arg)
{
    (void)arg;
    uint16_t *rgb = heap_caps_malloc(MOT_PIX_MAX * 2, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    uint16_t *bg = heap_caps_malloc(MOT_PIX_MAX * 2, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (rgb == NULL || bg == NULL) {
        ESP_LOGE(TAG_MOT, "Het PSRAM - tat phat hien chuyen dong");
        vTaskDelete(NULL);
        return;
    }
    uint32_t last_seq = 0;
    int hits = 0, warm = 0, bw = 0, bh = 0;
    int64_t cool_until = 0;
    bool was_on = false;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(MOTION_PERIOD_MS));
        if (!g_cfg.motion || s_ota_busy) {
            was_on = false;
            continue;
        }
        if (!was_on) {
            was_on = true;
            bw = 0;
            bh = 0;
            hits = 0;
            warm = 0;
        }
        int idx = -1;
        if (!store_acquire(last_seq, 0, &idx)) {
            continue;
        }
        last_seq = s_slots[idx].seq;
        const uint8_t *jb = s_slots[idx].buf;
        size_t jl = s_slots[idx].len;

        esp_jpeg_image_cfg_t ic = {
            .indata = (uint8_t *)jb,
            .indata_size = jl,
            .out_format = JPEG_IMAGE_FORMAT_RGB565,
            .out_scale = JPEG_IMAGE_SCALE_1_8,
        };
        esp_jpeg_image_output_t io;
        memset(&io, 0, sizeof(io));
        int w = 0, h = 0;
        if (esp_jpeg_get_image_info(&ic, &io) == ESP_OK) {
            w = io.width / 8;  // get_image_info tra kich thuoc goc; giai ma 1/8 cho (rong/8) x (cao/8)
            h = io.height / 8;
        }
        bool ok = w > 0 && h > 0 && (w * h) <= MOT_PIX_MAX && jpg2rgb565(jb, jl, (uint8_t *)rgb, JPG_SCALE_8X);
        if (!ok) {
            static int fails;
            if (fails++ % 20 == 0) {
                ESP_LOGW(TAG_MOT, "Khong giai ma duoc khung (%dx%d, %u byte)", w, h, (unsigned)jl);
            }
            store_release(idx);
            continue;
        }
        int n = w * h;
        if (w != bw || h != bh) {  // moi bat hoac doi do phan giai: lap nen moi
            for (int i = 0; i < n; i++) {
                bg[i] = (uint16_t)(gray565(rgb[i]) << 4);
            }
            bw = w;
            bh = h;
            hits = 0;
            warm = 2;
            store_release(idx);
            continue;
        }
        int thr = g_cfg.motion_thr;
        int cnt = 0;
        for (int i = 0; i < n; i++) {
            int g = gray565(rgb[i]);
            int d = g - (bg[i] >> 4);
            if (d < 0) {
                d = -d;
            }
            if (d > thr) {
                cnt++;
            }
            bg[i] = (uint16_t)((int)bg[i] + (((g << 4) - (int)bg[i]) >> 4));  // nen troi cham
        }
        float pct = 100.0f * (float)cnt / (float)n;
        int64_t now = esp_timer_get_time();
        if (warm > 0) {
            warm--;
            hits = 0;
        } else if (now < cool_until) {
            hits = 0;
        } else if (pct > (float)g_cfg.motion_pct) {
            hits++;
            if (hits >= 2) {
                hits = 0;
                cool_until = now + MOTION_COOLDOWN_US;
                ESP_LOGI(TAG_MOT, "%.1f%%", (double)pct);
                event_record(idx, pct);
            }
        } else {
            hits = 0;
        }
        store_release(idx);
    }
}

// ---------------------------------------------------------------------------
// Clip: bo dem truoc su kien (PSRAM) + dieu khien ghi. Task nay KHONG goi esp_camera_fb_get;
// doc khung moi nhat da copy, chep sang ban rieng, chuyen cho task sd qua queue.
// ---------------------------------------------------------------------------
typedef struct {
    uint8_t *buf;
    uint32_t len;
    int64_t t_us;
    uint32_t w, h;
} ring_e_t;

static ring_e_t s_ring[CLIP_RING_MAX];
static int s_ring_head;  // phan tu cu nhat
static int s_ring_n;
static size_t s_ring_bytes;

static void ring_drop_oldest(void)
{
    if (s_ring_n == 0) {
        return;
    }
    heap_caps_free(s_ring[s_ring_head].buf);
    s_ring_bytes -= s_ring[s_ring_head].len;
    s_ring_head = (s_ring_head + 1) % CLIP_RING_MAX;
    s_ring_n--;
}

static void ring_clear(void)
{
    while (s_ring_n > 0) {
        ring_drop_oldest();
    }
    s_ring_head = 0;
}

static void ring_push(const ring_e_t *e)
{
    if (s_ring_n == CLIP_RING_MAX) {
        ring_drop_oldest();
    }
    s_ring[(s_ring_head + s_ring_n) % CLIP_RING_MAX] = *e;
    s_ring_n++;
    s_ring_bytes += e->len;
}

// Dong clip dang ghi (gui CLOSE cho task sd; thu lai neu queue day)
static void clip_end(bool *rec)
{
    sd_job_t j;
    memset(&j, 0, sizeof(j));
    j.kind = JOB_CLIP_CLOSE;
    for (int i = 0; i < 3; i++) {
        if (xQueueSend(s_sd_q, &j, pdMS_TO_TICKS(1000)) == pdTRUE) {
            break;
        }
    }
    *rec = false;
    xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
    s_clip_active = false;
    xSemaphoreGive(s_ev_mtx);
}

static void clip_send_frame(uint8_t *buf, uint32_t len, int64_t t_us, TickType_t wait)
{
    sd_job_t j;
    memset(&j, 0, sizeof(j));
    j.kind = JOB_CLIP_FRAME;
    j.buf = buf;
    j.len = len;
    j.t_us = t_us;
    if (xQueueSend(s_sd_q, &j, wait) != pdTRUE) {
        heap_caps_free(buf);
        s_clip_drop++;
    }
}

static void clip_task(void *arg)
{
    (void)arg;
    uint32_t last_seq = 0;
    bool rec = false;
    int64_t rec_start = 0, last_mo = 0;

    for (;;) {
        int cf = g_clip.clip_fps;
        vTaskDelay(pdMS_TO_TICKS(1000 / (cf < 1 ? 1 : cf)));
        bool armed = g_cfg.motion && g_clip.clip && s_sd_ok && !s_ota_busy;
        if (!armed) {
            if (rec) {
                clip_end(&rec);
            }
            ring_clear();
            xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
            s_clip_pending = false;
            xSemaphoreGive(s_ev_mtx);
            continue;
        }
        if (rec && s_clip_err) {  // task sd bao loi/huy clip
            clip_end(&rec);
        }
        int idx = -1;
        if (!store_acquire(last_seq, 0, &idx)) {
            continue;
        }
        last_seq = s_slots[idx].seq;
        uint32_t len = (uint32_t)s_slots[idx].len;
        int64_t t_us = s_slots[idx].t_us;
        uint8_t *cp = heap_caps_malloc(len, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (cp != NULL) {
            memcpy(cp, s_slots[idx].buf, len);
        }
        store_release(idx);
        if (cp == NULL) {
            continue;
        }
        int64_t now = esp_timer_get_time();

        if (rec) {
            clip_send_frame(cp, len, t_us, 0);  // queue day -> bo khung, khong chan
            xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
            if (s_clip_pending) {  // chuyen dong moi: keo dai clip
                s_clip_pending = false;
                last_mo = now;
            }
            xSemaphoreGive(s_ev_mtx);
            if (now - last_mo > (int64_t)g_clip.post_s * 1000000LL ||
                now - rec_start > (int64_t)CLIP_MAX_S * 1000000LL) {
                clip_end(&rec);
            }
            continue;
        }

        ring_e_t e = {.buf = cp, .len = len, .t_us = t_us, .w = 0, .h = 0};
        if (!avi_jpeg_dims(cp, len, &e.w, &e.h)) {
            e.w = 0;
            e.h = 0;
        }
        ring_push(&e);
        while (s_ring_n > 1 && (s_ring[(s_ring_head + s_ring_n - 1) % CLIP_RING_MAX].t_us - s_ring[s_ring_head].t_us >
                                    (int64_t)g_clip.pre_s * 1000000LL ||
                                s_ring_bytes > CLIP_RING_BYTES)) {
            ring_drop_oldest();
        }

        char path[56] = "";
        bool pend = false;
        xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
        if (s_clip_pending) {
            pend = true;
            s_clip_pending = false;
            snprintf(path, sizeof(path), "%s", s_clip_req_path);
        }
        xSemaphoreGive(s_ev_mtx);
        if (!pend) {
            continue;
        }
        uint32_t w = 0, h = 0;
        for (int k = 0; k < s_ring_n; k++) {
            const ring_e_t *r = &s_ring[(s_ring_head + k) % CLIP_RING_MAX];
            if (r->w > 0 && r->h > 0) {
                w = r->w;
                h = r->h;
            }
        }
        if (w == 0) {
            ESP_LOGW(TAG_SD, "Khong doc duoc kich thuoc JPEG - bo clip");
            continue;
        }
        sd_job_t j;
        memset(&j, 0, sizeof(j));
        j.kind = JOB_CLIP_OPEN;
        snprintf(j.path, sizeof(j.path), "%s", path);
        j.w = w;
        j.h = h;
        j.fps = (uint32_t)g_clip.clip_fps;
        s_clip_err = false;
        if (xQueueSend(s_sd_q, &j, pdMS_TO_TICKS(1000)) != pdTRUE) {
            s_clip_drop++;
            continue;
        }
        // khung truoc su kien -> task sd (so huu bo nho chuyen sang queue)
        int n = s_ring_n, head = s_ring_head;
        s_ring_n = 0;
        s_ring_head = 0;
        s_ring_bytes = 0;
        for (int k = 0; k < n; k++) {
            ring_e_t *r = &s_ring[(head + k) % CLIP_RING_MAX];
            clip_send_frame(r->buf, r->len, r->t_us, pdMS_TO_TICKS(1000));
            r->buf = NULL;
        }
        rec = true;
        rec_start = now;
        last_mo = now;
        xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
        snprintf(s_clip_cur_path, sizeof(s_clip_cur_path), "%s", path);
        s_clip_active = true;
        xSemaphoreGive(s_ev_mtx);
        ESP_LOGI(TAG_SD, "Bat dau ghi clip %s (truoc %d khung)", path, n);
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
    bool clip_armed = g_cfg.motion && g_clip.clip && s_sd_ok;
    int need = clip_armed && g_clip.clip_fps > MOTION_FPS ? g_clip.clip_fps : MOTION_FPS;
    if (s_viewers <= 0 && s_cap_waiters <= 0) {
        f = need;  // chi chay vi phat hien chuyen dong / ghi clip
    } else if (g_cfg.motion && f < need) {
        f = need;
    }
    if (s_nong && f > HOT_FPS) {
        f = HOT_FPS;  // nong: ha fps (ca khi ghi clip)
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

// Camera ngu (log "[CAM] Camera ngu"): dung XCLK + DMA that su. Goi khi giu s_cam_mtx.
static void camera_sleep_locked(void)
{
    esp_camera_deinit();
    s_cam_sleep = true;
    ESP_LOGI(TAG, "Camera ngu (khong ai dung %d s)", CAM_IDLE_SLEEP_S);
}

// Danh thuc camera: init lai theo cau hinh da luu. Goi khi giu s_cam_mtx.
static void camera_wake_locked(void)
{
    esp_err_t e = camera_init_hw();
    if (e == ESP_OK) {
        sensor_apply();  // ap framesize/cai dat da doi luc ngu, bo 3 khung dau
        s_cam_ok = true;
        ESP_LOGI(TAG, "Camera thuc");
    } else {
        s_cam_ok = false;  // watchdog NULL > 3 s se init lai
        ESP_LOGE(TAG, "Camera thuc that bai: 0x%x", (unsigned)e);
    }
    s_cam_sleep = false;
}

// Task DUY NHAT lay khung tu camera.
static void cam_task(void *arg)
{
    (void)arg;
    bool was_idle = true;
    int64_t next_us = 0;
    int64_t null_since = 0;
    int64_t idle_since = esp_timer_get_time();

    for (;;) {
        if (s_viewers <= 0 && s_cap_waiters <= 0 && !g_cfg.motion) {
            was_idle = true;
            null_since = 0;
            if (!s_cam_sleep && s_cam_ok && !s_ota_busy &&
                esp_timer_get_time() - idle_since >= (int64_t)CAM_IDLE_SLEEP_S * 1000000LL) {
                xSemaphoreTake(s_cam_mtx, portMAX_DELAY);
                if (s_viewers <= 0 && s_cap_waiters <= 0 && !g_cfg.motion) {
                    camera_sleep_locked();
                }
                xSemaphoreGive(s_cam_mtx);
            }
            ulTaskNotifyTake(pdTRUE, pdMS_TO_TICKS(200));
            continue;
        }
        idle_since = esp_timer_get_time();
        if (s_cam_sleep) {
            xSemaphoreTake(s_cam_mtx, portMAX_DELAY);
            camera_wake_locked();
            xSemaphoreGive(s_cam_mtx);
            was_idle = true;
            null_since = 0;
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
        camera_fb_t *fb = (s_cam_ok && !s_cam_sleep) ? esp_camera_fb_get() : NULL;
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
// Mang: tat AP khi da vao Wi-Fi nha, modem sleep khi khong ai xem
// ---------------------------------------------------------------------------
static void net_task(void *arg)
{
    (void)arg;
    int64_t conn_since = 0;  // 0 = dang khong co IP
    int64_t disc_since = 0;  // 0 = dang co IP (chi dung khi AP tat)
    int ps_cur = -1;         // -1 chua dat, 0 = NONE, 1 = MIN_MODEM

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(500));
        int64_t now = esp_timer_get_time();
        bool connected = wifi_nha_sta_connected();
        bool configured = wifi_nha_configured();

        if (s_ap_on) {
            if (connected) {
                if (conn_since == 0) {
                    conn_since = now;
                }
                if (now - conn_since >= (int64_t)AP_OFF_DELAY_S * 1000000LL) {
                    esp_err_t e = esp_wifi_set_mode(WIFI_MODE_STA);
                    if (e == ESP_OK) {
                        s_ap_on = false;
                        ps_cur = -1;
                        disc_since = 0;
                        ESP_LOGI(TAG, "Da vao Wi-Fi nha %d s - tat AP", AP_OFF_DELAY_S);
                    } else {
                        ESP_LOGW(TAG, "Tat AP loi: %s", esp_err_to_name(e));
                        conn_since = now;
                    }
                }
            } else {
                conn_since = 0;
            }
        } else {
            if (connected && configured) {
                disc_since = 0;
            } else {
                if (disc_since == 0) {
                    disc_since = now;
                }
                if (!configured || now - disc_since >= (int64_t)AP_BACK_DELAY_S * 1000000LL) {
                    esp_err_t e = esp_wifi_set_mode(WIFI_MODE_APSTA);
                    if (e == ESP_OK) {
                        s_ap_on = true;
                        s_ps_none = true;
                        conn_since = 0;
                        ESP_LOGI(TAG, "Mat Wi-Fi nha - bat lai AP");
                    } else {
                        ESP_LOGW(TAG, "Bat lai AP loi: %s", esp_err_to_name(e));
                        disc_since = now;
                    }
                }
            }
        }

        if (!s_ap_on) {  // modem sleep chi dung duoc o che do STA
            int want = (s_viewers > 0) ? 0 : 1;
            if (want != ps_cur) {
                esp_err_t e = (want == 0) ? esp_wifi_set_ps(WIFI_PS_NONE) : esp_wifi_set_ps(WIFI_PS_MIN_MODEM);
                if (e == ESP_OK) {
                    ps_cur = want;
                    s_ps_none = (want == 0);
                } else {
                    ESP_LOGW(TAG, "esp_wifi_set_ps loi: %s", esp_err_to_name(e));
                }
            }
        }
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
    bool marked = false;

    for (;;) {
        vTaskDelay(pdMS_TO_TICKS(2000));
        if (!marked && s_cam_ok && (esp_timer_get_time() - s_boot_us) > 30 * 1000000LL) {
            marked = true;  // chay on 30 s va camera OK: bo rollback
            esp_err_t e = esp_ota_mark_app_valid_cancel_rollback();
            ESP_LOGI(TAG_OTA, "Danh dau ban hop le (%s)", esp_err_to_name(e));
        }
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
    const esp_partition_t *running = esp_ota_get_running_partition();
    static char buf[2304];  // chi 1 handler cong 80 chay 1 luc (server don luong)
    int n = snprintf(buf, sizeof(buf),
        "{\"version\":\"" CAM_VERSION "\",\"uptime_s\":%" PRId64 ",\"nhiet_do_chip\":%.1f,\"nong\":%s,"
        "\"fps_cai\":%d,\"fps_thuc\":%.1f,\"so_nguoi_xem\":%d,\"framesize\":\"%s\",\"quality\":%d,"
        "\"vflip\":%d,\"hmirror\":%d,\"brightness\":%d,\"contrast\":%d,\"saturation\":%d,"
        "\"aec\":%d,\"ae_level\":%d,\"rotate\":%d,\"heap_free\":%u,\"psram_free\":%u,\"frame_loi\":%u,"
        "\"cam_reinit\":%u,\"cam_ok\":%s,%s,\"ap_ssid\":\"%s\","
        "\"ota_partition\":\"%s\",\"sd_ok\":%s,\"sd_free_mb\":%u,\"time_ok\":%s,\"motion\":%d,"
        "\"motion_thr\":%d,\"motion_pct\":%d,\"motion_count\":%u,\"motion_last_s\":%d,"
        "\"cam_sleep\":%s,\"ap_on\":%s,\"wifi_ps\":\"%s\","
        "\"clip\":%d,\"clip_fps\":%d,\"pre_s\":%d,\"post_s\":%d,\"clip_rec\":%s,\"clip_count\":%u,\"clip_drop\":%u}",
        (esp_timer_get_time() - s_boot_us) / 1000000, (double)s_temp, s_nong ? "true" : "false",
        g_cfg.fps, (double)s_fps_thuc, (int)s_viewers, fs_name(g_cfg.framesize), g_cfg.quality,
        g_cfg.vflip, g_cfg.hmirror, g_cfg.brightness, g_cfg.contrast, g_cfg.saturation,
        g_cfg.aec, g_cfg.ae_level, g_cfg.rotate, (unsigned)esp_get_free_heap_size(),
        (unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM), (unsigned)s_frame_loi,
        (unsigned)s_cam_reinit, s_cam_ok ? "true" : "false", nha, s_ap_ssid,
        running != NULL ? running->label : "?", s_sd_ok ? "true" : "false", (unsigned)(s_sd_ok ? s_sd_free_mb : 0),
        time_ok() ? "true" : "false", g_cfg.motion, g_cfg.motion_thr, g_cfg.motion_pct,
        (unsigned)s_motion_count,
        s_motion_last_us < 0 ? -1 : (int)((esp_timer_get_time() - s_motion_last_us) / 1000000),
        s_cam_sleep ? "true" : "false", s_ap_on ? "true" : "false", s_ps_none ? "none" : "min_modem",
        g_clip.clip, g_clip.clip_fps, g_clip.pre_s, g_clip.post_s, s_clip_rec ? "true" : "false",
        (unsigned)s_clip_count, (unsigned)s_clip_drop);
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

    if (strcmp(var, "clip") == 0 || strcmp(var, "clip_fps") == 0 || strcmp(var, "pre_s") == 0 ||
        strcmp(var, "post_s") == 0) {
        clip_cfg_t nc = g_clip;
        if (strcmp(var, "clip") == 0) {
            nc.clip = val;
        } else if (strcmp(var, "clip_fps") == 0) {
            nc.clip_fps = val;
        } else if (strcmp(var, "pre_s") == 0) {
            nc.pre_s = val;
        } else {
            nc.post_s = val;
        }
        if (!clip_valid(&nc)) {
            return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "gia tri ngoai khoang cho phep");
        }
        g_clip = nc;
        clip_save();
        cam_wake();
        httpd_resp_set_type(req, "application/json");
        return httpd_resp_sendstr(req, "{\"ok\":1}");
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
    } else if (strcmp(var, "motion") == 0) {
        n.motion = val;
    } else if (strcmp(var, "motion_thr") == 0) {
        n.motion_thr = val;
    } else if (strcmp(var, "motion_pct") == 0) {
        n.motion_pct = val;
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
    if (s_cam_ok && !s_cam_sleep) {  // dang ngu: chi luu cau hinh, ap khi thuc
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
    if (strcmp(var, "motion") == 0) {
        cam_wake();
    }

    httpd_resp_set_type(req, "application/json");
    return httpd_resp_sendstr(req, "{\"ok\":1}");
}


static esp_err_t event_jpg_get(httpd_req_t *req)
{
    xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
    if (s_ev_len == 0) {
        xSemaphoreGive(s_ev_mtx);
        return httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "chua co su kien");
    }
    httpd_resp_set_type(req, "image/jpeg");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    esp_err_t r = httpd_resp_send(req, (const char *)s_ev_jpg, s_ev_len);
    xSemaphoreGive(s_ev_mtx);
    return r;
}

static esp_err_t events_get(httpd_req_t *req)
{
    static char buf[4608];  // server cong 80 don luong
    size_t o = 0;
    o += (size_t)snprintf(buf + o, sizeof(buf) - o, "[");
    xSemaphoreTake(s_ev_mtx, portMAX_DELAY);
    for (int k = 0; k < s_ev_n && o + 280 < sizeof(buf); k++) {
        int i = (s_ev_head - s_ev_n + k + 2 * N_EVENTS) % N_EVENTS;
        const event_t *e = &s_events[i];
        char t[32];
        if (e->wall != 0) {
            struct tm tmv;
            localtime_r(&e->wall, &tmv);
            strftime(t, sizeof(t), "%Y-%m-%d %H:%M:%S", &tmv);
        } else {
            snprintf(t, sizeof(t), "boot+%" PRId64 "s", e->boot_s);
        }
        o += (size_t)snprintf(buf + o, sizeof(buf) - o, "%s{\"t\":\"%s\",\"pct\":%.1f,\"file\":",
                              k ? "," : "", t, (double)e->pct);
        if (e->file[0] != '\0') {
            o += (size_t)snprintf(buf + o, sizeof(buf) - o, "\"%s\",\"clip\":", e->file);
        } else {
            o += (size_t)snprintf(buf + o, sizeof(buf) - o, "null,\"clip\":");
        }
        if (e->clip[0] != '\0') {
            o += (size_t)snprintf(buf + o, sizeof(buf) - o, "\"%s\"}", e->clip);
        } else {
            o += (size_t)snprintf(buf + o, sizeof(buf) - o, "null}");
        }
    }
    xSemaphoreGive(s_ev_mtx);
    o += (size_t)snprintf(buf + o, sizeof(buf) - o, "]");
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_send(req, buf, o);
}

static bool sd_path_ok(const char *f)
{
    size_t n = strlen(f);
    if (n == 0 || n > 60 || f[0] == '/' || strstr(f, "..") != NULL) {
        return false;
    }
    bool is_jpg = n > 4 && strcmp(f + n - 4, ".jpg") == 0;
    bool is_avi = n > 4 && strcmp(f + n - 4, ".avi") == 0;
    if (!is_jpg && !is_avi) {
        return false;  // chi cho xem .jpg va .avi
    }
    for (size_t i = 0; i < n; i++) {
        char c = f[i];
        bool good = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') ||
                    c == '.' || c == '/' || c == '-' || c == '_';
        if (!good) {
            return false;
        }
    }
    return true;
}

static esp_err_t sd_get(httpd_req_t *req)
{
    char query[96];
    char f[72];
    if (httpd_req_get_url_query_str(req, query, sizeof(query)) != ESP_OK ||
        httpd_query_key_value(query, "f", f, sizeof(f)) != ESP_OK || !sd_path_ok(f)) {
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "duong dan khong hop le");
    }
    if (!s_sd_ok) {
        httpd_resp_set_status(req, "503 Service Unavailable");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Chua co the TF");
    }
    char full[112];
    if (strncmp(f, SD_DIR "/", strlen(SD_DIR) + 1) == 0) {
        snprintf(full, sizeof(full), SD_MOUNT "/%s", f);
    } else {
        snprintf(full, sizeof(full), SD_MOUNT "/" SD_DIR "/%s", f);
    }
    FILE *fp = fopen(full, "rb");
    if (fp == NULL) {
        return httpd_resp_send_err(req, HTTPD_404_NOT_FOUND, "khong co file");
    }
    char *chunk = malloc(8192);
    if (chunk == NULL) {
        fclose(fp);
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "het bo nho");
    }
    size_t fl = strlen(f);
    httpd_resp_set_type(req, strcmp(f + fl - 4, ".avi") == 0 ? "video/x-msvideo" : "image/jpeg");
    esp_err_t r = ESP_OK;
    size_t got;
    while (r == ESP_OK && (got = fread(chunk, 1, 8192, fp)) > 0) {  // file lon: gui theo khoi
        r = httpd_resp_send_chunk(req, chunk, got);
    }
    fclose(fp);
    free(chunk);
    if (r == ESP_OK) {
        r = httpd_resp_send_chunk(req, NULL, 0);
    }
    return r;
}

// ---------------------------------------------------------------------------
// OTA: POST /ota, body = .bin tho, header X-OTA-Key
// ---------------------------------------------------------------------------
static void ota_drain(httpd_req_t *req)
{
    char tmp[256];
    size_t left = req->content_len < 16384 ? req->content_len : 16384;
    while (left > 0) {
        int r = httpd_req_recv(req, tmp, left < sizeof(tmp) ? left : sizeof(tmp));
        if (r <= 0) {
            break;
        }
        left -= (size_t)r;
    }
}

static esp_err_t ota_post(httpd_req_t *req)
{
    char given[72] = "";
    size_t hl = httpd_req_get_hdr_value_len(req, "X-OTA-Key");
    bool auth = false;
    if (hl > 0 && hl < sizeof(given)) {
        if (httpd_req_get_hdr_value_str(req, "X-OTA-Key", given, sizeof(given)) == ESP_OK) {
            auth = ota_key_check(given);
        }
    }
    memset(given, 0, sizeof(given));
    if (!auth) {
        ota_drain(req);
        ESP_LOGW(TAG_OTA, "Tu choi: thieu/sai khoa hoac chua cai khoa");
        httpd_resp_set_status(req, "403 Forbidden");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Khoa OTA sai/thieu");
    }
    if (s_ota_busy) {
        httpd_resp_set_status(req, "409 Conflict");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Dang OTA");
    }
    size_t total = req->content_len;
    if (total == 0 || total > OTA_MAX_BYTES) {
        ota_drain(req);
        return httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "kich thuoc khong hop le (toi da 4 MB)");
    }
    const esp_partition_t *part = esp_ota_get_next_update_partition(NULL);
    if (part == NULL) {
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "khong co phan vung OTA");
    }
    s_ota_busy = true;
    ESP_LOGI(TAG_OTA, "Bat dau %u byte -> %s", (unsigned)total, part->label);
    esp_ota_handle_t oh = 0;
    esp_err_t e = esp_ota_begin(part, total, &oh);
    if (e != ESP_OK) {
        s_ota_busy = false;
        ESP_LOGE(TAG_OTA, "esp_ota_begin loi %s", esp_err_to_name(e));
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "khong bat dau duoc OTA");
    }
    char *buf = malloc(4096);
    if (buf == NULL) {
        esp_ota_abort(oh);
        s_ota_busy = false;
        return httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "het bo nho");
    }
    size_t got = 0;
    int timeouts = 0;
    int bad = 0;  // 0 ok, 400 anh hong, 500 loi khac
    while (got < total) {
        size_t want = total - got < 4096 ? total - got : 4096;
        int r = httpd_req_recv(req, buf, want);
        if (r == HTTPD_SOCK_ERR_TIMEOUT) {
            if (++timeouts > 4) {
                bad = 500;
                break;
            }
            continue;
        }
        if (r <= 0) {
            bad = 500;
            break;
        }
        timeouts = 0;
        e = esp_ota_write(oh, buf, (size_t)r);
        if (e != ESP_OK) {
            bad = (e == ESP_ERR_OTA_VALIDATE_FAILED) ? 400 : 500;
            break;
        }
        got += (size_t)r;
    }
    free(buf);
    if (bad == 0) {
        e = esp_ota_end(oh);
        if (e != ESP_OK) {
            bad = (e == ESP_ERR_OTA_VALIDATE_FAILED) ? 400 : 500;
        }
    } else {
        esp_ota_abort(oh);
    }
    if (bad == 0) {
        e = esp_ota_set_boot_partition(part);
        if (e != ESP_OK) {
            bad = 500;
        }
    }
    if (bad != 0) {
        s_ota_busy = false;
        ESP_LOGE(TAG_OTA, "That bai (%s) sau %u byte - giu ban cu", esp_err_to_name(e), (unsigned)got);
        return httpd_resp_send_err(req, bad == 400 ? HTTPD_400_BAD_REQUEST : HTTPD_500_INTERNAL_SERVER_ERROR,
                                   bad == 400 ? "anh firmware hong" : "loi ghi OTA");
    }
    ESP_LOGI(TAG_OTA, "Xong %u byte - khoi dong lai", (unsigned)got);
    httpd_resp_set_type(req, "text/plain");
    esp_err_t r = httpd_resp_sendstr(req, "OK, khoi dong lai");
    vTaskDelay(pdMS_TO_TICKS(500));
    esp_restart();
    return r;
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
    cfg.max_uri_handlers = 12;
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
        {.uri = "/ota", .method = HTTP_POST, .handler = ota_post, .user_ctx = NULL},
        {.uri = "/event.jpg", .method = HTTP_GET, .handler = event_jpg_get, .user_ctx = NULL},
        {.uri = "/events", .method = HTTP_GET, .handler = events_get, .user_ctx = NULL},
        {.uri = "/sd", .method = HTTP_GET, .handler = sd_get, .user_ctx = NULL},
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
    if (start_server(c80, main_uris, sizeof(main_uris) / sizeof(main_uris[0])) == NULL) {
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
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, on_got_ip, NULL));
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
    s_ev_mtx = xSemaphoreCreateMutex();
    s_sd_q = xQueueCreate(SD_Q_LEN, sizeof(sd_job_t));
    setenv("TZ", "ICT-7", 1);
    tzset();

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    cfg_load();
    clip_load();

    temperature_sensor_config_t tc = TEMPERATURE_SENSOR_CONFIG_DEFAULT(-10, 80);
    if (temperature_sensor_install(&tc, &s_tsens) != ESP_OK || temperature_sensor_enable(s_tsens) != ESP_OK) {
        s_tsens = NULL;
        ESP_LOGW(TAG, "Khong doc duoc nhiet do chip");
    }

    // DFS 80-240 MHz, khong light sleep
    esp_pm_config_t pmc = {
        .max_freq_mhz = 240,
        .min_freq_mhz = 80,
        .light_sleep_enable = false,
    };
    esp_err_t pe = esp_pm_configure(&pmc);
    if (pe != ESP_OK) {
        ESP_LOGW(TAG, "esp_pm_configure loi: %s", esp_err_to_name(pe));
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
    xTaskCreate(net_task, "net", 3072, NULL, 3, NULL);
    xTaskCreate(sd_task, "sd", 6144, NULL, 3, NULL);
    xTaskCreate(motion_task, "motion", 8192, NULL, 3, NULL);
    xTaskCreate(clip_task, "clip", 4096, NULL, 3, NULL);
    ESP_LOGI(TAG, "STLab Cam " CAM_VERSION " chay");
}
