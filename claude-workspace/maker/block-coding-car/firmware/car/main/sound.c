// MAX98357A qua I2S standard (Philips), 16 kHz. Cac am tu sinh bang sin, co envelope 5 ms de khong bi tach.
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "driver/i2s_std.h"
#include "esp_log.h"

#include "pins.h"
#include "sound.h"

#define SAMPLE_RATE   16000
#define CHUNK         256           // mau moi lan ghi (stereo: x2)
#define FADE_SAMPLES  80            // 5 ms
#define AMP           (32767 * SOUND_MAX_PCT / 100)

static const char *TAG = "sound";

static i2s_chan_handle_t s_tx = NULL;
static SemaphoreHandle_t s_lock = NULL;
static volatile bool s_stop = false;

void sound_init(void)
{
    s_lock = xSemaphoreCreateMutex();
    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    cc.auto_clear = true;
    ESP_ERROR_CHECK(i2s_new_channel(&cc, &s_tx, NULL));
    i2s_std_config_t sc = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = PIN_I2S_BCLK,
            .ws = PIN_I2S_LRC,
            .dout = PIN_I2S_DIN,
            .din = I2S_GPIO_UNUSED,
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_std_mode(s_tx, &sc));
    ESP_LOGI(TAG, "I2S san sang (bien do <= %d %%)", SOUND_MAX_PCT);
}

void sound_stop(void)
{
    s_stop = true;
}

// Phat 1 not (freq Hz, ms mili giay). Tra false neu bi dung giua chung.
static bool tone(int freq, int ms)
{
    int total = SAMPLE_RATE / 1000 * ms;
    float step = 2.0f * (float)M_PI * (float)freq / (float)SAMPLE_RATE;
    static float phase = 0.0f;
    int16_t buf[CHUNK * 2];
    int done = 0;
    while (done < total) {
        if (s_stop) {
            return false;
        }
        int n = total - done < CHUNK ? total - done : CHUNK;
        for (int i = 0; i < n; i++) {
            int pos = done + i;
            int edge = pos < total - pos ? pos : total - pos;
            float env = edge < FADE_SAMPLES ? (float)edge / (float)FADE_SAMPLES : 1.0f;
            int16_t v = (int16_t)(sinf(phase) * (float)AMP * env);
            phase += step;
            if (phase > 2.0f * (float)M_PI) {
                phase -= 2.0f * (float)M_PI;
            }
            buf[2 * i] = v;
            buf[2 * i + 1] = v;
        }
        size_t written = 0;
        if (i2s_channel_write(s_tx, buf, (size_t)n * 4, &written, 1000) != ESP_OK) {
            return false;
        }
        done += n;
    }
    return true;
}

void sound_play(int id)
{
    xSemaphoreTake(s_lock, portMAX_DELAY);
    s_stop = false;
    if (i2s_channel_enable(s_tx) == ESP_OK) {
        if (id == 0) {
            tone(880, 150);
        } else if (id == 1) {
            if (tone(440, 300)) {
                tone(660, 300);
            }
        } else if (id == 2) {
            static const int NOTES[4] = {523, 659, 784, 1047};  // C5 E5 G5 C6
            for (int i = 0; i < 4; i++) {
                if (!tone(NOTES[i], 250)) {
                    break;
                }
            }
        }
        // Xa not cuoi bang im lang de loa khong keu tach roi tat kenh
        static const int16_t silence[CHUNK * 2];
        size_t w = 0;
        i2s_channel_write(s_tx, silence, sizeof(silence), &w, 200);
        i2s_channel_disable(s_tx);
    }
    xSemaphoreGive(s_lock);
}
