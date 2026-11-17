// Chuoi DSP guitar (C thuan, float). Tham so lay tu trang thai UMI.
#ifndef DSP_H
#define DSP_H
#include <stdint.h>
#include "umi_proto.h"

/* -std=c11 chat khong khai bao M_PI trong math.h (gate host dung M_PI) */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct { int volume, tone, echo, mic, string_sens, auto_bal, amp_out, fx3d; } dsp_params_t;

void  dsp_params_from_state(const umi_state_t *s, dsp_params_t *o);
int   dsp_init(int sample_rate);
void  dsp_set(const dsp_params_t *p);
void  dsp_process(const int16_t *in_l, const int16_t *in_r, int16_t *out_l, int16_t *out_r, int n);
float dsp_volume_gain(int volume);

#endif
