# Job headless (fc_job): xi-lanh v3 - N20 LA00x truc thang (STEP thu vien) + truc vit/banh vit in, sua horn kep.
import FreeCAD as App, Part, math, json, os, shutil, time
from FreeCAD import Vector as V
JOB=os.environ.get("FC_JOB_DIR",r"D:\06_FreeCAD\pushrod_arm\_work")
P=r"D:\06_FreeCAD\pushrod_arm"; FC=os.path.join(P,"pushrod_arm.FCStd")
LIB=r"D:\04_Stlab\04_STLAB_Toolhub\claude-workspace\community"
def log(*a):
    print(*a, flush=True)
    with open(os.path.join(JOB,"progress.txt"),"a",encoding="utf-8") as f: f.write(" ".join(str(x) for x in a)+"\n")
t0=time.time()
os.makedirs(os.path.join(P,"_backup"),exist_ok=True)
shutil.copy2(FC,os.path.join(P,"_backup","pushrod_arm_truoc_xilanh_v3.FCStd"))
doc=App.openDocument(FC)
OBJ={o.Label:o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
GRP={o.Label:o for o in doc.Objects if o.isDerivedFrom("App::DocumentObjectGroup")}
A20=math.radians(20)
def invf(a): return math.tan(a)-a
def gear_pts(cx,cz,z,m,x=0.0,ph=0.0,bl=0.15,n_=8):
    rp=m*z/2; rb=rp*math.cos(A20); ra=rp+m*(1+x); rf=rp-m*(1.25-x); psi=(math.pi/2+2*x*math.tan(A20))/z-bl/(2*rp); r0=max(rb,rf)
    def th(r): return psi+invf(A20)-invf(math.acos(min(1,rb/r)))
    pts=[]
    for i in range(z):
        c=math.radians(ph)+2*math.pi*i/z; rs=[r0+(ra-r0)*k/n_ for k in range(n_+1)]
        if rf<rb: pts.append((rf,c-th(rb)))
        pts+=[(r,c-th(r)) for r in rs]+[(r,c+th(r)) for r in reversed(rs)]
        if rf<rb: pts.append((rf,c+th(rb)))
        a0=c+th(r0); a1=c+2*math.pi/z-th(r0); pts+=[(rf,a0+(a1-a0)*k/3) for k in range(1,3)]
    return [(cx+r*math.cos(a),cz+r*math.sin(a)) for r,a in pts]
def wire_xz(pts,y): return Part.makePolygon([V(x,y,z) for x,z in pts]+[V(pts[0][0],y,pts[0][1])])
def face_xz(pts,y0,y1): return Part.Face(wire_xz(pts,y0)).extrude(V(0,y1-y0,0))
def ycyl(p,r,y0,y1): return Part.makeCylinder(r,y1-y0,V(p[0],y0,p[1]),V(0,1,0))
def xcyl(r,x0,x1,y,z): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def box(x0,x1,y0,y1,z0,z1):
    z0,z1=sorted((z0,z1)); return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
# ---------------- worm / wheel (elbow config: worm above wheel) ----------------
XP,ZC,ZW,YW,Y0,Y1=60.0,8.25,20.25,9.4,7.4,11.4
FACE=53.9
def worm_outer(x0,x1,bl=0.15):
    L=x1-x0; lead=math.pi; hel=Part.makeHelix(lead,L+2*lead,2.75,0,False); hel.translate(V(0,0,-lead))
    tp=math.tan(A20); h0=(math.pi/2-bl)/2; hr=h0+1.25*tp; ht=h0-1.0*tp
    pr=Part.makePolygon([V(2.55,0,-lead-hr),V(5.0,0,-lead-ht),V(5.0,0,-lead+ht),V(2.55,0,-lead+hr),V(2.55,0,-lead-hr)])
    sw=Part.Wire(hel).makePipeShell([pr],True,True)
    w=sw.fuse(Part.makeCylinder(2.75,L+2*lead,V(0,0,-lead))).common(Part.makeCylinder(6,L,V(0,0,0))).removeSplitter()
    w.rotate(V(0,0,0),V(0,1,0),90); w.translate(V(x0,YW,ZW)); return w
WX0,WX1=FACE+2.3,FACE+9.95
WO=worm_outer(WX0,WX1)
# bore: round Ø3.2 over the round part of the LA002 shaft (first 4.0 mm from gearbox face), D-bore (flat 1.1) after
bore=xcyl(1.6,WX0-0.1,FACE+4.2,YW,ZW).fuse(xcyl(1.6,FACE+4.2,WX1+0.1,YW,ZW).cut(box(FACE+4.2,WX1+0.2,YW-2,YW+2,ZW+1.1,ZW+3)))
WORM=WO.cut(bore).removeSplitter()
throat=xcyl(5.3,40,80,YW,ZW)
def wheel(tw,ph,bl=0.25):
    g=Part.makeLoft([wire_xz(gear_pts(XP,ZC,16,1,0,ph,bl),Y0),wire_xz(gear_pts(XP,ZC,16,1,0,ph+tw/2,bl),(Y0+Y1)/2),
                     wire_xz(gear_pts(XP,ZC,16,1,0,ph+tw,bl),Y1)],True,True)
    return g.cut(throat)
ca=V(0,YW,ZW); CA=V(1,0,0); wa=V(XP,0,ZC); WA=V(0,1,0)
def mesh_worst(G,steps=12,stop=None):
    worst=0
    for k in range(steps):
        th=k*360.0/steps; w2=WO.copy(); w2.rotate(ca,CA,th); g2=G.copy(); g2.rotate(wa,WA,-th/16)
        worst=max(worst,w2.common(g2).Volume)
        if stop is not None and worst>=stop: break
    return worst
best=None
for tw in (3.58,-3.58):
    for i in range(30):
        ph=i*0.75; w=mesh_worst(wheel(tw,ph),12,best[0] if best else None)
        if best is None or w<best[0]: best=(w,tw,ph); log("search",round(w,3),tw,ph)
log("best",best, round(time.time()-t0),"s")
WHEEL=wheel(best[1],best[2])
fine=[]
for k in range(25):
    th=k*15.0; w2=WORM.copy(); w2.rotate(ca,CA,th); g2=WHEEL.copy(); g2.rotate(wa,WA,-th/16)
    fine.append((th,round(w2.common(g2).Volume,4),round(w2.distToShape(g2)[0],3)))
log("fine",fine)
# ---------------- motor = library N20 (Pololu, same mould as LA002) + library SH rear board ----------------
N20=Part.read(LIB+r"\n20-motor\models\n20-tieu-chuan\n20-tieu-chuan.step")
SHB=Part.read(LIB+r"\n20-motor\models\bo-cam-jst-sh-phia-sau\bo-cam-jst-sh-phia-sau.step")
SHB.rotate(V(0,0,0),V(1,0,0),180); SHB.translate(V(0,0,-16.3))     # board at 16.3 mm behind gearbox face, connector rearward
MOT0=Part.makeCompound([N20,SHB])
report={"motor_check":{}}
for t,zs in (("Shoulder",-1),("Elbow",1)):
    PL=OBJ["Rack_"+t].Placement
    def loc(o):
        s=o.Shape.copy(); s.Placement=PL.inverse().multiply(s.Placement); return s
    def glob(s):
        s=s.copy(); s.Placement=PL.multiply(s.Placement); return s
    zc=zs*ZC; zw=zs*ZW
    wheel_=WHEEL.copy(); worm_=WORM.copy()
    if zs<0:
        for s_ in (wheel_,worm_): s_.rotate(V(XP,0,ZC),V(0,1,0),180); s_.translate(V(0,0,-2*ZC))
    pin=loc(OBJ["Pinion_m1_z10_"+t]).common(ycyl((XP,zc),7.0,-2.5,2.5))
    gs=pin.fuse([ycyl((XP,zc),4.0,-2.5,2.5),ycyl((XP,zc),3.0,-5.9,-2.5),ycyl((XP,zc),6.2,2.5,6.2),
                 ycyl((XP,zc),7.5,6.2,6.8),ycyl((XP,zc),6.2,6.8,7.45),wheel_])
    gs=gs.cut(ycyl((XP,zc),1.1,-5.95,-0.9)).removeSplitter()
    H=loc(OBJ["Housing_"+t]).common(box(-30,110,-30,6.0,-50,50))
    H=H.fuse(ycyl((XP,zc),7.0,-6.0,-3.2))
    H=H.fuse([box(31.0,FACE,1.6,17.2,zs*13.45,zs*27.05),box(FACE,FACE+2.0,1.6,17.2,zs*13.45,zs*27.05),
              box(31.0,50.0,-6.0,6.0,zs*6.0,zs*14.0)])
    H=H.cut(box(30.9,FACE+0.05,3.2,15.6,zs*15.05,zs*25.45))
    H=H.cut(xcyl(2.2,FACE-0.4,FACE+2.6,YW,zw))
    for yy in (YW-4.5,YW+4.5): H=H.cut(xcyl(0.9,FACE-0.4,FACE+2.6,yy,zw))
    H=H.cut(ycyl((XP,zc),3.2,-7.0,-3.0)).cut(ycyl((XP,zc),6.4,2.9,7.0)).cut(ycyl((XP,zc),9.6,6.9,11.95))
    H=H.cut(xcyl(5.6,FACE+2.05,64.6,YW,zw))
    for zz in (zs*14.25,zs*26.25): H=H.cut(ycyl((40.0,zz),1.0,0.0,18.0))
    H=H.removeSplitter()
    M=App.Matrix(0,0,1,FACE-9.0, 1,0,0,YW, 0,1,0,zw, 0,0,0,1)
    mot=MOT0.copy().transformGeometry(M)
    wsh=ycyl((XP,zc),4.5,-7.2,-6.0).cut(ycyl((XP,zc),1.35,-7.3,-5.9))
    scr=ycyl((XP,zc),2.25,-8.7,-7.2).fuse(ycyl((XP,zc),1.25,-7.2,-1.2))
    env=box(FACE-28.9,FACE,-6.0+YW,6.0+YW,zw-5.0,zw+5.0)          # LA002 envelope incl. rear SH board (box, per skill)
    rk=loc(OBJ["Rack_"+t])
    chk={"H_valid":H.isValid(),"H_solids":len(H.Solids),"gs_valid":gs.isValid(),"gs_solids":len(gs.Solids),
         "env_x_H":round(env.common(H).Volume,3),"worm_x_H":round(worm_.common(H).Volume,3),"gs_x_H":round(gs.common(H).Volume,3),
         "gs_gap_H":round(gs.distToShape(H)[0],3),"worm_x_motor":round(worm_.common(mot).Volume,3),"gs_x_motor":round(gs.common(mot).Volume,3),
         "worm_x_gs":round(worm_.common(gs).Volume,3),"rack_x_gs":round(rk.common(gs).Volume,3),"rack_gap_gs":round(rk.distToShape(gs)[0],3),
         "wheel_gap_motor":round(gs.distToShape(env)[0],3)}
    report["motor_check"][t]=chk; log(t,chk)
    # write into document
    def put(lbl,shape,grp):
        o=OBJ.get(lbl)
        if o is None:
            o=doc.addObject("Part::Feature",lbl); o.Label=lbl; GRP[grp].addObject(o); OBJ[lbl]=o
        o.Placement=App.Placement(); o.Shape=glob(shape); return o
    g="PushRod_"+t
    put("Housing_"+t,H,g); put("Pinion_WormWheel_"+t,gs,g); put("Worm_"+t,worm_,g); put("CB_N20_LA003_"+t,mot,g)
    put("Washer_shaft_"+t,wsh,g); put("M2_5x6_shaft_"+t,scr,g)
    for old in ("Pinion_m1_z10_"+t,"CB_N20_worm_LA008_"+t):
        if old in OBJ: doc.removeObject(OBJ[old].Name); OBJ.pop(old)
# ---------------- gripper: horn oriented like the real part (socket toward servo), keyed pocket in jaw 1 ----------------
E0=(96.41814145600076,194.90666646784498)
PG=App.Placement(V(E0[0]+130*math.cos(math.radians(-30)),0,E0[1]+130*math.sin(math.radians(-30))+4),App.Rotation(V(0,1,0),30))
J1=(28,7.5)
def hull2d(pts):
    pts=sorted(set((round(x,4),round(z,4)) for x,z in pts))
    def cr(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo=[];up=[]
    for p in pts:
        while len(lo)>=2 and cr(lo[-2],lo[-1],p)<=0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up)>=2 and cr(up[-2],up[-1],p)<=0: up.pop()
        up.append(p)
    return lo[:-1]+up[:-1]
def hull_poly(items,y0,y1,n=64):
    pts=[]
    for p,r in items: pts+=[(p[0]+r*math.cos(2*math.pi*k/n),p[1]+r*math.sin(2*math.pi*k/n)) for k in range(n)]
    return face_xz(hull2d(pts),y0,y1)
HORN=Part.read(LIB+r"\cyberbrick-official\models\pg002-pg001-9g-servo-motor-with-clutch-protection\9g-servo-motor-with-clutch-protection-half-arm1.step")
th=math.radians(14); c,s=math.cos(th),math.sin(th)
horn=HORN.copy().transformGeometry(App.Matrix(c,s,0,28-20*s, 0,0,1,-2.6, s,-c,0,7.5+20*c, 0,0,0,1))
tip=(J1[0]+14.15*c,J1[1]+14.15*s)
j=face_xz(gear_pts(J1[0],J1[1],15,1.0,0.0,-90,0.15,10),-2.6,2.6).fuse(hull_poly([(J1,5.5),((50,13),3),((68,5),2.4)],-2.6,2.6))
j=j.cut(hull_poly([((60,6.6),1.6),((68,4.4),1.3)],-3.0,3.0))
j=j.cut(hull_poly([(J1,3.85),(tip,2.25)],-2.7,-0.85)).cut(ycyl(J1,3.85,-2.7,1.75)).cut(ycyl(J1,2.4,1.6,2.8)).removeSplitter()
for lbl,sh in (("Servo_horn",horn),("Jaw_1_driven_by_servo",j)):
    sh=sh.copy(); sh.Placement=PG.multiply(sh.Placement); OBJ[lbl].Placement=App.Placement(); OBJ[lbl].Shape=sh
sv=OBJ["CB_Servo9g_180_gripper"].Shape; hz=OBJ["Servo_horn"].Shape; jz=OBJ["Jaw_1_driven_by_servo"].Shape
report["gripper"]={"jaw1_valid":jz.isValid(),"jaw1_solids":len(jz.Solids),"horn_x_jaw1":round(hz.common(jz).Volume,3),
                   "horn_x_servo_spline":round(hz.common(sv).Volume,3),"horn_x_frame":round(hz.common(OBJ["Gripper_frame"].Shape).Volume,3)}
log("gripper",report["gripper"])
report["mesh_search_best"]=best; report["mesh_fine"]=fine
doc.recompute(); doc.saveAs(FC)
rp=os.path.join(P,"pushrod_arm_rest.json"); rest=json.load(open(rp))
for o in doc.Objects:
    if o.isDerivedFrom("Part::Feature"): rest[o.Name]=[list(o.Placement.Base),list(o.Placement.Rotation.Q)]
for n in list(rest):
    if doc.getObject(n) is None: rest.pop(n)
json.dump(rest,open(rp,"w"))
WHEEL.exportBrep(os.path.join(P,"_work","wheel_z16_light.brep")); WORM.exportBrep(os.path.join(P,"_work","worm_LA002.brep"))
report["time_s"]=round(time.time()-t0)
json.dump(report,open(os.path.join(JOB,"report.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
log("DONE",report["time_s"])
