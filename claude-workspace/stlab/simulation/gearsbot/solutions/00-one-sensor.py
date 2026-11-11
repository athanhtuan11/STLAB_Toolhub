#!/usr/bin/env python3
# Chuong trinh mau buoi 1 (giao vien phat san): do line bang 1 cam bien (cam bien trai, cong 1).
# Thay den -> re trai, thay trang -> re phai: robot di "zigzag" men theo mep line.
# Dung de thi nghiem doi VI TRI cam bien trong Robot Configurator (truoc truc / tren truc / sau truc).
import time
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *

tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
cam = ColorSensor(INPUT_1)

DEN = 50   # do sang duoi muc nay coi la den (line)

while True:
    if cam.reflected_light_intensity < DEN:
        tank_drive.on(5, 30)    # thay line -> re trai
    else:
        tank_drive.on(30, 5)    # thay nen trang -> re phai
    time.sleep(0.01)
