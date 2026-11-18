import numpy as np, sys
from transfer import seat_mask
from parts import src_game
k=sys.argv[1]; T,L,names=src_game(k); sm=seat_mask(k,T,L,names,sys.argv[2:]); np.save(k+'_seattris.npy',T[sm].astype(np.float32)); print(sm.sum())
