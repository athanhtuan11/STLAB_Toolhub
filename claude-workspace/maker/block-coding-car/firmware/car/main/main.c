// block-coding-car v0.1.0: web app tu flash + WebSocket /ws + thong dich chuong trinh khoi lenh.
// Giao thuc: maker/block-coding-car/protocol/PROTOCOL.md (muc 4-5). Phan cung: hardware/wiring.yaml.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_attr.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "esp_http_server.h"
#include "esp_ota_ops.h"
#include "esp_app_desc.h"
#include "nvs.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "cJSON.h"

#include "pins.h"
#include "prog.h"
#include "stepper.h"
#include "sound.h"
#include "eyes.h"
#include "batt.h"
#include "netcfg.h"

static const char *TAG = "car";

// ---- Hang so lay tu PROTOCOL.md muc 5 ----
#define DEFAULT_STEPS_CELL   4054   // buoc / o 150 mm
#define DEFAULT_STEPS_90     1698   // buoc moi banh de quay 90 do
#define CAL_CELL_MIN         1000
#define CAL_CELL_MAX         8000
#define CAL_90_MIN           500
#define CAL_90_MAX           4000
#define REST_MS              300    // nghi giua 2 buoc
#define BATT_RUN_REFUSE_MV   4400   // < 4400 mV tu choi run (batt_low)
#define BATT_RUN_STOP_MV     4200   // dang chay < 4200 mV lien tuc 2 s -> dung
#define BATT_STOP_HOLD_MS    2000
#define BATT_REPORT_MS       5000
#define BTN_DEBOUNCE_MS      30
#define WS_MAX_LEN           2048
#define OTA_MAX_BYTES        0x400000   // slot OTA 4 MB

extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[] asm("_binary_index_html_gz_end");

typedef struct {
    int n;
    prog_step_t steps[PROG_MAX_STEPS];
} job_t;

static httpd_handle_t s_server = NULL;
static SemaphoreHandle_t s_send_lock = NULL;
static QueueHandle_t s_run_q = NULL;
static TaskHandle_t s_btn_task = NULL;
static volatile bool s_busy = false;
static volatile bool s_ota_busy = false;
static const char *volatile s_stop_why = NULL;
static int s_steps_cell = DEFAULT_STEPS_CELL;
static int s_steps_90 = DEFAULT_STEPS_90;

// ---------------------------------------------------------------------------
// Gui thong diep ws
// ---------------------------------------------------------------------------
static void send_one(int fd, const char *txt)
{
    httpd_ws_frame_t f;
    memset(&f, 0, sizeof(f));
    f.type = HTTPD_WS_TYPE_TEXT;
    f.payload = (uint8_t *)txt;
    f.len = strlen(txt);
    f.final = true;
    httpd_ws_send_frame_async(s_server, fd, &f);
}

// fd >= 0: gui 1 client; fd < 0: gui moi client ws dang noi
static void ws_send(int fd, const char *txt)
{
    if (s_server == NULL) {
        return;
    }
    xSemaphoreTake(s_send_lock, portMAX_DELAY);
    if (fd >= 0) {
        send_one(fd, txt);
    } else {
        int fds[16];
        size_t n = sizeof(fds) / sizeof(fds[0]);
        if (httpd_get_client_list(s_server, &n, fds) == ESP_OK) {
            for (size_t i = 0; i < n; i++) {
                if (httpd_ws_get_fd_info(s_server, fds[i]) == HTTPD_WS_CLIENT_WEBSOCKET) {
                    send_one(fds[i], txt);
                }
            }
        }
    }
    xSemaphoreGive(s_send_lock);
}

static int jt(char *b, size_t n, const char *type)
{
    return snprintf(b, n, "{\"t\":\"%s\"", type);
}

