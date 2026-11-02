import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

scene_path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
data = json.loads(scene_path.read_text(encoding="utf-8"))
scene = bpy.context.scene

# -- Start from a truly empty scene: factory-startup ships a Cube, Camera and Light. --
for ob in list(bpy.data.objects):
    bpy.data.objects.remove(ob, do_unlink=True)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials,
                   bpy.data.cameras, bpy.data.lights, bpy.data.worlds):
    for block in list(datablocks):
        if block.users == 0:
            datablocks.remove(block)

# -- Render settings -----------------------------------------------------------
engine_ids = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
if data["engine"] == "cycles":
    scene.render.engine = "CYCLES"
else:
    scene.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in engine_ids else next(iter(engine_ids))
scene.render.resolution_x, scene.render.resolution_y = data["size"]
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
if data["engine"] == "cycles":
    scene.cycles.samples = data["samples"]
    scene.cycles.use_denoising = True
else:
    eevee = getattr(scene, "eevee", None)
    if eevee is not None and hasattr(eevee, "taa_render_samples"):
        eevee.taa_render_samples = data["samples"]

scene.view_settings.view_transform = "AgX"
for look in ("AgX - Medium High Contrast", "AgX - Medium Contrast", "None"):
    try:
        scene.view_settings.look = look
        break
    except Exception:
        pass


def lin(value):
    value = int(value, 16) / 255.0
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def rgb(hex_color):
    return tuple(lin(hex_color[i:i + 2]) for i in (1, 3, 5))


BG = rgb(data["background"])
BG_STRENGTH = 3.0
AMBIENT_STRENGTH = 0.35


def set_input(node, name, value):
    if name in node.inputs:
        node.inputs[name].default_value = value


# -- World: camera rays see the exact background, lighting rays stay soft. -----
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnt.nodes.clear()
w_out = wnt.nodes.new("ShaderNodeOutputWorld")
w_cam = wnt.nodes.new("ShaderNodeBackground")
w_cam.inputs["Color"].default_value = (*BG, 1.0)
w_cam.inputs["Strength"].default_value = BG_STRENGTH
w_amb = wnt.nodes.new("ShaderNodeBackground")
w_amb.inputs["Color"].default_value = (0.92, 0.95, 0.97, 1.0)
w_amb.inputs["Strength"].default_value = AMBIENT_STRENGTH
w_mix = wnt.nodes.new("ShaderNodeMixShader")
w_path = wnt.nodes.new("ShaderNodeLightPath")
wnt.links.new(w_path.outputs["Is Camera Ray"], w_mix.inputs[0])
wnt.links.new(w_amb.outputs["Background"], w_mix.inputs[1])
wnt.links.new(w_cam.outputs["Background"], w_mix.inputs[2])
wnt.links.new(w_mix.outputs["Shader"], w_out.inputs["Surface"])


def make_material(label, hex_color, finish):
    mat = bpy.data.materials.new(label + " PETG")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    base = rgb(hex_color)
    set_input(bsdf, "Base Color", (*base, 1.0))
    set_input(bsdf, "Roughness", {"matte": 0.65, "satin": 0.45, "gloss": 0.25}[finish])
    set_input(bsdf, "Specular IOR Level", 0.3)
    set_input(bsdf, "Specular", 0.3)
    if data["engine"] == "cycles":
        bevel = nt.nodes.new("ShaderNodeBevel")
        set_input(bevel, "Radius", 0.0003)
        nt.links.new(bevel.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


# -- Import STLs in millimetres and bake scale 0.001 so world coords are metres. --
mesh_objects = []
for item in data["objects"]:
    bpy.ops.wm.stl_import(filepath=item["stl"])
    ob = bpy.context.object
    ob.name = item["label"]
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    ob.scale = (0.001, 0.001, 0.001)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30))
    mat = make_material(item["label"], item["color"], item["finish"])
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    mesh_objects.append(ob)

bpy.context.view_layer.update()
points = [ob.matrix_world @ Vector(corner) for ob in mesh_objects for corner in ob.bound_box]
if not points:
    raise SystemExit("blender_scene: no STL geometry imported")
lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
center = (lo + hi) / 2.0
extent = hi - lo
radius = max((p - center).length for p in points)
radius = max(radius, 1e-4)
base_z = lo.z


# -- Cyclorama: emissive L-shaped studio backdrop, wide enough for every view. --
BACK_Y = center.y + 8.0 * radius
BACK_X = 40.0 * radius
MANY = 30.0 * radius
verts = [
    (center.x - BACK_X, center.y - MANY, base_z),
    (center.x + BACK_X, center.y - MANY, base_z),
    (center.x + BACK_X, BACK_Y, base_z),
    (center.x - BACK_X, BACK_Y, base_z),
    (center.x - BACK_X, BACK_Y, base_z + MANY),
    (center.x + BACK_X, BACK_Y, base_z + MANY),
]
faces = [(0, 1, 2, 3), (3, 2, 5, 4)]
cyc_mesh = bpy.data.meshes.new("Cyclorama")
cyc_mesh.from_pydata(verts, [], faces)
cyc_mesh.update()
cyc = bpy.data.objects.new("Cyclorama", cyc_mesh)
scene.collection.objects.link(cyc)

