// Chan GPIO – khop hardware/wiring.yaml (test_static_fw.py so khop). Doi chan: sua CA wiring.yaml.
// Tranh: GPIO0/3/45/46 (strapping), 19/20 (USB), 35-37 (PSRAM octal), 43/44 (UART log).
#pragma once

#define PIN_ML_IN1     4
#define PIN_ML_IN2     5
#define PIN_ML_IN3     6
#define PIN_ML_IN4     7

#define PIN_MR_IN1     15
#define PIN_MR_IN2     16
#define PIN_MR_IN3     17
#define PIN_MR_IN4     18

#define PIN_LED        12   // WS2812 x2 qua 74AHCT125
#define PIN_I2S_BCLK   9
#define PIN_I2S_LRC    10
#define PIN_I2S_DIN    11
#define PIN_BTN_STOP   13   // keo len noi, nhan = muc 0
#define PIN_BATT_ADC   1    // ADC1_CH0, chia ap 100k/100k

// Chieu quay motor: 2 motor gan doi xung nen chieu quay nguoc nhau khi xe tien.
// TODO: kiem tren xe that – neu xe lui thay vi tien thi doi dau ca hai.
#define DIR_LEFT       (-1)
#define DIR_RIGHT      (+1)

#define SOUND_MAX_PCT  30   // PROTOCOL muc 5: bien do am thanh toi da (% full-scale)
#define LED_MAX_PCT    25   // PROTOCOL muc 5: do sang mat toi da (%)
