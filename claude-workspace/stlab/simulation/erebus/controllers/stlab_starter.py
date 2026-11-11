"""Controller khoi dau cho doi RCJ Rescue Simulation (Erebus) - STLab.

Robot: robot MAC DINH cua trang https://robot.erebus.rcj.cloud (2 banh + 4 cam bien khoang cach phia truoc:
"distance sensor1".."distance sensor4").
Trong robot mac dinh: wheel1 o x=+260 va la banh TRAI (theo ExamplePlayerController cua Erebus) -> +x = trai,
nen sensor1 (x=-213) o ben PHAI, sensor4 (x=+220) o ben TRAI. TODO: xac nhan khi chay that. Doi robot thi sua TEN_CAM_BIEN cho khop customName.
Viec lam: chay thang, gap tuong phia truoc thi xoay tai cho ve phia thoang hon. CHUA do ban do/nan nhan -
day la buoc 1 de doi lam quen Webots + Erebus.

CHUA CHAY THU (2026-11-11): may STLab chua cai Webots R2023b. Ten thiet bi, don vi lay tu ma Erebus v26
(ProtoGenerator.py: "<customName> motor", cam bien khoang cach tra met 0-0,8; maxVelocity 6,28 rad/s).
"""
from controller import Robot

TIME_STEP = 32
MAX_VEL = 6.28                       # rad/s - gioi han banh cua Erebus
TOC_DO = 0.5 * MAX_VEL
GAN = 0.06                           # m: tuong gan hon muc nay thi xoay
TEN_CAM_BIEN = ["distance sensor1", "distance sensor2", "distance sensor3", "distance sensor4"]

robot = Robot()
banh_trai = robot.getDevice("wheel1 motor")
banh_phai = robot.getDevice("wheel2 motor")
for b in (banh_trai, banh_phai):
    b.setPosition(float("inf"))     # che do dieu khien van toc
    b.setVelocity(0.0)

cam = [robot.getDevice(t) for t in TEN_CAM_BIEN]
for c in cam:
    c.enable(TIME_STEP)

dem = 0
while robot.step(TIME_STEP) != -1:
    d = [c.getValue() for c in cam]          # met, 0 - 0,8
    dem += 1
    if dem % 30 == 0:
        print("khoang cach (m):", ["%.2f" % x for x in d])
    truoc = min(d[1], d[2])
    if truoc < GAN:
        # d[3] = ben trai, d[0] = ben phai: trai thoang hon -> xoay trai, nguoc lai xoay phai
        if d[3] > d[0]:
            banh_trai.setVelocity(-TOC_DO)
            banh_phai.setVelocity(TOC_DO)
        else:
            banh_trai.setVelocity(TOC_DO)
            banh_phai.setVelocity(-TOC_DO)
    else:
        banh_trai.setVelocity(TOC_DO)
        banh_phai.setVelocity(TOC_DO)
