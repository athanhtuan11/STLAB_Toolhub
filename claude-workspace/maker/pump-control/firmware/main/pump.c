#include "pump.h"

#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

static const char *TAG = "pump";

static gpio_num_t s_gpio;
static bool s_on;
static int s_max_min;
static int64_t s_started_us;
static int64_t s_off_us;  // luc tat gan nhat (khoi dong = luc tat)
static esp_timer_handle_t s_timer;
static pump_change_cb_t s_cb;
static SemaphoreHandle_t s_lock;

static void relay_write(bool on)
{
    // Module relay opto dat jumper H (kich muc cao): 1 = dong cuon hut contactor.
    gpio_set_level(s_gpio, on ? 1 : 0);
}

static void arm_timer(void)
{
    esp_timer_stop(s_timer);  // loi ESP_ERR_INVALID_STATE khi timer chua chay - bo qua
    int64_t left_us = (int64_t)s_max_min * 60 * 1000000 - (esp_timer_get_time() - s_started_us);
    esp_timer_start_once(s_timer, left_us > 0 ? left_us : 1);
}

static void timeout_cb(void *arg)
{
    ESP_LOGW(TAG, "het %d phut chay toi da -> tat", s_max_min);
    pump_set(false, PUMP_SRC_TIMEOUT);
}

void pump_init(gpio_num_t relay_gpio, int max_minutes, pump_change_cb_t cb)
{
    s_gpio = relay_gpio;
    s_max_min = max_minutes;
    s_cb = cb;
    s_lock = xSemaphoreCreateMutex();
    // Muc 0 TRUOC khi bat output de chan khong co xung dong relay luc khoi dong
    gpio_set_level(s_gpio, 0);
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << s_gpio,
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));
    relay_write(false);
    s_off_us = esp_timer_get_time();  // mat dien chop chop -> cung phai cho, motor khong khoi dong lien tuc
    const esp_timer_create_args_t args = {.callback = timeout_cb, .name = "pump_max"};
    ESP_ERROR_CHECK(esp_timer_create(&args, &s_timer));
    ESP_LOGI(TAG, "relay GPIO%d = TAT, chay toi da %d phut", s_gpio, s_max_min);
}

static int lockout_s_locked(void)
{
    if (s_on) {
        return 0;
    }
    int64_t left_us = (int64_t)PUMP_MIN_OFF_S * 1000000 - (esp_timer_get_time() - s_off_us);
    return left_us > 0 ? (int)((left_us + 999999) / 1000000) : 0;  // lam tron len giay
}

bool pump_set(bool on, pump_src_t src)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    if (on && lockout_s_locked() > 0) {
        int left = lockout_s_locked();
        xSemaphoreGive(s_lock);
        ESP_LOGW(TAG, "tu choi BAT: moi tat, con cho %d s", left);
        return false;
    }
    bool changed = (on != s_on);
    s_on = on;
    relay_write(on);
    if (on && changed) {
        s_started_us = esp_timer_get_time();
        arm_timer();
    } else if (!on) {
        esp_timer_stop(s_timer);
        if (changed) {
            s_off_us = esp_timer_get_time();
        }
    }
    xSemaphoreGive(s_lock);
    ESP_LOGI(TAG, "bom %s (%s)", on ? "BAT" : "TAT", src == PUMP_SRC_TIMEOUT ? "het gio" : "lenh");
    if (changed && s_cb) {
        s_cb(on, src);
    }
    return true;
}

int pump_lockout_seconds(void)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    int left = lockout_s_locked();
    xSemaphoreGive(s_lock);
    return left;
}

bool pump_is_on(void)
{
    return s_on;
}

void pump_set_max_minutes(int minutes)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_max_min = minutes;
    if (s_on) {
        arm_timer();
    }
    xSemaphoreGive(s_lock);
}

int pump_get_max_minutes(void)
{
    return s_max_min;
}

int pump_remaining_minutes(void)
{
    if (!s_on) {
        return 0;
    }
    int64_t left_us = (int64_t)s_max_min * 60 * 1000000 - (esp_timer_get_time() - s_started_us);
    return left_us > 0 ? (int)((left_us + 59999999) / 60000000) : 0;  // lam tron len phut
}
