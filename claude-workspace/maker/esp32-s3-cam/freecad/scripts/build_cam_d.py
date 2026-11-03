import json, math, os, shutil, sys, time
import FreeCAD as App, Part, Mesh
HERE=os.path.dirname(os.path.abspath(__file__)); PROJ=os.path.dirname(HERE)
sys.path.insert(0,os.path.join(PROJ,'..','..','..','tools','robotics-cad','scripts'))
from cad_lib import box,cyl,rrect
P=json.loads(open(os.environ.get('CAMD_PARAMS',os.path.join(PROJ,'params.json')),encoding='utf-8').read())
OUT=os.environ.get('CAMD_OUT',os.path.join(HERE,'cam_d.FCStd'))
T,M,S,N,U,D=[P[k] for k in ('than','mat_truoc','mach','truc_nghieng','khung_u','de_xoay')]; K=P['khe_nhiet']; USB=P['usb']; C=P['coupon']
zd=D['de_cao']-D['lom_sau']+D['dia_day']; zp=zd+N['cao_tam_tren_dia']; y0=-(T['d']+M['t'])/2+M['t']; yp=y0+.5+S['cam_cao_tren_pcb']; zl=zp+S['pcb_h']/2-S['ong_kinh_cach_canh_tren']
doc=App.newDocument('cam_d')
def fuse(*a):
 s=a[0]
 for x in a[1:]: s=s.fuse(x)
 return s.removeSplitter()
def cut(s,*a): return s.cut(fuse(*a)).removeSplitter()
def add(n,s,c=None):
 o=doc.addObject('Part::Feature',n); o.Label=n; o.Shape=s
 if c and o.ViewObject:o.ViewObject.ShapeColor=c
 return o
def hexcut(flat,axis,span,at):
 r=flat/math.sqrt(3); pts=[]
 for i in range(6):
  a=math.radians(i*60); u,v=at[0]+r*math.cos(a),at[1]+r*math.sin(a)
  pts.append(App.Vector(span[0],u,v) if axis=='x' else App.Vector(u,v,span[0]))
 pts.append(pts[0]); return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(span[1]-span[0],0,0) if axis=='x' else App.Vector(0,0,span[1]-span[0]))
def text_solid(txt,h,depth):
 # glyphs in XY plane centred at origin, z 0..depth
 font=M.get('font')
 if not font or not os.path.isfile(font): raise RuntimeError('font missing')
 parts=[]
 for g in Part.makeWireString(txt,font,h):
  ws=sorted(g,key=lambda w:-Part.Face(w).Area if w.isClosed() else 0)
  if not ws: continue
  f=Part.Face(ws[0])
  for w in ws[1:]: f=f.cut(Part.Face(w))
  parts.append(f.extrude(App.Vector(0,0,depth)))
 if not parts: raise RuntimeError('no glyph')
 sh=fuse(*parts); b=sh.BoundBox; sh.translate(App.Vector(-(b.XMin+b.XMax)/2,-(b.YMin+b.YMax)/2,-b.ZMin)); return sh
