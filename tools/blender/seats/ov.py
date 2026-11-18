import numpy as np, sys
from transfer import seat_mask
from parts import src_game
from dec import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
k=sys.argv[1]; T,L,names=src_game(k); sm=seat_mask(k,T,L,names,sys.argv[2:]); S=T.mean(1)[sm]
h,g=load(k); fig,ax=plt.subplots(1,2,figsize=(16,5))
for gn,(P,N,C,A,I) in g.items():
    if not gn.startswith('b_'): continue
    q=P[I].mean(1); tc=C[I[:,0]]
    for a,(i,j) in zip(ax,[(0,2),(0,1)]): a.scatter(q[:,i],q[:,j],s=1,c='#bbb' if gn!='b_vc' else plt.cm.tab20(tc%20))
for a,(i,j) in zip(ax,[(0,2),(0,1)]): a.scatter(S[::5,i],S[::5,j],s=.3,c='red'); a.set_aspect('equal')
plt.tight_layout(); plt.savefig(k+'_ov.png',dpi=60)
