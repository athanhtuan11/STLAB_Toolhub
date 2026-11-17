// Giao thuc BLE dan GUITAR UMI (xem docs/ble-protocol.md). C thuan, khong phu thuoc ESP-IDF.
#ifndef UMI_PROTO_H
#define UMI_PROTO_H
#include <stddef.h>
#include <stdint.h>

#define UMI_FRAME_LEN 129
typedef struct { uint8_t p[UMI_FRAME_LEN]; } umi_state_t;

void umi_state_default(umi_state_t *s);
// 55 ff fe 01 -> 1 (gui trang thai, *changed = 0); khung 129 byte 03 00 01 00 -> ap dung + chan khoang, 1; khac -> 0.
int umi_handle_write(umi_state_t *s, const uint8_t *d, size_t n, int *changed);
void umi_build_status(const umi_state_t *s, uint8_t batt_dv, uint8_t *out);

#endif
