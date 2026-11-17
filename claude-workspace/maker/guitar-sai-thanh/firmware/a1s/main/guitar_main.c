// Firmware v0.1: thay the mach dan GUITAR UMI tren ESP32-A1S (LINE IN -> ES8388 -> DSP -> loa/tai nghe),
// gia lap giao thuc BLE cua dan goc de app Umi Music ket noi duoc. Xem ../spec-v01.md.
// Khong dung ma RudeBox. Trinh tu ES8388 lay lai tu tools/esp32-a1s/probe.
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "driver/uart.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "nimble/nimble_port.h"
#include "nimble/nimble_port_freertos.h"
#include "host/ble_hs.h"
#include "host/util/util.h"
#include "services/gap/ble_svc_gap.h"
#include "services/gatt/ble_svc_gatt.h"
#include "umi_proto.h"
#include "dsp.h"

#define LOG(fmt, ...) printf("[GUITAR] " fmt "\n", ##__VA_ARGS__)

// ---- cau hinh ----
#define GUITAR_BLE_NAME      "GUITAR UMI"
#define GUITAR_ADC_INPUT     1        // 1 = LIN1/RIN1 (line-in), 2 = LIN2/RIN2. TODO: xac nhan khi thu tren mach
#define GUITAR_ADC_PGA       0x00     // ADCCONTROL1: 0 dB hai kenh (line-in). TODO: chinh khi noi pickup
#define GUITAR_OUT_MAX       0.7f     // tran an toan tai/loa, nhan sau am luong (ap o tang ghi I2S)
#define GUITAR_BATT_DV       120      // TODO: A1S khong do duoc pin -> 12,0 V co dinh
#define SAMPLE_RATE          44100
#define FRAME_SAMPLES        256
#define NOTIFY_PERIOD_US     15000000LL
#define SAVE_DELAY_US        2000000LL

#define PIN_SCL   32
#define PIN_SDA   33
#define PIN_MCLK  0
#define PIN_BCK   27
#define PIN_WS    25
#define PIN_DOUT  26
#define PIN_DIN   35
#define PIN_PA    21      // ampli tren bo (PA)
#define PIN_LED   22
#define PIN_KEY5  18      // am luong -1
#define PIN_KEY6  5       // am luong +1
#define ES_ADDR   0x10
#define OUT_VOL_REG 0x18  // LOUT/ROUT 1+2, thap hon muc toi da ~13,5 dB (nhu probe)

// ---- ES8388 (trinh tu da chay tren bo nay) ----
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

static i2c_master_bus_handle_t s_bus;
static i2c_master_dev_handle_t s_es;
static i2s_chan_handle_t s_tx, s_rx;
static bool s_codec_ready;

static umi_state_t s_state;
static SemaphoreHandle_t s_mtx;        // bao ve s_state
static SemaphoreHandle_t s_dsp_mtx;    // bao ve dsp_set / dsp_process
static volatile int64_t s_save_due_us; // 0 = khong co gi can luu
static volatile int s_tone_frames;     // so khung con phat sine thu loa
// chan doan (lenh LVL, 2026-11-17): dinh vao trai/phai, so vong, doc thieu, thoi gian xu ly lon nhat (us)
static volatile int s_pk_l, s_pk_r, s_loops, s_short, s_maxus;
static volatile int s_adc_in = GUITAR_ADC_INPUT;

static uint16_t s_conn = BLE_HS_CONN_HANDLE_NONE;
static uint16_t s_h_2b10, s_h_2b16;
static uint8_t s_own_addr_type;

// ---------------------------------------------------------------- ES8388
static esp_err_t es_write(uint8_t reg, uint8_t val)
{
    uint8_t b[2] = { reg, val };
    return i2c_master_transmit(s_es, b, 2, 100);
}