bg_mat = bpy.data.materials.new("Cyclorama")
bg_mat.use_nodes = True
bnt = bg_mat.node_tree
bnt.nodes.clear()
b_out = bnt.nodes.new("ShaderNodeOutputMaterial")
b_light = bnt.nodes.new("ShaderNodeEmission")
b_light.inputs["Color"].default_value = (*BG, 1.0)
b_light.inputs["Strength"].default_value = BG_STRENGTH
b_dark = bnt.nodes.new("ShaderNodeEmission")
b_dark.inputs["Color"].default_value = (*[c * 0.55 for c in BG], 1.0)
b_dark.inputs["Strength"].default_value = BG_STRENGTH
b_shadow = bnt.nodes.new("ShaderNodeMixShader")

b_coord = bnt.nodes.new("ShaderNodeTexCoord")
b_sep = bnt.nodes.new("ShaderNodeSeparateXYZ")
bnt.links.new(b_coord.outputs["Object"], b_sep.inputs["Vector"])
b_comb = bnt.nodes.new("ShaderNodeCombineXYZ")
bnt.links.new(b_sep.outputs["X"], b_comb.inputs["X"])
bnt.links.new(b_sep.outputs["Y"], b_comb.inputs["Y"])
b_dist = bnt.nodes.new("ShaderNodeVectorMath")
b_dist.operation = "DISTANCE"
bnt.links.new(b_comb.outputs["Vector"], b_dist.inputs[0])
b_dist.inputs[1].default_value = (center.x, center.y, 0.0)
b_radial = bnt.nodes.new("ShaderNodeMapRange")
b_radial.inputs["From Min"].default_value = 0.0
b_radial.inputs["From Max"].default_value = max(extent.x, extent.y) * 0.75
b_radial.inputs["To Min"].default_value = 1.0
b_radial.inputs["To Max"].default_value = 0.0
b_radial.clamp = True
bnt.links.new(b_dist.outputs["Value"], b_radial.inputs["Value"])
b_floor = bnt.nodes.new("ShaderNodeMapRange")
b_floor.inputs["From Min"].default_value = base_z
b_floor.inputs["From Max"].default_value = base_z + max(extent.z, radius * 0.2)
b_floor.inputs["To Min"].default_value = 1.0
b_floor.inputs["To Max"].default_value = 0.0
b_floor.clamp = True
bnt.links.new(b_sep.outputs["Z"], b_floor.inputs["Value"])
b_mul1 = bnt.nodes.new("ShaderNodeMath")
b_mul1.operation = "MULTIPLY"
bnt.links.new(b_radial.outputs["Result"], b_mul1.inputs[0])
bnt.links.new(b_floor.outputs["Result"], b_mul1.inputs[1])
b_mul2 = bnt.nodes.new("ShaderNodeMath")
b_mul2.operation = "MULTIPLY"
bnt.links.new(b_mul1.outputs["Value"], b_mul2.inputs[0])
b_mul2.inputs[1].default_value = 0.45
bnt.links.new(b_mul2.outputs["Value"], b_shadow.inputs[0])
bnt.links.new(b_light.outputs["Emission"], b_shadow.inputs[1])
bnt.links.new(b_dark.outputs["Emission"], b_shadow.inputs[2])
bnt.links.new(b_shadow.outputs["Shader"], b_out.inputs["Surface"])
cyc.data.materials.append(bg_mat)

# -- Three soft area lights (key upper-left, weak fill right, rim behind). -----
for name, loc, power, size in (("Key", (-3, -4, 5), 300, 4),
                               ("Fill", (4, -2, 2), 120, 4),
                               ("Rim", (1, 4, 4), 240, 3)):
    light_pos = center + Vector(loc) * radius
    bpy.ops.object.light_add(type="AREA", location=light_pos)
    light = bpy.context.object
    light.name = name
    light.data.energy = power * radius * radius
    light.data.shape = "DISK"
    light.data.size = size * radius
    light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()

# -- Camera fit: 12% margin on each side, orthographic for front/top. ----------
bpy.ops.object.camera_add()
cam = bpy.context.object
scene.camera = cam
cam.data.sensor_fit = "AUTO"
cam.data.clip_start = 0.001
cam.data.clip_end = 1000.0
w, h = data["size"]
aspect = w / h
sensor_w = cam.data.sensor_width
sensor_h = sensor_w * h / w if w >= h else sensor_w * w / h
MARGIN = 1.24
PERSP_MARGIN = 1.00

for view in data["views"]:
    az, el = {"iso": (-45, 30), "front": (0, 0), "top": (0, 90), "side34": (-30, 15)}[view]
    az = math.radians(az)
    el = math.radians(el)
    direction = Vector((math.cos(el) * math.sin(az),
                        -math.cos(el) * math.cos(az),
                        math.sin(el)))
    cam.rotation_mode = "XYZ"
    if view in ("front", "top"):
        cam.data.type = "ORTHO"
        horizontal, vertical = (extent.x, extent.z) if view == "front" else (extent.x, extent.y)
        cam.data.ortho_scale = max(horizontal, vertical * aspect) * MARGIN
        dist = radius * 6.0
    else:
        cam.data.type = "PERSP"
        cam.data.lens = 85.0 if view == "side34" else 50.0
        half_min = min(math.atan((sensor_w / 2.0) / cam.data.lens),
                       math.atan((sensor_h / 2.0) / cam.data.lens))
        dist = radius * PERSP_MARGIN / math.tan(half_min)
    cam.location = center + direction * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(scene_path.parent / (scene_path.stem.replace("-scene", "") + "-" + view + ".png"))
    bpy.ops.render.render(write_still=True)
