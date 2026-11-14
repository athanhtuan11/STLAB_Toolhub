"""Ghep chu moi vao 3mf goc, GIU NGUYEN mau (34 chi tiet balo + paint voi + support ve tay + cai dat in cua tac gia).
Moi balo: bo 8 chi tiet chu ELEPHANT (id 26, 34-40), them 1 chi tiet chu xam (dau nhua 3).
  python -I build_3mf.py <goc.3mf> <ra.3mf> <text-stlab.stl> <text-small-tree.stl>
Balo object 41, 43 -> STLAB; 42 -> SMALL TREE. Bo muc <assemble> (chi la khung nhin lap rap, chi so volume da doi).
"""
import re, struct, sys, uuid, zipfile
import numpy as np
src, dst, stl_a, stl_b = sys.argv[1:5]
LET = {"26", "34", "35", "36", "37", "38", "39", "40"}
OFF = (0.0, -16.77, -23.985)                     # goc toa do chi tiet chu (nhu chu goc)
TXT = {"44": ("text-stlab", stl_a), "45": ("text-small-tree", stl_b)}
PLAN = {"41": ("44", "backpack-stlab"), "42": ("45", "backpack-small-tree"), "43": ("44", "backpack-stlab")}
GREY = 3

def read_stl(p):
    b = open(p, "rb").read(); n = struct.unpack("<I", b[80:84])[0]
    v = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", 9), ("a", "<u2")]))["v"]
    v = v.reshape(-1, 3).astype(np.float64)
    u, inv = np.unique(v.round(5), axis=0, return_inverse=True)
    return u, inv.reshape(-1, 3)

def mesh_xml(oid, name, v, t):
    v = v - np.array(OFF)
    L = [f'  <object id="{oid}" p:UUID="{uuid.uuid4()}" type="model">', "   <mesh>", "    <vertices>"]
    L += [f'     <vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in v]
    L += ["    </vertices>", "    <triangles>"]
    L += [f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t]
    L += ["    </triangles>", "   </mesh>", "  </object>"]
    return "\n".join(L)

zin = zipfile.ZipFile(src)
meshes, nface = [], {}
for oid, (name, p) in TXT.items():
    v, t = read_stl(p); nface[oid] = len(t); meshes.append(mesh_xml(oid, name, v, t))
text_model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
              'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
              'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
              ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n' + "\n".join(meshes) +
              '\n </resources>\n <build/>\n</model>\n')
TF = f"1 0 0 0 1 0 0 0 1 {OFF[0]} {OFF[1]} {OFF[2]}"
MAT = f"1 0 0 {OFF[0]} 0 1 0 {OFF[1]} 0 0 1 {OFF[2]} 0 0 0 1"

def fix_top(s):
    out, cur = [], None
    for line in s.splitlines():
        m = re.search(r'<object id="(\d+)"', line)
        if m: cur = m.group(1)
        if cur in PLAN:
            mc = re.search(r'<component p:path="/3D/Objects/object_12.model" objectid="(\d+)"', line)
            if mc and mc.group(1) in LET:
                continue
            if "</components>" in line:
                out.append(f'    <component p:path="/3D/Objects/text.model" objectid="{PLAN[cur][0]}" '
                           f'p:UUID="{uuid.uuid4()}" transform="{TF}" />')
        out.append(line)
    return "\n".join(out) + "\n"

def fix_settings(s):
    s = re.sub(r"\s*<assemble>.*?</assemble>", "", s, flags=re.S)
    def obj(m):
        oid, body = m.group(1), m.group(0)
        if oid not in PLAN: return body
        tid, name = PLAN[oid]
        body = re.sub(r'\s*<part id="(\d+)"[^>]*>.*?</part>',
                      lambda p: "" if p.group(1) in LET else p.group(0), body, flags=re.S)
        body = body.replace('<metadata key="name" value="backpack.stl"/>', f'<metadata key="name" value="{name}"/>', 1)
        part = (f'\n    <part id="{tid}" subtype="normal_part" uuid="{uuid.uuid4()}">\n'
                f'      <metadata key="name" value="{TXT[tid][0]}"/>\n'
                f'      <metadata key="matrix" value="{MAT}"/>\n'
                f'      <metadata key="extruder" value="{GREY}"/>\n'
                f'      <mesh_stat face_count="{nface[tid]}" edges_fixed="0" degenerate_facets="0" facets_removed="0" '
                f'facets_reversed="0" backwards_edges="0"/>\n    </part>\n  </object>')
        return re.sub(r"\s*</object>$", part, body)
    return re.sub(r'<object id="(\d+)">.*?</object>', obj, s, flags=re.S)

with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zin.infolist():
        data = zin.read(it.filename)
        if it.filename == "3D/3dmodel.model":
            data = fix_top(data.decode("utf-8")).encode("utf-8")
        elif it.filename == "Metadata/model_settings.config":
            data = fix_settings(data.decode("utf-8")).encode("utf-8")
        elif it.filename == "3D/_rels/3dmodel.model.rels":
            data = data.decode("utf-8").replace("</Relationships>",
                ' <Relationship Target="/3D/Objects/text.model" Id="rel-text" '
                'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>').encode("utf-8")
        zo.writestr(it, data)
    zo.writestr("3D/Objects/text.model", text_model)
print("WROTE", dst, nface)
