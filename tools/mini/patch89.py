"""Patch 89 (web v227): the Accent colour shows on every vehicle.
The owner: "the accent color option doesn't change anything, test it on every car to see if it makes a visible change. if nothing
changes then add some accent color spots".
Measured (scratch/paint/acctest.js: every body from 4 sides, accent off vs neon green, the share of the kart's pixels that change):
accent painted classes 2 (stripe), 13 (calipers) and 17 (red) only; 30 of 38 bodies have none of those on show (0 to 0.7%: only
their calipers, behind the spokes). The code-built Wedge's stripe is buried in its cheese (the body's .3 bevel covers it), the Tomato
has no stripe at all.
- styleVC(st, id): accent also paints the body's chrome trim (10: grilles, window surrounds, bumpers, badges) and carbon (6: splitters,
  diffusers, wings, mirrors), ahead of the trim colour on carbon; where the chrome is hidden or missing, one more class (ACC_X: metal 7 on the Neutron, MX, Rocket bike,
  Retro GT; dark 1 on the Grand Coupe, Concept, Muscle, Slip); not the Slip's carbon (its whole body: ACC_NO6). Nothing changes
  until an accent is picked. Every car body has chrome or carbon (scratch/paint/clsuse.js).
- accM: an accent spot on a code-built kart: the part keeps its own material until an accent is picked (Wedge: the nose splitter and
  grille; Tomato: the porthole rings and lamp brows). Named g_acc for the PC (its kart_builder paints g_acc with the accent: pc86).
Run once, after patch 88: tools/py.cmd tools/mini/patch89.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 89' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const _svc={};function styleVC(st){", "/* (patch 89) a body's own extra accent class (the Neutron: its metal) */const ACC_X={bike_neutron:7,bike_mx:7,bike_rocket:7,retrogt:7,coupe:1,concept:1,muscle:1,slip:1},ACC_NO6={slip:1};/* (the Slip: carbon is most of its body) */\nconst _svc={};function styleVC(st,id){")
rep("const key=[st.tr|0,st.ac|0,st.in|0,st.cl|0].join('.');", "const ax=ACC_X[id]??-1,a6=ACC_NO6[id]?0:1,key=[st.tr|0,st.ac|0,st.in|0,st.cl|0,ax,a6].join('.');")
rep("uRc:{value:C(cw&&cw.h)},uRon:{value:cw&&cw.h?1:0},", "uRc:{value:C(cw&&cw.h)},uRon:{value:cw&&cw.h?1:0},uAx:{value:ax},uA6:{value:a6},")
rep("sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB,uRc;uniform float uRon;uniform vec4 uTM;\\n'",
    "sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB,uRc;uniform float uRon,uAx,uA6;uniform vec4 uTM;\\n'")
rep("+'if(uRon>.5&&abs(sCi-13.)<.1){diffuseColor.rgb=uRc*clamp(sMx/.78,.3,1.2);sG=4.;}\\nelse if(uOn.x>.5&&(abs(sCi-1.)<.1",
    "+'if(uRon>.5&&abs(sCi-13.)<.1){diffuseColor.rgb=uRc*clamp(sMx/.78,.3,1.2);sG=4.;}\\n'"
    "+'else if(uOn.y>.5&&(abs(sCi-10.)<.1||(uA6>.5&&abs(sCi-6.)<.1)||abs(sCi-uAx)<.1)){diffuseColor.rgb=uA*clamp(sMx/(abs(sCi-10.)<.1?.93:abs(sCi-7.)<.1?.49:uB.x),.3,1.2);sG=2.;}/* (patch 89: chrome trim, carbon) */\\n'"
    "+'else if(uOn.x>.5&&(abs(sCi-1.)<.1")
rep("M.vcM=styleVC(st);", "M.vcM=styleVC(st,(BODIES[spec.b]||{}).id);/* (patch 89: its own accent class) */")
# accent spots on the code-built karts
rep("function buildWheel(type,side,M){", "/* (patch 89) an accent spot on a code-built kart: the part's own material until an accent is picked (g_acc: the PC paints it) */\n"
    "function accM(M,base){const m=base.clone();m.name='g_acc';m.userData.keyed=true;const a=TRIMS[(M&&M.st&&M.st.ac)|0];if(a&&a.h){m.color.set(a.h);m.metalness=a.m?.9:.35;m.roughness=a.m?(a.r||.22):.32;}return m;}\n"
    "function buildWheel(type,side,M){")
rep("P3(kProf([[5.9,.7],[5.6,.95],[4.4,.95],[4.4,.7]],4.6,.05),SH.chrome,0,0,0,S);for(const s of [-1,1])kLamp(S,5.1,1.12,1.6*s,.22);",
    "P3(kProf([[5.9,.7],[5.6,.95],[4.4,.95],[4.4,.7]],4.6,.05),accM(M,SH.chrome),0,0,0,S);for(const s of [-1,1])kLamp(S,5.1,1.12,1.6*s,.22);/* (patch 89: the splitter, an accent spot) */")
rep("const gr=kAdd(kRBox(.14,.9,2.2,.05),SH.metal,5.2,.95,0,S);", "const gr=kAdd(kRBox(.14,.9,2.2,.05),accM(M,SH.metal),5.2,.95,0,S);")
rep("for(const s of [-1,1]){kLamp(S,3.85,2.75,1.25*s,.42);kAdd(new THREE.TorusGeometry(.45,.06,6,20,Math.PI),SH.chrome,3.95,2.95,1.25*s,S,0,Math.PI/2,0);}",
    "{const am=accM(M,SH.chrome);for(const s of [-1,1]){kLamp(S,3.85,2.75,1.25*s,.42);kAdd(new THREE.TorusGeometry(.45,.06,6,20,Math.PI),am,3.95,2.95,1.25*s,S,0,Math.PI/2,0);}}/* (patch 89: lamp brows and portholes, accent spots) */")
rep("for(const s of [-1,1]){kAdd(new THREE.TorusGeometry(.95,.09,8,32),SH.chrome,-.6,3.05,3.35*s,S);",
    "const amP=accM(M,SH.chrome);for(const s of [-1,1]){kAdd(new THREE.TorusGeometry(.95,.09,8,32),amP,-.6,3.05,3.35*s,S);")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 89 applied')
