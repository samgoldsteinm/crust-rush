"""Patch 82 (web v224): the rim colour paints the wheel's spokes and the brake caliper, nothing else.
The owner: "changing the rim color doesnt change the tire spoke color currently like it should it only changes the brake drum in the
wheel"; then, on the first try (which painted a kart's whole wheel): "the entire wheel shouldnt change colors only the brake caliper and
the wheel spokes".
- a kart's wheel set (WHEELS pack 'wheelset', M.rimW = rimVC(st, ds)): its spokes are its own colour class (redline red 17, emerald and
  stealth green 16, turbo bluem 18, forged bronze 19; forged's red is its caliper), so the wheel-set copy (uniform uAll) recolours
  13, 16, 17, 18, 19 and no longer the metal classes (on these wheels the hub: "only the brake drum").
- a car's own wheels (rimM) keep their rim classes (the spokes) and add the caliper (13).
- the code-built wheels: only the spokes take the rim colour (standard KG.spoke / spokeHQ, slick's spokes; M.rimS); rim, hub, cap stay.
- a car body's calipers (class 13 in the body, which took the ACCENT colour in styleVC) take the rim colour when one is chosen.
Run once, after patch 81: py.cmd tools/mini/patch82.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 82' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# rimVC: wheel sets their spoke classes and the caliper; a car's wheels the rim classes and the caliper
rep("const U={uR:{value:new THREE.Color(r.h)},uRM:{value:new THREE.Vector2(r.m?.95:.3,r.m?(r.r||.2):.38)}};",
    "const U={uR:{value:new THREE.Color(r.h)},uRM:{value:new THREE.Vector2(r.m?.95:.3,r.m?(r.r||.2):.38)},uAll:{value:ds?1:0}};/* (patch 82: a wheel set's spoke classes) */")
rep("sh.fragmentShader='uniform vec3 uR;uniform vec2 uRM;\\n'", "sh.fragmentShader='uniform vec3 uR;uniform vec2 uRM;uniform float uAll;\\n'")
rep("if(abs(rCi-7.)<.1||abs(rCi-10.)<.1||abs(rCi-11.)<.1||abs(rCi-15.)<.1||abs(rCi-19.)<.1||abs(rCi-21.)<.1){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=1.;}",
    "if(abs(rCi-13.)<.1||(uAll>.5?(abs(rCi-16.)<.1||abs(rCi-17.)<.1||abs(rCi-18.)<.1||abs(rCi-19.)<.1):(abs(rCi-7.)<.1||abs(rCi-10.)<.1||abs(rCi-11.)<.1||abs(rCi-15.)<.1||abs(rCi-19.)<.1||abs(rCi-21.)<.1))){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=abs(rCi-13.)<.1?2.:1.;}")
rep("+'if(rG==1.){metalnessFactor=uRM.x;roughnessFactor=uRM.y;}');", "+'if(rG==1.){metalnessFactor=uRM.x;roughnessFactor=uRM.y;}');/* (a caliper, rG 2, keeps its painted finish) */")
# code-built wheels: the spokes only
rep("const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),paint,",
    "const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),rimS:(()=>{const r=TRIMS[stOf(spec).rm|0];return r&&r.h?new THREE.MeshStandardMaterial({color:r.h,metalness:r.m?.95:.3,roughness:r.m?(r.r||.2):.38}):null;})()/* (patch 82: a code-built wheel's spokes) */,paint,")
rep("sp=P3(KG.spoke,M.paint,Math.cos(a)*.36", "sp=P3(KG.spoke,M.rimS||M.paint,Math.cos(a)*.36")
rep("sp=P3(KG.spokeHQ,M.paint,", "sp=P3(KG.spokeHQ,M.rimS||M.paint,")
rep("sp=P3(KG.spoke,SH.metal,", "sp=P3(KG.spoke,M.rimS||SH.metal,")
# a car body's calipers: the rim colour, when one is chosen (they took the accent colour)
rep("function styleVC(st){const t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],n=TRIMS[st.in|0];if(!(t&&t.h)&&!(a&&a.h)&&!(n&&n.h))return null;const key=[st.tr|0,st.ac|0,st.in|0].join('.');",
    "function styleVC(st){const t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],n=TRIMS[st.in|0],rw=TRIMS[st.rm|0];if(!(t&&t.h)&&!(a&&a.h)&&!(n&&n.h)&&!(rw&&rw.h))return null;const key=[st.tr|0,st.ac|0,st.in|0,st.rm|0].join('.');/* (patch 82: the rims' colour reaches the calipers) */")
rep("uOn:{value:new THREE.Vector3(t.h?1:0,a.h?1:0,n.h?1:0)},", "uOn:{value:new THREE.Vector3(t.h?1:0,a.h?1:0,n.h?1:0)},uRc:{value:C(rw&&rw.h)},uRon:{value:rw&&rw.h?1:0},")
rep("sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB;uniform vec4 uTM;\\n'", "sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB,uRc;uniform float uRon;uniform vec4 uTM;\\n'")
rep("+'if(uOn.x>.5&&(abs(sCi-1.)<.1", "+'if(uRon>.5&&abs(sCi-13.)<.1){diffuseColor.rgb=uRc*clamp(sMx/.78,.3,1.2);sG=4.;}\\nelse if(uOn.x>.5&&(abs(sCi-1.)<.1")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 82 applied')