// 2026-11-17: PGA 3 dB/nac (0..8 = 0..24 dB), ca 2 kenh. Mic tren bo (IN 2) can +24 dB nhu firmware do (0xBB).
static void es_set_gain(int g)
{
    if (g < 0) g = 0;
    if (g > 8) g = 8;
    es_write(ES_ADCCONTROL1, (uint8_t)((g << 4) | g));
}

static void es_select_input(int in)
{
    es_write(ES_ADCCONTROL2, in == 2 ? 0x50 : 0x00);
    if (in == 2) {
        es_set_gain(8);
    }
}

static int es_init_regs(void)
{
    int err = 0;
#define W(r, v) do { if (es_write((r), (v)) != ESP_OK) { err++; } } while (0)
    W(ES_DACCONTROL3, 0x04);      // mute DAC khi cau hinh
    W(ES_CONTROL2, 0x50);
    W(ES_CHIPPOWER, 0x00);
    W(ES_MASTERMODE, 0x00);       // slave (MCLK tu GPIO0)
    W(ES_DACPOWER, 0x3E);
    W(ES_CONTROL1, 0x12);
    W(ES_DACCONTROL1, 0x18);      // I2S, 16-bit
    W(ES_DACCONTROL2, 0x02);      // ty le 256
    W(ES_DACCONTROL16, 0x00);
    W(ES_DACCONTROL17, 0x90);
    W(ES_DACCONTROL20, 0x90);
    W(ES_DACCONTROL21, 0x80);
    W(ES_DACCONTROL23, 0x00);
    W(ES_DACCONTROL4, 0x00);
    W(ES_DACCONTROL5, 0x00);
    W(ES_LOUT1VOL, OUT_VOL_REG);
    W(ES_ROUT1VOL, OUT_VOL_REG);
    W(ES_LOUT2VOL, OUT_VOL_REG);
    W(ES_ROUT2VOL, OUT_VOL_REG);
    W(ES_ADCPOWER, 0xFF);
    W(ES_ADCCONTROL1, GUITAR_ADC_PGA);
    W(ES_ADCCONTROL2, GUITAR_ADC_INPUT == 2 ? 0x50 : 0x00);
    W(ES_ADCCONTROL3, 0x02);
    W(ES_ADCCONTROL4, 0x0C);      // I2S, 16-bit
    W(ES_ADCCONTROL5, 0x02);      // ty le 256
    W(ES_ADCCONTROL8, 0x00);
    W(ES_ADCCONTROL9, 0x00);
    W(ES_ADCCONTROL10, 0x22);
    W(ES_ADCCONTROL11, 0xA0);
    W(ES_ADCCONTROL12, 0x12);
    W(ES_ADCCONTROL13, 0x06);
    W(ES_ADCCONTROL14, 0xC3);
    W(ES_CHIPPOWER, 0xF0);
    W(ES_CHIPPOWER, 0x00);
    W(ES_ADCPOWER, 0x00);
    W(ES_DACPOWER, 0x3C);
    W(ES_DACCONTROL3, 0x00);      // mo mute
#undef W
    return err;
}

