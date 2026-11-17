#include <string.h>
#include "umi_proto.h"

static const uint8_t DEFAULT_8_32[25] = {
    0x0d, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x0c, 0x4b,
    0x00, 0x00, 0x00, 0x00, 0x1e, 0x00, 0x00, 0x00, 0x00, 0x14, 0x00, 0x0f
};

void umi_state_default(umi_state_t *s)
{
    memset(s->p, 0, sizeof s->p);
    memcpy(s->p + 8, DEFAULT_8_32, sizeof DEFAULT_8_32);
}

static uint8_t clamp30(uint8_t v)
{
    return v > 30 ? 30 : v;
}

int umi_handle_write(umi_state_t *s, const uint8_t *d, size_t n, int *changed)
{
    int dummy;
    if (!changed) {
        changed = &dummy;
    }
    *changed = 0;
    if (n == 4 && d[0] == 0x55 && d[1] == 0xff && d[2] == 0xfe && d[3] == 0x01) {
        return 1;
    }
    if (n == UMI_FRAME_LEN && d[0] == 0x03 && d[1] == 0x00 && d[2] == 0x01 && d[3] == 0x00) {
        uint8_t old[UMI_FRAME_LEN];
        memcpy(old, s->p, sizeof old);
        memcpy(s->p + 8, d + 8, UMI_FRAME_LEN - 8);
        s->p[8] = clamp30(s->p[8]);
        s->p[15] = clamp30(s->p[15]);
        s->p[19] = clamp30(s->p[19]);
        s->p[25] = clamp30(s->p[25]);
        s->p[27] = clamp30(s->p[27]);
        s->p[20] = s->p[20] < 88 ? 75 : 100;
        s->p[21] = s->p[21] ? 2 : 0;
        s->p[22] = s->p[22] ? 1 : 0;
        s->p[45] = s->p[45] ? 1 : 0;
        *changed = memcmp(old + 8, s->p + 8, UMI_FRAME_LEN - 8) != 0;
        return 1;
    }
    return 0;
}

void umi_build_status(const umi_state_t *s, uint8_t batt_dv, uint8_t *out)
{
    out[0] = 0x03;
    out[1] = 0x10;
    out[2] = 0x01;
    out[3] = 0x00;
    out[4] = batt_dv;
    out[5] = 0x00;
    out[6] = 0x00;
    out[7] = 0x00;
    memcpy(out + 8, s->p + 8, UMI_FRAME_LEN - 8);
}
