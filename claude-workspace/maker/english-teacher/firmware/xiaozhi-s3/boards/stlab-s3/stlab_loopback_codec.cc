#include "stlab_loopback_codec.h"

#include <algorithm>
#include <cmath>
#include <cstring>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <esp_timer.h>

#define TAG "StlabAEC"

StlabAecStats& GetStlabAecStats() {
    static StlabAecStats stats;
    return stats;
}

StlabLoopbackCodec::StlabLoopbackCodec(int input_sample_rate, int output_sample_rate,
                                       gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout,
                                       gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din)
    : NoAudioCodecSimplex(input_sample_rate, output_sample_rate,
                          spk_bclk, spk_ws, spk_dout, I2S_STD_SLOT_LEFT,
                          mic_sck, mic_ws, mic_din, I2S_STD_SLOT_LEFT) {
    // Kenh 0 = mic, kenh 1 = tham chieu loa ("MR")
    input_reference_ = true;
    input_channels_ = 2;

    // Vao/ra cung tan so thi ref khong can doi tan so
    delay_samples_ = (size_t)input_sample_rate_ / 1000 * STLAB_AEC_REF_DELAY_MS;
    ring_cap_ = 16384;   // ~1 s o 16 kHz, du cho tre toi da 200 ms + khung doc
    ring_ = static_cast<int16_t*>(heap_caps_calloc(ring_cap_, sizeof(int16_t), MALLOC_CAP_SPIRAM));
    if (ring_ == nullptr) {
        ESP_LOGE(TAG, "Khong cap duoc vong dem tham chieu trong PSRAM -> ref = 0");
        ring_cap_ = 0;
    }
    ESP_LOGI(TAG, "Tham chieu mem: tre %d ms (%u mau), vong dem %u mau PSRAM",
             STLAB_AEC_REF_DELAY_MS, (unsigned)delay_samples_, (unsigned)ring_cap_);
}

StlabLoopbackCodec::~StlabLoopbackCodec() {
    if (ring_ != nullptr) {
        heap_caps_free(ring_);
        ring_ = nullptr;
    }
}

void StlabLoopbackCodec::EnableOutput(bool enable) {
    NoAudioCodecSimplex::EnableOutput(enable);
    if (!enable) {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        rp_ = wp_;   // loa tat -> bo mau cu
    }
}

void StlabLoopbackCodec::PushRef(const int16_t* data, int samples) {
    if (ring_ == nullptr || samples <= 0) {
        return;
    }
    std::lock_guard<std::mutex> lock(ring_mutex_);
    const size_t mask = ring_cap_ - 1;
    for (int i = 0; i < samples; i++) {
        ring_[(wp_ + i) & mask] = data[i];
    }
    wp_ += samples;
    last_write_us_ = esp_timer_get_time();
}

// Tra n mau tham chieu: tre co dinh delay_samples_ so voi luc Write; thieu mau -> 0; loa ngung ghi thi xa not phan con lai.
void StlabLoopbackCodec::FetchRef(int16_t* out, int n) {
    std::memset(out, 0, (size_t)n * sizeof(int16_t));
    if (ring_ == nullptr) {
        return;
    }
    std::lock_guard<std::mutex> lock(ring_mutex_);
    const size_t mask = ring_cap_ - 1;
    const bool idle = (esp_timer_get_time() - last_write_us_) > 60000;
    uint64_t avail = wp_ - rp_;
    if (avail > ring_cap_) {
        rp_ = wp_ - ring_cap_;
        avail = ring_cap_;
    }
    // Write() day ca khung Opus 60 ms mot lan -> avail dao dong toi 1 khung; chi nhay khi vuot 2 khung + 1 lan doc
    const uint64_t burst = (uint64_t)output_sample_rate_ * 60 / 1000;
    if (!idle && avail > delay_samples_ + 2 * burst + (uint64_t)n) {
        // Luc bat dau, hang doi DMA nap nhanh hon thoi gian that -> nhay ve dung do tre muc tieu
        rp_ = wp_ - delay_samples_;
        avail = delay_samples_;
    }
    uint64_t usable = idle ? avail : (avail > delay_samples_ ? avail - delay_samples_ : 0);
    int k = (int)std::min<uint64_t>((uint64_t)n, usable);
    for (int i = 0; i < k; i++) {
        out[i] = ring_[(rp_ + i) & mask];
    }
    rp_ += k;
}

int StlabLoopbackCodec::Write(const int16_t* data, int samples) {
    std::lock_guard<std::mutex> lock(data_if_mutex_);
    std::vector<int32_t> buffer(samples);
    std::vector<int16_t> played(samples);

    // output_volume_: 0-100; volume_factor: 0-65536 (giong NoAudioCodec::Write cua xiaozhi)
    int32_t volume_factor = pow(double(output_volume_) / 100.0, 2) * 65536;
    for (int i = 0; i < samples; i++) {
        int64_t temp = int64_t(data[i]) * volume_factor;
        if (temp > INT32_MAX) {
            buffer[i] = INT32_MAX;
        } else if (temp < INT32_MIN) {
            buffer[i] = INT32_MIN;
        } else {
            buffer[i] = static_cast<int32_t>(temp);
        }
        played[i] = static_cast<int16_t>(buffer[i] >> 16);   // dung mau MAX98357A nhan, o thang 16 bit
    }

    size_t bytes_written = 0;
    ESP_ERROR_CHECK(i2s_channel_write(tx_handle_, buffer.data(), samples * sizeof(int32_t), &bytes_written, portMAX_DELAY));
    PushRef(played.data(), samples);
    GetStlabAecStats().last_play_us.store(esp_timer_get_time());
    return bytes_written / sizeof(int32_t);
}

int StlabLoopbackCodec::Read(int16_t* dest, int samples) {
    const int frames = samples / 2;
    if (frames <= 0) {
        return 0;
    }
    mic_buf_.resize(frames);
    ref_buf_.resize(frames);
    int n = NoAudioCodecSimplex::Read(mic_buf_.data(), frames);
    if (n <= 0) {
        return 0;
    }
    FetchRef(ref_buf_.data(), n);

    uint64_t msq = 0, rsq = 0;
    for (int i = 0; i < n; i++) {
        dest[2 * i] = mic_buf_[i];       // M
        dest[2 * i + 1] = ref_buf_[i];   // R
        msq += (uint64_t)((int64_t)mic_buf_[i] * mic_buf_[i]);
        rsq += (uint64_t)((int64_t)ref_buf_[i] * ref_buf_[i]);
    }
    auto& st = GetStlabAecStats();
    st.mic_sq += msq;
    st.mic_n += n;
    st.ref_sq += rsq;
    st.ref_n += n;
    return n * 2;
}
