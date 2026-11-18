import numpy as np, sys, json, os, shutil
import dec
from transfer import write, BK, D
k=sys.argv[1]; Z=np.load(k+'_seat.npz')
for pk,tg in ((k,1326),(k+'_hq',1799)):
    if not os.path.exists(D+pk+'.bin'): continue
    P,F,N=Z[f'P{700 if tg==1326 else 1800}'],Z[f'F{700 if tg==1326 else 1800}'],Z[f'N{700 if tg==1326 else 1800}']
    P=P.copy(); N=N.copy(); P[:,2]*=-1; N[:,2]*=-1          # undo the fit's mirror: the model's own left and right
    fn=np.cross(P[F[:,1]]-P[F[:,0]],P[F[:,2]]-P[F[:,0]]); vn=np.zeros_like(P)
    for j in range(3): np.add.at(vn,F[:,j],fn)
    if (vn*N).sum(1).mean()<0: N=-N
    raw=open(D+pk+'.bin','rb').read(); hh=json.load(open(D+pk+'.json'))['h']; _,g=dec.load(pk)
    o=0; G={}
    for m in hh['meta']:
        v,i=m['v'],m['i']; o+=v*8; o+=o%2; o+=i*2; o+=(-o)%4; uv=None
        if m.get('uv'): uv=np.frombuffer(raw,'<f4',v*2,o); o+=v*8
        G[m['n']]=list(g[m['n']])+[uv]
    Pv,Nv,Cv,Av,Iv,_=G['b_vc']; tc=Cv[Iv[:,0]]; ao=int(np.median(Av[Iv[tc==1].ravel()]))
    n0=len(Pv); G['b_vc'][:5]=[np.r_[Pv,P],np.r_[Nv,np.round(N*127).clip(-127,127)],np.r_[Cv,np.full(len(P),9)],np.r_[Av,np.full(len(P),ao)],np.r_[Iv,F+n0]]
    assert len(G['b_vc'][0])<65535
    os.makedirs(BK,exist_ok=True)
    for e in ('.bin','.json'):
        if not os.path.exists(BK+pk+e): shutil.copy(D+pk+e,BK+pk+e)
    write(pk,hh,G); print(pk,'added',len(F),'seat tris, ao',ao)
