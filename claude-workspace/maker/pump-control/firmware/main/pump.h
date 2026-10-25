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

// Dat relay = TAT ngay lap tuc (goi DAU TIEN trong app_main, truoc Wi-Fi/RainMaker).
void pump_init(gpio_num_t relay_gpio, int max_minutes, pump_change_cb_t cb);
void pump_set(bool on, pump_src_t src);
bool pump_is_on(void);
void pump_set_max_minutes(int minutes);  // ap dung ngay neu dang chay (tinh lai tu luc bat)
int pump_get_max_minutes(void);
int pump_remaining_minutes(void);        // 0 neu dang tat