# Body hollow enclosure, open front.
body=rrect('y',(y0,y0+T['d']),(T['w']/2,T['h']/2),T['r_goc'],(0,zp)).cut(rrect('y',(y0-.1,y0+T['d']-T['thanh']),(T['w']/2-T['thanh'],T['h']/2-T['thanh']),T['r_goc']-T['thanh'],(0,zp)))
extra=[]; holes=[]; ov=.5; k=S['khe_moi_ben']; wi=T['w']/2-T['thanh']; hi=T['h']/2-T['thanh']; yr=y0+T['d']-T['thanh']
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*(T['w']/2-M['vit_cach_canh']); z=zp+sz*(T['h']/2-M['vit_cach_canh'])
  extra.append(cyl(M['tru_vit_d']/2,'y',(y0,y0+M['tru_vit_sau']),(x,z)))
  extra.append(box(x=tuple(sorted((x,sx*(wi+ov)))),y=(y0,y0+M['tru_vit_sau']),z=tuple(sorted((z,zp+sz*(hi+ov))))))
  holes.append(cyl(M['vit_m25_tu_ren']/2,'y',(y0-.1,y0+M['tru_vit_sau']),(x,z)))
 for za,zb in ((zp+6,zp+18),(zp-18,zp-6)):
  extra.append(box(x=tuple(sorted((sx*(wi+ov),sx*(S['pcb_w']/2+k)))),y=(yp,yp+S['stack_t']),z=(za,zb)))
 extra.append(box(x=tuple(sorted((sx*(S['pcb_w']/2-5.5),sx*(S['pcb_w']/2-2.5)))),y=(yp+S['stack_t']+k,yr+ov),z=(zp-S['pcb_h']/2,zp+S['pcb_h']/2)))
 for sz in (-1,1):
  zin=zp+sz*(S['pcb_h']/2+k); zw=zp+sz*(hi+ov)
  xc=sx*(S['pcb_w']/2-2.5); yc=yp+S['stack_t']-2
  extra.append(box(x=(xc-1.5,xc+1.5),y=(yc-1.5,yc+1.5),z=tuple(sorted((zin,zw)))))
 xi=sx*(wi+ov); xo=sx*(wi-N['tru_than_dai']); extra.append(cyl(N['tru_than_d']/2,'x',tuple(sorted((xi,xo))),(0,zp)))
 holes.append(hexcut(N['dai_oc_s'],'x',tuple(sorted((xo-sx*.01,xo+sx*N['dai_oc_sau']))),(0,zp)))
holes += [cyl(N['m3_xuyen']/2,'x',(-T['w']/2-.1,T['w']/2+.1),(0,zp))]
holes.append(rrect('z',(zp-T['h']/2-.1,zp-T['h']/2+T['thanh']+.1),(USB['o_rong_x']/2,USB['o_sau_y']/2),USB['bo_mep'],(0,yp+S['stack_t']-USB['o_sau_y']/2)))
for x in (-21,-17.5,-14,14,17.5,21): holes.append(box(x=(x-K['rong']/2,x+K['rong']/2),y=(yp+2,yp+2+K['dai']),z=(zp-T['h']/2-.1,zp-T['h']/2+T['thanh']+.1)))
for x in (-10,-6,-2,2,6,10): holes.append(box(x=(x-K['rong']/2,x+K['rong']/2),y=(y0+3,y0+3+K['dai']),z=(zp+T['h']/2-T['thanh']-.1,zp+T['h']/2+.1)))
body=cut(fuse(body,*extra),*holes); add('Body',body,(.92,.92,.92))
# Bezel with optical window, decorative counterbore, LEDs and screw holes.
bez=rrect('y',(y0-M['t'],y0),(T['w']/2,T['h']/2),T['r_goc'],(0,zp)); bh=[cyl(M['lo_ong_kinh_d']/2,'y',(y0-M['t']-.1,y0+.1),(0,zl)),cyl(M['vong_trang_tri_d']/2,'y',(y0-M['t']-.1,y0-M['t']+M['vong_trang_tri_sau']),(0,zl))]
zled=zl-M['den_duoi_ong_kinh']
for sx in (-1,1): bh.append(cyl(M['den_d']/2,'y',(y0-M['t']+M['den_da_mong'],y0+.1),(sx*M['den_cach_nhau']/2,zled)))
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*(T['w']/2-M['vit_cach_canh']); z=zp+sz*(T['h']/2-M['vit_cach_canh']); bh.append(cyl(M['vit_m25_xuyen']/2,'y',(y0-M['t']-.1,y0+.1),(x,z)))
  bh.append(Part.makeCone(2.5,M['vit_m25_xuyen']/2,2.5-M['vit_m25_xuyen']/2,App.Vector(x,y0-M['t'],z),App.Vector(0,1,0)))
