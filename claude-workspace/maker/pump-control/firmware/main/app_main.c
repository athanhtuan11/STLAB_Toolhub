// May bom dieu khien tu xa - ESP32-WROOM-32D + ESP RainMaker (app "ESP RainMaker" iOS/Android).
// Giao dien tren app (thiet bi "May bom"):
//   - Bat/Tat           (toggle, KHONG luu -> khoi dong/co dien lai luon TAT)
//   - Chay toi da (phut) (thanh keo 5..240, luu lai qua mat dien)
//   - Con lai (phut)     (chi doc, cap nhat moi phut khi dang chay)
//   - Gio thiet bi       (chi doc, moi phut - kiem mui gio truoc khi tin lich tuoi)
//   - Phien ban / Ban moi (chi doc) + nut "Cap nhat": khach bam -> tai firmware moi Tuan dang tren GitHub (ota_pull.c)
//   + Lich hen gio (Schedules) co san trong app.
// Lich tuoi: app -> Schedules -> vd. 06:00 + 18:00 hang ngay "Bat"; bom tu tat sau "Chay toi da" = thoi gian tuoi.
// Lich luu va chay TREN ESP32 (mat Internet van chay, mien la da co gio; mat dien + mat mang thi cho dong bo gio lai).
// Ket noi Wi-Fi lan dau: app RainMaker -> Add device -> quet ma QR / Bluetooth (in log Serial).
// Nut BOOT (GPIO0): giu 3 s = xoa Wi-Fi, giu 10 s = reset nha may.
#include <string.h>
#include <time.h>

#include "esp_log.h"
#include "esp_timer.h"
#include "nvs_flash.h"

#include "esp_rmaker_core.h"
#include "esp_rmaker_ota.h"
#include "esp_rmaker_schedule.h"
#include "esp_rmaker_standard_params.h"
#include "esp_rmaker_standard_types.h"

#include "app_network.h"
#include "app_reset.h"

#include "ota_pull.h"
#include "pump.h"

#define RELAY_GPIO        GPIO_NUM_26  // -> IN1 module relay (jumper H)
#define RESET_BUTTON_GPIO GPIO_NUM_0   // nut BOOT tren bo DevKitC
#define MAX_MIN_DEFAULT   30           // phut - doi trong app
#define MAX_MIN_LOW       5
#define MAX_MIN_HIGH      240

#define PARAM_MAX  "Chay toi da (phut)"
#define PARAM_LEFT "Con lai (phut)"
#define PARAM_CLOCK "Gio thiet bi"
#define PARAM_VER   "Phien ban"
#define PARAM_NEW   "Ban moi"
#define PARAM_UPD   "Cap nhat"
#define OTA_CHECK_HOURS 6

static const char *TAG = "app";

static esp_rmaker_param_t *s_power;
static esp_rmaker_param_t *s_max;
static esp_rmaker_param_t *s_left;
static esp_rmaker_param_t *s_clock;
static esp_rmaker_param_t *s_new;
static esp_timer_handle_t s_tick;
static esp_timer_handle_t s_clock_tick;
static esp_timer_handle_t s_ota_tick;

static void report_left(void)
{
    if (s_left) {
        esp_rmaker_param_update_and_report(s_left, esp_rmaker_int(pump_remaining_minutes()));
    }
}

static void tick_cb(void *arg)
{
    report_left();
}

static void ota_status_cb(const char *text)
{
    if (s_new) {
        esp_rmaker_param_update_and_report(s_new, esp_rmaker_str(text));
    }
}

static void ota_tick_cb(void *arg)
{
    ota_pull_check_async();  // chi kiem, khong tu cai
}

static void clock_cb(void *arg)
{
    time_t now = time(NULL);
    struct tm t;
    localtime_r(&now, &t);
    char buf[32];
    if (t.tm_year < (2024 - 1900)) {
        snprintf(buf, sizeof(buf), "chua co gio (cho Internet)");
    } else {
        strftime(buf, sizeof(buf), "%H:%M %d/%m/%Y", &t);
    }
    if (s_clock) {
        esp_rmaker_param_update_and_report(s_clock, esp_rmaker_str(buf));
    }
}

