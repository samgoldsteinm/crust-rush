import numpy as np, sys, itertools, json
from dec import load
def packpts(k):
    h,g=load(k); pts=[]
    for n,(P,N,C,A,I) in g.items():
        if n.startswith('b_'): pts.append(P[I].mean(1))
    for i,w in enumerate(h['wheels']):
        if f'w{i}' in g: P,N,C,A,I=g[f'w{i}']; pts.append(P[I].mean(1)+np.array(w['c']))
    return np.concatenate(pts)
def nn(a,b,ch=400):
    out=np.empty(len(a))
    for i in range(0,len(a),ch): out[i:i+ch]=np.sqrt(((a[i:i+ch,None,:]-b[None])**2).sum(-1).min(1))
    return out
def fit(k,pk=None):
    Q=packpts(pk or k); z=np.load(k+'.npz'); S=z['T'].mean(1)
    rng=np.random.default_rng(0); qs=Q[rng.choice(len(Q),min(1500,len(Q)),replace=False)]; ss=S[rng.choice(len(S),min(6000,len(S)),replace=False)]
    qc=(Q.min(0)+Q.max(0))/2; qe=Q.max(0)-Q.min(0); best=None
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product([1,-1],repeat=3):
            R=np.zeros((3,3)); 
            for i in range(3): R[i,perm[i]]=sg[i]
            X=ss@R.T; lo,hi=np.percentile(X,[.3,99.7],axis=0); c=(lo+hi)/2; e=hi-lo; s=qe[0]/e[0]
            if not (0.7<(e[1]*s)/qe[1]<1.4 and 0.7<(e[2]*s)/qe[2]<1.4): continue
            Y=(X-c)*s+qc; d=nn(qs,Y).mean()
            if best is None or d<best[0]: best=(d,R,c,s)
    d,R,c,s=best; print(k,'fit err',round(d,3),'scale',s); return R,c,s,qc
if __name__=='__main__':
    for k in sys.argv[1:]:
        R,c,s,qc=fit(k); np.savez(k+'_al.npz',R=R,c=c,s=s,qc=qc)
