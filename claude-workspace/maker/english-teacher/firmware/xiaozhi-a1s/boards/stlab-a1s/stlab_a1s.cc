#include "wifi_board.h"
#include "codecs/es8388_audio_codec.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "settings.h"
#include "led/led.h"
#include <driver/gpio.h>
#include <esp_timer.h>
#include "display/display.h"
#include "power_save_timer.h"
#include "assets/lang_config.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include <algorithm>
#include <vector>
#include <mutex>
#include <esp_codec_dev.h>
#include <esp_log.h>
#include <driver/i2c_master.h>

#define TAG "StlabA1S"

// Codec ES8388 co tran am luong: moi duong dat am luong (nut, MCP, may chu) deu di qua day.
class StlabEs8388Codec : public Es8388AudioCodec {
public:
    using Es8388AudioCodec::Es8388AudioCodec;

    virtual void Start() override {
        Es8388AudioCodec::Start();
        // Lan dau (chua luu) dung mac dinh 40; sau do kep theo tran.
        Settings settings("audio", false);
        int saved = settings.GetInt("output_volume", -1);
        output_volume_ = std::min(saved < 0 ? AUDIO_DEFAULT_OUTPUT_VOLUME : output_volume_, STLAB_MAX_VOLUME);
    }

    // Mic cua A1S noi vao LIN2/RIN2 (do thuc te). Driver esp_codec_dev co dinh LIN1/RIN1 luc es8388_open
    // (es8388.c: ADCCONTROL2 = ADC_INPUT_LINPUT1_RINPUT1), nen chon lai LIN2/RIN2 sau khi mo duong vao.
    virtual void EnableInput(bool enable) override {
        Es8388AudioCodec::EnableInput(enable);
        if (enable) {
            uint8_t sel = 0x50;  // ADCCONTROL2 (0x0A): LINSEL=01 (LIN2), RINSEL=01 (RIN2)
            ESP_ERROR_CHECK_WITHOUT_ABORT(ctrl_if_->write_reg(ctrl_if_, 0x0A, 1, &sel, 1));
        }
    }

    // Driver mo duong ra 1 kenh (mono) -> chi loa trai co tieng (Tuan nghe thu 2026-11-05; thu MONO mix 0x1D khong an).
    // Mo truoc duong ra 2 kenh (base thay output_device_opened_ = true se bo qua lenh mo mono) va nhan doi moi mau L = R.
    virtual void EnableOutput(bool enable) override {
        if (enable) {
            std::lock_guard<std::mutex> lock(data_if_mutex_);
            if (!output_device_opened_) {
                esp_codec_dev_sample_info_t fs = {
                    .bits_per_sample = 16,
                    .channel = 2,
                    .channel_mask = 0,
                    .sample_rate = (uint32_t)output_sample_rate_,
                    .mclk_multiple = 0,
                };
                ESP_ERROR_CHECK(esp_codec_dev_open(output_dev_, &fs));
                output_device_opened_ = true;
            }
        }
        Es8388AudioCodec::EnableOutput(enable);
    }

    virtual int Write(const int16_t* data, int samples) override {
        if (output_enabled_ && output_dev_ && data != nullptr && samples > 0) {
            stereo_.resize((size_t)samples * 2);
            for (int i = 0; i < samples; i++) {
                stereo_[2 * i] = data[i];
                stereo_[2 * i + 1] = data[i];
            }
            ESP_ERROR_CHECK_WITHOUT_ABORT(esp_codec_dev_write(output_dev_, stereo_.data(), stereo_.size() * sizeof(int16_t)));
        }
        return samples;
    }

private:
    std::vector<int16_t> stereo_;

public:

    virtual void SetOutputVolume(int volume) override {
        volume = std::max(0, std::min(volume, STLAB_MAX_VOLUME));
        Es8388AudioCodec::SetOutputVolume(volume);
    }
};

