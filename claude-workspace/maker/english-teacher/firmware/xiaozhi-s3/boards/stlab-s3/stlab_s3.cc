#include "wifi_board.h"
#include "stlab_loopback_codec.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "led/single_led.h"
#include "power_save_timer.h"
#include "backlight.h"
#include "owl_eyes_display.h"
#include "mcp_server.h"
#include "assets/lang_config.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>
#include <esp_timer.h>
#include <driver/spi_common.h>
#include <driver/gpio.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_panel_ops.h>
#include <esp_lcd_panel_vendor.h>
#include <esp_lcd_ili9341.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#define TAG "StlabS3"

// Log do AEC moi ~5 s khi co dang noi: RMS mic, RMS tham chieu, RMS sau AFE (AFE goi ham nay qua patch 0002).
// Dung de chinh STLAB_AEC_REF_DELAY_MS: sau AFE phai nho hon mic nhieu khi chi co loa phat (khong ai noi).
extern "C" void stlab_afe_out_hook(const int16_t* data, size_t samples) {
    auto& st = GetStlabAecStats();
    uint64_t sq = 0;
    for (size_t i = 0; i < samples; i++) {
        sq += (uint64_t)((int64_t)data[i] * data[i]);
    }
    st.out_sq += sq;
    st.out_n += samples;
    int64_t now = esp_timer_get_time();
    if (now - st.last_log_us.load() < 5000000) {
        return;
    }
    st.last_log_us.store(now);
    uint64_t mn = st.mic_n.exchange(0), msq = st.mic_sq.exchange(0);
    uint64_t rn = st.ref_n.exchange(0), rsq = st.ref_sq.exchange(0);
    uint64_t on = st.out_n.exchange(0), osq = st.out_sq.exchange(0);
    if (now - st.last_play_us.load() > 1000000) {
        return;   // loa im: khong can log
    }
    auto rms = [](uint64_t s, uint64_t n) { return n ? (int)std::sqrt((double)s / (double)n) : 0; };
    ESP_LOGI("AEC", "[AEC] delay=%d ms rms mic=%d ref=%d afe_out=%d clip=%u", st.delay_ms.load(),
             rms(msq, mn), rms(rsq, rn), rms(osq, on), (unsigned)st.clip_n.exchange(0));
}

class StlabS3Board : public WifiBoard {
private:
    Button talk_button_;   // GPIO1: switch MX ngoai vo (2 chan GPIO-GND, pull-up noi)
    Button boot_button_;   // GPIO0: nut BOOT tren devkit, chi de thu tren ban
    SingleLed* led_ = nullptr;
    OwlEyesDisplay* display_ = nullptr;   // nullptr neu khong dung duoc man -> NoDisplay, bo van chay
    PowerSaveTimer* power_save_timer_ = nullptr;
    volatile bool sleeping_ = false;
    volatile bool bye_pending_ = false;   // da xin ket thuc, dang cho co chao tam biet
    int64_t last_press_us_ = 0;           // chong doi phim cho phan ung luc nhan xuong
    volatile bool seen_release_ = false;  // da thay tha nut it nhat 1 lan tu luc bat may

    // Co ngu cua bo + mat Cu Bong (nham mat, den nen xuong 8 %)
    void SetSleeping(bool on) {
        sleeping_ = on;
        if (display_ != nullptr) {
            display_->SetPowerSaveMode(on);
        }
    }

    // Tat den + ampli loa (dung chung cho ngu tu dong va ngu do giu nut)
    void SleepOutputs() {
        if (led_ != nullptr) {
            led_->OnStateChanged();
        }
        GetAudioCodec()->EnableOutput(false);
    }

