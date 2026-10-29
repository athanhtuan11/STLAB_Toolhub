// Lop dieu khien may bom - KHONG phu thuoc cloud (doi RainMaker sang Telegram... khong phai sua file nay).
// Quyet dinh Tuan 2026-10-25: khoi dong / co dien lai -> TAT; tu tat sau thoi gian chay toi da.
#pragma once

#include <stdbool.h>
#include "driver/gpio.h"

typedef enum {
    PUMP_SRC_USER,     // lenh tu app / lich
    PUMP_SRC_TIMEOUT,  // het thoi gian chay toi da
} pump_src_t;

// Goi khi trang thai doi (de lop ket noi bao len app). Chay trong task esp_timer hoac task goi pump_set.
typedef void (*pump_change_cb_t)(bool on, pump_src_t src);

// Chong bat/tat lien tuc: sau khi tat (ke ca luc khoi dong / co dien lai) phai cho PUMP_MIN_OFF_S moi bat lai.
// Tuan chot 5 s (2026-10-29). Tham khao: Grundfos bom 1-5 HP / tu khoi dong KEMET ~20 lan/gio (~180 s/lan).
#define PUMP_MIN_OFF_S 5

// Dat relay = TAT ngay lap tuc (goi DAU TIEN trong app_main, truoc Wi-Fi/RainMaker).
void pump_init(gpio_num_t relay_gpio, int max_minutes, pump_change_cb_t cb);
// Tra false neu lenh BAT bi tu choi vi chua het thoi gian cho (TAT luon duoc).
bool pump_set(bool on, pump_src_t src);
int pump_lockout_seconds(void);          // so giay con phai cho truoc khi bat lai; 0 = bat duoc
bool pump_is_on(void);
void pump_set_max_minutes(int minutes);  // ap dung ngay neu dang chay (tinh lai tu luc bat)
int pump_get_max_minutes(void);
int pump_remaining_minutes(void);        // 0 neu dang tat
