import numpy as np, sys, json
from dec import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def src_game(k):
    z=np.load(k+'.npz'); a=np.load(k+'_al.npz'); T=z['T']; X=((T.reshape(-1,3)@a['R'].T)-a['c'])*a['s']+a['qc']; return X.reshape(-1,3,3),z['L'],z['names']
def comps(T):
    V=T.reshape(-1,3); _,pid=np.unique(np.round(V,4),axis=0,return_inverse=True); pid=pid.ravel(); J=pid.reshape(-1,3)
    n=pid.max()+1; par=np.arange(n)
    # vectorised union-find by iterative min-label propagation
    lab=np.arange(n)
    for _ in range(200):
        m=np.minimum(np.minimum(lab[J[:,0]],lab[J[:,1]]),lab[J[:,2]]); old=lab.copy()
        for j in range(3): np.minimum.at(lab,J[:,j],m)
        lab=lab[lab]
        if (lab==old).all(): break
    return lab[J[:,0]]
def cabin_box(k):
    h,g=load(k); P,N,C,A,I=g['b_glass']; q=P[I].mean(1)
    lo=q.min(0); hi=q.max(0); return lo,hi
if __name__=='__main__':
    k=sys.argv[1]; T,L,names=src_game(k); h,_=load(k); W=h['wheels']
    xs=sorted(w['c'][0] for w in W) or [-99,99]; r=max([w['r'] for w in W] or [0]); hw=max([abs(w['c'][2]) for w in W] or [99])
    c=T.mean(1); m=(c[:,0]>xs[0]+r*.6)&(c[:,0]<xs[-1]-r*.6)&(np.abs(c[:,2])<hw*.8)&(c[:,1]>0.4)
    idx=np.where(m)[0]; tl=comps(T[idx]); u,inv,cnt=np.unique(tl,return_inverse=True,return_counts=True)
    rows=[]
    for j,(uu,cc) in enumerate(zip(u,cnt)):
        s=idx[inv==j]; q=T[s].reshape(-1,3); mats=np.unique(L[s]); 
        rows.append((cc,j,q.min(0),q.max(0),[names[x][:40] for x in mats[:3]]))
    rows.sort(key=lambda r:-r[0]); json.dump({'idx':idx.tolist(),'comp':inv.tolist()},open(k+'_parts.json','w'))
    for cc,j,a,b,mm in rows[:int(__import__('os').environ.get('NR','60'))]: print(f'{j:4d} {cc:6d} x[{a[0]:5.2f},{b[0]:5.2f}] y[{a[1]:5.2f},{b[1]:5.2f}] z[{a[2]:5.2f},{b[2]:5.2f}]', mm)
    fig,ax=plt.subplots(2,1,figsize=(13,11)); top=[r[1] for r in rows[:30]]
    for j in top:
        s=idx[inv==j]; q=c[s]; col=plt.cm.tab20(j%20)
        ax[0].scatter(q[:,0],q[:,2],s=1,color=col); ax[1].scatter(q[:,0],q[:,1],s=1,color=col)
        mq=q.mean(0); ax[0].text(mq[0],mq[2],str(j),fontsize=8); ax[1].text(mq[0],mq[1],str(j),fontsize=8)
    for a in ax: a.set_aspect('equal')
    plt.tight_layout(); plt.savefig(k+'_parts.png',dpi=65)