    // Tu ngu sau STLAB_IDLE_SLEEP_S giay khong giao tiep; cpu_max_freq = -1: khong doi xung nhip, khong tat Wi-Fi
    void InitializePowerSaveTimer() {
        power_save_timer_ = new PowerSaveTimer(-1, STLAB_IDLE_SLEEP_S);
        power_save_timer_->OnEnterSleepMode([this]() {
            ESP_LOGI(TAG, "Ngu (khong giao tiep %d s)", STLAB_IDLE_SLEEP_S);
            SetSleeping(true);
            SleepOutputs();
        });
        power_save_timer_->OnExitSleepMode([this]() {
            ESP_LOGI(TAG, "Thuc day");
            SetSleeping(false);
            if (led_ != nullptr) {
                led_->OnStateChanged();
            }
        });
        power_save_timer_->SetEnabled(true);
    }

    // Cham luc dang nghe: cho co noi cau chao tam biet roi dong phien; qua han thi tu dong (khong ket phien)
    static void ByeTask(void* arg) {
        auto* self = static_cast<StlabS3Board*>(arg);
        auto& app = Application::GetInstance();
        for (int i = 0; i < 60; i++) {
            vTaskDelay(pdMS_TO_TICKS(100));
            auto st = app.GetDeviceState();
            if (st == kDeviceStateIdle) { self->bye_pending_ = false; vTaskDelete(nullptr); return; }
            if (st == kDeviceStateSpeaking) break;
        }
        for (int i = 0; i < 100 && app.GetDeviceState() == kDeviceStateSpeaking; i++) {
            vTaskDelay(pdMS_TO_TICKS(100));
        }
        for (int i = 0; i < 20 && app.GetDeviceState() != kDeviceStateIdle; i++) {
            vTaskDelay(pdMS_TO_TICKS(100));
        }
        if (app.GetDeviceState() == kDeviceStateListening) {
            ESP_LOGW(TAG, "Cau noi khong dong phien sau tam biet -> tu dong");
            app.ToggleChatState();
        }
        self->bye_pending_ = false;
        vTaskDelete(nullptr);
    }

    static void SleepTask(void* arg) {
        auto* self = static_cast<StlabS3Board*>(arg);
        auto& app = Application::GetInstance();
        self->bye_pending_ = true;
        for (int i = 0; i < 10; i++) {
            auto st = app.GetDeviceState();
            if (st != kDeviceStateListening && st != kDeviceStateSpeaking && st != kDeviceStateConnecting) {
                break;
            }
            if (st != kDeviceStateConnecting) {
                app.ToggleChatState();
            }
            vTaskDelay(pdMS_TO_TICKS(150));
        }
        self->bye_pending_ = false;
        app.PlaySound(Lang::Sounds::OGG_POPUP);
        vTaskDelay(pdMS_TO_TICKS(600));
        self->SetSleeping(true);
        self->SleepOutputs();
        ESP_LOGI(TAG, "Ngu theo nut giu");
        vTaskDelete(nullptr);
    }