static bool codec_start(void)
{
    i2c_master_bus_config_t bc = {
        .i2c_port = -1,
        .sda_io_num = PIN_SDA,
        .scl_io_num = PIN_SCL,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .flags.enable_internal_pullup = true,
    };
    if (i2c_new_master_bus(&bc, &s_bus) != ESP_OK) {
        LOG("khong mo duoc I2C %d/%d", PIN_SCL, PIN_SDA);
        return false;
    }
    if (i2c_master_probe(s_bus, ES_ADDR, 100) != ESP_OK) {
        LOG("ES8388 0x%02X khong ACK", ES_ADDR);
        return false;
    }
    i2c_device_config_t dc = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = ES_ADDR,
        .scl_speed_hz = 100000,
    };
    if (i2c_master_bus_add_device(s_bus, &dc, &s_es) != ESP_OK) {
        LOG("khong them duoc thiet bi I2C");
        return false;
    }
    int err = es_init_regs();
    if (err) {
        LOG("ES8388 init: %d loi ghi", err);
        return false;
    }
    i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
    cc.auto_clear = true;
    if (i2s_new_channel(&cc, &s_tx, &s_rx) != ESP_OK) {
        return false;
    }
    i2s_std_config_t sc = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_STEREO),
        .gpio_cfg = { .mclk = PIN_MCLK, .bclk = PIN_BCK, .ws = PIN_WS, .dout = PIN_DOUT, .din = PIN_DIN },
    };
    sc.clk_cfg.mclk_multiple = I2S_MCLK_MULTIPLE_256;
    if (i2s_channel_init_std_mode(s_tx, &sc) != ESP_OK || i2s_channel_init_std_mode(s_rx, &sc) != ESP_OK) {
        return false;
    }
    if (i2s_channel_enable(s_tx) != ESP_OK || i2s_channel_enable(s_rx) != ESP_OK) {
        return false;
    }
    return true;
}

// ---------------------------------------------------------------- trang thai + NVS
static void apply_state_to_dsp(void)
{
    dsp_params_t p;
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    dsp_params_from_state(&s_state, &p);
    xSemaphoreGive(s_mtx);
    xSemaphoreTake(s_dsp_mtx, portMAX_DELAY);
    dsp_set(&p);
    xSemaphoreGive(s_dsp_mtx);
}

static void schedule_save(void)
{
    s_save_due_us = esp_timer_get_time() + SAVE_DELAY_US;
}

static void nvs_save_state(void)
{
    nvs_handle_t h;
    uint8_t blob[UMI_FRAME_LEN - 8];
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    memcpy(blob, s_state.p + 8, sizeof blob);
    xSemaphoreGive(s_mtx);
    if (nvs_open("guitar", NVS_READWRITE, &h) == ESP_OK) {
        nvs_set_blob(h, "p", blob, sizeof blob);
        nvs_commit(h);
        nvs_close(h);
        LOG("da luu cai dat vao NVS");
    }
}

static void nvs_load_state(void)
{
    umi_state_default(&s_state);
    nvs_handle_t h;
    uint8_t blob[UMI_FRAME_LEN - 8];
    size_t len = sizeof blob;
    if (nvs_open("guitar", NVS_READONLY, &h) == ESP_OK) {
        if (nvs_get_blob(h, "p", blob, &len) == ESP_OK && len == sizeof blob) {
            memcpy(s_state.p + 8, blob, sizeof blob);
            LOG("nap cai dat tu NVS");
        }
        nvs_close(h);
    }
}

// ---------------------------------------------------------------- BLE
static int gap_event(struct ble_gap_event *ev, void *arg);

static void start_adv(void)
{
    struct ble_hs_adv_fields f;
    memset(&f, 0, sizeof f);
    f.flags = BLE_HS_ADV_F_DISC_GEN | BLE_HS_ADV_F_BREDR_UNSUP;
    f.name = (const uint8_t *)GUITAR_BLE_NAME;
    f.name_len = (uint8_t)strlen(GUITAR_BLE_NAME);
    f.name_is_complete = 1;
    static ble_uuid16_t svc_uuid = BLE_UUID16_INIT(0x2B00);
    f.uuids16 = &svc_uuid;
    f.num_uuids16 = 1;
    f.uuids16_is_complete = 1;
    int rc = ble_gap_adv_set_fields(&f);
    if (rc != 0) {
        LOG("adv_set_fields loi %d", rc);
        return;
    }
    struct ble_gap_adv_params ap;
    memset(&ap, 0, sizeof ap);
    ap.conn_mode = BLE_GAP_CONN_MODE_UND;
    ap.disc_mode = BLE_GAP_DISC_MODE_GEN;
    rc = ble_gap_adv_start(s_own_addr_type, NULL, BLE_HS_FOREVER, &ap, gap_event, NULL);
    if (rc != 0) {
        LOG("adv_start loi %d", rc);
    }
}

