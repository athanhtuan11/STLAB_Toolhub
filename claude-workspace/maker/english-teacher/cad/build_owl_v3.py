# build_owl_v3.py - CAD Cu Bong v3 LAP RAP THAT (spec-owl-v3-assembly.md, Claude 2026-11-27) tu ban s3-screen. Blender 5.2 bpy/bmesh.
# Vo truoc = khung (moi chi tiet bat vit/lay vao vo truoc), vo sau = nap (lo sac + 6 gieng vit M2.5 x 12), be rong chong lat.
# Chay: "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python-exit-code 1 -P build_owl_s3.py -- out-s3
# He lap rap: mm, +Z len, mat truoc = -Y, x ngang. Mat ranh gioi hai nua vo: mat phang y = Y0.
import bpy, bmesh, math, json, sys, os, shutil
from pathlib import Path
from mathutils import Vector, Matrix

OUT = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
OUT.mkdir(parents=True, exist_ok=True)

# ============================================================ THAM SO (mm)
WALL = 2.4                 # thanh vo
SPEAKER_POCKET_D = 52.6    # loa O52 + khe 0,3/ben
SPEAKER_D, SPEAKER_L = 52.0, 26.0

# Co cau giu loa bang mep truoc (Tuan do mep day 5, than < O39) - KHONG VIT:
# ron EVA giua mat tam luoi va mat loa; vong ep NGAM XOAY (bayonet): 3 chot tren ong om vanh loa, 3 ranh chu L trong ong tay vong ep;
# an vong ep vao (ep them ron) roi xoay BAY_TWIST, nha ra -> ron day vong ep lui, mat tren chot ty vao vach ranh -> khoa.
FLANGE_T, GASKET_T = 5.0, 1.5          # GASKET_T: khe danh nghia mat luoi - mat loa khi chua ep them
BODY_D_MAX = 39.0                      # than loa < O39
SRING_T, RING_ID = 2.4, 48.0           # vong ep loa. 2026-11-26 Tuan: O47 khong dua loa vo duoc -> O48,0 (de mep O52 2,0/ben)
BAY_ANG = (90.0, 210.0, 330.0)         # goc 3 chot (vi tri da khoa)
BAY_TWIST = 30.0                       # goc xoay khoa
BPIN_W, BPIN_H, BPIN_T = 4.0, 1.1, 1.5 # chot: rong tiep tuyen, nho ra, day doc truc
BPIN_DZ = 2.5                          # mat duoi chot cach mat cuoi ong om
SLEEVE_CLR, BPIN_CLR, GROOVE_CLR = 0.40, 0.40, 0.45   # 2026-11-26 Tuan: vong ep qua khit (0,25/0,25/0,30) -> noi, CHI phia vong ep (bezel da in giu nguyen)
SLEEVE_T, SLEEVE_LEN = 2.4, 5.0
LIP_PRE, OUT_GAP = 0.3, 0.3
GRILLE_HOLE_D, GRILLE_PITCH, GRILLE_ZONE_D = 2.8, 5.6, 56.0
MIC_HOLE_D = 2.0
M3_CLEAR_D, M3_NUT_S, NUT_DEPTH = 3.4, 5.9, 2.8   # 2026-11-26: tui ecu M3 5,5 AF + 0,2/ben = 5,9 (cu 5,8: 0,15/ben)
BUTTON_CAP_D, BUTTON_HOLE_D = 50.0, 50.8
DIFFUSER_T = 0.8
VENT_W, VENT_L = 2.0, 18.0

# S3 LINH KIEN:
# Bo ESP32-S3: hop giu cho 72 x 29 x 16 (pcb_box), dung dung o nua sau, dau USB xuong duoi
PCB_BOX = (29.0, 72.0, 16.0)          # x rong, y DAI (nam ngang, dau USB ve LUNG +y), z day
PCB_Y_USB = 44.7                      # mat cong USB (y); dau truoc bo o y = 44,7 - 72 = -27,3 (sat than loa y <= -28,6)
PCB_CENTER = [0.0, PCB_Y_USB - PCB_BOX[1] / 2, 34.0]
USB_GAP_ROOF = 0.3                    # mai hoc (chan mai) cach mat cong 0,3 mm; dinh mai cao hon 8,2 (45 do)
CABLE_W, CABLE_H, CABLE_R = 14.0, 9.0, 2.0   # lo cap USB-C thang, chu nhat bo goc R2

# 2 ampli MAX98357A (moi loa 1 cai), khay amp-tray v2 dat tren san khoang bay mo rong 2 ben (xem make_bays)
AMP_BOX = (22.0, 22.0, 10.0)
AMP_POS = [(-3.0, -13.0), (3.0, 12.5)]  # 2 khay duoi bo S3 giua 2 ray (|x| < 14,8), 1 o nua truoc, 1 o nua sau
AMP_Z0 = 7.3                           # day khay (san bay z = 6,0 + 0,4 khe)

# Mic INMP441 PCB tron O15, NGHIENG 45 do theo vom tran (spec muc 9): truc n = (0, -cos45, +sin45) huong ra truoc-len
MIC_DROP = 0.9                         # 2026-11-26: ha mic 0,9 de nap nut di >= 4,5 mm (nap/hoc con GIU theo MIC_C_REF cu)
MIC_C_REF = (0.0, -29.2, 133.3)        # tam mic cu: chi dung de tinh con hoc duoi nap (CAP_DISH_K)
MIC_C = (0.0, -29.2, 133.3 - MIC_DROP) # tam module that
MIC_N = Vector((0.0, -math.sqrt(0.5), math.sqrt(0.5)))
MIC_T = Vector((0.0, math.sqrt(0.5), math.sqrt(0.5)))   # tiep tuyen "len-sau" tren mat module
MIC_L = 8.3 + 0.64                     # tam module -> mat ngoai vom doc truc (+0,64 vi ha mic 0,9 theo z)
MIC_PCB_D, MIC_PCB_T = 15.0, 1.6
MIC_BORE_R = 8.0                       # khoang module O16 (PCB O15 + 0,5/ben), w -0,5..+6,2 (cham tren khoang truoc)
MIC_FRONT_W = 6.2                      # buong truoc module: w tu 0,8 den 6,2 (khong vat nao trong Y-dia cua gate)
MIC_SLEEVE_BORE_R = 10.9               # lo ong lot (sleeve) phia sau, thong xuong khoang than (tent)
MIC_HOLE_X = (-1.5, 0.0, 1.5)
# Bit mic = RON XOP (bo me cung): hoc PCB sau them den w = 1,8 (khong ranh -> khong overhang them): PCB mat truoc w 0,8, mat vach w 1,8
# -> khe ron 1,0 mm; ron xop vong 1,2 mm (OD 12 / ID 6,4) dan len vach quanh ong dan am O4, PCB ep ron 0,2 (17 %)
MIC_TRAVEL_BVH = 4.85                  # hanh trinh nap truoc khi cham PCB mic (do BVH sau khi ha mic 0,9; kep mic 8,05)
MIC_GASKET_T = 1.2
MIC_POCKET_W1 = 1.8                    # vach truoc hoc PCB (cu 1,0)
MIC_GASKET_OD, MIC_GASKET_ID = 12.0, 6.4
MIC_TUBE_OD, MIC_TUBE_ID = 7.4, 4.0

# 2 loa NGANG H0 (Tuan chon 2026-11-26): truc ra ngoai [+-1,0,0], mat loa tren vo suon, vanh loa + yen non nhu ban A1S
SPK_A = Vector((1.0, 0.0, 0.0))
SPK_CX, SPK_CY, SPK_Z = 51.8, 0.37, 46.0
BZL_RF, BZL_REAR, BZL_A, BZL_RHO = 38.0, 54.0, 25.0, 8.0   # BZL_RF 36 -> 38: vanh loa +2,0 mm ban kinh (Tuan 2026-11-26)
BZL_T = math.tan(math.radians(BZL_A))
SPEAKERS = [{"center": [-SPK_CX, SPK_CY, SPK_Z], "axis": [-1.0, 0.0, 0.0]},
            {"center": [SPK_CX, SPK_CY, SPK_Z], "axis": [1.0, 0.0, 0.0]}]

# MAN TFT 2,8" MSP2807 (ban ve LCDWiki): tam PCB (0, ?, 100), header +x
SCR_ZC = 100.0
SCR_PCB = (86.0, 50.0, 1.6); SCR_GLASS = (69.2, 50.0); SCR_AA = (57.6, 43.2); SCR_T = 5.6
SCR_HOLES = (80.0, 44.0); SCR_HOLE_D = 3.2   # hang that V1.1 (Tuan do 2026-11-26): doi xung
GLASS_RECESS = 1.5                     # spec muc 9: vien 1,35 sau khe 0,15
YS_OUT = -53.0                         # mat phang nen (thang dung), y
YF = YS_OUT - 4.0                      # mat truoc dia nho 4 so voi nen
GLASS_Y = YF + GLASS_RECESS
SCR_PCB_Y = GLASS_Y + (SCR_T - SCR_PCB[2]) + SCR_PCB[2] / 2      # tam PCB (y)
WIN = (58.4, 44.0, 2.5, -4.9)          # rong, cao, goc, lech x
DISC = (47.0, 29.0, 14.0)              # nua rong, nua cao, goc R14 (muc 12: dia mat bo R14 trong mat phang)
DISC_YR = 10.0                         # goc R cua yen vat/vanh chan (giu nhu ban da in; vit goc o (45,5; 27,5) nam trong goc nay)
YEN_TR = 1.7                           # chuyen R14 -> R10 bang 45 do (khong mai treo) truoc khi yen vat bat dau
FR_R = 3.0                             # mep truoc dia bo R3 (+ vat 0,88 x 45 do cho cham ban in)
T0, BEV, FL_T = 8.0, 5.0, 2.0          # nen thang sau 8; yen vat 45 do rong 5; vanh chan day 2,0
FP_SHELL_GAP = 0.3
PAD_W, PAD_H = 55.2, 37.2              # nua kich thuoc nen toi da (lo 104,6 x 68,6 + thanh >= 2,3)
PAD_A = 6.4                            # vai ellip: lech ngang tu mep phang (48,8 x 30,8) ra thanh day du
PAD_B = 26.0                           # vai ellip: sau (u 4 -> 30) toi cho gap vo cong (khong con thanh thang)
YU0 = T0 + 4.0                         # u bat dau yen (12)
YU1 = YU0 + YEN_TR                     # yen 45 do bat dau
YU2 = YU1 + BEV                        # yen ket thuc
U_END = YU2 + FL_T                     # mat sau vanh chan (20,7)
HOLE_END = U_END + 2.0                 # lo vo ket thuc, pheu bat dau
SCREW_FP = (45.5, 27.5)                # 4 vit M2.5 x 6 o 4 goc (xem README: doi khoi (49, 31) vi goc R15 cua vanh)

FIT, SLIDE = 0.3, 0.2
Y0 = 0.37                  # mat phang ranh gioi 2 nua
BZ, BR, NT, NB, TAPER = 78.0, (66.0, 56.0, 80.0), 2.2, 4.2, 0.05
FLOOR_CUT = 4.0           # vo cat phang o z = 4; tam de day 4 mm
CZ, CRAD = 81.0, (BR[0] - WALL, BR[1] - WALL, 74.6)
CONE_T = math.tan(math.radians(10))
CONE_CLR = 0.3

# Tam bung: giu nguyen ban A1S de khong bi lech yen non
BELLY_Z, BELLY_FRONT, BELLY_RF, BELLY_REAR = 28.0, -58.5, 18.0, -42.0

# Hinh hoc vanh loa theo truc Y (local z -> world -y)
SPK_XF = 69.0
SPK_FACE = SPK_XF - 3.0 - GASKET_T
CUP_END = SPK_FACE - FLANGE_T
CUP_OR = SPEAKER_POCKET_D / 2 + 2.7
z_spk_center = SPK_FACE + LIP_PRE - SPEAKER_L / 2

EYE_X, EYE_Z, BEAK_Z = 36.5, 108.0, 102.0
RING_D, RING_T = 54.0, 3.0
BTN_TOP, SEAT_Z = 166.0, 145.0

# Switch MX (fit-library catpaw)
MX_HOLE, MX_DEPTH, MX_STEM_L, MX_STEM_W, MX_STEM_H = 14.0, 8.58, 4.19, 1.25, 3.6
MX_BODY_UP, MX_BODY_W, MX_HOUSING_H = 15.6, 5.0, 3.0
MX_GROOVE = (1.94, 2.69, 3.44, 15.44)
MX_INSERT, MX_TRAVEL = 1.2, 2.4
# 2026-11-18 Tuan: button-cap khong nhet duoc chan switch (chu thap khoet thang vao khoi dac, PETG co lo). Theo mau catpaw: chu thap
# nam trong ONG NHUN O5,71, ranh vong quanh ong de ong gian nhe khi ep. Kem bo thu chu thap 3 co (mx-cross-gauge.stl).
MX_TUBE_OD, MX_RELIEF_R, MX_RELIEF_H = 5.71, 4.6, 4.0
MX_GAUGE_W = (1.25, 1.35, 1.45)
# 2026-11-26 Tuan in thu: nap nut chim xuong (nap khong an chu thap, mat phang duoi nap chay vo switch). Lam lai theo clicky chay that
# (catpaw/mx-keycap-cross + mx-socket, docs/research-notes/cat-paw-clicker-fits.md): hoc duoi nap sau 9,80 tu vanh, ong O5,71 dau ong o +4,31 tren vanh,
# lo chu thap 4,19 x 1,25 xuyen het ong (5,49); mieng o switch nam o DAY HOC (nhu mau), o 14,00 sau 8,58 + ranh V.
CAP_HOLLOW_R, CAP_CEIL, CAP_TUBE_END, MX_CROSS_DEPTH = 16.6, 9.80, 4.31, 5.49     # mau cat-paw (hoc O33,2 >= 33,15 x 24,2)
CAP_STOP_GAP = 1.0                  # khe doc truc vanh nap <-> go chan cua vo luc nghi (nap khong ep, chu thap van an 5,49)
TUBE_GAP = 1.0                      # dau ong nap cao hon dinh vo switch luc nghi -> chu thap an MX_STEM_H - TUBE_GAP = 2,6 mm vao chan
MX_TOWER_W = 17.0                   # ong ngoai o switch cua mau cat-paw (17 x 17); ban nay o khoet thang vao khoi dac dau, day hoc phang o muc mieng
REST_UP = 0.3 - CAP_STOP_GAP        # dung de khe doc truc go chan = CAP_STOP_GAP (nap hanh theo mat con va vanh)
CONE_CLR_KEY = 0.3

# Vol-pod o lung (2 nut am luong)
VOL_X, VOL_Z = 24.0, 103.0
VOL_NECK_R, VOL_HOLE_R, VOL_FLANGE_R = 4.0, 4.5, 6.8
POD_W, POD_CB, POD_CT, POD_D = 9.6, -9.6, 10.35, 22.0
POD_PLATE, POD_BAY, POD_CLOSE = 3.0, 15.8, 7.95
POD_GAP, POD_RECESS = 0.3, 0.5
POD_DISH_R = 9.0
POD_TF, POD_STRIP = 3.0, (-18.8, -5.6, POD_CT - 0.5, 20.7)
POD_HOLES = ((-9.2, 12.3), (-15.2, 17.0))
SCR_CLEAR, SCR_HEAD, SCR_PILOT, SCR_PILOT_DEPTH, SCR_LEN = 2.8, 5.0, 2.2, 6.2, 10.0
EAR_GAP, G_HEAD = 0.4, 4.0
TALK_FLANGE_R = 27.0   # 2026-11-26: 29 -> 27 (van nap lot goc PCB mic khi an 4 mm; van trong rong hon lo 1,6 >= 1,5)
TALK_ZB = 139.0
TENT_XM, TENT_ZLO, TENT_ZHI = 48.0, 6.0, 124.0
TENT_SL = 1.0
TENT_FLAT = 1.0
SCREW_X, SCREW_Y = 9.0, 14.0
BOSSES = [(sx, sy) for sx in (-24.0, 24.0) for sy in (-14.0, 14.0)]
BOSS_TOP = 16.0
PIN_D, PIN_HALF = 2.0, 8.0

