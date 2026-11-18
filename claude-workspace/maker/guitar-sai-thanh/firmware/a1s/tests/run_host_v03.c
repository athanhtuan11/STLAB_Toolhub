// Gate v0.3 tren may tinh (Claude viet 2026-11-18, executor KHONG sua): module mix (ring A2DP + doi tan so + tron).
// Bien dich: zig cc -std=c11 -O1 -Wall -Werror -I../main run_host_v03.c ../main/mix.c -lm
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mix.h"

static int fails = 0;
#define OK(c, m) do { if (c) printf("PASS %s\n", m); else { printf("FAIL %s\n", m); fails++; } } while (0)
#define PI 3.14159265358979323846

static mix_t M;  // tinh (struct co the lon)

// tao khung stereo sine tan so f tai rate, bat dau tu mau thu `start`
static void sine_lr(int16_t *lr, int frames, int rate, double f, long start, double amp, int r_inv) {
    for (int i = 0; i < frames; i++) {
        double v = amp * sin(2 * PI * f * (double)(start + i) / rate);
        lr[2 * i] = (int16_t)lrint(v);
        lr[2 * i + 1] = (int16_t)lrint(r_inv ? -v : v);
    }
}

// dem diem cat 0 di len -> tan so
static double freq_of(const int16_t *x, int n, int rate) {
    int first = -1, last = -1, cnt = 0;
    for (int i = 1; i < n; i++)
        if (x[i - 1] < 0 && x[i] >= 0) { if (first < 0) first = i; last = i; cnt++; }
    if (cnt < 2) return 0;
    return (double)(cnt - 1) * rate / (last - first);
}

static double rms(const int16_t *x, int n) {
    double a = 0; for (int i = 0; i < n; i++) a += (double)x[i] * x[i]; return sqrt(a / n);
}

