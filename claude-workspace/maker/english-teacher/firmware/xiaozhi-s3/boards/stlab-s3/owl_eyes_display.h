#pragma once
// Doi mat Cu Bong tren man TFT 2,8" (320x240) + cam ung XPT2046. Chi co mat: khong chu, khong thanh trang thai
// (tru man cai Wi-Fi cho nguoi lon). Tu ve bang LVGL 9 (doi tuong/cung/lv_anim), khong anh/GIF.
#include "display/lcd_display.h"

#include <esp_lcd_touch.h>
#include <driver/spi_master.h>
#include <esp_timer.h>

#include <atomic>
#include <functional>
#include <string>

class OwlEyesDisplay : public SpiLcdDisplay {
public:
    OwlEyesDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, int width, int height,
                   int offset_x, int offset_y, bool mirror_x, bool mirror_y, bool swap_xy);
    ~OwlEyesDisplay() override;

    void SetupUI() override;
    void SetEmotion(const char* emotion) override;
    void SetStatus(const char* status) override;
    void SetChatMessage(const char* role, const char* content) override;
    void ClearChatMessages() override;
    void ShowNotification(const char* notification, int duration_ms = 3000) override;
    void ShowNotification(const std::string& notification, int duration_ms = 3000) override;
    void SetPowerSaveMode(bool on) override;
    void UpdateStatusBar(bool update_all = false) override;
    // 2026-11-28: ban goc dat style cho thanh trang thai/o chat (khong dung o day -> con tro rong, crash luc Assets::Apply)
    void SetTheme(Theme* theme) override;
    void SetPreviewImage(std::unique_ptr<LvglImage> image) override;
    void SetHideSubtitle(bool hide) override;

    // Den nen: board noi ham dat do sang (0..100 %). Man chua ve xong khung dau thi den nen van tat.
    void SetBacklightSetter(std::function<void(int)> setter) { backlight_setter_ = std::move(setter); }
    // Cam ung XPT2046 tren bus SPI da khoi tao (host). Khong co man / khong khoi tao duoc -> bo qua, khong loi.
    // on_tap chay trong task timer 30 ms (board dung de danh thuc power save timer).
    void EnableTap(spi_host_device_t host, std::function<void()> on_tap);

private:
    enum Look { kLookIdle, kLookListen, kLookSpeak, kLookThink, kLookPraise, kLookSleep, kLookError, kLookWifi };
    struct Eye {
        lv_obj_t* ball = nullptr;    // mat (elip)
        lv_obj_t* pupil = nullptr;   // con ngươi
        lv_obj_t* glint = nullptr;   // diem sang
        lv_obj_t* lid = nullptr;     // mi (chop)
        lv_obj_t* arc = nullptr;     // cung "tho" khi nghe
        lv_obj_t* smile = nullptr;   // mat cuoi (khen)
        lv_obj_t* cheek = nullptr;   // ma
        lv_obj_t* sleep = nullptr;   // mat nham (ngu)
    };
    static constexpr int kArcPts = 19;

    Eye eye_[2];
    lv_point_precise_t smile_pts_[2][kArcPts];
    lv_point_precise_t sleep_pts_[2][kArcPts];
    lv_point_precise_t z_pts_[2][4];
    lv_obj_t* scene_ = nullptr;
    lv_obj_t* anim_host_ = nullptr;   // chu cua cac lv_anim theo trang thai
    lv_obj_t* stars_ = nullptr;       // 3 sao 4 canh (ve tay)
    lv_obj_t* zzz_[2] = {nullptr, nullptr};
    lv_obj_t* fade_ = nullptr;        // tam phu nen, mo dan 200 ms khi doi trang thai
    lv_obj_t* wifi_label_ = nullptr;
    lv_timer_t* tick_timer_ = nullptr;
    esp_timer_handle_t touch_timer_ = nullptr;
    esp_lcd_touch_handle_t touch_ = nullptr;
    std::function<void()> on_tap_;
    std::function<void(int)> backlight_setter_;

    Look look_ = kLookIdle;
    bool ui_ready_ = false;
    int star_scale_ = 100;     // % (lv_anim)
    int ticks_ = 0;
    int64_t next_blink_ms_ = 0;
    int last_bl_ = -1;

    std::atomic<bool> sleeping_{false};
    std::atomic<int64_t> praise_from_ms_{0};
    std::atomic<int64_t> praise_until_ms_{0};
    std::atomic<int64_t> error_until_ms_{0};
    std::atomic<bool> blink_req_{false};
    std::atomic<int> blink_ms_req_{0};
    std::atomic<int64_t> last_tap_ms_{-100000};
    int touch_hits_ = 0;
    int last_x_ = 0;
    int last_y_ = 0;
    int lid_full_[2] = {148, 148};

    static int64_t NowMs();
    Look WantedLook() const;
    void Tick();
    void ApplyLook(Look look);
    void Blink(int total_ms);
    void ApplyBacklight(Look look);
    void SetEllipse(lv_obj_t* obj, float cx, float cy, float rx, float ry, lv_color_t color);
    void BuildArcPoints(lv_point_precise_t* pts, float cx, float cy, float rx, float ry, int a0, int a1);
    void PollTouch();
    void StartAnim(void* var, lv_anim_exec_xcb_t cb, int from, int to, int ms, int playback_ms, int repeat);
    void PupilShift(float dx, float dy);
};
