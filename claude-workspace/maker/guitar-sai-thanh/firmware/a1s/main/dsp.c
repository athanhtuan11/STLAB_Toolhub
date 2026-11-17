#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "dsp.h"

#define ECHO_DELAY_MS   250
#define ECHO_MAX_MS     400
#define ECHO_FEEDBACK   0.35f
#define D3_DELAY_MS     12
#define SHELF_HZ        2000.0f
#define COMP_THRESH     0.12589254f   /* -18 dBFS */
#define COMP_RATIO_INV  0.25f         /* 4:1 */

static int s_sr = 44100;
static dsp_params_t s_p;
static float *s_echo;
static int s_echo_len, s_echo_delay, s_echo_w;
static float *s_d3;
static int s_d3_len, s_d3_w;
static float s_b0 = 1, s_b1, s_b2, s_a1, s_a2;
static float s_x1, s_x2, s_y1, s_y2;
static int s_tone_coef = -1;
static float s_env, s_att, s_rel;

void dsp_params_from_state(const umi_state_t *s, dsp_params_t *o)
{
    o->volume = s->p[15];
    o->tone = s->p[19];
    o->echo = s->p[27];
    o->mic = s->p[25];
    o->string_sens = s->p[20];
    o->auto_bal = s->p[21];
    o->amp_out = s->p[22];
    o->fx3d = s->p[45];
}

float dsp_volume_gain(int volume)
{
    if (volume <= 0) {
        return 0.0f;
    }
    if (volume > 30) {
        volume = 30;
    }
    float r = (float)volume / 30.0f;
    return r * r;
}

int dsp_init(int sample_rate)
{
    s_sr = sample_rate;
    free(s_echo);
    free(s_d3);
    s_echo_len = (int)((long)sample_rate * ECHO_MAX_MS / 1000);
    s_echo_delay = (int)((long)sample_rate * ECHO_DELAY_MS / 1000);
    s_d3_len = (int)((long)sample_rate * D3_DELAY_MS / 1000) + 1;
    s_echo = calloc((size_t)s_echo_len, sizeof(float));
    s_d3 = calloc((size_t)s_d3_len, sizeof(float));
    if (!s_echo || !s_d3) {
        free(s_echo);
        free(s_d3);
        s_echo = NULL;
        s_d3 = NULL;
        return -1;
    }
    s_echo_w = 0;
    s_d3_w = 0;
    s_x1 = s_x2 = s_y1 = s_y2 = 0;
    s_env = 0;
    s_att = expf(-1.0f / (0.005f * (float)sample_rate));
    s_rel = expf(-1.0f / (0.2f * (float)sample_rate));
    s_tone_coef = -1;
    memset(&s_p, 0, sizeof s_p);
    s_p.volume = 30;
    s_p.tone = 15;
    s_p.string_sens = 75;
    s_p.mic = 30;
    return 0;
}

static void shelf_coefs(int tone)
{
    float db = (float)(tone - 15) * 0.6f;
    float A = powf(10.0f, db / 40.0f);
    float w0 = 2.0f * 3.14159265f * SHELF_HZ / (float)s_sr;
    float c = cosf(w0), sn = sinf(w0);
    float alpha = sn / 2.0f * sqrtf(2.0f);   /* S = 1 */
    float tsa = 2.0f * sqrtf(A) * alpha;
    float b0 = A * ((A + 1) + (A - 1) * c + tsa);
    float b1 = -2.0f * A * ((A - 1) + (A + 1) * c);
    float b2 = A * ((A + 1) + (A - 1) * c - tsa);
    float a0 = (A + 1) - (A - 1) * c + tsa;
    float a1 = 2.0f * ((A - 1) - (A + 1) * c);
    float a2 = (A + 1) - (A - 1) * c - tsa;
    s_b0 = b0 / a0;
    s_b1 = b1 / a0;
    s_b2 = b2 / a0;
    s_a1 = a1 / a0;
    s_a2 = a2 / a0;
    s_tone_coef = tone;
}

void dsp_set(const dsp_params_t *p)
{
    s_p = *p;
    if (s_p.tone < 0) {
        s_p.tone = 0;
    } else if (s_p.tone > 30) {
        s_p.tone = 30;
    }
    if (s_p.tone != 15 && s_p.tone != s_tone_coef) {
        shelf_coefs(s_p.tone);
    }
}

static int16_t to_i16(float v)
{
    if (v >= 32767.0f) {
        return 32767;
    }
    if (v <= -32768.0f) {
        return -32768;
    }
    return (int16_t)floorf(v + 0.5f);
}

void dsp_process(const int16_t *in_l, const int16_t *in_r, int16_t *out_l, int16_t *out_r, int n)
{
    (void)in_r;   /* v0.1: mono, chi dung kenh trai */
    if (!s_echo || !s_d3) {
        memset(out_l, 0, (size_t)n * sizeof(int16_t));
        memset(out_r, 0, (size_t)n * sizeof(int16_t));
        return;
    }
    const float sens = s_p.string_sens >= 88 ? 1.6f : 1.0f;
    const float vol = dsp_volume_gain(s_p.volume);
    const int use_tone = s_p.tone != 15;
    const int use_comp = s_p.auto_bal == 2;
    const float emix = (float)s_p.echo / 30.0f * 0.5f;
    for (int i = 0; i < n; i++) {
        float x = (float)in_l[i] * sens;
        if (use_tone) {
            float y = s_b0 * x + s_b1 * s_x1 + s_b2 * s_x2 - s_a1 * s_y1 - s_a2 * s_y2;
            s_x2 = s_x1;
            s_x1 = x;
            s_y2 = s_y1;
            s_y1 = y;
            x = y;
        }
        if (use_comp) {
            float a = fabsf(x) / 32768.0f;
            s_env = a > s_env ? s_att * s_env + (1.0f - s_att) * a : s_rel * s_env + (1.0f - s_rel) * a;
            if (s_env > COMP_THRESH) {
                x *= powf(s_env / COMP_THRESH, COMP_RATIO_INV - 1.0f);
            }
        }
        int rd = s_echo_w - s_echo_delay;
        if (rd < 0) {
            rd += s_echo_len;
        }
        if (s_p.echo > 0) {
            float d = s_echo[rd];
            s_echo[s_echo_w] = x + ECHO_FEEDBACK * d;
            x += emix * d;
        } else {
            s_echo[s_echo_w] = 0.0f;
        }
        if (++s_echo_w >= s_echo_len) {
            s_echo_w = 0;
        }
        x *= vol;
        float l = x, r = x;
        float old = s_d3[s_d3_w];   /* ban cu nhat = tre D3_DELAY_MS */
        s_d3[s_d3_w] = x;
        if (++s_d3_w >= s_d3_len) {
            s_d3_w = 0;
        }
        if (s_p.fx3d) {
            r = 0.85f * old - 0.25f * x;
        }
        out_l[i] = to_i16(l);
        out_r[i] = to_i16(r);
    }
}
