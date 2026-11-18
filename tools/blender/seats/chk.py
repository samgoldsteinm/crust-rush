import json, numpy as np, sys
sys.path.insert(0,'.')
import dec
for k in sys.argv[1:]:
    a=json.load(open('D:/crust-rush/scratch/cars_prev_seat/'+k+'.json'))['h']; b=json.load(open('D:/crust-rush/source/data/cars/'+k+'.json'))['h']
    assert a['wheels']==b['wheels'], k
    dm=[(x['n'],x['v'],y['v'],x['i'],y['i']) for x,y in zip(a['meta'],b['meta']) if x!=y]
    dec.D='D:/crust-rush/scratch/cars_prev_seat/'; _,ga=dec.load(k); dec.D='D:/crust-rush/source/data/cars/'; _,gb=dec.load(k)
    for n in ga:
        Pa=ga[n][0][ga[n][4]]; Pb=gb[n][0][gb[n][4]]
        sa=np.sort(Pa.reshape(len(Pa),-1).round(3),axis=0); sb=np.sort(Pb.reshape(len(Pb),-1).round(3),axis=0)
        assert sa.shape==sb.shape and np.allclose(sa,sb), (k,n)
    print(k,'shape identical; changed groups',dm)
