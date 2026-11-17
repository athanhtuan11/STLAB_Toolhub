// Gate tren may tinh (Claude viet 2026-11-17, executor KHONG sua): giao thuc UMI + chuoi DSP cua firmware A1S.
// Bien dich: zig cc -std=c11 -O1 -Wall -Werror -I../main run_host.c ../main/umi_proto.c ../main/dsp.c -lm
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "umi_proto.h"
#include "dsp.h"

static int fails = 0;
#define OK(c, m) do { if (c) printf("PASS %s\n", m); else { printf("FAIL %s\n", m); fails++; } } while (0)
#define SR 44100

static void frame_from(const umi_state_t *s, uint8_t *f) {
    memset(f, 0, UMI_FRAME_LEN);
    f[0] = 0x03; f[1] = 0x00; f[2] = 0x01; f[3] = 0x00;
    memcpy(f + 8, s->p + 8, UMI_FRAME_LEN - 8);
}

static double rms(const int16_t *x, int n) {
    double a = 0; for (int i = 0; i < n; i++) a += (double)x[i] * x[i]; return sqrt(a / n);
}

static void run(dsp_params_t *p, const int16_t *in, int16_t *ol, int16_t *or_, int n) {
    dsp_set(p);
    int16_t zr[256] = {0};
    for (int i = 0; i < n; i += 256) {
        int k = n - i < 256 ? n - i : 256;
        dsp_process(in + i, zr, ol + i, or_ + i, k);
    }
}

static dsp_params_t flat(void) {
    dsp_params_t p; memset(&p, 0, sizeof p);
    p.volume = 30; p.tone = 15; p.echo = 0; p.mic = 30; p.string_sens = 75; p.auto_bal = 0; p.amp_out = 0; p.fx3d = 0;
    return p;
}

