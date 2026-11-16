// Mat WS2812 x2 qua led_strip (RMT). Tat ca mau nhan he so LED_MAX_PCT/100.
#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_log.h"
#include "led_strip.h"

#include "pins.h"
#include "eyes.h"

#define NUM_EYES 2

static const char *TAG = "eyes";

typedef struct {
    uint8_t r, g, b;
} rgb_t;

// Thu tu theo PROTOCOL bang `eye`: 0 do, 1 xanh la, 2 xanh duong, 3 vang, 4 tim, 5 tat
static const rgb_t PALETTE[6] = {
    {255, 0, 0}, {0, 255, 0}, {0, 0, 255}, {255, 190, 0}, {160, 0, 255}, {0, 0, 0},
};

static led_strip_handle_t s_strip = NULL;
static SemaphoreHandle_t s_lock = NULL;
static eyes_status_t s_status = EYES_ST_CONNECTING;
static int s_prog_color = -1;   // -1 = khong co mau chuong trinh
static bool s_blink_on = true;

static void apply_locked(void)
{
    rgb_t c = {0, 0, 0};
    if (s_prog_color >= 0) {
        c = PALETTE[s_prog_color];
    } else {
        switch (s_status) {
        case EYES_ST_CONNECTING:
            c = s_blink_on ? PALETTE[2] : PALETTE[5];
            break;
        case EYES_ST_WIFI_OK:
            c = PALETTE[1];
            break;
        case EYES_ST_AP:
            c = PALETTE[3];
            break;
        case EYES_ST_BATT_LOW:
            c = s_blink_on ? PALETTE[0] : PALETTE[5];
            break;
        }
    }
    uint32_t r = (uint32_t)c.r * LED_MAX_PCT / 100;
    uint32_t g = (uint32_t)c.g * LED_MAX_PCT / 100;
    uint32_t b = (uint32_t)c.b * LED_MAX_PCT / 100;
    for (int i = 0; i < NUM_EYES; i++) {
        led_strip_set_pixel(s_strip, (uint32_t)i, r, g, b);
    }
    led_strip_refresh(s_strip);
}

static void blink_task(void *arg)
{
    (void)arg;
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(400));
        xSemaphoreTake(s_lock, portMAX_DELAY);
        s_blink_on = !s_blink_on;
        bool blinking = s_prog_color < 0 && (s_status == EYES_ST_CONNECTING || s_status == EYES_ST_BATT_LOW);
        if (blinking) {
            apply_locked();
        }
        xSemaphoreGive(s_lock);
    }
}

void eyes_init(void)
{
    s_lock = xSemaphoreCreateMutex();
    led_strip_config_t sc = {
        .strip_gpio_num = PIN_LED,
        .max_leds = NUM_EYES,
        .led_model = LED_MODEL_WS2812,
        .color_component_format = LED_STRIP_COLOR_COMPONENT_FMT_GRB,
        .flags = {.invert_out = false},
    };
    led_strip_rmt_config_t rc = {
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 10 * 1000 * 1000,
        .flags = {.with_dma = false},
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&sc, &rc, &s_strip));
    xSemaphoreTake(s_lock, portMAX_DELAY);
    apply_locked();
    xSemaphoreGive(s_lock);
    xTaskCreate(blink_task, "eyes", 2048, NULL, 3, NULL);
    ESP_LOGI(TAG, "mat san sang (do sang <= %d %%)", LED_MAX_PCT);
}

void eyes_set_status(eyes_status_t st)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_status = st;
    apply_locked();
    xSemaphoreGive(s_lock);
}

void eyes_set_program_color(int color)
{
    if (color < 0 || color > 5) {
        return;
    }
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_prog_color = color;
    apply_locked();
    xSemaphoreGive(s_lock);
}

void eyes_clear_program_color(void)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_prog_color = -1;
    apply_locked();
    xSemaphoreGive(s_lock);
}
