"""Patch 105 (web v238): the GT Racer's roof over its whole cabin; the Hypercar's glass roof shows; the Hypercar's driver fits.
The owner (the GT in the garage still open over the driver; the Hypercar): "The roof is missing on this car as well"; "Make the
characters smaller so they fit into this car better after you fix the roof"; "Did you lower the driver to fit better in this car too?"
- GT: roofFix's zone went only .8 below the top; the roof slopes down to the windscreen. Now 1.5 (every carbon triangle over the cabin,
  |z| < 1.3, two-sided).
- Hypercar: its roof is a glass canopy (scratch/paint/hyglass.js: b_glass at roof height) drawn at 18% opacity: it read as no roof.
  GLASS_ROOF (hyper): the glass triangles facing up (normal y > .45) within .9 of the top are split out and drawn as smoked glass
  (near-black, 88% opaque, glossy). Its side windows and windscreen stay clear.
- Hypercar driver: fit s .32 -> .24, rim 1.6 -> 1.35 (smaller and lower, under the canopy).
- PC: from the export.
Run once, after patch 104: tools/py.cmd tools/mini/patch105.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 105' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("    if(cy<yt-.8||Math.abs(cz)>1.3)continue;add.push(t);}", "    if(cy<yt-1.5||Math.abs(cz)>1.3)continue;add.push(t);}/* (patch 105: the whole sloping roof) */")
rep("hyper(S,M,rc,idx,B){carBody('hyper',M,B);return {car:'hyper',fit:{open:1,rim:1.6,s:.32,lean:.3}",
    "hyper(S,M,rc,idx,B){carBody('hyper',M,B);return {car:'hyper',fit:{open:1,rim:1.35,s:.24,lean:.3}/* (patch 105: smaller, lower) */")
rep("  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);",
    "  /* (patch 105) a glass roof drawn smoked, so it reads as a roof */\n"
    "  if(GLASS_ROOF[cid]&&g.b_glass){const sp=glassRoofSplit(g);if(sp){const me=new THREE.Mesh(sp.roof,GLASS_ROOF_M||(GLASS_ROOF_M=new THREE.MeshPhysicalMaterial({color:'#0b0d10',roughness:.05,metalness:.1,clearcoat:1,transparent:true,opacity:.88,envMapIntensity:1.1})));me.castShadow=true;B.add(me);g={...g,b_glass:sp.rest};}}\n"
    "  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);")
rep("const TAIL_ROOF={interceptor:2.2},TAIL_DEEP={interceptor:1};",
    "const TAIL_ROOF={interceptor:2.2},TAIL_DEEP={interceptor:1},GLASS_ROOF={hyper:1};let GLASS_ROOF_M=null;\n"
    "function glassRoofSplit(g){const geo=g.b_glass;if(geo.userData.roofsplit!==undefined)return geo.userData.roofsplit;geo.userData.roofsplit=null;let yt=-1e9;for(const k in g){if(!k.startsWith('b_'))continue;const P=g[k].attributes.position;for(let i=0;i<P.count;i++)yt=Math.max(yt,P.getY(i));}\n"
    "  const P=geo.attributes.position,N=geo.attributes.normal,I=geo.index&&geo.index.array;if(!I||!N)return null;const a=[],b=[];\n"
    "  for(let t=0;t<I.length;t+=3){const cy=(P.getY(I[t])+P.getY(I[t+1])+P.getY(I[t+2]))/3,ny=Math.abs(N.getY(I[t])+N.getY(I[t+1])+N.getY(I[t+2]))/3;((cy>yt-.9&&ny>.45)?b:a).push(I[t],I[t+1],I[t+2]);}if(!b.length)return null;\n"
    "  const mk=ix=>{const ng=new THREE.BufferGeometry();for(const k in geo.attributes)ng.setAttribute(k,geo.attributes[k]);ng.setIndex(new THREE.BufferAttribute(I instanceof Uint32Array?new Uint32Array(ix):new Uint16Array(ix),1));ng.computeBoundingSphere();CARGEO.add(ng);return ng;};\n"
    "  return geo.userData.roofsplit={rest:mk(a),roof:mk(b)};}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 105 applied')
