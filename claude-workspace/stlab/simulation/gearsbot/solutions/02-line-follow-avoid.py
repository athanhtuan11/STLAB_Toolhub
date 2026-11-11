#!/usr/bin/env python3
# Loi giai mau (giao vien) - Buoi 2: do line + tranh vat can 20 x 20 cm bang sieu am.
# Robot: stlab-line-bot.robot.json | World: line-obstacles.
# Vong tranh: xoay 90 bang encoder banh roi chay cung tron toi khi gap lai line - khong can gyro.
import time
from ev3dev2.motor import *
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *

tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
cam_trai = ColorSensor(INPUT_1)
cam_phai = ColorSensor(INPUT_2)
sieu_am = UltrasonicSensor(INPUT_3)

TOC_DO = 30
KP = 0.6
GAN = 10          # cm: gap vat can gan hon muc nay thi vong tranh
DEN = 30          # do sang duoi muc nay coi la thay line

# Hinh hoc robot ao (cm): banh 4,2; khoang cach 2 tam banh = 13,5 + 2*0,2 + 1,9 = 15,8
BANH = 4.2
VET = 15.8
# Vong tranh = cung tron quanh vat can. Ban kinh cung R = VET/2 * (v_ngoai + v_trong) / (v_ngoai - v_trong)
# = 7,9 * 78 / 22 ~ 28 cm: tam cung ~ tam vat can (gap vat can o 10 cm), mep trong robot cach goc vat can ~5 cm.
V_TRONG = 28
V_NGOAI = 50

def do_quay(goc):
    """So do banh can quay de robot xoay tai cho 'goc' do (banh truot nen chi gan dung)."""
    cung = 3.14159 * VET * goc / 360
    return cung / (3.14159 * BANH) * 360

def thay_line():
    return cam_trai.reflected_light_intensity < DEN or cam_phai.reflected_light_intensity < DEN

def vong_tranh():
    tank_drive.on_for_degrees(30, -30, do_quay(90))     # xoay phai 90: vat can nam ben trai robot
    tank_drive.on(V_TRONG, V_NGOAI)                     # cung tron vong qua ben trai (banh trai cham)
    time.sleep(1.5)                                     # roi khoi line cu truoc khi tim line moi
    while not thay_line():
        time.sleep(0.01)
    tank_drive.on_for_degrees(30, -30, do_quay(60))     # xoay phai, bat lai huong line

while True:
    if sieu_am.distance_centimeters < GAN:
        vong_tranh()
    lech = cam_trai.reflected_light_intensity - cam_phai.reflected_light_intensity
    tank_drive.on(TOC_DO + KP * lech, TOC_DO - KP * lech)
    time.sleep(0.01)
