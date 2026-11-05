// Firmware do ESP32-A1S Audio Kit (ESP32-D0WD-V3). Chay 1 luot khi khoi dong, log UART tien to [DO].
// Bo chan ung vien lay tu ../../CLAUDE.md (pschatzmann/arduino-audio-driver, chi lay so chan):
//   ES8388 v1: I2C SCL/SDA 32/33, I2S MCLK/BCK/WS/DOUT/DIN 0/27/25/26/35
//   ES8388 v2: I2C SCL/SDA 23/18, I2S MCLK/BCK/WS/DOUT/DIN 0/5/25/26/35
//   AC101    : I2C SCL/SDA 32/33, I2S MCLK/BCK/WS/DOUT/DIN 0/27/26/25/35   (chi nhan dien, chua ho tro phat)
//   PA 21, nut 36,13,19,23,18,5 (active low)
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_heap_caps.h"
#include "esp_psram.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "driver/uart.h"

#define DO(fmt, ...) printf("[DO] " fmt "\n", ##__VA_ARGS__)

// Am luong tran (% bien do so toi da): tai nguoi thu gan loa -> de thap. Khong tang khi chua hoi Tuan.
#define VOL_MAX        30
#define SAMPLE_RATE    16000
#define TONE_HZ        1000
#define TONE_MS        1500
#define REC_MS         3000
#define WIN_MS         500
#define BTN_WATCH_MS   15000
#define PIN_PA         21
#define PIN_MCLK       0
#define PIN_DIN        35
#define AMP_MAX        (32767 * VOL_MAX / 100)
#define OUT_VOL_REG    0x18   // 0..33 (0x21), moi nac 1,5 dB; 0x18 = thap hon muc toi da ~13,5 dB

// ---- thanh ghi ES8388 (datasheet Everest ES8388; trinh tu theo ESP-ADF components/audio_hal/driver/es8388/es8388.c) ----
#define ES_CONTROL1     0x00
#define ES_CONTROL2     0x01
#define ES_CHIPPOWER    0x02
#define ES_ADCPOWER     0x03
#define ES_DACPOWER     0x04
#define ES_MASTERMODE   0x08
#define ES_ADCCONTROL1  0x09
#define ES_ADCCONTROL2  0x0A
#define ES_ADCCONTROL3  0x0B
#define ES_ADCCONTROL4  0x0C
#define ES_ADCCONTROL5  0x0D
#define ES_ADCCONTROL8  0x10
#define ES_ADCCONTROL9  0x11
#define ES_ADCCONTROL10 0x12
#define ES_ADCCONTROL11 0x13
#define ES_ADCCONTROL12 0x14
#define ES_ADCCONTROL13 0x15
#define ES_ADCCONTROL14 0x16
#define ES_DACCONTROL1  0x17
#define ES_DACCONTROL2  0x18
#define ES_DACCONTROL3  0x19
#define ES_DACCONTROL4  0x1A
#define ES_DACCONTROL5  0x1B
#define ES_DACCONTROL16 0x26
#define ES_DACCONTROL17 0x27
#define ES_DACCONTROL20 0x2A
#define ES_DACCONTROL21 0x2B
#define ES_DACCONTROL23 0x2D
#define ES_LOUT1VOL     0x2E
#define ES_ROUT1VOL     0x2F
#define ES_LOUT2VOL     0x30
#define ES_ROUT2VOL     0x31

typedef struct {
    const char *name;
    int scl, sda;
    int bck, ws, dout;
} pinset_t;

static const pinset_t SET_V1 = { "ES8388 v1", 32, 33, 27, 25, 26 };
static const pinset_t SET_V2 = { "ES8388 v2", 23, 18, 5, 25, 26 };
static const pinset_t SET_AC = { "AC101", 32, 33, 27, 26, 25 };

static const int BTN_PINS[6] = { 36, 13, 19, 23, 18, 5 };

static i2c_master_bus_handle_t s_bus;
static i2c_master_dev_handle_t s_es;
static i2s_chan_handle_t s_tx, s_rx;
static int16_t *s_rec;              // mono, REC_MS
static size_t s_rec_frames;
static int s_rms_l = -1, s_rms_r = -1;
static int s_es_addr;
static bool s_codec_ready;
static const pinset_t *s_set;