# ============================================================ V3 (spec-owl-v3-assembly.md)
# Moi vit trong long Cu song song truc y, bat tu mat rap khi vo truoc nam ngua (vo sau chua dong) -> tua vit thang O8 x 80.
SHELL_SCREWS = [(-47.0, 11.0), (47.0, 11.0), (-52.0, 113.0), (52.0, 113.0), (-35.0, 151.0), (35.0, 151.0)]   # (x, z) tren mat rap
SCREW_L = 12.0             # M2.5 x 12 tu ren noi 2 nua (TODO Tuan xac nhan co san; doi chieu dai -> doi SCREW_L, an ren >= 6)
WELL_FLOOR, WELL_D, THRU_D, PILOT_D = 3.0, 5.6, 2.8, 2.4    # gieng vo sau: day 3,0; lo thong O2,8; mui O2,4 (fit-library, da in)
SHELL_BOSS_R = 4.8
EAR_T, EAR_CLR = 3.0, 0.2  # tai vit chi tiet (vanh loa, khay, de nut): day 3,0, hoc tren vo truoc +0,2/ben, mat tai thap hon mat rap 0,1
EAR_Y1 = Y0 - 0.1          # mat tren tai (phia vo sau)
EAR_Y0 = EAR_Y1 - EAR_T    # mat duoi tai (ty len day hoc)
SCREW6_PILOT = 4.6         # M2.5 x 6 qua tai 3,0: mui O2,4 sau 4,6 duoi tai (an ren 3,0 + du)
HEAD_D, HEAD_T = 8.0, 3.8  # hoc dau vit tren mat rap vo sau: CON 45 do O8 -> dinh (tai 1,7 con O4,6 > dau O4,5), khong tran phang
DRIVER_D, DRIVER_L = 8.0, 80.0
# vanh loa: 1 vay vit (2 vit M2.5 x 6) noi tiep mep sau vanh, 2 canh vat 45 do (in mat loa xuong ban khong support)
BZ_FIN = [(54.6, 42.8), (45.5, 33.7), (45.5, 53.5), (54.6, 44.4)]      # (|x|, r) r = khoang cach toi truc loa theo +z
BZ_FIN_SCREWS = [(47.4, 40.4), (47.4, 46.8)]   # cach 6,4 > hoc dau O6; vach toi 2 canh vat >= 1,2 (lo sat canh -> manh treo khi in)
BZ_TRIM_Z = FLOOR_CUT + 0.3          # vanh loa cat phang day (be o duoi z 4)
# 2026-11-27 Tuan "vanh loa chi co vit tren, co ro khong": them VIT DAY M2.5 x 12 tu duoi de len tru O6 o day vanh (giu 2 dau).
BZ_BOT_X, BZ_BOT_R, BZ_BOT_TOP = 57.5, 3.0, 13.0     # tru: x 54,5..60,5 (vach leu x 54 cach 0,5), dinh 13,0 (vong ep z 14,2 cach 1,2)
BZ_BOT_CB_D, BZ_BOT_CB_H = 5.4, 1.8                   # hoc dau vit duoi de (dau O4,5 + 0,9); an ren = 12 - (6 - 1,8) - 0,3 = 7,5
DET_H, DET_W = 0.20, 1.2                              # nac khoa vong ep: go 0,20 tren mat ranh ngang; an vong ep 0,25 (< OUT_GAP 0,3 cham coc, < khe ranh 0,45) la qua; rong 1,2; TODO in thu
# be (tam de moi): sieu ellip lech truoc, day phang, vat 45 do mep tren, 4 bu-long M3 tu duoi (giu hoc dai oc 5,9)
BASE_BOT, BASE_TOP = -2.0, FLOOR_CUT
BASE_HX, BASE_YF, BASE_YB, BASE_N = 62.0, 62.0, 50.0, 2.6
BASE_CH, BASE_BCH = 2.5, 0.8
FOOT_D, FOOT_T = 10.4, 1.0           # hoc chan cao su O10 (TODO chon loai), khe 0,2
FEET = [(-40.0, -38.0), (40.0, -38.0), (-38.0, 32.0), (38.0, 32.0)]
# khay chung bo S3 + 2 ampli (Tuan: so ray/khoi bo hien tai dung -> giu; ampli DUNG o 2 mat ngoai ray, sat loa cua no)
TRAY_Z0, TRAY_T = 8.6, 2.5   # tren san cong cua khoang (z ~7-8)
TRAY_Y1_V3 = 29.5                   # duoi ray (y): <= 30 de khay nam gon duoi mai leu 45 do cua vo sau (khong tran phang); bo S3 dai ra sau tua hoc vo sau
TRAY_TAB_X1, TRAY_TAB_H, TRAY_SCREW_X = 30.0, 4.6, 26.0   # tai cao 4,6 -> tran hoc 5,0 khi in (cau <= 5)
AMP_PCB_W, AMP_PCB_L = 18.0, 19.4    # MAX98357A (giu so khay v2; TODO do module that)
AMP_YC = -3.0                        # tam ampli theo y (ca 2 ben)
AMP_ZB = 20.5                        # canh duoi PCB ampli (cot giu vat 45 do tu z 16,3, tren khoi tru bu-long de z 16)
AMP_BACK_GAP = 1.5                   # mat sau PCB cach thanh ray (chan han)
# de nut (o switch MX tach khoi vo): giu nguyen o 14,00 + ranh V, bat 2 vit M2.5 x 6 vao vo truoc
BB_HALF, BB_WING_X1, BB_WING_H, BB_SCREW_X = 11.0, 21.0, 4.6, 16.5
# lap tu ngoai: hoc chim 1,0 cho vanh + lay gai (gá 0,8 + khe 0,2; dai >= 10, day 1,2)
FP_LIP, FP_BODY_END, FP_WIN_U = 1.5, 17.5, 15.5
HOLE_END3 = 20.0
BELLY_SEAT, BELLY_BORE_R, BELLY_PLATE_T, BELLY_CAV_Y = -49.0, 15.2, 2.0, -44.6   # BELLY_CAV_Y: dinh con 45 do sau vach (mat moc lay, khong tran phang)
BEAK_FR, BEAK_FL_T, BEAK_H, BEAK_HOLE_R, BEAK_HOLE_L = 8.6, 1.0, 7.5, 7.0, 9.0
# 2026-11-27 Tuan: mo + bung bo lay -> VIT GIAU TU TRONG (M2.5 x 12 tu ren, lo moi O2,4 fit-library; lo thong O2,8; khe +0,2).
# Bat khi vo truoc nam ngua (truoc khi dong vo sau), tua vit O8 x 80 theo -y tu mat rap. Dau vit ngoi con 45 do (O4,6 > dau O4,5).
HID_SCREW_L = 12.0
HID_PLATE_T = 3.0                    # tam chan sau lo mo (vit xuyen qua)
BEAK_PLATE_Y0 = -55.0 + BEAK_HOLE_L  # -46 (BEAK_Y -55 khai bao sau): mat tam chan phia mo (ong mo dung cach 0,2)
# Bung: vach dac sau bung KHONG in duoc (khoang r 38 phia sau -> mat dong tam lo lo lung) -> giu lo O30,4 cat bang 1 canh (chu D),
# bung co VAU CHU D cam vao lo (chong xoay, chu STLAB dung chieu) + tru vit O7; THANH KEP ROI (belly-clamp, in phang day 3,0) hai dau
# vat theo mat con 45 do san co sau vach -> vit M2.5 x 12 xuyen thanh kep vao tru bung, keo thanh nem vao con + keo bung ep vao hoc.
BELLY_BOSS_R = 3.5
BELLY_D_FLAT = 12.8                  # canh phang lo chu D: z = BELLY_Z - 12,8 (vau bung 12,6 -> khe 0,2)
BELLY_SPIG_RI = 13.0                 # vau chu D: vanh r 13,0..15,0 (lo r 15,2 -> khe 0,2)
CLAMP_YF, CLAMP_T, CLAMP_W, CLAMP_CLR = -44.4, 3.0, 8.0, 0.28   # thanh kep: mat truoc y -44,4, day 3,0, rong 8,0; khe 0,2 phap tuyen voi con 45 do
MIC_SNAP_W = -5.6                    # canh moc cua so kep mic (w)

def hexc(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)

# ============================================================ HAM CO BAN
bpy.ops.wm.read_factory_settings(use_empty=True)
SC = bpy.context.scene

def new_obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); SC.collection.objects.link(o); return o

def place(o, M):
    o.data.transform(M)
    if M.determinant() < 0:
        o.data.flip_normals()
    return o

def cp(o, name=None):
    n = o.copy(); n.data = o.data.copy(); n.name = name or o.name + "_c"; SC.collection.objects.link(n); return n

def bop(a, b, op, keep=False):
    bpy.context.view_layer.update()
    m = a.modifiers.new('bool', 'BOOLEAN'); m.operation = op; m.object = b
    try:
        m.solver = 'MANIFOLD'
    except Exception:
        m.solver = 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(a.evaluated_get(dg))
    a.modifiers.remove(m)
    old = a.data; a.data = me; bpy.data.meshes.remove(old)
    if not keep:
        bpy.data.objects.remove(b)
    return a

def union(a, b): return bop(a, b, 'UNION')
def diff(a, b): return bop(a, b, 'DIFFERENCE')
def inter(a, b): return bop(a, b, 'INTERSECT')

def sup(name, c, rad, nt=2.0, nb=2.0, taper=0.0, rot=0.0, seg=96, rings=48):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        n = nt if z >= 0 else nb
        ln = math.hypot(x, y)
        nl = ln ** (2.0 / n) if ln > 1e-9 else 0.0
        nz = math.copysign(abs(z) ** (2.0 / n), z)
        f = (nl / ln) if ln > 1e-9 else 0.0
        s = 1.0 - taper * nz
        v.co = Vector((x * f * rad[0] * s, y * f * rad[1] * s, nz * rad[2]))
    bmesh.ops.transform(bm, matrix=Matrix.Translation(c) @ Matrix.Rotation(math.radians(rot), 4, 'Y'), verts=bm.verts)
    return new_obj(name, bm)

def cyl(name, p0, p1, r0, r1=None, seg=48):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r0,
                          radius2=r0 if r1 is None else r1, depth=d.length)
    rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) / 2) @ rot, verts=bm.verts)
    return new_obj(name, bm)

def box(name, mn, mx):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((mn[0] if v.co.x < 0 else mx[0], mn[1] if v.co.y < 0 else mx[1], mn[2] if v.co.z < 0 else mx[2]))
    return new_obj(name, bm)

