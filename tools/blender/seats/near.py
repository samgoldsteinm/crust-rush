import numpy as np, sys
from transfer import seat_mask, nnd
from parts import src_game
from dec import load
k=sys.argv[1]; T,L,names=src_game(k); sm=seat_mask(k,T,L,names,sys.argv[2:]); S=T.mean(1)[sm]
h,g=load(k)
for gn,(P,N,C,A,I) in g.items():
    if not gn.startswith('b_'): continue
    q=P[I].mean(1); d=nnd(q,S); tc=C[I[:,0]]; m=d<.2
    if m.sum(): print(gn, dict(zip(*[x.tolist() for x in np.unique(tc[m],return_counts=True)])))