// ---------------------------------------------------------------- I2C
static bool bus_open(int scl, int sda)
{
    i2c_master_bus_config_t cfg = {
        .i2c_port = -1,
        .sda_io_num = sda,
        .scl_io_num = scl,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    return i2c_new_master_bus(&cfg, &s_bus) == ESP_OK;
}

static void bus_close(void)
{
    if (s_bus) {
        i2c_del_master_bus(s_bus);
        s_bus = NULL;
    }
}

// Quet 0x08..0x77, in dia chi ACK. Tra ve bit: 1 = co 0x10/0x11, 2 = co 0x1A.
static int scan_bus(int scl, int sda, int *es_addr)
{
    int res = 0, n = 0;
    if (!bus_open(scl, sda)) {
        DO("I2C %d/%d: khong mo duoc bus", scl, sda);
        return 0;
    }
    for (int a = 0x08; a <= 0x77; a++) {
        if (i2c_master_probe(s_bus, a, 50) == ESP_OK) {
            n++;
            if (a == 0x10 || a == 0x11) {
                DO("I2C %d/%d: ACK 0x%02X  <- ES8388", scl, sda, a);
                res |= 1;
                *es_addr = a;
            } else if (a == 0x1A) {
                DO("I2C %d/%d: ACK 0x%02X  <- AC101", scl, sda, a);
                res |= 2;
            } else {
                DO("I2C %d/%d: ACK 0x%02X", scl, sda, a);
            }
        }
    }
    if (n == 0) {
        DO("I2C %d/%d: khong thiet bi nao ACK", scl, sda);
    }
    bus_close();
    return res;
}

static esp_err_t es_write(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = { reg, val };
    return i2c_master_transmit(s_es, b, 2, 100);
}

static int es_read(uint8_t reg)
{
    uint8_t v = 0;
    if (i2c_master_transmit_receive(s_es, &reg, 1, &v, 1, 100) != ESP_OK) {
        return -1;
    }
    return v;
}

// ---------------------------------------------------------------- ES8388
// Chuoi thanh ghi toi thieu: slave mode, I2S 16-bit, MCLK/Fs=256, DAC -> LOUT/ROUT 1+2, ADC mic PGA +24 dB.
// Nguon: ESP-ADF es8388.c (es8388_init + es8388_start), doi chieu ten thanh ghi voi datasheet ES8388. Tong hop tu tri nho
// (khong tai ma nguon luc viet) -> ket qua that tren mach moi la chuan.
static int es_init_regs(void)
{
    int err = 0;
#define W(r, v) do { if (es_write((r), (v)) != ESP_OK) { err++; } } while (0)
    W(ES_DACCONTROL3, 0x04);      // mute DAC khi cau hinh
    W(ES_CONTROL2, 0x50);
    W(ES_CHIPPOWER, 0x00);
    W(ES_MASTERMODE, 0x00);       // slave (MCLK tu GPIO0)
    W(ES_DACPOWER, 0x3E);         // bat DAC + LOUT1/ROUT1/LOUT2/ROUT2
    W(ES_CONTROL1, 0x12);
    W(ES_DACCONTROL1, 0x18);      // I2S, 16-bit
    W(ES_DACCONTROL2, 0x02);      // ty le 256
    W(ES_DACCONTROL16, 0x00);
    W(ES_DACCONTROL17, 0x90);     // DAC trai -> mixer trai
    W(ES_DACCONTROL20, 0x90);     // DAC phai -> mixer phai
    W(ES_DACCONTROL21, 0x80);
    W(ES_DACCONTROL23, 0x00);
    W(ES_DACCONTROL4, 0x00);      // DAC digital 0 dB
    W(ES_DACCONTROL5, 0x00);
    W(ES_LOUT1VOL, OUT_VOL_REG);
    W(ES_ROUT1VOL, OUT_VOL_REG);
    W(ES_LOUT2VOL, OUT_VOL_REG);
    W(ES_ROUT2VOL, OUT_VOL_REG);
    // ADC
    W(ES_ADCPOWER, 0xFF);
    W(ES_ADCCONTROL1, 0xBB);      // mic PGA +24 dB hai kenh
    W(ES_ADCCONTROL2, 0x50);      // mac dinh LINPUT2/RINPUT2 (se tu chon lai khi thu)
    W(ES_ADCCONTROL3, 0x02);
    W(ES_ADCCONTROL4, 0x0C);      // I2S, 16-bit
    W(ES_ADCCONTROL5, 0x02);      // ty le 256
    W(ES_ADCCONTROL8, 0x00);      // ADC digital 0 dB
    W(ES_ADCCONTROL9, 0x00);
    W(ES_ADCCONTROL10, 0x22);
    W(ES_ADCCONTROL11, 0xA0);
    W(ES_ADCCONTROL12, 0x12);
    W(ES_ADCCONTROL13, 0x06);
    W(ES_ADCCONTROL14, 0xC3);
    // start: reset may trang thai, bat ADC, mo mute DAC
    W(ES_CHIPPOWER, 0xF0);
    W(ES_CHIPPOWER, 0x00);
    W(ES_ADCPOWER, 0x00);
    W(ES_DACPOWER, 0x3C);
    W(ES_DACCONTROL3, 0x00);
#undef W
    return err;
}

// ---------------------------------------------------------------- I2S
static bool i2s_open(const pinset_t *p)
{
    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    cc.auto_clear = true;
    if (i2s_new_channel(&cc, &s_tx, &s_rx) != ESP_OK) {
        return false;
    }
    i2s_std_config_t sc = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = {
            .mclk = PIN_MCLK,
            .bclk = p->bck,
            .ws = p->ws,
            .dout = p->dout,
            .din = PIN_DIN,
        },
    };
    sc.clk_cfg.mclk_multiple = I2S_MCLK_MULTIPLE_256;
    if (i2s_channel_init_std_mode(s_tx, &sc) != ESP_OK || i2s_channel_init_std_mode(s_rx, &sc) != ESP_OK) {
        return false;
    }
    return i2s_channel_enable(s_tx) == ESP_OK;
}