static const char *err_msg(const char *code)
{
    if (strcmp(code, "busy") == 0) {
        return "Xe đang chạy chương trình khác.";
    }
    if (strcmp(code, "batt_low") == 0) {
        return "Pin yếu, hãy thay pin mới.";
    }
    if (strcmp(code, "bad_msg") == 0) {
        return "Thông điệp không hợp lệ.";
    }
    if (strcmp(code, "bad_json") == 0) {
        return "Chương trình bị hỏng.";
    }
    if (strcmp(code, "bad_version") == 0) {
        return "Phiên bản chương trình không đúng.";
    }
    if (strcmp(code, "empty") == 0) {
        return "Chương trình đang trống.";
    }
    if (strcmp(code, "bad_op") == 0) {
        return "Có khối lệnh lạ.";
    }
    if (strcmp(code, "bad_arg") == 0) {
        return "Có khối lệnh sai số hoặc thiếu số.";
    }
    if (strcmp(code, "dup_id") == 0) {
        return "Có hai khối trùng số hiệu.";
    }
    if (strcmp(code, "nested_repeat") == 0) {
        return "Không đặt khối lặp trong khối lặp.";
    }
    if (strcmp(code, "empty_repeat") == 0) {
        return "Khối lặp đang trống.";
    }
    if (strcmp(code, "too_many_blocks") == 0) {
        return "Quá nhiều khối lệnh.";
    }
    return "Lỗi không rõ.";
}

static void send_err(int fd, const char *code)
{
    char b[256];
    int o = jt(b, sizeof(b), "err");
    snprintf(b + o, sizeof(b) - (size_t)o, ",\"code\":\"%s\",\"msg\":\"%s\"}", code, err_msg(code));
    ws_send(fd, b);
}

static const char *fw_version(void)
{
    return esp_app_get_description()->version;
}

static void build_hello(char *b, size_t n)
{
    int o = jt(b, n, "hello");
    snprintf(b + o, n - (size_t)o,
             ",\"name\":\"%s\",\"color\":\"%s\",\"fw\":\"%s\",\"batt_mv\":%d,\"busy\":%s,\"steps_cell\":%d,\"steps_90\":%d}",
             netcfg_name(), netcfg_color(), fw_version(), batt_mv(), s_busy ? "true" : "false", s_steps_cell,
             s_steps_90);
}

// ---------------------------------------------------------------------------
// Dung xe
// ---------------------------------------------------------------------------
// why: "client" | "button" | "batt". Dang chay -> huy, runner se gui `stopped`; ranh -> nha cuon + bao ngay.
static void request_stop(const char *why)
{
    if (s_busy) {
        if (s_stop_why == NULL) {
            s_stop_why = why;
        }
        stepper_abort();
        sound_stop();
        return;
    }
    stepper_release();
    sound_stop();
    char b[96];
    int o = jt(b, sizeof(b), "stopped");
    snprintf(b + o, sizeof(b) - (size_t)o, ",\"why\":\"%s\"}", why);
    ws_send(-1, b);
}

// ---------------------------------------------------------------------------
// Nut Dung: ngat GPIO + chong doi 30 ms
// ---------------------------------------------------------------------------
static void IRAM_ATTR btn_isr(void *arg)
{
    (void)arg;
    BaseType_t woken = pdFALSE;
    vTaskNotifyGiveFromISR(s_btn_task, &woken);
    if (woken == pdTRUE) {
        portYIELD_FROM_ISR();
    }
}

static void btn_task(void *arg)
{
    (void)arg;
    while (true) {
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        vTaskDelay(pdMS_TO_TICKS(BTN_DEBOUNCE_MS));
        if (gpio_get_level(PIN_BTN_STOP) == 0) {
            request_stop("button");
            while (gpio_get_level(PIN_BTN_STOP) == 0) {
                vTaskDelay(pdMS_TO_TICKS(20));
            }
            vTaskDelay(pdMS_TO_TICKS(BTN_DEBOUNCE_MS));
        }
        ulTaskNotifyTake(pdTRUE, 0);
    }
}

