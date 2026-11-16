// Kiem tra + bung chuong trinh khoi lenh theo PROTOCOL.md muc 1-2. Chi dung thu vien chuan + cJSON.
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#include "prog.h"

typedef struct {
    const char *name;
    int lo;      // lo > hi: khoi khong co tham so n
    int hi;
    int dflt;
    int is_repeat;
    int op;
} op_def_t;

static const op_def_t OPS[] = {
    {"fwd", 1, 4, 1, 0, PROG_OP_FWD},
    {"back", 1, 4, 1, 0, PROG_OP_BACK},
    {"left", 1, 0, 0, 0, PROG_OP_LEFT},
    {"right", 1, 0, 0, 0, PROG_OP_RIGHT},
    {"sound", 0, 2, 0, 0, PROG_OP_SOUND},
    {"eye", 0, 5, 0, 0, PROG_OP_EYE},
    {"repeat", 2, 4, 2, 1, -1},
};

#define OPS_COUNT ((int)(sizeof(OPS) / sizeof(OPS[0])))

typedef struct {
    prog_step_t *out;
    int max;
    int n_out;
    int count;            // tong so khoi da dem
    int ids[PROG_MAX_BLOCKS + 1];
    int n_ids;
    const char *err;
} ctx_t;

const char *prog_op_name(prog_op_t op)
{
    switch (op) {
    case PROG_OP_FWD: return "fwd";
    case PROG_OP_BACK: return "back";
    case PROG_OP_LEFT: return "left";
    case PROG_OP_RIGHT: return "right";
    case PROG_OP_SOUND: return "sound";
    case PROG_OP_EYE: return "eye";
    default: return "?";
    }
}

// So nguyen: cJSON luu double; true/false khong phai so (cJSON_IsNumber da loai).
static bool get_int(const cJSON *item, int *v)
{
    if (!cJSON_IsNumber(item)) {
        return false;
    }
    double d = item->valuedouble;
    if (!(fabs(d) < 1000000.0)) {
        return false;
    }
    if (d != (double)(int)d) {
        return false;
    }
    *v = (int)d;
    return true;
}

static int fail(ctx_t *c, const char *code)
{
    c->err = code;
    return -1;
}

static int push_step(ctx_t *c, int id, int op, int arg)
{
    if (c->n_out >= c->max) {
        return fail(c, "too_many_blocks");
    }
    c->out[c->n_out].id = id;
    c->out[c->n_out].op = (prog_op_t)op;
    c->out[c->n_out].arg = arg;
    c->n_out++;
    return 0;
}

// Kiem 1 khoi va them buoc. inside = dang trong body cua repeat.
static int check_block(ctx_t *c, const cJSON *blk, bool inside)
{
    if (!cJSON_IsObject(blk)) {
        return fail(c, "bad_json");
    }
    const cJSON *jop = cJSON_GetObjectItemCaseSensitive(blk, "op");
    const op_def_t *def = NULL;
    if (cJSON_IsString(jop) && jop->valuestring != NULL) {
        for (int i = 0; i < OPS_COUNT; i++) {
            if (strcmp(jop->valuestring, OPS[i].name) == 0) {
                def = &OPS[i];
                break;
            }
        }
    }
    if (def == NULL) {
        return fail(c, "bad_op");
    }
    int id = 0;
    if (!get_int(cJSON_GetObjectItemCaseSensitive(blk, "id"), &id) || id < 0 || id > 999) {
        return fail(c, "bad_arg");
    }
    for (int i = 0; i < c->n_ids; i++) {
        if (c->ids[i] == id) {
            return fail(c, "dup_id");
        }
    }
    if (c->n_ids < PROG_MAX_BLOCKS + 1) {
        c->ids[c->n_ids++] = id;
    }
    c->count++;

    int arg = 0;
    if (def->lo <= def->hi) {
        arg = def->dflt;
        const cJSON *jn = cJSON_GetObjectItemCaseSensitive(blk, "n");
        if (jn != NULL) {
            if (!get_int(jn, &arg) || arg < def->lo || arg > def->hi) {
                return fail(c, "bad_arg");
            }
        }
    }

    if (!def->is_repeat) {
        return push_step(c, id, def->op, arg);
    }

    if (inside) {
        return fail(c, "nested_repeat");
    }
    const cJSON *body = cJSON_GetObjectItemCaseSensitive(blk, "body");
    if (!cJSON_IsArray(body) || cJSON_GetArraySize(body) == 0) {
        return fail(c, "empty_repeat");
    }
    if (cJSON_GetArraySize(body) > PROG_MAX_BODY) {
        return fail(c, "too_many_blocks");
    }
    int start = c->n_out;
    const cJSON *b = NULL;
    cJSON_ArrayForEach(b, body) {
        if (check_block(c, b, true) != 0) {
            return -1;
        }
    }
    int len = c->n_out - start;
    for (int rep = 1; rep < arg; rep++) {
        for (int k = 0; k < len; k++) {
            if (c->n_out >= c->max) {
                return fail(c, "too_many_blocks");
            }
            c->out[c->n_out] = c->out[start + k];
            c->n_out++;
        }
    }
    return 0;
}

int prog_expand_array(const cJSON *prog, prog_step_t *out, int max, const char **err_code)
{
    ctx_t c;
    memset(&c, 0, sizeof(c));
    c.out = out;
    c.max = max;
    c.err = "bad_json";
    if (!cJSON_IsArray(prog)) {
        if (err_code != NULL) {
            *err_code = "bad_json";
        }
        return -1;
    }
    if (cJSON_GetArraySize(prog) == 0) {
        if (err_code != NULL) {
            *err_code = "empty";
        }
        return -1;
    }
    const cJSON *b = NULL;
    cJSON_ArrayForEach(b, prog) {
        if (check_block(&c, b, false) != 0) {
            if (err_code != NULL) {
                *err_code = c.err;
            }
            return -1;
        }
    }
    if (c.count > PROG_MAX_BLOCKS) {
        if (err_code != NULL) {
            *err_code = "too_many_blocks";
        }
        return -1;
    }
    return c.n_out;
}

int prog_expand(const char *json_text, prog_step_t *out, int max, const char **err_code)
{
    cJSON *doc = (json_text != NULL) ? cJSON_Parse(json_text) : NULL;
    if (!cJSON_IsObject(doc)) {
        cJSON_Delete(doc);
        if (err_code != NULL) {
            *err_code = "bad_json";
        }
        return -1;
    }
    const cJSON *jprog = cJSON_GetObjectItemCaseSensitive(doc, "prog");
    int r = -1;
    if (jprog == NULL) {
        if (err_code != NULL) {
            *err_code = "bad_json";
        }
    } else {
        int ver = 0;
        if (!get_int(cJSON_GetObjectItemCaseSensitive(doc, "v"), &ver) || ver != 1) {
            if (err_code != NULL) {
                *err_code = "bad_version";
            }
        } else {
            r = prog_expand_array(jprog, out, max, err_code);
        }
    }
    cJSON_Delete(doc);
    return r;
}
