// 2 dong co buoc 28BYJ-48 (nua buoc 8 pha) qua ULN2003, chay cung nhip.
#pragma once

#include <stdbool.h>

// Cau hinh 8 chan ra, nha cuon.
void stepper_init(void);

// Chay left_steps / right_steps (> 0 = banh lan ve truoc, < 0 = lui; ham tu nhan DIR_LEFT/DIR_RIGHT cua pins.h).
// Chan toi khi xong (tra 0) hoac bi huy (tra -1; da nha cuon). Hai ben di cung nhip, doc tuyen chung.
int stepper_move(int left_steps, int right_steps);

// Huy ngay (<= 50 ms). Goi duoc tu ISR hoac task khac; co hieu luc toi khi stepper_clear_abort().
void stepper_abort(void);
void stepper_clear_abort(void);
bool stepper_is_aborted(void);

// Dua 8 chan ve 0 (nha cuon).
void stepper_release(void);
