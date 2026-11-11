#!/usr/bin/env python3
# Loi giai mau (giao vien) - Buoi 1: do line bang 2 cam bien mau, dieu khien ti le (P).
# Robot: stlab-line-bot.robot.json | World: line-simple / line-sharp.
# Ban that (maker/line-bot) dung cung y tuong: lech = trai - phai -> chinh toc do 2 banh.
import time
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *

tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
cam_trai = ColorSensor(INPUT_1)
cam_phai = ColorSensor(INPUT_2)

TOC_DO = 30   # % toc do co ban
KP = 0.6      # he so ti le: lon qua -> lac, nho qua -> truot khoi khuc cua

while True:
    lech = cam_trai.reflected_light_intensity - cam_phai.reflected_light_intensity
    # line (den, sang thap) nam duoi cam bien trai -> lech am -> banh trai cham lai -> re trai
    tank_drive.on(TOC_DO + KP * lech, TOC_DO - KP * lech)
    time.sleep(0.01)
