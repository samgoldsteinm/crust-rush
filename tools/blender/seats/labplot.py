import numpy as np, sys
from parts import src_game
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
k=sys.argv[1]; ids=list(map(int,sys.argv[2:])); T,L,names=src_game(k); c=T.mean(1)
fig,ax=plt.subplots(len(ids),2,figsize=(14,3.2*len(ids)))
for r,a in enumerate(ids):
    q=c[L==a]; ax[r,0].scatter(q[:,0],q[:,2],s=.5); ax[r,1].scatter(q[:,0],q[:,1],s=.5); ax[r,0].set_title(f'{a} {names[a][:60]} top'); ax[r,1].set_title('side')
    for x in ax[r]: x.set_aspect('equal')
plt.tight_layout(); plt.savefig(f'{k}_labs.png',dpi=55)
