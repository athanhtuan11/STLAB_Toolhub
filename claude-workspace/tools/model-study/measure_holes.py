#!/usr/bin/env python3
import argparse, csv, json, os, re, struct, sys
import numpy as np
STEP=0.25

def read_stl(path):
    data=open(path,'rb').read()
    if len(data)>=84:
        n=struct.unpack_from('<I',data,80)[0]
        if 84+n*50==len(data):
            dt=np.dtype([('n','<f4',(3,)),('v','<f4',(3,3)),('a','<u2')])
            return np.frombuffer(data,dtype=dt,offset=84,count=n)['v'].astype(float)
    s=data.decode('ascii')
    v=np.asarray([[float(x),float(y),float(z)] for x,y,z in re.findall(r'vertex\s+([-+\d.eE]+)\s+([-+\d.eE]+)\s+([-+\d.eE]+)',s,re.I)])
    if len(v)%3: raise ValueError('invalid ASCII STL')
    return v.reshape((-1,3,3))

def fit_circle(p):
    x,y=p[:,0],p[:,1]
    a,b,c=np.linalg.lstsq(np.column_stack((x,y,np.ones(len(p)))),-(x*x+y*y),rcond=None)[0]
    cx,cy=-a/2,-b/2; r2=cx*cx+cy*cy-c
    if r2<=0:return None
    r=float(np.sqrt(r2)); mids=(p+np.roll(p,-1,axis=0))/2
    dev=max(float(np.max(np.abs(np.linalg.norm(p-[cx,cy],axis=1)-r))),float(np.max(np.abs(np.linalg.norm(mids-[cx,cy],axis=1)-r))))
    return cx,cy,r,dev

def inside(point,loops):
    x,y=point; parity=False
    for p in loops:
        q=np.roll(p,-1,axis=0)
        cross=((p[:,1]>y)!=(q[:,1]>y)) & (x < (q[:,0]-p[:,0])*(y-p[:,1])/(q[:,1]-p[:,1]+1e-300)+p[:,0])
        if np.count_nonzero(cross)%2: parity=not parity
    return parity

def slice_loops(tris,axis,pos):
    uv=[i for i in range(3) if i!=axis]; z=tris[:,:,axis]
    t=tris[(z.min(axis=1)<=pos)&(z.max(axis=1)>=pos)]
    if not len(t):return []
    v=t[:,:,axis]-pos; hit=(v<=0)!=(np.roll(v,-1,axis=1)<=0)
    ii,jj=np.nonzero(hit); den=v[ii,jj]-v[ii,(jj+1)%3]; good=np.abs(den)>1e-15
    ii,jj,den=ii[good],jj[good],den[good]; f=v[ii,jj]/den
    p=t[ii,jj,:][:,uv]+f[:,None]*(t[ii,(jj+1)%3,:][:,uv]-t[ii,jj,:][:,uv])
    seg=[]
    for i in range(0,len(p)-1,2):
        if np.linalg.norm(p[i]-p[i+1])>1e-8:seg.append((p[i],p[i+1]))
    nodes={}; edges=[]
    def key(q):return tuple(np.rint(q/1e-5).astype(np.int64))
    for a,b in seg:
        ka,kb=key(a),key(b); nodes.setdefault(ka,np.asarray(ka)*1e-5); nodes.setdefault(kb,np.asarray(kb)*1e-5); edges.append((ka,kb))
    adj={}
    for i,(a,b) in enumerate(edges):adj.setdefault(a,[]).append(i);adj.setdefault(b,[]).append(i)
    used=set(); loops=[]
    for ei,(a,b) in enumerate(edges):
        if ei in used:continue
        used.add(ei); chain=[a,b]; cur=b
        while cur!=chain[0] and len(chain)<=len(edges)+1:
            opts=[k for k in adj.get(cur,[]) if k not in used]
            if len(opts)!=1:break
            k=opts[0];used.add(k);x,y=edges[k];cur=y if x==cur else x;chain.append(cur)
        if len(chain)>=17 and chain[-1]==chain[0]:loops.append(np.asarray([nodes[k] for k in chain[:-1]]))
    return loops

def detect(loops):
    circles=[]
    for p in loops:
        if len(p)<16:continue
        f=fit_circle(p)
        if f and .2<=f[2]<=30 and f[3]<=max(.03,.01*f[2]):circles.append((*f,p))
    found=[]
    for cx,cy,r,dev,_ in circles:
        d=min(.1,.2*r); outer=[]; inner=[]
        for ang in np.arange(8)*np.pi/4:
            ux,uy=np.cos(ang),np.sin(ang); outer.append(inside((cx+(r+d)*ux,cy+(r+d)*uy),loops)); inner.append(inside((cx+(r-d)*ux,cy+(r-d)*uy),loops))
        typ='hole' if all(outer) and not any(inner) else 'boss' if all(inner) and not any(outer) else None
        if typ:found.append((typ,cx,cy,2*r,dev))
    return found

def measure(tris):
    result=[]
    for axis,name in enumerate('xyz'):
        lo,hi=float(tris[:,:,axis].min()),float(tris[:,:,axis].max()); positions=np.arange(lo+STEP/2,hi,STEP); groups=[]
        for pos in positions:
            for typ,a,b,d,dev in detect(slice_loops(tris,axis,float(pos))):
                g=next((g for g in reversed(groups) if g[-1][0]>=pos-STEP*1.01 and g[-1][1]==typ and np.hypot(g[-1][2]-a,g[-1][3]-b)<=.1 and abs(g[-1][4]-d)<=.05),None)
                rec=[float(pos),typ,a,b,d,dev]
                if g is None:groups.append([rec])
                else:g.append(rec)
        for g in groups:
            if len(g)<2:continue
            ar=np.asarray([[v[0],v[2],v[3],v[4],v[5]] for v in g]); start=ar[0,0]-.125; end=ar[-1,0]+.125
            result.append({'type':g[0][1],'axis':name,'d_mm':round(float(ar[:,3].mean()),3),'center':[round(float(ar[:,1].mean()),5),round(float(ar[:,2].mean()),5)],'from_mm':round(start,5),'to_mm':round(end,5),'length_mm':round(end-start,5),'n_slices':len(g),'max_dev_mm':round(float(ar[:,4].max()),5)})
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path'); o=ap.add_mutually_exclusive_group(required=True); o.add_argument('--json'); o.add_argument('--csv'); args=ap.parse_args()
    paths=sorted(os.path.join(args.path,n) for n in os.listdir(args.path) if n.lower().endswith('.stl')) if os.path.isdir(args.path) else [args.path]
    rows=[]
    for path in paths:
        try:
            features=measure(read_stl(path))
        except FileNotFoundError:
            # Continue a batch if a path vanishes after directory enumeration.
            if os.path.isdir(args.path):
                continue
            raise
        rows.extend({'file':os.path.basename(path),**f} for f in features)
    if args.json:
        with open(args.json,'w',encoding='utf-8') as f:json.dump({'file':os.path.basename(args.path),'features':[{k:v for k,v in r.items() if k!='file'} for r in rows]},f,indent=2)
    else:
        cols=['file','type','axis','d_mm','center_a','center_b','from_mm','to_mm','length_mm','n_slices','max_dev_mm']
        with open(args.csv,'w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
            for r in rows:r=dict(r);r['center_a'],r['center_b']=r.pop('center');w.writerow(r)
if __name__=='__main__':
    try:main()
    except Exception as e:print('measure_holes:',e,file=sys.stderr);sys.exit(1)