static void btn_init(void)
{
    gpio_config_t io;
    memset(&io, 0, sizeof(io));
    io.pin_bit_mask = 1ULL << PIN_BTN_STOP;
    io.mode = GPIO_MODE_INPUT;
    io.pull_up_en = GPIO_PULLUP_ENABLE;
    io.intr_type = GPIO_INTR_NEGEDGE;
    ESP_ERROR_CHECK(gpio_config(&io));
    xTaskCreate(btn_task, "btn", 3072, NULL, 10, &s_btn_task);
    ESP_ERROR_CHECK(gpio_install_isr_service(0));
    ESP_ERROR_CHECK(gpio_isr_handler_add(PIN_BTN_STOP, btn_isr, NULL));
}

// ---------------------------------------------------------------------------
// Chay chuong trinh
// ---------------------------------------------------------------------------
// Nghi REST_MS, ngat som neu co lenh dung. Tra false neu bi dung.
static bool rest(void)
{
    for (int t = 0; t < REST_MS; t += 20) {
        if (s_stop_why != NULL) {
            return false;
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
    return s_stop_why == NULL;
}

// Tra 0 neu xong buoc, -1 neu bi huy
static int run_step(const prog_step_t *s)
{
    switch (s->op) {
    case PROG_OP_FWD:
        return stepper_move(s->arg * s_steps_cell, s->arg * s_steps_cell);
    case PROG_OP_BACK:
        return stepper_move(-s->arg * s_steps_cell, -s->arg * s_steps_cell);
    case PROG_OP_LEFT:
        return stepper_move(-s_steps_90, s_steps_90);
    case PROG_OP_RIGHT:
        return stepper_move(s_steps_90, -s_steps_90);
    case PROG_OP_SOUND:
        sound_play(s->arg);
        return s_stop_why == NULL ? 0 : -1;
    case PROG_OP_EYE:
        eyes_set_program_color(s->arg);
        return 0;
    default:
        return -1;
    }
}

static void runner_task(void *arg)
{
    (void)arg;
    static job_t job;
    while (true) {
        if (xQueueReceive(s_run_q, &job, portMAX_DELAY) != pdTRUE) {
            continue;
        }
        for (int i = 0; i < job.n; i++) {
            if (s_stop_why != NULL) {
                break;
            }
            char b[64];
            int o = jt(b, sizeof(b), "step");
            snprintf(b + o, sizeof(b) - (size_t)o, ",\"i\":%d,\"id\":%d}", i, job.steps[i].id);
            ws_send(-1, b);
            if (run_step(&job.steps[i]) != 0) {
                break;
            }
            if (i + 1 < job.n && !rest()) {
                break;
            }
        }
        // Xong / dung / loi: luon nha cuon, tat loa, tra mau mat ve trang thai
        stepper_release();
        sound_stop();
        eyes_clear_program_color();
        const char *why = s_stop_why;
        s_busy = false;
        char b[64];
        if (why == NULL) {
            jt(b, sizeof(b), "done");
            strcat(b, "}");
        } else {
            int o = jt(b, sizeof(b), "stopped");
            snprintf(b + o, sizeof(b) - (size_t)o, ",\"why\":\"%s\"}", why);
        }
        ws_send(-1, b);
    }
}

// ---------------------------------------------------------------------------
// Xu ly thong diep ws
// ---------------------------------------------------------------------------
static bool get_int(const cJSON *item, int *v)
{
    if (!cJSON_IsNumber(item)) {
        return false;
    }
    double d = item->valuedouble;
    if (d < -1000000.0 || d > 1000000.0 || d != (double)(int)d) {
        return false;
    }
    *v = (int)d;
    return true;
}

static void on_run(int fd, const cJSON *root)
{
    static job_t job;   // chi task httpd goi ham nay (1 task) nen dung chung duoc
    const char *err = NULL;
    int n = prog_expand_array(cJSON_GetObjectItemCaseSensitive(root, "prog"), job.steps, PROG_MAX_STEPS, &err);
    if (n < 0) {
        send_err(fd, err);
        return;
    }
    if (s_busy || s_ota_busy) {
        send_err(fd, "busy");
        return;
    }
    if (batt_mv() < BATT_RUN_REFUSE_MV) {
        send_err(fd, "batt_low");
        return;
    }
    job.n = n;
    s_stop_why = NULL;
    stepper_clear_abort();
    s_busy = true;
    char b[64];
    int o = jt(b, sizeof(b), "started");
    snprintf(b + o, sizeof(b) - (size_t)o, ",\"n\":%d}", n);
    ws_send(-1, b);
    if (xQueueSend(s_run_q, &job, 0) != pdTRUE) {
        s_busy = false;
        stepper_release();
        send_err(fd, "busy");
    }
}

static void on_dry(int fd, const cJSON *root)
{
    prog_step_t steps[PROG_MAX_STEPS];
    const char *err = NULL;
    int n = prog_expand_array(cJSON_GetObjectItemCaseSensitive(root, "prog"), steps, PROG_MAX_STEPS, &err);
    if (n < 0) {
        send_err(fd, err);
        return;
    }
    char b[PROG_MAX_STEPS * 24 + 48];
    int o = jt(b, sizeof(b), "dry");
    o += snprintf(b + o, sizeof(b) - (size_t)o, ",\"steps\":[");
    for (int i = 0; i < n; i++) {
        o += snprintf(b + o, sizeof(b) - (size_t)o, "%s[%d,\"%s\",%d]", i > 0 ? "," : "", steps[i].id,
                      prog_op_name(steps[i].op), steps[i].arg);
    }
    snprintf(b + o, sizeof(b) - (size_t)o, "]}");
    ws_send(fd, b);
}

static void on_cal(int fd, const cJSON *root)
{
    int cell = 0;
    int s90 = 0;
    if (!get_int(cJSON_GetObjectItemCaseSensitive(root, "steps_cell"), &cell) ||
        !get_int(cJSON_GetObjectItemCaseSensitive(root, "steps_90"), &s90) || cell < CAL_CELL_MIN ||
        cell > CAL_CELL_MAX || s90 < CAL_90_MIN || s90 > CAL_90_MAX) {
        send_err(fd, "bad_msg");
        return;
    }
    if (s_busy) {
        send_err(fd, "busy");
        return;
    }
    nvs_handle_t h;
    esp_err_t e = nvs_open("car", NVS_READWRITE, &h);
    if (e == ESP_OK) {
        e = nvs_set_i32(h, "steps_cell", cell);
        if (e == ESP_OK) {
            e = nvs_set_i32(h, "steps_90", s90);
        }
        if (e == ESP_OK) {
            e = nvs_commit(h);
        }
        nvs_close(h);
    }
    if (e != ESP_OK) {
        ESP_LOGE(TAG, "luu cal loi: %s", esp_err_to_name(e));
        send_err(fd, "bad_msg");
        return;
    }
    s_steps_cell = cell;
    s_steps_90 = s90;
    char b[96];
    int o = jt(b, sizeof(b), "cal");
    snprintf(b + o, sizeof(b) - (size_t)o, ",\"steps_cell\":%d,\"steps_90\":%d}", cell, s90);
    ws_send(-1, b);
}

static void handle_msg(int fd, const char *text)
{
    cJSON *root = cJSON_Parse(text);
    const cJSON *jt_ = cJSON_IsObject(root) ? cJSON_GetObjectItemCaseSensitive(root, "t") : NULL;
    if (!cJSON_IsString(jt_) || jt_->valuestring == NULL) {
        send_err(fd, "bad_msg");
        cJSON_Delete(root);
        return;
    }
    const char *t = jt_->valuestring;
    if (strcmp(t, "hello") == 0) {
        char b[256];
        build_hello(b, sizeof(b));
        ws_send(fd, b);
    } else if (strcmp(t, "run") == 0) {
        on_run(fd, root);
    } else if (strcmp(t, "stop") == 0) {
        request_stop("client");
    } else if (strcmp(t, "dry") == 0) {
        on_dry(fd, root);
    } else if (strcmp(t, "cal") == 0) {
        on_cal(fd, root);
    } else {
        send_err(fd, "bad_msg");
    }
    cJSON_Delete(root);
}

static esp_err_t ws_handler(httpd_req_t *req)
{
    if (req->method == HTTP_GET) {
        return ESP_OK;   // bat tay ws xong
    }
    int fd = httpd_req_to_sockfd(req);
    httpd_ws_frame_t f;
    memset(&f, 0, sizeof(f));
    f.type = HTTPD_WS_TYPE_TEXT;
    esp_err_t e = httpd_ws_recv_frame(req, &f, 0);
    if (e != ESP_OK) {
        return e;
    }
    if (f.len == 0) {
        return ESP_OK;
    }
    if (f.len > WS_MAX_LEN) {
        send_err(fd, "bad_msg");
        return ESP_FAIL;
    }
    uint8_t *buf = (uint8_t *)calloc(1, f.len + 1);
    if (buf == NULL) {
        return ESP_ERR_NO_MEM;
    }
    f.payload = buf;
    e = httpd_ws_recv_frame(req, &f, f.len);
    if (e == ESP_OK) {
        if (f.type == HTTPD_WS_TYPE_TEXT) {
            handle_msg(fd, (const char *)buf);
        } else {
            send_err(fd, "bad_msg");
        }
    }
    free(buf);
    return e;
}

// ---------------------------------------------------------------------------
// HTTP: /, /info, /ota
// ---------------------------------------------------------------------------
static esp_err_t root_get(httpd_req_t *req)
{
    httpd_resp_set_type(req, "text/html; charset=utf-8");
    httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache");
    return httpd_resp_send(req, (const char *)index_html_gz_start, (ssize_t)(index_html_gz_end - index_html_gz_start));
}

static esp_err_t info_get(httpd_req_t *req)
{
    char b[256];
    build_hello(b, sizeof(b));
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_sendstr(req, b);
}

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

// POST /ota: body = .bin tho, header X-OTA-Key (khoa trong NVS, dat bang lenh UART OTAKEY)
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
        ESP_LOGW(TAG, "OTA tu choi: thieu/sai khoa hoac chua cai khoa");
        httpd_resp_set_status(req, "403 Forbidden");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Khoa OTA sai/thieu");
    }
    if (s_ota_busy || s_busy) {
        httpd_resp_set_status(req, "409 Conflict");
        httpd_resp_set_type(req, "text/plain");
        return httpd_resp_sendstr(req, "Xe dang ban");
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
    ESP_LOGI(TAG, "OTA bat dau %u byte -> %s", (unsigned)total, part->label);
    esp_ota_handle_t oh = 0;
    esp_err_t e = esp_ota_begin(part, total, &oh);
    if (e != ESP_OK) {
        s_ota_busy = false;
        ESP_LOGE(TAG, "esp_ota_begin loi %s", esp_err_to_name(e));
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
    int bad = 0;   // 0 ok, 400 anh hong, 500 loi khac
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
        ESP_LOGE(TAG, "OTA that bai (%s) sau %u byte - giu ban cu", esp_err_to_name(e), (unsigned)got);
        return httpd_resp_send_err(req, bad == 400 ? HTTPD_400_BAD_REQUEST : HTTPD_500_INTERNAL_SERVER_ERROR,
                                   bad == 400 ? "anh firmware hong" : "loi ghi OTA");
    }
    ESP_LOGI(TAG, "OTA xong %u byte - khoi dong lai", (unsigned)got);
    httpd_resp_set_type(req, "text/plain");
    esp_err_t r = httpd_resp_sendstr(req, "OK, khoi dong lai");
    vTaskDelay(pdMS_TO_TICKS(500));
    esp_restart();
    return r;
}

static void http_start(void)
{
    static const httpd_uri_t uris[] = {
        {.uri = "/", .method = HTTP_GET, .handler = root_get, .user_ctx = NULL},
        {.uri = "/info", .method = HTTP_GET, .handler = info_get, .user_ctx = NULL},
        {.uri = "/ota", .method = HTTP_POST, .handler = ota_post, .user_ctx = NULL},
        {.uri = "/ws", .method = HTTP_GET, .handler = ws_handler, .user_ctx = NULL, .is_websocket = true,
         .handle_ws_control_frames = false},
    };
    httpd_config_t c = HTTPD_DEFAULT_CONFIG();
    c.stack_size = 8192;
    c.max_uri_handlers = 8;
    c.lru_purge_enable = true;
    c.send_wait_timeout = 3;
    if (httpd_start(&s_server, &c) != ESP_OK) {
        ESP_LOGE(TAG, "khong mo duoc HTTP server");
        s_server = NULL;
        return;
    }
    for (size_t i = 0; i < sizeof(uris) / sizeof(uris[0]); i++) {
        ESP_ERROR_CHECK(httpd_register_uri_handler(s_server, &uris[i]));
    }
}

// ---------------------------------------------------------------------------
// Trong nom: mau mat theo trang thai, pin (dung khi yeu, bao 5 s), danh dau OTA hop le
// ---------------------------------------------------------------------------
static void housekeeping_task(void *arg)
{
    (void)arg;
    int low_ms = 0;
    int report_ms = 0;
    bool marked = false;
    eyes_status_t last = (eyes_status_t)-1;
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(500));
        int mv = batt_mv();

        eyes_status_t st = (mv > 0 && mv < BATT_RUN_REFUSE_MV) ? EYES_ST_BATT_LOW : netcfg_eye_status();
        if (st != last) {
            last = st;
            eyes_set_status(st);
        }

        if (s_busy && mv > 0 && mv < BATT_RUN_STOP_MV) {
            low_ms += 500;
            if (low_ms >= BATT_STOP_HOLD_MS) {
                request_stop("batt");
                low_ms = 0;
            }
        } else {
            low_ms = 0;
        }

        report_ms += 500;
        if (report_ms >= BATT_REPORT_MS) {
            report_ms = 0;
            char b[48];
            int o = jt(b, sizeof(b), "batt");
            snprintf(b + o, sizeof(b) - (size_t)o, ",\"mv\":%d}", mv);
            ws_send(-1, b);
        }

        // Wi-Fi (STA hoac AP) + HTTP da chay on -> bo rollback
        if (!marked && s_server != NULL && (netcfg_sta_connected() || netcfg_ap_on())) {
            marked = true;
            esp_err_t e = esp_ota_mark_app_valid_cancel_rollback();
            ESP_LOGI(TAG, "danh dau ban hop le (%s)", esp_err_to_name(e));
        }
    }
}

