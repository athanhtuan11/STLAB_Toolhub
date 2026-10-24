# Job headless (fc_job): test dong hoc - quet tu the bang chinh logic cua pushrod_arm_sim.FCMacro,
# kiem va cham giua cac cum (cap cua macro) + trong cum kep (ham mo/dong). Khong ghi .FCStd.
import FreeCAD as App, math, json, os, sys, time, types
P = r"D:\04_Stlab\04_STLAB_Toolhub\claude-workspace\maker\pushrod-arm\freecad"  # model + macro + rest
OUT = os.path.join(P, "check")  # ket qua (file sinh, khong len git)
os.makedirs(OUT, exist_ok=True)
JOB = os.environ.get("FC_JOB_DIR", OUT)
OUTJ = os.path.join(OUT, "kinematics-test%s.json" % ("-brep" if os.environ.get("KT_BREP") == "1" else ""))
t0 = time.time()
def log(*a):
    print(*a, flush=True)
    with open(os.path.join(OUT, "kinematics-test.log"), "a", encoding="utf-8") as f:
        f.write(" ".join(str(x) for x in a) + "\n")
try:
    App.openDocument(os.path.join(P, "pushrod_arm.FCStd"))
    src = open(os.path.join(P, "pushrod_arm_sim.FCMacro"), encoding="utf-8").read()
    src = src.split("class Panel", 1)[0]
    # bo import GUI/Qt: chay trong freecadcmd
    src = src.replace("import FreeCAD as App, FreeCADGui as Gui, math, json, os", "import FreeCAD as App, math, json, os")
    i0 = src.index("try:\n    from PySide"); i1 = src.index("DOC = ")
    src = src[:i0] + src[i1:]
    G = {"__name__": "sim", "Gui": types.SimpleNamespace(updateGui=lambda: None)}
    exec(compile(src, "pushrod_arm_sim.FCMacro", "exec"), G)
    set_pose, check_c, OBJ, ST = G["set_pose"], G["check_collisions"], G["OBJ"], G["STATE"]
    # luoi nhanh (robotics-cad/scripts/fast_collide.py); "brep=1" tren dong lenh/env -> boolean B-rep cu (doi chieu)
    BREP = os.environ.get("KT_BREP") == "1" or "brep=1" in sys.argv
    fast = None if BREP else G["fast_collider"]()
    def check(): return check_c(fast)
    LMIN, LMAX, L1MAX, L1_0, L2_0 = G["LMIN"], G["LMAX"], G["L1MAX"], G["L1_0"], G["L2_0"]
    res = {"rest": {"L1": L1_0, "L2": L2_0}, "arm": [], "grip": [], "unreachable": []}

    # 1) canh tay: luoi tu the (yaw 0 va 90), kep mo het
    L1s = [LMIN, (LMIN + L1MAX) / 2, L1MAX]
    L2s = [LMIN, LMIN + (LMAX - LMIN) / 3, LMIN + 2 * (LMAX - LMIN) / 3, LMAX]
    for yaw in (0, 90):
        for L1 in L1s:
            for L2 in L2s:
                ok = set_pose(yaw, L1, L2, -55, update=False)
                if not ok: res["unreachable"].append([yaw, L1, L2]); continue
                h = check()
                res["arm"].append({"yaw": yaw, "L1": round(L1, 1), "L2": round(L2, 1), "phi": round(ST["phi"], 1),
                                   "psi": round(ST["psi"], 1), "hits": h})
                log("arm", yaw, round(L1, 1), round(L2, 1), "->", h or "OK", round(time.time() - t0))

    # 2) kep: quet goc tai tu the goc
    J1 = ["Jaw_1_driven_by_servo", "Jaw_1_driven_by_servo_TPU_pad", "Servo_horn"]
    J2 = ["Jaw_2_idler", "Jaw_2_idler_TPU_pad"]
    FIX = ["Gripper_frame", "Gripper_top_plate", "CB_Servo9g_180_gripper", "Forearm_plate_L", "Forearm_plate_R", "Wrist_spacer"]
    PIVOT2 = ["Pin_jaw2", "Spacer_jaw2", "Washer_pin", "M2_5x6_pin"]
    EXPECT = {("Servo_horn", "CB_Servo9g_180_gripper")}
    gfast = None
    if fast is not None:
        import fast_collide
        gfast = fast_collide.Collider({l: OBJ[l] for l in J1 + J2 + FIX + PIVOT2 if l in OBJ})
    def common(a, b):
        if gfast is not None: return gfast.volume(a, b) or 0.0
        sa, sb = OBJ[a].Shape, OBJ[b].Shape
        bb = sa.BoundBox; bb.enlarge(0.5)
        if not bb.intersect(sb.BoundBox): return 0.0
        try: return sa.common(sb).Volume
        except Exception: return -1.0
    for gdeg in (-55, -40, -26, -13, 0, 3):
        set_pose(0, L1_0, L2_0, gdeg, update=False)
        hits = []
        for a in J1:
            for b in J2 + FIX + PIVOT2:
                if (a, b) in EXPECT: continue
                v = common(a, b)
                if v > 0.5 or v < 0: hits.append("%s x %s: %.1f mm3" % (a, b, v))
        for a in J2:
            for b in FIX:
                v = common(a, b)
                if v > 0.5 or v < 0: hits.append("%s x %s: %.1f mm3" % (a, b, v))
        p1, p2 = OBJ["Jaw_1_driven_by_servo_TPU_pad"].Shape, OBJ["Jaw_2_idler_TPU_pad"].Shape
        # min_gap cua manifold3d: ban kinh tim lon (50 mm) tra sai/treo -> tim trong 20 mm, xa hon thi B-rep
        gap = gfast.gap("Jaw_1_driven_by_servo_TPU_pad", "Jaw_2_idler_TPU_pad", 20.0) if gfast else None
        if gap is None: gap = p1.distToShape(p2)[0]
        res["grip"].append({"grip_deg": gdeg, "pad_gap_mm": round(gap, 2), "hits": hits})
        log("grip", gdeg, "gap %.2f" % gap, "->", hits or "OK", round(time.time() - t0))
    res["time_s"] = round(time.time() - t0); res["method"] = "brep" if BREP else "mesh"
    json.dump(res, open(OUTJ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("DONE", res["time_s"])
except Exception:
    import traceback; log("FAIL", traceback.format_exc()); raise
