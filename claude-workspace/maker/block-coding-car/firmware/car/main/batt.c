// Doc pin: adc_oneshot + adc_cali (curve fitting) -> mV o chan ADC, nhan 2 (chia ap 100k/100k) -> mV pin.
#include <stdbool.h>
#include <stdint.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_oneshot.h"
#include "esp_adc/adc_cali.h"
#include "esp_adc/adc_cali_scheme.h"
#include "esp_log.h"

#include "pins.h"
#include "batt.h"

#define ADC_CH       ADC_CHANNEL_0    // GPIO1 = ADC1_CH0 tren ESP32-S3
#define SAMPLES      8
#define PERIOD_MS    500
#define DIVIDER      2                // 100k / 100k

static const char *TAG = "batt";

static adc_oneshot_unit_handle_t s_adc = NULL;
static adc_cali_handle_t s_cali = NULL;
static volatile int s_mv = 0;

static int read_once(void)
{
    int sum = 0;
    int n = 0;
    for (int i = 0; i < SAMPLES; i++) {
        int raw = 0;
        int mv = 0;
        if (adc_oneshot_read(s_adc, ADC_CH, &raw) == ESP_OK && adc_cali_raw_to_voltage(s_cali, raw, &mv) == ESP_OK) {
            sum += mv;
            n++;
        }
        vTaskDelay(1);
    }
    return n > 0 ? sum / n * DIVIDER : 0;
}

static void batt_task(void *arg)
{
    (void)arg;
    while (true) {
        s_mv = read_once();
        vTaskDelay(pdMS_TO_TICKS(PERIOD_MS));
    }
}

int batt_mv(void)
{
    return s_mv;
}

void batt_init(void)
{
    adc_oneshot_unit_init_cfg_t uc = {
        .unit_id = ADC_UNIT_1,
    };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&uc, &s_adc));
    adc_oneshot_chan_cfg_t cc = {
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(s_adc, ADC_CH, &cc));
    adc_cali_curve_fitting_config_t cf = {
        .unit_id = ADC_UNIT_1,
        .chan = ADC_CH,
        .atten = ADC_ATTEN_DB_12,
        .bitwidth = ADC_BITWIDTH_DEFAULT,
    };
    ESP_ERROR_CHECK(adc_cali_create_scheme_curve_fitting(&cf, &s_cali));
    s_mv = read_once();
    xTaskCreate(batt_task, "batt", 3072, NULL, 3, NULL);
    ESP_LOGI(TAG, "pin %d mV (GPIO%d)", s_mv, PIN_BATT_ADC);
}
