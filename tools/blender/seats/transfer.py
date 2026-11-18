"""transfer.py <car> sel... : seats from the source onto the existing pack (shape unchanged, only the class of cabin triangles)
sel: 'c:<comp ids comma>' (parts.json components) | 'r:<regex on mat@obj>' | 'm:<regex>' (material filter applied to the selected seats)"""
import numpy as np, sys, json, re, os, shutil
from dec import load
from parts import src_game
from align import nn
D='D:/crust-rush/source/data/cars/'; BK='D:/crust-rush/scratch/cars_prev_seat/'
def seat_mask(k,T,L,names,sels):
    sm=np.zeros(len(T),bool); mf=None
    for s in sels:
        t,v=s.split(':',1)
        if t=='c':
            d=json.load(open(k+'_parts.json')); idx=np.array(d['idx']); comp=np.array(d['comp']); sm[idx[np.isin(comp,[int(x) for x in v.split(',')])]]=True
        elif t=='r':
            ok=np.array([bool(re.search(v,n,re.I)) for n in names]); sm|=ok[L]
        elif t=='B':
            a=v.split(',',6); x0,x1,y0,y1,z0,z1=map(float,a[:6]); c=T.mean(1); ok=np.array([bool(re.search(a[6],n,re.I)) for n in names])[L]
            sm|=ok&(c[:,0]>x0)&(c[:,0]<x1)&(c[:,1]>y0)&(c[:,1]<y1)&(c[:,2]>z0)&(c[:,2]<z1)
        elif t=='m': mf=np.array([bool(re.search(v,n,re.I)) for n in names])[L]
    if mf is not None: sm&=mf
    return sm
def nnd(a,b):
    if len(b)>40000: b=b[np.random.default_rng(1).choice(len(b),40000,replace=False)]
    return nn(a,b,ch=150)
def write(k,h,g):
    blob=bytearray()
    for m in h['meta']:
        P,N,C,A,I,UV=g[m['n']]
        blob+=np.round(P*1000).astype('<i2').tobytes()+N.astype(np.int8).tobytes()+C.astype(np.uint8).tobytes()+A.astype(np.uint8).tobytes()
        if len(blob)%2: blob+=b'\0'
        blob+=I.astype('<u2').tobytes()
        while len(blob)%4: blob+=b'\0'
        if UV is not None: blob+=UV.astype('<f4').tobytes()
        m['v']=len(P); m['i']=I.size
    open(D+k+'.bin','wb').write(bytes(blob)); json.dump({'h':h},open(D+k+'.json','w'),separators=(',',':'))
def regroup(P,N,C,A,I,tc):
    rows=np.concatenate([np.round(P[I.ravel()]*1000),N[I.ravel()].astype(np.int32),np.repeat(tc,3)[:,None],A[I.ravel()][:,None]],1).astype(np.int32)
    u,inv=np.unique(rows,axis=0,return_inverse=True); assert len(u)<65535
    return u[:,:3]/1000,u[:,3:6],u[:,6],u[:,7],inv.reshape(-1,3)
def run(k,sels,pk,cls_from=(1,9),dmax=.25,dry=False):
    T,L,names=src_game(k); sm=seat_mask(k,T,L,names,sels); c=T.mean(1)
    h,_=load(pk); W=h['wheels']; xs=sorted(w['c'][0] for w in W) or [-99,99]; r=max([w['r'] for w in W] or [0]); hw=max([abs(w['c'][2]) for w in W] or [99])
    box=lambda q:(q[:,0]>xs[0]+r*.3)&(q[:,0]<xs[-1]-r*.3)&(np.abs(q[:,2])<hw*.9)&(q[:,1]>0.3)
    big=(c[:,0]>xs[0]-r)&(c[:,0]<xs[-1]+r)&(c[:,1]>0.2); S=c[sm]; O=c[big&~sm]; print(pk,'source seat tris',sm.sum(),'other cabin',len(O))
    raw=open(D+pk+'.bin','rb').read(); hh=json.load(open(D+pk+'.json'))['h']; _,g=load(pk)
    # keep each group's livery uvs
    o=0; G={}
    for m in hh['meta']:
        v,i=m['v'],m['i']; o+=v*8; o+=o%2; o+=i*2; o+=(-o)%4; uv=None
        if m.get('uv'): uv=np.frombuffer(raw,'<f4',v*2,o); o+=v*8
        G[m['n']]=list(g[m['n']])+[uv]
    stats={}
    for gn in ('b_vc','l_vc'):
        if gn not in G: continue
        P,N,C,A,I,UV=G[gn]; tc=C[I[:,0]].astype(np.int32); q=P[I].mean(1); cand=np.where(box(q)&np.isin(tc,cls_from))[0]
        ds=nnd(q[cand],S); do=nnd(q[cand],O); seat=(ds<dmax)&(ds<do)
        new=tc.copy(); new[cand[seat]]=9;
        new[(tc==9)]=1; new[cand[seat]]=9
        stats[gn]=(int((tc==9).sum()),int((new==9).sum()))
        if not dry: G[gn][:5]=regroup(P,N,C,A,I,new)
        G[gn+'_new']=new
    print('  seat tris before/after',stats)
    if not dry:
        os.makedirs(BK,exist_ok=True)
        for e in ('.bin','.json'):
            if not os.path.exists(BK+pk+e): shutil.copy(D+pk+e,BK+pk+e)
        write(pk,hh,{n:G[n] for n in [m['n'] for m in hh['meta']]})
    return G
if __name__=='__main__':
    k=sys.argv[1]; dry=os.environ.get('DRY')=='1'; sels=sys.argv[2:]
    for pk in [k,k+'_hq']:
        if os.path.exists(D+pk+'.bin'): run(k,sels,pk,dry=dry,cls_from=tuple(int(x) for x in os.environ.get('CLS','1,9').split(',')))
