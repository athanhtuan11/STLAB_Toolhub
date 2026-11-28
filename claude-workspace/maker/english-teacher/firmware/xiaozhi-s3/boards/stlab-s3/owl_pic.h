#pragma once
// Tao doi tuong hinh LVGL cho the chu viet (tach rieng khoi owl_eyes_display.cc: mat Cu Bong tu ve, khong dung anh).
#include <lvgl.h>

// Hinh tam (cx, cy) trong parent, thu/phong tu 72 px goc ve px (Twemoji RGB565A8); dsc phai song cung doi tuong.
lv_obj_t* OwlPicCreate(lv_obj_t* parent, const lv_image_dsc_t* dsc, int cx, int cy, int px);