// ---------------------------------------------------------------- bip + thu + phat lai
static void write_frames(const int16_t *stereo, size_t frames)
{
    size_t done = 0, bytes = frames * 4;
    const uint8_t *p = (const uint8_t *)stereo;
    while (done < bytes) {
        size_t w = 0;
        if (i2s_channel_write(s_tx, p + done, bytes - done, &w, 1000) != ESP_OK) {
            DO("i2s write loi");
            return;
        }
        done += w;
    }
}

static void play_beep(void)
{
    int16_t tab[SAMPLE_RATE / TONE_HZ];
    int period = SAMPLE_RATE / TONE_HZ;
    for (int i = 0; i < period; i++) {
        tab[i] = (int16_t)(AMP_MAX * sinf(2.0f * 3.14159265f * i / period));
    }
    size_t total = (size_t)SAMPLE_RATE * TONE_MS / 1000, ramp = 160, idx = 0;
    int16_t buf[256 * 2];
    while (idx < total) {
        size_t n = total - idx > 256 ? 256 : total - idx;
        for (size_t i = 0; i < n; i++) {
            size_t k = idx + i;
            int32_t s = tab[k % period];
            if (k < ramp) {
                s = s * (int32_t)k / (int32_t)ramp;
            } else if (total - k < ramp) {
                s = s * (int32_t)(total - k) / (int32_t)ramp;
            }
            buf[2 * i] = (int16_t)s;
            buf[2 * i + 1] = (int16_t)s;
        }
        write_frames(buf, n);
        idx += n;
    }
}

// Doc `frames` khung stereo, tinh tong binh phuong/peak moi kenh. Neu dst != NULL luu mono (L+R)/2.
typedef struct {
    double sq[2];
    int peak[2];
    size_t n;
} stat_t;

static void read_frames(size_t frames, int16_t *dst, stat_t *st)
{
    int16_t buf[256 * 2];
    size_t got = 0;
    while (got < frames) {
        size_t want = frames - got > 256 ? 256 : frames - got, r = 0;
        if (i2s_channel_read(s_rx, buf, want * 4, &r, 1000) != ESP_OK) {
            DO("i2s read loi");
            return;
        }
        size_t n = r / 4;
        for (size_t i = 0; i < n; i++) {
            for (int c = 0; c < 2; c++) {
                int v = buf[2 * i + c];
                st->sq[c] += (double)v * v;
                int a = v < 0 ? -v : v;
                if (a > st->peak[c]) {
                    st->peak[c] = a;
                }
            }
            if (dst) {
                dst[got + i] = (int16_t)(((int)buf[2 * i] + (int)buf[2 * i + 1]) / 2);
            }
        }
        st->n += n;
        got += n;
    }
}

