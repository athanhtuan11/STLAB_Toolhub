// Cap nhat firmware tu xa do KHACH bam nut "Cap nhat" tren app (Tuan 2026-10-25: khong vao duoc tai khoan khach).
// Tuan build o nha -> release.ps1 day .bin + manifest.json len GitHub (repo public) -> ESP32 tai qua HTTPS.
// Ban moi loi (khong len cloud trong 90 s) -> bootloader tu quay ve ban cu (RainMaker + APP_ROLLBACK).
#pragma once

#include <stdbool.h>

// Ket qua de lop app bao len RainMaker. Goi tu task OTA.
typedef void (*ota_pull_status_cb_t)(const char *latest_text);

void ota_pull_init(ota_pull_status_cb_t cb);
void ota_pull_check_async(void);   // chi kiem manifest, cap nhat chu "Ban moi"
void ota_pull_update_async(void);  // kiem + tai + cai + khoi dong lai (neu co ban moi hon)
bool ota_pull_busy(void);          // dang tai firmware -> khong cho bat bom
const char *ota_pull_current_version(void);