    void InitializeButtons() {
        // Giu hanh vi nut nhu A1S: cham = mo/dong phien; cham luc co noi = ngat loi; giu 3 s = ngu.
        // Ban realtime van ngat loi bang giong (AEC + BargeGate may chu), nut chi la phuong an du phong.
        // Phan ung luc NHAN XUONG (BUTTON_PRESS_DOWN), khong dung OnClick: SINGLE_CLICK cua iot_button chi ban
        // sau khi tha tay + cho them CONFIG_BUTTON_SHORT_PRESS_TIME_MS (180 ms) de loai nhap doi -> be thay cham.
        // Chong doi phim lan 2: bo qua nhan xuong trong 300 ms sau lan truoc (ca 2 nut dung chung moc thoi gian).
        auto on_talk_click = [this]() {
            const int64_t now_us = esp_timer_get_time();
            if (now_us - last_press_us_ < 300000) {
                return;
            }
            last_press_us_ = now_us;
            auto& app = Application::GetInstance();
            ESP_LOGI(TAG, "Nut noi nhan xuong (state=%d, da_tha=%d)", (int)app.GetDeviceState(), (int)seen_release_);
            // Chan bat nham: chan nut doc "dang nhan" ngay tu luc bat may (dau day/chap) -> chua tung thay tha thi bo qua
            if (!seen_release_) {
                return;
            }
            SetSleeping(false);
            power_save_timer_->WakeUp();
            // Dang khoi dong: cham ngan KHONG vao cai Wi-Fi nua (2.5.2.5 bi phat hotspot khi cham luc bat may);
            // muon cai Wi-Fi: giu nut 5 s luc dang khoi dong (on_talk_long)
            if (app.GetDeviceState() == kDeviceStateStarting) {
                return;
            }
            // Dang NGHE ma cham = xin ket thuc: "abort" co reason wake_word_detected (bo nay tat wake word nen khong trung)
            // -> co chao tam biet -> cau noi dong phien. Du phong 6 s chua dong thi tu dong.
            if (app.GetDeviceState() == kDeviceStateListening && !bye_pending_) {
                bye_pending_ = true;
                app.AbortSpeaking(kAbortReasonWakeWordDetected);
                xTaskCreate(ByeTask, "stlab_bye", 3072, this, 3, nullptr);
                return;
            }
            // Dang NOI ma cham = ngat loi co + xoa ngay hang doi phat de im lap tuc
            if (app.GetDeviceState() == kDeviceStateSpeaking) {
                app.AbortSpeaking(kAbortReasonNone);
                app.GetAudioService().ResetDecoder();
                ESP_LOGI(TAG, "Ngat loi co (xoa hang doi phat)");
                return;
            }
            app.ToggleChatState();
        };
        auto on_talk_long = [this]() {
            if (!seen_release_) {
                return;   // chan nut bi giu tu luc bat may: khong ngu, khong cai Wi-Fi
            }
            if (Application::GetInstance().GetDeviceState() == kDeviceStateStarting) {
                ESP_LOGI(TAG, "Giu nut %d ms luc khoi dong -> che do cai Wi-Fi", STLAB_TALK_LONG_MS);
                EnterWifiConfigMode();
                return;
            }
            ESP_LOGI(TAG, "Nut noi giu %d ms -> ngu", STLAB_TALK_LONG_MS);
            xTaskCreate(SleepTask, "stlab_sleep", 4096, this, 3, nullptr);
        };
        // Nut ngoai GPIO1 (switch MX) va nut BOOT GPIO0 (thu tren ban) cung hanh vi
        auto on_release = [this]() { seen_release_ = true; };
        talk_button_.OnPressDown(on_talk_click);
        talk_button_.OnPressUp(on_release);
        talk_button_.OnLongPress(on_talk_long);
        boot_button_.OnPressDown(on_talk_click);
        boot_button_.OnPressUp(on_release);
        boot_button_.OnLongPress(on_talk_long);
    }