bez=cut(bez,*bh)
try:
 t=text_solid(M['chu'],M['chu_cao'],M['chu_sau']+.1); t.rotate(App.Vector(0,0,0),App.Vector(1,0,0),90)
 t.translate(App.Vector(0,y0-M['t']+M['chu_sau'],zled-M['chu_duoi_den'])); bez=bez.cut(t).removeSplitter()
except Exception as e: print('WARNING: text omitted: %s'%e)
st=[]
for sx in (-1,1):
 for sz in (-1,1): st.append(cyl(1.25,'y',(y0-1,yp-S['khe_moi_ben']),(sx*(S['pcb_w']/2-1.5),zp+sz*(S['pcb_h']/2-1.5))))
bez=fuse(bez,*st); add('Bezel',bez,(.08,.08,.08))
# U frame and pivot bores.
xi=T['w']/2+N['khe_tay_than']; arms=[]; ucut=[]
for sx in (-1,1):
 x=sx*xi; xe=x+sx*U['tay_day']; a=box(x=tuple(sorted((x,xe))),y=(-U['tay_sau_y']/2,U['tay_sau_y']/2),z=(zd-1,zd+U['tay_cao']))
 ed=[e for e in a.Edges if abs(e.BoundBox.XLength-U['tay_day'])<1e-6 and e.BoundBox.ZMin>zd+U['tay_cao']-1e-6]
 a=a.makeFillet(3,ed); arms.append(a)
 ucut.append(cyl(N['m3_xuyen']/2,'x',tuple(sorted((x-sx*.1,xe+sx*.1))),(0,zp)))
 ucut.append(cyl(N['loc_dau_vit_d']/2,'x',tuple(sorted((xe-sx*N['loc_dau_vit_sau'],xe+sx*.1))),(0,zp)))
disc=cyl(D['dia_d']/2,'z',(zd-D['dia_day'],zd)); uf=fuse(disc,*arms)
uf=cut(uf,cyl(D['lo_dia_d']/2,'z',(zd-D['dia_day']-.1,zd+.1)),cyl(D['loc_dia_d']/2,'z',(zd-D['loc_dia_sau'],zd+.1)),*ucut); add('U_frame',uf,(.2,.55,.82))
# Base and pin cap.
# R2 fillet as an 8-segment revolved profile (cones): a true torus gives a loose BoundBox (gate checks XLength).
Rb=D['de_d']/2; hb=D['de_cao']; rf=2.0; pr=[(0,0),(Rb,0),(Rb,hb-rf)]+[(Rb-rf+rf*math.cos(math.radians(a)),hb-rf+rf*math.sin(math.radians(a))) for a in range(11,90,11)]+[(Rb-rf,hb),(0,hb)]
base=Part.Face(Part.makePolygon([App.Vector(px,0,pz) for px,pz in pr]+[App.Vector(0,0,0)])).revolve(App.Vector(0,0,0),App.Vector(0,0,1),360)
base=cut(base,cyl(D['lom_d']/2,'z',(D['de_cao']-D['lom_sau'],D['de_cao']+.1))); floor=D['de_cao']-D['lom_sau']; ptop=zd-D['loc_dia_sau']+D['khe_doc']; base=fuse(base,cyl(D['chot_d']/2,'z',(floor-1,ptop)))
bc=[cyl(M['vit_m25_tu_ren']/2,'z',(ptop-8,ptop+.1))]
for sx in (-1,1):
 x=sx*D['lo_khoa_cach']/2; bc += [cyl(D['lo_khoa_d']/2,'z',(-.1,D['de_cao']+.1),(x,0)),Part.makeCone(D['lo_khoa_dau_d']/2,D['lo_khoa_d']/2,(D['lo_khoa_dau_d']-D['lo_khoa_d'])/2,App.Vector(x,0,floor),App.Vector(0,0,-1))]