static int rms_of(const stat_t *st, int c)
{
    return st->n ? (int)sqrt(st->sq[c] / (double)st->n) : 0;
}

static void record_and_play(void)
{
    // 1) chon dau vao micro: thu thu 0,5 s tren LINPUT2 (0x50) va LINPUT1 (0x00), lay kenh manh hon
    es_write(ES_ADCCONTROL2, 0x50);
    stat_t warm = { 0 };
    read_frames(SAMPLE_RATE / 2, NULL, &warm);
    int best_in = 0x50, best_e = -1;
    const uint8_t ins[2] = { 0x50, 0x00 };
    const char *names[2] = { "LIN2/RIN2", "LIN1/RIN1" };
    for (int k = 0; k < 2; k++) {
        es_write(ES_ADCCONTROL2, ins[k]);
        stat_t settle = { 0 };
        read_frames(SAMPLE_RATE * 3 / 10, NULL, &settle);   // bo 0,3 s: ADC on dinh sau khi doi dau vao
        stat_t t = { 0 };
        read_frames(SAMPLE_RATE / 2, NULL, &t);
        int e = rms_of(&t, 0) + rms_of(&t, 1);
        DO("thu thu dau vao %s: rms L=%d R=%d", names[k], rms_of(&t, 0), rms_of(&t, 1));
        // uu tien LIN2 (A1S): chi doi sang LIN1 neu manh hon > 2 lan
        if (best_e < 0 || e > 2 * best_e) {
            best_e = e;
            best_in = ins[k];
        }
    }
    es_write(ES_ADCCONTROL2, (uint8_t)best_in);
    DO("chon dau vao micro: %s", best_in == 0x50 ? names[0] : names[1]);

    // 2) thu 3 s, in rms/peak moi 0,5 s
    DO("Thu micro %d ms - hay noi/vo tay gan mach", REC_MS);
    s_rec_frames = (size_t)SAMPLE_RATE * REC_MS / 1000;
    if (!s_rec) {
        s_rec = heap_caps_malloc(s_rec_frames * sizeof(int16_t), MALLOC_CAP_8BIT);
    }
    stat_t all = { 0 };
    size_t win = (size_t)SAMPLE_RATE * WIN_MS / 1000;
    for (size_t off = 0; off < s_rec_frames; off += win) {
        stat_t w = { 0 };
        read_frames(win, s_rec ? s_rec + off : NULL, &w);
        all.sq[0] += w.sq[0];
        all.sq[1] += w.sq[1];
        all.n += w.n;
        for (int c = 0; c < 2; c++) {
            if (w.peak[c] > all.peak[c]) {
                all.peak[c] = w.peak[c];
            }
        }
        DO("mic %4u ms: rms L=%d R=%d  peak L=%d R=%d", (unsigned)(off * 1000 / SAMPLE_RATE),
           rms_of(&w, 0), rms_of(&w, 1), w.peak[0], w.peak[1]);
    }
    s_rms_l = rms_of(&all, 0);
    s_rms_r = rms_of(&all, 1);
    DO("mic tong: rms L=%d R=%d  peak L=%d R=%d", s_rms_l, s_rms_r, all.peak[0], all.peak[1]);

    // 3) phat lai: chuan hoa dinh ve bien do tran AMP_MAX (khuech toi da 30x)
    if (!s_rec) {
        DO("khong du heap de phat lai (malloc that bai)");
        return;
    }
    int peak = 1;
    for (size_t i = 0; i < s_rec_frames; i++) {
        int a = s_rec[i] < 0 ? -s_rec[i] : s_rec[i];
        if (a > peak) {
            peak = a;
        }
    }
    float gain = (float)AMP_MAX / (float)peak;
    if (gain > 30.0f) {
        gain = 30.0f;
    }
    DO("Phat lai %d ms vua thu (gain %.1fx, tran %d%%) - Tuan nghe xac nhan", REC_MS, (double)gain, VOL_MAX);
    int16_t buf[256 * 2];
    size_t idx = 0;
    while (idx < s_rec_frames) {
        size_t n = s_rec_frames - idx > 256 ? 256 : s_rec_frames - idx;
        for (size_t i = 0; i < n; i++) {
            int v = (int)(s_rec[idx + i] * gain);
            if (v > AMP_MAX) {
                v = AMP_MAX;
            } else if (v < -AMP_MAX) {
                v = -AMP_MAX;
            }
            buf[2 * i] = (int16_t)v;
            buf[2 * i + 1] = (int16_t)v;
        }
        write_frames(buf, n);
        idx += n;
    }
}