// Lop dieu khien bao doi trang thai (ke ca tu tat khi het gio) -> cap nhat app
static void on_pump_change(bool on, pump_src_t src)
{
    if (s_power) {
        esp_rmaker_param_update_and_report(s_power, esp_rmaker_bool(on));
    }
    if (on) {
        esp_timer_start_periodic(s_tick, 60LL * 1000000);
    } else {
        esp_timer_stop(s_tick);
    }
    report_left();
    if (src == PUMP_SRC_TIMEOUT) {
        esp_rmaker_raise_alert("May bom da tu tat: het thoi gian chay toi da");
    }
}

static esp_err_t write_cb(const esp_rmaker_device_t *device, const esp_rmaker_param_t *param,
                          const esp_rmaker_param_val_t val, void *priv_data, esp_rmaker_write_ctx_t *ctx)
{
    const char *name = esp_rmaker_param_get_name(param);
    if (strcmp(name, ESP_RMAKER_DEF_POWER_NAME) == 0) {
        ESP_LOGI(TAG, "lenh %s tu %s", val.val.b ? "BAT" : "TAT", esp_rmaker_device_cb_src_to_str(ctx->src));
        if (val.val.b && ota_pull_busy()) {
            ota_status_cb("Dang cap nhat firmware - chua bat bom duoc");
            esp_rmaker_param_update_and_report(param, esp_rmaker_bool(false));
            return ESP_OK;
        }
        if (!pump_set(val.val.b, PUMP_SRC_USER)) {
            // Chong bat/tat lien tuc: bao khach + tra nut ve TAT
            char msg[96];
            snprintf(msg, sizeof(msg), "May bom vua tat - cho %d giay nua moi bat lai duoc", pump_lockout_seconds());
            esp_rmaker_raise_alert(msg);
            esp_rmaker_param_update_and_report(param, esp_rmaker_bool(false));
            return ESP_OK;
        }
        esp_rmaker_param_update(param, val);
    } else if (strcmp(name, PARAM_MAX) == 0) {
        int m = val.val.i;
        if (m < MAX_MIN_LOW || m > MAX_MIN_HIGH) {
            return ESP_ERR_INVALID_ARG;
        }
        pump_set_max_minutes(m);
        esp_rmaker_param_update(param, val);  // co PROP_FLAG_PERSIST -> luu NVS
        report_left();
    } else if (strcmp(name, PARAM_UPD) == 0) {
        if (pump_is_on()) {
            ota_status_cb("Dang bom - tat bom roi bam Cap nhat lai");  // khong ngat giua luc tuoi
        } else {
            ota_pull_update_async();
        }
    }
    return ESP_OK;
}