// LED trang thai GPIO22 (muc thap = sang). Khong dung led/gpio_led.cc vi ban ghim loai no khoi ESP32 (thieu ledc_fade_stop).
class StlabStatusLed : public Led {
public:
    explicit StlabStatusLed(gpio_num_t gpio) : gpio_(gpio) {
        gpio_config_t io = {};
        io.pin_bit_mask = 1ULL << gpio_;
        io.mode = GPIO_MODE_OUTPUT;
        ESP_ERROR_CHECK(gpio_config(&io));
        Set(false);
        esp_timer_create_args_t args = {};
        args.callback = [](void* arg) { static_cast<StlabStatusLed*>(arg)->Toggle(); };
        args.arg = this;
        args.name = "stlab_led";
        ESP_ERROR_CHECK(esp_timer_create(&args, &timer_));
    }

    void OnStateChanged() override {
        esp_timer_stop(timer_);
        switch (Application::GetInstance().GetDeviceState()) {
            case kDeviceStateStarting:
                esp_timer_start_periodic(timer_, 100 * 1000);
                break;
            case kDeviceStateWifiConfiguring:
                esp_timer_start_periodic(timer_, 500 * 1000);
                break;
            case kDeviceStateListening:
            case kDeviceStateSpeaking:
            case kDeviceStateConnecting:
            case kDeviceStateUpgrading:
                Set(true);
                break;
            default:
                Set(false);
                break;
        }
    }

private:
    gpio_num_t gpio_;
    esp_timer_handle_t timer_ = nullptr;
    bool on_ = false;

    void Set(bool on) {
        on_ = on;
        gpio_set_level(gpio_, on ? 0 : 1);  // A1S: LED sang khi muc thap (TODO kiem tren mach)
    }
    void Toggle() { Set(!on_); }
};

class StlabA1sBoard : public WifiBoard {
private:
    i2c_master_bus_handle_t i2c_bus_ = nullptr;
    Button talk_button_;
    Button volume_up_button_;
    Button volume_down_button_;
    StlabStatusLed* led_ = nullptr;
    PowerSaveTimer* power_save_timer_ = nullptr;
    volatile bool sleeping_ = false;

    // Tat den + ampli loa (dung chung cho ngu tu dong va ngu do giu KEY4)
    void SleepOutputs() {
        if (led_ != nullptr) {
            led_->OnStateChanged();
        }
        GetAudioCodec()->EnableOutput(false);
    }

    // Tu ngu sau STLAB_IDLE_SLEEP_S giay khong giao tiep (PowerSaveTimer tu bo qua khi dang noi chuyen/nang cap).
    // cpu_max_freq = -1: khong doi xung nhip, khong tat Wi-Fi/nghe -> cham la noi ngay.
    void InitializePowerSaveTimer() {
        power_save_timer_ = new PowerSaveTimer(-1, STLAB_IDLE_SLEEP_S);
        power_save_timer_->OnEnterSleepMode([this]() {
            ESP_LOGI(TAG, "Ngu (khong giao tiep %d s)", STLAB_IDLE_SLEEP_S);
            sleeping_ = true;
            SleepOutputs();
        });
        power_save_timer_->OnExitSleepMode([this]() {
            ESP_LOGI(TAG, "Thuc day");
            sleeping_ = false;
            if (led_ != nullptr) {
                led_->OnStateChanged();
            }
        });
        power_save_timer_->SetEnabled(true);
    }

    // Giu KEY4: ket thuc phien neu dang noi/nghe, phat am bao, tat den + ampli.
    static void SleepTask(void* arg) {
        auto* self = static_cast<StlabA1sBoard*>(arg);
        auto& app = Application::GetInstance();
        for (int i = 0; i < 4; i++) {
            auto st = app.GetDeviceState();
            if (st != kDeviceStateListening && st != kDeviceStateSpeaking && st != kDeviceStateConnecting) {
                break;
            }
            app.ToggleChatState();  // Speaking: ngat loi; Listening: dong kenh am thanh
            vTaskDelay(pdMS_TO_TICKS(700));
        }
        if (app.GetDeviceState() == kDeviceStateIdle) {
            app.PlaySound(Lang::Sounds::OGG_POPUP);
            vTaskDelay(pdMS_TO_TICKS(800));
        }
        self->sleeping_ = true;
        self->SleepOutputs();
        ESP_LOGI(TAG, "Ngu theo nut giu KEY4");
        vTaskDelete(nullptr);
    }

