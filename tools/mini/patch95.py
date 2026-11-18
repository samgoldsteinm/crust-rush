"""Patch 95 (web v230): the owner's notes on v229.
1. Slipstream: "that red line on the wheel is moving with the wheel when it's supposed to be stationary": a red crescent (class 17,
   36 triangles, under 160 degrees) in the wheel model: held (WHEEL_HOLD slip, patch 88): it steers, does not roll, keeps its red.
2. Accent "random spots ... that don't actually cover a part of the car" (Slipstream's wing and nose): those were the Slipstream's
   black decal patches (class 1, ACC_X from 89). ACC_X loses slip and concept (its body is covered in black decal patches); the Onyx's accent left its carbon engine cover (ACC_NO6 onyx:
   "the onyx cars spoiler is messed up": a white accent turned the cover's carbon white). Every vehicle checked again from four sides
   (scratch/paint/accall.js).
3. Interceptor: "the taillights and top lights are still orange and it looks weird": the four roof slots are tail-lamp material
   (they glowed): now trim (the Trim colour, stock near-black); its tail lamps a deeper red with less glow (TAIL_DEEP).
4. GT Racer: "The character currently is really big": fit.s .4 -> .22.
PC: pc90 (ACC_X / ACC_NO6; the rest comes with the export).
Run once, after patch 94: tools/py.cmd tools/mini/patch95.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 95' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("bike_mx:{any:1,n:1,r1:.86},", "bike_mx:{any:1,n:1,r1:.86},slip:{cls:[17]}/* (patch 95: the red crescent) */,")
rep("retrogt:7,coupe:1,concept:1,muscle:1,slip:1},ACC_NO6={slip:1};", "retrogt:7,coupe:1,muscle:1},ACC_NO6={slip:1,onyx:1};/* (patch 95: not the Slipstream's decals, not the Onyx's carbon cover) */")
rep("gt(S,M,rc,idx,B){carBody('gt',M,B);return {car:'gt',fit:{open:1,rim:1.8,s:.4},", "gt(S,M,rc,idx,B){carBody('gt',M,B);return {car:'gt',fit:{open:1,rim:1.8,s:.22}/* (patch 95: smaller) */,")
# the Interceptor's roof slots and deeper tail lamps
rep("  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);",
    "  /* (patch 95) tail-lamp material that is not a lamp (roof slots above TAIL_ROOF): the Trim colour; TAIL_DEEP: a deeper red lamp */\n"
    "  const cid=id.replace(/_hq$/,'');if(TAIL_DEEP[cid]){mats.tail=M.tailM.clone();mats.tail.color.set('#b3000c');mats.tail.emissive.set('#a0000a');mats.tail.emissiveIntensity=.45;}\n"
    "  if(TAIL_ROOF[cid]!=null&&g.b_tail){const sp=tailSplit(g.b_tail,TAIL_ROOF[cid]);if(sp){const tr=TRIMS[(M.st&&M.st.tr)|0];const me=new THREE.Mesh(sp.roof,new THREE.MeshStandardMaterial({color:tr&&tr.h||'#161618',metalness:tr&&tr.m?.9:.3,roughness:tr&&tr.m?(tr.r||.22):.45}));me.castShadow=true;me.receiveShadow=true;B.add(me);g={...g,b_tail:sp.lamp};}}\n"
    "  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);")
rep("function carBody(id,M,B){",
    "const TAIL_ROOF={interceptor:2.2},TAIL_DEEP={interceptor:1};\n"
    "function tailSplit(geo,y0){if(geo.userData.tsplit!==undefined)return geo.userData.tsplit;const P=geo.attributes.position,I=geo.index&&geo.index.array;geo.userData.tsplit=null;if(!I)return null;const a=[],b=[];\n"
    "  for(let t=0;t<I.length;t+=3)((P.getY(I[t])+P.getY(I[t+1])+P.getY(I[t+2]))/3>y0?b:a).push(I[t],I[t+1],I[t+2]);if(!b.length)return null;\n"
    "  const mk=ix=>{const g=new THREE.BufferGeometry();for(const k in geo.attributes)g.setAttribute(k,geo.attributes[k]);g.setIndex(new THREE.BufferAttribute(new Uint16Array(ix),1));g.computeBoundingSphere();CARGEO.add(g);return g;};\n"
    "  return geo.userData.tsplit={lamp:mk(a),roof:mk(b)};}\n"
    "function carBody(id,M,B){let g0;")
rep("function carBody(id,M,B){let g0;const g=carGeos(", "function carBody(id,M,B){let g=carGeos(")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 95 applied')