int main(void) {
    // ---------- A. giao thuc ----------
    umi_state_t s; umi_state_default(&s);
    OK(s.p[8] == 13 && s.p[11] == 0x11 && s.p[15] == 20 && s.p[19] == 12 && s.p[20] == 75 && s.p[25] == 30 && s.p[27] == 0
       && s.p[30] == 20 && s.p[32] == 15, "trang thai mac dinh = gia tri doc tu dan that");
    int ch = -1;
    const uint8_t hello[4] = {0x55, 0xff, 0xfe, 0x01};
    OK(umi_handle_write(&s, hello, 4, &ch) == 1 && ch == 0, "55 ff fe 01 -> gui trang thai, khong doi tham so");
    uint8_t f[UMI_FRAME_LEN];
    frame_from(&s, f); f[15] = 10;
    OK(umi_handle_write(&s, f, UMI_FRAME_LEN, &ch) == 1 && ch == 1 && s.p[15] == 10, "khung 129 byte am luong 10 -> ap dung + bao doi");
    frame_from(&s, f); f[15] = 10;
    OK(umi_handle_write(&s, f, UMI_FRAME_LEN, &ch) == 1 && ch == 0, "khung giong het -> khong bao doi");
    frame_from(&s, f); f[0] = 0x04; f[15] = 5;
    OK(umi_handle_write(&s, f, UMI_FRAME_LEN, &ch) == 0 && s.p[15] == 10, "header sai -> bo qua");
    frame_from(&s, f); f[15] = 5;
    OK(umi_handle_write(&s, f, 50, &ch) == 0 && s.p[15] == 10, "do dai sai -> bo qua");
    frame_from(&s, f); f[15] = 99; f[19] = 200; f[27] = 31; f[25] = 255; f[8] = 77; f[20] = 50; f[21] = 1; f[22] = 9; f[45] = 3;
    umi_handle_write(&s, f, UMI_FRAME_LEN, &ch);
    OK(s.p[15] == 30 && s.p[19] == 30 && s.p[27] == 30 && s.p[25] == 30 && s.p[8] == 30, "chan khoang 0-30 (am luong, am sac, echo, mic, LED)");
    OK(s.p[20] == 75 && s.p[21] == 2 && s.p[22] == 1 && s.p[45] == 1, "chan nhay day 75/100, can bang 0/2, am ly/3D 0/1");
    frame_from(&s, f); f[20] = 95; umi_handle_write(&s, f, UMI_FRAME_LEN, &ch);
    OK(s.p[20] == 100, "nhay day >= 88 -> 100");
    uint8_t st[UMI_FRAME_LEN];
    umi_build_status(&s, 117, st);
    OK(st[0] == 0x03 && st[1] == 0x10 && st[2] == 0x01 && st[3] == 0x00 && st[4] == 117 && st[5] == 0 && st[6] == 0 && st[7] == 0,
       "khung trang thai: 03 10 01 00 <pin> 00 00 00");
    OK(memcmp(st + 8, s.p + 8, UMI_FRAME_LEN - 8) == 0, "khung trang thai chep dung tham so");

    // ---------- B. DSP ----------
    OK(dsp_init(SR) == 0, "dsp_init(44100)");
    OK(dsp_volume_gain(0) == 0.0f && fabsf(dsp_volume_gain(30) - 1.0f) < 1e-3f, "volume 0 = tat, 30 = 1.0");
    int mono = 1; for (int v = 1; v <= 30; v++) if (!(dsp_volume_gain(v) > dsp_volume_gain(v - 1))) mono = 0;
    OK(mono, "volume tang dan");

    const int N = SR;  // 1 s
    int16_t *in = calloc(N, 2), *ol = calloc(N, 2), *or_ = calloc(N, 2);
    for (int i = 0; i < N; i++) in[i] = (int16_t)(8000 * sin(2 * M_PI * 440 * i / SR));
    dsp_params_t p = flat();
    run(&p, in, ol, or_, N);
    int maxd = 0, lr = 1;
    for (int i = 2000; i < N; i++) { int d = abs(ol[i] - in[i]); if (d > maxd) maxd = d; if (ol[i] != or_[i]) lr = 0; }
    OK(maxd <= 2, "phang (vol 30, tone 15, khong hieu ung) = di qua nguyen (sai <= 2 LSB)");
    OK(lr, "khong 3D -> trai = phai");

    dsp_init(SR);
    memset(in, 0, N * 2); in[100] = 20000;
    p = flat(); p.echo = 30; run(&p, in, ol, or_, N);
    int best = 0, at = 0;
    for (int i = 1000; i < N; i++) if (abs(ol[i]) > best) { best = abs(ol[i]); at = i; }
    double dms = (at - 100) * 1000.0 / SR;
    OK(dms > 245 && dms < 255 && best > 4000, "echo 30: tieng vong dau tien ~250 ms, du lon");
    dsp_init(SR);
    p = flat(); p.echo = 0; run(&p, in, ol, or_, N);
    best = 0; for (int i = 1000; i < N; i++) if (abs(ol[i]) > best) best = abs(ol[i]);
    OK(best == 0, "echo 0: khong co tieng vong");

    double r[3]; int tones[3] = {0, 15, 30};
    for (int k = 0; k < 3; k++) {
        dsp_init(SR);
        for (int i = 0; i < N; i++) in[i] = (int16_t)(6000 * sin(2 * M_PI * 5000 * i / SR));
        p = flat(); p.tone = tones[k]; run(&p, in, ol, or_, N); r[k] = rms(ol + 4000, N - 4000);
    }
    OK(20 * log10(r[1] / r[0]) >= 3 && 20 * log10(r[2] / r[1]) >= 3, "am sac 0 < 15 < 30 o 5 kHz (moi buoc >= 3 dB)");

    dsp_init(SR);
    for (int i = 0; i < N; i++) in[i] = (i / 50) % 2 ? 32767 : -32768;
    p = flat(); p.string_sens = 100; p.auto_bal = 2; run(&p, in, ol, or_, N);
    int wrap = 0; for (int i = 2000; i < N; i++) if ((in[i] > 0 && ol[i] < -1000) || (in[i] < 0 && ol[i] > 1000)) wrap++;
    OK(wrap == 0, "vuong full-scale + nhay day 100 + can bang: khong tran so (giu dau)");

    dsp_init(SR);
    for (int i = 0; i < N; i++) in[i] = (int16_t)(8000 * sin(2 * M_PI * 440 * i / SR));
    p = flat(); p.fx3d = 1; run(&p, in, ol, or_, N);
    int diff = 0; for (int i = 4000; i < N; i++) if (ol[i] != or_[i]) diff++;
    OK(diff > N / 4, "3D bat -> trai khac phai");

    p = flat(); p.volume = 0; dsp_init(SR); run(&p, in, ol, or_, N);
    best = 0; for (int i = 0; i < N; i++) if (abs(ol[i]) > best) best = abs(ol[i]);
    OK(best == 0, "volume 0 -> im lang");

    printf("\n%s run_host (%d loi)\n", fails ? "FAIL" : "PASS", fails);
    return fails ? 1 : 0;
}
