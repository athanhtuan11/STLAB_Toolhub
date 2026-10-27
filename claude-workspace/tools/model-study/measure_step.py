#!/usr/bin/env python3
import csv, math, os, sys
import Part


def vec(v): return (v.x, v.y, v.z)
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def mag(a): return math.sqrt(dot(a,a))
def unit(a): return mul(a,1.0/mag(a))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def canon(v):
    v=unit(v); i=max(range(3),key=lambda k:abs(v[k]))
    if v[i]<0: v=mul(v,-1)
    for j,n in enumerate('xyz'):
        if math.degrees(math.acos(min(1,abs(v[j]))))<.5: return v,n
    return v,','.join('%.3f'%x for x in v)
def distline(c,d,a):
    q=sub(d,c); return mag(sub(q,mul(a,dot(q,a))))
def arange(face,a,c):
    vals=[dot(sub(vec(v.Point),c),a) for v in face.Vertexes]
    if not vals:
        for e in face.Edges: vals += [dot(sub(vec(v.Point),c),a) for v in e.Vertexes]
    return (min(vals),max(vals)) if vals else (0,0)
def angular(fs):
    ints=[]
    for f in fs:
        u0,u1=f.ParameterRange[:2]; span=min(2*math.pi,abs(u1-u0)); s=u0%(2*math.pi); e=s+span
        if e<=2*math.pi+1e-8: ints.append((s,min(e,2*math.pi)))
        else: ints.extend([(s,2*math.pi),(0,e-2*math.pi)])
    ints.sort(); merged=[]
    for a,b in ints:
        if merged and a<=merged[-1][1]+1e-8: merged[-1]=(merged[-1][0],max(merged[-1][1],b))
        else: merged.append((a,b))
    return min(360,sum(b-a for a,b in merged)*180/math.pi)
def make_groups(items, axis):
    par=list(range(len(items)))
    def root(i):
        while par[i]!=i: par[i]=par[par[i]]; i=par[i]
        return i
    for i in range(len(items)):
        f,ri=items[i]
        for j in range(i):
            g,rj=items[j]
            if abs(f.Surface.Radius-g.Surface.Radius)>.001: continue
            if mag(cross(axis[0],axis[1]))>math.sin(math.radians(.5)): continue
            if distline(vec(f.Surface.Center),vec(g.Surface.Center),axis[0])>=.001: continue
            if ri[0]>rj[1]+1e-6 or rj[0]>ri[1]+1e-6: continue
            par[root(i)]=root(j)
    d={}
    for i,x in enumerate(items): d.setdefault(root(i),[]).append(x)
    return list(d.values())
def extract(path):
    shape=Part.read(path); solids=list(shape.Solids) or [shape]; rows=[]
    for part,solid in enumerate(solids,1):
        fs=[f for f in solid.Faces if isinstance(f.Surface,Part.Cylinder)]
        remaining=set(range(len(fs)))
        while remaining:
            i=min(remaining); f=fs[i]; a,name=canon(vec(f.Surface.Axis)); c=vec(f.Surface.Center)
            cand=[]
            for j,g in enumerate(fs):
                ga,_=canon(vec(g.Surface.Axis))
                if abs(f.Surface.Radius-g.Surface.Radius)<=.001 and mag(cross(a,ga))<=math.sin(math.radians(.5)) and distline(c,vec(g.Surface.Center),a)<.001:
                    cand.append((j,g,arange(g,a,c)))
            groups=make_groups([(g,r) for _,g,r in cand],(a,a))
            group=next((gr for gr in groups if any(cand[k][0]==i for k,(gf,_) in enumerate([(x[1],x[2]) for x in cand]))),None)
            # select component containing current face
            group=next(gr for gr in groups if any(g is f for g,r in gr))
            ids={j for j,g,r in cand if any(g is q for q,rq in group)}; remaining-=ids
            lo=min(r[0] for g,r in group); hi=max(r[1] for g,r in group); sweep=angular([g for g,r in group])
            mid=(lo+hi)/2; center=add(c,mul(a,mid))
            kind='arc'
            if sweep>=300:
                q=group[0][0]; u0,u1,v0,v1=q.ParameterRange; p=vec(q.valueAt((u0+u1)/2,(v0+v1)/2)); n=vec(q.normalAt((u0+u1)/2,(v0+v1)/2))
                radial=sub(sub(p,vec(q.Surface.Center)),mul(a,dot(sub(p,vec(q.Surface.Center)),a)))
                kind='hole' if dot(n,radial)<0 else 'pin'
            rows.append(dict(part=part,kind=kind,diameter=2*f.Surface.Radius,axis=name,cx=center[0],cy=center[1],cz=center[2],length=hi-lo,sweep_deg=sweep,faces=len(group)))
    rows.sort(key=lambda x:(x['part'],x['axis'],x['cx'],x['cy'],x['cz'],x['diameter']))
    for i,r in enumerate(rows,1): r['idx']=i
    return rows
def output(rows,out):
    os.makedirs(out,exist_ok=True); cols=['idx','part','kind','diameter','axis','cx','cy','cz','length','sweep_deg','faces']
    with open(os.path.join(out,'step_features.csv'),'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
        for r in rows: w.writerow({k:('%.1f'%r[k] if k=='sweep_deg' else '%.3f'%r[k] if k in ('diameter','cx','cy','cz','length') else r[k]) for k in cols})
    lines=['# STEP features','']
    for p in sorted(set(r['part'] for r in rows)):
        lines+=['## Part %d'%p,'','| idx | kind | diameter | axis | cx | cy | cz | length | sweep_deg | faces |','|---:|---|---:|---|---:|---:|---:|---:|---:|---:|']
        for r in rows:
            if r['part']==p: lines.append('| %d | %s | %.3f | %s | %.3f | %.3f | %.3f | %.3f | %.1f | %d |'%(r['idx'],r['kind'],r['diameter'],r['axis'],r['cx'],r['cy'],r['cz'],r['length'],r['sweep_deg'],r['faces']))
        lines.append('')
    lines+=['## Thong ke duong kinh','','| kind | diameter | count |','|---|---:|---:|']; bins=[]
    for r in rows:
        if r['kind'] not in ('hole','pin'): continue
        b=next((b for b in bins if b[0]==r['kind'] and abs(b[1]-r['diameter'])<=.005),None)
        if b: b[2]+=1
        else: bins.append([r['kind'],r['diameter'],1])
    lines += ['| %s | %.3f | %d |'%tuple(b) for b in bins]
    with open(os.path.join(out,'step_features.md'),'w',encoding='utf-8',newline='') as f: f.write('\n'.join(lines)+'\n')
def main():
    args=[a for a in sys.argv[1:] if not a.endswith('.py')]
    if len(args)<2: raise ValueError('usage: measure_step.py <file.step> <output directory>')
    output(extract(args[0]),args[1])
try: main()
except Exception as e: print('measure_step:',e,file=sys.stderr); sys.exit(1)

