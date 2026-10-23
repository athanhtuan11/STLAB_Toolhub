"""Dung model board KHONG co STEP chinh hang, tu BAN VE CO KHI chinh hang (community/boards-official/drawings/).

Muc dich: thiet ke hop/ga (bien dang ngoai, lo bat, vi tri cong). KHONG dung de ve mach.
  - Toa do mat bang (kich thuoc bo mach, lo, tam cong): lay tu ban ve, ghi nguon tung board.
  - Chieu cao/kich thuoc than linh kien: ban ve khong cho -> gia tri "uoc" (ghi ro nguon uoc tinh).
    Thiet ke hop: chua khe >= 1 mm quanh cong va DO HANG THAT truoc khi in.

Chay bang FreeCAD:  "C:/Program Files/FreeCAD 1.1/bin/freecadcmd.exe" boards_param.py
Ra: community/boards-official/models/<id>/<id>.step (+ <id>.png: hinh chieu de duyet)
Truc: X doc canh dai, Y doc canh ngan, Z len; mat duoi PCB o Z=0, goc duoi-trai PCB o (0,0).
"""

from __future__ import annotations

from pathlib import Path

import FreeCAD as App
import Part

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "community" / "boards-official" / "models"
ESP3D = ROOT / "community" / "espressif-kicad-libraries" / "3dmodels" / "espressif.3dshapes"
WROOM32E = ESP3D / "ESP32-WROOM-32E.STEP"
WROOM1 = ESP3D / "ESP32-S3-WROOM-1.STEP"
V = App.Vector

# Uoc tinh dung chung (khong co trong ban ve):
PCB_T = 1.6  # uoc: do day PCB pho bien. TODO do hang that (Pi Zero co the mong hon)
# Do tu model Pi 4B (FreeCAD-library, CC-BY 3.0) ngay 2026-10-22 – Pi 5 dung cung kieu cong:
USB_STACK = dict(w=15.4, d=17.9, h=15.6, nho=3.0)   # cum USB-A 2 tang; nho = nho ra khoi mep (ban ve Pi 5: 3)
RJ45 = dict(w=16.3, d=21.6, h=13.7, nho=3.0)
HDR_H = 8.5  # uoc: header 2,54 mm (nhua 2,5 + chan ~6) – TODO do hang that


def pcb(lx, ly, r, holes, hole_d):
    """Tam PCB bo goc r, khoet lo (x, y)."""
    s = Part.makeBox(lx, ly, PCB_T)
    if r > 0:
        s = s.makeFillet(r, [e for e in s.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[1].Point.z) > 1e-6])
    for x, y in holes:
        s = s.cut(Part.makeCylinder(hole_d / 2, PCB_T + 2, V(x, y, -1)))
    return s


def box(x0, y0, z0, lx, ly, lz):
    return Part.makeBox(lx, ly, lz, V(x0, y0, z0))


def header(xc, yc, n, rows=2, up=True, pitch=2.54):
    """Header n chan x rows hang, tam (xc, yc), doc truc X."""
    lx, ly = n * pitch, rows * pitch
    z = PCB_T if up else -HDR_H
    return box(xc - lx / 2, yc - ly / 2, z, lx, ly, HDR_H)


def edge_port_bottom(xc, w, d, h, nho):
    """Cong o canh duoi (y=0), tam theo X = xc, nho ra ngoai mep nho mm."""
    return box(xc - w / 2, -nho, PCB_T, w, d, h)


def edge_port_right(lx, yc, w, d, h, nho):
    return box(lx + nho - d, yc - w / 2, PCB_T, d, w, h)


# ---------------------------------------------------------------- Raspberry Pi 5
def rpi5():
    # Nguon: raspberry-pi-5-mechanical-drawing.pdf (Raspberry Pi Ltd). 85 x 56; lo Ø2.7 cach mep 3.5,
    # khoang lo 58 x 49; header tam x = 3.5 + 29; USB-C x 11.2, micro-HDMI x 25.8 / 39.2;
    # Ethernet tam y 10.2, USB y 29.1 / 47; RJ45 nho 3 mm.
    lx, ly = 85.0, 56.0
    holes = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
    parts = [pcb(lx, ly, 3.0, holes, 2.7),  # r = 3: uoc theo hinh, ban ve khong ghi
             header(32.5, 52.5, 20)]
    parts.append(edge_port_bottom(11.2, 9.0, 7.5, 3.3, 1.0))   # USB-C: than uoc 9 x 7.5 x 3.3
    for xc in (25.8, 39.2):
        parts.append(edge_port_bottom(xc, 6.6, 7.5, 3.4, 1.0))  # micro-HDMI: uoc
    parts.append(edge_port_right(lx, 10.2, **RJ45))
    for yc in (29.1, 47.0):
        parts.append(edge_port_right(lx, yc, **USB_STACK))
    return parts


