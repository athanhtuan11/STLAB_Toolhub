# CU (13 buoc, gui qua RPC) - da THAY bang render_assembly_steps.py (32 buoc, kieu "thao tac", 2026-10-25). Giu de tham khao.
# Render anh huong dan lap rap (ASSEMBLY.md) trong FreeCAD GUI - gui noi dung file qua RPC (cong 9875).
# Moi buoc: chi tiet cua cac buoc truoc -> mo (trong suot), chi tiet MOI -> dac + to xanh (selection); anh b phong to chi tiet moi.
# Chi doi hien thi (Visibility/Transparency), xong tra lai nhu cu, KHONG Luu file. Ra: freecad/images/assembly/step-XX-{a,b}.png
import FreeCAD as App, FreeCADGui as Gui, fnmatch, json, os

P = r"D:/04_Stlab/04_STLAB_Toolhub/claude-workspace/maker/pushrod-arm/freecad/"
OUT = P + "images/assembly/"
STEPS = [  # (ma buoc, glob Label cac chi tiet MOI) - thu tu = thu tu lap trong ASSEMBLY.md
    ("01", ["Base_foot", "Base_housing"]),
    ("02", ["CB_Servo9g_360_turntable", "Pinion_m1_z10_turntable", "Battery_bay", "Receiver_riser", "CB_XA003_XA004_receiver"]),
    ("03", ["Base_deck", "Slide_ring", "Turntable", "Turntable_gear_m1_z60", "M2_5x10_gear*"]),
    ("04", ["M2_5x8_deck*"]),
    ("05", ["Turret_one_piece", "M2_5x6_turret*"]),
    ("06", ["Housing_*", "Pinion_WormWheel_*", "Worm_*", "CB_030_gearbox_*", "Pin_gearbox_*", "Washer_shaft_*", "M2_5x6_shaft_*", "Rack_*"]),
    ("07", ["Boom001", "Spacer_S", "Spacer_S001", "Pin_S", "Pin_S_*"]),
    ("08", ["Spacer_A", "Spacer_A001", "Pin_A", "Pin_A_*", "Pin_B", "Pin_B_*"]),
    ("09", ["Forearm_plate_L", "Forearm_plate_R", "Spacer_D", "Spacer_E", "Wrist_spacer", "M2_5x6_wrist_spacer*"]),
    ("10", ["Pin_E", "Pin_E_*"]),
    ("11", ["Pin_C", "Pin_C_*", "Pin_D", "Pin_D_*"]),
    ("12", ["Gripper_frame", "CB_Servo9g_180_gripper", "Servo_horn", "Jaw_*", "Pin_jaw2", "Spacer_jaw2", "Washer_pin",
            "M2_5x6_pin", "Gripper_top_plate", "M2_5x6_top*"]),
    ("13", ["M2_5x6_wrist", "M2_5x6_wrist00*"]),
]
doc = App.getDocument("pushrod_arm")
Gui.setActiveDocument(doc.Name)
gd = Gui.getDocument(doc.Name)
view = gd.ActiveView
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature")]
cu = {o.Name: (o.Visibility, o.ViewObject.Transparency) for o in parts}
buoc_cua = {}
for ma, globs in STEPS:
    for o in parts:
        if o.Name not in buoc_cua and any(fnmatch.fnmatch(o.Label, g) for g in globs):
            buoc_cua[o.Name] = ma
thieu = [o.Label for o in parts if o.Name not in buoc_cua]
os.makedirs(OUT, exist_ok=True)
anh = []
try:
    for ma, _ in STEPS:
        Gui.Selection.clearSelection()
        for o in parts:
            b = buoc_cua.get(o.Name)
            o.Visibility = b is not None and b <= ma
            if b is not None and b <= ma:
                o.ViewObject.Transparency = 0 if b == ma else 80
                if b == ma:
                    Gui.Selection.addSelection(o)
        for ten in ("a", "b"):  # a = toan canh; b = phong to vao chi tiet moi (vit, chot nho van thay ro)
            view.viewIsometric()
            if ten == "a":
                view.fitAll()
            else:
                Gui.SendMsgToActiveView("ViewSelection")
            f = OUT + "step-%s-%s.png" % (ma, ten)
            view.saveImage(f, 1600, 1200, "White")
            anh.append(os.path.basename(f))
finally:
    Gui.Selection.clearSelection()
    for o in parts:
        v, t = cu[o.Name]
        o.Visibility = v
        o.ViewObject.Transparency = t
    view.viewIsometric(); view.fitAll()
print(json.dumps({"anh": anh, "chi_tiet_khong_thuoc_buoc_nao": thieu, "UndoCount": doc.UndoCount}, ensure_ascii=False))
