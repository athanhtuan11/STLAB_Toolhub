import bpy, sys, statistics
from mathutils.bvhtree import BVHTree
a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
def load(p):
    bpy.ops.wm.stl_import(filepath=p); return bpy.context.selected_objects[0]
full, dec = load(a[0]), load(a[1])
t = BVHTree.FromObject(dec, bpy.context.evaluated_depsgraph_get())
d = sorted(t.find_nearest(v.co)[3] for v in full.data.vertices)
n = len(d)
# vung chu (z > 33 mm, y < -17 mm so voi tam): sai lech rieng
print(f"DEV mean {statistics.fmean(d):.4f} p99 {d[int(n*0.99)]:.4f} max {d[-1]:.4f} mm")