def lathe(name, prof, seg=72, M=None):
    bm = bmesh.new(); rings = []
    for (r, h) in prof:
        if r < 1e-9:
            rings.append([bm.verts.new((0, 0, h))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), h)) for i in range(seg)])
    n = len(prof)
    for k in range(n):
        A, B = rings[k], rings[(k + 1) % n]
        for i in range(seg):
            j = (i + 1) % seg
            if len(A) == 1 and len(B) == 1:
                continue
            if len(A) == 1:
                bm.faces.new((A[0], B[j], B[i]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[j], B[0]))
            else:
                bm.faces.new((A[i], A[j], B[j], B[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

def arc(cr, ch, rho, a0, a1, n=8):
    return [(cr + rho * math.cos(math.radians(a0 + (a1 - a0) * i / n)), ch + rho * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def frame(P, axis):
    z = Vector(axis).normalized(); x = Vector((1, 0, 0)); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    return Matrix(((x.x, y.x, z.x, P[0]), (x.y, y.y, z.y, P[1]), (x.z, y.z, z.z, P[2]), (0, 0, 0, 1)))

def cyl_local(name, M, u0, u1, r, seg=48):
    return cyl(name, M @ Vector((0, 0, u0)), M @ Vector((0, 0, u1)), r, seg=seg)

def hexp(name, p0, p1):
    return cyl(name, p0, p1, M3_NUT_S / math.sqrt(3), seg=6)

def body_y(x, z):
    nz = (z - BZ) / BR[2]; n = NT if nz >= 0 else NB
    a = 1 - abs(nz) ** n; nl = a ** (1 / n) if a > 0 else 0
    s = 1 - TAPER * nz
    t = nl * nl - (x / (BR[0] * s)) ** 2
    return -BR[1] * s * math.sqrt(max(t, 0))

def body_normal(x, z):
    e = 0.05
    return Vector(((body_y(x + e, z) - body_y(x - e, z)) / (2 * e), -1, (body_y(x, z + e) - body_y(x, z - e)) / (2 * e))).normalized()

def cavity(grow=0.0):
    return sup('cav', (0, 0, CZ), (CRAD[0] + grow, CRAD[1] + grow, CRAD[2] + grow), NT, NB, TAPER)

# ============================================================ KHOANG TRONG
def extrude(name, poly, u0, u1, M):
    bm = bmesh.new()
    lo = [bm.verts.new((a, b, u0)) for a, b in poly]; hi = [bm.verts.new((a, b, u1)) for a, b in poly]
    n = len(poly)
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

def M_half(sgn):
    return Matrix(((1, 0, 0, 0), (0, sgn, 0, Y0), (0, 0, 1, 0), (0, 0, 0, 1)))

def diamond(r): return [(r, 0.0), (0.0, r), (-r, 0.0), (0.0, -r)]
def hr(w): return w * math.sqrt(2) / 2

def teardrop(r, h0=-0.5):
    pts = [(-r, h0), (-r, 0.0)]
    for k in range(1, 8):
        t = math.radians(180 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(0.0, r * math.sqrt(2))]
    for k in range(0, 8):
        t = math.radians(45 - 45 * k / 7); pts.append((r * math.cos(t), r * math.sin(t)))
    pts += [(r, 0.0), (r, h0)]
    return pts

def bcone(y, extra): return BELLY_RF + extra + CONE_T * (y - BELLY_FRONT)

def make_cavity():
    parts = []
    xm, f = TENT_XM, TENT_FLAT
    tent = [(-xm, -0.5), (xm, -0.5), (f, (xm - f) / TENT_SL), (-f, (xm - f) / TENT_SL)]
    for sgn in (-1, 1):
        M = M_half(sgn)
        parts.append(extrude('tent', tent, TENT_ZLO, TENT_ZHI, M))
    # Khoang ong tru bung cho loa va tam bung:
    # rb = 37.8; keo dai qua BELLY_REAR de nuot hoan toan duoi bhole2 (khong de lai goc nhon/mat phang o z=42.4)
    rb = bcone(BELLY_REAR, CONE_CLR) + 0.4
    # v3: khoang tru bung ket thuc bang CON 45 do (dinh r 15,2 tai BELLY_CAV_Y) -> tran sau vach in khong support, mat con = mat moc lay bung
    _yc0 = BELLY_CAV_Y + (rb + 0.2 - BELLY_BORE_R)
    parts.append(cyl('belly_t1', (0, Y0 + 0.5, BELLY_Z), (0, _yc0, BELLY_Z), rb + 0.2, seg=96))
    parts.append(cyl('belly_t1c', (0, _yc0 + 0.01, BELLY_Z), (0, BELLY_CAV_Y - 0.3, BELLY_Z), rb + 0.2, BELLY_BORE_R - 0.3, seg=96))
    cav = parts[0]
    for p_ in parts[1:]:
        union(cav, p_)
    return inter(cav, cavity())

def mx_cutters(M, u_rim):
    out = []
    out.append(extrude('mxpocket', diamond(hr(MX_HOLE)), u_rim, u_rim + MX_DEPTH, M))
    g0, g1, g2, gw = MX_GROOVE
    bm = bmesh.new(); pts = []
    for (u, w) in ((g0, MX_HOLE), (g1, gw), (g2, MX_HOLE)):
        r = hr(w)
        for a, b in diamond(r):
            pts.append(bm.verts.new(Vector((a, b, u_rim + u))))
    bmesh.ops.convex_hull(bm, input=pts)
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    out.append(new_obj('mxgroove', bm))
    out.append(extrude('mxwin', diamond(hr(9.0)), u_rim + MX_DEPTH - 0.1, u_rim + MX_DEPTH + 7.0, M))
    return out

# ============================================================ HAM BO SUNG (man hinh, nong dau, loa chech)
import numpy as np

def rr(hx, hz, r, n=8):
    """hinh chu nhat bo goc (nua rong hx, nua cao hz, goc r), luon 4*(n+1) diem (loft dung chung)."""
    r = max(0.3, min(r, hx - 0.05, hz - 0.05))
    pts = []
    for (cx, cz, a0) in ((hx - r, hz - r, 0), (-hx + r, hz - r, 90), (-hx + r, -hz + r, 180), (hx - r, -hz + r, 270)):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    return pts

def loft(name, rings, M=None):
    """rings = [(u, poly)], moi poly cung so diem; noi lien tiep, nap 2 dau."""
    bm = bmesh.new(); R = []
    for (u, poly) in rings:
        R.append([bm.verts.new((a, b, u)) for (a, b) in poly])
    n = len(R[0])
    bm.faces.new(R[0][::-1]); bm.faces.new(R[-1])
    for k in range(len(R) - 1):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((R[k][i], R[k][j], R[k + 1][j], R[k + 1][i]))
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

# He toa do man hinh: (a, b, u) -> (x = a, y = YF + u, z = SCR_ZC + b); u = 0 mat truoc dia, u = 4 mat phang nen
MS = Matrix(((1, 0, 0, 0), (0, 0, 1, YF), (0, 1, 0, SCR_ZC), (0, 0, 0, 1)))

def body_x(y, z):
    nz = (z - BZ) / BR[2]; n = NT if nz >= 0 else NB
    a = 1 - abs(nz) ** n; nl = a ** (1 / n) if a > 0 else 0; s = 1 - TAPER * nz
    t = nl * nl - (y / (BR[1] * s)) ** 2
    return BR[0] * s * math.sqrt(max(t, 0))

def teardrop_full(r, apex_sign=1):
    """tiet dien giot nuoc day du (chop 90 do huong +a neu apex_sign = 1, -a neu -1), toa do (a, b)."""
    pts = [(0.0, r * math.sqrt(2))]
    for k in range(0, 25):
        t = math.radians(135 + 270 * k / 24); pts.append((r * math.cos(t), r * math.sin(t)))
    return pts

# ---------- loa H0: he toa do cuc bo cua vanh loa (local z = |x|; tam loa tai local z = z_spk_center)
SPK_ZC_LOCAL = z_spk_center
def spk_frame(sgn):
    a = Vector((sgn, 0.0, 0.0)); c = Vector((sgn * SPK_CX, SPK_CY, SPK_Z))
    M = Matrix(((0, 0, sgn, c.x), (1, 0, 0, c.y), (0, sgn, 0, c.z), (0, 0, 0, 1))) @ Matrix.Translation((0, 0, -SPK_ZC_LOCAL))
    return M, a, c

SPK_Z_END = 34.0            # day chup tru (local z)
SPK_TUBE_R = 33.9
SPK_BARB_Z = 37.0           # vi tri goc bam (local z)
SPK_BARB_H = 0.8
MIC_WEB_R, MIC_WEB_W0, MIC_WEB_W1 = 9.0, 1.0, 2.5   # tam chan nua duoi truoc PCB (w 1,0..2,5) noi ong dan am
MIC_BORE3_END = 6.5

def mpt(w, v=0.0):
    return Vector(MIC_C) + MIC_N * w + MIC_T * v

# ============================================================ THAN NGOAI
OUTER = sup('outer', (0, 0, BZ), BR, NT, NB, TAPER)
for s in (-1, 1):
    union(OUTER, sup('ear', (s * 42, 0, 148), (17, 13, 26), 2, 2, 0.32, rot=s * 20, seg=48, rings=24))
    # canh trang tri: doi len z ~112, ra sau, nho lai (khong de len vanh loa)
    union(OUTER, sup('wing', (s * 55, 14, 110), (6, 12, 16), 2, 2, -0.3, rot=s * 5, seg=48, rings=24))

PLATE = sup('plate', (0, 0, BZ), BR, NT, NB, TAPER)
inter(PLATE, box('slab', (-200, -200, 0), (200, 200, FLOOR_CUT)))
diff(OUTER, box('flat', (-200, -200, -50), (200, 200, FLOOR_CUT)))
OUTER_HEAD = cp(OUTER, 'outer_head')            # than dau truoc khi them hop man (de bao ve vach vo)

# --- hop man: san phang thang dung YS_OUT (u = 4), thanh 2,4, ben ngoai thang roi thu nho 45 do ve than (khong mai treo)
PAD_R = 18.2
pad_rings = []
for _ph in (0, 4, 8, 13, 18, 24, 30, 37, 44, 52, 60, 68, 76, 84, 90):
    _ins = PAD_A * (1.0 - math.sin(math.radians(_ph)))
    _u = 4.0 + PAD_B * (1.0 - math.cos(math.radians(_ph)))
    pad_rings.append((_u, rr(PAD_W - _ins, PAD_H - _ins, PAD_R - _ins)))
_UPF = 4.0 + PAD_B
pad_rings.append((_UPF + 6.0, rr(PAD_W, PAD_H, PAD_R)))
for X in (6, 12, 18, 24, 30, 36):
    pad_rings.append((_UPF + 6.0 + X, rr(PAD_W - X, PAD_H - X, PAD_R - X)))
PADOUT = loft('padout', pad_rings, MS)
FLATCUT = loft('flatcut', [(-14.0, rr(PAD_W - PAD_A, PAD_H - PAD_A, PAD_R - PAD_A)), (4.0, rr(PAD_W - PAD_A, PAD_H - PAD_A, PAD_R - PAD_A))], MS)
diff(OUTER, FLATCUT)
union(OUTER, PADOUT)

SPK_F = {}
for sgn in (-1, 1):
    SPK_F[sgn] = spk_frame(sgn)

def outer(): return cp(OUTER, 'o')
def clip(o): return inter(o, outer())

S = outer(); diff(S, make_cavity())

# --- khoang bay 2 ben cho khay ampli (tent rong 45 do, z 6..22, gioi han boi vo trong)
def make_bays():
    xm = 80.0
    tent = [(-xm, -0.5), (xm, -0.5), (1.0, (xm - 1.0) / TENT_SL), (-1.0, (xm - 1.0) / TENT_SL)]
    parts = [extrude('bay', tent, 6.0, 22.0, M_half(sg)) for sg in (-1, 1)]
    b = parts[0]; union(b, parts[1])
    return inter(b, sup('inner2', (0, 0, BZ), (BR[0] - WALL, BR[1] - WALL, BR[2] - WALL), NT, NB, TAPER))

# --- lo man hinh: lo nen + yen vat 45 do + hoc vanh chan (u theo he man hinh); phan phia sau thu nho 45 do (phuong an khong support)
_hx, _hz = DISC[0] + 0.3, DISC[1] + 0.3
# v3: lo thang (face-plate + man day tu NGOAI vao), hoc chim 1,0 cho vanh FP_LIP, 6 cua so lay sau u = FP_WIN_U, pheu 45 do sau u = 20
HOLE = loft('hole', [(-1.0, rr(_hx, _hz, DISC[2] + 0.3)), (HOLE_END3, rr(_hx, _hz, DISC[2] + 0.3))], MS)
fun_rings = [(HOLE_END3, rr(_hx, _hz, DISC[2] + 0.3))]
for X in (6, 12, 18, 24, 28):
    fun_rings.append((HOLE_END3 + X, rr(_hx - X, _hz - X, DISC[2] + 0.3 - X)))
FUNNEL = loft('funnel', fun_rings, MS)
SKIN = cp(OUTER_HEAD, 'skin'); diff(SKIN, cavity())
diff(FUNNEL, SKIN)
diff(S, HOLE); diff(S, FUNNEL)
_lw = DISC[0] + FP_LIP + 0.2, DISC[1] + FP_LIP + 0.2
diff(S, loft('lip_rec', [(2.0, rr(_lw[0], _lw[1], DISC[2] + FP_LIP + 0.2)), (5.0, rr(_lw[0], _lw[1], DISC[2] + FP_LIP + 0.2))], MS))
FP_FINGERS = [('z', 25.0, 1), ('z', -25.0, 1), ('z', 25.0, -1), ('z', -25.0, -1), ('x', 0.0, 1), ('x', 0.0, -1)]   # (mat, toa do doc canh, dau)
def fp_window(kind, c, sg):
    # o cua so: cau rong 5,6 (<= 6, in bac cau), sau 1,2 vao vach lo; canh moc o u = FP_WIN_U (tran cua so khi in)
    if kind == 'z':
        b0, b1 = sorted((sg * (_hz - 0.1), sg * (_hz + 1.2)))
        return box('fpw', MS @ Vector((c - 2.8, b0, FP_WIN_U)), MS @ Vector((c + 2.8, b1, FP_WIN_U + 2.2)))
    a0, a1 = sorted((sg * (_hx - 0.1), sg * (_hx + 1.2)))
    return box('fpw', MS @ Vector((a0, -2.8, FP_WIN_U)), MS @ Vector((a1, 2.8, FP_WIN_U + 2.2)))
for (k_, c_, sg_) in FP_FINGERS:
    w_ = fp_window(k_, c_, sg_)
    bm_ = bmesh.new(); bm_.from_mesh(w_.data); bmesh.ops.recalc_face_normals(bm_, faces=bm_.faces); bm_.to_mesh(w_.data); bm_.free()
    diff(S, w_)

# ---------------- chi tiet noi bo ----------------
BEAK_Z = 61.0                     # v3: ha 2,4 de vanh mo (O17,2) + hoc chim nam duoi lo man (z 70,7) va duoi vanh FP (z 69,3)
BEAK_Y = -55.0                    # mat ngoi vanh mo (hoc chim ~1,1-1,6 vao mat vo cong)
BEAK_P = Vector((0, BEAK_Y, BEAK_Z))
BEAK_M = frame(BEAK_P, Vector((0, -1, 0)))
t = cyl('bcol', (0, Y0, SEAT_Z), (0, Y0, 175), 31.6, seg=90); clip(t); union(S, t)

# Bo ESP32-S3 NAM NGANG (giu nguyen ban S3 hien tai)
PZ0, PZ1 = PCB_CENTER[2] - PCB_BOX[2] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2      # 26..42
hx = PCB_BOX[0] / 2 + FIT   # 14.8
Y_ROOF = PCB_Y_USB + USB_GAP_ROOF
Y_FRONT = PCB_Y_USB - PCB_BOX[1]
CABLE_WALL_T = 56.4 - Y_ROOF
LEDGE_T = 1.8
# v3: ray bo S3 khong con lien vo -> khay chung s3-tray (make_s3_tray), so ray/goi do giu nguyen
_zh = (PZ1 - PZ0) / 2 + 0.2
_zc = PCB_CENTER[2]
pk = extrude('pcb_pocket', [(_zc - _zh, 30.0), (_zc + _zh, 30.0), (_zc + _zh, Y_ROOF), (_zc, Y_ROOF + _zh), (_zc - _zh, Y_ROOF)],
             -hx, hx, Matrix(((0, 0, 1, 0), (0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1))))
diff(S, pk)
def rrect(w, h, r, n=6):
    pts = []
    for (cx, cz, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            t_ = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(t_), cz + r * math.sin(t_)))
    return pts
M_cab = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))) @ Matrix.Translation((0, 0, 0))
cab = extrude('cable', rrect(CABLE_W, CABLE_H, CABLE_R), Y_ROOF - 0.5, 90.0, M_cab)
cab.data.transform(Matrix.Translation((PCB_CENTER[0], 0, PCB_CENTER[2]))); diff(S, cab)

# 4 tru vit o de
for (sx, sy) in BOSSES:
    if True:
        b_ = cyl('boss', (sx, sy, 5.0), (sx, sy, BOSS_TOP), 7.0, seg=48)
        y_a, y_b = sorted((sy, Y0))
        union(b_, box('bossw', (sx - 7.0, y_a, 5.0), (sx + 7.0, y_b, BOSS_TOP)))
        union(S, b_)

# ============================================================ CAT LO
for sgn in (-1, 1):
    diff(S, extrude('bhole', teardrop(BUTTON_HOLE_D / 2), SEAT_Z - 0.3, 180.0, M_half(sgn)))
TALK_R = TALK_FLANGE_R + 0.4
CAP_RIM_Z = TALK_ZB + REST_UP                       # vanh nap (mat duoi) luc nghi
z_cone_end = SEAT_Z - (TALK_R - BUTTON_HOLE_D / 2)
TALK_RIM = CAP_RIM_Z + CAP_TUBE_END - TUBE_GAP - MX_HOUSING_H     # mieng o switch = DAY HOC (mau cat-paw: mieng o nam o day hoc)
# Goc PCB mic (O15, nghieng 45 do) nho vao hoc nut tai r = 24,8, z = 139,17 (khong doi mic): khi nap an xuong, goc PCB tuong doi di LEN
# trong khung nap -> mat duoi nap (r > hoc) khoet con 45 do: z = (z + r cua goc) + hanh trinh 4,0 + du 0,5 - r (khong chung that voi PCB mic)
_pc = (Vector(MIC_C_REF) + MIC_N * (MIC_PCB_T / 2) + MIC_T * (MIC_PCB_D / 2))
CAP_DISH_K = _pc.z + abs(_pc.y - Y0) + 4.0 + 0.5
# day hoc = phang o muc mieng o (nhu mau cat-paw: mieng o nam o day hoc). Thanh tru O54,8 chi cao <= 5,0 mm (z_cone_end -> z_w) vi mai vom nam
# ngua > 5 mm bi slicer bao CAN SUPPORT (printability bridge_max 5,0). Vanh nap (mep con) cach day: TRAVEL_SHELL (nap cham day truoc khi het 4,0 cua switch)
TALK_ZPOCKET = TALK_RIM - 0.5
TSEAT_PROF = [(0, SEAT_Z), (BUTTON_HOLE_D / 2, SEAT_Z), (TALK_R, z_cone_end), (TALK_R, TALK_ZPOCKET), (TALK_R - 0.5, TALK_RIM), (0, TALK_RIM)]
TRAVEL_SHELL = CAP_DISH_K - TALK_FLANGE_R - TALK_ZPOCKET
diff(S, lathe('tseat', TSEAT_PROF, seg=96, M=Matrix.Translation((0, Y0, 0))))
MT = Matrix(((1, 0, 0, 0), (0, 1, 0, Y0), (0, 0, -1, TALK_RIM), (0, 0, 0, 1)))
for o_ in mx_cutters(MT, 0.0):
    diff(S, o_)

# Mic INMP441 nghieng 45 do: lo ong lot (thong xuong khoang than), hoc PCB/mam O19,6, lo ong dan am O7,7, 3 lo O2
diff(S, cyl('micb1', mpt(-17.0), mpt(-0.5), MIC_SLEEVE_BORE_R, seg=64))
diff(S, cyl('micb2', mpt(-1.0), mpt(MIC_POCKET_W1), 8.2, seg=64))     # hoc PCB O16,4, vach truoc w = 1,0 (khe 0,2 voi mat PCB: 'ong' dan am = lo O4 trong vach vo)
diff(S, cyl('micb3', mpt(0.9), mpt(MIC_BORE3_END), MIC_TUBE_ID / 2, seg=48))
for dx in MIC_HOLE_X:
    diff(S, cyl('mich', mpt(MIC_BORE3_END - 0.3) + Vector((dx, 0, 0)), mpt(MIC_L + 5.0) + Vector((dx, 0, 0)), MIC_HOLE_D / 2, seg=24))

# Mo (beak) thu nho
# v3: hoc chim vanh mo + lo O14 dai 9 + con 45 do (mat moc lay, khong treo) + hoc sau O15,6
diff(S, cyl_local('beakrec', BEAK_M, 0.0, 14.0, BEAK_FR + 0.2, seg=64))
diff(S, cyl_local('beakhole', BEAK_M, -BEAK_HOLE_L, 0.5, BEAK_HOLE_R, seg=64))
# v3 vit giau: lo O14 dai 9 -> tam chan 3,0 (lo thong O2,8) -> hoc O15,6 lam duong tua vit, day con 45 do toi O4,6 (khong tran phang)
_bt0 = -BEAK_HOLE_L - HID_PLATE_T                    # mat dau vit (local z)
_bc = BEAK_HOLE_R + 0.8 - 2.3                        # chieu cao con 45 do r 7,8 -> 2,3
diff(S, cyl_local('beakpocket', BEAK_M, -26.0, _bt0 - _bc, BEAK_HOLE_R + 0.8, seg=64))
diff(S, cyl('beakpcone', BEAK_M @ Vector((0, 0, _bt0 - _bc - 0.01)), BEAK_M @ Vector((0, 0, _bt0 + 0.01)), BEAK_HOLE_R + 0.8, 2.3, seg=64))
diff(S, cyl_local('beakthru', BEAK_M, _bt0 - 0.5, -BEAK_HOLE_L + 0.5, THRU_D / 2, seg=24))

# Lo non tam bung (nho ngoai, rong vao trong -> yen non, lap tu trong)
# v3: hoc chim vanh bung r 18,2 toi mat ngoi BELLY_SEAT + lo O30,4 xuyen vach toi khoang (mat sau vach y -44 = mat moc 4 lay)
diff(S, cyl('belly_rec', (0, BELLY_FRONT - 14.0, BELLY_Z), (0, BELLY_SEAT, BELLY_Z), BELLY_RF + 0.2, seg=96))
# 2026-11-27 vit giau: lo O30,4 cat 1 canh phang (chu D, chong xoay bung); lo doc theo y = vach dung khi in (khong treo)
_yw = BELLY_CAV_Y                                    # -44,6: het vach (sau do la con 45 do cua khoang)
_bb = cyl('belly_bore', (0, BELLY_SEAT - 1.0, BELLY_Z), (0, _yw, BELLY_Z), BELLY_BORE_R, seg=96)
inter(_bb, box('belly_bd', (-30, -80, BELLY_Z - BELLY_D_FLAT), (30, 0, BELLY_Z + 30)))
diff(S, _bb)
diff(S, cyl('belly_bore2', (0, _yw - 0.01, BELLY_Z), (0, BELLY_CAV_Y + 4.0, BELLY_Z), BELLY_BORE_R, seg=96))
# manh chu D chi trong vach, mat duoi vat 45 do theo con khoang keo dai (r = 14,9 + (y + 44,9)) -> khong treo; canh phang an y -49..-47
diff(S, cyl('belly_dcone', (0, BELLY_SEAT, BELLY_Z), (0, _yw + 0.01, BELLY_Z), BELLY_BORE_R - 0.3 + (BELLY_SEAT - (BELLY_CAV_Y - 0.3)), BELLY_BORE_R + 0.01, seg=96))

# Loa ngang (nhu ban A1S): yen non 25 do lap tu trong + duong ham giot nuoc (chop huong len khi in, moi nua vo mot chop)
def zcone(h, extra): return BZL_RF + extra + BZL_T * (SPK_XF - h)
for s in (-1, 1):
    diff(S, cyl('szhole', (s * (SPK_XF + 1.5), Y0, SPK_Z), (s * BZL_REAR, Y0, SPK_Z), zcone(SPK_XF + 1.5, CONE_CLR), zcone(BZL_REAR, CONE_CLR), seg=96))
    for sg_ in (-1, 1):
        Mx_ = Matrix(((0, 0, s, 0), (0, sg_, 0, Y0), (1, 0, 0, SPK_Z), (0, 0, 0, 1)))   # local (a, h, u) -> (s*u, Y0 + sg*h, SPK_Z + a)
        diff(S, extrude('stun', teardrop(BODY_D_MAX / 2 + 0.8), 36.0, 55.0, Mx_))

# 5 khe thoat nhiet o lung
for i in range(5):
    x = (i - 2) * 7.0
    diff(S, box('vent', (x - VENT_W / 2, 30, 82 - VENT_L / 2), (x + VENT_W / 2, 70, 82 + VENT_L / 2)))

# Hoc dai oc vit de
for (sx, sy) in BOSSES:
    if True:
        diff(S, hexp('nut', (sx, sy, BOSS_TOP - NUT_DEPTH), (sx, sy, BOSS_TOP + 0.1)))
        diff(S, cyl('mclear', (sx, sy, 3.0), (sx, sy, BOSS_TOP - NUT_DEPTH + 0.1), M3_CLEAR_D / 2, seg=24))

SCREW_INFO = []

# v3: bo 6 lo chot O2 (chot chua tung ve) -> 6 vit M2.5 x 12 tu ren: tru + lo moi O2,4 o vo truoc, gieng O5,6 + lo thong O2,8 o vo sau
def poly_offset(pts, d):
    # da giac loi CCW -> doi ra ngoai d (giao cac canh da dich)
    n = len(pts); L = []
    for i in range(n):
        (x0, y0_), (x1, y1_) = pts[i], pts[(i + 1) % n]
        ex, ey = x1 - x0, y1_ - y0_; ln = math.hypot(ex, ey); nx, ny = ey / ln, -ex / ln
        L.append(((x0 + nx * d, y0_ + ny * d), (ex, ey)))
    out = []
    for i in range(n):
        (p, u), (q, v) = L[i - 1], L[i]
        den = u[0] * v[1] - u[1] * v[0]
        t_ = ((q[0] - p[0]) * v[1] - (q[1] - p[1]) * v[0]) / den
        out.append((p[0] + u[0] * t_, p[1] + u[1] * t_))
    return out
def ccw(pts):
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if a > 0 else pts[::-1]
M_XZY = lambda sgn: Matrix(((sgn, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # (p, q, t) -> (x = sgn p, y = t, z = q)
def fin_poly(d=0.0):
    pts = ccw([(c, SPK_Z + r) for (c, r) in BZ_FIN])
    return poly_offset(pts, d) if d else pts
def ear_cuts(target, pts_xz, screws_xz, ext_x=None):
    # lo moi M2.5 x 6 tren vo truoc + hoc dau vit con 45 do tren vo sau (nhieu vit: bao loi cac con -> mai sống, khong yen ngua treo)
    hb = bmesh.new(); vs = []
    for (sx_, sz_) in screws_xz:
        diff(target, cyl('epil', (sx_, EAR_Y0 + 0.5, sz_), (sx_, EAR_Y0 - SCREW6_PILOT, sz_), PILOT_D / 2, seg=20))
    # ext_x: keo hoc dau vit vao trong khoang leu (vit sat mep leu -> khong de manh mong kep giua vach leu 45 do va con)
    for (sx_, sz_) in screws_xz + ([(ext_x, z_) for (_x, z_) in screws_xz] if ext_x is not None else []):
        for k in range(24):
            a_ = 2 * math.pi * k / 24
            vs.append(hb.verts.new((sx_ + HEAD_D / 2 * math.cos(a_), Y0 - 0.01, sz_ + HEAD_D / 2 * math.sin(a_))))
            vs.append(hb.verts.new((sx_ + 0.2 * math.cos(a_), Y0 + HEAD_T, sz_ + 0.2 * math.sin(a_))))
    if os.environ.get('V3_NOHEAD'):
        hb.free(); return
    bmesh.ops.convex_hull(hb, input=vs)
    bmesh.ops.delete(hb, geom=[v for v in hb.verts if not v.link_faces], context='VERTS')
    bmesh.ops.recalc_face_normals(hb, faces=hb.faces)
    diff(target, new_obj('ehead', hb))
V3_SKIP = os.environ.get('V3_SKIP', '').split(',')   # chi de chia doi tim loi in (khong dung khi xuat that)
SCREWS6 = []      # (ten, part, x, z) - vit M2.5 x 6 trong long, kiem tua vit
FIN_C0 = 49.0   # day vay: phang (day 3,0) tu dau trong toi c 50 (tran hoc cau <= 5 neo vach), sau do doc 45 do ra mep (vay day dan) -> khong treo
def fin_vcut(sgn, dy=0.0):
    pts = [(44.0, EAR_Y0 - 20.0), (44.0, EAR_Y0), (FIN_C0, EAR_Y0), (56.0, EAR_Y0 - (56.0 - FIN_C0)), (56.0, EAR_Y0 - 20.0)]
    pts = [(sgn * c, y + dy) for (c, y) in pts]
    return extrude('fin_v', pts, 70.0, 110.0, Matrix.Identity(4))
for sgn in (-1, 1):
    side = 'L' if sgn < 0 else 'R'
    _fp = extrude('fin_pocket', fin_poly(EAR_CLR), EAR_Y0 - 9.0, Y0 + 0.01, M_XZY(sgn))
    _a, _b = sorted((sgn * 40.0, sgn * 46.5))   # keo hoc vao trong leu (bo manh kep giua vach leu va vach hoc)
    union(_fp, box('fin_ext', (_a, EAR_Y0 - EAR_CLR, SPK_Z + 33.0), (_b, Y0 + 0.01, SPK_Z + 54.0)))
    diff(_fp, fin_vcut(sgn, -EAR_CLR))
    diff(S, _fp)
    scr = [(sgn * c, SPK_Z + r) for (c, r) in BZ_FIN_SCREWS]
    ear_cuts(S, None, scr, ext_x=sgn * 40.0)
    SCREWS6 += [('bezel-%s-%d' % (side, i), 'speaker-bezel-' + side, x_, z_) for i, (x_, z_) in enumerate(scr)]
# khay chung: phong bi + hoc tai vit trong khoi tru bu-long de
TRAY_Y0, TRAY_Y1 = Y_FRONT - 2.7, TRAY_Y1_V3
TRAY_HXO = hx + 2.4
AMP_PCB_X = TRAY_HXO + AMP_BACK_GAP
AMP_HOLD_X1 = AMP_PCB_X + 1.6 + 0.2 + 1.2
AMP_TOP = AMP_ZB + AMP_PCB_L - 2.0
# khay nam gon trong long leu 45 do (khong cat hop vuong -> dau hop la tran phang khi in); chi xen 1 dai 0,6 trong 2 khoi tru bu-long de
for sg in (-1, 1):
    a, b = sorted((sg * (TRAY_HXO - 0.6), sg * (TRAY_HXO + 0.3)))
    diff(S, box('tray_strip', (a, -abs(BOSSES[0][1]) - 7.5, TRAY_Z0 - 0.3), (b, abs(BOSSES[0][1]) + 7.5, BOSS_TOP + 0.3)))
for sgn in (-1, 1):
    a, b = sorted((sgn * TRAY_HXO, sgn * (AMP_HOLD_X1 + 0.3)))
    if 'tray' not in V3_SKIP: diff(S, box('amp_env', (a, AMP_YC - 11.55, 16.0), (b, AMP_YC + 11.55, AMP_TOP + 0.3)))
    a, b = sorted((sgn * TRAY_HXO, sgn * (TRAY_TAB_X1 + EAR_CLR)))
    diff(S, box('tray_tabp', (a, EAR_Y0 - EAR_CLR, TRAY_Z0 - EAR_CLR), (b, Y0 + 0.01, TRAY_Z0 + TRAY_TAB_H + EAR_CLR)))
    scr = [(sgn * TRAY_SCREW_X, TRAY_Z0 + TRAY_TAB_H / 2)]
    ear_cuts(S, None, scr)
    SCREWS6 += [('tray-%s' % ('L' if sgn < 0 else 'R'), 's3-tray', scr[0][0], scr[0][1])]
# de nut: phong bi khoi o switch (mo ve +y o vo truoc, ve -y o vo sau) + 2 tai
BB_ZB = TALK_RIM - MX_DEPTH - 3.0
if 'bb' not in V3_SKIP: diff(S, box('bb_env', (-BB_HALF - EAR_CLR, Y0 - BB_HALF - EAR_CLR, BB_ZB - EAR_CLR), (BB_HALF + EAR_CLR, Y0 + BB_HALF + EAR_CLR, TALK_RIM + 0.02)))
_z0, _z1 = BB_ZB - EAR_CLR, TALK_RIM + 0.02; _zm = (_z0 + _z1) / 2; _h = (_z1 - _z0) / 2
for sg in (-1, 1):   # mai 45 do o 2 dau phong bi (dau phong bi la tran khi in 2 nua vo mat rap xuong)
    _ye = Y0 + sg * (BB_HALF + EAR_CLR)
    if 'bb' not in V3_SKIP: diff(S, extrude('bb_gable', [(_ye - sg * 0.01, _z0), (_ye - sg * 0.01, _z1), (_ye + sg * _h, _zm)], -BB_HALF - EAR_CLR, BB_HALF + EAR_CLR,
                    Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))))
for sgn in (-1, 1):
    a, b = sorted((sgn * BB_HALF, sgn * (BB_WING_X1 + EAR_CLR)))
    diff(S, box('bb_wingp', (a, EAR_Y0 - EAR_CLR, BB_ZB - EAR_CLR), (b, Y0 + 0.01, BB_ZB + BB_WING_H + EAR_CLR)))
    scr = [(sgn * BB_SCREW_X, BB_ZB + BB_WING_H / 2)]
    ear_cuts(S, None, scr)
    SCREWS6 += [('button-%s' % ('L' if sgn < 0 else 'R'), 'button-base', scr[0][0], scr[0][1])]
# kep mic: 2 cua so lay o 2 vach ben ong lot (vung dau dac z > 124)
M_MICF = frame(MIC_C, MIC_N)
for sgn in (-1, 1):
    a, b = sorted((sgn * 10.6, sgn * 12.0))
    w_ = box('micwin', (a, -2.5, MIC_SNAP_W), (b, 2.0, MIC_SNAP_W + 2.2)); w_.data.transform(M_MICF); diff(S, w_)
# 6 vit noi 2 nua
for (sx_, sz_) in ([] if 'screws' in V3_SKIP else SHELL_SCREWS):
    b_ = cyl('sboss', (sx_, Y0 - 14.0, sz_), (sx_, Y0 + 70.0, sz_), SHELL_BOSS_R, seg=40)
    if sz_ < 30.0:
        union(b_, box('sweb', (sx_ - 3.0, Y0 - 14.0, FLOOR_CUT), (sx_ + 3.0, Y0 + 70.0, sz_)))
    clip(b_); union(S, b_)
    diff(S, cyl('spilot', (sx_, Y0 + 0.5, sz_), (sx_, Y0 - (SCREW_L - WELL_FLOOR) - 1.0, sz_), PILOT_D / 2, seg=20))
    diff(S, cyl('sthru', (sx_, Y0 - 0.5, sz_), (sx_, Y0 + WELL_FLOOR + 0.01, sz_), THRU_D / 2, seg=20))
    diff(S, cyl('swell', (sx_, Y0 + WELL_FLOOR, sz_), (sx_, Y0 + 90.0, sz_), WELL_D / 2, seg=32))

# Bo nhung manh vun roi (< 20 mm3) con sot giua day hoc nut / lo mic (khong bam vao vo)
def drop_islands(o, min_vol=20.0):
    bm = bmesh.new(); bm.from_mesh(o.data)
    seen = set(); comps = []
    for v in bm.verts:
        if v.index in seen:
            continue
        stack = [v]; seen.add(v.index); comp = []
        while stack:
            x = stack.pop(); comp.append(x)
            for e in x.link_edges:
                w = e.other_vert(x)
                if w.index not in seen:
                    seen.add(w.index); stack.append(w)
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    n = 0
    for comp in comps[1:]:
        if len(comp) < 400:
            bmesh.ops.delete(bm, geom=comp, context='VERTS'); n += 1
    bm.to_mesh(o.data); bm.free()
    print("DROP_ISLANDS", n)
drop_islands(S)

# ============================================================ TACH 2 NUA
SRC = cp(S, 'src')
A = S; B = cp(S, 'back')
inter(A, box('fr', (-300, -300, -50), (300, Y0, 300)))
inter(B, box('bk', (-300, Y0, -50), (300, 300, 300)))

# ============================================================ GO ROI AM DUONG (Tuan 2026-11-27: "vo truoc va sau nen co dang go am duong,
# dung lam tron han se kho lap rap"). Ca 2 nua in up mat rap xuong ban, mat rap co ~4900 mm2 vach trong + gieng vit -> go LIEN se
# nhac vach trong khoi ban (phai support) -> Tuan chon GO ROI: ranh am o mep trong thanh vo CA 2 nua, vong go duong in phang rieng
# (seam-spline) ep vao ranh vo truoc roi up vo sau len. Go = dai thanh vo [r_i, r_i + SPL_T] cat theo SRC (chi o cho co thanh).
SPL_T, SPL_H, SPL_CLR = 1.0, 4.0, 0.2      # go day 1,0 (> 2 duong in 0,9), cao 4,0 = 2,0 vao moi nua; khe 0,2 (maker/CLAUDE.md)
GRV_IN = 0.3                                 # ranh lan vao long 0,3: cat sach chan vach trong o mep trong, khong gay go
GRV_D = SPL_H / 2 + SPL_CLR                  # sau ranh moi nua 2,2 -> thanh ngoai con WALL - SPL_T - SPL_CLR = 1,2
def wall_band(name, d0, d1, y0, y1):
    """dai lop vo tu mat trong + d0 toi mat trong + d1 (cung ho sieu ellip voi OUTER/inner2), cat theo y0..y1"""
    o_ = sup(name + '_o', (0, 0, BZ), tuple(r - WALL + d1 for r in BR), NT, NB, TAPER)
    diff(o_, sup(name + '_i', (0, 0, BZ), tuple(r - WALL + d0 for r in BR), NT, NB, TAPER))
    inter(o_, box(name + '_y', (-300, y0, FLOOR_CUT), (300, y1, 300)))
    return o_
SPLINE = wall_band('spline', 0.0, SPL_T, Y0 - SPL_H / 2, Y0 + SPL_H / 2)
inter(SPLINE, cp(SRC, 'src_spl'))
diff(A, wall_band('grvA', -GRV_IN, SPL_T + SPL_CLR, Y0 - GRV_D, Y0 + 1.0))
diff(B, wall_band('grvB', -GRV_IN, SPL_T + SPL_CLR, Y0 - 1.0, Y0 + GRV_D))
_bm = bmesh.new(); _bm.from_mesh(SPLINE.data)
_isl = []; _seen = set(); _drop = []
for _v in _bm.verts:
    if _v.index in _seen: continue
    _st = [_v]; _seen.add(_v.index); _vs = []
    while _st:
        _x = _st.pop(); _vs.append(_x)
        for _e in _x.link_edges:
            _w = _e.other_vert(_x)
            if _w.index not in _seen: _seen.add(_w.index); _st.append(_w)
    _z = [q.co.z for q in _vs]
    if max(_z) - min(_z) < 20.0:     # mau ngan o chan (z 4..10, dai ~12): mong 1,0 de gay, khong giup dinh vi -> bo
        _drop += _vs
    else:
        _isl.append((round(min(_z), 1), round(max(_z), 1)))
bmesh.ops.delete(_bm, geom=_drop, context='VERTS'); _bm.to_mesh(SPLINE.data); _bm.free()
print("SPLINE giu", len(_isl), "cung (z tu, z toi):", _isl, "| bo", len(_drop), "dinh mau ngan")

# v3: BE thay tam de (Tuan: "de nen co de bang phang va Cu dung duoc"): sieu ellip lech truoc nho ra ngoai chan vo,
# day phang + 4 hoc chan cao su, mep tren vat 45 do 2,5 (in mat tren xuong ban), 4 bu-long M3 x 16 tu duoi vao dai oc trong vo
def base_ring(d):
    pts = []
    for i in range(96):
        t_ = 2 * math.pi * i / 96; c_, s_ = math.cos(t_), math.sin(t_)
        ex = 2.0 / BASE_N
        x_ = (BASE_HX - d) * math.copysign(abs(c_) ** ex, c_)
        y_ = ((BASE_YB - d) if s_ > 0 else -(BASE_YF - d)) * abs(s_) ** ex
        pts.append((x_, y_))
    return pts
bpy.data.objects.remove(PLATE)
PLATE = loft('base', [(BASE_BOT, base_ring(BASE_BCH)), (BASE_BOT + BASE_BCH, base_ring(0.0)), (BASE_TOP - BASE_CH, base_ring(0.0)), (BASE_TOP, base_ring(BASE_CH))])
for (sx, sy) in BOSSES:
    diff(PLATE, cyl('plh', (sx, sy, BASE_BOT - 1), (sx, sy, BASE_TOP + 1), M3_CLEAR_D / 2, seg=24))
    diff(PLATE, cyl('plc', (sx, sy, BASE_BOT - 1), (sx, sy, BASE_BOT + 2.8), 4.5, seg=40))
for sgn in (-1, 1):   # vit day vanh loa M2.5 x 12 tu duoi
    diff(PLATE, cyl('bzb_h', (sgn * BZ_BOT_X, Y0, BASE_BOT - 1), (sgn * BZ_BOT_X, Y0, BASE_TOP + 1), THRU_D / 2, seg=20))
    diff(PLATE, cyl('bzb_cb', (sgn * BZ_BOT_X, Y0, BASE_BOT - 1), (sgn * BZ_BOT_X, Y0, BASE_BOT + BZ_BOT_CB_H), BZ_BOT_CB_D / 2, seg=32))
for (fx, fy) in FEET:
    diff(PLATE, cyl('foot', (fx, fy, BASE_BOT - 1), (fx, fy, BASE_BOT + FOOT_T), FOOT_D / 2, seg=40))

# ============================================================ BO PHAN RIENG
# --- Tam bung (belly): dia kem TRON (khong lo loa), 12 vach long vu khac nong 0,4 + chu STLAB khac sau 0,6
rf = BELLY_RF; yf = BELLY_FRONT; rho = 3.0; t1 = rho * math.tan(math.radians(30))
r_rear = rf + CONE_T * (BELLY_REAR - yf)
ti = 2.4 / math.cos(math.radians(30))
# v3: bung lap tu NGOAI: dia r 18 (mep R2) + vay r 16..18 ngoi hoc chim toi BELLY_SEAT; 4 lay r 13,8..15 dai 14,5 tu mat trong dia,
# moc 0,8 qua mat sau vach (y -44, khe 0,2)
def rsector(name, prof, a0, a1, n=12):
    bm = bmesh.new(); R_ = []
    for i in range(n + 1):
        t_ = math.radians(a0 + (a1 - a0) * i / n); c_, s_ = math.cos(t_), math.sin(t_)
        R_.append([bm.verts.new((r * c_, r * s_, h)) for (r, h) in prof])
    m = len(prof)
    for i in range(n):
        for k in range(m):
            bm.faces.new((R_[i][k], R_[i][(k + 1) % m], R_[i + 1][(k + 1) % m], R_[i + 1][k]))
    bm.faces.new(R_[0][::-1]); bm.faces.new(R_[n])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)
_rh = 2.0
prof_belly = [(0.0, yf), (rf - _rh, yf)] + arc(rf - _rh, yf + _rh, _rh, -90, 0, 6)[1:]
prof_belly += [(rf, BELLY_SEAT), (rf - 2.0, BELLY_SEAT), (rf - 2.0, yf + BELLY_PLATE_T), (0.0, yf + BELLY_PLATE_T)]
M_BELLY = Matrix.Translation((0, 0, BELLY_Z)) @ Matrix.Rotation(-math.pi / 2, 4, 'X')
BELLY = lathe('belly', prof_belly, seg=96)
# 2026-11-27 vit giau: tru O7 toi y -45,1 (lo moi O2,4 tu -54,0) + vau chu D r 13..15 toi y -45,3 (cuc bo: z = y the gioi,
# y cuc bo = -(z the gioi - BELLY_Z) -> canh phang z the gioi BELLY_Z - 12,6 = y cuc bo +12,6)
_ye = CLAMP_YF - 0.7
union(BELLY, cyl('bl_boss', (0, 0, yf + BELLY_PLATE_T - 0.1), (0, 0, _ye), BELLY_BOSS_R, seg=40))
diff(BELLY, cyl('bl_pilot', (0, 0, -54.0), (0, 0, _ye + 0.5), PILOT_D / 2, seg=20))
_sp = cyl('bl_spig', (0, 0, yf + BELLY_PLATE_T - 0.1), (0, 0, _ye - 0.2), BELLY_BORE_R - 0.2, seg=96)
diff(_sp, cyl('bl_spig_i', (0, 0, yf), (0, 0, _ye + 1.0), BELLY_SPIG_RI, seg=96))
inter(_sp, box('bl_spig_d', (-30, -30, yf - 1), (30, BELLY_D_FLAT - 0.2, 0)))
union(BELLY, _sp)
BELLY.data.transform(Matrix.Rotation(-math.pi / 2, 4, 'X'))
BELLY.data.transform(Matrix.Translation((0, 0, BELLY_Z)))

# thanh kep bung (belly-clamp): hop x +-20, y CLAMP_YF..+3,0, z +-4 giao con 45 do (r <= 14,9 + (y + 44,9) - khe) -> dau vat khop con
CLAMP = box('belly_clamp', (-20.0, CLAMP_YF, BELLY_Z - CLAMP_W / 2), (20.0, CLAMP_YF + CLAMP_T, BELLY_Z + CLAMP_W / 2))
_r0 = BELLY_BORE_R - 0.3 + (CLAMP_YF - 1.0 - (BELLY_CAV_Y - 0.3)) - CLAMP_CLR
inter(CLAMP, cyl('clamp_cone', (0, CLAMP_YF - 1.0, BELLY_Z), (0, CLAMP_YF + CLAMP_T + 1.0, BELLY_Z), _r0, _r0 + CLAMP_T + 2.0, seg=96))
diff(CLAMP, cyl('clamp_h', (0, CLAMP_YF - 1, BELLY_Z), (0, CLAMP_YF + CLAMP_T + 1, BELLY_Z), THRU_D / 2, seg=24))

def feather(px, pz):
    for sgn in (-1, 1):
        b = box('vc', (-0.6, yf - 1.5, 0.0), (0.6, yf + 0.4, 6.0))
        b.data.transform(Matrix.Translation((px, 0, pz)) @ Matrix.Rotation(sgn * math.radians(38), 4, 'Y'))
        diff(BELLY, b)
for (px, pz) in ((-8, BELLY_Z + 7), (0, BELLY_Z + 7), (8, BELLY_Z + 7), (-8, BELLY_Z - 1), (0, BELLY_Z - 1), (8, BELLY_Z - 1)):
    feather(px, pz)      # 6 chu V = 12 vach

def text_cutter(body, size, center, depth):
    cu = bpy.data.curves.new('txt', 'FONT'); cu.body = body; cu.size = size; cu.extrude = 0.5 * (depth + 1.0)
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('txt', cu); SC.collection.objects.link(ob)
    for o_ in bpy.context.view_layer.objects: o_.select_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.view_layer.objects.active
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    # chu nam trong mat phang XY, day theo z -> quay de mat chu huong -y (nhin tu truoc doc duoc), len = +z
    bmesh.ops.transform(bm, matrix=Matrix.Translation(center) @ Matrix.Rotation(math.radians(90), 4, 'X'), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bpy.data.objects.remove(ob)
    return new_obj('txt_m', bm)
try:
    _tx = text_cutter("STLAB", 4.0, Vector((0, yf + 0.6 - 0.8, BELLY_Z - 10.0)), 0.6)
    diff(BELLY, _tx)
except Exception as e:
    print("TEXT FAIL", repr(e))
    raise

# --- Vanh loa (bezel): dia O72 (luoi O56) + ong non 25 do (yen non lap tu trong) + ong om vanh loa + 3 chot ngam xoay
def make_bezel():
    h0 = SPK_XF; rho = BZL_RHO
    turn = 90.0 - BZL_A; tb = rho * math.tan(math.radians(turn / 2)); tib = 2.4 / math.cos(math.radians(BZL_A))
    cx = BZL_RF - tb; A_S, CH = 40.0, 50.0
    ax, az = cx + rho * math.cos(math.radians(A_S)), h0 - rho + rho * math.sin(math.radians(A_S))
    pr = [(0, h0), (ax - (h0 - az) / math.tan(math.radians(CH)), h0), (ax, az)]
    pr += arc(cx, h0 - rho, rho, A_S, BZL_A, 6)[1:]
    r_rear = BZL_RF + BZL_T * (SPK_XF - BZL_REAR)
    plate_back = h0 - 3.0
    pr += [(r_rear, BZL_REAR), (r_rear - tib, BZL_REAR), (BZL_RF - tib + BZL_T * 3.0, plate_back),
           (CUP_OR, plate_back), (CUP_OR, CUP_END), (SPEAKER_POCKET_D / 2, CUP_END), (SPEAKER_POCKET_D / 2, plate_back), (0, plate_back)]
    z = lathe('bezel', pr, seg=96)
    bm = bmesh.new(); rmax = GRILLE_ZONE_D / 2 - GRILLE_HOLE_D / 2
    dy = GRILLE_PITCH * math.sqrt(3) / 2; cnt = 0
    for j in range(-6, 7):
        for i in range(-6, 7):
            x = i * GRILLE_PITCH + (GRILLE_PITCH / 2 if j % 2 else 0); y = j * dy
            if math.hypot(x, y) <= rmax:
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=14, radius1=GRILLE_HOLE_D / 2, radius2=GRILLE_HOLE_D / 2,
                                      depth=5.0, matrix=Matrix.Translation((x, y, h0 - 1.2)))
                cnt += 1
    gc = new_obj('grille', bm); diff(z, gc)
    for a in BAY_ANG:
        R = Matrix.Rotation(math.radians(a), 4, 'Z')
        pz0 = CUP_END + BPIN_DZ
        pn = box('bpin', (CUP_OR - 0.5, -BPIN_W / 2, pz0), (CUP_OR + BPIN_H, BPIN_W / 2, pz0 + BPIN_T)); pn.data.transform(R)
        union(z, pn)
    return z, cnt

def sector(name, r0, r1, z0, z1, a0, a1, n=16):
    bm = bmesh.new(); V = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n); c, sn = math.cos(t), math.sin(t)
        V.append([bm.verts.new((r * c, r * sn, h)) for (r, h) in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(n):
        A_, B_ = V[i], V[i + 1]
        for k in range(4):
            bm.faces.new((A_[k], A_[(k + 1) % 4], B_[(k + 1) % 4], B_[k]))
    bm.faces.new(V[0][::-1]); bm.faces.new(V[n])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm)

def make_clamp_ring(locked=False):
    zB = CUP_END - OUT_GAP - SRING_T; zL = CUP_END + LIP_PRE; zO = CUP_END - OUT_GAP
    rl = SPEAKER_POCKET_D / 2 - 0.3; rsi = CUP_OR + SLEEVE_CLR; rso = rsi + SLEEVE_T; ztop = CUP_END + SLEEVE_LEN
    r = lathe('sring', [(RING_ID / 2, zB), (RING_ID / 2, zL), (rl, zL), (rl, zO), (rsi, zO), (rsi, ztop), (rso, ztop), (rso, zB)], seg=96)
    pz0 = CUP_END + BPIN_DZ; pz1 = pz0 + BPIN_T
    rg = CUP_OR + BPIN_H + BPIN_CLR
    half = math.degrees((BPIN_W / 2 + 0.4) / rsi)
    for a in BAY_ANG:
        g0, g1 = pz0 - GROOVE_CLR, pz1
        diff(r, sector('gh', rsi - 0.5, rg, g0, g1, a - BAY_TWIST - half, a + half, 12))
        diff(r, sector('gv', rsi - 0.5, rg, g0, ztop + 0.5, a - BAY_TWIST - half, a - BAY_TWIST + half, 4))
        # nac khoa (2026-11-27): go DET_H tren mat ranh phia pz1 (mat chot ty khi xop loa day vong ep), ngay truoc vi tri khoa ->
        # chot vuot qua go (nen xop them) roi roi vao cho khoa, rung khong tu xoay lo
        rp = rsi; hp = math.degrees((BPIN_W / 2 + 0.4) / rp); bw = math.degrees(DET_W / rp)   # go tu mat trong vong ep (rsi), khong lan vao coc vanh
        union(r, sector('det', rsi, rg, pz1 - DET_H, pz1 + 0.01, a - hp - bw, a - hp, 4))
    return r

BEZEL_LOCAL, GRILLE_N = make_bezel()
SRING_LOCAL = make_clamp_ring(False)
BEZEL_W, SRING_W = {}, {}
for sgn in (-1, 1):
    F_ = SPK_F[sgn][0]
    BEZEL_W[sgn] = cp(BEZEL_LOCAL, 'bezel_w%d' % sgn); BEZEL_W[sgn].data.transform(F_)
    SRING_W[sgn] = cp(SRING_LOCAL, 'sring_w%d' % sgn); SRING_W[sgn].data.transform(F_)
    # v3: vay vit 2 x M2.5 x 6 (dat theo -y vao hoc mat rap vo truoc) + cat phang day tren be
    fin = extrude('bz_fin', fin_poly(), EAR_Y0 - 8.0, EAR_Y1, M_XZY(sgn))
    diff(fin, fin_vcut(sgn))
    for (c, r) in BZ_FIN_SCREWS:
        diff(fin, cyl('bz_fh', (sgn * c, EAR_Y0 - 1, SPK_Z + r), (sgn * c, EAR_Y1 + 1, SPK_Z + r), THRU_D / 2, seg=20))
    union(BEZEL_W[sgn], fin)
    union(BEZEL_W[sgn], cyl('bz_bot', (sgn * BZ_BOT_X, Y0, BZ_TRIM_Z - 1.0), (sgn * BZ_BOT_X, Y0, BZ_BOT_TOP), BZ_BOT_R, seg=32))
    diff(BEZEL_W[sgn], cyl('bz_botp', (sgn * BZ_BOT_X, Y0, BZ_TRIM_Z - 1.5), (sgn * BZ_BOT_X, Y0, BZ_BOT_TOP - 0.7), PILOT_D / 2, seg=20))
    inter(BEZEL_W[sgn], box('bz_trim', (-300, -300, BZ_TRIM_Z), (300, 300, 300)))

# --- Khay ampli MAX98357A (amp-tray.stl) giu nguyen hinh ban v2 (PCB 18 x 19,4 x 1,6, parts_h 3,0; TODO do module that); 2 khay
AMP_PCB_W, AMP_PCB_L = 18.0, 19.4
AMP_RAIL_CLR, AMP_SLOT = 0.25, 2.0
AMP_GAP_UNDER = 3.0
AMP_SCREW_X = 8.75
AMP_BASE_T = 2.5
def make_amp_tray():
    zt = AMP_BASE_T
    z_pcb = zt + AMP_GAP_UNDER
    xi = AMP_PCB_W / 2 - 1.0
    xg = AMP_PCB_W / 2 + AMP_RAIL_CLR
    xo = xg + 2.0
    L = AMP_PCB_L + 3.0; y0, y1 = -L / 2, L / 2
    tray = box('at_base', (-xo, y0, 0.0), (xo, y1, zt))
    for dx in (-4.0, 0.0, 4.0):
        diff(tray, box('vent', (dx - 1.2, y0 + 3.0, -0.5), (dx + 1.2, y1 - 3.0, zt + 0.5)))
    for dx in (-AMP_SCREW_X, AMP_SCREW_X):
        diff(tray, cyl('at_hole', (dx, 0, -0.5), (dx, 0, zt + 0.5), 1.4, seg=24))
    for s_ in (-1, 1):
        xa, xb = sorted((s_ * xi, s_ * xo))
        rail = box('at_rail', (xa, y0, zt - 0.2), (xb, y1, z_pcb + AMP_SLOT + 1.2))
        ga, gb = sorted((s_ * (xi - 0.5), s_ * xg))
        diff(rail, box('at_slot', (ga, y0 - 1, z_pcb), (gb, y1 + 1, z_pcb + AMP_SLOT)))
        union(tray, rail)
        ba, bb = sorted((s_ * (xi - 1.2), s_ * xi))
        bump = extrude('at_bump', [(y0 + 0.2, z_pcb - 0.01), (y0 + 1.6, z_pcb - 0.01), (y0 + 1.6, z_pcb + 0.4), (y0 + 1.2, z_pcb + 0.4)],
                       ba, bb, Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
        union(tray, bump)
    union(tray, box('at_stop', (-xi, y1 - 1.0, zt - 0.2), (xi, y1, z_pcb + 0.8)))
    return tray

# v3: KHAY CHUNG s3-tray (toa do lap rap): day + 2 thanh ray 29,6 + go do + chan dau (so cu) + 2 gia ampli dung o mat ngoai ray
# + 2 tai vit M2.5 x 6 (bat theo -y vao khoi tru bu-long de cua vo truoc). In dung (day xuong ban), go do vat 45 do.
M_YZX = Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)))      # (p, q, t) -> (x = t, y = p, z = q)
M_XZYp = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))     # (p, q, t) -> (x = p, y = t, z = q)
def make_s3_tray():
    zb, zt = TRAY_Z0, TRAY_Z0 + TRAY_T
    t = box('tr_base', (-TRAY_HXO, TRAY_Y0, zb), (TRAY_HXO, TRAY_Y1, zt))
    for dx in (-7.0, 0.0, 7.0):
        diff(t, box('tr_vent', (dx - 1.6, TRAY_Y0 + 6.0, zb - 0.5), (dx + 1.6, TRAY_Y1 - 6.0, zt + 0.5)))
    for sg in (-1, 1):
        a, b = sorted((sg * hx, sg * TRAY_HXO))
        union(t, box('tr_wall', (a, TRAY_Y0, zb), (b, TRAY_Y1, PZ1 + 1.0)))
        # go do bo (cu: 12,5..14,8 day 1,8 duoi PZ0 - 0,2): mat duoi vat 45 do de in dung khong support
        z1 = PZ0 - 0.2; z0 = z1 - LEDGE_T
        led = extrude('tr_ledge', [(sg * hx, z0 - (hx - 12.5)), (sg * hx, z1), (sg * 12.5, z1), (sg * 12.5, z0)], Y_FRONT - 2.7, TRAY_Y1, M_XZYp)
        union(t, led)
        a2, b2 = sorted((sg * 12.5, sg * TRAY_HXO))
        union(t, box('tr_stop', (a2, TRAY_Y0, zb), (b2, Y_FRONT - 0.2, PZ0 + 4.0)))
        # tai vit
        a3, b3 = sorted((sg * (TRAY_HXO - 0.5), sg * TRAY_TAB_X1))
        tab = box('tr_tab', (a3, EAR_Y0, zb), (b3, EAR_Y1, zb + TRAY_TAB_H))
        diff(tab, cyl('tr_th', (sg * TRAY_SCREW_X, EAR_Y0 - 1, zb + TRAY_TAB_H / 2), (sg * TRAY_SCREW_X, EAR_Y1 + 1, zb + TRAY_TAB_H / 2), THRU_D / 2, seg=20))
        union(t, tab)
        # gia ampli: 2 cot co ranh 2,0 (PCB 1,6 + 0,4) giu 2 canh doc PCB 18 (an 1,0, khe 0,25); day ranh do canh duoi PCB
        for sy in (-1, 1):
            ya, yb = sorted((AMP_YC + sy * (AMP_PCB_W / 2 - 1.0), AMP_YC + sy * (AMP_PCB_W / 2 + 0.25 + 2.0)))
            xa, xb = sorted((sg * (TRAY_HXO - 0.5), sg * AMP_HOLD_X1))
            _x0, _x1 = sg * (TRAY_HXO - 0.5), sg * AMP_HOLD_X1
            col = extrude('amp_col', [(_x0, 16.3), (_x1, 16.3 + AMP_HOLD_X1 - TRAY_HXO + 0.5), (_x1, AMP_TOP), (_x0, AMP_TOP)], ya, yb, M_XZYp)   # day vat 45 do
            sa, sb_ = sorted((sg * (AMP_PCB_X - 0.2), sg * (AMP_PCB_X + 1.6 + 0.2)))
            ga, gb = sorted((AMP_YC + sy * (AMP_PCB_W / 2 - 1.0 - 0.5), AMP_YC + sy * (AMP_PCB_W / 2 + 0.25)))
            diff(col, box('amp_slot', (sa, ga, AMP_ZB), (sb_, gb, AMP_TOP + 1.0)))
            union(t, col)
    return t
