import json,math,sys
P=json.load(open(sys.argv[1],encoding='utf-8'))
T,M,S,N,U,D=[P[k] for k in ('than','mat_truoc','mach','truc_nghieng','khung_u','de_xoay')]
zd=D['de_cao']-D['lom_sau']+D['dia_day']; zp=zd+N['cao_tam_tren_dia']; y0=-(T['d']+M['t'])/2+M['t']; yp=y0+.5+S['cam_cao_tren_pcb']; zl=zp+S['pcb_h']/2-S['ong_kinh_cach_canh_tren']
cmd=[]; A=lambda c,**p: cmd.append({"command":c,"params":p})
XZ=lambda y:{"origin":[0,y,0],"x_dir":[1,0,0],"y_dir":[0,0,1]}   # normal -Y
B="Bezel"
A("sketch.create",plane=XZ(y0)); A("sketch.rectangle.rounded",p0=[-T['w']/2,zp-T['h']/2],p1=[T['w']/2,zp+T['h']/2],radius=T['r_goc']); A("sketch.finish")
A("solid.extrude",distance=M['t'],body_name=B,operation="new_body")
Y=[0,1,0]; yf=y0-M['t']
cy=lambda d,y_a,y_b,x,z,op="cut": A("solid.cylinder",diameter=d,height=y_b-y_a,base=[x,y_a,z],axis=Y,operation=op,targets=[B])
cy(M['lo_ong_kinh_d'],yf-.1,y0+.1,0,zl); cy(M['vong_trang_tri_d'],yf-.1,yf+M['vong_trang_tri_sau'],0,zl)
zled=zl-M['den_duoi_ong_kinh']
for sx in (-1,1): cy(M['den_d'],yf+M['den_da_mong'],y0+.1,sx*M['den_cach_nhau']/2,zled)
for sx in (-1,1):
 for sz in (-1,1):
  x=sx*(T['w']/2-M['vit_cach_canh']); z=zp+sz*(T['h']/2-M['vit_cach_canh'])
  A("solid.cone",radius=2.5,top_radius=M['vit_m25_xuyen']/2-.3,height=2.5-M['vit_m25_xuyen']/2+.3,base=[x,yf,z],axis=Y,operation="cut",targets=[B])
  cy(M['vit_m25_xuyen'],yf-.1,y0+.1,x,z)
# text on front face (mirror-correct when viewed from front: sketch seen from -Y => x_dir +X, y_dir +Z, normal -Y)
A("sketch.create",plane=XZ(yf+M['chu_sau']))
A("sketch.text",text=M['chu'],at=[0,zled-M['chu_duoi_den']-M['chu_cao']/2],height=M['chu_cao'],align="center",font=M['font'])
A("sketch.finish"); A("solid.extrude",distance=M['chu_sau']+.1,operation="cut",targets=[B])
for sx in (-1,1):
 for sz in (-1,1): A("solid.cylinder",diameter=2.5,height=(yp-S['khe_moi_ben'])-(y0-1),base=[sx*(S['pcb_w']/2-1.5),y0-1,zp+sz*(S['pcb_h']/2-1.5)],axis=Y,operation="join",targets=[B])
# Base revolve with R2 fillet
Rb=D['de_d']/2; hb=D['de_cao']; rf=2.0
A("sketch.create",plane="XZ")   # sketch x=+X, y=-Z
A("sketch.line",points=[[0,0],[Rb,0],[Rb,-(hb-rf)]]); A("sketch.arc.center_point",center=[Rb-rf,-(hb-rf)],start=[Rb,-(hb-rf)],end=[Rb-rf,-hb],clockwise=True)
A("sketch.line",points=[[Rb-rf,-hb],[0,-hb],[0,0]]); A("sketch.finish")
A("solid.revolve",axis="Z",body_name="Base",operation="new_body")
# U arm with fillet on top edges
xi=T['w']/2+N['khe_tay_than']; x=xi; xe=x+U['tay_day']
A("solid.box",corner=[x,-U['tay_sau_y']/2,zd-1],length=U['tay_day'],width=U['tay_sau_y'],height=U['tay_cao']+1,body_name="Arm")
zt=zd+U['tay_cao']; A("solid.fillet",edges=[[(x+xe)/2,-U['tay_sau_y']/2,zt],[(x+xe)/2,U['tay_sau_y']/2,zt]],radius=3,body="Arm")
json.dump({"commands":cmd},open(sys.argv[2],'w'),indent=1)
