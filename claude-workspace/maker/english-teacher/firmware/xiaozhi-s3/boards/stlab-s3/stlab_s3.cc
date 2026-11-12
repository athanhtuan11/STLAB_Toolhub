#include "wifi_board.h"
#include "stlab_loopback_codec.h"
#include "application.h"
#include "button.h"
#include "config.h"
#include "led/single_led.h"
#include "power_save_timer.h"
#include "assets/lang_config.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <esp_log.h>
#include <esp_timer.h>

#include <algorithm>
#include <cmath>

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
    ESP_LOGI("AEC", "[AEC] delay=%d ms rms mic=%d ref=%d afe_out=%d", STLAB_AEC_REF_DELAY_MS,
             rms(msq, mn), rms(rsq, rn), rms(osq, on));
}

class StlabS3Board : public WifiBoard {
private:
    Button talk_button_;
    Button volume_up_button_;
    Button volume_down_button_;
    SingleLed* led_ = nullptr;
    PowerSaveTimer* power_save_timer_ = nullptr;
    volatile bool sleeping_ = false;
    volatile bool bye_pending_ = false;   // da xin ket thuc, dang cho co chao tam biet

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
        self->sleeping_ = true;
        self->SleepOutputs();
        ESP_LOGI(TAG, "Ngu theo nut giu");
        vTaskDelete(nullptr);
    }

    void ChangeVolume(int delta) {
        sleeping_ = false;
        power_save_timer_->WakeUp();
        auto codec = GetAudioCodec();
        int volume = std::max(0, std::min(codec->output_volume() + delta, 100));
        codec->SetOutputVolume(volume);
        ESP_LOGI(TAG, "Volume %d", volume);
    }

    void InitializeButtons() {
        // Giu hanh vi nut nhu A1S: cham = mo/dong phien; cham luc co noi = ngat loi; giu 3 s = ngu.
        // Ban realtime van ngat loi bang giong (AEC + BargeGate may chu), nut chi la phuong an du phong.
        talk_button_.OnClick([this]() {
            auto& app = Application::GetInstance();
            sleeping_ = false;
            power_save_timer_->WakeUp();
            if (app.GetDeviceState() == kDeviceStateStarting) {
                EnterWifiConfigMode();
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
        });

        talk_button_.OnLongPress([this]() {
            ESP_LOGI(TAG, "Nut noi giu %d ms -> ngu", STLAB_TALK_LONG_MS);
            xTaskCreate(SleepTask, "stlab_sleep", 4096, this, 3, nullptr);
        });

        // vol+ / vol-: +/- 10; giu vol+ de vao cau hinh Wi-Fi
        volume_up_button_.OnClick([this]() { ChangeVolume(STLAB_VOLUME_STEP); });
        volume_up_button_.OnLongPress([this]() { EnterWifiConfigMode(); });
        volume_down_button_.OnClick([this]() { ChangeVolume(-STLAB_VOLUME_STEP); });
    }

public:
    StlabS3Board()
        : WifiBoard(),
          talk_button_(TALK_BUTTON_GPIO, false, STLAB_TALK_LONG_MS),
          volume_up_button_(VOLUME_UP_BUTTON_GPIO),
          volume_down_button_(VOLUME_DOWN_BUTTON_GPIO) {
        InitializeButtons();
        InitializePowerSaveTimer();
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
