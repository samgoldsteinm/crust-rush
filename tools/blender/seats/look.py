import numpy as np, sys
from dec import load
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
for k in sys.argv[1:]:
    h,g=load(k); P,N,C,A,I=g['b_vc']; tc=C[I[:,0]]; q=P[I].mean(1)
    fig,ax=plt.subplots(1,2,figsize=(15,4.5)); col=np.where(tc==9,'red',np.where(tc==1,'#999','#ccc'))
    o=np.argsort(tc==9)
    for a,(i,j) in zip(ax,[(0,2),(0,1)]): a.scatter(q[o,i],q[o,j],s=2,c=col[o]); a.set_aspect('equal')
    ax[0].set_title(k+' red = interior colour (top)'); ax[1].set_title('side'); plt.tight_layout(); plt.savefig(f'look_{k}.png',dpi=60)