    void InitializeI2c() {
        i2c_master_bus_config_t bus_config = {
            .i2c_port = I2C_NUM_0,
            .sda_io_num = AUDIO_CODEC_I2C_SDA_PIN,
            .scl_io_num = AUDIO_CODEC_I2C_SCL_PIN,
            .clk_source = I2C_CLK_SRC_DEFAULT,
            .glitch_ignore_cnt = 7,
            .intr_priority = 0,
            .trans_queue_depth = 0,
            .flags = {
                .enable_internal_pullup = 1,
            },
        };
        ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &i2c_bus_));
    }

    void ChangeVolume(int delta) {
        sleeping_ = false;
        power_save_timer_->WakeUp();
        auto codec = GetAudioCodec();
        int volume = std::max(0, std::min(codec->output_volume() + delta, STLAB_MAX_VOLUME));
        codec->SetOutputVolume(volume);
        ESP_LOGI(TAG, "Volume %d (max %d)", volume, STLAB_MAX_VOLUME);
    }

    void InitializeButtons() {
        // KEY4 (2026-11-06, Tuan bo giu-nha): cham 1 lan = mo phien noi chuyen tu dong (AutoStop: may chu VAD tu chot cau,
        // co noi xong tu nghe tiep); cham khi co dang noi = ngat loi co; cham khi dang nghe = ket thuc phien.
        // Luc dang khoi dong cham de vao cau hinh Wi-Fi.
        talk_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            // Dang ngu: cham = thuc day + noi chuyen ngay (1 lan cham)
            sleeping_ = false;
            power_save_timer_->WakeUp();
            if (app.GetDeviceState() == kDeviceStateStarting) {
                EnterWifiConfigMode();
                return;
            }
            app.ToggleChatState();
        });

        // Giu KEY4 5 s = ngu (nut nay cham nhanh van la OnClick)
        talk_button_.OnLongPress([this]() {
            xTaskCreate(SleepTask, "stlab_sleep", 4096, this, 3, nullptr);
        });

        // KEY5 / KEY6: am luong +/- 10, giu KEY5 de vao cau hinh Wi-Fi
        volume_up_button_.OnClick([this]() { ChangeVolume(STLAB_VOLUME_STEP); });
        volume_up_button_.OnLongPress([this]() { EnterWifiConfigMode(); });
        volume_down_button_.OnClick([this]() { ChangeVolume(-STLAB_VOLUME_STEP); });
    }

public:
    StlabA1sBoard()
        : WifiBoard(),
          talk_button_(TALK_BUTTON_GPIO, false, STLAB_TALK_LONG_MS),
          volume_up_button_(VOLUME_UP_BUTTON_GPIO),
          volume_down_button_(VOLUME_DOWN_BUTTON_GPIO) {
        InitializeI2c();
        InitializeButtons();
        InitializePowerSaveTimer();
    }

    virtual Led* GetLed() override {
        if (led_ == nullptr) {
            led_ = new StlabStatusLed(BUILTIN_LED_GPIO);
        }
        return led_;
    }

    virtual AudioCodec* GetAudioCodec() override {
        static StlabEs8388Codec audio_codec(
            i2c_bus_, I2C_NUM_0,
            AUDIO_INPUT_SAMPLE_RATE, AUDIO_OUTPUT_SAMPLE_RATE,
            AUDIO_I2S_GPIO_MCLK, AUDIO_I2S_GPIO_BCLK, AUDIO_I2S_GPIO_WS,
            AUDIO_I2S_GPIO_DOUT, AUDIO_I2S_GPIO_DIN,
            AUDIO_CODEC_PA_PIN, AUDIO_CODEC_ES8388_ADDR);
        return &audio_codec;
    }
};

DECLARE_BOARD(StlabA1sBoard);
