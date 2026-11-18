import json, numpy as np, sys
D='D:/crust-rush/source/data/cars/'
def load(k):
    h=json.load(open(D+k+'.json'))['h']; b=open(D+k+'.bin','rb').read(); o=0; out={}
    for m in h['meta']:
        v,i=m['v'],m['i']; P=np.frombuffer(b,'<i2',v*3,o).reshape(-1,3)/1000; o+=v*6
        N=np.frombuffer(b,np.int8,v*3,o).reshape(-1,3); o+=v*3; C=np.frombuffer(b,np.uint8,v,o); o+=v; A=np.frombuffer(b,np.uint8,v,o); o+=v
        if o%2: o+=1
        I=np.frombuffer(b,'<u2',i,o).reshape(-1,3); o+=i*2
        while o%4: o+=1
        if m.get('uv'): o+=v*8
        out[m['n']]=(P,N,C,A,I)
    assert o==len(b),(o,len(b)); return h,out
if __name__=='__main__':
    for k in sys.argv[1:]:
        h,g=load(k); P,N,C,A,I=g['b_vc']; tc=C[I[:,0]]
        u,c=np.unique(tc,return_counts=True); print(k, dict(zip(u.tolist(),c.tolist())))
        s=I[tc==9]; 
        if len(s): q=P[s].mean(1); print('  seat tris', len(s), 'x', q[:,0].min().round(2), q[:,0].max().round(2),'y',q[:,1].min().round(2),q[:,1].max().round(2),'z',q[:,2].min().round(2),q[:,2].max().round(2))
