import json,math,sys
P=json.load(open(sys.argv[1],encoding='utf-8')); C=P['coupon']; S=P['mach']; D=P['de_xoay']
cmd=[]; A=lambda c,**p: cmd.append({"command":c,"params":p})
B="Coupon"
A("solid.box",corner=[-35,-17,0],length=70,width=34,height=4,body_name=B)
xs=(-23,0,23)
cutcyl=lambda d,x,y,z0,z1: A("solid.cylinder",diameter=d,height=z1-z0,base=[x,y,z0],operation="cut",targets=[B])
for x,d in zip(xs,C['m3_xuyen']): cutcyl(d,x,-8,-.1,4.1)
for x,d in zip(xs,C['dai_oc_s']):
  A("sketch.create",plane={"origin":[0,0,1.4],"x_dir":[1,0,0],"y_dir":[0,1,0]})
  A("sketch.polygon.inscribed",center=[x,-8],radius=d/math.sqrt(3),sides=6,angle=0)
  A("sketch.finish"); A("solid.extrude",distance=2.7,operation="cut",targets=[B])
  cutcyl(3.4,x,-8,-.1,4.1)
for x,d in zip(xs,C['lo_ong_kinh']): cutcyl(d,x,8,-.1,4.1)
for x,d in zip((-10,10),C['den_da_mong']): cutcyl(3.4,x,0,d,4.1)
A("solid.cylinder",diameter=8,height=6.1,base=[30,0,3.9],operation="join",targets=[B])
fw=S['pcb_w']+2*S['khe_moi_ben']; fh=S['pcb_h']+2*S['khe_moi_ben']
A("solid.box",corner=[34.5,-fh/2-1.2,0],length=fw+2.4,width=fh+2.4,height=5,operation="join",targets=[B])
A("solid.box",corner=[35.7,-fh/2,-.1],length=fw,width=fh,height=5.2,operation="cut",targets=[B])
for lst,yy in ((C['m3_xuyen'],-14.5),(C['lo_ong_kinh'],14.5)):
  for x,d in zip(xs,lst):
    A("sketch.create",plane={"origin":[0,0,3.5],"x_dir":[1,0,0],"y_dir":[0,1,0]})
    A("sketch.text",text='%g'%d,at=[x,yy-1.5],height=3,align="center",font="C:/Windows/Fonts/arialbd.ttf")
    A("sketch.finish"); A("solid.extrude",distance=0.6,operation="cut",targets=[B])
R="Coupon_ring"
A("solid.cylinder",diameter=15,height=4,base=[0,40,0],body_name=R)
A("solid.cylinder",diameter=D['lo_dia_d'],height=4.2,base=[0,40,-.1],operation="cut",targets=[R])
json.dump({"commands":cmd},open(sys.argv[2],'w'),indent=1)