S3_TRAY = make_s3_tray()

# --- Kep mic INMP441 (mic-clamp.stl): nua ong lot (phia duoi) + gai me cung + 2 mep chan sau; module O15 nghieng 45 do
# He cuc bo: z = w (doc truc n, ra truoc-len), y = tiep tuyen "len-sau" (MIC_T), x = x the gioi. Dung tren mat sau (rear) khi in.
MC_RO, MC_RI = MIC_SLEEVE_BORE_R - 0.5, MIC_PCB_D / 2 + 0.3        # 10,4 va 7,8
MC_W0, MC_W1 = -12.0, -0.7
MC_YCUT = 2.0
def make_mic_clamp():
    sl = cyl('mc_out', (0, 0, MC_W0), (0, 0, MC_W1), MC_RO, seg=64)
    diff(sl, cyl('mc_in', (0, 0, MC_W0 - 1), (0, 0, MC_W1 + 1), MC_RI, seg=64))
    # mep chan sau module: vanh trong R 6,3, w -5,2..-3,7 (module o w -0,8..0,8, nhet tu tren xuong)
    lip = lathe('mc_lip', [(MC_RI + 0.3, -5.2), (6.3, -3.7), (6.3, -3.2), (MC_RI + 0.3, -3.2)], seg=64)
    union(sl, lip)
    inter(sl, box('mc_half', (-20, -20, -20), (20, MC_YCUT, 20)))
    # v3: 2 gai lay (vao cua so vach ong lot vo truoc) – chan lui theo truc (+y, -z cua the gioi)
    for sg in (-1, 1):
        g = extrude('mc_snap', [(sg * (MC_RO - 0.3), MIC_SNAP_W + 0.2), (sg * (MC_RO + 0.8), MIC_SNAP_W + 0.2), (sg * (MC_RO + 0.8), MIC_SNAP_W + 0.8),
                                (sg * (MC_RO - 0.3), MIC_SNAP_W + 1.9)], -2.0, 1.5, Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
        union(sl, g)
    return sl
MIC_CLAMP_LOCAL = make_mic_clamp()
M_mic_clamp = frame(MIC_C, MIC_N)
MIC_CLAMP_W = cp(MIC_CLAMP_LOCAL, 'mic_clamp_w'); MIC_CLAMP_W.data.transform(M_mic_clamp)

# --- Mo (beak) thu nho 0,8
# v3: mo lap tu NGOAI: vanh O17,2 day 1,0 ngoi hoc chim, vom cao 7,5; ong O13,6 rong (r 5,6) xe 3 lay dai 11, moc con 45 do
BEAK_FING_L = BEAK_HOLE_L - 0.2      # 2026-11-27 vit giau: ong dac dung cach tam chan 0,2 (vit keo vanh mo ep vao hoc chim)
bp = [(0, -BEAK_FING_L), (BEAK_HOLE_R - 0.2, -BEAK_FING_L), (BEAK_HOLE_R - 0.2, 0.0), (BEAK_FR, 0.0), (BEAK_FR, BEAK_FL_T)]
bp += [(BEAK_FR * math.cos(math.radians(a)), BEAK_FL_T + BEAK_H * math.sin(math.radians(a))) for a in range(10, 90, 10)]
BEAK = lathe('beak', bp + [(0, BEAK_FL_T + BEAK_H)], seg=64)
# an ren: 12 - 3,0 tam chan - 0,2 khe - 0,3 dau ngoi con = 8,5 -> lo moi sau 10 (toi h 1,2; vom cao 8,5)
diff(BEAK, cyl('bk_pilot', (0, 0, -BEAK_FING_L - 1), (0, 0, -BEAK_FING_L + 10.0), PILOT_D / 2, seg=20))
BEAK.data.transform(BEAK_M)

# --- Nut dau (button-cap) giu nguyen
def cross_cutters(M, u_open, depth, dirn, angs=(45.0, 135.0)):
    out = []
    for ang in angs:
        z0, z1 = sorted((u_open - dirn * 0.2, u_open + dirn * depth))
        b_ = box('crs', (-MX_STEM_L / 2, -MX_STEM_W / 2, z0), (MX_STEM_L / 2, MX_STEM_W / 2, z1))
        b_.data.transform(M @ Matrix.Rotation(math.radians(ang), 4, 'Z')); out.append(b_)
    return out

cp_ = [(0, BTN_TOP), (19, BTN_TOP)] + arc(19, BTN_TOP - 6, 6, 90, 0, 8)[1:]
cp_ += [(25.0, SEAT_Z + REST_UP + 0.1), (TALK_FLANGE_R, SEAT_Z + REST_UP + 0.1 - (TALK_FLANGE_R - 25.0)), (TALK_FLANGE_R, TALK_ZB + REST_UP), (0, TALK_ZB + REST_UP)]
CAP = lathe('cap', cp_, seg=96, M=Matrix.Translation((0, Y0, 0)))
_zc = CAP_RIM_Z
_tube_z = _zc + CAP_TUBE_END
_ceil_z = _zc + CAP_CEIL
# hoc duoi nap (mau cat-paw): O33,2 sau 9,80 tu vanh; ong O5,71 tu tran xuong, dau ong +4,31; chu thap xuyen het ong
_r_out = TALK_FLANGE_R + 0.3
_r_ce = CAP_DISH_K - _ceil_z                     # tai r nay duong con cat tran hoc
diff(CAP, lathe('caphollow', [(0, _zc - 0.5), (_r_out, _zc - 0.5), (_r_out, CAP_DISH_K - _r_out), (_r_ce, _ceil_z), (0, _ceil_z)],
                seg=96, M=Matrix.Translation((0, Y0, 0))))
union(CAP, cyl('captube', (0, Y0, _tube_z), (0, Y0, _ceil_z + 0.5), MX_TUBE_OD / 2, seg=48))
for o_ in cross_cutters(Matrix.Translation((0, Y0, _tube_z)), 0.0, MX_CROSS_DEPTH, 1):
    diff(CAP, o_)

def make_cross_gauge():
    g = box('gbase', (-17.0, -6.0, 0.0), (17.0, 6.0, 1.2))
    for i, w in enumerate(MX_GAUGE_W):
        cx = (i - 1) * 11.5
        blk = box('gblk', (cx - 5.2, -5.2, 0.0), (cx + 5.2, 5.2, 7.0))
        rel = cyl('grel', (cx, 0, 7.0 - MX_RELIEF_H), (cx, 0, 7.5), MX_RELIEF_R, seg=48)
        diff(rel, cyl('gtube', (cx, 0, 2.0), (cx, 0, 8.0), MX_TUBE_OD / 2, seg=48))
        diff(blk, rel)
        for ang in (45.0, 135.0):
            c_ = box('gcr', (-MX_STEM_L / 2, -w / 2, 7.0 - 4.5), (MX_STEM_L / 2, w / 2, 7.5))
            c_.data.transform(Matrix.Translation((cx, 0, 0)) @ Matrix.Rotation(math.radians(ang), 4, 'Z'))
            diff(blk, c_)
        for k in range(i + 1):
            diff(blk, cyl('gdot', (cx - 2.0 + 2.0 * k, -5.8, 4.0), (cx - 2.0 + 2.0 * k, -4.6, 4.0), 0.6, seg=12))
        union(g, blk)
    return g
GAUGE = make_cross_gauge()

# --- Face-plate (kem): dia 94 x 58 R10 (nho 4 tren nen), yen vat 45 do rong 5, vanh chan 104 x 68 day 2,0 (lap tu trong, 4 vit M2.5 x 6).
# He cuc bo (a, b, u): u = 0 mat truoc (in mat truoc xuong ban). Dung chong lai MS khi lap.
def make_face_plate():
    hx, hz, r = DISC
    rings = [(0.0, rr(hx - 2 * 0.88, hz - 2 * 0.88, r - 2 * 0.88))]
    for ph in (45, 52, 60, 68, 76, 84, 90):
        ins = FR_R * (1.0 - math.sin(math.radians(ph))); uu = FR_R * (1.0 - math.cos(math.radians(ph)))
        rings.append((uu, rr(hx - ins, hz - ins, r - ins)))
    # v3: bo yen vat + vanh chan 104 x 68 (lap tu trong) -> vanh FP_LIP 1,5 day 1,0 ngoi hoc chim mat nen, than thang toi FP_BODY_END
    rings += [(4.0, rr(hx, hz, r)), (4.0, rr(hx + FP_LIP, hz + FP_LIP, r + FP_LIP)), (5.0, rr(hx + FP_LIP, hz + FP_LIP, r + FP_LIP)),
              (5.0, rr(hx, hz, r)), (FP_BODY_END, rr(hx, hz, r))]
    fp = loft('fp', rings)
    ww, wh, wr, wo = WIN
    win = [(a + wo, b) for (a, b) in rrect(ww, wh, wr, 8)]
    diff(fp, extrude('fp_win', win, -1.0, 2.0, Matrix.Identity(4)))
    # vat 0,5 mep cua so mat truoc
    ch0 = [(a + wo, b) for (a, b) in rrect(ww + 2.0, wh + 2.0, wr + 1.0, 8)]
    ch1 = [(a + wo, b) for (a, b) in rrect(ww, wh, wr, 8)]
    diff(fp, loft('fp_ch', [(-0.5, ch0), (0.5, ch1)]))
    # hoc kinh 69,8 x 50,6 (kinh x -36,6..32,6 -> tam -2,0), tu u = 1,35 (vien day 1,35 sau khe 0,15)
    gl = [(a - 2.0, b) for (a, b) in rrect(SCR_GLASS[0] + 0.6, SCR_GLASS[1] + 0.6, 1.0, 6)]
    u_glass = GLASS_RECESS - 0.15
    diff(fp, extrude('fp_gl', gl, u_glass, 5.7, Matrix.Identity(4)))
    # hoc PCB 86,4 x 50,6 tu u = 5,5 (mat truoc PCB) ra sau; header + day di ra sau
    u_pcb = GLASS_RECESS + (SCR_T - SCR_PCB[2])
    diff(fp, extrude('fp_pcb', rrect(SCR_PCB[0] + 0.4, SCR_PCB[1] + 0.6, 0.6, 4), u_pcb, FP_BODY_END + 1.0, Matrix.Identity(4)))
    # lom 1,6 mat truoc PCB cho moi han chan header (dai 6 x 38, x 38..43,2)
    hb = box('fp_hdr', (38.0, -19.0, u_pcb - 1.6), (43.3, 19.0, u_pcb + 0.1)); diff(fp, hb)
    # 4 lo mo O2,4 (vit tu ren) tai lo PCB (x -40,00 / +36,08 ; z +-22), tu mat truoc PCB lui vao 3,6
    for (px, pz) in ((-40.0, 22.0), (-40.0, -22.0), (40.0, 22.0), (40.0, -22.0)):
        diff(fp, cyl('fp_pil', (px, pz, u_pcb - 3.6), (px, pz, u_pcb + 0.3), 1.2, seg=20))
    # v3: 6 lay gai (4 tren/duoi, 2 ben) xe tu vach than: day 1,2, rong 5, chan u 5,6 -> moc o u FP_WIN_U + 0,2 (gờ 0,8)
    for (k_, c_, sg_) in FP_FINGERS:
        if k_ == 'z':
            b_o = sg_ * hz
            ba, bb_ = sorted((sg_ * (hz - 1.2), sg_ * 24.9))
            diff(fp, box('fpf_back', (c_ - 3.0, ba, 5.6), (c_ + 3.0, bb_, FP_BODY_END + 0.5)))
            for e_ in (-1, 1):
                xa, xb = sorted((c_ + e_ * 2.5, c_ + e_ * 3.0))
                ba2, bb2 = sorted((sg_ * 24.9, sg_ * (hz + 0.5)))
                diff(fp, box('fpf_slot', (xa, ba2, 5.6), (xb, bb2, FP_BODY_END + 0.5)))
            diff(fp, box('fpf_tip', (c_ - 3.0, min(sg_ * 24.9, sg_ * (hz + 0.5)), FP_WIN_U + 1.85), (c_ + 3.0, max(sg_ * 24.9, sg_ * (hz + 0.5)), FP_BODY_END + 0.5)))
            hk = [(sg_ * (hz - 1.2), FP_WIN_U + 0.2), (sg_ * (hz + 0.8), FP_WIN_U + 0.2), (sg_ * (hz + 0.8), FP_WIN_U + 1.0), (sg_ * hz, FP_WIN_U + 1.8), (sg_ * (hz - 1.2), FP_WIN_U + 1.8)]
            g = extrude('fpf_hook', hk, c_ - 2.5, c_ + 2.5, Matrix(((0, 0, 1, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
            union(fp, g)
        else:
            aa, ab = sorted((sg_ * (hx - 1.2), sg_ * 43.0))
            diff(fp, box('fpf_back', (aa, -3.0, 5.6), (ab, 3.0, FP_BODY_END + 0.5)))
            for e_ in (-1, 1):
                za, zb_ = sorted((e_ * 2.5, e_ * 3.0))
                aa2, ab2 = sorted((sg_ * 43.0, sg_ * (hx + 0.5)))
                diff(fp, box('fpf_slot', (aa2, za, 5.6), (ab2, zb_, FP_BODY_END + 0.5)))
            diff(fp, box('fpf_tip', (min(sg_ * 43.0, sg_ * (hx + 0.5)), -3.0, FP_WIN_U + 1.85), (max(sg_ * 43.0, sg_ * (hx + 0.5)), 3.0, FP_BODY_END + 0.5)))
            hk = [(sg_ * (hx - 1.2), FP_WIN_U + 0.2), (sg_ * (hx + 0.8), FP_WIN_U + 0.2), (sg_ * (hx + 0.8), FP_WIN_U + 1.0), (sg_ * hx, FP_WIN_U + 1.8), (sg_ * (hx - 1.2), FP_WIN_U + 1.8)]
            g = extrude('fpf_hook', hk, -2.5, 2.5, Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
            union(fp, g)
    # dau lap ▲ khac sau 0,6 mep duoi dia (net >= 0,8)
    diff(fp, extrude('fp_tri', [(-2.2, -26.8), (2.2, -26.8), (0.0, -23.4)], -1.0, 0.6, Matrix.Identity(4)))
    return fp
FP_LOCAL = make_face_plate()
FP_W = cp(FP_LOCAL, 'fp_w'); FP_W.data.transform(MS); FP_W.data.flip_normals()

# ============================================================ XUAT STL
def export_obj(o, T, path):
    c = cp(o, 'exp'); c.data.transform(T)
    xs = [v.co.x for v in c.data.vertices]; ys = [v.co.y for v in c.data.vertices]; zs = [v.co.z for v in c.data.vertices]
    c.data.transform(Matrix.Translation((-(max(xs) + min(xs)) / 2, -(max(ys) + min(ys)) / 2, -min(zs))))
    for ob in bpy.context.view_layer.objects:
        ob.select_set(False)
    c.select_set(True); bpy.context.view_layer.objects.active = c
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
    d = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    print("EXPORT %s %.1f x %.1f x %.1f" % (path.name, *d))
    bpy.data.objects.remove(c)

def Mx(rows): return Matrix(rows)
T_front = Mx(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, Y0), (0, 0, 0, 1)))
T_back = Mx(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, -Y0), (0, 0, 0, 1)))
T_belly = Mx(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, -BELLY_FRONT), (0, 0, 0, 1)))   # mat truoc xuong ban
T_cap = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, BTN_TOP), (0, 0, 0, 1)))
T_beak = BEAK_M.inverted()   # lay xuong ban, vom len (export_obj tu dat z min = 0)
T_bezel = Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, SPK_XF), (0, 0, 0, 1)))