int main(void) {
    static int16_t lr[2 * 4096], out[16384], tmp[512];

    // 1. khoi tao
    mix_init(&M);
    OK(mix_fill(&M) == 0 && mix_underruns(&M) == 0 && mix_overflows(&M) == 0, "mix_init: ring rong, bo dem 0");
    OK(MIX_RING_CAP == 8820 && MIX_PRIME == 4410 && MIX_RATE == 44100, "hang so ring 200 ms / prime 100 ms / 44100");

    // 2. chua primed -> ra 0
    sine_lr(lr, 1000, 44100, 1000, 0, 10000, 0);
    int w = mix_push_pcm(&M, lr, 1000);
    OK(w == 1000, "44100 -> 44100: 1000 khung -> 1000 mau");
    for (int i = 0; i < 256; i++) out[i] = 123;
    int g = mix_pop(&M, out, 256);
    int allz = 1; for (int i = 0; i < 256; i++) if (out[i]) allz = 0;
    OK(g == 0 && allz, "fill < MIX_PRIME: mix_pop tra 0 va ghi so 0");
    OK(mix_fill(&M) == 1000, "chua primed khong tieu mau");

    // 3. du prime -> phat dung du lieu (44100 -> khong doi tan so, giu bien do)
    mix_reset(&M);
    OK(mix_fill(&M) == 0, "mix_reset xa ring");
    long t = 0;
    for (int k = 0; k < 5; k++) { sine_lr(lr, 1000, 44100, 1000, t, 10000, 0); t += 1000; mix_push_pcm(&M, lr, 1000); }
    OK(mix_fill(&M) == 5000, "fill = 5000 sau 5 x 1000");
    int got = 0;
    for (int k = 0; k < 16; k++) got += mix_pop(&M, out + 256 * k, 256);
    OK(got == 4096, "primed: 16 x 256 mau that");
    double f = freq_of(out, 4096, 44100), a = rms(out, 4096);
    OK(fabs(f - 1000) < 10, "44100: tan so 1000 Hz giu nguyen");
    OK(fabs(a - 10000 / sqrt(2)) < 300, "44100: bien do giu nguyen (rms ~7071)");

    // 4. tron mono (L+R)/2: L = -R -> 0
    mix_init(&M);
    t = 0;
    for (int k = 0; k < 6; k++) { sine_lr(lr, 1000, 44100, 500, t, 12000, 1); t += 1000; mix_push_pcm(&M, lr, 1000); }
    mix_pop(&M, out, 4096);
    int mx = 0; for (int i = 0; i < 4096; i++) if (abs(out[i]) > mx) mx = abs(out[i]);
    OK(mx <= 2, "mono (L+R)/2: L nguoc pha R -> ~0");

    // 5. 48000 -> 44100: so mau + tan so
    mix_init(&M);
    mix_set_src_rate(&M, 48000);
    t = 0; int tot = 0;
    for (int k = 0; k < 50; k++) {  // 50 x 96 = 4800 khung = 100 ms
        sine_lr(lr, 96, 48000, 1000, t, 10000, 0); t += 96; tot += mix_push_pcm(&M, lr, 96);
    }
    OK(abs(tot - 4410) <= 3, "48000 -> 44100: 4800 khung -> ~4410 mau (pha lien tuc giua cac lan goi)");
    OK(mix_fill(&M) == tot, "fill = so mau da ghi");
    got = mix_pop(&M, out, 4096);
    f = freq_of(out, got, 44100);
    OK(got == 4096 && fabs(f - 1000) < 10, "48000 -> 44100: sine 1000 Hz van 1000 Hz");
    a = rms(out + 100, 3900);
    OK(fabs(a - 10000 / sqrt(2)) < 400, "48000 -> 44100: bien do giu (rms ~7071)");
    int jump = 0; for (int i = 1; i < 4096; i++) if (abs(out[i] - out[i - 1]) > 1600) jump++;
    OK(jump == 0, "48000 -> 44100: khong co buoc nhay (khong mat/lap mau o ranh gioi khoi 96)");

    // 6. 32000 / 16000 -> 44100 so mau; rate la -> giu nguyen
    mix_init(&M); mix_set_src_rate(&M, 32000);
    t = 0; tot = 0;
    for (int k = 0; k < 10; k++) { sine_lr(lr, 320, 32000, 440, t, 8000, 0); t += 320; tot += mix_push_pcm(&M, lr, 320); }
    OK(abs(tot - 4410) <= 3, "32000 -> 44100: 3200 khung -> ~4410 mau");
    mix_init(&M); mix_set_src_rate(&M, 16000);
    t = 0; tot = 0;
    for (int k = 0; k < 10; k++) { sine_lr(lr, 160, 16000, 440, t, 8000, 0); t += 160; tot += mix_push_pcm(&M, lr, 160); }
    OK(abs(tot - 4410) <= 3, "16000 -> 44100: 1600 khung -> ~4410 mau");
    mix_init(&M); mix_set_src_rate(&M, 22050);
    sine_lr(lr, 441, 44100, 440, 0, 8000, 0);
    OK(mix_push_pcm(&M, lr, 441) == 441, "rate khong ho tro (22050) -> giu 44100");

    // 7. tran ring
    mix_init(&M);
    t = 0; tot = 0;
    for (int k = 0; k < 3; k++) { sine_lr(lr, 4000, 44100, 300, t, 5000, 0); t += 4000; tot += mix_push_pcm(&M, lr, 4000); }
    OK(tot == MIX_RING_CAP && mix_fill(&M) == MIX_RING_CAP, "day: ghi toi da MIX_RING_CAP");
    OK(mix_overflows(&M) == 12000 - MIX_RING_CAP, "overflows dem dung so mau bi bo");

    // 8. can (underrun) -> dem + ve chua primed
    mix_init(&M);
    t = 0;
    for (int k = 0; k < 5; k++) { sine_lr(lr, 1000, 44100, 300, t, 5000, 0); t += 1000; mix_push_pcm(&M, lr, 1000); }
    got = 0; for (int k = 0; k < 19; k++) got += mix_pop(&M, out, 256);  // 4864
    OK(got == 4864, "doc 19 x 256");
    for (int i = 0; i < 256; i++) out[i] = 77;
    g = mix_pop(&M, out, 256);     // con 136
    int tailz = 1; for (int i = 136; i < 256; i++) if (out[i]) tailz = 0;
    OK(g == 136 && tailz, "thieu: tra phan that + phan con lai = 0");
    OK(mix_underruns(&M) == 1, "underruns = 1");
    sine_lr(lr, 1000, 44100, 300, t, 5000, 0); t += 1000; mix_push_pcm(&M, lr, 1000);
    g = mix_pop(&M, out, 256);
    OK(g == 0, "sau khi can: phai doi du MIX_PRIME moi phat lai");
    for (int k = 0; k < 4; k++) { sine_lr(lr, 1000, 44100, 300, t, 5000, 0); t += 1000; mix_push_pcm(&M, lr, 1000); }
    OK(mix_pop(&M, out, 256) == 256, "du MIX_PRIME lai -> phat");

    // 9. vong quanh chi so (nhieu lan ghi/doc qua CAP)
    mix_init(&M);
    t = 0; long pushed = 0, popped = 0; int bad = 0;
    for (int k = 0; k < 400; k++) {
        sine_lr(lr, 256, 44100, 1000, t, 9000, 0); t += 256; pushed += mix_push_pcm(&M, lr, 256);
        int r = mix_pop(&M, tmp, 256); popped += r;
        if (r && r != 256) bad++;
    }
    OK(bad == 0 && pushed - popped == mix_fill(&M) && mix_overflows(&M) == 0, "400 vong ghi/doc: chi so quay vong dung, khong tran");
    f = freq_of(tmp, 256, 44100);
    OK(fabs(f - 1000) < 60, "sau vong quanh: du lieu van dung (1000 Hz)");

    // 10. mix_add bao hoa + he so
    {
        int16_t L[4] = {1000, 30000, -30000, 0}, R[4] = {-1000, 30000, -30000, 0}, mu[4] = {2000, 10000, -10000, 0};
        mix_add(L, R, mu, 4, 0.5f);
        OK(L[0] == 2000 && R[0] == 0, "mix_add: cong music*gain");
        OK(L[1] == 32767 && R[1] == 32767 && L[2] == -32768 && R[2] == -32768, "mix_add: bao hoa, khong tran so");
        OK(L[3] == 0, "mix_add: music 0 khong doi");
        int16_t L2[2] = {500, -500}, R2[2] = {500, -500}, mu2[2] = {30000, -30000};
        mix_add(L2, R2, mu2, 2, 0.0f);
        OK(L2[0] == 500 && L2[1] == -500, "mix_add gain 0 -> giu nguyen");
    }

    printf("\n%s run_host_v03 (%d loi)\n", fails ? "FAIL" : "PASS", fails);
    return fails ? 1 : 0;
}
