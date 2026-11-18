import numpy as np, sys, re
from parts import src_game
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
k=sys.argv[1]; rx=sys.argv[2]; x0,x1=map(float,sys.argv[3:5]); T,L,names=src_game(k); c=T.mean(1)
ok=np.array([bool(re.search(rx,n,re.I)) for n in names])[L]&(c[:,0]>x0)&(c[:,0]<x1)
q=c[ok]; fig,ax=plt.subplots(1,3,figsize=(16,4.5))
ax[0].scatter(q[:,0],q[:,2],s=.5); ax[1].scatter(q[:,0],q[:,1],s=.5); ax[2].scatter(q[:,2],q[:,1],s=.5)
for a in ax: a.set_aspect('equal'); a.grid(True)
ax[0].set_title('top x/z'); ax[1].set_title('side x/y'); ax[2].set_title('front z/y'); plt.tight_layout(); plt.savefig(f'{k}_box.png',dpi=60)