def refine(o, lo, hi, L=6.0):
    bm_ = bmesh.new(); bm_.from_mesh(o.data)
    for _ in range(10):
        es = set()
        for f in bm_.faces:
            vs = [v.co for v in f.verts]
            if any(max(c[i] for c in vs) < lo[i] or min(c[i] for c in vs) > hi[i] for i in (0, 1, 2)):
                continue
            for e in f.edges:
                if e.calc_length() > L:
                    es.add(e)
        if not es:
            break
        bmesh.ops.subdivide_edges(bm_, edges=list(es), cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm_, faces=bm_.faces[:])
    bm_.to_mesh(o.data); o.data.update(); bm_.free()

# chia nho tam giac to quanh PCB mic (gate kiem va cham theo dia O15 nghieng / hop)
_mc = Vector(MIC_C)
for _o in (A, B):
    refine(_o, (_mc.x - 14, _mc.y - 14, _mc.z - 14), (_mc.x + 14, _mc.y + 14, _mc.z + 14))
# va quanh 2 man hinh / header
_sc = Vector((0, SCR_PCB_Y, SCR_ZC))
refine(A, (-50, YF - 5, SCR_ZC - 40), (50, YF + 25, SCR_ZC + 40), L=8.0)

export_obj(A, T_front, OUT / "shell-front.stl")
export_obj(B, T_back, OUT / "shell-back.stl")
export_obj(SPLINE, T_front, OUT / "seam-spline.stl")   # in phang: mat cat y -> z (cao 4,0)
export_obj(BELLY, T_belly, OUT / "belly.stl")
export_obj(CLAMP, T_front, OUT / "belly-clamp.stl")   # in phang day 3,0
export_obj(BEAK, T_beak, OUT / "beak.stl")
export_obj(CAP, T_cap, OUT / "button-cap.stl")

