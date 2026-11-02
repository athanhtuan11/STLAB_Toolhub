import bpy, json, math, sys
from mathutils import Vector
from pathlib import Path
p=sys.argv[sys.argv.index("--")+1]; data=json.load(open(p,encoding="utf-8")); scene=bpy.context.scene
# Remove factory-startup cube, camera, and light before importing STL.
for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
for datablocks in (bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.cameras,bpy.data.lights):
 for block in list(datablocks):
  if block.users==0: datablocks.remove(block)
engine_ids={item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
scene.render.engine="CYCLES" if data["engine"]=="cycles" else ("BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_ids else "BLENDER_EEVEE")
scene.render.resolution_x,scene.render.resolution_y=data["size"]; scene.render.resolution_percentage=100
if data["engine"]=="cycles": scene.cycles.samples=data["samples"]; scene.cycles.use_denoising=True
scene.view_settings.view_transform="AgX"; scene.view_settings.look="AgX - Medium High Contrast"
def lin(x):
 x=int(x,16)/255; return x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4
def rgba(h): return (*[lin(h[i:i+2]) for i in (1,3,5)],1)
scene.world.color=(0.12,0.12,0.12)
for item in data["objects"]:
 bpy.ops.wm.stl_import(filepath=item["stl"]); ob=bpy.context.object; ob.name=item["label"]; ob.scale=(.001,)*3
 for poly in ob.data.polygons: poly.use_smooth=True
 mat=bpy.data.materials.new(item["label"]+" PETG"); mat.diffuse_color=rgba(item["color"]); mat.use_nodes=True
 bs=mat.node_tree.nodes.get("Principled BSDF"); bs.inputs["Base Color"].default_value=rgba(item["color"]); bs.inputs["Roughness"].default_value={"matte":.65,"satin":.45,"gloss":.25}[item["finish"]]
 if "Specular IOR Level" in bs.inputs: bs.inputs["Specular IOR Level"].default_value=.3
 if "Emission Color" in bs.inputs: bs.inputs["Emission Color"].default_value=rgba(item["color"]); bs.inputs["Emission Strength"].default_value=.12
 ob.data.materials.clear(); ob.data.materials.append(mat)
 for poly in ob.data.polygons: poly.material_index=0
bpy.context.view_layer.update()
objects=[o for o in scene.objects if o.type=="MESH"]; pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
lo=Vector(tuple(min(v[i] for v in pts) for i in range(3))); hi=Vector(tuple(max(v[i] for v in pts) for i in range(3))); center=(lo+hi)/2; extent=hi-lo; radius=max(extent)*.5
bg=bpy.data.materials.new("Studio background"); bg.diffuse_color=rgba(data["background"]); bg.use_nodes=True
nodes=bg.node_tree.nodes; nodes.clear(); out=nodes.new("ShaderNodeOutputMaterial"); emission=nodes.new("ShaderNodeEmission")
emission.inputs["Color"].default_value=rgba(data["background"]); emission.inputs["Strength"].default_value=2.0
bg.node_tree.links.new(emission.outputs["Emission"],out.inputs["Surface"])
verts=[]; faces=[]; sweep=[(-3,0),(0,0),(1,.15),(2,.6),(2.7,1.5),(3,5)]
for y,z in sweep: verts.extend([(-4*max(radius,.1),center.y+y*radius,lo.z+z*radius),(4*max(radius,.1),center.y+y*radius,lo.z+z*radius)])
for j in range(len(sweep)-1): faces.append((2*j,2*j+1,2*j+3,2*j+2))
mesh=bpy.data.meshes.new("Cyclorama"); mesh.from_pydata(verts,[],faces); cyc=bpy.data.objects.new("Cyclorama",mesh); scene.collection.objects.link(cyc); cyc.data.materials.append(bg)
for name,loc,power,size in [("Key",(-3,-4,5),300,4),("Fill",(4,-2,2),120,4),("Rim",(1,4,4),240,3)]:
 bpy.ops.object.light_add(type="AREA",location=Vector(center)+Vector(loc)*max(radius,.1)); light=bpy.context.object; light.name=name; light.data.energy=power*max(radius,.1)**2; light.data.shape="DISK"; light.data.size=size*max(radius,.1); light.rotation_euler=(center-light.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(); cam=bpy.context.object; scene.camera=cam
def point_cam(pos,target): cam.location=pos; cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
for view in data["views"]:
 az,el={"iso":(-45,30),"front":(0,0),"top":(0,90),"side34":(-30,15)}[view]; az=math.radians(az); el=math.radians(el); direction=Vector((math.cos(el)*math.sin(az),-math.cos(el)*math.cos(az),math.sin(el)))
 point_cam(center+direction*max(radius,.1)*(3.9 if view=="iso" else 6.5),center); cam.data.lens=85 if view=="side34" else 50
 if view in ("front","top"):
  cam.data.type="ORTHO"
  horizontal,vertical=(extent.x,extent.z) if view=="front" else (extent.x,extent.y)
  cam.data.ortho_scale=max(horizontal,vertical*scene.render.resolution_x/scene.render.resolution_y)*1.24
 else: cam.data.type="PERSP"
 scene.render.filepath=str(Path(p).parent/(Path(p).stem.replace("-scene","")+"-"+view+".png")); bpy.ops.render.render(write_still=True)