# ---------------------------------------------------------------- Raspberry Pi Zero 2 W
def rpi_zero2w():
    # Nguon: raspberry-pi-zero-2-w-mechanical-drawing.pdf. 65 x 30; lo cach mep 3.5, khoang 58 x 23;
    # header tam x = 3.5 + 29, y = 30 - 3.5; mini-HDMI x 12.4, micro-USB x 41.4 (du lieu) / 54 (nguon).
    lx, ly = 65.0, 30.0
    holes = [(3.5, 3.5), (61.5, 3.5), (3.5, 26.5), (61.5, 26.5)]
    return [pcb(lx, ly, 3.0, holes, 2.7),  # Ø lo khong ghi tren ban ve -> 2.7 nhu Pi 5 (M2.5). TODO do
            header(32.5, 26.5, 20),      # ban Zero 2 W thuong KHONG han san header (ban WH co)
            edge_port_bottom(12.4, 11.2, 7.5, 3.3, 0.5),   # mini-HDMI: uoc
            edge_port_bottom(41.4, 8.0, 5.5, 2.8, 1.0),    # micro-USB: uoc
            edge_port_bottom(54.0, 8.0, 5.5, 2.8, 1.0)]


# ---------------------------------------------------------------- ESP32-DevKitC V4
def esp32_devkitc_v4():
    # Nguon: esp32_devkitc_v4_dimensions.pdf (Espressif). PCB 27.94 x 48.26 (dung doc -> o day X = 48.26);
    # 2 hang 19 chan, cach 25.40, buoc 2.54; chan cuoi cach mep 1.29; module rong 18 nho khoi mep 6.04.
    lx, ly = 48.26, 27.94
    parts = [pcb(lx, ly, 0.0, [], 0)]
    n, pitch = 19, 2.54
    x_mid = 1.29 + (n - 1) * pitch / 2
    for yc in (1.27, 1.27 + 25.40):
        parts.append(header(x_mid, yc, n, rows=1, up=False))
    # Module ESP32-WROOM-32E: model chinh hang Espressif, anten nho khoi mep x = lx + 6.04.
    parts.append(esp_module(WROOM32E, lx + 6.04, ly / 2))
    parts.append(edge_port_bottom_x0(ly / 2, 8.0, 5.5, 2.8, 1.0))  # micro-USB o dau doi dien anten: uoc
    return parts


def esp_module(path, x_anten, yc):
    """Dat module Espressif: canh dai doc truc X, dau anten o x = x_anten, tam Y = yc, nam tren PCB."""
    m = Part.read(str(path))
    b = m.BoundBox
    if b.XLength < b.YLength:  # file goc dung doc theo Y
        m.rotate(V(0, 0, 0), V(0, 0, 1), -90)
        b = m.BoundBox
    m.translate(V(x_anten - b.XMax, yc - (b.YMin + b.YMax) / 2, PCB_T - b.ZMin))
    return m


# ---------------------------------------------------------------- ESP32-S3-DevKitC-1 v1.1
def esp32_s3_devkitc_1():
    # Nguon: DXF_ESP32-S3-DevKitC-1_V1.1_20220429 (.pdf + .dxf, Espressif) – toa do doc thang tu DXF:
    # PCB 25.40 x 62.74 (o day X = 62.74); 2 hang 22 chan cach mep 1.27, chan cuoi cach mep duoi 8.00;
    # module 18 rong, tam 12.75, anten den 69.15 (nho 6.41); 2 micro-USB (UART, USB) tam 6.0 / 19.4 o mep duoi.
    lx, ly = 62.74, 25.40
    parts = [pcb(lx, ly, 0.0, [], 0)]
    n, pitch = 22, 2.54
    for yc in (1.27, ly - 1.27):
        parts.append(header(8.00 + (n - 1) * pitch / 2, yc, n, rows=1, up=False))
    parts.append(esp_module(WROOM1, 69.15, 12.75))
    for yc in (6.0, 19.4):
        parts.append(edge_port_bottom_x0(yc, 8.0, 5.5, 2.8, 1.0))  # micro-USB: than uoc
    return parts


def edge_port_bottom_x0(yc, w, d, h, nho):
    """Cong o canh x=0, tam theo Y = yc."""
    return box(-nho, yc - w / 2, PCB_T, d, w, h)


