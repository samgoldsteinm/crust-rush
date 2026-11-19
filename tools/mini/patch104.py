"""Patch 104 (web v237): the GT Racer's roof shows.
The owner: "Make sure to fix the roof on the gt racer as well" (earlier: "the gt racers roof is gone").
Why (scratch/paint/roofw.js, gtroof2.py): its roof is a one-sided carbon (class 6) panel modelled facing INTO the car (its normals
point down), so from outside it was culled: the car looked open. Drawn double-sided, the black roof appears.
- ROOF_FIX (gt): every carbon triangle in the roof zone (within .8 of the body's top, |z| < 1.3) gets a reversed twin (the
  roof two-sided: the detailed pack's roof faces point both ways) (winding reversed, normals negated) in b_vc. Both packs; the PC from the export.
Run once, after patch 103: tools/py.cmd tools/mini/patch104.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 104' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("  if(SHAPE_SYM[id.replace(/_hq$/,'')])shapeSym(g,'add');/* (patch 100) */",
    "  if(SHAPE_SYM[id.replace(/_hq$/,'')])shapeSym(g,'add');/* (patch 100) */\n  if(ROOF_FIX[id.replace(/_hq$/,'')]&&g.b_vc)g.b_vc=roofFix(g);/* (patch 104) */")
rep("function rotorMark(geo,os,sp){",
    "/* (patch 104) a roof modelled facing into the car: its carbon gets a facing-out twin */\nconst ROOF_FIX={gt:1};\n"
    "function roofFix(g){let yt=-1e9;for(const k in g){if(!k.startsWith('b_'))continue;const P=g[k].attributes.position;for(let i=0;i<P.count;i++)yt=Math.max(yt,P.getY(i));}\n"
    "  const G=g.b_vc,P=G.attributes.position,N=G.attributes.normal,C=G.attributes.color,U=G.attributes.uv,I=G.index.array,add=[];\n"
    "  for(let t=0;t<I.length;t+=3){if(Math.floor(U.getX(I[t])*32)!==6)continue;const cy=(P.getY(I[t])+P.getY(I[t+1])+P.getY(I[t+2]))/3,cz=(P.getZ(I[t])+P.getZ(I[t+1])+P.getZ(I[t+2]))/3;\n"
    "    if(cy<yt-.8||Math.abs(cz)>1.3)continue;add.push(t);}/* (every roof face: its twin makes it two-sided) */\n"
    "  if(!add.length)return G;const n0=P.count,nv=n0+add.length*3,pos=new Float32Array(nv*3),nor=new Float32Array(nv*3),col=new Float32Array(nv*3),uv=new Float32Array(nv*2);\n"
    "  pos.set(P.array.subarray(0,n0*3));nor.set(N.array.subarray(0,n0*3));col.set(C.array.subarray(0,n0*3));uv.set(U.array.subarray(0,n0*2));const idx=Array.from(I);let v=n0;\n"
    "  for(const t of add){for(const j of [0,2,1]){const i=I[t+j];pos.set([P.getX(i),P.getY(i),P.getZ(i)],v*3);nor.set([-N.getX(i),-N.getY(i),-N.getZ(i)],v*3);col.set([C.getX(i),C.getY(i),C.getZ(i)],v*3);uv.set([U.getX(i),U.getY(i)],v*2);idx.push(v);v++;}}\n"
    "  const ng=new THREE.BufferGeometry();ng.setAttribute('position',new THREE.BufferAttribute(pos,3));ng.setAttribute('normal',new THREE.BufferAttribute(nor,3));ng.setAttribute('color',new THREE.BufferAttribute(col,3));ng.setAttribute('uv',new THREE.BufferAttribute(uv,2));\n"
    "  ng.setIndex(new THREE.BufferAttribute(nv>65535?new Uint32Array(idx):new Uint16Array(idx),1));ng.computeBoundingSphere();CARGEO.add(ng);return ng;}\n"
    "function rotorMark(geo,os,sp){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 104 applied')
# the detailed GT pack's roof has a gap at the front (its model): the GT uses its standard pack everywhere (NO_HQ)
s = open(p, encoding='utf-8', newline='').read()
rep("function carBody(id,M,B){let g=carGeos(HQB&&hqReady(id)?id+'_hq':id);", "const NO_HQ={gt:1};/* (patch 104: its detailed roof has a gap) */\nfunction carBody(id,M,B){let g=carGeos(HQB&&hqReady(id)&&!NO_HQ[id]?id+'_hq':id);")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 104 NO_HQ applied')
# with the roof back, the driver sits lower (its head showed through the roof)
s = open(p, encoding='utf-8', newline='').read()
rep("gt(S,M,rc,idx,B){carBody('gt',M,B);return {car:'gt',fit:{open:1,rim:1.8,s:.22}", "gt(S,M,rc,idx,B){carBody('gt',M,B);return {car:'gt',fit:{open:1,rim:1.45,s:.22}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 104 driver applied')