    // LCD + XPT2046 chung 1 bus SPI3 (MISO = GPIO13). Khong ESP_ERROR_CHECK: chua cam man van chay binh thuong.
    void InitializeDisplay() {
        GetBacklight()->SetBrightness(0);   // tat den nen cho toi khi ve xong khung dau (tranh nhay trang)
        spi_bus_config_t bus = {};
        bus.mosi_io_num = DISPLAY_MOSI_PIN;
        bus.miso_io_num = TOUCH_MISO_PIN;
        bus.sclk_io_num = DISPLAY_SCK_PIN;
        bus.quadwp_io_num = GPIO_NUM_NC;
        bus.quadhd_io_num = GPIO_NUM_NC;
        bus.max_transfer_sz = DISPLAY_WIDTH * 20 * sizeof(uint16_t);
        if (spi_bus_initialize(SPI3_HOST, &bus, SPI_DMA_CH_AUTO) != ESP_OK) {
            ESP_LOGW(TAG, "Khong khoi tao duoc bus SPI man hinh -> chay khong man");
            return;
        }
        esp_lcd_panel_io_handle_t panel_io = nullptr;
        esp_lcd_panel_io_spi_config_t io_cfg = {};
        io_cfg.cs_gpio_num = DISPLAY_CS_PIN;
        io_cfg.dc_gpio_num = DISPLAY_DC_PIN;
        io_cfg.spi_mode = DISPLAY_SPI_MODE;
        io_cfg.pclk_hz = DISPLAY_SPI_HZ;
        io_cfg.trans_queue_depth = 10;
        io_cfg.lcd_cmd_bits = 8;
        io_cfg.lcd_param_bits = 8;
        if (esp_lcd_new_panel_io_spi(SPI3_HOST, &io_cfg, &panel_io) != ESP_OK) {
            ESP_LOGW(TAG, "Khong tao duoc panel io -> chay khong man");
            return;
        }
        esp_lcd_panel_dev_config_t panel_cfg = {};
        panel_cfg.reset_gpio_num = DISPLAY_RST_PIN;
        panel_cfg.rgb_ele_order = DISPLAY_RGB_ORDER;
        panel_cfg.bits_per_pixel = 16;
        esp_lcd_panel_handle_t panel = nullptr;
#if STLAB_LCD_ST7789
        esp_err_t err = esp_lcd_new_panel_st7789(panel_io, &panel_cfg, &panel);
#else
        esp_err_t err = esp_lcd_new_panel_ili9341(panel_io, &panel_cfg, &panel);
#endif
        if (err != ESP_OK || panel == nullptr) {
            ESP_LOGW(TAG, "Khong tao duoc panel LCD (%s) -> chay khong man", esp_err_to_name(err));
            return;
        }
        esp_lcd_panel_reset(panel);
        esp_lcd_panel_init(panel);
        esp_lcd_panel_invert_color(panel, DISPLAY_INVERT_COLOR);
        esp_lcd_panel_swap_xy(panel, DISPLAY_SWAP_XY);
        esp_lcd_panel_mirror(panel, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y);
        display_ = new OwlEyesDisplay(panel_io, panel, DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_OFFSET_X,
                                      DISPLAY_OFFSET_Y, DISPLAY_MIRROR_X, DISPLAY_MIRROR_Y, DISPLAY_SWAP_XY);
        display_->SetBacklightSetter([this](int pct) { GetBacklight()->SetBrightness(static_cast<uint8_t>(pct)); });
        // Cham man: danh thuc power save timer (chay trong task timer 30 ms cua man)
        // + bo co ngu cua bo (ngu do giu nut khong qua power save timer); khong goi display_ o day (dang trong task man)
        display_->EnableTap(SPI3_HOST, [this]() { sleeping_ = false; power_save_timer_->WakeUp(); });
    }