// Gui khung trang thai tren ca 0x2B10 va 0x2B16, cat con (MTU - 3) byte neu MTU nho.
static void notify_state(void)
{
    uint16_t conn = s_conn;
    if (conn == BLE_HS_CONN_HANDLE_NONE) {
        return;
    }
    uint8_t st[UMI_FRAME_LEN];
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    umi_build_status(&s_state, GUITAR_BATT_DV, st);
    xSemaphoreGive(s_mtx);
    int len = (int)ble_att_mtu(conn) - 3;
    if (len > UMI_FRAME_LEN) {
        len = UMI_FRAME_LEN;
    }
    if (len < 1) {
        return;
    }
    const uint16_t hs[2] = { s_h_2b10, s_h_2b16 };
    for (int i = 0; i < 2; i++) {
        struct os_mbuf *om = ble_hs_mbuf_from_flat(st, (uint16_t)len);
        if (om) {
            ble_gatts_notify_custom(conn, hs[i], om);
        }
    }
}

// Xu ly du lieu ghi vao (tu BLE hoac UART). Tra ve ket qua umi_handle_write.
static int handle_input(const uint8_t *d, size_t n)
{
    int changed = 0;
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    int r = umi_handle_write(&s_state, d, n, &changed);
    xSemaphoreGive(s_mtx);
    if (r) {
        if (changed) {
            apply_state_to_dsp();
            schedule_save();
        }
        notify_state();
    }
    return r;
}

static int chr_access(uint16_t conn, uint16_t attr, struct ble_gatt_access_ctxt *ctxt, void *arg)
{
    (void)conn;
    (void)attr;
    (void)arg;
    if (ctxt->op != BLE_GATT_ACCESS_OP_WRITE_CHR) {
        return BLE_ATT_ERR_READ_NOT_PERMITTED;
    }
    uint8_t buf[UMI_FRAME_LEN + 8];
    uint16_t n = OS_MBUF_PKTLEN(ctxt->om);
    if (n > sizeof buf) {
        return 0;   // qua dai -> bo qua
    }
    if (ble_hs_mbuf_to_flat(ctxt->om, buf, sizeof buf, &n) != 0) {
        return BLE_ATT_ERR_UNLIKELY;
    }
    handle_input(buf, n);
    return 0;
}

static const struct ble_gatt_svc_def GATT_SVCS[] = {
    {
        .type = BLE_GATT_SVC_TYPE_PRIMARY,
        .uuid = BLE_UUID16_DECLARE(0x2B00),
        .characteristics = (struct ble_gatt_chr_def[]) {
            {
                .uuid = BLE_UUID16_DECLARE(0x2B12),
                .access_cb = chr_access,
                .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_NO_RSP,
            },
            {
                .uuid = BLE_UUID16_DECLARE(0x2B10),
                .access_cb = chr_access,
                .val_handle = &s_h_2b10,
                .flags = BLE_GATT_CHR_F_NOTIFY,
            },
            {
                .uuid = BLE_UUID16_DECLARE(0x2B16),
                .access_cb = chr_access,
                .val_handle = &s_h_2b16,
                .flags = BLE_GATT_CHR_F_WRITE | BLE_GATT_CHR_F_WRITE_NO_RSP | BLE_GATT_CHR_F_NOTIFY,
            },
            { 0 },
        },
    },
    { 0 },
};