void app_main(void)
{
    // 1) Relay TAT truoc moi thu khac
    pump_init(RELAY_GPIO, MAX_MIN_DEFAULT, on_pump_change);
    const esp_timer_create_args_t targs = {.callback = tick_cb, .name = "pump_tick"};
    ESP_ERROR_CHECK(esp_timer_create(&targs, &s_tick));

    button_handle_t btn = app_reset_button_create(RESET_BUTTON_GPIO, 0);
    if (btn) {
        app_reset_button_register(btn, 3, 10);
    }

    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    app_network_init();

    esp_rmaker_config_t cfg = {.enable_time_sync = true};  // SNTP: lich hen gio can gio dung
    esp_rmaker_node_t *node = esp_rmaker_node_init(&cfg, "STLab May bom", "Pump");
    if (!node) {
        ESP_LOGE(TAG, "khong khoi tao duoc RainMaker node");
        abort();
    }

    esp_rmaker_device_t *dev = esp_rmaker_device_create("May bom", ESP_RMAKER_DEVICE_SWITCH, NULL);
    esp_rmaker_device_add_cb(dev, write_cb, NULL);
    esp_rmaker_device_add_param(dev, esp_rmaker_name_param_create(ESP_RMAKER_DEF_NAME_PARAM, "May bom"));

    // Bat/Tat: KHONG co PROP_FLAG_PERSIST -> sau mat dien luon TAT (quyet dinh Tuan)
    s_power = esp_rmaker_param_create(ESP_RMAKER_DEF_POWER_NAME, ESP_RMAKER_PARAM_POWER, esp_rmaker_bool(false),
                                      PROP_FLAG_READ | PROP_FLAG_WRITE);
    esp_rmaker_param_add_ui_type(s_power, ESP_RMAKER_UI_TOGGLE);
    esp_rmaker_device_add_param(dev, s_power);
    esp_rmaker_device_assign_primary_param(dev, s_power);

    s_max = esp_rmaker_param_create(PARAM_MAX, "stlab.param.max-minutes", esp_rmaker_int(MAX_MIN_DEFAULT),
                                    PROP_FLAG_READ | PROP_FLAG_WRITE | PROP_FLAG_PERSIST);
    esp_rmaker_param_add_ui_type(s_max, ESP_RMAKER_UI_SLIDER);
    esp_rmaker_param_add_bounds(s_max, esp_rmaker_int(MAX_MIN_LOW), esp_rmaker_int(MAX_MIN_HIGH), esp_rmaker_int(5));
    esp_rmaker_device_add_param(dev, s_max);

    s_left = esp_rmaker_param_create(PARAM_LEFT, "stlab.param.minutes-left", esp_rmaker_int(0), PROP_FLAG_READ);
    esp_rmaker_param_add_ui_type(s_left, ESP_RMAKER_UI_TEXT);
    esp_rmaker_device_add_param(dev, s_left);

    s_clock = esp_rmaker_param_create(PARAM_CLOCK, "stlab.param.device-time", esp_rmaker_str("chua co gio (cho Internet)"),
                                      PROP_FLAG_READ);
    esp_rmaker_param_add_ui_type(s_clock, ESP_RMAKER_UI_TEXT);
    esp_rmaker_device_add_param(dev, s_clock);

    esp_rmaker_device_add_param(dev, esp_rmaker_param_create(PARAM_VER, "stlab.param.fw-version",
                                     esp_rmaker_str(ota_pull_current_version()), PROP_FLAG_READ));
    s_new = esp_rmaker_param_create(PARAM_NEW, "stlab.param.fw-latest", esp_rmaker_str("chua kiem"), PROP_FLAG_READ);
    esp_rmaker_param_add_ui_type(s_new, ESP_RMAKER_UI_TEXT);
    esp_rmaker_device_add_param(dev, s_new);
    esp_rmaker_param_t *upd = esp_rmaker_param_create(PARAM_UPD, "stlab.param.fw-update", esp_rmaker_bool(false),
                                                      PROP_FLAG_READ | PROP_FLAG_WRITE);
    esp_rmaker_param_add_ui_type(upd, ESP_RMAKER_UI_TRIGGER);
    esp_rmaker_device_add_param(dev, upd);
    ota_pull_init(ota_status_cb);

    esp_rmaker_node_add_device(node, dev);

    esp_rmaker_ota_enable_default();
    esp_rmaker_timezone_service_enable();
    esp_rmaker_schedule_enable();  // hen gio bat bom trong app; bat bom theo lich van bi gioi han "chay toi da"
    esp_rmaker_system_serv_config_t sys = {
        .flags = SYSTEM_SERV_FLAGS_ALL, .reboot_seconds = 2, .reset_seconds = 2, .reset_reboot_seconds = 2};
    esp_rmaker_system_service_enable(&sys);

    esp_rmaker_start();

    const esp_timer_create_args_t cargs = {.callback = clock_cb, .name = "clock_tick"};
    ESP_ERROR_CHECK(esp_timer_create(&cargs, &s_clock_tick));
    esp_timer_start_periodic(s_clock_tick, 60LL * 1000000);
    const esp_timer_create_args_t oargs = {.callback = ota_tick_cb, .name = "ota_tick"};
    ESP_ERROR_CHECK(esp_timer_create(&oargs, &s_ota_tick));
    esp_timer_start_periodic(s_ota_tick, OTA_CHECK_HOURS * 3600LL * 1000000);

    err = app_network_start(POP_TYPE_RANDOM);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "khong ket noi duoc Wi-Fi (%s) - relay van TAT", esp_err_to_name(err));
    } else {
        // app_network_start tra ve truoc khi Wi-Fi ket noi xong -> kiem ban moi lan dau sau 90 s
        static esp_timer_handle_t first;
        const esp_timer_create_args_t fargs = {.callback = ota_tick_cb, .name = "ota_first"};
        if (esp_timer_create(&fargs, &first) == ESP_OK) {
            esp_timer_start_once(first, 90LL * 1000000);
        }
    }
}