    // Man the chu viet (spec-literacy.md muc 0): may chu -> bo qua MCP tools/call; bo -> may chu khi be cham the.
    // Moi tool tra true ngay (khong cho ve xong). Tu khong co hinh -> the chi hien chu.
    void InitializeLiteracyTools() {
        if (display_ == nullptr) {
            return;   // khong co man: cac tool khong duoc khai bao, may chu nhan loi "tool khong ton tai" va bo qua
        }
        // Cham the -> notification JSON-RPC (khong co id), CHI khi kenh dang mo (be dang nghe/co dang noi)
        display_->SetTouchNotifier([](const char* screen, const std::string& word, int correct) {
            const DeviceState st = Application::GetInstance().GetDeviceState();
            if (st != kDeviceStateListening && st != kDeviceStateSpeaking) {
                return;
            }
            const char* c = correct < 0 ? "null" : (correct == 0 ? "false" : "true");
            char buf[256];
            snprintf(buf, sizeof(buf),
                     "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/stlab_touch\",\"params\":{\"screen\":\"%s\",\"word\":\"%s\",\"correct\":%s}}",
                     screen, word.c_str(), c);
            Application::GetInstance().SendMcpMessage(buf);   // lich chay trong task chinh, an toan da luong
        });
        auto& mcp = McpServer::GetInstance();
        mcp.AddTool("self.screen.show_word",
                    "Show a word card (picture + lowercase word) on the owl's screen. word: a-z, spaces, hyphen.",
                    PropertyList({Property("word", kPropertyTypeString)}),
                    [this](const PropertyList& p) -> ReturnValue {
                        display_->ShowWordCard(p["word"].value<std::string>());
                        return true;
                    });
        mcp.AddTool("self.screen.show_pick",
                    "Show two word cards side by side; the child taps the one named. Left/right is randomised on the device.",
                    PropertyList({Property("target", kPropertyTypeString), Property("other", kPropertyTypeString)}),
                    [this](const PropertyList& p) -> ReturnValue {
                        display_->ShowPickCards(p["target"].value<std::string>(), p["other"].value<std::string>());
                        return true;
                    });
        mcp.AddTool("self.screen.show_letter",
                    "Show the first letter of a word (big) next to a small word card; the child taps the letter.",
                    PropertyList({Property("word", kPropertyTypeString)}),
                    [this](const PropertyList& p) -> ReturnValue {
                        display_->ShowLetterCard(p["word"].value<std::string>());
                        return true;
                    });
        mcp.AddTool("self.screen.show_stickers",
                    "Show up to 3 sticker cards at the end of a lesson. words: comma separated.",
                    PropertyList({Property("words", kPropertyTypeString)}),
                    [this](const PropertyList& p) -> ReturnValue {
                        std::vector<std::string> ws;
                        const std::string all = p["words"].value<std::string>();
                        size_t pos = 0;
                        while (pos <= all.size() && ws.size() < 3) {
                            size_t comma = all.find(',', pos);
                            if (comma == std::string::npos) {
                                comma = all.size();
                            }
                            ws.push_back(all.substr(pos, comma - pos));
                            pos = comma + 1;
                        }
                        display_->ShowStickers(ws);
                        return true;
                    });
        mcp.AddTool("self.screen.clear", "Clear any card and go back to the owl's eyes.", PropertyList(),
                    [this](const PropertyList&) -> ReturnValue {
                        display_->ClearCard();
                        return true;
                    });
    }

public:
    StlabS3Board()
        : WifiBoard(),
          talk_button_(TALK_BUTTON_GPIO, false, STLAB_TALK_LONG_MS),
          boot_button_(BOOT_BUTTON_GPIO, false, STLAB_TALK_LONG_MS) {
        InitializeButtons();
        // Nut tich cuc muc thap (pull-up noi do iot_button bat): ca 2 chan muc 1 = dang nha -> nhan lenh ngay lan cham dau
        seen_release_ = gpio_get_level(TALK_BUTTON_GPIO) == 1 && gpio_get_level(BOOT_BUTTON_GPIO) == 1;
        ESP_LOGI(TAG, "Nut luc bat may: GPIO1=%d GPIO0=%d -> %s", gpio_get_level(TALK_BUTTON_GPIO),
                 gpio_get_level(BOOT_BUTTON_GPIO), seen_release_ ? "san sang" : "dang bi giu, cho tha");
        InitializePowerSaveTimer();
        InitializeDisplay();
        InitializeLiteracyTools();
    }

    virtual Display* GetDisplay() override {
        return display_ != nullptr ? static_cast<Display*>(display_) : WifiBoard::GetDisplay();
    }

    virtual Backlight* GetBacklight() override {
        static PwmBacklight backlight(DISPLAY_BACKLIGHT_PIN, DISPLAY_BACKLIGHT_OUTPUT_INVERT);
        return &backlight;
    }

    virtual Led* GetLed() override {
        if (led_ == nullptr) {
            led_ = new SingleLed(BUILTIN_LED_GPIO);
        }
        return led_;
    }

    virtual AudioCodec* GetAudioCodec() override {
        static StlabLoopbackCodec audio_codec(
            AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
            AUDIO_I2S_SPK_GPIO_BCLK, AUDIO_I2S_SPK_GPIO_LRCK, AUDIO_I2S_SPK_GPIO_DOUT,
            AUDIO_I2S_MIC_GPIO_SCK, AUDIO_I2S_MIC_GPIO_WS, AUDIO_I2S_MIC_GPIO_DIN);
        return &audio_codec;
    }
};

DECLARE_BOARD(StlabS3Board);
