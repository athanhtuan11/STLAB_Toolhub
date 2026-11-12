#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

// STLab ESP32-S3 N16R8 + INMP441 (mic) + MAX98357A (ampli) - tro chuyen truc tiep, AEC tren bo bang tham chieu phan mem.
// Chan giong bread-compact-wifi (simplex, 2 cong I2S). N16R8 PSRAM octal chiem GPIO35..37 -> khong dung.

// Vao/ra CUNG 16 kHz: mau ra loa dung lam tham chieu AEC khong phai doi tan so.
#define AUDIO_INPUT_SAMPLE_RATE     16000
#define AUDIO_OUTPUT_SAMPLE_RATE    16000

#define AUDIO_DEFAULT_OUTPUT_VOLUME 100  // Tuan 2026-11-12: loa 3 W qua nho, luon de 100
#define STLAB_VOLUME_STEP           10

// INMP441 (3,3 V): chan L/R noi GND -> kenh trai
#define AUDIO_I2S_MIC_GPIO_WS   GPIO_NUM_4
#define AUDIO_I2S_MIC_GPIO_SCK  GPIO_NUM_5
#define AUDIO_I2S_MIC_GPIO_DIN  GPIO_NUM_6
// MAX98357A
#define AUDIO_I2S_SPK_GPIO_DOUT GPIO_NUM_7
#define AUDIO_I2S_SPK_GPIO_BCLK GPIO_NUM_15
#define AUDIO_I2S_SPK_GPIO_LRCK GPIO_NUM_16

// Tre tham chieu AEC (ms): mau ghi ra loa duoc tra ve kenh tham chieu sau STLAB_AEC_REF_DELAY_MS.
// Gia tri khoi dau 100 ms = do sau hang doi DMA phat (AUDIO_CODEC_DMA_DESC_NUM 6 x 240 mau o 16 kHz = 90 ms, luc phat lien tuc
// hang doi day nen mau chep vao vong dem ra loa that khoang 90 ms sau) + ~10 ms tu loa toi mic + do tre doc mic.
// Day la uoc tinh, KHONG do duoc khi chua co bo: chinh bang log [AEC] (RMS mic / ref / sau AFE) roi build lai.
// Bo loc AFE bu duoc tre con lai nho; khoang 0..200 ms.
#define STLAB_AEC_REF_DELAY_MS 45   // 2026-11-12 [AEC-LAG] do 32-48 ms (100 ms la uoc tinh cu, sai)

// 1 = tu do tre bang tuong quan cheo (log [AEC-LAG]) va chinh delay luc chay (0..300 ms); STLAB_AEC_REF_DELAY_MS chi la gia tri khoi dau.
#define STLAB_AEC_AUTO_DELAY 1
// Do loi mic INMP441: du lieu 32 bit >> STLAB_MIC_SHIFT. xiaozhi goc 12; 2026-11-12 do clip ~38 % khi loa gan -> 14 (-12 dB)
#define STLAB_MIC_SHIFT 13   // 2026-11-12: 14 lam giong cach 20 cm qua nho (Tuan: khong nghe ro) -> 13

// Nut noi NGOAI = switch MX 2 chan GPIO1 <-> GND (active-low, pull-up noi); nut BOOT GPIO0 chay song song de thu tren ban (BOOT chim trong vo).
// Deep sleep (neu bat sau nay): GPIO1 la RTC GPIO, dung lam chan danh thuc. Nut: vol+ / vol-; LED WS2812 tren bo (neu devkit khong co thi khong sang, khong sao)
#define TALK_BUTTON_GPIO        GPIO_NUM_1
#define BOOT_BUTTON_GPIO        GPIO_NUM_0
#define VOLUME_UP_BUTTON_GPIO   GPIO_NUM_40
#define VOLUME_DOWN_BUTTON_GPIO GPIO_NUM_39
#define BUILTIN_LED_GPIO        GPIO_NUM_48

// Giu nut noi 3 s = ngu; 60 s khong giao tiep = tu ngu (khong tat Wi-Fi, cham la noi ngay)
#define STLAB_TALK_LONG_MS      5000
#define STLAB_IDLE_SLEEP_S      60

#endif // _BOARD_CONFIG_H_