def col(x, y0, n, z0, h, cols=1, pitch=2.54):
    """Hang chan doc truc Y: chan dau tai (x, y0), n chan di len, cols cot sang +X."""
    return box(x - pitch / 2, y0 - pitch / 2, z0, cols * pitch, n * pitch, h)


# ---------------------------------------------------------------- STM32 Nucleo-64 (MB1136)
def nucleo64():
    # Nguon: ST UM1724 Rev 14, Figure 5 (drawings/um1724-stm32-nucleo64.pdf).
    # Toan bo 70 x 82.5; phan chinh (sau khi be ST-LINK) cao 57.54.
    # Toa do do tren ban ve (10 px/mm), KHOP CHEO voi chuan chan Arduino UNO:
    # cot Arduino x = 10.87 / 59.13 (cach 48.26); hang chan duoi y = 5.04 (= 82.5 - 3.80 - 2.54 - 71.12);
    # lo: (10.87, 40.60 + 13.97), (59.13, 49.74 + 3.56), (10.87 + 33.02, 5.04 - 2.54).
    # Morpho CN7/CN10: 2 x 19, hai cot ngoai cach 63.50, doi xung quanh tam bo -> x = 3.25 / 66.75.
    lx, ly, y_stlink = 70.0, 82.5, 57.54
    holes = [(10.87, 54.57), (59.13, 53.30), (43.89, 2.50)]
    # Ø lo: ban ve khong ghi -> 3.2 nhu Arduino UNO (TODO do). Phan ST-LINK (y > y_stlink) be duoc: tach rieng
    # 2 tam de hop co the thiet ke cho ca ban da be (chi dung tam duoi).
    parts = [pcb(lx, y_stlink, 0.0, holes, 3.2), box(0, y_stlink, 0, lx, ly - y_stlink, PCB_T)]
    y0 = 5.04
    for x in (3.25, 64.21):  # Morpho: chan duc 2 phia (uoc: tren HDR_H, duoi 6)
        parts += [col(x, y0, 19, PCB_T, HDR_H, cols=2), col(x, y0, 19, -6.0, 6.0, cols=2)]
    # Arduino: header CAI (cai) phia tren, uoc cao 8.5
    parts += [col(10.87, 22.82, 8, PCB_T, 8.5),   # CN6 nguon: VIN y = 22.82 .. 40.60
              col(10.87, y0, 6, PCB_T, 8.5),      # CN8 A0..A5
              col(59.13, y0, 8, PCB_T, 8.5),      # CN9 D0..D7
              col(59.13, 26.88, 10, PCB_T, 8.5)]  # CN5 D8..SCL (cach CN9 4.06)
    parts.append(box(47.0 - 3.9, ly - 8.0, PCB_T, 7.8, 9.0, 4.0))  # mini-USB ST-LINK tam x ~ 47 (do ban ve): than uoc
    return parts


# ---------------------------------------------------------------- STM32 "Blue Pill" (generic, khong co hang chinh thuc)
def blue_pill():
    # Nguon cong dong, mau thuan: 23 x 53 (stm32-base.org), 22.5 x 53 (qeda),
    # 22.86 x 53.34 (diyAudio; ban J.2 dai 58.42).
    # Chon 22.86 x 53.34 (= 0.9" x 2.1"); 2 hang 20 chan buoc 2.54,
    # hai hang cach 15.24 (0.6"; qeda ghi 15) -> DO HANG THAT.
    # Khong co lo bat. Cong micro-USB o mot dau, header SWD 4 chan o dau kia.
    lx, ly = 53.34, 22.86
    parts = [pcb(lx, ly, 0.0, [], 0)]
    x_mid, p = lx / 2, 2.54
    for yc in (ly / 2 - 7.62, ly / 2 + 7.62):
        parts.append(header(x_mid, yc, 20, rows=1, up=False))
    parts.append(edge_port_bottom_x0(ly / 2, 8.0, 5.5, 2.8, 1.0))   # micro-USB: uoc
    parts.append(box(lx - 2 * p, ly / 2 - 2 * p, PCB_T, p, 4 * p, HDR_H))  # SWD 4 chan dung: vi tri uoc
    return parts