base=cut(base,*bc); add('Base',base,(.2,.55,.82)); capz=ptop; cap=cut(cyl(D['nap_chot_d']/2,'z',(capz,capz+D['nap_chot_day'])),cyl(M['vit_m25_xuyen']/2,'z',(capz-.1,capz+D['nap_chot_day']+.1))); add('Pin_cap',cap,(.2,.55,.82))
add('Ref_Stack',box(x=(-S['pcb_w']/2,S['pcb_w']/2),y=(yp,yp+S['stack_t']),z=(zp-S['pcb_h']/2,zp+S['pcb_h']/2))); add('Ref_Cam',box(x=(-4.25,4.25),y=(y0+.5,y0+4.7),z=(zl-4.25,zl+4.25)))
for sx,n in ((-1,'Ref_Screw_L'),(1,'Ref_Screw_R')): add(n,cyl(1.5,'x',tuple(sorted((sx*(xi+U['tay_day']-N['loc_dau_vit_sau']),sx*(xi+U['tay_day']-N['loc_dau_vit_sau'])-sx*12))),(0,zp)))
# Coupon and ring.
c=box(x=(-35,35),y=(-17,17),z=(0,4)); xs=(-23,0,23)
for x,d in zip(xs,C['m3_xuyen']): c=cut(c,cyl(d/2,'z',(-.1,4.1),(x,-8)))
for x,d in zip(xs,C['dai_oc_s']): c=cut(c,hexcut(d,'z',(1.4,4.1),(x,-8)),cyl(1.7,'z',(-.1,4.1),(x,-8)))
for x,d in zip(xs,C['lo_ong_kinh']): c=cut(c,cyl(d/2,'z',(-.1,4.1),(x,8)))
for x,d in zip((-10,10),C['den_da_mong']): c=cut(c,cyl(1.7,'z',(d,4.1),(x,0)))
c=fuse(c,cyl(4,'z',(3.9,10),(30,0))); fw=S['pcb_w']+2*S['khe_moi_ben']; fh=S['pcb_h']+2*S['khe_moi_ben']; frame=box(x=(34.5,34.5+fw+2.4),y=(-fh/2-1.2,fh/2+1.2),z=(0,5)).cut(box(x=(35.7,35.7+fw),y=(-fh/2,fh/2),z=(-.1,5.1))); c=fuse(c,frame)
try:
 for (lst,yy) in ((C['m3_xuyen'],-14.5),(C['lo_ong_kinh'],14.5)):
  for xx,d in zip(xs,lst):
   t=text_solid('%g'%d,3,.5); t.translate(App.Vector(xx,yy,3.6)); c=c.cut(t)
 c=c.removeSplitter()
except Exception as e: print('WARNING: coupon text omitted: %s'%e)
add('Coupon',c); add('Coupon_ring',cut(cyl(7.5,'z',(0,4)),cyl(D['lo_dia_d']/2,'z',(-.1,4.1))))
doc.recompute(); os.makedirs(os.path.dirname(OUT) or '.',exist_ok=True)
if os.path.exists(OUT):
 d=os.path.join(os.path.dirname(OUT),'backup'); os.makedirs(d,exist_ok=True); shutil.copy2(OUT,os.path.join(d,'cam_d.%s.FCStd'%time.strftime('%Y%m%d-%H%M%S')))
doc.saveAs(OUT)
# Export body laid on its back; bezel on its front; other parts on flat bottom.
stldir=os.path.join(os.path.dirname(OUT),'stl'); os.makedirs(stldir,exist_ok=True)
for nm,label,ang in [('body','Body',-90),('bezel','Bezel',90),('u_frame','U_frame',0),('base','Base',0),('pin_cap','Pin_cap',0),('coupon','Coupon',0),('coupon_ring','Coupon_ring',0)]:
 sh=doc.getObjectsByLabel(label)[0].Shape.copy()
 if ang: sh.rotate(App.Vector(0,0,0),App.Vector(1,0,0),ang)
 bb=sh.BoundBox; sh.translate(App.Vector(0,0,-bb.ZMin)); ob=add('Export_'+nm,sh); Mesh.export([ob],os.path.join(stldir,nm+'.stl'))
print('CAMD OK')




