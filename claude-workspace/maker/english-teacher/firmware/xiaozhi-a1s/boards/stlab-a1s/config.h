#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

// STLab ESP32-A1S Audio Kit (ES8388 v1), chan theo ket qua do mach that 2026-11-05
#define AUDIO_INPUT_SAMPLE_RATE     24000
#define AUDIO_OUTPUT_SAMPLE_RATE    24000

// Am luong: mac dinh 40, tran 60 (be nho, tai nghe/loa gan tai) - moi lenh dat am luong bi kep o board .cc
#define AUDIO_DEFAULT_OUTPUT_VOLUME 70   // 2026-11-06 Tuan: to hon, tu chinh KEY5/KEY6
#define STLAB_MAX_VOLUME            100  // Tuan bo tran (2026-11-06). Cho be dung: chinh nho lai! KEY5 +10, KEY6 -10
#define STLAB_VOLUME_STEP           10

#define AUDIO_I2S_GPIO_MCLK GPIO_NUM_0
#define AUDIO_I2S_GPIO_BCLK GPIO_NUM_27
#define AUDIO_I2S_GPIO_WS   GPIO_NUM_25
#define AUDIO_I2S_GPIO_DOUT GPIO_NUM_26
#define AUDIO_I2S_GPIO_DIN  GPIO_NUM_35

#define AUDIO_CODEC_I2C_SCL_PIN GPIO_NUM_32
#define AUDIO_CODEC_I2C_SDA_PIN GPIO_NUM_33
#define AUDIO_CODEC_PA_PIN      GPIO_NUM_21
#define AUDIO_CODEC_ES8388_ADDR ES8388_CODEC_DEFAULT_ADDR

// Mic noi vao ES8388 LIN2/RIN2 (do thuc te 2026-11-05: dinh 1000 Hz SNR 23,7 dB, LIN1 im lang); board .cc chon qua ADCCONTROL2=0x50
#define STLAB_MIC_INPUT_LINE2 1

// GPIO0 la MCLK nen KHONG co nut BOOT. Nut KEY1..6 = GPIO36,13,19,23,18,5 (bam = muc thap)
#define TALK_BUTTON_GPIO        GPIO_NUM_23   // KEY4: cham = mo/ket thuc phien noi chuyen, cham khi co noi = ngat
#define VOLUME_UP_BUTTON_GPIO   GPIO_NUM_18   // KEY5
#define VOLUME_DOWN_BUTTON_GPIO GPIO_NUM_5    // KEY6

// 2026-11-06 Tuan: giu KEY4 5 s = ngu; 60 s khong giao tiep = tu ngu (khong tat Wi-Fi, cham la noi ngay)
#define STLAB_TALK_LONG_MS      3000   // 2026-11-06 Tuan: giu 5 s lau qua -> 3 s
#define STLAB_IDLE_SLEEP_S      60

#define BUILTIN_LED_GPIO        GPIO_NUM_22   // LED trang thai (muc thap = sang)

#endif // _BOARD_CONFIG_H_
