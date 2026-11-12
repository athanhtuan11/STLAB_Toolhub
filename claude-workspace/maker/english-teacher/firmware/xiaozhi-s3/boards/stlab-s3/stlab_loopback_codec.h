#ifndef _STLAB_LOOPBACK_CODEC_H_
#define _STLAB_LOOPBACK_CODEC_H_

#include "codecs/no_audio_codec.h"
#include "config.h"

#include <atomic>
#include <cstdint>
#include <mutex>
#include <vector>

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
    void PushRef(const int16_t* data, int samples);
    void FetchRef(int16_t* out, int n);

    int16_t* ring_ = nullptr;          // vong dem tham chieu (PSRAM)
    size_t ring_cap_ = 0;              // so mau (luy thua cua 2)
    uint64_t wp_ = 0;                  // tong so mau da ghi
    uint64_t rp_ = 0;                  // tong so mau da tra
    int64_t last_write_us_ = 0;
    size_t delay_samples_ = 0;
    std::mutex ring_mutex_;
    std::vector<int16_t> mic_buf_;
    std::vector<int16_t> ref_buf_;
};

// Thong ke RMS cho log [AEC] (mic / ref / sau AFE); AFE goi stlab_afe_out_hook (patch 0002).
struct StlabAecStats {
    std::atomic<uint64_t> mic_sq{0}, mic_n{0};
    std::atomic<uint64_t> ref_sq{0}, ref_n{0};
    std::atomic<uint64_t> out_sq{0}, out_n{0};
    std::atomic<int64_t> last_play_us{0};
    std::atomic<int64_t> last_log_us{0};
};
StlabAecStats& GetStlabAecStats();

#endif // _STLAB_LOOPBACK_CODEC_H_