# ---------------------------------------------------------------- LOLIN (Wemos) D1 mini v4.0.0
def d1_mini():
    # Nguon: dim_d1_mini_v4.0.0.pdf (wemos.cc). 25.4 x 34.3; 2 hang 8 chan cach 22.86 (cach mep 1.27);
    # 2 lo Ø2.0 tai 2.5 va 2.5 + 20.4 tinh tu canh trai. Toa do doc (ban ve khong ghi so) DO tren ban ve
    # (22.5 px/mm): chan cuoi cach mep USB 8.79, khoang 8 chan = 17.78 (ban ve ghi 17.7); tam lo cach dau tren 3.24.
    # Bo goc tron + vat goc canh USB khong dung (hop bao chu nhat -> rong hon that mot chut).
    lx, ly = 34.3, 25.4
    holes = [(lx - 3.24, 2.5), (lx - 3.24, 22.9)]
    parts = [pcb(lx, ly, 0.0, holes, 2.0)]
    n, pitch = 8, 2.54
    for yc in (1.27, ly - 1.27):
        parts.append(header(8.79 + (n - 1) * pitch / 2, yc, n, rows=1, up=False))  # ban giao kem header roi
    parts.append(edge_port_bottom_x0(ly / 2, 9.0, 7.3, 3.2, 0.5))  # USB-C (v4): than uoc
    return parts


# ---------------------------------------------------------------- AI-Thinker ESP32-CAM
def esp32_cam():
    # Nguon: datasheet "ESP32-CAM Wi-Fi + BT SoC Module V1.0" (AI-Thinker, ban Elecrow phat hanh):
    # hinh ghi 27 x 40, bang thong so ghi 27 x 40.5 x 4.5 (±0.2) -> dung 40.5 cho hop bao.
    # 2 hang 8 chan (DIP-16) cach 22.86, buoc 2.54, chan cuoi cach mep duoi 4.58; vung anten 6.218 o dau tren.
    lx, ly, h = 40.5, 27.0, 4.5
    parts = [box(0, 0, 0, lx, ly, h)]  # ca module (PCB + linh kien) theo thong so 4.5 mm
    n, pitch = 8, 2.54
    for yc in (ly / 2 - 11.43, ly / 2 + 11.43):
        parts.append(header(4.58 + (n - 1) * pitch / 2, yc, n, rows=1, up=False))
    return parts  # camera OV2640 (ong kinh + cap FPC) CHUA dung: TODO do hang that


BOARDS = {
    "raspberry-pi-5": rpi5,
    "raspberry-pi-zero-2-w": rpi_zero2w,
    "esp32-devkitc-v4": esp32_devkitc_v4,
    "esp32-s3-devkitc-1": esp32_s3_devkitc_1,
    "stm32-nucleo-64": nucleo64,
    "stm32-blue-pill": blue_pill,
    "lolin-d1-mini-v4": d1_mini,
    "esp32-cam": esp32_cam,
}


def preview(shape, png: Path, title: str):
    """Hinh chieu bang + canh (matplotlib) de Tuan duyet bang anh."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    verts, tris = shape.tessellate(0.2)
    fig, axs = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [3, 2]})
    for ax, (i, j, lab) in zip(axs, [(0, 1, "Nhin tu tren (X, Y)"), (0, 2, "Nhin ngang (X, Z)")]):
        polys = [[(verts[k][i], verts[k][j]) for k in t] for t in tris]
        ax.add_collection(PolyCollection(polys, facecolor="#9ab", edgecolor="none", alpha=0.35))
        bb = shape.BoundBox
        lo, hi = (bb.XMin, bb.YMin, bb.ZMin), (bb.XMax, bb.YMax, bb.ZMax)
        ax.set_xlim(lo[i] - 3, hi[i] + 3)
        ax.set_ylim(lo[j] - 3, hi[j] + 3)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_title(lab)
        ax.set_xlabel("mm")
    b = shape.BoundBox
    fig.suptitle(f"{title}   hop bao {b.XLength:.1f} x {b.YLength:.1f} x {b.ZLength:.1f} mm  (dung tu ban ve)")
    fig.tight_layout()
    fig.savefig(png, dpi=110)
    plt.close(fig)


def main():
    for bid, fn in BOARDS.items():
        shape = Part.makeCompound(fn())
        d = OUT / bid
        d.mkdir(parents=True, exist_ok=True)
        shape.exportStep(str(d / f"{bid}.step"))
        b = shape.BoundBox
        print(f"{bid:24} hop le={shape.isValid()} hop bao {b.XLength:.1f} x {b.YLength:.1f} x {b.ZLength:.1f} mm")
        try:
            preview(shape, d / f"{bid}.png", bid)
        except ImportError as e:
            print("  bo qua anh xem truoc:", e)


main()
