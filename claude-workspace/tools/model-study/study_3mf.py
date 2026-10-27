import csv, json, math, os, re, struct, sys, zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict, deque
import numpy as np

def tag(e): return e.tag.rsplit('}',1)[-1].split(':')[-1]
def at(e): return {k.rsplit('}',1)[-1].split(':')[-1]:v for k,v in e.attrib.items()}
def mat(s):
 if not s:return np.eye(4)
 a=np.array(list(map(float,s.split())))
 if len(a)!=12: raise ValueError('transform must have 12 values')
 m=np.eye(4);m[:3,:]=a.reshape(4,3).T;return m
def tr(v,m):return v@m[:3,:3]+m[3,:3]
def clean(s):return re.sub(r'-+','-',re.sub(r'[^a-zA-Z0-9]+','-',re.sub(r'\.[^.]+$','',s))).strip('-').lower() or 'part'
def parse(path):
 z=zipfile.ZipFile(path); root=ET.fromstring(z.read('3D/3dmodel.model')); objs={at(x).get('id'):x for x in root.iter() if tag(x)=='object'}; names={}; settings={}
 if 'Metadata/model_settings.config' in z.namelist():
  cfg=ET.fromstring(z.read('Metadata/model_settings.config'))
  for o in cfg:
   if tag(o)=='object':
    values={}
    for md in o:
     a=at(md)
     if tag(md)=='metadata' and a.get('key'):values[a['key']]=a.get('value','')
    oid=at(o).get('id')
    if oid is not None:
     if 'name' in values:names.setdefault(oid,values['name'])
     settings[oid]={'support':values.get('enable_support',''),'support_type':values.get('support_type',''),'print_settings':{k:v for k,v in sorted(values.items()) if k!='name'}}
 cache={}
 def mesh(oid,stack=()):
  oid=str(oid)
  if oid in stack:raise ValueError('cyclic components')
  if oid in cache:return [(v.copy(),f.copy()) for v,f in cache[oid]]
  o=objs.get(oid);res=[]
  if o is None:return res
  me=next((x for x in o if tag(x)=='mesh'),None)
  if me is not None:
   ve=next(x for x in me if tag(x)=='vertices');te=next(x for x in me if tag(x)=='triangles')
   v=np.array([[float(at(q)[k]) for k in ('x','y','z')] for q in ve]);f=np.array([[int(at(q)[k]) for k in ('v1','v2','v3')] for q in te],dtype=np.int64)
   if len(f):res.append((v,f))
  co=next((x for x in o if tag(x)=='components'),None)
  if co is not None:
   for c in co:
    a=at(c); child=a.get('objectid');pth=a.get('path')
    if pth:
     sub=ET.fromstring(z.read(pth.lstrip('/')))
     for q in sub.iter():
      if tag(q)=='object' and at(q).get('id')==child:objs[child]=q
    for v,f in mesh(child,stack+(oid,)):res.append((tr(v,mat(a.get('transform'))),f.copy()))
  cache[oid]=[(v.copy(),f.copy()) for v,f in res];return res
 plnames=defaultdict(deque)
 support_types={}
 for oid,st in settings.items():
  if st['support_type'] and names.get(oid):support_types.setdefault(names[oid],st['support_type'])
 for n in z.namelist():
  m=re.fullmatch(r'Metadata/plate_(\d+)\.json',n)
  if m:
   for x in json.loads(z.read(n)).get('bbox_objects',[]):plnames[x.get('name','')].append(int(m.group(1)))
 direct={}
 for p in root.iter():
  if tag(p)=='plate':
   pid=next((at(x).get('value') for x in p.iter() if tag(x)=='metadata' and at(x).get('key')=='plater_id'),None)
   if pid:
    for i in p.iter():
     if tag(i)=='model_instance':
      for md in i.iter():
       a=at(md)
       if tag(md)=='metadata' and a.get('key')=='object_id':direct[a.get('value')]=int(pid)
 b=next(x for x in root.iter() if tag(x)=='build'); out=[]
 for item in b:
  if tag(item)!='item':continue
  a=at(item);oid=a.get('objectid');pieces=mesh(oid)
  if not pieces:continue
  vs=[];fs=[];offset=0
  for v,f in pieces:vs.append(tr(v,mat(a.get('transform'))));fs.append(f+offset);offset+=len(v)
  name=names.get(oid,'object-'+oid); plate=direct.get(oid)
  if plate is None:plate=plnames[name].popleft() if plnames[name] else 0
  st=settings.get(str(oid),{'support':'','support_type':'','print_settings':{}}).copy()
  if st['support']=='1' and not st['support_type']:st['support_type']=support_types.get(name,'(mặc định)')
  out.append((name,plate,np.concatenate(vs),np.concatenate(fs),st))
 return out
def readstl(p):
 d=open(p,'rb').read()
 if len(d)>=84:
  n=struct.unpack_from('<I',d,80)[0]
  if len(d)==84+50*n:
   v=np.empty((3*n,3));f=np.arange(3*n).reshape(n,3)
   for i in range(n):v[3*i:3*i+3]=np.array(struct.unpack_from('<12fH',d,84+50*i)[3:12]).reshape(3,3)
   return v,f
 pts=[tuple(map(float,x)) for x in re.findall(rb'vertex\s+([-+\deE.]+)\s+([-+\deE.]+)\s+([-+\deE.]+)',d,re.I)]
 if len(pts)%3:raise ValueError('invalid STL '+p)
 return np.array(pts),np.arange(len(pts)).reshape(-1,3)
