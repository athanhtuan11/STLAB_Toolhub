#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

// STLab ESP32-S3 N16R8 + INMP441 (mic) + MAX98357A (ampli) - tro chuyen truc tiep, AEC tren bo bang tham chieu phan mem.
// Chan giong bread-compact-wifi (simplex, 2 cong I2S). N16R8 PSRAM octal chiem GPIO35..37 -> khong dung.

// Vao/ra CUNG 16 kHz: mau ra loa dung lam tham chieu AEC khong phai doi tan so.
#define AUDIO_INPUT_SAMPLE_RATE     16000
#define AUDIO_OUTPUT_SAMPLE_RATE    16000

#define AUDIO_DEFAULT_OUTPUT_VOLUME 100  // Tuan 2026-11-12: loa 3 W qua nho, luon de 100

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
#define STLAB_MIC_SHIFT 12   // 2026-11-12 Tuan "dua ve goc": bang xiaozhi goc (>>12)

// Nut noi NGOAI = switch MX 2 chan GPIO1 <-> GND (active-low, pull-up noi); nut BOOT GPIO0 chay song song de thu tren ban (BOOT chim trong vo).
// Deep sleep (neu bat sau nay): GPIO1 la RTC GPIO, dung lam chan danh thuc. LED WS2812 tren bo (neu devkit khong co thi khong sang, khong sao)
// Vo khong co nut am luong (wiring-s3.md 5.6): GPIO39/40 de trong.
#define TALK_BUTTON_GPIO        GPIO_NUM_1
#define BOOT_BUTTON_GPIO        GPIO_NUM_0
#define BUILTIN_LED_GPIO        GPIO_NUM_48

// Giu nut noi 3 s = ngu; 60 s khong giao tiep = tu ngu (khong tat Wi-Fi, cham la noi ngay)
#define STLAB_TALK_LONG_MS      5000
#define STLAB_IDLE_SLEEP_S      60

// ---- Man TFT 2,8" MSP2807 (240x320 SPI) dat NGANG 320x240 + cam ung XPT2046 (spec-display.md) ----
// LCD va touch chung 1 bus SPI: SCK=T_CLK, MOSI=T_DIN, MISO=T_DO (GPIO13).
#define DISPLAY_SCK_PIN         GPIO_NUM_12
#define DISPLAY_MOSI_PIN        GPIO_NUM_11
#define DISPLAY_CS_PIN          GPIO_NUM_10
#define DISPLAY_DC_PIN          GPIO_NUM_9
#define DISPLAY_RST_PIN         GPIO_NUM_8
#define DISPLAY_BACKLIGHT_PIN   GPIO_NUM_14
#define TOUCH_MISO_PIN          GPIO_NUM_13
#define TOUCH_CS_PIN            GPIO_NUM_17
#define TOUCH_IRQ_PIN           GPIO_NUM_18

#define DISPLAY_SPI_HZ          20000000   // day <= 10 cm (wiring-s3.md muc 6)
#define TOUCH_SPI_HZ            2000000    // XPT2046 <= 2 MHz

// Chip man: LCDWiki ghi ILI9341, shop ghi ST7789 -> 0 = ILI9341 (mac dinh), 1 = ST7789. Doi roi build lai.
#define STLAB_LCD_ST7789 1

// Hang doc ngang: man goc 240x320, swap_xy = true.
// DA THU THAT 2026-11-28: chip la ST7789 (ILI9341 -> man doc + nhieu); SWAP_XY true + MIRROR_X true hien dung ngang (Tuan: "man mat dep roi").
#define DISPLAY_WIDTH           320
#define DISPLAY_HEIGHT          240
#define DISPLAY_SWAP_XY         true
#define DISPLAY_MIRROR_X        true
#define DISPLAY_MIRROR_Y        false
#if STLAB_LCD_ST7789
#define DISPLAY_INVERT_COLOR    true
#define DISPLAY_RGB_ORDER       LCD_RGB_ELEMENT_ORDER_RGB
#else
#define DISPLAY_INVERT_COLOR    false
#define DISPLAY_RGB_ORDER       LCD_RGB_ELEMENT_ORDER_BGR
#endif
#define DISPLAY_OFFSET_X        0
#define DISPLAY_OFFSET_Y        0
#define DISPLAY_SPI_MODE        0
#define DISPLAY_BACKLIGHT_OUTPUT_INVERT false

// Den nen (% PWM) - mat be: tran 60 %, khong bao gio vuot
#define STLAB_BL_ACTIVE         40   // nghe / noi / khen / nghi
#define STLAB_BL_IDLE           25   // cho
#define STLAB_BL_SLEEP          8    // ngu
#define STLAB_BL_WIFI           60   // cai Wi-Fi (nguoi lon nhin)
#define STLAB_BL_MAX            60

// Cham: 1 lan / 400 ms
#define STLAB_TOUCH_DEBOUNCE_MS 400

#endif // _BOARD_CONFIG_H_
