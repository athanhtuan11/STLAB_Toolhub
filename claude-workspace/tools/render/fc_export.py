import json, os
from pathlib import Path
import FreeCAD, MeshPart
model=Path(os.environ["RENDER_MODEL"]); out=Path(os.environ["RENDER_STL_DIR"]); manifest=Path(os.environ["RENDER_EXPORT_JSON"]); out.mkdir(parents=True,exist_ok=True)
doc=FreeCAD.openDocument(str(model)); result=[]
try:
 for i,obj in enumerate(doc.Objects):
  if obj.TypeId!="Part::Feature" or obj.Label.startswith("_") or not getattr(obj.ViewObject,"Visibility",True): continue
  shape=getattr(obj,"Shape",None)
  if shape is None or shape.isNull() or not shape.Solids: continue
  mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.05,AngularDeflection=0.2,Relative=False)
  path=out/("object-%04d.stl"%i); mesh.write(str(path)); result.append({"label":obj.Label,"stl":str(path.resolve())})
 manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
finally: FreeCAD.closeDocument(doc.Name)