# --- Khoi thu o switch (ban thu p2-button): chep dung o + thap + go chan nap cua dinh dau, khong in ca vo
def make_socket_test():
    zb = TALK_RIM - MX_DEPTH - 2.0
    R_o = TALK_R + 4.0
    blk = cyl('sockt', (0, Y0, zb), (0, Y0, SEAT_Z + 2.0), R_o, seg=96)
    diff(blk, lathe('tseat_t', TSEAT_PROF, seg=96, M=Matrix.Translation((0, Y0, 0))))
    diff(blk, cyl('bhole_t', (0, Y0, SEAT_Z - 0.3), (0, Y0, SEAT_Z + 5.0), BUTTON_HOLE_D / 2, seg=96))
    for o_ in mx_cutters(MT, 0.0):
        diff(blk, o_)
    return blk
SOCKET_TEST = make_socket_test()
export_obj(SOCKET_TEST, Matrix.Identity(4), OUT / "mx-socket-test.stl")
export_obj(FP_LOCAL, Matrix.Identity(4), OUT / "face-plate.stl")
for sgn, side in ((-1, "L"), (1, "R")):
    export_obj(BEZEL_W[sgn], T_bezel @ SPK_F[sgn][0].inverted(), OUT / f"speaker-bezel-{side}.stl")
    export_obj(SRING_LOCAL, Matrix.Identity(4), OUT / f"speaker-ring-{side}.stl")
