import numpy as np, sys, json
from parts import src_game
from dec import load
k=sys.argv[1]; T,L,names=src_game(k); h,_=load(k); W=h['wheels']
xs=sorted(w['c'][0] for w in W); r=max(w['r'] for w in W); hw=max(abs(w['c'][2]) for w in W)
c=T.mean(1); m=(c[:,0]>xs[0]+r*.6)&(c[:,0]<xs[-1]-r*.6)&(np.abs(c[:,2])<hw*.8)&(c[:,1]>0.4)
u,cnt=np.unique(L[m],return_counts=True); tot=np.bincount(L,minlength=len(names))
rows=[]
for a,b in zip(u,cnt):
    q=c[m&(L==a)]; rows.append((b,a,q.min(0),q.max(0),tot[a]))
rows.sort(key=lambda x:-x[0])
for b,a,lo,hi,t in rows[:int(sys.argv[2]) if len(sys.argv)>2 else 50]: print(f'{a:4d} {b:6d}/{t:6d} x[{lo[0]:5.2f},{hi[0]:5.2f}] y[{lo[1]:5.2f},{hi[1]:5.2f}] z[{lo[2]:5.2f},{hi[2]:5.2f}] {names[a][:70]}')
