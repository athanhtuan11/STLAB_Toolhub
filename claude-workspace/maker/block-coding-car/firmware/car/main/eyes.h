// 2 mat WS2812 (noi tiep, 1 chan data qua 74AHCT125). Do sang <= LED_MAX_PCT %.
#pragma once

typedef enum {
    EYES_ST_CONNECTING = 0,   // xanh duong nhap nhay – dang noi Wi-Fi
    EYES_ST_WIFI_OK,          // xanh la – cho lenh
    EYES_ST_AP,               // vang – che do diem phat
    EYES_ST_BATT_LOW,         // do nhap nhay – pin yeu
} eyes_status_t;

void eyes_init(void);

// Mau trang thai (khi khong chay chuong trinh)
void eyes_set_status(eyes_status_t st);

// Mau khoi `eye` (0 do, 1 xanh la, 2 xanh duong, 3 vang, 4 tim, 5 tat) – de len tren mau trang thai
void eyes_set_program_color(int color);

// Bo mau chuong trinh, ve mau trang thai (sau done/stopped)
void eyes_clear_program_color(void);