static void load_cal(void)
{
    nvs_handle_t h;
    if (nvs_open("car", NVS_READONLY, &h) != ESP_OK) {
        return;
    }
    int32_t v = 0;
    if (nvs_get_i32(h, "steps_cell", &v) == ESP_OK && v >= CAL_CELL_MIN && v <= CAL_CELL_MAX) {
        s_steps_cell = (int)v;
    }
    if (nvs_get_i32(h, "steps_90", &v) == ESP_OK && v >= CAL_90_MIN && v <= CAL_90_MAX) {
        s_steps_90 = (int)v;
    }
    nvs_close(h);
}

void app_main(void)
{
    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES || e == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        e = nvs_flash_init();
    }
    ESP_ERROR_CHECK(e);
    load_cal();

    s_send_lock = xSemaphoreCreateMutex();
    s_run_q = xQueueCreate(1, sizeof(job_t));

    stepper_init();   // nha cuon ngay khi len dien
    eyes_init();
    batt_init();
    sound_init();
    btn_init();
    xTaskCreate(runner_task, "runner", 6144, NULL, 5, NULL);

    netcfg_start();
    http_start();
    xTaskCreate(housekeeping_task, "house", 4096, NULL, 3, NULL);
    ESP_LOGI(TAG, "block-coding-car %s san sang (cell=%d, 90=%d)", fw_version(), s_steps_cell, s_steps_90);
}
