"""
build_part.py - Tao chi tiet Piston_rod_Shoulder cho canh tay pushrod-arm (FreeCAD Part module).
Xuat part.step (1 solid duy nhat).
"""

import math
import os
import sys
import FreeCAD as App
import Part

# ==========================================
# THAM SO THIET KE (PARAMETRIC DEFINITIONS)
# ==========================================

# 1. Than ty (Piston rod body)
ROD_X_START = 27.38
ROD_X_END = 94.78
ROD_Y_THICKNESS = 6.0    # y from -3.0 to +3.0
ROD_Z_WIDTH = 8.0        # z from -4.0 to +4.0
ROD_FILLET_R = 1.5       # Bo 4 canh doc truc X

# 2. Mat noi (Connecting eye)
EYE_CENTER_X = 99.78
EYE_CENTER_Z = 0.0
EYE_R = 6.0
EYE_PIN_HOLE_D = 5.4     # Duong kinh lo chot (khe 0.3/ben voi chot 4.8)

# 3. Lo ty ren (Threaded rod hole)
ROD_HOLE_D = 3.6         # Duong kinh lo ty ren M3 (khe 0.3/ben voi ty ren 3.0)
ROD_HOLE_X_START = 27.38 # Mo o mat dau
ROD_HOLE_X_CUT = 61.88   # Cat tai x = 61.88 (khong thung)

# 4. Hoc dai oc M3 (M3 Nut pocket)
NUT_X_START = 30.03
NUT_X_END = 32.73
NUT_FLAT_TO_FLAT = 5.7   # Luc giac rong 2 mat 5.7 (5.5 + 0.2 khe ho)
NUT_SLOT_Y_MAX = 4.0     # Ranh ho mo len mat +Y thoat khoi mat y = +3

# Output file
OUTPUT_FILENAME = "part.step"


def build_piston_rod():
    V = App.Vector

    # -------------------------------------------------------------
    # 1. Than ty: tiet dien 6.0 (y -3..+3) x 8.0 (z -4..+4), bo 4 canh doc
    # -------------------------------------------------------------
    rod_len = ROD_X_END - ROD_X_START
    rod_box = Part.makeBox(
        rod_len,
        ROD_Y_THICKNESS,
        ROD_Z_WIDTH,
        V(ROD_X_START, -ROD_Y_THICKNESS / 2.0, -ROD_Z_WIDTH / 2.0)
    )

    # Chon 4 canh doc theo truc X (song song voi truc X)
    longitudinal_edges = [
        e for e in rod_box.Edges
        if abs(e.Vertexes[0].Point.x - e.Vertexes[1].Point.x) > (rod_len - 1e-4)
    ]
    than_ty = rod_box.makeFillet(ROD_FILLET_R, longitudinal_edges)

    # -------------------------------------------------------------
    # 2. Mat noi: tru tron truc Y, tam (99.78, 0), R=6.0, y -3..+3
    # -------------------------------------------------------------
    mat_noi = Part.makeCylinder(
        EYE_R,
        ROD_Y_THICKNESS,
        V(EYE_CENTER_X, -ROD_Y_THICKNESS / 2.0, EYE_CENTER_Z),
        V(0, 1, 0)
    )

    # Hop than ty va mat noi
    part = than_ty.fuse(mat_noi)

    # -------------------------------------------------------------
    # Lo chot mat noi: duong kinh 5.4, xuyen doc theo truc Y
    # -------------------------------------------------------------
    eye_hole = Part.makeCylinder(
        EYE_PIN_HOLE_D / 2.0,
        ROD_Y_THICKNESS + 2.0,
        V(EYE_CENTER_X, -ROD_Y_THICKNESS / 2.0 - 1.0, EYE_CENTER_Z),
        V(0, 1, 0)
    )
    part = part.cut(eye_hole)

    # -------------------------------------------------------------
    # 3. Lo ty ren: duong kinh 3.6 doc truc X, x = 27.38 -> 61.88
    # -------------------------------------------------------------
    hole_len = ROD_HOLE_X_CUT - ROD_HOLE_X_START
    rod_hole = Part.makeCylinder(
        ROD_HOLE_D / 2.0,
        hole_len + 0.5,
        V(ROD_HOLE_X_START - 0.5, 0, 0),
        V(1, 0, 0)
    )
    part = part.cut(rod_hole)

    # -------------------------------------------------------------
    # 4. Hoc dai oc M3 va ranh ho len mat +Y
    # -------------------------------------------------------------
    # Luc giac rong 2 mat NUT_FLAT_TO_FLAT:
    # 2 dinh tren truc Z (z = +-R_corner), 2 mat song song XZ tai y = +-flat_half
    flat_half = NUT_FLAT_TO_FLAT / 2.0
    corner_r = NUT_FLAT_TO_FLAT / math.sqrt(3.0)
    nut_len = NUT_X_END - NUT_X_START

    # Mat cat hoc dai oc trong mat phang YZ:
    # Ranh mo ve mat +Y tu z = -corner_r toi +corner_r, y tu 0 toi NUT_SLOT_Y_MAX
    # Nua duoi la hinh luc giac (y tu 0 xuong -flat_half)
    pts = [
        V(NUT_X_START, NUT_SLOT_Y_MAX, corner_r),
        V(NUT_X_START, 0.0, corner_r),
        V(NUT_X_START, -flat_half, corner_r / 2.0),
        V(NUT_X_START, -flat_half, -corner_r / 2.0),
        V(NUT_X_START, 0.0, -corner_r),
        V(NUT_X_START, NUT_SLOT_Y_MAX, -corner_r),
        V(NUT_X_START, NUT_SLOT_Y_MAX, corner_r),
    ]
    pocket_wire = Part.makePolygon(pts)
    pocket_face = Part.Face(pocket_wire)
    pocket_solid = pocket_face.extrude(V(nut_len, 0, 0))

    part = part.cut(pocket_solid)

    # Don dep cac canh/mat thua neu co
    part = part.removeSplitter()

    return part


def run():
    print("Dang tao chi tiet Piston_rod_Shoulder...", flush=True)
    part = build_piston_rod()

    if not part.isValid():
        print("LOI: Part khong hop le (invalid shape)!", flush=True)
        sys.exit(1)

    solids = part.Solids
    if len(solids) != 1:
        print(f"LOI: So luong solid = {len(solids)}, can dung 1 solid!", flush=True)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    out_path = os.path.join(out_dir, OUTPUT_FILENAME)
    part.exportStep(out_path)
    print(f"Da xuat thanh cong: {out_path}", flush=True)
    print(f"BoundBox: {part.BoundBox}", flush=True)
    print(f"Volume: {part.Volume:.2f} mm3", flush=True)


run()
