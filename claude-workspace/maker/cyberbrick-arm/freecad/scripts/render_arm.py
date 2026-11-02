import json, os, subprocess, sys, tempfile, math
from pathlib import Path
import FreeCAD as App
HERE=Path(__file__).resolve().parent; PROJ=HERE.parent.parent; ROOT=PROJ.parent.parent
sys.path.insert(0,str(ROOT/'tools'/'robotics-cad'/'scripts'))
from mpl_render import render
P=json.loads((PROJ/'freecad'/'params.json').read_text(encoding='utf-8'))
FCC=Path(r'C:\Program Files\FreeCAD 1.1\bin\FreeCADCmd.exe'); BUILD=HERE/'build_arm.py'; OUT=PROJ/'design'/'concepts'; OUT.mkdir(parents=True,exist_ok=True)
IN=(.82,.84,.86); CB=(.13,.14,.16); WORM=(1,.43,.08)
def load(pose,tmp):
    out=Path(tmp)/('arm_'+pose+'.FCStd'); env=dict(os.environ,ARM_OUT=str(out),ARM_PARAMS=str(PROJ/'freecad'/'params.json'),ARM_POSE=pose)
    run=subprocess.run([str(FCC),str(BUILD)],env=env,capture_output=True,text=True,timeout=900)
    if run.returncode or not out.exists(): raise RuntimeError(run.stdout[-1000:]+run.stderr[-1000:])
    doc=App.openDocument(str(out)); items=[]
    for o in doc.Objects:
        if o.isDerivedFrom('Part::Feature') and o.Shape.Solids:
            col=CB if o.Label.startswith('CB_') else WORM if o.Label in ('Worm','Pinion_24T') else IN
            items.append((o.Shape.copy(),col))
    return doc,items,json.loads(out.with_suffix('.json').read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='arm-render-') as tmp:
    poses={}; docs=[]
    for p in P['tu_the']:
        doc,items,data=load(p,tmp); docs.append(doc); poses[p]=(items,data)
        for view in ('front','top','iso'): render(items,str(OUT/('arm-%s-%s.png'%(p,view))),view=view,title='Cyberbrick arm - %s - %s'%(p,view))
    layers=[]
    for items,_ in poses.values(): layers.extend((s,c,.35) for s,c,*rest in items)
    reach=max(math.hypot(data['T'][0],data['T'][1]) for _,data in poses.values())
    render(layers,str(OUT/'arm-reach.png'),view='front',title='Reach %.1f mm; shoulder height %.1f mm'%(reach,P['vai']['J1'][1]))
    for doc in docs: App.closeDocument(doc.Name)
print('RENDER OK 10')
