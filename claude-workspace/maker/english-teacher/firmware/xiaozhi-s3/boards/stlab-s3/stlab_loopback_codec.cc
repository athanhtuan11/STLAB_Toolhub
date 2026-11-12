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
    GetStlabAecStats().delay_ms.store(STLAB_AEC_REF_DELAY_MS);
    hist_mic_ = static_cast<int16_t*>(heap_caps_calloc(kHistN, sizeof(int16_t), MALLOC_CAP_SPIRAM));
    hist_ref_ = static_cast<int16_t*>(heap_caps_calloc(kHistN, sizeof(int16_t), MALLOC_CAP_SPIRAM));
    if (hist_mic_ != nullptr && hist_ref_ != nullptr) {
        xTaskCreate(&StlabLoopbackCodec::LagTask, "aec_lag", 6144, this, 1, &lag_task_);
    } else {
        ESP_LOGE(TAG, "Khong cap duoc bo nho uoc luong tre AEC");
    }
    ESP_LOGI(TAG, "Tham chieu mem: tre %d ms (%u mau), vong dem %u mau PSRAM",
             STLAB_AEC_REF_DELAY_MS, (unsigned)delay_samples_, (unsigned)ring_cap_);
}

StlabLoopbackCodec::~StlabLoopbackCodec() {
    lag_stop_ = true;
    if (lag_task_ != nullptr) {
        vTaskDelay(pdMS_TO_TICKS(1300));   // cho task thoat vong
    }
    if (hist_mic_ != nullptr) heap_caps_free(hist_mic_);
    if (hist_ref_ != nullptr) heap_caps_free(hist_ref_);
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
    raw_buf_.resize(frames);
    size_t bytes_read = 0;
    if (i2s_channel_read(rx_handle_, raw_buf_.data(), frames * sizeof(int32_t), &bytes_read, 200) != ESP_OK) {
        return 0;
    }
    int n = bytes_read / sizeof(int32_t);
    for (int i = 0; i < n; i++) {
        int32_t v = raw_buf_[i] >> STLAB_MIC_SHIFT;
        mic_buf_[i] = (int16_t)std::clamp<int32_t>(v, -INT16_MAX, INT16_MAX);
    }
    if (n <= 0) {
        return 0;
    }
    FetchRef(ref_buf_.data(), n);

    uint64_t msq = 0, rsq = 0, clip = 0;
    for (int i = 0; i < n; i++) {
        if (mic_buf_[i] >= 32000 || mic_buf_[i] <= -32000) clip++;
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
    st.clip_n += clip;
    HistPush(mic_buf_.data(), ref_buf_.data(), n);
    return n * 2;
}

// Ha mau 4:1 (trung binh) mic va ref (ref = dung cai AFE nhin thay, da qua tre hien tai) vao vong lich su.
void StlabLoopbackCodec::HistPush(const int16_t* mic, const int16_t* ref, int n) {
    if (hist_mic_ == nullptr || hist_ref_ == nullptr) {
        return;
    }
    std::lock_guard<std::mutex> lock(hist_mutex_);
    for (int i = 0; i < n; i++) {
        acc_m_ += mic[i];
        acc_r_ += ref[i];
        if (++acc_k_ == 4) {
            size_t idx = hist_n_ % kHistN;
            hist_mic_[idx] = (int16_t)(acc_m_ / 4);
            hist_ref_[idx] = (int16_t)(acc_r_ / 4);
            hist_n_++;
            acc_m_ = acc_r_ = acc_k_ = 0;
        }
    }
}

void StlabLoopbackCodec::LagTask(void* arg) {
    static_cast<StlabLoopbackCodec*>(arg)->LagLoop();
    vTaskDelete(nullptr);
}

// Moi ~1 s: tuong quan cheo chuan hoa giua mic va ref_out (ref da tre delay_samples_). Mic[t] ~ ref_out[t - L];
// tre toan phan so voi mau Write tho = delay hien tai + L, tim trong 0..400 ms (L am: ref_out tre qua, duong: chua du tre).
void StlabLoopbackCodec::LagLoop() {
    const int kRate = 4000;                    // Hz sau ha mau
    const int kMaxTotal = 400 * kRate / 1000;  // 1600 mau = 400 ms
    std::vector<float> m(kHistN), r(kHistN);
    std::vector<float> pre_r(kHistN + 1);      // tong binh phuong luy ke cua r
    int stable = 0, loud_cnt = 0;
    int last_best_ms = -1000;
    while (!lag_stop_) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        if (lag_stop_) break;
        size_t d16;
        {
            std::lock_guard<std::mutex> lock(ring_mutex_);
            d16 = delay_samples_;
        }
        {
            std::lock_guard<std::mutex> lock(hist_mutex_);
            if (hist_delay_ != d16) {   // tre vua doi (hoac lan dau) -> lich su khong dong nhat, xoa
                hist_delay_ = d16;
                hist_n_ = 0;
                acc_m_ = acc_r_ = acc_k_ = 0;
                continue;
            }
            if (hist_n_ < (uint64_t)kHistN) continue;
            for (int i = 0; i < kHistN; i++) {   // theo thu tu thoi gian
                size_t idx = (hist_n_ + i) % kHistN;
                m[i] = hist_mic_[idx] * (1.0f / 32768.0f);
                r[i] = hist_ref_[idx] * (1.0f / 32768.0f);
            }
        }
        auto& st = GetStlabAecStats();
        if (esp_timer_get_time() - st.last_play_us.load() > 1000000) {
            stable = 0;
            last_best_ms = -1000;
            continue;   // loa im
        }
        pre_r[0] = 0;
        for (int i = 0; i < kHistN; i++) {
            pre_r[i + 1] = pre_r[i] + r[i] * r[i];
        }
        if (std::sqrt(pre_r[kHistN] / kHistN) < 100.0f / 32768.0f) {   // ref qua nho (loa chua phat du lon)
            continue;
        }
        const int d4 = (int)(d16 / 4);             // tre hien tai, mau 4 kHz
        const int lo = -d4, hi = kMaxTotal - d4;
        std::vector<float> corr(hi - lo + 1);
        // float (S3 co FPU don, double la phan mem -> treo watchdog); nhuong CPU moi 32 lag;
        // |corr|: loa BTL / day loa dao cuc -> vong toi mic co the nguoc pha (tuong quan am)
        for (int L = lo; L <= hi; L++) {
            int t0 = std::max(0, L), t1 = std::min(kHistN, kHistN + L);
            float sxy = 0, sxx = 0;
            for (int t = t0; t < t1; t++) {
                sxy += m[t] * r[t - L];
                sxx += m[t] * m[t];
            }
            float syy = pre_r[t1 - L] - pre_r[t0 - L];
            float den = std::sqrt(sxx * syy);
            corr[L - lo] = den > 1e-9f ? std::fabs(sxy / den) : 0.f;
            if (((L - lo) & 31) == 31) vTaskDelay(1);
        }
        float best = -1, second = -1;
        int best_L = lo, second_L = lo;
        for (int i = 0; i < (int)corr.size(); i++) {
            if (corr[i] > best) { best = corr[i]; best_L = lo + i; }
        }
        for (int i = 0; i < (int)corr.size(); i++) {
            if (std::abs((lo + i) - best_L) > 20 && corr[i] > second) { second = corr[i]; second_L = lo + i; }   // > 5 ms cach dinh
        }
        const int d_ms = (int)(d16 / 16);
        const int best_ms = d_ms + best_L * 1000 / kRate;
        const int second_ms = d_ms + second_L * 1000 / kRate;
        if ((loud_cnt++ % 5) == 0) {
            ESP_LOGI("AEC", "[AEC-LAG] best=%d ms corr=%.2f second=%d ms (corr2=%.2f) delay=%d ms",
                     best_ms, best, second_ms, second, d_ms);
        }
#if STLAB_AEC_AUTO_DELAY
        if (best >= 0.3f) {   // 2026-11-12 do that: corr 0,19-0,34 o tre 32-48 ms -> nguong 0,5 khong bao gio dat
            stable = (last_best_ms > -500 && std::abs(best_ms - last_best_ms) <= 10) ? stable + 1 : 1;
            last_best_ms = best_ms;
        } else {
            stable = 0;
            last_best_ms = -1000;
        }
        if (stable >= 3) {
            int target = std::max(0, std::min(300, best_ms));
            if (std::abs(target - d_ms) > 2) {
                {
                    std::lock_guard<std::mutex> lock(ring_mutex_);
                    delay_samples_ = (size_t)input_sample_rate_ / 1000 * target;
                }
                st.delay_ms.store(target);
                ESP_LOGI("AEC", "[AEC] delay -> %d ms (auto, corr=%.2f)", target, best);
            }
            stable = 0;
            last_best_ms = -1000;
        }
#endif
    }
    lag_task_ = nullptr;
}