// ---------------------------------------------------------------- nut bam
static bool btn_skipped(int pin)
{
    if (!s_set) {
        return false;
    }
    return pin == s_set->scl || pin == s_set->sda || pin == s_set->bck || pin == s_set->ws ||
           pin == s_set->dout || pin == PIN_DIN || pin == PIN_MCLK;
}

static void buttons_init(void)
{
    for (int i = 0; i < 6; i++) {
        int pin = BTN_PINS[i];
        if (btn_skipped(pin)) {
            DO("nut GPIO%d: bo qua (dang dung cho I2C/I2S cua bo %s)", pin, s_set->name);
            continue;
        }
        gpio_config_t g = {
            .pin_bit_mask = 1ULL << pin,
            .mode = GPIO_MODE_INPUT,
            // GPIO36/39 chi vao, khong co pull-up trong
            .pull_up_en = (pin == 36 || pin == 39) ? GPIO_PULLUP_DISABLE : GPIO_PULLUP_ENABLE,
        };
        gpio_config(&g);
    }
}

// ---------------------------------------------------------------- lenh UART: REC <giay> <in>, BEEP
static volatile int s_cmd;          // 0 khong, 1 REC, 2 BEEP
static volatile int s_cmd_sec, s_cmd_in;

static void uart_cmd_task(void *arg)
{
    (void)arg;
    char line[64];
    int n = 0;
    while (true) {
        uint8_t c;
        if (uart_read_bytes(UART_NUM_0, &c, 1, pdMS_TO_TICKS(100)) != 1) {
            continue;
        }
        if (c != 10 && c != 13) {
            if (n < (int)sizeof(line) - 1) {
                line[n++] = (char)c;
            }
            continue;
        }
        line[n] = 0;
        n = 0;
        int sec = 0, in = 0;
        if (sscanf(line, "REC %d %d", &sec, &in) == 2 && sec >= 1 && sec <= 8 && (in == 1 || in == 2)) {
            s_cmd_sec = sec;
            s_cmd_in = in;
            s_cmd = 1;
        } else if (strncmp(line, "BEEP", 4) == 0) {
            s_cmd = 2;
        } else if (line[0]) {
            DO("lenh la: %s (dung: REC <1-8> <1|2>, BEEP)", line);
        }
    }
}

static uint32_t crc32_upd(uint32_t crc, const uint8_t *d, size_t n)
{
    crc = ~crc;
    for (size_t i = 0; i < n; i++) {
        crc ^= d[i];
        for (int k = 0; k < 8; k++) {
            crc = (crc >> 1) ^ (0xEDB88320u & (0u - (crc & 1u)));
        }
    }
    return ~crc;
}