static int gap_event(struct ble_gap_event *ev, void *arg)
{
    (void)arg;
    switch (ev->type) {
    case BLE_GAP_EVENT_CONNECT:
        if (ev->connect.status == 0) {
            s_conn = ev->connect.conn_handle;
            LOG("BLE ket noi (handle %u)", (unsigned)s_conn);
        } else {
            s_conn = BLE_HS_CONN_HANDLE_NONE;
            start_adv();
        }
        break;
    case BLE_GAP_EVENT_DISCONNECT:
        LOG("BLE ngat ket noi");
        s_conn = BLE_HS_CONN_HANDLE_NONE;
        start_adv();
        break;
    case BLE_GAP_EVENT_ADV_COMPLETE:
        start_adv();
        break;
    case BLE_GAP_EVENT_MTU:
        LOG("MTU = %u", (unsigned)ev->mtu.value);
        break;
    default:
        break;
    }
    return 0;
}

static void on_sync(void)
{
    if (ble_hs_util_ensure_addr(0) != 0 || ble_hs_id_infer_auto(0, &s_own_addr_type) != 0) {
        LOG("khong lay duoc dia chi BLE");
        return;
    }
    start_adv();
    LOG("quang ba \"%s\" (dich vu 0x2B00)", GUITAR_BLE_NAME);
}

static void host_task(void *param)
{
    (void)param;
    nimble_port_run();
    nimble_port_freertos_deinit();
}

static bool ble_start(void)
{
    if (nimble_port_init() != ESP_OK) {
        return false;
    }
    ble_hs_cfg.sync_cb = on_sync;
    ble_svc_gap_init();
    ble_svc_gatt_init();
    if (ble_gatts_count_cfg(GATT_SVCS) != 0 || ble_gatts_add_svcs(GATT_SVCS) != 0) {
        return false;
    }
    ble_svc_gap_device_name_set(GUITAR_BLE_NAME);
    nimble_port_freertos_init(host_task);
    return true;
}

// ---------------------------------------------------------------- am thanh
static void audio_task(void *arg)
{
    (void)arg;
    static int16_t inb[FRAME_SAMPLES * 2], outb[FRAME_SAMPLES * 2];
    static int16_t il[FRAME_SAMPLES], ir[FRAME_SAMPLES], ol[FRAME_SAMPLES], orr[FRAME_SAMPLES];
    // 2026-11-17: bang sine tinh 1 lan (sinf tung mau tren ESP32 cham ~30 us -> 7,8 ms/khung > 5,8 ms -> thieu I2S, xet xet)
    static int16_t sine_tab[1024];
    for (int i = 0; i < 1024; i++) {
        sine_tab[i] = (int16_t)(32767.0f * sinf(2.0f * 3.14159265f * (float)i / 1024.0f));
    }
    const uint32_t tone_step = (uint32_t)((1000.0 * 4294967296.0) / SAMPLE_RATE);   // 1 kHz, pha 32 bit
    uint32_t tone_phase = 0;
    while (true) {
        size_t got = 0;
        if (i2s_channel_read(s_rx, inb, sizeof inb, &got, 1000) != ESP_OK) {
            continue;
        }
        int n = (int)(got / 4);
        if (n <= 0) {
            continue;
        }
        int64_t t0 = esp_timer_get_time();
        if (n < FRAME_SAMPLES) {
            s_short++;
        }
        for (int i = 0; i < n; i++) {
            il[i] = inb[2 * i];
            ir[i] = inb[2 * i + 1];
            int al = il[i] < 0 ? -il[i] : il[i], ar = ir[i] < 0 ? -ir[i] : ir[i];
            if (al > s_pk_l) s_pk_l = al;
            if (ar > s_pk_r) s_pk_r = ar;
        }
        s_loops++;
        xSemaphoreTake(s_dsp_mtx, portMAX_DELAY);
        dsp_process(il, ir, ol, orr, n);
        xSemaphoreGive(s_dsp_mtx);
        if (s_tone_frames > 0) {
            // sine 1 kHz thu loa, am luong theo [15]
            xSemaphoreTake(s_mtx, portMAX_DELAY);
            float g = dsp_volume_gain(s_state.p[15]) * 0.5f;
            xSemaphoreGive(s_mtx);
            for (int i = 0; i < n; i++) {
                int16_t v = (int16_t)(g * (float)sine_tab[tone_phase >> 22]);
                tone_phase += tone_step;
                ol[i] = v;
                orr[i] = v;
            }
            s_tone_frames = s_tone_frames - 1;
        }
        for (int i = 0; i < n; i++) {
            outb[2 * i] = (int16_t)((float)ol[i] * GUITAR_OUT_MAX);
            outb[2 * i + 1] = (int16_t)((float)orr[i] * GUITAR_OUT_MAX);
        }
        int us = (int)(esp_timer_get_time() - t0);
        if (us > s_maxus) s_maxus = us;
        size_t done = 0, bytes = (size_t)n * 4;
        while (done < bytes) {
            size_t w = 0;
            if (i2s_channel_write(s_tx, (uint8_t *)outb + done, bytes - done, &w, 1000) != ESP_OK) {
                break;
            }
            done += w;
        }
    }
}

