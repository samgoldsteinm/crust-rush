"""Patch 82 (web v224): the rim colour paints a kart's whole wheel (spokes too), not just its hub.
The owner: "changing the rim color doesnt change the tire spoke color currently like it should it only changes the brake drum in the
wheel". Cars were right (their wheel's metal classes are the rim). Karts were not:
- a kart's wheel set (WHEELS with pack 'wheelset', material M.rimW = rimVC(st, ds)) was recoloured only on the metal classes
  (7, 10, 11, 15, 19, 21); on those wheels the spokes are other classes, so only the hub turned. Now the wheel-set copy (uniform uAll)
  recolours every class but the tyre (rubber 8) and the caliper (13).
- the code-built wheels (buildWheel: standard, slick, monster, hub) never took the rim colour: the standard rim took the trim colour
  (M.dark) and its spokes the body paint. Now with a rim colour set (M.rimS) the rim, spokes, cap and hub take it.
Run once, after patch 81: py.cmd tools/mini/patch82.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 82' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const U={uR:{value:new THREE.Color(r.h)},uRM:{value:new THREE.Vector2(r.m?.95:.3,r.m?(r.r||.2):.38)}};",
    "const U={uR:{value:new THREE.Color(r.h)},uRM:{value:new THREE.Vector2(r.m?.95:.3,r.m?(r.r||.2):.38)},uAll:{value:ds?1:0}};/* (patch 82: a wheel set: all but tyre and caliper) */")
rep("sh.fragmentShader='uniform vec3 uR;uniform vec2 uRM;\\n'", "sh.fragmentShader='uniform vec3 uR;uniform vec2 uRM;uniform float uAll;\\n'")
rep("if(abs(rCi-7.)<.1||abs(rCi-10.)<.1||abs(rCi-11.)<.1||abs(rCi-15.)<.1||abs(rCi-19.)<.1||abs(rCi-21.)<.1){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=1.;}",
    "if((uAll>.5&&abs(rCi-8.)>.1&&abs(rCi-13.)>.1)||abs(rCi-7.)<.1||abs(rCi-10.)<.1||abs(rCi-11.)<.1||abs(rCi-15.)<.1||abs(rCi-19.)<.1||abs(rCi-21.)<.1){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=1.;}")
rep("const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),paint,",
    "const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),rimS:(()=>{const r=TRIMS[stOf(spec).rm|0];return r&&r.h?new THREE.MeshStandardMaterial({color:r.h,metalness:r.m?.95:.3,roughness:r.m?(r.r||.2):.38}):null;})()/* (patch 82: a code-built wheel's rim colour) */,paint,")
rep("hrx(P3(KG.rim,M.dark,0,0,0,W));", "hrx(P3(KG.rim,M.rimS||M.dark,0,0,0,W));")
rep("sp=P3(KG.spoke,M.paint,Math.cos(a)*.36", "sp=P3(KG.spoke,M.rimS||M.paint,Math.cos(a)*.36")
rep("sp=P3(KG.spokeHQ,M.paint,", "sp=P3(KG.spokeHQ,M.rimS||M.paint,")
rep("hrx(P3(KG.rimHQ[side>0?0:1],M.dark,0,0,0,W));", "hrx(P3(KG.rimHQ[side>0?0:1],M.rimS||M.dark,0,0,0,W));")
rep("hrx(P3(KG.hub,SH.chrome,0,0,0,W));}\n  if(type!=='hover')", "hrx(P3(KG.hub,M.rimS||SH.chrome,0,0,0,W));}\n  if(type!=='hover')")
rep("P3(KG.slickRing,M.stripe,0,0,side*.66,W);hrx(P3(HQB?KG.rimHQ[side>0?0:1]:KG.rim,SH.chrome,0,0,0,W));",
    "P3(KG.slickRing,M.stripe,0,0,side*.66,W);hrx(P3(HQB?KG.rimHQ[side>0?0:1]:KG.rim,M.rimS||SH.chrome,0,0,0,W));")
rep("sp=P3(KG.spoke,SH.metal,", "sp=P3(KG.spoke,M.rimS||SH.metal,")
rep("hrx(P3(KG.rim,SH.black,0,0,0,W));", "hrx(P3(KG.rim,M.rimS||SH.black,0,0,0,W));")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 82 applied')
