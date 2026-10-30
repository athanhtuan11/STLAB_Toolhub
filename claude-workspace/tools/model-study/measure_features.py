#!/usr/bin/env python3
"""Measure cylindrical surface features in a triangulated mesh."""
import argparse, json, sys
import numpy as np
import trimesh

def unit(v):
    n=np.linalg.norm(v)
    return v/n if n>1e-12 else v

def fit_circle(p):
    x,y=p[:,0],p[:,1]
    a,b,c=np.linalg.lstsq(np.column_stack((2*x,2*y,np.ones(len(x)))),x*x+y*y,rcond=None)[0]
    r2=c+a*a+b*b
    if r2<=0:return None
    r=float(np.sqrt(r2)); e=np.linalg.norm(p-[a,b],axis=1)-r
    return np.array([a,b]),r,float(np.sqrt(np.mean(e*e)))

def measure_mesh(mesh: trimesh.Trimesh) -> dict:
    mesh=mesh.copy(); mesh.remove_unreferenced_vertices()
    faces,normals=mesh.faces,mesh.face_normals
    parent=np.arange(len(faces))
    def root(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def join(a,b):
        ra,rb=root(int(a)),root(int(b))
        if ra!=rb:parent[rb]=ra
    for (a,b),ang in zip(mesh.face_adjacency,mesh.face_adjacency_angles):
        if ang<np.radians(30):join(a,b)
    regs={}
    for i in range(len(faces)):regs.setdefault(root(i),[]).append(i)
    cs=[]
    for ids in regs.values():
        if len(ids)<3:continue
        ns=normals[ids]; mn=unit(ns.mean(axis=0))
        if np.mean(np.linalg.norm(ns-mn,axis=1))<.015:continue
        vals,vecs=np.linalg.eigh(ns.T@ns/len(ns)); axis=unit(vecs[:,np.argmin(vals)])
        if vals.min()>.08:continue
        pts=mesh.vertices[np.unique(faces[ids].reshape(-1))]
        ref=np.eye(3)[np.argmin(np.abs(axis))]; u=unit(np.cross(axis,ref)); v=np.cross(axis,u)
        q=np.column_stack((pts@u,pts@v)); fit=fit_circle(q)
        if fit is None:continue
        cc,r,rms=fit
        if r<.15 or rms>.02*r:continue
        c2=cc[0]*u+cc[1]*v; h=pts@axis; lo,hi=float(h.min()),float(h.max())
        if hi-lo<.05:continue
        rel=pts-(c2+h[:,None]*axis); theta=np.sort(np.mod(np.arctan2(rel@v,rel@u),2*np.pi))
        gaps=np.diff(np.r_[theta,theta[0]+2*np.pi])
        coverage=float(np.degrees(2*np.pi-gaps.max()))
        radial=np.mean(np.sum(ns*(mesh.triangles_center[ids]-c2),axis=1))
        cs.append(dict(axis=axis,center=c2+(lo+hi)/2*axis,r=r,lo=lo,hi=hi,rms=rms,cov=coverage,kind='hole' if radial<0 else 'boss',faces=set(ids)))
    merged=[]
    for c in cs:
        m=next((m for m in merged if abs(np.dot(c['axis'],m['axis']))>=np.cos(np.radians(1)) and abs(c['r']-m['r'])<=.02 and np.linalg.norm((c['center']-m['center'])-np.dot(c['center']-m['center'],m['axis'])*m['axis'])<=.02 and c['kind']==m['kind']),None)
        if m is None:merged.append(c)
        else:
            m['faces']|=c['faces'];m['lo']=min(m['lo'],c['lo']);m['hi']=max(m['hi'],c['hi']);m['cov']=min(360,m['cov']+c['cov']);m['rms']=max(m['rms'],c['rms'])
    out=[]
    for i,c in enumerate(merged,1):
        typ=c['kind'] if c['cov']>=300 else 'arc'; conf=max(0.,1-4*c['rms']/c['r'])*min(1.,c['cov']/300)
        if len(c['faces'])<12:conf*=.75
        f=dict(id=i,type=typ,d_mm=round(2*c['r'],4),axis=np.round(c['axis'],6).tolist(),center=np.round(c['center'],5).tolist(),length_mm=round(c['hi']-c['lo'],4),coverage_deg=round(c['cov'],2),rms_mm=round(c['rms'],5),confidence=round(float(conf),4),n_faces=len(c['faces']))
        if typ=='hole':
            centers=mesh.triangles_center; heights=centers@c['axis']
            relc=centers-heights[:,None]*c['axis']
            axcenter=c['center']-np.dot(c['center'],c['axis'])*c['axis']
            radial=np.linalg.norm(relc-axcenter,axis=1)
            planar=np.abs(mesh.face_normals@c['axis'])>.999
            blocked=[bool(np.any(planar & (np.abs(heights-end)<1e-4) & (radial<c['r']*.98))) for end in (c['lo'],c['hi'])]
            f['through']=not any(blocked)
        out.append(f)
    groups=[]
    for i,a in enumerate(out):
        if a['type']!='hole':continue
        for b in out[i+1:]:
            if b['type']!='hole' or abs(a['d_mm']-b['d_mm'])<.05:continue
            ax=np.asarray(a['axis']); bx=np.asarray(b['axis'])
            if abs(np.dot(ax,bx))<np.cos(np.radians(1)):continue
            delta=np.asarray(a['center'])-b['center']
            if np.linalg.norm(delta-delta.dot(ax)*ax)>.05:continue
            small,large=(a,b) if a['d_mm']<b['d_mm'] else (b,a)
            depth=abs(float(np.dot(np.asarray(large['center'])-small['center'],ax)))
            if depth>.05:groups.append(dict(type='counterbore',members=[small['id'],large['id']],depth_mm=round(depth,4),axis=small['axis']))
    return dict(units='mm',n_faces=int(len(faces)),features=out,groups=groups)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('files',nargs='+');ap.add_argument('--json',required=True);a=ap.parse_args();out=[]
    for path in a.files:
        try:
            m=trimesh.load(path,force='mesh')
            if not isinstance(m,trimesh.Trimesh) or not len(m.faces):raise ValueError('empty or unsupported mesh')
            out.append(dict(file=path,**measure_mesh(m)))
        except Exception as e:print(f'{path}: {e}',file=sys.stderr);return 1
    with open(a.json,'w',encoding='utf-8') as f:json.dump(out[0] if len(out)==1 else out,f,ensure_ascii=False,indent=1)
    return 0
if __name__=='__main__':sys.exit(main())
