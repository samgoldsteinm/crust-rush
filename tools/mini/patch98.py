"""Patch 98 (web v233): the Chariot's accent is symmetrical.
The owner (the Chariot from the front with an accent): "can we fix these accents so they are symettrical". The Chariot's model has its
carbon (class 6) panels laid out differently on its two sides; the accent paints carbon (patch 89), so the patches showed lopsided. The
stock look (carbon is dark) stays as the owner designed it.
- symAcc (carGeos, ACC_SYM: chariot): a carbon triangle whose mirror point (z -> 2 zc - z, zc the body's centre) is not on a carbon
  surface (within .06) is labelled dark 1 (uv only): carbon and dark have the same colour and finish (CAR_PBR), so nothing changes until
  an accent is picked. Measured (scratch/paint/sym3.js): 33% of the Chariot's carbon and chrome has no twin; the other cars are
  symmetric once their centre is used (Hyper 0%, Monster 3%) or their odd pieces are real one-sided parts.
- PC: the labels come with the export.
Run once, after patch 97: tools/py.cmd tools/mini/patch98.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 98' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */",
    "  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */\n"
    "  if(ACC_SYM[id.replace(/_hq$/,'')])symAcc(g);/* (patch 98) */")
rep("function rotorMark(geo,os,sp){",
    "/* (patch 98) a body whose carbon is laid out differently on its two sides: carbon with no twin across the middle becomes dark 1 (same look) */\n"
    "const ACC_SYM={chariot:1};\n"
    "function symAcc(g){const T=[];let z0=1e9,z1=-1e9;for(const k in g){if(!k.startsWith('b_'))continue;const P=g[k].attributes.position;for(let i=0;i<P.count;i++){const z=P.getZ(i);if(z<z0)z0=z;if(z>z1)z1=z;}}const zc=(z0+z1)/2;\n"
    "  for(const k in g){if(!k.startsWith('b_')||!g[k].attributes.uv||!g[k].index)continue;const geo=g[k],P=geo.attributes.position,uv=geo.attributes.uv,I=geo.index.array;\n"
    "    for(let t=0;t<I.length;t+=3){if(Math.floor(uv.getX(I[t])*32)!==6)continue;const a=new THREE.Vector3().fromBufferAttribute(P,I[t]),b=new THREE.Vector3().fromBufferAttribute(P,I[t+1]),d=new THREE.Vector3().fromBufferAttribute(P,I[t+2]);T.push({uv,I,t,a,b,d,m:a.clone().add(b).add(d).divideScalar(3)});}}\n"
    "  const cs=.3,H=new Map(),cl=(x)=>Math.floor(x/cs);for(const e of T)for(let x=cl(Math.min(e.a.x,e.b.x,e.d.x));x<=cl(Math.max(e.a.x,e.b.x,e.d.x));x++)for(let y=cl(Math.min(e.a.y,e.b.y,e.d.y));y<=cl(Math.max(e.a.y,e.b.y,e.d.y));y++)for(let z=cl(Math.min(e.a.z,e.b.z,e.d.z));z<=cl(Math.max(e.a.z,e.b.z,e.d.z));z++){const kk=x+','+y+','+z;(H.get(kk)||H.set(kk,[]).get(kk)).push(e);}\n"
    "  const v=new THREE.Vector3(),tr=new THREE.Triangle(),cp=new THREE.Vector3(),un=[];for(const e of T){if(Math.abs(e.m.z-zc)<.06)continue;v.set(e.m.x,e.m.y,2*zc-e.m.z);let ok=false;\n"
    "    for(const u of H.get(cl(v.x)+','+cl(v.y)+','+cl(v.z))||[]){tr.set(u.a,u.b,u.d);tr.closestPointToPoint(v,cp);if(cp.distanceTo(v)<.06){ok=true;break;}}if(!ok)un.push(e);}\n"
    "  for(const e of un)for(let j=0;j<3;j++)e.uv.setX(e.I[e.t+j],(1+.5)/32);for(const k in g)if(g[k].attributes.uv)g[k].attributes.uv.needsUpdate=true;}\n"
    "function rotorMark(geo,os,sp){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 98 applied')
