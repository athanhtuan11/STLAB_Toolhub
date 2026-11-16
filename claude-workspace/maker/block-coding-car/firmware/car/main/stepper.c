// Dieu khien 2 motor 28BYJ-48: nua buoc, doc lap bang esp_timer (task uu tien cao), doc tuyen 200 -> 500 buoc/s trong 300 buoc.
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include "esp_log.h"

#include "pins.h"
#include "stepper.h"

#define SPEED_START_HZ  200   // PROTOCOL muc 5
#define SPEED_MAX_HZ    500   // khong vuot 500 (gioi han keo vao > 600 Hz theo datasheet)
#define RAMP_STEPS      300

static const char *TAG = "stepper";

static const uint8_t PHASES[8] = {0x1, 0x3, 0x2, 0x6, 0x4, 0xC, 0x8, 0x9};  // bit0 = IN1 ... bit3 = IN4

static const int PINS_L[4] = {PIN_ML_IN1, PIN_ML_IN2, PIN_ML_IN3, PIN_ML_IN4};
static const int PINS_R[4] = {PIN_MR_IN1, PIN_MR_IN2, PIN_MR_IN3, PIN_MR_IN4};

static esp_timer_handle_t s_timer = NULL;
static SemaphoreHandle_t s_done = NULL;
static volatile bool s_abort = false;
static volatile bool s_running = false;
static volatile bool s_aborted_result = false;

// Trang thai 1 lan chay (chi dung trong callback sau khi stepper_move khoi dong)
static int s_total;            // so tick (= max(|l|, |r|))
static int s_tick;
static int s_cnt_l, s_cnt_r;   // so buoc muon chay moi ben (gia tri tuyet doi)
static int s_acc_l, s_acc_r;   // bo cong Bresenham
static int s_dir_l, s_dir_r;   // +1 / -1 theo phase
static int s_ph_l, s_ph_r;     // chi so pha hien tai

static void write_phase(const int *pins, int ph)
{
    uint8_t m = PHASES[ph & 7];
    for (int i = 0; i < 4; i++) {
        gpio_set_level((gpio_num_t)pins[i], (m >> i) & 1);
    }
}

void stepper_release(void)
{
    for (int i = 0; i < 4; i++) {
        gpio_set_level((gpio_num_t)PINS_L[i], 0);
        gpio_set_level((gpio_num_t)PINS_R[i], 0);
    }
}

void stepper_abort(void)
{
    s_abort = true;
}

void stepper_clear_abort(void)
{
    s_abort = false;
}

bool stepper_is_aborted(void)
{
    return s_abort;
}

static int speed_at(int i, int n)
{
    int a = i < RAMP_STEPS ? i : RAMP_STEPS;
    int j = n - 1 - i;
    int d = j < RAMP_STEPS ? j : RAMP_STEPS;
    int m = a < d ? a : d;
    return SPEED_START_HZ + (SPEED_MAX_HZ - SPEED_START_HZ) * m / RAMP_STEPS;
}

static void finish(bool aborted)
{
    s_running = false;
    s_aborted_result = aborted;
    stepper_release();
    xSemaphoreGive(s_done);
}

static void tick_cb(void *arg)
{
    (void)arg;
    if (s_abort) {
        finish(true);
        return;
    }
    // Moi ben di 1 buoc khi bo cong Bresenham vuot s_total (cung nhip, so buoc co the khac nhau)
    s_acc_l += s_cnt_l;
    if (s_acc_l >= s_total) {
        s_acc_l -= s_total;
        s_ph_l = (s_ph_l + s_dir_l + 8) & 7;
        write_phase(PINS_L, s_ph_l);
    }
    s_acc_r += s_cnt_r;
    if (s_acc_r >= s_total) {
        s_acc_r -= s_total;
        s_ph_r = (s_ph_r + s_dir_r + 8) & 7;
        write_phase(PINS_R, s_ph_r);
    }
    s_tick++;
    if (s_tick >= s_total) {
        finish(false);
        return;
    }
    int hz = speed_at(s_tick, s_total);
    esp_timer_start_once(s_timer, 1000000 / hz);
}

void stepper_init(void)
{
    uint64_t mask = 0;
    for (int i = 0; i < 4; i++) {
        mask |= 1ULL << PINS_L[i];
        mask |= 1ULL << PINS_R[i];
    }
    gpio_config_t io;
    memset(&io, 0, sizeof(io));
    io.pin_bit_mask = mask;
    io.mode = GPIO_MODE_OUTPUT;
    ESP_ERROR_CHECK(gpio_config(&io));
    stepper_release();

    s_done = xSemaphoreCreateBinary();
    const esp_timer_create_args_t args = {
        .callback = tick_cb,
        .arg = NULL,
        .dispatch_method = ESP_TIMER_TASK,
        .name = "stepper",
        .skip_unhandled_events = true,
    };
    ESP_ERROR_CHECK(esp_timer_create(&args, &s_timer));
    ESP_LOGI(TAG, "stepper san sang");
}

int stepper_move(int left_steps, int right_steps)
{
    if (s_abort) {
        stepper_release();
        return -1;
    }
    int l = left_steps * DIR_LEFT;
    int r = right_steps * DIR_RIGHT;
    int al = abs(l);
    int ar = abs(r);
    s_total = al > ar ? al : ar;
    if (s_total == 0) {
        return 0;
    }
    s_cnt_l = al;
    s_cnt_r = ar;
    s_dir_l = l >= 0 ? 1 : -1;
    s_dir_r = r >= 0 ? 1 : -1;
    s_acc_l = 0;
    s_acc_r = 0;
    s_tick = 0;
    xSemaphoreTake(s_done, 0);
    s_running = true;
    // Buoc dau chay ngay trong callback dau tien
    esp_timer_start_once(s_timer, 1000000 / SPEED_START_HZ);
    xSemaphoreTake(s_done, portMAX_DELAY);
    return s_aborted_result ? -1 : 0;
}
