# Phac dang 3 huong de flexi (chi de duyet anh, khong phai CAD). Chay: blender -b -P make_concepts.py -- <outdir>
import bpy, sys, math
from mathutils import Vector
out = sys.argv[sys.argv.index("--")+1]
W="#F7F2E6"; Y="#E8B33A"; R="#C8372D"; G="#2A2E33"
def hexc(h): 
    h=h.lstrip('#'); return tuple(pow(int(h[i:i+2],16)/255,2.2) for i in (0,2,4))+(1,)
mats={}
def mat(c):
    if c not in mats:
        m=bpy.data.materials.new(c); m.use_nodes=True
        b=m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value=hexc(c); b.inputs["Roughness"].default_value=0.45
        mats[c]=m
    return mats[c]
def bead(c,p,r):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=p)
    o=bpy.context.object; o.scale=r; o.data.materials.append(mat(c)); bpy.ops.object.shade_smooth()
def mir(c,p,r):
    bead(c,p,r)
    if abs(p[1])>0.01: bead(c,(p[0],-p[1],p[2]),r)
def ring(c,p,R_,r_,rot=(0,math.radians(90),0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R_,minor_radius=r_,location=p,rotation=rot,major_segments=48,minor_segments=16)
    o=bpy.context.object; o.data.materials.append(mat(c)); bpy.ops.object.shade_smooth()
def chain(c,pts,rs,sym=True):
    P=[];R_=[]
    for i in range(len(pts)):
        P.append(pts[i]);R_.append(rs[i])
        if i+1<len(pts):
            for t in (1/3,2/3):
                P.append(tuple(pts[i][k]*(1-t)+pts[i+1][k]*t for k in range(3)));R_.append(rs[i]*(1-t)+rs[i+1]*t)
    for p,r in zip(P,R_): (mir if sym else bead)(c,p,(r,r,r))

def goat_A():  # Mui tron: chibi, dung, dau to, 10 dot than + chan 2 dot
    mir(W,(66,0,64),(23,20,21)); mir(W,(86,0,57),(11,10,9)); mir(Y,(79,0,41),(4.5,4.5,9))
    mir(W,(60,26,70),(11,6,7)); chain(Y,[(57,9,86),(49,10,95),(40,10,98)],[6.5,5.8,5])
    mir(W,(38,0,57),(16,15,15)); ring(R,(38,0,57),16,3.5)
    for x,r in [(12,(22,20,19)),(-21,(21,19,18)),(-50,(20,18,17))]: mir(W,(x,0,50),r)
    mir(W,(-69,0,58),(8,7,7)); mir(Y,(-78,0,64),(5,5,5))
    for x in (20,-46):
        mir(W,(x,13,30),(9,8,10)); mir(Y,(x,13,8),(9.5,8.5,8))
def goat_B():  # Mui nui: cao, co dai, chan 3 dot, sung cong dai
    mir(W,(92,0,92),(18,15,14)); mir(W,(110,0,86),(10,8,8)); mir(Y,(106,0,70),(3.5,3.5,8))
    mir(W,(86,19,96),(10,5,6)); chain(Y,[(88,8,107),(80,9,116),(68,9,121),(56,9,117)],[6,5.6,5.2,4.8])
    for p in [(70,0,82),(52,0,72),(36,0,63)]: mir(W,p,(14,12,13))
    ring(R,(62,0,77),13.5,3.2,rot=(0,math.radians(65),0))
    for x,r in [(18,(19,17,16)),(-10,(19,17,16)),(-38,(18,16,15)),(-64,(16,14,13))]: mir(W,(x,0,50),r)
    chain(W,[(-80,0,52),(-92,0,58),(-98,0,67)],[7,6,5],sym=False)
    bead(Y,(-101,0,77),(5,5,5))
    for x in (24,-58):
        mir(W,(x,12,33),(7.5,6.5,9)); mir(W,(x,12,17),(7,6.2,8)); mir(Y,(x,12,5.5),(8.5,7.5,6))
def goat_C():  # Mui nam: nam sap, chan gap, sung xoan oc, 8 dot
    mir(W,(52,0,50),(25,22,23)); mir(W,(74,0,43),(12,11,9)); mir(Y,(67,0,26),(4.5,4.5,6))
    mir(W,(46,28,56),(12,6,8))
    import math as m
    pts=[];rs=[]
    for i in range(6):
        t=i/5*1.3*m.pi
        rad=18-i*2.2; pts.append((44-rad*0.2*m.cos(t)-2, 10+rad*0.35, 76+rad*m.sin(t)*0.0+ (rad*m.sin(t)))); rs.append(6.5-i*0.5)
    chain(Y,[(46,10,76),(40,13,86),(30,15,90),(21,14,85),(19,13,76),(26,12,72)],[7,6.5,6,5.5,5,4.5])
    mir(W,(32,0,32),(18,16,14)); ring(R,(30,0,43),17.5,3.2,rot=(0,math.radians(75),0))
    for x,r in [(8,(24,21,16)),(-24,(23,20,15)),(-50,(18,16,13))]: mir(W,(x,0,22),r)
    for x in (22,-38): mir(W,(x,22,9),(15,7,9))
    mir(Y,(-66,0,22),(6,6,6)); mir(W,(-60,0,24),(7,7,7))
    for x in (30,-30): mir(Y,(x,21,7),(7,6,6))

scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else "BLENDER_EEVEE_NEXT"
scene.render.resolution_x=1000; scene.render.resolution_y=800
scene.view_settings.view_transform="Standard"
w=bpy.data.worlds.new("w"); scene.world=w; w.use_nodes=True
bg=w.node_tree.nodes["Background"]; bg.inputs[0].default_value=hexc("#ECF1EF"); bg.inputs[1].default_value=0.9
def light(loc,e,sz):
    d=bpy.data.lights.new("l","AREA"); d.energy=e; d.size=sz
    o=bpy.data.objects.new("l",d); scene.collection.objects.link(o); o.location=loc
    o.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new("c"); cam.type='ORTHO'; cam.ortho_scale=225
co=bpy.data.objects.new("c",cam); scene.collection.objects.link(co); scene.camera=co
def snap(name,which,view):
    for o in list(bpy.data.objects):
        if o.type!='CAMERA': bpy.data.objects.remove(o,do_unlink=True)
    {"A":goat_A,"B":goat_B,"C":goat_C}[which]()
    # ground
    bpy.ops.mesh.primitive_plane_add(size=900,location=(0,0,0)); g=bpy.context.object; g.data.materials.append(mat("#B9C6C1"))
    for rot,e in [((math.radians(50),math.radians(10),math.radians(35)),2.4),((math.radians(60),0,math.radians(-140)),0.8)]:
        d=bpy.data.lights.new("s","SUN"); d.energy=e; d.angle=math.radians(12)
        o=bpy.data.objects.new("s",d); scene.collection.objects.link(o); o.rotation_euler=rot
    if view=="side": co.location=(0,-600,70); co.rotation_euler=(math.radians(90),0,0); cam.ortho_scale=225
    else: co.location=(0,0,600); co.rotation_euler=(0,0,0); cam.ortho_scale=225
    co.location.x={"A":6,"B":12,"C":9}[which]; cam.ortho_scale=250 if which=="B" else 225
    scene.render.filepath=f"{out}/{name}"; bpy.ops.render.render(write_still=True)
    for o in list(bpy.data.objects):
        if o.type=='LIGHT': bpy.data.objects.remove(o,do_unlink=True)
for k in "ABC":
    for v in ("side","top"): snap(f"{k}-{v}.png",k,v)
