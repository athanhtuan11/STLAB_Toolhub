// Do dien ap pin qua chia ap 100k/100k vao GPIO1 (ADC1_CH0), co hieu chinh ADC.
#pragma once

void batt_init(void);

// mV tai pin (da nhan 2), trung binh 8 mau, cap nhat moi 500 ms. 0 neu chua do lan nao.
int batt_mv(void);