// ---------------------------------------------------------------- nut + dinh ky
static void volume_step(int d)
{
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    int v = (int)s_state.p[15] + d;
    if (v < 0) {
        v = 0;
    }
    if (v > 30) {
        v = 30;
    }
    bool ch = v != s_state.p[15];
    s_state.p[15] = (uint8_t)v;
    xSemaphoreGive(s_mtx);
    if (ch) {
        LOG("am luong = %d", v);
        apply_state_to_dsp();
        schedule_save();
        notify_state();
    }
}

static void ctl_task(void *arg)
{
    (void)arg;
    const int pins[2] = { PIN_KEY5, PIN_KEY6 };
    int stable[2] = { 1, 1 }, cnt[2] = { 0, 0 };
    int64_t last_notify = esp_timer_get_time();
    while (true) {
        for (int k = 0; k < 2; k++) {
            int lv = gpio_get_level(pins[k]);
            if (lv != stable[k]) {
                if (++cnt[k] >= 3) {   // 3 x 10 ms = chong doi 30 ms
                    stable[k] = lv;
                    cnt[k] = 0;
                    if (lv == 0) {
                        volume_step(k == 0 ? -1 : 1);
                    }
                }
            } else {
                cnt[k] = 0;
            }
        }
        int64_t now = esp_timer_get_time();
        if (s_conn != BLE_HS_CONN_HANDLE_NONE && now - last_notify >= NOTIFY_PERIOD_US) {
            last_notify = now;
            notify_state();
        }
        if (s_save_due_us && now >= s_save_due_us) {
            s_save_due_us = 0;
            nvs_save_state();
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// ---------------------------------------------------------------- UART
static void print_stat(void)
{
    xSemaphoreTake(s_mtx, portMAX_DELAY);
    LOG("STAT am luong[15]=%u am sac[19]=%u echo[27]=%u mic[25]=%u nhay day[20]=%u can bang[21]=%u am ly[22]=%u 3D[45]=%u LED[8]=%u mau[11]=0x%02X",
        s_state.p[15], s_state.p[19], s_state.p[27], s_state.p[25], s_state.p[20], s_state.p[21],
        s_state.p[22], s_state.p[45], s_state.p[8], s_state.p[11]);
    xSemaphoreGive(s_mtx);
    LOG("ngo vao ADC = %d, BLE %s", (int)s_adc_in, s_conn == BLE_HS_CONN_HANDLE_NONE ? "chua ket noi" : "da ket noi");
}

static void uart_cmd_line(const char *line)
{
    int idx = 0, val = 0, in = 0;
    if (strncmp(line, "STAT", 4) == 0) {
        print_stat();
    } else if (sscanf(line, "SET %d %d", &idx, &val) == 2 && idx >= 8 && idx < UMI_FRAME_LEN && val >= 0 && val <= 255) {
        uint8_t f[UMI_FRAME_LEN];
        xSemaphoreTake(s_mtx, portMAX_DELAY);
        memcpy(f, s_state.p, sizeof f);
        xSemaphoreGive(s_mtx);
        f[0] = 0x03;
        f[1] = 0x00;
        f[2] = 0x01;
        f[3] = 0x00;
        f[idx] = (uint8_t)val;
        handle_input(f, sizeof f);
        print_stat();
    } else if (sscanf(line, "IN %d", &in) == 1 && (in == 1 || in == 2)) {
        s_adc_in = in;
        if (s_codec_ready) {
            es_select_input(in);
        }
        LOG("ngo vao ADC = %d (%s)", in, in == 1 ? "LIN1/RIN1" : "LIN2/RIN2");
    } else if (sscanf(line, "GAIN %d", &val) == 1) {
        es_set_gain(val);
        LOG("PGA ngo vao = %d dB (nac %d)", (val < 0 ? 0 : val > 8 ? 8 : val) * 3, val);
    } else if (strncmp(line, "LVL", 3) == 0) {
        s_pk_l = s_pk_r = s_loops = s_short = s_maxus = 0;
        vTaskDelay(pdMS_TO_TICKS(1000));
        LOG("LVL 1 s: dinh vao L=%d R=%d | vong=%d (can ~%d) doc_thieu=%d | xu ly max %d us (khung %d us)",
            s_pk_l, s_pk_r, s_loops, SAMPLE_RATE / FRAME_SAMPLES, s_short, s_maxus, FRAME_SAMPLES * 1000000 / SAMPLE_RATE);
    } else if (strncmp(line, "TONE", 4) == 0) {
        s_tone_frames = 2 * SAMPLE_RATE / FRAME_SAMPLES;
        LOG("phat sine 1 kHz 2 s");
    } else if (line[0]) {
        LOG("lenh la: %s (dung: STAT, SET <idx> <val>, IN 1|2, TONE)", line);
    }
}

static void uart_task(void *arg)
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
        uart_cmd_line(line);
    }
}

// ---------------------------------------------------------------- main
void app_main(void)
{
    uart_driver_install(UART_NUM_0, 1024, 0, 0, NULL, 0);
    s_mtx = xSemaphoreCreateMutex();
    s_dsp_mtx = xSemaphoreCreateMutex();

    gpio_config_t pa = { .pin_bit_mask = 1ULL << PIN_PA, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&pa);
    gpio_set_level(PIN_PA, 0);   // PA tat cho toi khi codec san sang
    gpio_config_t led = { .pin_bit_mask = 1ULL << PIN_LED, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&led);
    gpio_config_t keys = {
        .pin_bit_mask = (1ULL << PIN_KEY5) | (1ULL << PIN_KEY6),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&keys);

    esp_err_t e = nvs_flash_init();
    if (e == ESP_ERR_NVS_NO_FREE_PAGES || e == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        nvs_flash_erase();
        nvs_flash_init();
    }
    nvs_load_state();

    if (dsp_init(SAMPLE_RATE) != 0) {
        LOG("dsp_init that bai (het bo nho)");
        return;
    }
    apply_state_to_dsp();

    s_codec_ready = codec_start();
    if (s_codec_ready) {
        gpio_set_level(PIN_PA, 1);
        gpio_set_level(PIN_LED, 1);
        xTaskCreate(audio_task, "audio", 6144, NULL, 10, NULL);
        LOG("codec san sang: I2S %d Hz, PA GPIO%d bat", SAMPLE_RATE, PIN_PA);
    } else {
        LOG("codec KHONG san sang - chi chay BLE/UART");
    }

    if (!ble_start()) {
        LOG("khoi dong BLE that bai");
    }
    xTaskCreate(ctl_task, "ctl", 4096, NULL, 5, NULL);
    xTaskCreate(uart_task, "uartcmd", 4096, NULL, 4, NULL);
    LOG("v0.1 chay. Lenh UART: STAT, SET <idx> <val>, IN 1|2, TONE");
}