static void b64_line(const uint8_t *d, size_t n)
{
    static const char T[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    char out[80];
    size_t o = 0;
    for (size_t i = 0; i < n; i += 3) {
        uint32_t v = (uint32_t)d[i] << 16;
        if (i + 1 < n) {
            v |= (uint32_t)d[i + 1] << 8;
        }
        if (i + 2 < n) {
            v |= d[i + 2];
        }
        out[o++] = T[(v >> 18) & 63];
        out[o++] = T[(v >> 12) & 63];
        out[o++] = i + 1 < n ? T[(v >> 6) & 63] : '=';
        out[o++] = i + 2 < n ? T[v & 63] : '=';
    }
    out[o] = 0;
    puts(out);
}

// Thu `sec` giay mono 16 kHz tu dau vao `in` (1 = LIN1/RIN1, 2 = LIN2/RIN2), gui base64 qua UART.
static void do_rec(int sec, int in)
{
    size_t frames = (size_t)SAMPLE_RATE * sec;
    int16_t *buf = heap_caps_malloc(frames * sizeof(int16_t), MALLOC_CAP_8BIT);
    if (!buf) {
        DO("REC: khong du heap");
        return;
    }
    es_write(ES_ADCCONTROL2, in == 1 ? 0x00 : 0x50);
    stat_t settle = { 0 };
    read_frames(SAMPLE_RATE * 3 / 10, NULL, &settle);
    stat_t st = { 0 };
    read_frames(frames, buf, &st);
    const uint8_t *raw = (const uint8_t *)buf;
    size_t bytes = frames * sizeof(int16_t);
    uint32_t crc = crc32_upd(0, raw, bytes);
    printf("[REC] BEGIN %u" "\x0a", (unsigned)bytes);
    for (size_t off = 0; off < bytes; off += 57) {
        b64_line(raw + off, bytes - off > 57 ? 57 : bytes - off);
        if ((off / 57) % 8 == 7) {
            vTaskDelay(1);   // nhuong IDLE0, tranh task watchdog khi in nhieu qua UART
        }
    }
    printf("[REC] END %08x" "\x0a", (unsigned)crc);
    free(buf);
}

static void poll_cmd(void)
{
    int c = s_cmd;
    if (!c || !s_codec_ready) {
        s_cmd = 0;
        return;
    }
    s_cmd = 0;
    if (c == 1) {
        do_rec(s_cmd_sec, s_cmd_in);
    } else {
        gpio_set_level(PIN_PA, 1);
        DO("BEEP %d Hz", TONE_HZ);
        play_beep();
        gpio_set_level(PIN_PA, 0);
    }
}

// Doc nut lien tuc (ms < 0: mai mai), log [NUT] khi doi trang thai, dong thoi xu ly lenh UART.
static void watch_buttons(int ms)
{
    int last[6];
    for (int i = 0; i < 6; i++) {
        last[i] = btn_skipped(BTN_PINS[i]) ? -1 : gpio_get_level(BTN_PINS[i]);
    }
    int64_t t0 = esp_timer_get_time();
    while (ms < 0 || (esp_timer_get_time() - t0) / 1000 < ms) {
        for (int i = 0; i < 6; i++) {
            if (last[i] < 0) {
                continue;
            }
            int v = gpio_get_level(BTN_PINS[i]);
            if (v != last[i]) {
                vTaskDelay(pdMS_TO_TICKS(30));   // chong rung
                v = gpio_get_level(BTN_PINS[i]);
            }
            if (v != last[i]) {
                last[i] = v;
                printf("[NUT] %d GPIO%d %s" "\x0a", i + 1, BTN_PINS[i], v ? "nha" : "nhan");
            }
        }
        poll_cmd();
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

// ---------------------------------------------------------------- main
void app_main(void)
{
    uart_driver_install(UART_NUM_0, 1024, 0, 0, NULL, 0);
    vTaskDelay(pdMS_TO_TICKS(500));
    gpio_config_t pa = { .pin_bit_mask = 1ULL << PIN_PA, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&pa);
    gpio_set_level(PIN_PA, 0);   // PA tat cho toi khi codec san sang

    // 1) chip / flash / PSRAM / heap
    esp_chip_info_t ci;
    esp_chip_info(&ci);
    uint32_t flash = 0;
    esp_flash_get_physical_size(NULL, &flash);
    DO("chip: model=%d cores=%d rev=v%d.%d", (int)ci.model, ci.cores, ci.revision / 100, ci.revision % 100);
    DO("flash that: %u KB", (unsigned)(flash / 1024));
    size_t psram = esp_psram_is_initialized() ? esp_psram_get_size() : 0;
    if (psram) {
        DO("PSRAM: %u KB", (unsigned)(psram / 1024));
    } else {
        DO("PSRAM: khong co");
    }
    DO("heap trong: %u B (8bit), toi da 1 khoi %u B", (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
       (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT));

    // 2) quet I2C 2 bo chan
    int es_a = 0, es_b = 0;
    int ra = scan_bus(32, 33, &es_a);
    int rb = scan_bus(23, 18, &es_b);

    const char *codec = "khong thay";
    if ((ra & 1) && !(rb & 1)) {
        s_set = &SET_V1;
        s_es_addr = es_a;
    } else if (rb & 1) {
        s_set = &SET_V2;
        s_es_addr = es_b;
    } else if (ra & 2) {
        s_set = &SET_AC;
    }
    char codec_str[24];
    if (s_set == &SET_V1 || s_set == &SET_V2) {
        snprintf(codec_str, sizeof(codec_str), "ES8388@0x%02X", s_es_addr);
        codec = codec_str;
    } else if (s_set == &SET_AC) {
        codec = "AC101@0x1A";
    }
    if (s_set) {
        DO("bo chan khop: %s (I2C %d/%d, I2S 0/%d/%d/%d/%d)", s_set->name, s_set->scl, s_set->sda, s_set->bck,
           s_set->ws, s_set->dout, PIN_DIN);
    } else {
        DO("khong thay codec tren 2 bo chan I2C - dung o buoc 2");
    }

    // 3) init codec (chi ES8388)
    if (s_set == &SET_AC) {
        DO("AC101 - chua ho tro phat");
    } else if (s_set) {
        if (!bus_open(s_set->scl, s_set->sda)) {
            DO("khong mo lai duoc I2C %d/%d", s_set->scl, s_set->sda);
        } else {
            i2c_device_config_t dc = {
                .dev_addr_length = I2C_ADDR_BIT_LEN_7,
                .device_address = s_es_addr,
                .scl_speed_hz = 100000,
            };
            if (i2c_master_bus_add_device(s_bus, &dc, &s_es) != ESP_OK) {
                DO("khong them duoc thiet bi I2C 0x%02X", s_es_addr);
            } else {
                DO("ES8388 CONTROL1 (0x00) doc duoc = 0x%02X (reset 0x06)", es_read(ES_CONTROL1));
                int err = es_init_regs();
                DO("ES8388 init: %d loi ghi; CHIPPOWER=0x%02X DACPOWER=0x%02X ADCCONTROL4=0x%02X", err,
                   es_read(ES_CHIPPOWER), es_read(ES_DACPOWER), es_read(ES_ADCCONTROL4));
                if (err == 0 && i2s_open(s_set)) {
                    s_codec_ready = true;
                    DO("I2S 16 kHz 16-bit Philips: MCLK=%d BCK=%d WS=%d DOUT=%d DIN=%d", PIN_MCLK, s_set->bck,
                       s_set->ws, s_set->dout, PIN_DIN);
                } else {
                    DO("ES8388 / I2S khong san sang");
                }
            }
        }
    }

    // 4)+5) bip, thu, phat lai
    if (s_codec_ready) {
        gpio_set_level(PIN_PA, 1);
        DO("PA GPIO%d = cao", PIN_PA);
        if (i2s_channel_enable(s_rx) != ESP_OK) {
            DO("khong bat duoc kenh RX");
            s_codec_ready = false;
        } else {
            DO("Bip %d Hz %d ms, bien do tran %d%% - nghe thay tieng?", TONE_HZ, TONE_MS, VOL_MAX);
            play_beep();
            record_and_play();
        }
        gpio_set_level(PIN_PA, 0);
    }

    // 6) nut bam
    xTaskCreate(uart_cmd_task, "uartcmd", 3072, NULL, 5, NULL);
    buttons_init();
    DO("Doc 6 nut trong %d s (36,13,19,23,18,5; active low)...", BTN_WATCH_MS / 1000);
    watch_buttons(BTN_WATCH_MS);

    // 7) tong ket
    char i2c_str[16] = "na", i2s_str[32] = "na", mic_str[24] = "na";
    if (s_set) {
        snprintf(i2c_str, sizeof(i2c_str), "%d/%d", s_set->scl, s_set->sda);
        snprintf(i2s_str, sizeof(i2s_str), "%d/%d/%d/%d/%d", PIN_MCLK, s_set->bck, s_set->ws, s_set->dout, PIN_DIN);
    }
    if (s_rms_l >= 0) {
        snprintf(mic_str, sizeof(mic_str), "%d/%d", s_rms_l, s_rms_r);
    }
    printf("[KQ] psram=%u codec=%s i2c=%s i2s=%s pa=%d mic_rms=%s\n", (unsigned)(psram / (1024 * 1024)), codec,
           i2c_str, i2s_str, PIN_PA, mic_str);

    // idle: log nut lien tuc + lenh UART (REC <giay> <in>, BEEP)
    DO("Idle. Lenh UART: REC <1-8> <1|2>, BEEP. Nut bam duoc log [NUT].");
    watch_buttons(-1);
}
