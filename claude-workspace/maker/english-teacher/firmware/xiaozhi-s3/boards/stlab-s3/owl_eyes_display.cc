#include "owl_eyes_display.h"

#include "application.h"
#include "assets/lang_config.h"
#include "config.h"
#include "lvgl_theme.h"

#include <driver/gpio.h>
#include <esp_lcd_panel_io.h>
#include <esp_lcd_touch_xpt2046.h>
#include <esp_log.h>
#include <esp_random.h>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>

#define TAG "OwlEyes"

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
    const float s = wifi ? 0.5f : 1.0f;
    const float cy = wifi ? 66.0f : (shape == kLookSleep ? static_cast<float>(kSleepY) : static_cast<float>(kEyeY));
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
        const float x = static_cast<float>(kCenterX) + static_cast<float>(kEyeX[i] - kCenterX) * s;
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
            int d = kRingR * 2;
            lv_obj_set_size(e.arc, d, d);
            lv_obj_set_pos(e.arc, static_cast<int>(lroundf(x)) - kRingR, static_cast<int>(lroundf(cy)) - kRingR);
            lv_obj_set_style_arc_width(e.arc, 5, LV_PART_MAIN);
            lv_obj_set_style_arc_color(e.arc, color, LV_PART_MAIN);
            lv_obj_set_style_arc_opa(e.arc, LV_OPA_COVER, LV_PART_MAIN);
        }
        if (shape == kLookPraise) {
            // mat cuoi: cung elip hop (x +/- 62, y - 30 ... y + 70) goc 205 -> 335, day 16
            BuildArcPoints(smile_pts_[i], x, cy + 20, 62, 50, 205, 335);
            lv_line_set_points(e.smile, smile_pts_[i], kArcPts);
            lv_obj_set_style_line_width(e.smile, 16, 0);
            lv_obj_set_style_line_color(e.smile, color, 0);
            lv_obj_set_style_line_rounded(e.smile, false, 0);
            // ma: elip 44 x 24 tam (x ra ngoai 50, y + 52)
            SetEllipse(e.cheek, x + sign * 50, cy + 52, 22, 12, color);
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
    Show(stars_, shape == kLookPraise);
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
    cfg.x_max = static_cast<uint16_t>(width_);
    cfg.y_max = static_cast<uint16_t>(height_);
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
    if (touch_hits_ > 0 && (std::abs(static_cast<int>(pt[0].x) - last_x_) > kTouchMaxJumpPx ||
                            std::abs(static_cast<int>(pt[0].y) - last_y_) > kTouchMaxJumpPx)) {
        touch_hits_ = 0;
    }
    last_x_ = pt[0].x;
    last_y_ = pt[0].y;
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
