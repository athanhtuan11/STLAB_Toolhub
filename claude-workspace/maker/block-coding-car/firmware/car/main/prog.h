// Thong dich chuong trinh khoi lenh – C thuan, bien dich duoc tren may tinh (gate host test).
// Nguon so lieu duy nhat: maker/block-coding-car/protocol/PROTOCOL.md muc 1-2.
#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "cJSON.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROG_MAX_BLOCKS 12   // tong so khoi (ca repeat + body)
#define PROG_MAX_BODY   6    // so khoi toi da trong body cua repeat
#define PROG_MAX_STEPS  40   // toi da sau khi bung (PROTOCOL muc 1)

typedef enum {
    PROG_OP_FWD = 0,
    PROG_OP_BACK,
    PROG_OP_LEFT,
    PROG_OP_RIGHT,
    PROG_OP_SOUND,
    PROG_OP_EYE,
} prog_op_t;

typedef struct {
    int id;
    prog_op_t op;
    int arg;
} prog_step_t;

const char *prog_op_name(prog_op_t op);

// Kiem + bung chuong trinh {"v":1,"prog":[...]}. Tra so buoc >= 0, hoac -1 va *err_code = ma loi PROTOCOL.
int prog_expand(const char *json_text, prog_step_t *out, int max, const char **err_code);

// Nhu tren nhung nhan thang mang `prog` (thong diep ws `run`/`dry`); khong kiem "v".
int prog_expand_array(const cJSON *prog, prog_step_t *out, int max, const char **err_code);

#ifdef __cplusplus
}
#endif
