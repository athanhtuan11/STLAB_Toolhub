import argparse, fnmatch, json, os, subprocess, sys
from pathlib import Path
FC_CMD=Path(r"C:\Program Files\FreeCAD 1.1\bin\freecadcmd.exe")
BLENDER=Path(r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
VIEWS=("iso","front","top","side34")
def color(v):
 if not isinstance(v,str) or len(v)!=7 or v[0]!="#": raise ValueError("Expected #RRGGBB color")
 int(v[1:],16); return v.upper()
def run(cmd,env=None):
 p=subprocess.run(cmd,capture_output=True,text=True,env=env)
 if p.stdout or p.stderr: print("\n".join((p.stdout+"\n"+p.stderr).splitlines()[-20:]))
 if p.returncode: raise RuntimeError("\n".join((p.stdout+"\n"+p.stderr).splitlines()[-12:]))
def main():
 p=argparse.ArgumentParser()
 p.add_argument("model",type=Path); p.add_argument("--cmf",required=True,type=Path); p.add_argument("--out",required=True,type=Path)
 p.add_argument("--views",default="iso,front,top,side34"); p.add_argument("--samples",type=int,default=64); p.add_argument("--size",default="1600x1200")
 p.add_argument("--name"); p.add_argument("--engine",choices=("eevee","cycles"),default="eevee"); a=p.parse_args()
 try:
  if not a.model.is_file() or not a.cmf.is_file(): raise ValueError("Model or CMF file does not exist")
  cmf=json.loads(a.cmf.read_text(encoding="utf-8")); default=cmf.get("default",{"color":"#D9DDD9","finish":"satin"})
  bg=color(cmf.get("background","#ECF1EF"))
  for s in [default]+cmf.get("rules",[]):
   color(s["color"]); assert s["finish"] in ("matte","satin","gloss")
  views=[v.strip() for v in a.views.split(",") if v.strip()]
  if not views or any(v not in VIEWS for v in views): raise ValueError("Invalid view")
  w,h=map(int,a.size.lower().split("x")); assert w>0 and h>0 and a.samples>0
  name=a.name or a.model.stem; a.out.mkdir(parents=True,exist_ok=True); stld=a.out/"_stl"; stld.mkdir(exist_ok=True)
  tmp=a.out/(name+"-export.json"); scene_path=a.out/(name+"-scene.json"); env=os.environ.copy()
  env.update(RENDER_MODEL=str(a.model.resolve()),RENDER_STL_DIR=str(stld.resolve()),RENDER_EXPORT_JSON=str(tmp.resolve()))
  if not FC_CMD.is_file(): raise RuntimeError("FreeCAD command not found: "+str(FC_CMD))
  run([str(FC_CMD),str(Path(__file__).with_name("fc_export.py"))],env)
  exported=json.loads(tmp.read_text(encoding="utf-8")); objects=[]
  for o in exported:
   style=default
   for r in cmf.get("rules",[]):
    names=r["names"] if isinstance(r["names"],list) else [r["names"]]
    if any(fnmatch.fnmatchcase(o["label"],n) for n in names): style=r; break
   objects.append({"label":o["label"],"stl":o["stl"],"color":color(style["color"]),"finish":style["finish"]})
  scene={"background":bg,"views":views,"objects":objects,"size":[w,h],"engine":a.engine,"samples":a.samples}
  scene_path.write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding="utf-8")
  if not BLENDER.is_file(): raise RuntimeError("Blender not found: "+str(BLENDER))
  run([str(BLENDER),"-b","--factory-startup","-P",str(Path(__file__).with_name("blender_scene.py")),"--",str(scene_path)])
  missing=[name+"-"+v+".png" for v in views if not (a.out/(name+"-"+v+".png")).is_file()]
  if missing: raise RuntimeError("Blender did not create: "+", ".join(missing))
  print("RENDER OK "+str(len(views))+" images"); return 0
 except Exception as e: print("render: "+str(e),file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