export_obj(MIC_CLAMP_LOCAL, Matrix.Identity(4), OUT / "mic-clamp.stl")
export_obj(S3_TRAY, Matrix.Identity(4), OUT / "s3-tray.stl")
export_obj(GAUGE, Matrix.Identity(4), OUT / "mx-cross-gauge.stl")
export_obj(PLATE, Mx(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, FLOOR_CUT), (0, 0, 0, 1))), OUT / "base.stl")   # mat tren xuong ban
BUTTON_BASE = box('bb', (-BB_HALF, Y0 - BB_HALF, BB_ZB), (BB_HALF, Y0 + BB_HALF, TALK_RIM))
for sgn in (-1, 1):
    a, b = sorted((sgn * (BB_HALF - 0.5), sgn * BB_WING_X1))
    w_ = box('bb_wing', (a, EAR_Y0, BB_ZB), (b, EAR_Y1, BB_ZB + BB_WING_H))
    diff(w_, cyl('bb_th', (sgn * BB_SCREW_X, EAR_Y0 - 1, BB_ZB + BB_WING_H / 2), (sgn * BB_SCREW_X, EAR_Y1 + 1, BB_ZB + BB_WING_H / 2), THRU_D / 2, seg=20))
    union(BUTTON_BASE, w_)
for o_ in mx_cutters(MT, 0.0):
    diff(BUTTON_BASE, o_)
export_obj(BUTTON_BASE, Matrix.Identity(4), OUT / "button-base.stl")   # in dung, mieng o len tren

# ============================================================ LAP RAP (owl-assembled.stl)
ALL_OBJS = [A, B, SPLINE, CLAMP, PLATE, BELLY, BEAK, CAP, FP_W, BEZEL_W[-1], BEZEL_W[1], SRING_W[-1], SRING_W[1], MIC_CLAMP_W, S3_TRAY, BUTTON_BASE]
asm = bmesh.new()
for o in ALL_OBJS:
    asm.from_mesh(o.data)
am = bpy.data.meshes.new('asm'); asm.to_mesh(am); asm.free()
ao = bpy.data.objects.new('asm', am); SC.collection.objects.link(ao)
for ob in bpy.context.view_layer.objects:
    ob.select_set(False)
ao.select_set(True); bpy.context.view_layer.objects.active = ao
bpy.ops.wm.stl_export(filepath=str(OUT / "owl-assembled.stl"), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)
bpy.data.objects.remove(ao)

# ============================================================ ASM CHI TIET (do duoc + gate bayonet)
(OUT / "asm").mkdir(exist_ok=True)
def export_asm(o, path):
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)

for sgn, side in ((-1, "L"), (1, "R")):
    export_asm(BEZEL_W[sgn], OUT / "asm" / f"speaker-bezel-{side}.stl")
    export_asm(SRING_W[sgn], OUT / "asm" / f"speaker-ring-{side}.stl")
export_asm(A, OUT / "asm" / "shell-front.stl")
export_asm(B, OUT / "asm" / "shell-back.stl")
export_asm(SPLINE, OUT / "asm" / "seam-spline.stl")
export_asm(CLAMP, OUT / "asm" / "belly-clamp.stl")
export_asm(BELLY, OUT / "asm" / "belly.stl")
export_asm(BEAK, OUT / "asm" / "beak.stl")
export_asm(CAP, OUT / "asm" / "button-cap.stl")
export_asm(FP_W, OUT / "asm" / "face-plate.stl")
export_asm(MIC_CLAMP_W, OUT / "asm" / "mic-clamp.stl")
export_asm(S3_TRAY, OUT / "asm" / "s3-tray.stl")
export_asm(BUTTON_BASE, OUT / "asm" / "button-base.stl")
export_asm(PLATE, OUT / "asm" / "base.stl")

# ============================================================ PARAMS JSON
amp_params = []
for sgn in (-1, 1):
    _px = sgn * (AMP_PCB_X + 0.8)
    amp_params.append(dict(center=[round(sgn * (AMP_PCB_X + 2.3), 2), AMP_YC, round(AMP_ZB + AMP_PCB_L / 2, 2)], box=[4.6, AMP_PCB_W, AMP_PCB_L],
                           orient="dung, mat linh kien huong ra loa (x)",
                           pcb=dict(center=[round(_px, 2), AMP_YC, round(AMP_ZB + AMP_PCB_L / 2, 2)], box=[1.6, AMP_PCB_W, AMP_PCB_L], parts_h=3.0, parts_dir=[sgn, 0, 0],
                                    note="clone Shopee 18x19 / Adafruit 19,4x17,8; TODO do")))
