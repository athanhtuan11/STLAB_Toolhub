#include "owl_eyes_display.h"

#include "application.h"
#include "assets.h"
#include "assets/lang_config.h"
#include "config.h"
#include "lvgl_theme.h"
#include "owl_pic.h"
#include "misc/cache/instance/lv_image_cache.h"

#include <driver/gpio.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_touch_xpt2046.h>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <esp_random.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>

#define TAG "OwlEyes"

// Phong Andika Bold (OFL), file C sinh bang assets/gen_fonts.py
extern "C" {
extern const lv_font_t andika_bold_52;
extern const lv_font_t andika_bold_34;
extern const lv_font_t andika_bold_120;
}

namespace {
// Mau (spec-display.md muc 2.1)
const uint32_t kBgHex = 0x0A0F18;        // nen
const uint32_t kBlueHex = 0x4FC3F7;      // nghe / cho / nghi
const uint32_t kYellowHex = 0xFFC83D;    // noi
const uint32_t kPinkHex = 0xFF7FB0;      // khen
const uint32_t kPurpleHex = 0xA99BE0;    // ngu (pha 55 % len nen)
const uint32_t kPupilHex = 0x14203A;     // con ngươi
const uint32_t kGrayHex = 0x7A8699;      // loi / mat mang

// Hinh hoc (pixel, goc tren-trai, man 320 x 240): tam hai mat x = 160 -/+ 83 = 77 / 243, y = 120 (ngu: 130), r = 72
const int kEyeX[2] = {77, 243};
const int kCenterX = 160;
const int kEyeY = 120;
const int kSleepY = 130;
const int kEyeR = 72;
const int kRingR = 84;                   // cung "tho" khi nghe, day 5, 200 -> 340 do
const int kSpeakRx = 62;                 // mat noi: elip 62 x 82
const int kSpeakRy = 82;
const int kPupilR = 36;                  // con ngươi r = 36, lech y +6
const float kPupilSpeakRx = 31.0f;       // elip 31 x 35,6
const float kPupilSpeakRy = 35.6f;
const int kPupilDy = 6;
const int kGlintR = 10;                  // diem sang tam (x + 24, y - 24)
const int kGlintDx = 24;
const int kGlintDy = -24;

// Thoi gian (ms)
const int kBlinkMs = 150;                // chop mat: mi xuong + len, tong 150 ms
const int kBlinkMinGapMs = 2500;         // khoang cach ngau nhien 2,5 - 6 s
const int kBlinkMaxGapMs = 6000;
const int kPraiseMs = 2500;              // khen tu ve sau 2,5 s
const int kFadeMs = 200;                 // doi trang thai
const int kErrorHoldMs = 5000;
const int kTapBlinkMs = 300;             // cham: nham 300 ms roi mat cuoi 600 ms
const int kTapPraiseMs = 900;
const int kTouchPollMs = 30;
const int kTouchMaxJumpPx = 30;
const int kTickMs = 50;
const int kBacklightWarmupTicks = 5;     // cho khung dau ve xong roi moi bat den nen

// ---- The chu viet: mau/hinh hoc lay tu design/make_screen_literacy.py (K = 1, dung pixel 320 x 240) ----
const uint32_t kCardHex = 0xFFF3DF;      // the kem
const uint32_t kInkHex = 0x22304A;       // chu
const uint32_t kOrangeHex = 0xFF8A3D;    // chu cai dau
const uint32_t kGreenHex = 0x5BD27A;     // dung
const uint32_t kDimHex = 0x5A6273;       // the mo / khong chon
const uint32_t kDimInkHex = 0x3A4150;    // chu tren the mo
const uint32_t kSpeakerHex = 0x8FA3BF;   // loa (khong doc)
const int kCardRadius = 18;
const int kMiniEyeX[2] = {134, 186};     // mat thu nho o dai tren
const int kMiniEyeY = 26;
const int kMiniEyeR = 17;
const int kWordTimeoutMs = 8000;         // tu ve doi mat sau 8 s khong cham
const int kPickTimeoutMs = 15000;        // man B: 15 s
const int kUnderlineMsPerLetter = 220;   // gach chan vang chay ~220 ms / chu
const int kShakeMs = 300;
const int kShakePx = 6;
const int kLvImageMagic = 0x19;          // LV_IMAGE_HEADER_MAGIC
const int kLvCfRgb565a8 = 0x14;          // LV_COLOR_FORMAT_RGB565A8

lv_color_t Bg() { return lv_color_hex(kBgHex); }

lv_obj_t* NewObj(lv_obj_t* parent, void* owner) {
    lv_obj_t* o = lv_obj_create(parent);
    lv_obj_remove_style_all(o);
    lv_obj_remove_flag(o, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
    lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
    lv_obj_set_user_data(o, owner);
    return o;
}

lv_obj_t* NewLine(lv_obj_t* parent, void* owner) {
    lv_obj_t* o = lv_line_create(parent);
    lv_obj_remove_flag(o, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
    lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
    lv_obj_set_pos(o, 0, 0);
    lv_obj_set_user_data(o, owner);
    return o;
}

void Show(lv_obj_t* o, bool on) {
    if (on) {
        lv_obj_remove_flag(o, LV_OBJ_FLAG_HIDDEN);
    } else {
        lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN);
    }
}

OwlEyesDisplay* OwnerOf(void* var) {
    return static_cast<OwlEyesDisplay*>(lv_obj_get_user_data(static_cast<lv_obj_t*>(var)));
}
}  // namespace

int64_t OwlEyesDisplay::NowMs() { return esp_timer_get_time() / 1000; }

OwlEyesDisplay::OwlEyesDisplay(esp_lcd_panel_io_handle_t panel_io, esp_lcd_panel_handle_t panel, int width,
                               int height, int offset_x, int offset_y, bool mirror_x, bool mirror_y,
                               bool swap_xy)
    : SpiLcdDisplay(panel_io, panel, width, height, offset_x, offset_y, mirror_x, mirror_y, swap_xy) {
    next_blink_ms_ = NowMs() + kBlinkMinGapMs;
}

OwlEyesDisplay::~OwlEyesDisplay() {
    if (touch_timer_ != nullptr) {
        esp_timer_stop(touch_timer_);
        esp_timer_delete(touch_timer_);
    }
    if (tick_timer_ != nullptr) {
        lv_timer_delete(tick_timer_);
    }
}

void OwlEyesDisplay::SetupUI() {
    if (setup_ui_called_) {
        return;
    }
    Display::SetupUI();
    DisplayLockGuard lock(this);

    lv_obj_t* scr = lv_screen_active();
    lv_obj_remove_flag(scr, LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_color(scr, Bg(), 0);
    lv_obj_set_style_bg_opa(scr, LV_OPA_COVER, 0);

    scene_ = lv_obj_create(scr);
    lv_obj_remove_style_all(scene_);
    lv_obj_set_size(scene_, width_, height_);
    lv_obj_set_pos(scene_, 0, 0);
    lv_obj_remove_flag(scene_, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
    anim_host_ = NewObj(scene_, this);

    for (int i = 0; i < 2; i++) {
        Eye& e = eye_[i];
        e.ball = NewObj(scene_, this);
        e.pupil = NewObj(scene_, this);
        e.glint = NewObj(scene_, this);
        e.smile = NewLine(scene_, this);
        e.cheek = NewObj(scene_, this);
        e.sleep = NewLine(scene_, this);
        e.lid = NewObj(scene_, this);
        Show(e.lid, true);
        lv_obj_set_style_bg_color(e.lid, Bg(), 0);
        lv_obj_set_style_bg_opa(e.lid, LV_OPA_COVER, 0);
        lv_obj_set_height(e.lid, 0);
        e.arc = lv_arc_create(scene_);
        lv_obj_remove_flag(e.arc, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
        lv_obj_remove_style(e.arc, nullptr, LV_PART_KNOB);
        lv_obj_set_style_bg_opa(e.arc, LV_OPA_TRANSP, 0);
        lv_obj_set_style_border_width(e.arc, 0, 0);
        lv_obj_set_style_pad_all(e.arc, 0, 0);
        lv_obj_set_style_arc_rounded(e.arc, false, LV_PART_MAIN);
        lv_obj_set_style_arc_opa(e.arc, LV_OPA_TRANSP, LV_PART_INDICATOR);
        lv_arc_set_bg_angles(e.arc, 200, 340);
        lv_arc_set_value(e.arc, 0);
        lv_obj_set_user_data(e.arc, this);
        lv_obj_add_flag(e.arc, LV_OBJ_FLAG_HIDDEN);
    }

    stars_ = NewObj(scene_, this);
    lv_obj_set_size(stars_, width_, height_);
    lv_obj_set_pos(stars_, 0, 0);
    lv_obj_add_event_cb(
        stars_,
        [](lv_event_t* ev) {
            auto* self = static_cast<OwlEyesDisplay*>(lv_event_get_user_data(ev));
            lv_layer_t* layer = lv_event_get_layer(ev);
            // 3 sao 4 canh: tam (160, 40) r 16; (30, 50) r 10; (290, 45) r 11; ban kinh trong 0,3 r
            static const float kStar[3][3] = {{160, 40, 16}, {30, 50, 10}, {290, 45, 11}};
            for (const auto& st : kStar) {
                float r = st[2] * static_cast<float>(self->star_scale_) / 100.0f;
                float vx[8], vy[8];
                for (int k = 0; k < 8; k++) {
                    float rad = (k % 2 == 0) ? r : r * 0.3f;
                    float ang = static_cast<float>(M_PI) * static_cast<float>(k) / 4.0f;
                    vx[k] = st[0] + rad * sinf(ang);
                    vy[k] = st[1] - rad * cosf(ang);
                }
                for (int k = 0; k < 8; k++) {
                    lv_draw_triangle_dsc_t dsc;
                    lv_draw_triangle_dsc_init(&dsc);
                    dsc.color = lv_color_hex(kPinkHex);
                    dsc.opa = LV_OPA_COVER;
                    dsc.p[0].x = static_cast<lv_value_precise_t>(st[0]);
                    dsc.p[0].y = static_cast<lv_value_precise_t>(st[1]);
                    dsc.p[1].x = static_cast<lv_value_precise_t>(vx[k]);
                    dsc.p[1].y = static_cast<lv_value_precise_t>(vy[k]);
                    dsc.p[2].x = static_cast<lv_value_precise_t>(vx[(k + 1) % 8]);
                    dsc.p[2].y = static_cast<lv_value_precise_t>(vy[(k + 1) % 8]);
                    lv_draw_triangle(layer, &dsc);
                }
            }
        },
        LV_EVENT_DRAW_MAIN, this);

    // Chu "Z" khi ngu: (240, 40) co 22 va (268, 20) co 14, net 3
    const int zx[2] = {240, 268}, zy[2] = {40, 20}, zs[2] = {22, 14};
    for (int i = 0; i < 2; i++) {
        zzz_[i] = NewLine(scene_, this);
        z_pts_[i][0] = {static_cast<lv_value_precise_t>(zx[i]), static_cast<lv_value_precise_t>(zy[i])};
        z_pts_[i][1] = {static_cast<lv_value_precise_t>(zx[i] + zs[i]), static_cast<lv_value_precise_t>(zy[i])};
        z_pts_[i][2] = {static_cast<lv_value_precise_t>(zx[i]), static_cast<lv_value_precise_t>(zy[i] + zs[i])};
        z_pts_[i][3] = {static_cast<lv_value_precise_t>(zx[i] + zs[i]), static_cast<lv_value_precise_t>(zy[i] + zs[i])};
        lv_line_set_points(zzz_[i], z_pts_[i], 4);
        lv_obj_set_style_line_width(zzz_[i], 3, 0);
        lv_obj_set_style_line_rounded(zzz_[i], false, 0);
    }

    // Man cai Wi-Fi (cho nguoi lon): 2 dong chu trang nua duoi, font co san cua xiaozhi
    wifi_label_ = lv_label_create(scene_);
    lv_label_set_long_mode(wifi_label_, LV_LABEL_LONG_MODE_WRAP);
    lv_label_set_text(wifi_label_, "");
    lv_obj_set_width(wifi_label_, width_ - 20);
    lv_obj_set_pos(wifi_label_, 10, height_ / 2 + 10);
    lv_obj_set_style_text_align(wifi_label_, LV_TEXT_ALIGN_CENTER, 0);
    lv_obj_set_style_text_color(wifi_label_, lv_color_white(), 0);
    auto* theme = static_cast<LvglTheme*>(current_theme_);
    if (theme != nullptr && theme->text_font() != nullptr) {
        lv_obj_set_style_text_font(wifi_label_, theme->text_font()->font(), 0);
    }
    lv_obj_add_flag(wifi_label_, LV_OBJ_FLAG_HIDDEN);

    // Lop the chu viet (an khi chi co mat); nam tren mat, duoi lop fade
    card_layer_ = lv_obj_create(scene_);
    lv_obj_remove_style_all(card_layer_);
    lv_obj_set_size(card_layer_, width_, height_);
    lv_obj_set_pos(card_layer_, 0, 0);
    lv_obj_remove_flag(card_layer_, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
    lv_obj_add_flag(card_layer_, LV_OBJ_FLAG_HIDDEN);

    fade_ = NewObj(scr, this);
    lv_obj_set_size(fade_, width_, height_);
    lv_obj_set_pos(fade_, 0, 0);
    Show(fade_, true);
    lv_obj_set_style_bg_color(fade_, Bg(), 0);
    lv_obj_set_style_bg_opa(fade_, LV_OPA_COVER, 0);

    ApplyLook(kLookIdle);
    tick_timer_ = lv_timer_create(
        [](lv_timer_t* t) { static_cast<OwlEyesDisplay*>(lv_timer_get_user_data(t))->Tick(); }, kTickMs, this);
    ui_ready_ = true;
}

void OwlEyesDisplay::StartAnim(void* var, lv_anim_exec_xcb_t cb, int from, int to, int ms, int playback_ms,
                               int repeat) {
    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, var);
    lv_anim_set_exec_cb(&a, cb);
    lv_anim_set_values(&a, from, to);
    lv_anim_set_duration(&a, ms);
    if (playback_ms > 0) {
        lv_anim_set_reverse_duration(&a, playback_ms);
    }
    lv_anim_set_repeat_count(&a, repeat);
    lv_anim_set_path_cb(&a, lv_anim_path_ease_in_out);
    lv_anim_start(&a);
}

// Elip tam (cx, cy) ban kinh rx, ry: doi tuong tron duong kinh 2 rx, keo gian theo y quanh tam.
void OwlEyesDisplay::SetEllipse(lv_obj_t* obj, float cx, float cy, float rx, float ry, lv_color_t color) {
    int d = std::max(2, static_cast<int>(lroundf(rx * 2)));
    lv_obj_set_size(obj, d, d);
    lv_obj_set_pos(obj, static_cast<int>(lroundf(cx - rx)), static_cast<int>(lroundf(cy - rx)));
    lv_obj_set_style_radius(obj, LV_RADIUS_CIRCLE, 0);
    lv_obj_set_style_bg_color(obj, color, 0);
    lv_obj_set_style_bg_opa(obj, LV_OPA_COVER, 0);
    lv_obj_set_style_transform_pivot_x(obj, d / 2, 0);
    lv_obj_set_style_transform_pivot_y(obj, d / 2, 0);
    lv_obj_set_style_transform_scale_x(obj, 256, 0);
    lv_obj_set_style_transform_scale_y(obj, static_cast<int>(lroundf(256.0f * ry / rx)), 0);
    lv_obj_set_style_translate_x(obj, 0, 0);
    lv_obj_set_style_translate_y(obj, 0, 0);
}

// Cung elip: goc a0 -> a1 (do, tinh tu 3 gio, chieu kim dong ho nhu PIL/LVGL), thanh duong gap khuc kArcPts diem
void OwlEyesDisplay::BuildArcPoints(lv_point_precise_t* pts, float cx, float cy, float rx, float ry, int a0,
                                    int a1) {
    for (int k = 0; k < kArcPts; k++) {
        float a = (static_cast<float>(a0) + static_cast<float>(a1 - a0) * static_cast<float>(k) /
                                                static_cast<float>(kArcPts - 1)) *
                  static_cast<float>(M_PI) / 180.0f;
        pts[k].x = static_cast<lv_value_precise_t>(cx + rx * cosf(a));
        pts[k].y = static_cast<lv_value_precise_t>(cy + ry * sinf(a));
    }
}

void OwlEyesDisplay::PupilShift(float dx, float dy) {
    dx *= shift_k_;
    dy *= shift_k_;
    for (auto& e : eye_) {
        lv_obj_set_style_translate_x(e.pupil, static_cast<int>(lroundf(dx)), 0);
        lv_obj_set_style_translate_y(e.pupil, static_cast<int>(lroundf(dy)), 0);
        lv_obj_set_style_translate_x(e.glint, static_cast<int>(lroundf(dx)), 0);
        lv_obj_set_style_translate_y(e.glint, static_cast<int>(lroundf(dy)), 0);
    }
}

void OwlEyesDisplay::ApplyLook(Look look) {
    const bool wifi = (look == kLookWifi);
    const Look shape = wifi ? kLookIdle : look;      // man Wi-Fi = mat Cho thu nho 50 %
    // mat thu nho o dai tren khi co the: r 17 (so voi 72), tam y 26, x 134 / 186 (spec-literacy.md muc 1)
    const bool mini = mini_ && !wifi;
    const float s = wifi ? 0.5f : (mini ? static_cast<float>(kMiniEyeR) / static_cast<float>(kEyeR) : 1.0f);
    const float cy = mini ? static_cast<float>(kMiniEyeY)
                          : (wifi ? 66.0f : (shape == kLookSleep ? static_cast<float>(kSleepY) : static_cast<float>(kEyeY)));
    shift_k_ = s;
    const lv_color_t bg = Bg();
    lv_color_t color = lv_color_hex(kBlueHex);
    switch (shape) {
        case kLookSpeak: color = lv_color_hex(kYellowHex); break;
        case kLookPraise: color = lv_color_hex(kPinkHex); break;
        case kLookSleep: color = lv_color_mix(lv_color_hex(kPurpleHex), bg, 140); break;   // 55 % len nen
        case kLookError: color = lv_color_hex(kGrayHex); break;
        case kLookIdle: color = lv_color_mix(lv_color_hex(kBlueHex), bg, 179); break;      // 70 %
        default: break;
    }
    const bool round_eye = (shape == kLookIdle || shape == kLookListen || shape == kLookThink || shape == kLookError);
    const bool open_eye = round_eye || shape == kLookSpeak;

    lv_anim_delete(anim_host_, nullptr);
    for (auto& e : eye_) {
        lv_anim_delete(e.lid, nullptr);
        lv_obj_set_height(e.lid, 0);
    }
    lv_anim_delete(stars_, nullptr);
    PupilShift(0, 0);

    for (int i = 0; i < 2; i++) {
        Eye& e = eye_[i];
        const float x = mini ? static_cast<float>(kMiniEyeX[i])
                             : static_cast<float>(kCenterX) + static_cast<float>(kEyeX[i] - kCenterX) * s;
        const float sign = (i == 0) ? -1.0f : 1.0f;   // -1: ra phia ngoai ben trai
        Show(e.ball, open_eye);
        Show(e.pupil, open_eye);
        Show(e.glint, open_eye);
        Show(e.arc, shape == kLookListen);
        Show(e.smile, shape == kLookPraise);
        Show(e.cheek, shape == kLookPraise);
        Show(e.sleep, shape == kLookSleep);

        if (open_eye) {
            const float rx = (shape == kLookSpeak ? kSpeakRx : kEyeR) * s;
            const float ry = (shape == kLookSpeak ? kSpeakRy : kEyeR) * s;
            SetEllipse(e.ball, x, cy, rx, ry, color);
            if (shape == kLookSpeak) {
                SetEllipse(e.pupil, x, cy + kPupilDy * s, kPupilSpeakRx * s, kPupilSpeakRy * s, lv_color_hex(kPupilHex));
            } else {
                SetEllipse(e.pupil, x, cy + kPupilDy * s, kPupilR * s, kPupilR * s, lv_color_hex(kPupilHex));
            }
            SetEllipse(e.glint, x + kGlintDx * s, cy + kGlintDy * s, kGlintR * s, kGlintR * s, lv_color_white());
            // Mi: hinh chu nhat mau nen, rong hon mat 4 px moi ben, keo xuong tu dinh mat
            lv_obj_set_width(e.lid, static_cast<int>(lroundf(rx * 2)) + 8);
            lv_obj_set_pos(e.lid, static_cast<int>(lroundf(x - rx)) - 4, static_cast<int>(lroundf(cy - ry)) - 2);
            lid_full_[i] = static_cast<int>(lroundf(ry * 2)) + 4;
        }
        if (shape == kLookListen) {
            const int ring = std::max(4, static_cast<int>(lroundf(static_cast<float>(kRingR) * s)));
            lv_obj_set_size(e.arc, ring * 2, ring * 2);
            lv_obj_set_pos(e.arc, static_cast<int>(lroundf(x)) - ring, static_cast<int>(lroundf(cy)) - ring);
            lv_obj_set_style_arc_width(e.arc, std::max(2, static_cast<int>(lroundf(5.0f * s))), LV_PART_MAIN);
            lv_obj_set_style_arc_color(e.arc, color, LV_PART_MAIN);
            lv_obj_set_style_arc_opa(e.arc, LV_OPA_COVER, LV_PART_MAIN);
        }
        if (shape == kLookPraise) {
            // mat cuoi: cung elip hop (x +/- 62, y - 30 ... y + 70) goc 205 -> 335, day 16
            BuildArcPoints(smile_pts_[i], x, cy + 20 * s, 62 * s, 50 * s, 205, 335);
            lv_line_set_points(e.smile, smile_pts_[i], kArcPts);
            lv_obj_set_style_line_width(e.smile, mini ? 5 : 16, 0);
            lv_obj_set_style_line_color(e.smile, color, 0);
            lv_obj_set_style_line_rounded(e.smile, false, 0);
            // ma: elip 44 x 24 tam (x ra ngoai 50, y + 52)
            SetEllipse(e.cheek, x + sign * 50 * s, cy + 52 * s, 22 * s, 12 * s, color);
        }
        if (shape == kLookSleep) {
            // mat nham: cung elip hop (x +/- 62, y - 62 ... y + 28) goc 25 -> 155, day 14 (tam y = 130)
            BuildArcPoints(sleep_pts_[i], x, cy - 17, 62, 45, 25, 155);
            lv_line_set_points(e.sleep, sleep_pts_[i], kArcPts);
            lv_obj_set_style_line_width(e.sleep, 14, 0);
            lv_obj_set_style_line_color(e.sleep, color, 0);
            lv_obj_set_style_line_rounded(e.sleep, false, 0);
        }
    }
    for (auto* z : zzz_) {
        Show(z, shape == kLookSleep);
        lv_obj_set_style_line_color(z, color, 0);
    }
    Show(stars_, shape == kLookPraise && !mini);
    Show(wifi_label_, wifi);

    // Dong: tho (cung nghe, mat ngu), con ngươi co gian (noi), quet (nghi), sao nhap nhay (khen)
    switch (shape) {
        case kLookListen:
            StartAnim(anim_host_, [](void* v, int32_t o) {
                auto* self = OwnerOf(v);
                for (auto& e : self->eye_) lv_obj_set_style_arc_opa(e.arc, static_cast<lv_opa_t>(o), LV_PART_MAIN);
            }, 102, 255, 500, 500, LV_ANIM_REPEAT_INFINITE);      // opacity 40 <-> 100 %, chu ky 1 s
            break;
        case kLookSpeak:
            StartAnim(anim_host_, [](void* v, int32_t o) {
                auto* self = OwnerOf(v);
                for (auto& e : self->eye_) {
                    lv_obj_set_style_transform_scale_x(e.pupil, 256 * (1000 + o) / 1000, 0);
                    lv_obj_set_style_transform_scale_y(e.pupil, static_cast<int>(256.0f * kPupilSpeakRy / kPupilSpeakRx) * (1000 + o) / 1000, 0);
                }
            }, -80, 80, 200, 200, LV_ANIM_REPEAT_INFINITE);        // +/- 8 %, chu ky 400 ms
            break;
        case kLookThink:
            PupilShift(0, -14);
            StartAnim(anim_host_, [](void* v, int32_t o) { OwnerOf(v)->PupilShift(static_cast<float>(o), -14); },
                      -14, 14, 1000, 1000, LV_ANIM_REPEAT_INFINITE);   // quet +/- 14 px, chu ky 2 s
            break;
        case kLookError:
            PupilShift(0, 16);
            break;
        case kLookPraise:
            star_scale_ = 100;
            StartAnim(stars_, [](void* v, int32_t o) {
                OwnerOf(v)->star_scale_ = o;
                lv_obj_invalidate(static_cast<lv_obj_t*>(v));
            }, 100, 70, 250, 250, 2);                               // nhap nhay 2 lan roi giu 100 %
            break;
        case kLookSleep:
            StartAnim(anim_host_, [](void* v, int32_t o) {
                auto* self = OwnerOf(v);
                for (auto& e : self->eye_) lv_obj_set_style_line_opa(e.sleep, static_cast<lv_opa_t>(o), 0);
                for (auto* z : self->zzz_) lv_obj_set_style_line_opa(z, static_cast<lv_opa_t>(o), 0);
            }, 153, 255, 2000, 2000, LV_ANIM_REPEAT_INFINITE);     // opacity 60 <-> 100 %, chu ky 4 s
            break;
        default:
            break;
    }

    // Fade 200 ms: tam phu nen mo dan
    lv_anim_delete(fade_, nullptr);
    lv_obj_move_foreground(fade_);
    lv_obj_set_style_bg_opa(fade_, LV_OPA_COVER, 0);
    StartAnim(fade_, [](void* v, int32_t o) { lv_obj_set_style_bg_opa(static_cast<lv_obj_t*>(v), static_cast<lv_opa_t>(o), 0); },
              255, 0, kFadeMs, 0, 1);

    look_ = look;
    next_blink_ms_ = NowMs() + kBlinkMinGapMs + static_cast<int>(esp_random() % (kBlinkMaxGapMs - kBlinkMinGapMs));
    if (ticks_ >= kBacklightWarmupTicks) {
        ApplyBacklight(look);
    }
}

void OwlEyesDisplay::Blink(int total_ms) {
    for (int i = 0; i < 2; i++) {
        lv_obj_t* lid = eye_[i].lid;
        lv_anim_delete(lid, nullptr);
        StartAnim(lid, [](void* v, int32_t h) { lv_obj_set_height(static_cast<lv_obj_t*>(v), h); }, 0, lid_full_[i],
                  total_ms / 2, total_ms / 2, 1);
    }
}

void OwlEyesDisplay::ApplyBacklight(Look look) {
    int pct = STLAB_BL_IDLE;
    switch (look) {
        case kLookListen:
        case kLookSpeak:
        case kLookPraise:
        case kLookThink: pct = STLAB_BL_ACTIVE; break;
        case kLookSleep: pct = STLAB_BL_SLEEP; break;
        case kLookWifi: pct = STLAB_BL_WIFI; break;
        default: pct = STLAB_BL_IDLE; break;
    }
    if (mode_ != kModeEyes) {
        pct = std::max(pct, STLAB_BL_ACTIVE);   // dang co the chu: du sang de doc
    }
    pct = std::min(pct, STLAB_BL_MAX);
    if (pct == last_bl_ || !backlight_setter_) {
        return;
    }
    last_bl_ = pct;
    backlight_setter_(pct);
}

OwlEyesDisplay::Look OwlEyesDisplay::WantedLook() const {
    const int64_t now = NowMs();
    const DeviceState st = Application::GetInstance().GetDeviceState();
    if (st == kDeviceStateWifiConfiguring) {
        return kLookWifi;
    }
    if (sleeping_.load()) {
        return kLookSleep;
    }
    if (now >= praise_from_ms_.load() && now < praise_until_ms_.load()) {
        return kLookPraise;
    }
    if (now < error_until_ms_.load()) {
        return kLookError;
    }
    switch (st) {
        case kDeviceStateListening: return kLookListen;
        case kDeviceStateSpeaking:
        case kDeviceStateNotifying: return kLookSpeak;
        case kDeviceStateConnecting:
        case kDeviceStateStarting:
        case kDeviceStateActivating:
        case kDeviceStateUpgrading: return kLookThink;
        case kDeviceStateFatalError: return kLookError;
        default: return kLookIdle;
    }
}

void OwlEyesDisplay::Tick() {
    if (!ui_ready_) {
        return;
    }
    ticks_++;
    const int64_t now = NowMs();
    Look want = WantedLook();
    if (want != look_) {
        ApplyLook(want);
    } else if (ticks_ == kBacklightWarmupTicks) {
        ApplyBacklight(look_);
    }
    if (mode_ != kModeEyes) {
        CardTick(now);
    }
    const bool can_blink = (look_ == kLookIdle || look_ == kLookListen || look_ == kLookSpeak || look_ == kLookThink);
    int req = blink_ms_req_.exchange(0);
    if (req > 0) {
        Blink(req);
    } else if (now >= next_blink_ms_ && can_blink) {
        Blink(kBlinkMs);
        next_blink_ms_ = now + kBlinkMinGapMs + static_cast<int>(esp_random() % (kBlinkMaxGapMs - kBlinkMinGapMs));
    }
}

void OwlEyesDisplay::SetEmotion(const char* emotion) {
    if (emotion == nullptr) {
        return;
    }
    static const char* const kPraise[] = {"happy", "laughing", "loving", "funny", "winking",
                                          "cool", "delicious", "kissy", "confident"};
    for (const char* name : kPraise) {
        if (strcmp(emotion, name) == 0) {
            const int64_t now = NowMs();
            praise_from_ms_ = now;
            praise_until_ms_ = now + kPraiseMs;
            return;
        }
    }
}

void OwlEyesDisplay::SetStatus(const char* status) {
    if (status != nullptr && strcmp(status, Lang::Strings::ERROR) == 0) {
        error_until_ms_ = NowMs() + kErrorHoldMs;
    }
}

void OwlEyesDisplay::SetChatMessage(const char* role, const char* content) {
    (void)role;
    if (content == nullptr || content[0] == '\0' || wifi_label_ == nullptr) {
        return;
    }
    if (Application::GetInstance().GetDeviceState() != kDeviceStateWifiConfiguring) {
        return;   // be khong doc chu: chi giu huong dan cai Wi-Fi cho nguoi lon
    }
    DisplayLockGuard lock(this);
    lv_label_set_text(wifi_label_, content);
}

void OwlEyesDisplay::ClearChatMessages() {
    // Khong co khung chat tren man: nhan nay duoc bo qua co chu y
    ESP_LOGD(TAG, "ClearChatMessages: man chi co mat");
}

void OwlEyesDisplay::ShowNotification(const char* notification, int duration_ms) {
    (void)duration_ms;
    if (notification == nullptr || wifi_label_ == nullptr) {
        return;
    }
    // Chi hien khi dang cai Wi-Fi (thong bao "vao che do cai Wi-Fi"); chu cu duoc thay khi co huong dan day du
    const DeviceState st = Application::GetInstance().GetDeviceState();
    if (st == kDeviceStateWifiConfiguring || st == kDeviceStateStarting) {
        DisplayLockGuard lock(this);
        lv_label_set_text(wifi_label_, notification);
    }
}

void OwlEyesDisplay::ShowNotification(const std::string& notification, int duration_ms) {
    ShowNotification(notification.c_str(), duration_ms);
}

void OwlEyesDisplay::SetPowerSaveMode(bool on) {
    sleeping_ = on;
}

void OwlEyesDisplay::UpdateStatusBar(bool update_all) {
    (void)update_all;   // khong co thanh trang thai
}

void OwlEyesDisplay::SetTheme(Theme* theme) {
    // KHONG goi LcdDisplay::SetTheme: no dat style cho mute/battery/network label + o chat ma lop mat khong tao (EXCVADDR 0x28).
    // Phai gan lai phong MOI cho o chu Wi-Fi ngay day: LvglDisplay::SetTextFont giai phong phong cu sau khi goi SetTheme,
    // o chu (ke ca dang an) van duoc LVGL tinh kich thuoc -> con tro phong treo -> Cache error (2026-11-28).
    // lvgl_port_lock la khoa long nhau -> lay lai khoa o day an toan ca khi SetTextFont dang giu.
    DisplayLockGuard lock(this);
    current_theme_ = theme;
    auto* t = static_cast<LvglTheme*>(theme);
    if (wifi_label_ != nullptr && t != nullptr && t->text_font() != nullptr && t->text_font()->font() != nullptr) {
        lv_obj_set_style_text_font(wifi_label_, t->text_font()->font(), 0);
    }
}

void OwlEyesDisplay::SetPreviewImage(std::unique_ptr<LvglImage> image) {
    image.reset();   // khong hien anh xem truoc tren mat
}

void OwlEyesDisplay::SetHideSubtitle(bool hide) {
    (void)hide;      // khong co phu de
}

// ---------------- Cam ung XPT2046 ----------------

void OwlEyesDisplay::EnableTap(spi_host_device_t host, std::function<void()> on_tap) {
    on_tap_ = std::move(on_tap);
    // T_IRQ keo len: chua cam man thi chan noi, khong "cham ma"
    gpio_config_t irq = {};
    irq.pin_bit_mask = 1ULL << TOUCH_IRQ_PIN;
    irq.mode = GPIO_MODE_INPUT;
    irq.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&irq);

    esp_lcd_panel_io_handle_t io = nullptr;
    esp_lcd_panel_io_spi_config_t io_cfg = ESP_LCD_TOUCH_IO_SPI_XPT2046_CONFIG(TOUCH_CS_PIN);
    io_cfg.pclk_hz = TOUCH_SPI_HZ;
    esp_err_t err = esp_lcd_new_panel_io_spi(host, &io_cfg, &io);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "XPT2046 io loi %s - bo qua cam ung", esp_err_to_name(err));
        return;
    }
    esp_lcd_touch_config_t cfg = {};
    // Toa do tho 0..4095 (khong swap/mirror o driver); PollTouch tu doi sang pixel man theo TOUCH_SWAP_XY/MIRROR_X/MIRROR_Y
    cfg.x_max = 4095;
    cfg.y_max = 4095;
    cfg.rst_gpio_num = GPIO_NUM_NC;
    cfg.int_gpio_num = GPIO_NUM_NC;   // IRQ doc tay trong PollTouch (muc thap = dang cham)
    err = esp_lcd_touch_new_spi_xpt2046(io, &cfg, &touch_);
    if (err != ESP_OK) {
        ESP_LOGW(TAG, "XPT2046 loi %s - bo qua cam ung", esp_err_to_name(err));
        touch_ = nullptr;
        return;
    }
    esp_timer_create_args_t args = {};
    args.callback = [](void* arg) { static_cast<OwlEyesDisplay*>(arg)->PollTouch(); };
    args.arg = this;
    args.dispatch_method = ESP_TIMER_TASK;
    args.name = "owl_touch";
    if (esp_timer_create(&args, &touch_timer_) == ESP_OK) {
        esp_timer_start_periodic(touch_timer_, kTouchPollMs * 1000);
        ESP_LOGI(TAG, "XPT2046 san sang (doc moi %d ms)", kTouchPollMs);
    }
}

// Loc cham ma: T_IRQ phai o muc thap + doc duoc toa do + 2 lan doc lien tiep lech <= 30 px
void OwlEyesDisplay::PollTouch() {
    if (touch_ == nullptr) {
        return;
    }
    if (gpio_get_level(TOUCH_IRQ_PIN) != 0) {
        touch_hits_ = 0;
        return;
    }
    if (esp_lcd_touch_read_data(touch_) != ESP_OK) {
        touch_hits_ = 0;
        return;
    }
    esp_lcd_touch_point_data_t pt[1] = {};
    uint8_t count = 0;
    if (esp_lcd_touch_get_data(touch_, pt, &count, 1) != ESP_OK || count == 0) {
        touch_hits_ = 0;
        return;
    }
    // hieu chinh: truc tho -> pixel man (320 x 240)
    const float fa = static_cast<float>(pt[0].x) / 4095.0f;
    const float fb = static_cast<float>(pt[0].y) / 4095.0f;
    float u = TOUCH_SWAP_XY ? fb : fa;
    float v = TOUCH_SWAP_XY ? fa : fb;
    if (TOUCH_MIRROR_X) u = 1.0f - u;
    if (TOUCH_MIRROR_Y) v = 1.0f - v;
    const int tx = std::clamp(static_cast<int>(u * static_cast<float>(width_)), 0, width_ - 1);
    const int ty = std::clamp(static_cast<int>(v * static_cast<float>(height_)), 0, height_ - 1);
    if (touch_hits_ > 0 && (std::abs(tx - last_x_) > kTouchMaxJumpPx || std::abs(ty - last_y_) > kTouchMaxJumpPx)) {
        touch_hits_ = 0;
    }
    last_x_ = tx;
    last_y_ = ty;
    if (++touch_hits_ < 2) {
        return;
    }
    touch_hits_ = 0;
    const int64_t now = NowMs();
    if (now - last_tap_ms_.load() < STLAB_TOUCH_DEBOUNCE_MS) {
        return;   // 1 lan cham / 400 ms
    }
    last_tap_ms_ = now;
    if (on_tap_) {
        on_tap_();
    }
    if (sleeping_.load()) {
        sleeping_ = false;   // chi danh thuc + mo mat, khong mo phien noi
        return;
    }
    if (mode_ != kModeEyes) {
        HandleCardTouch(tx, ty);   // dang co the chu: cham vao the, khong chop mat
        return;
    }
    const DeviceState st = Application::GetInstance().GetDeviceState();
    if (st == kDeviceStateIdle || st == kDeviceStateListening) {
        // nham 300 ms roi mat cuoi Khen 600 ms
        praise_from_ms_ = now + kTapBlinkMs;
        praise_until_ms_ = now + kTapPraiseMs;
        blink_ms_req_ = kTapBlinkMs;
    } else {
        // Dang noi (hoac nghi...): chi chop mat, khong lam gian doan
        blink_ms_req_ = kBlinkMs;
    }
}

// ---------------- The chu viet (spec-literacy.md muc 1) ----------------

namespace {
lv_obj_t* Box(lv_obj_t* parent, int x, int y, int w, int h) {
    lv_obj_t* o = lv_obj_create(parent);
    lv_obj_remove_style_all(o);
    lv_obj_remove_flag(o, static_cast<lv_obj_flag_t>(LV_OBJ_FLAG_CLICKABLE | LV_OBJ_FLAG_SCROLLABLE));
    lv_obj_set_pos(o, x, y);
    lv_obj_set_size(o, w, h);
    return o;
}

// Chi giu a-z, khoang trang, '-', dau nhay don; chu thuong; gop khoang trang
std::string CleanWord(const std::string& in) {
    std::string out;
    for (char c : in) {
        if (c >= 'A' && c <= 'Z') {
            c = static_cast<char>(c - 'A' + 'a');
        }
        const bool ok = (c >= 'a' && c <= 'z') || c == '-' || c == '\'';
        if (ok) {
            out.push_back(c);
        } else if (c == ' ' && !out.empty() && out.back() != ' ') {
            out.push_back(' ');
        }
    }
    while (!out.empty() && out.back() == ' ') {
        out.pop_back();
    }
    return out;
}

int TextWidth(const lv_font_t* f, const std::string& t) {
    int w = 0;
    for (size_t i = 0; i < t.size(); i++) {
        const uint32_t next = (i + 1 < t.size()) ? static_cast<uint8_t>(t[i + 1]) : 0;
        w += lv_font_get_glyph_width(f, static_cast<uint8_t>(t[i]), next);
    }
    return w;
}

void DrawStar(lv_layer_t* layer, float cx, float cy, float r, lv_color_t color) {
    float vx[8], vy[8];
    for (int k = 0; k < 8; k++) {
        const float rad = (k % 2 == 0) ? r : r * 0.35f;
        const float ang = static_cast<float>(M_PI) * static_cast<float>(k) / 4.0f;
        vx[k] = cx + rad * sinf(ang);
        vy[k] = cy - rad * cosf(ang);
    }
    for (int k = 0; k < 8; k++) {
        lv_draw_triangle_dsc_t dsc;
        lv_draw_triangle_dsc_init(&dsc);
        dsc.color = color;
        dsc.opa = LV_OPA_COVER;
        dsc.p[0].x = static_cast<lv_value_precise_t>(cx);
        dsc.p[0].y = static_cast<lv_value_precise_t>(cy);
        dsc.p[1].x = static_cast<lv_value_precise_t>(vx[k]);
        dsc.p[1].y = static_cast<lv_value_precise_t>(vy[k]);
        dsc.p[2].x = static_cast<lv_value_precise_t>(vx[(k + 1) % 8]);
        dsc.p[2].y = static_cast<lv_value_precise_t>(vy[(k + 1) % 8]);
        lv_draw_triangle(layer, &dsc);
    }
}

void DrawTri(lv_layer_t* layer, int x0, int y0, int x1, int y1, int x2, int y2, lv_color_t color) {
    lv_draw_triangle_dsc_t dsc;
    lv_draw_triangle_dsc_init(&dsc);
    dsc.color = color;
    dsc.opa = LV_OPA_COVER;
    dsc.p[0].x = x0;
    dsc.p[0].y = y0;
    dsc.p[1].x = x1;
    dsc.p[1].y = y1;
    dsc.p[2].x = x2;
    dsc.p[2].y = y2;
    lv_draw_triangle(layer, &dsc);
}
}  // namespace

bool OwlEyesDisplay::CanShowCard() const {
    if (!ui_ready_ || sleeping_.load() || look_ == kLookWifi) {
        return false;
    }
    return Application::GetInstance().GetDeviceState() != kDeviceStateWifiConfiguring;
}

void OwlEyesDisplay::ClearCardObjects() {
    if (card_layer_ == nullptr) {
        return;
    }
    lv_obj_clean(card_layer_);
    for (int k = 0; k < pic_n_; k++) {
        lv_image_cache_drop(&pic_dsc_[k]);   // dia chi dsc duoc dung lai cho hinh khac: bo cache theo con tro
        if (pic_buf_[k] != nullptr) {
            heap_caps_free(pic_buf_[k]);
            pic_buf_[k] = nullptr;
        }
    }
    pic_n_ = 0;
    hits_.clear();
    letters_.clear();
    star_pts_.clear();
    word_bg_ = nullptr;
    icon_ = nullptr;
    card_stars_ = nullptr;
}

void OwlEyesDisplay::BeginCard(Mode mode, int timeout_ms) {
    ClearCardObjects();
    const bool entering = (mode_ == kModeEyes);
    mode_ = mode;
    card_timeout_ms_ = timeout_ms;
    card_deadline_ms_ = NowMs() + timeout_ms;
    reading_ = false;
    pick_done_ = false;
    Show(card_layer_, true);
    if (entering) {
        mini_ = true;
        ApplyLook(look_);   // mat thu nho o dai tren
    }
}

void OwlEyesDisplay::ClearCard() {
    if (card_layer_ == nullptr) {
        return;
    }
    DisplayLockGuard lock(this);
    if (mode_ == kModeEyes) {
        return;
    }
    ClearCardObjects();
    Show(card_layer_, false);
    mode_ = kModeEyes;
    mini_ = false;
    ApplyLook(look_);
}

// Hinh Twemoji RGB565A8 (.bin: lv_image_header_t 12 byte + RGB565 + A8) trong phan vung assets (GetAssetData, mmap).
// Chep phan diem anh vao PSRAM (<= 15,6 KB/hinh, toi da 4): con tro mmap + 2 byte "ZZ" co the le 2 byte, LVGL doc 16 bit.
bool OwlEyesDisplay::AddPic(lv_obj_t* parent, const std::string& word, int cx, int cy, int px) {
    if (pic_n_ >= 4) {
        return false;
    }
    std::string name = word;
    std::replace(name.begin(), name.end(), ' ', '_');
    name += ".bin";
    void* ptr = nullptr;
    size_t size = 0;
    if (!Assets::GetInstance().GetAssetData(name, ptr, size) || ptr == nullptr || size < sizeof(lv_image_header_t)) {
        return false;
    }
    lv_image_header_t hd;
    memcpy(&hd, ptr, sizeof(hd));
    if (hd.magic != kLvImageMagic || hd.cf != kLvCfRgb565a8 || hd.w == 0 || hd.h == 0 || hd.w > 128 || hd.h > 128) {
        ESP_LOGW(TAG, "hinh %s sai dinh dang", name.c_str());
        return false;
    }
    const size_t pix = static_cast<size_t>(hd.w) * hd.h * 3;   // RGB565 (2 byte) + A8 (1 byte)
    if (size < sizeof(hd) + pix) {
        return false;
    }
    void* buf = heap_caps_malloc(pix, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (buf == nullptr) {
        buf = heap_caps_malloc(pix, MALLOC_CAP_8BIT);
    }
    if (buf == nullptr) {
        return false;
    }
    memcpy(buf, static_cast<const uint8_t*>(ptr) + sizeof(hd), pix);
    const int k = pic_n_++;
    pic_buf_[k] = buf;
    pic_dsc_[k] = {};
    pic_dsc_[k].header = hd;
    pic_dsc_[k].data_size = static_cast<uint32_t>(pix);
    pic_dsc_[k].data = static_cast<const uint8_t*>(buf);
    OwlPicCreate(parent, &pic_dsc_[k], cx, cy, px);
    return true;
}

lv_obj_t* OwlEyesDisplay::AddCardBg(lv_obj_t* group, int w, int h, uint32_t fill, uint32_t border, int border_w) {
    lv_obj_t* o = Box(group, 0, 0, w, h);
    lv_obj_set_style_radius(o, kCardRadius, 0);
    lv_obj_set_style_bg_color(o, lv_color_hex(fill), 0);
    lv_obj_set_style_bg_opa(o, LV_OPA_COVER, 0);
    lv_obj_set_style_border_color(o, lv_color_hex(border), 0);
    lv_obj_set_style_border_width(o, border_w, 0);
    lv_obj_set_style_border_opa(o, LV_OPA_COVER, 0);
    return o;
}

// Chu thuong, tung chu cai 1 nhan (de to mau chu dau + gach chan vang chay theo tieng). Qua rong -> co 34 -> tach 2 dong.
std::vector<OwlEyesDisplay::Letter> OwlEyesDisplay::BuildText(lv_obj_t* parent, const std::string& text, int cx, int cy,
                                                              const lv_font_t* font, int max_w, lv_color_t first,
                                                              lv_color_t rest, bool underline) {
    std::vector<Letter> out;
    const lv_font_t* f = font;
    if (TextWidth(f, text) > max_w && f == &andika_bold_52) {
        f = &andika_bold_34;
    }
    std::vector<std::string> lines{text};
    if (TextWidth(f, text) > max_w) {
        int best = -1;
        int best_w = 1 << 30;
        for (size_t i = 0; i < text.size(); i++) {
            if (text[i] != ' ') {
                continue;
            }
            const int w = std::max(TextWidth(f, text.substr(0, i)), TextWidth(f, text.substr(i + 1)));
            if (w < best_w) {
                best_w = w;
                best = static_cast<int>(i);
            }
        }
        if (best >= 0) {
            lines = {text.substr(0, best), text.substr(best + 1)};
        }
    }
    const int lh = f->line_height;
    const int asc = lh - f->base_line;
    const int n = static_cast<int>(lines.size());
    bool first_done = false;
    for (int li = 0; li < n; li++) {
        const std::string& ln = lines[li];
        const int ytop = cy - (n * lh) / 2 + li * lh;
        int x = cx - TextWidth(f, ln) / 2;
        for (size_t i = 0; i < ln.size(); i++) {
            const uint32_t next = (i + 1 < ln.size()) ? static_cast<uint8_t>(ln[i + 1]) : 0;
            const int adv = lv_font_get_glyph_width(f, static_cast<uint8_t>(ln[i]), next);
            if (ln[i] != ' ') {
                Letter L;
                L.label = lv_label_create(parent);
                const char one[2] = {ln[i], '\0'};
                lv_label_set_text(L.label, one);
                lv_obj_set_style_text_font(L.label, f, 0);
                lv_obj_set_style_text_color(L.label, first_done ? rest : first, 0);
                lv_obj_set_pos(L.label, x, ytop);
                first_done = true;
                if (underline) {
                    L.under = Box(parent, x, ytop + asc + 4, std::max(adv, 4), 5);
                    lv_obj_set_style_radius(L.under, 3, 0);
                    lv_obj_set_style_bg_color(L.under, lv_color_hex(kYellowHex), 0);
                    lv_obj_set_style_bg_opa(L.under, LV_OPA_COVER, 0);
                    lv_obj_add_flag(L.under, LV_OBJ_FLAG_HIDDEN);
                }
                out.push_back(L);
            }
            x += adv;
        }
    }
    return out;
}

void OwlEyesDisplay::SetCardStars(const std::vector<StarPt>& pts) {
    star_pts_ = pts;
    if (card_stars_ == nullptr) {
        card_stars_ = Box(card_layer_, 0, 0, width_, height_);
        lv_obj_add_event_cb(
            card_stars_,
            [](lv_event_t* ev) {
                auto* self = static_cast<OwlEyesDisplay*>(lv_event_get_user_data(ev));
                lv_layer_t* layer = lv_event_get_layer(ev);
                for (const auto& st : self->star_pts_) {
                    DrawStar(layer, st.x, st.y, st.r, lv_color_hex(kYellowHex));
                }
            },
            LV_EVENT_DRAW_MAIN, this);
    }
    lv_obj_invalidate(card_stars_);
}

// A. The tu: hinh + chu, cham = nghe lai; gach chan vang chay khi co doc
void OwlEyesDisplay::ShowWordCard(const std::string& word_in) {
    const std::string word = CleanWord(word_in);
    if (word.empty() || !CanShowCard()) {
        return;
    }
    DisplayLockGuard lock(this);
    BeginCard(kModeWord, kWordTimeoutMs);
    card_word_ = word;
    lv_obj_t* group = Box(card_layer_, 34, 52, 252, 180);
    word_bg_ = AddCardBg(group, 252, 180, kCardHex, kYellowHex, 0);
    const bool pic = AddPic(group, word, 126, 56, 64);
    letters_ = BuildText(group, word, 126, pic ? 138 : 90, &andika_bold_52, 232, lv_color_hex(kOrangeHex),
                         lv_color_hex(kInkHex), true);
    // loa o goc duoi phai (goc 252, 214; vong song theo trang thai doc)
    icon_ = Box(card_layer_, 240, 190, 70, 50);
    lv_obj_add_event_cb(
        icon_,
        [](lv_event_t* ev) {
            auto* self = static_cast<OwlEyesDisplay*>(lv_event_get_user_data(ev));
            lv_layer_t* layer = lv_event_get_layer(ev);
            lv_area_t a;
            lv_obj_get_coords(self->icon_, &a);
            const int x = a.x1 + 12;
            const int y = a.y1 + 24;
            const lv_color_t col = lv_color_hex(self->reading_ ? kYellowHex : kSpeakerHex);
            DrawTri(layer, x, y - 5, x + 6, y - 5, x + 6, y + 5, col);
            DrawTri(layer, x, y - 5, x + 6, y + 5, x, y + 5, col);
            DrawTri(layer, x + 6, y - 5, x + 13, y - 11, x + 13, y + 11, col);
            DrawTri(layer, x + 6, y - 5, x + 13, y + 11, x + 6, y + 5, col);
            for (int i = 0; i < (self->reading_ ? 2 : 1); i++) {
                lv_draw_arc_dsc_t arc;
                lv_draw_arc_dsc_init(&arc);
                arc.color = col;
                arc.width = 3;
                arc.center.x = x + 13;
                arc.center.y = y;
                arc.radius = static_cast<uint16_t>(17 + 7 * i);
                arc.start_angle = 320;
                arc.end_angle = 40;
                lv_draw_arc(layer, &arc);
            }
        },
        LV_EVENT_DRAW_MAIN, this);
    Hit h;
    h.x0 = 34;
    h.y0 = 52;
    h.x1 = 286;
    h.y1 = 232;
    h.word = word;
    h.group = group;
    h.bg = word_bg_;
    hits_.push_back(h);
}

// B. Chon 1 trong 2 theo loi co: vi tri trai/phai ngau nhien
void OwlEyesDisplay::ShowPickCards(const std::string& target_in, const std::string& other_in) {
    const std::string target = CleanWord(target_in);
    const std::string other = CleanWord(other_in);
    if (target.empty() || other.empty() || !CanShowCard()) {
        return;
    }
    DisplayLockGuard lock(this);
    BeginCard(kModePick, kPickTimeoutMs);
    const bool target_left = (esp_random() & 1) != 0;
    for (int i = 0; i < 2; i++) {
        const bool is_target = ((i == 0) == target_left);
        const std::string& w = is_target ? target : other;
        const int x0 = (i == 0) ? 10 : 166;
        lv_obj_t* group = Box(card_layer_, x0, 52, 144, 180);
        lv_obj_t* bg = AddCardBg(group, 144, 180, kCardHex, kYellowHex, 0);
        const bool pic = AddPic(group, w, 72, 66, 60);
        BuildText(group, w, 72, pic ? 144 : 90, pic ? &andika_bold_34 : &andika_bold_52, 124, lv_color_hex(kOrangeHex),
                  lv_color_hex(kInkHex), false);
        Hit h;
        h.x0 = x0;
        h.y0 = 52;
        h.x1 = x0 + 144;
        h.y1 = 232;
        h.word = w;
        h.target = is_target;
        h.group = group;
        h.bg = bg;
        hits_.push_back(h);
    }
}

// C. Chu cai dau (be > 3 tuoi): cham chu -> "c says /k/ ... cat"
void OwlEyesDisplay::ShowLetterCard(const std::string& word_in) {
    const std::string word = CleanWord(word_in);
    if (word.empty() || !CanShowCard()) {
        return;
    }
    DisplayLockGuard lock(this);
    BeginCard(kModeLetter, kWordTimeoutMs);
    card_word_ = word;
    lv_obj_t* g1 = Box(card_layer_, 18, 52, 144, 180);
    lv_obj_t* bg1 = AddCardBg(g1, 144, 180, kCardHex, kOrangeHex, 4);
    BuildText(g1, word.substr(0, 1), 72, 84, &andika_bold_120, 130, lv_color_hex(kOrangeHex), lv_color_hex(kOrangeHex),
              false);
    Hit h;
    h.x0 = 18;
    h.y0 = 52;
    h.x1 = 162;
    h.y1 = 232;
    h.word = word;
    h.group = g1;
    h.bg = bg1;
    hits_.push_back(h);

    lv_obj_t* g2 = Box(card_layer_, 172, 52, 130, 180);
    AddCardBg(g2, 130, 180, kCardHex, kYellowHex, 0);
    const bool pic = AddPic(g2, word, 65, 60, 54);
    BuildText(g2, word, 65, pic ? 138 : 90, pic ? &andika_bold_34 : &andika_bold_52, 118, lv_color_hex(kOrangeHex),
              lv_color_hex(kInkHex), false);
}

// D. Sticker cuoi buoi: toi da 3 tu, cham tung cai de nghe lai
void OwlEyesDisplay::ShowStickers(const std::vector<std::string>& words_in) {
    std::vector<std::string> words;
    for (const auto& w : words_in) {
        const std::string c = CleanWord(w);
        if (!c.empty() && words.size() < 3) {
            words.push_back(c);
        }
    }
    if (words.empty() || !CanShowCard()) {
        return;
    }
    DisplayLockGuard lock(this);
    BeginCard(kModeSticker, kWordTimeoutMs);
    const int n = static_cast<int>(words.size());
    for (int i = 0; i < n; i++) {
        const int cx = static_cast<int>(
            lroundf(160.0f + (static_cast<float>(i) - static_cast<float>(n - 1) / 2.0f) * 102.0f));
        lv_obj_t* group = Box(card_layer_, cx - 51, 60, 102, 160);
        lv_obj_t* disc = Box(group, 5, 6, 92, 92);
        lv_obj_set_style_radius(disc, LV_RADIUS_CIRCLE, 0);
        lv_obj_set_style_bg_color(disc, lv_color_hex(kCardHex), 0);
        lv_obj_set_style_bg_opa(disc, LV_OPA_COVER, 0);
        lv_obj_set_style_border_color(disc, lv_color_hex(kYellowHex), 0);
        lv_obj_set_style_border_width(disc, 4, 0);
        lv_obj_set_style_border_opa(disc, LV_OPA_COVER, 0);
        const bool pic = AddPic(group, words[i], 51, 52, 50);
        BuildText(group, words[i], 51, pic ? 130 : 52, &andika_bold_34, 98, lv_color_hex(kOrangeHex), lv_color_white(),
                  false);
        Hit h;
        h.x0 = cx - 51;
        h.y0 = 60;
        h.x1 = cx + 51;
        h.y1 = 220;
        h.word = words[i];
        h.group = group;
        h.bg = disc;
        hits_.push_back(h);
    }
    SetCardStars({{160, 222, 9}, {40, 224, 6}, {282, 222, 7}});
    const int64_t now = NowMs();   // mat cuoi trong luc hien sticker
    praise_from_ms_ = now;
    praise_until_ms_ = now + kPraiseMs;
}

void OwlEyesDisplay::FlashBorder(lv_obj_t* bg, int base_w) {
    lv_anim_delete(bg, nullptr);
    lv_obj_set_style_border_width(bg, base_w, 0);
    StartAnim(bg, [](void* v, int32_t o) { lv_obj_set_style_border_width(static_cast<lv_obj_t*>(v), o, 0); }, base_w,
              base_w + 5, 120, 120, 1);
}

// Rung +/- 6 px trong 300 ms (2 dao dong) roi ve vi tri cu
void OwlEyesDisplay::Shake(lv_obj_t* group) {
    lv_anim_delete(group, nullptr);
    lv_anim_t a;
    lv_anim_init(&a);
    lv_anim_set_var(&a, group);
    lv_anim_set_exec_cb(&a, [](void* v, int32_t o) {
        const float ph = static_cast<float>(o) * 4.0f * static_cast<float>(M_PI) / static_cast<float>(kShakeMs);
        lv_obj_set_style_translate_x(static_cast<lv_obj_t*>(v), static_cast<int>(lroundf(kShakePx * sinf(ph))), 0);
    });
    lv_anim_set_values(&a, 0, kShakeMs);
    lv_anim_set_duration(&a, kShakeMs);
    lv_anim_start(&a);
}

void OwlEyesDisplay::Notify(const char* screen, const std::string& word, int correct) {
    if (notifier_) {
        notifier_(screen, word, correct);
    }
}

void OwlEyesDisplay::HandleCardTouch(int x, int y) {
    DisplayLockGuard lock(this);
    if (mode_ == kModeEyes) {
        return;
    }
    const int64_t now = NowMs();
    card_deadline_ms_ = now + card_timeout_ms_;   // cham = con tuong tac, giu the
    for (auto& h : hits_) {
        if (x < h.x0 || x >= h.x1 || y < h.y0 || y >= h.y1) {
            continue;
        }
        switch (mode_) {
            case kModeWord:
                FlashBorder(h.bg, reading_ ? 4 : 0);
                Notify("word", h.word, -1);
                break;
            case kModeLetter:
                FlashBorder(h.bg, 4);
                Notify("letter", h.word, -1);
                break;
            case kModeSticker:
                FlashBorder(h.bg, 4);
                Notify("sticker", h.word, -1);
                break;
            case kModePick:
                if (pick_done_) {
                    break;
                }
                if (h.target) {
                    pick_done_ = true;
                    lv_anim_delete(h.bg, nullptr);
                    lv_obj_set_style_border_color(h.bg, lv_color_hex(kGreenHex), 0);
                    lv_obj_set_style_border_width(h.bg, 6, 0);
                    for (auto& o : hits_) {
                        if (&o == &h) {
                            continue;
                        }
                        lv_obj_set_style_bg_color(o.bg, lv_color_hex(kDimHex), 0);   // the kia mo
                        const uint32_t n = lv_obj_get_child_count(o.group);
                        for (uint32_t i = 0; i < n; i++) {
                            lv_obj_t* c = lv_obj_get_child(o.group, static_cast<int32_t>(i));
                            if (lv_obj_check_type(c, &lv_label_class)) {
                                lv_obj_set_style_text_color(c, lv_color_hex(kDimInkHex), 0);
                            }
                        }
                    }
                    // sao quanh the dung (mockup: the dung ben trai; ben phai thi lat ngang)
                    const bool left = (h.x0 < 160);
                    auto fx = [left](float v) { return left ? v : 320.0f - v; };
                    SetCardStars({{fx(30), 62, 12}, {fx(140), 70, 9}, {fx(120), 222, 8}});
                    praise_from_ms_ = now;
                    praise_until_ms_ = now + kPraiseMs;   // mat nho cuoi
                    card_deadline_ms_ = now + kWordTimeoutMs;
                    Notify("pick", h.word, 1);
                } else {
                    Shake(h.group);
                    Notify("pick", h.word, 0);
                }
                break;
            default:
                break;
        }
        return;
    }
}

void OwlEyesDisplay::CardTick(int64_t now) {
    if (sleeping_.load() || look_ == kLookWifi || now >= card_deadline_ms_) {
        ClearCard();
        return;
    }
    if (mode_ != kModeWord || word_bg_ == nullptr) {
        return;
    }
    // Co dang noi (Speaking): vien vang + loa 2 song + gach chan chay ~220 ms / chu
    const bool speaking = Application::GetInstance().GetDeviceState() == kDeviceStateSpeaking;
    if (speaking != reading_) {
        reading_ = speaking;
        if (speaking) {
            reading_start_ms_ = now;
        }
        lv_anim_delete(word_bg_, nullptr);
        lv_obj_set_style_border_width(word_bg_, speaking ? 4 : 0, 0);
        if (icon_ != nullptr) {
            lv_obj_invalidate(icon_);
        }
    }
    const int hi = reading_ ? static_cast<int>((now - reading_start_ms_) / kUnderlineMsPerLetter) : 0;
    for (size_t i = 0; i < letters_.size(); i++) {
        if (letters_[i].under != nullptr) {
            Show(letters_[i].under, static_cast<int>(i) < hi);
        }
    }
}
