#ifndef _STLAB_LOOPBACK_CODEC_H_
#define _STLAB_LOOPBACK_CODEC_H_

#include "codecs/no_audio_codec.h"
#include "config.h"

#include <atomic>
#include <cstdint>
#include <mutex>
#include <vector>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

// INMP441 + MAX98357A khong co codec tra tham chieu loa -> thay bang THAM CHIEU PHAN MEM:
// Write() chep mau PCM sau khi ap am luong (dung mau dua ra MAX98357A) vao vong dem PSRAM;
// Read() tra xen ke [mic, ref] (dinh dang "MR" cua AfeAudioEngine: kenh 0 = mic, kenh 1 = tham chieu),
// ref lay tu vong dem tre STLAB_AEC_REF_DELAY_MS. Loa im hoac vong dem thieu mau -> ref = 0, khong chan.
class StlabLoopbackCodec : public NoAudioCodecSimplex {
public:
    StlabLoopbackCodec(int input_sample_rate, int output_sample_rate,
                       gpio_num_t spk_bclk, gpio_num_t spk_ws, gpio_num_t spk_dout,
                       gpio_num_t mic_sck, gpio_num_t mic_ws, gpio_num_t mic_din);
    virtual ~StlabLoopbackCodec();

    virtual void EnableOutput(bool enable) override;

protected:
    virtual int Write(const int16_t* data, int samples) override;
    virtual int Read(int16_t* dest, int samples) override;

private:
    std::vector<int32_t> raw_buf_;
    void PushRef(const int16_t* data, int samples);
    void FetchRef(int16_t* out, int n);
    void HistPush(const int16_t* mic, const int16_t* ref, int n);
    void LagLoop();
    static void LagTask(void* arg);

    int16_t* ring_ = nullptr;          // vong dem tham chieu (PSRAM)
    size_t ring_cap_ = 0;              // so mau (luy thua cua 2)
    uint64_t wp_ = 0;                  // tong so mau da ghi
    uint64_t rp_ = 0;                  // tong so mau da tra
    int64_t last_write_us_ = 0;
    size_t delay_samples_ = 0;
    std::mutex ring_mutex_;
    std::vector<int16_t> mic_buf_;
    std::vector<int16_t> ref_buf_;

    // Uoc luong tre (AEC-LAG): lich su mic + ref (da qua tre hien tai) ha mau 4:1 (4 kHz) ~1 s, tuong quan cheo o task thap.
    static constexpr int kHistN = 4000;                 // 1 s o 4 kHz
    int16_t* hist_mic_ = nullptr;                       // vong, PSRAM
    int16_t* hist_ref_ = nullptr;
    uint64_t hist_n_ = 0;                               // so mau ha mau da ghi
    int acc_m_ = 0, acc_r_ = 0, acc_k_ = 0;             // bo cong ha mau
    size_t hist_delay_ = 0;                             // tre (mau 16 kHz) ung voi lich su; doi tre -> xoa lich su
    std::mutex hist_mutex_;
    TaskHandle_t lag_task_ = nullptr;
    volatile bool lag_stop_ = false;
};

// Thong ke RMS cho log [AEC] (mic / ref / sau AFE); AFE goi stlab_afe_out_hook (patch 0002).
struct StlabAecStats {
    std::atomic<uint64_t> mic_sq{0}, mic_n{0};
    std::atomic<uint64_t> ref_sq{0}, ref_n{0};
    std::atomic<uint64_t> out_sq{0}, out_n{0};
    std::atomic<int64_t> last_play_us{0};
    std::atomic<int64_t> last_log_us{0};
    std::atomic<uint64_t> clip_n{0};      // so mau mic |x| >= 32000 trong cua so log
    std::atomic<int> delay_ms{0};         // tre ref hien tai (auto co the doi)
};
StlabAecStats& GetStlabAecStats();

#endif // _STLAB_LOOPBACK_CODEC_H_
