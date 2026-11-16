// Am thanh tu sinh qua I2S + MAX98357A (16 kHz, 16 bit). Bien do toi da SOUND_MAX_PCT % full-scale.
#pragma once

void sound_init(void);

// Phat am id (0 bip, 1 coi 2 tong, 2 nhac vui 4 not). Chan toi khi phat xong hoac sound_stop(); tat kenh I2S khi xong.
void sound_play(int id);

// Dung ngay (goi tu task khac duoc). Co hieu luc voi lan phat dang chay.
void sound_stop(void);