params = dict(
    variant="v3",
    v3=dict(shell_screws=dict(xz=[list(p) for p in SHELL_SCREWS], thread="M2.5 x %g tu ren" % SCREW_L, pilot_d=PILOT_D, thru_d=THRU_D, well_d=WELL_D, well_floor=WELL_FLOOR, axis="+y"),
            screws6=[dict(name=n_, part=p_, pos=[round(x_, 2), round(EAR_Y1, 2), round(z_, 2)], axis=[0, 1, 0], head_top_y=round(EAR_Y1 + 1.7, 2)) for (n_, p_, x_, z_) in SCREWS6],
            ear=dict(t=EAR_T, clr=EAR_CLR, pilot_depth=SCREW6_PILOT, head_relief=[HEAD_D, HEAD_T]),
            base=dict(hx=BASE_HX, yf=BASE_YF, yb=BASE_YB, n=BASE_N, z=[BASE_BOT, BASE_TOP], chamfer=BASE_CH, feet=[list(f) for f in FEET], foot_d=FOOT_D,
                      bolts="4 x M3 x 16 tu duoi (TODO chieu dai theo vit co san)"),
            snaps=dict(face_plate=dict(n=len(FP_FINGERS), t=1.2, w=5.0, hook=0.8, win_u=FP_WIN_U), belly=dict(n=4, t=1.2, w=5.0, hook=0.8, len=round(BELLY_CAV_Y + 0.2 - (BELLY_FRONT + BELLY_PLATE_T), 2)),
                       beak=dict(n=3, t=1.2, w=4.5, hook=0.45, hole_d=2 * BEAK_HOLE_R), mic_clamp=dict(n=2, hook=0.8)),
            driver=[DRIVER_D, DRIVER_L],
            # 2026-11-27 vit giau mo/bung (tu trong, tua vit theo +y tu mat rap) + vit day vanh loa (tu duoi de, theo -z)
            hidden_screws=[dict(name='beak', part='beak', head=[0.0, round(BEAK_PLATE_Y0 + HID_PLATE_T, 2), BEAK_Z], axis=[0, 1, 0], length=HID_SCREW_L, pilot_d=PILOT_D),
                           dict(name='belly', part='belly', head=[0.0, CLAMP_YF + CLAMP_T, BELLY_Z], axis=[0, 1, 0], length=HID_SCREW_L, pilot_d=PILOT_D)]
                          + [dict(name='bezel-bot-%s' % sd, part='speaker-bezel-' + sd, head=[sg * BZ_BOT_X, Y0, BASE_BOT + BZ_BOT_CB_H], axis=[0, 0, -1], length=HID_SCREW_L, pilot_d=PILOT_D)
                             for sg, sd in ((-1, 'L'), (1, 'R'))]),
    wall=WALL,
    speaker_pocket_d=SPEAKER_POCKET_D,
    grille_hole_d=GRILLE_HOLE_D,
    mic_hole_d=MIC_HOLE_D,
    m3_clear_d=M3_CLEAR_D,
    m3_nut_s=M3_NUT_S,
    button_cap_d=BUTTON_CAP_D,
    button_hole_d=BUTTON_HOLE_D,
    vent_w=VENT_W,
    speakers=[dict(center=[round(q["center"][0], 2), q["center"][1], q["center"][2]], axis=[round(q["axis"][0], 4), round(q["axis"][1], 4), 0.0]) for q in SPEAKERS],
    pcb_center=PCB_CENTER,
    pcb_box=list(PCB_BOX),
    amps=amp_params,
    screen=dict(center=[0.0, round(SCR_PCB_Y, 2), SCR_ZC], glass_front_y=round(GLASS_Y, 2), header_side="+x",
                window=[WIN[0], WIN[1]], window_offset_x=WIN[3], glass_recess=GLASS_RECESS, bezel_over=2.5,
                holes=[SCR_HOLES[0], SCR_HOLES[1]], hole_d=SCR_HOLE_D, touch=True),
    mic=dict(center=list(MIC_C), box=[17.0, 8.0, 17.0], holes=3, hole_x=list(MIC_HOLE_X), hole_z=round(mpt(MIC_L).z, 2),
             axis=[0.0, round(-0.7075, 4), round(0.7067, 4)],
             seal=dict(type="gasket", pocket_floor_w=MIC_POCKET_W1, gap=round(MIC_POCKET_W1 - MIC_PCB_T / 2, 2), gasket_od=MIC_GASKET_OD, gasket_id=MIC_GASKET_ID, note="ron xop dan len vach quanh ong dan am O4; PCB ep ron"),
             gasket_t=MIC_GASKET_T, drop=MIC_DROP,
             pcb=dict(center=list(MIC_C), d=MIC_PCB_D, t=MIC_PCB_T, axis=[0.0, -0.7075, 0.7067], note="INMP441 Shopee tron ~O15, nghieng 45 do; day PCB TODO")),
    pcb_usb=dict(center=[PCB_CENTER[0], PCB_Y_USB, PCB_CENTER[2]], dir="+y"),
    cable_slot=dict(side="back", w=CABLE_W, h=CABLE_H, r=CABLE_R, center=[PCB_CENTER[0], round(Y_ROOF + CABLE_WALL_T / 2, 2), PCB_CENTER[2]], wall_t=round(CABLE_WALL_T, 2)),
    split_plane_y=Y0,
    grille_holes_per_speaker=GRILLE_N,
    speaker_dims=[SPEAKER_D, SPEAKER_L],
    speaker_clamp=dict(
        flange_t=FLANGE_T, gasket_t=GASKET_T, body_d_max=BODY_D_MAX, ring_t=SRING_T, ring_id=RING_ID,
        gasket_locked=round(GASKET_T - LIP_PRE, 3), gasket_slot_kept=True,
        gasket_note="bang xop 2 mm dan vong mat loa (khong lay PETG)",
        bayonet=dict(n=len(BAY_ANG), twist=BAY_TWIST, pin_w=BPIN_W, pin_h=BPIN_H, pin_t=BPIN_T, sleeve_clr=SLEEVE_CLR,
                     pin_clr=BPIN_CLR, groove_clr=GROOVE_CLR, detent_h=DET_H, lip_pre=LIP_PRE, out_gap=OUT_GAP, sleeve_t=SLEEVE_T)),
    mx=dict(hole=MX_HOLE, socket_depth=MX_DEPTH, stem_cross_l=MX_STEM_L, stem_cross_w=MX_STEM_W,
            cross_depth=MX_CROSS_DEPTH, travel_free=MIC_TRAVEL_BVH, travel_floor=round(TRAVEL_SHELL, 2), stop_gap=CAP_STOP_GAP, tube_gap=TUBE_GAP,
            cap_hollow_d=2 * CAP_HOLLOW_R, cap_hollow_depth=CAP_CEIL, tube_od=MX_TUBE_OD, tube_end_above_rim=CAP_TUBE_END,
            socket_outer_w=MX_TOWER_W, rim_z=round(CAP_RIM_Z, 3), mouth_z=round(TALK_RIM, 3), floor_z=round(TALK_ZPOCKET, 3),
            assumed=dict(housing_h=MX_HOUSING_H, stem_h=MX_STEM_H, travel=4.0, note="housing/stem/hanh trinh 4,0 la nguon phu chua datasheet"),
            source="fit-library catpaw/mx-keycap-cross + catpaw/mx-socket (docs/research-notes/cat-paw-clicker-fits.md)",
            keys=[dict(name="talk", gpio=1, axis="z", pos=[0.0, Y0, TALK_RIM], flange_over=round(TALK_FLANGE_R - BUTTON_HOLE_D / 2, 2))]),
    face_plate=dict(disc=[2 * DISC[0], 2 * DISC[1], DISC[2]], protrude=4.0, bevel=BEV, flange=[2 * (DISC[0] + BEV), 2 * (DISC[1] + BEV), FL_T],
                    screws=dict(n=4, xz=list(SCREW_FP), thread="M2.5 x 6", thru_d=2.8, pilot_d=2.4)),
)
(OUT / "owl-params.json").write_text(json.dumps(params, indent=1), encoding="utf-8")

# ============================================================ ANH PREVIEW & EXPLODED
PCOL = dict(shell='#F6BE9A', cream='#FFF3DF', butter='#FFC857', white='#FFFFFF', spk='#6B6F78', pcb='#2E8B57', amp='#4169E1', scr='#1F2A44')
TMP = OUT / "_tmp"; TMP.mkdir(exist_ok=True)

def dump(o, name):
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(TMP / (name + ".stl")), export_selected_objects=True, global_scale=1.0, apply_modifiers=False)

spk_dummies = []
for sgn in (-1, 1):
    c_ = SPK_F[sgn][2]; a_ = SPK_F[sgn][1]
    d1 = cyl('spk_d%d' % sgn, c_ + a_ * 13.0 - a_ * FLANGE_T, c_ + a_ * 13.0, SPEAKER_D / 2, seg=48)
    union(d1, cyl('spk_db%d' % sgn, c_ + a_ * 13.0 - a_ * FLANGE_T, c_ - a_ * 13.0, BODY_D_MAX / 2, seg=48))
    spk_dummies.append(d1)
pcb_dummy = box('pcb_d', (-PCB_BOX[0] / 2, PCB_CENTER[1] - PCB_BOX[1] / 2, PCB_CENTER[2] - PCB_BOX[2] / 2),
                         (PCB_BOX[0] / 2, PCB_CENTER[1] + PCB_BOX[1] / 2, PCB_CENTER[2] + PCB_BOX[2] / 2))
amp_dummies = [box('amp_d%d' % i, tuple(am_['pcb']['center'][k] - am_['pcb']['box'][k] / 2 for k in range(3)), tuple(am_['pcb']['center'][k] + am_['pcb']['box'][k] / 2 for k in range(3)))
               for i, am_ in enumerate(amp_params)]
scr_dummy = box('scr_d', (-43.0, GLASS_Y, SCR_ZC - 25.0), (43.0, GLASS_Y + 5.6, SCR_ZC + 25.0))
mic_dummy = cyl('mic_d', mpt(-0.8), mpt(0.8), MIC_PCB_D / 2, seg=48)

ITEMS = [
    (A, 'front', 'shell', (0, -75, 0)),
    (B, 'back', 'shell', (0, 75, 0)),
    (SPLINE, 'spline', 'shell', (0, 30, 0)),
    (PLATE, 'plate', 'cream', (0, 0, -45)),
    (BELLY, 'belly', 'cream', (0, -130, 0)),
    (CLAMP, 'clamp', 'cream', (0, -40, 0)),
    (BEAK, 'beak', 'butter', (0, -135, 30)),
    (CAP, 'cap', 'butter', (0, 0, 55)),
    (FP_W, 'fp', 'cream', (0, -150, 40)),
    (BEZEL_W[-1], 'bzl', 'shell', (-90, -60, 0)),
    (BEZEL_W[1], 'bzr', 'shell', (90, -60, 0)),
    (SRING_W[-1], 'srl', 'shell', (-75, -30, 0)),
    (SRING_W[1], 'srr', 'shell', (75, -30, 0)),
    (spk_dummies[0], 'spl', 'spk', (-60, -20, 0)),
    (spk_dummies[1], 'spr', 'spk', (60, -20, 0)),
    (S3_TRAY, 'tray', 'cream', (0, 30, 20)),
    (BUTTON_BASE, 'bbase', 'cream', (0, 0, 35)),
    (amp_dummies[0], 'al', 'amp', (-25, 0, 35)),
    (amp_dummies[1], 'ar', 'amp', (25, 0, 35)),
    (MIC_CLAMP_W, 'micclamp', 'shell', (0, -40, 30)),
    (mic_dummy, 'mic', 'pcb', (0, -40, 30)),
    (scr_dummy, 'scr', 'scr', (0, -50, 0)),
    (pcb_dummy, 'pcb', 'pcb', (0, 30, 0)),
]
for o, n, c, off in ITEMS:
    dump(o, n)

def fresh_scene(res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = 'Standard'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = hexc('#FBF3E8'); bg.inputs['Strength'].default_value = 0.45
    for nm, loc, en in (('key', (-300, -400, 500), 2.2), ('fill', (400, -300, 200), 0.8), ('rim', (100, 400, 400), 1.0)):
        ld = bpy.data.lights.new(nm, 'SUN'); ld.energy = en
        lo = bpy.data.objects.new(nm, ld); sc.collection.objects.link(lo)
        lo.rotation_euler = (-Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return sc

def load_items(sc, which, offs):
    for o, n, c, off in ITEMS:
        if n not in which:
            continue
        bpy.ops.wm.stl_import(filepath=str(TMP / (n + ".stl")))
        ob = bpy.context.selected_objects[0]
        m = bpy.data.materials.new(n); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = hexc(PCOL[c]); b.inputs['Roughness'].default_value = 0.6
        ob.data.materials.append(m)
        if offs:
            ob.location = off

def cam_at(sc, target, az, el, dist, lens=60):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_end = 5000
    cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    d = Vector((math.sin(math.radians(az)) * math.cos(math.radians(el)), -math.cos(math.radians(az)) * math.cos(math.radians(el)), math.sin(math.radians(el))))
    cam.location = Vector(target) + d * dist
    cam.rotation_euler = (-d).to_track_quat('-Z', 'Y').to_euler()

def render_png(sc, path):
    sc.render.filepath = str(path); sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)

def merge(p1, p2, out):
    imgs = []
    for p in (p1, p2):
        im = bpy.data.images.load(str(p)); a = np.empty(im.size[0] * im.size[1] * 4, dtype=np.float32); im.pixels.foreach_get(a)
        imgs.append(a.reshape(im.size[1], im.size[0], 4))
    big = np.concatenate(imgs, axis=1)
    nim = bpy.data.images.new('m', width=big.shape[1], height=big.shape[0], alpha=True)
    nim.pixels.foreach_set(big.reshape(-1)); nim.filepath_raw = str(out); nim.file_format = 'PNG'; nim.save()

ASM = ['front', 'back', 'spline', 'plate', 'belly', 'beak', 'cap', 'fp', 'bzl', 'bzr', 'srl', 'srr', 'micclamp', 'tray', 'bbase']
sc = fresh_scene((800, 1200)); load_items(sc, ASM, False)
cam_at(sc, (0, 0, 85), -32, 12, 560); render_png(sc, OUT / "_v1.png")
bpy.data.objects.remove(sc.camera)
cam_at(sc, (0, 0, 85), 148, 18, 560); render_png(sc, OUT / "_v2.png")
merge(OUT / "_v1.png", OUT / "_v2.png", OUT / "owl-preview.png")

sc = fresh_scene((1000, 1300)); load_items(sc, ASM, False)
cd_ = bpy.data.cameras.new('camf'); cd_.type = 'ORTHO'; cd_.ortho_scale = 200; cd_.clip_end = 5000
cf_ = bpy.data.objects.new('camf', cd_); sc.collection.objects.link(cf_); sc.camera = cf_
cf_.location = (0, -600, 85); cf_.rotation_euler = (math.radians(90), 0, 0)
render_png(sc, OUT / "owl-front.png")
cf_.location = (0, 600, 85); cf_.rotation_euler = (math.radians(90), 0, math.radians(180))
render_png(sc, OUT / "owl-back.png")

sc = fresh_scene((1600, 1200)); load_items(sc, [n for _, n, _, _ in ITEMS], True)
cam_at(sc, (0, -20, 75), -30, 22, 950, 70); render_png(sc, OUT / "owl-exploded.png")

for f in ("_v1.png", "_v2.png"):
    if (OUT / f).exists(): (OUT / f).unlink()
shutil.rmtree(TMP, ignore_errors=True)

print("BUILD OWL V3 OK")
