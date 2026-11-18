import numpy as np, sys
src,out=sys.argv[1:3]; V=[]; T=[]; L=[]; names=[]; cur=0
for line in open(src,encoding='utf-8',errors='ignore'):
    if line.startswith('v '): V.append([float(x) for x in line.split()[1:4]])
    elif line.startswith('usemtl'):
        n=line.split(None,1)[1].strip()
        if n not in names: names.append(n)
        cur=names.index(n)
    elif line.startswith('f '):
        ix=[int(p.split('/')[0]) for p in line.split()[1:]]; ix=[i-1 if i>0 else len(V)+i for i in ix]
        for j in range(1,len(ix)-1): T.append((ix[0],ix[j],ix[j+1])); L.append(cur)
V=np.array(V,np.float32); T=np.array(T)
if not names: names=['none']
np.savez_compressed(out,T=V[T],L=np.array(L),names=np.array(names)); print(len(T),'tris',len(names),'mats')