def closed(f):
 c=Counter(tuple(sorted((int(a),int(b)))) for x,y,z in f for a,b in ((x,y),(y,z),(z,x)))
 return bool(c) and all(n==2 for n in c.values())
def main():
 if len(sys.argv)!=3:raise SystemExit('Usage: study_3mf.py input output')
 src,out=sys.argv[1:]
 if os.path.isdir(src): items=[(os.path.basename(p),0,*readstl(p),{'support':'','support_type':'','print_settings':{}}) for p in sorted(os.path.join(src,x) for x in os.listdir(src) if x.lower().endswith('.stl'))]
 else:items=parse(src)
 if not items:raise ValueError('no meshes found')
 pd=os.path.join(out,'parts');os.makedirs(pd,exist_ok=True);rows=[];renders=[]
 for i,(name,plate,v,f,settings) in enumerate(items,1):
  v=v.copy();f=f.copy();lo=v.min(0);hi=v.max(0);v[:,:2]-=(lo[:2]+hi[:2])/2;v[:,2]-=lo[2];tri=v[f]
  cr=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);nn=np.linalg.norm(cr,axis=1);norm=np.divide(cr,nn[:,None],out=np.zeros_like(cr),where=nn[:,None]>0)
  vol=abs(float(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6));fn=f'{i:02d}-{clean(name)}.stl';dest=os.path.join(pd,fn)
  with open(dest,'wb') as fp:
   fp.write(b'Claude study mesh'.ljust(80,b'\0'));fp.write(struct.pack('<I',len(f)))
   for t,n in zip(tri,norm):fp.write(struct.pack('<12fH',*(list(n)+list(t.reshape(-1))+[0])))
  size=hi-lo;r={'idx':i,'name':name,'plate':plate,'file':os.path.relpath(dest,out).replace('\\','/'),'triangles':len(f),'size_x':f'{size[0]:.2f}','size_y':f'{size[1]:.2f}','size_z':f'{size[2]:.2f}','z_min':f'{v[:,2].min():.6f}','volume_mm3':f'{vol:.2f}','watertight':str(closed(f)).lower(),'support':settings['support'],'support_type':settings['support_type'],'print_settings':json.dumps(settings['print_settings'],ensure_ascii=False,sort_keys=True,separators=(',',':'))};rows.append(r);renders.append((tri,norm,r))
 cols=['idx','name','plate','file','triangles','size_x','size_y','size_z','z_min','volume_mm3','watertight','support','support_type','print_settings']
 with open(os.path.join(out,'parts.csv'),'w',newline='',encoding='utf-8') as fp:w=csv.DictWriter(fp,fieldnames=cols);w.writeheader();w.writerows(rows)
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from render import render_iso
 n=len(rows);nc=min(5,max(1,math.ceil(math.sqrt(n))));nr=math.ceil(n/nc);fig=plt.figure(figsize=(nc*3.2,nr*3))
 for i,(tri,norm,r) in enumerate(renders,1):
  ax=fig.add_subplot(nr,nc,i);ax.imshow(render_iso(tri));ax.set_axis_off();ax.set_title(f"{i:02d} {clean(r['name'])}  {r['size_x']}×{r['size_y']}×{r['size_z']} mm  P{r['plate']}",fontsize=8,pad=2)
 fig.tight_layout(pad=.6);fig.savefig(os.path.join(out,'contact-sheet.png'),dpi=110);plt.close(fig)
 totals=defaultdict(lambda:[0,0.])
 for r in rows:totals[str(r['plate'])][0]+=1;totals[str(r['plate'])][1]+=float(r['volume_mm3'])
 with open(os.path.join(out,'summary.md'),'w',encoding='utf-8') as fp:
  fp.write(f'# Study summary\n\nChi tiết: {len(rows)}\n\n| Plate | Số chi tiết | Tổng thể tích (mm³) |\n|---:|---:|---:|\n')
  for p,(count,vol) in sorted(totals.items(),key=lambda x:int(x[0])):fp.write(f'| {p} | {count} | {vol:.2f} |\n')
  fp.write('\n| idx | name | plate | file | triangles | size_x | size_y | size_z | z_min | volume_mm3 | watertight |\n|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|\n')
  for r in rows:fp.write('| '+' | '.join(str(r[k]) for k in cols)+' |\n')
  fp.write('\n## Cau hinh in cua tac gia\n\n### Chi tiet bat support\n\n')
  supported=[r for r in rows if r['support']=='1']
  if supported:
   fp.write('| idx | name | plate | support_type |\n|---:|---|---:|---|\n')
   for r in supported:fp.write(f"| {r['idx']} | {r['name']} | {r['plate']} | {r['support_type']} |\n")
  else:fp.write('Khong co chi tiet nao bat support.\n')
  parsed={r['idx']:json.loads(r['print_settings']) for r in rows}
  keys=sorted({k for ps in parsed.values() for k in ps})
  differing=[k for k in keys if len({json.dumps(ps.get(k),ensure_ascii=False,sort_keys=True) for ps in parsed.values()})>1]
  fp.write('\n### Key in khac biet giua cac chi tiet\n\n')
  if differing:
   fp.write('| key | idx: name = value |\n|---|---|\n')
   for k in differing:
    vals=[f"{r['idx']}: {r['name']} = {parsed[r['idx']].get(k,'(khong co)')}" for r in rows if k in parsed[r['idx']]]
    fp.write(f"| {k} | {'; '.join(vals)} |\n")
  else:fp.write('Khong co key in khac biet.\n')
if __name__=='__main__':main()

