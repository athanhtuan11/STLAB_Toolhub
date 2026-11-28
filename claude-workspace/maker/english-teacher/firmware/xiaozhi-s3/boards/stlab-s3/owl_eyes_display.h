#pragma once
// Doi mat Cu Bong tren man TFT 2,8" (320x240) + cam ung XPT2046. Mac dinh chi co mat: khong chu, khong thanh trang thai
// (tru man cai Wi-Fi cho nguoi lon). Tu ve bang LVGL 9 (doi tuong/cung/lv_anim).
// 2026-11-28: them lop THE chu viet (spec-literacy.md): the tu (A), chon 1 trong 2 (B), chu cai dau (C), sticker (D);
// mat thu nho o dai tren khi co the; hinh Twemoji RGB565A8 doc tu phan vung assets; cham the -> thong bao ve may chu.
#include "display/lcd_display.h"

#include <esp_lcd_touch.h>
#include <driver/spi_master.h>
#include <esp_timer.h>

#include <atomic>
#include <functional>
#include <string>
#include <vector>

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

    // ---- The chu viet (goi tu task MCP bat ky; tu khoa man hinh). Khong co hinh -> chi hien chu. ----
    // correct: -1 = khong ap dung (chi man B co y nghia), 0 = sai, 1 = dung
    using TouchNotify = std::function<void(const char* screen, const std::string& word, int correct)>;
    void SetTouchNotifier(TouchNotify notifier) { notifier_ = std::move(notifier); }
    void ShowWordCard(const std::string& word);                              // A
    void ShowPickCards(const std::string& target, const std::string& other); // B (vi tri trai/phai ngau nhien)
    void ShowLetterCard(const std::string& word);                            // C
    void ShowStickers(const std::vector<std::string>& words);                // D (toi da 3)
    void ClearCard();                                                        // ve doi mat

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
    enum Mode { kModeEyes, kModeWord, kModePick, kModeLetter, kModeSticker };
    struct Hit {
        int x0, y0, x1, y1;
        std::string word;
        bool target = false;
        lv_obj_t* group = nullptr;   // gom the + hinh + chu (rung ca cum)
        lv_obj_t* bg = nullptr;      // nen the (vien)
    };
    struct Letter {
        lv_obj_t* label = nullptr;
        lv_obj_t* under = nullptr;   // gach chan vang
    };
    struct StarPt {
        float x, y, r;
    };

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

    // ---- The chu viet ----
    Mode mode_ = kModeEyes;
    bool mini_ = false;                 // mat thu nho o dai tren (dang co the)
    float shift_k_ = 1.0f;              // ti le dich con ngươi theo co mat
    lv_obj_t* card_layer_ = nullptr;
    lv_obj_t* word_bg_ = nullptr;       // nen the man A
    lv_obj_t* icon_ = nullptr;          // loa man A
    lv_obj_t* card_stars_ = nullptr;
    std::vector<Hit> hits_;
    std::vector<Letter> letters_;       // man A
    std::vector<StarPt> star_pts_;
    std::string card_word_;
    bool reading_ = false;              // co dang doc (Speaking) - man A
    bool pick_done_ = false;
    int64_t reading_start_ms_ = 0;
    int64_t card_deadline_ms_ = 0;
    int64_t card_timeout_ms_ = 8000;
    lv_image_dsc_t pic_dsc_[4];
    void* pic_buf_[4] = {nullptr, nullptr, nullptr, nullptr};
    int pic_n_ = 0;
    TouchNotify notifier_;

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

    bool CanShowCard() const;
    void BeginCard(Mode mode, int timeout_ms);
    void ClearCardObjects();
    bool AddPic(lv_obj_t* parent, const std::string& word, int cx, int cy, int px);
    std::vector<Letter> BuildText(lv_obj_t* parent, const std::string& text, int cx, int cy, const lv_font_t* font,
                                  int max_w, lv_color_t first, lv_color_t rest, bool underline);
    lv_obj_t* AddCardBg(lv_obj_t* group, int w, int h, uint32_t fill, uint32_t border, int border_w);
    void HandleCardTouch(int x, int y);
    void CardTick(int64_t now);
    void FlashBorder(lv_obj_t* bg, int base_w);
    void Shake(lv_obj_t* group);
    void Notify(const char* screen, const std::string& word, int correct);
    void SetCardStars(const std::vector<StarPt>& pts);
};
