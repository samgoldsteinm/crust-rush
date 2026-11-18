"""Patch 82 (web v224): the Rims colour paints exactly the wheel's spokes; a new Calipers colour paints the brake calipers.
The owner: "changing the rim color doesnt change the tire spoke color ... it only changes the brake drum"; "the entire wheel shouldnt
change colors only the brake caliper and the wheel spokes"; "still have colored brake rotors/drums"; "make it so you can pick a different
color for the spokes and calipers so they arent the same. figure out exactly what the spokes and calipers are on a wheel".
Measured (scratch/paint/wheelan.js: each wheel's colour classes, their spread from the axle and their depth along it): a wheel's spokes
are ONE class, which differs by model: 'rim' 11 on most cars; chrome 10 on suv and retrogt; dark 1 on concept and chariot; carbon 6 on
skywing; chrome 10 on the bikes; steel 21 on rollpin, grater, comet, oilcan; a kart wheel set its own colour (redline red 17, emerald and
stealth green 16, turbo bluem 18, forged bronze 19). The rotor / drum is disc 12 or, on some cars, metal 7 / gunmetal 15 (GT, retrogt,
onyx...): never painted now (the first takes painted 7, 10, 15, 19, 21 on every wheel). Calipers: class 13 in a car's BODY (it took the
accent colour) and forged's red 17.
- WHEEL_SPOKES / WHEEL_CAL: the classes per car (its own wheels) or wheel set; default spokes = 11, no caliper.
- the 'rim' class holds the lip and barrel too (and the Monster's tread blocks): only its part inside the tyre is painted (uCut: the
  tyre's inner radius, its 2nd percentile, less 5% of the wheel's radius, per wheel geometry: front and rear can differ).
- rimVC(st, ds, id): spokes take st.rm, calipers st.cl; null when neither. Wheel sets get theirs in buildWheel (M.st).
- the style shop has a Calipers row (slot 'cl', the trim list; owned as trims are); styleVC paints a body's class 13 with it (no longer
  the accent).
- code-built kart wheels: their spokes only (M.rimS); they have no calipers.
Run once, after patch 81: py.cmd tools/mini/patch82.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 82' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


i = s.index('const _rvc={};function rimVC(st,ds){')
j = s.index("m.customProgramCacheKey=()=>'carvc-rim';SHSET.add(m);return _rvc[key]=m;}", i) + len("m.customProgramCacheKey=()=>'carvc-rim';SHSET.add(m);return _rvc[key]=m;}")
s = s[:i] + r"""/* (patch 82) each wheel's spokes and calipers: its colour classes, measured (tools/mini/patch82.py); not listed: spokes 11, no caliper */
const WHEEL_SPOKES={suv:[10],retrogt:[10],concept:[1],chariot:[1],skywing:[6],bike_mx:[10],bike_moto:[10],rollpin:[21],grater:[21],comet:[21],oilcan:[21],redline:[17],emerald:[16],stealth:[16],turbo:[18],forged:[19]},
  WHEEL_CAL={forged:[17]};
const _rvc={};function rimVC(st,ds,id,geo){const r=TRIMS[(st&&st.rm)|0],c=TRIMS[(st&&st.cl)|0],sp=WHEEL_SPOKES[id]||[11],cl=WHEEL_CAL[id]||[];
  if(!(r&&r.h)&&!(c&&c.h&&cl.length))return null;const key=[st.rm|0,st.cl|0,ds?'d':'',id,geo?geo.uuid:''].join('|');if(_rvc[key])return _rvc[key];const m=SH.carVC.clone();if(ds)m.side=THREE.DoubleSide;
  const v4=a=>new THREE.Vector4(...[0,1,2,3].map(i=>a[i]??-1));
  /* the spokes stop where the wheel's lip and barrel begin, just inside the tyre (the 'rim' class holds lip, barrel and spokes alike) */
  let cut=1e9;if(geo&&geo.attributes.uv){const P=geo.attributes.position,uv=geo.attributes.uv,rr=[];let Rm=0;for(let i=0;i<P.count;i++){const q=Math.hypot(P.getX(i),P.getY(i));Rm=Math.max(Rm,q);if(Math.floor(uv.getX(i)*32)===8)rr.push(q);}
    if(rr.length>20){rr.sort((a,b)=>a-b);cut=Math.max(.45*Rm,rr[Math.floor(rr.length*.02)]-.05*Rm);}}/* (never under 45%: the Monster's tyre reaches almost to its hub) */
  const U={uR:{value:new THREE.Color(r&&r.h||'#000')},uRM:{value:new THREE.Vector2(r&&r.m?.95:.3,r&&r.m?(r.r||.2):.38)},uC:{value:new THREE.Color(c&&c.h||'#000')},
    uS:{value:v4(r&&r.h?sp:[])},uK:{value:v4(c&&c.h?cl:[])},uCut:{value:cut}};
  m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);sh.vertexShader='varying vec2 vRO;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvRO=position.xy;');sh.fragmentShader='varying vec2 vRO;uniform float uCut;uniform vec3 uR,uC;uniform vec2 uRM;uniform vec4 uS,uK;\nbool rIn(float c,vec4 s){return abs(c-s.x)<.1||abs(c-s.y)<.1||abs(c-s.z)<.1||abs(c-s.w)<.1;}\n'+sh.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\n'
    +'float rCi=floor(vUv.x*32.);float rMx=max(vColor.r,max(vColor.g,vColor.b));float rG=0.;\n'
    +'if(rIn(rCi,uK)){diffuseColor.rgb=uC*clamp(rMx/.78,.35,1.2);rG=2.;}else if(rIn(rCi,uS)&&length(vRO)<uCut){diffuseColor.rgb=uR*clamp(rMx/.7,.45,1.15);rG=1.;}').replace('#include <metalnessmap_fragment>','#include <metalnessmap_fragment>\n'
    +'if(rG==1.){metalnessFactor=uRM.x;roughnessFactor=uRM.y;}');/* (a caliper keeps its painted finish) */};
  m.customProgramCacheKey=()=>'carvc-rim3';SHSET.add(m);return _rvc[key]=m;}""" + s[j:]
# the car's own wheels: its id; wheel sets in buildWheel by theirs
rep("const M={rimM:rimVC(stOf(spec)),rimW:rimVC(stOf(spec),1),paint,",
    "const M={st:stOf(spec),rimM:rimVC(stOf(spec),0,body.id),rimS:(()=>{const r=TRIMS[stOf(spec).rm|0];return r&&r.h?new THREE.MeshStandardMaterial({color:r.h,metalness:r.m?.95:.3,roughness:r.m?(r.r||.2):.38}):null;})()/* (patch 82: a code-built wheel's spokes) */,paint,")
rep("const m=new THREE.Mesh(packWheelGeo(wd.pack,wd.g,side),wd.pack==='wheelset'?(M&&M.rimW||wheelVC()):(M&&M.rimM||SH.carVC));", "const wg=packWheelGeo(wd.pack,wd.g,side),m=new THREE.Mesh(wg,wd.pack==='wheelset'?(M&&rimVC(M.st,1,wd.id,wg)||wheelVC()):(M&&rimVC(M.st,0,wd.id,wg)||SH.carVC));/* (patch 82: the wheel's own spokes) */")
rep("new THREE.Mesh(cg['w'+wi],M.rimM||SH.carVC)", "new THREE.Mesh(cg['w'+wi],rimVC(M.st,0,cfg.car,cg['w'+wi])||SH.carVC)", 2)   # (each of a car's own wheels: its spokes)
rep("sp=P3(KG.spoke,M.paint,Math.cos(a)*.36", "sp=P3(KG.spoke,M.rimS||M.paint,Math.cos(a)*.36")
rep("sp=P3(KG.spokeHQ,M.paint,", "sp=P3(KG.spokeHQ,M.rimS||M.paint,")
rep("sp=P3(KG.spoke,SH.metal,", "sp=P3(KG.spoke,M.rimS||SH.metal,")
# a body's calipers: the Calipers colour (they took the accent's)
rep("function styleVC(st){const t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],n=TRIMS[st.in|0];if(!(t&&t.h)&&!(a&&a.h)&&!(n&&n.h))return null;const key=[st.tr|0,st.ac|0,st.in|0].join('.');",
    "function styleVC(st){const t=TRIMS[st.tr|0],a=TRIMS[st.ac|0],n=TRIMS[st.in|0],cw=TRIMS[st.cl|0];if(!(t&&t.h)&&!(a&&a.h)&&!(n&&n.h)&&!(cw&&cw.h))return null;const key=[st.tr|0,st.ac|0,st.in|0,st.cl|0].join('.');/* (patch 82: the calipers' own colour) */")
rep("uOn:{value:new THREE.Vector3(t.h?1:0,a.h?1:0,n.h?1:0)},", "uOn:{value:new THREE.Vector3(t.h?1:0,a.h?1:0,n.h?1:0)},uRc:{value:C(cw&&cw.h)},uRon:{value:cw&&cw.h?1:0},")
rep("sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB;uniform vec4 uTM;\\n'", "sh.fragmentShader='uniform vec3 uT,uA,uI,uOn,uB,uRc;uniform float uRon;uniform vec4 uTM;\\n'")
rep("+'if(uOn.x>.5&&(abs(sCi-1.)<.1", "+'if(uRon>.5&&abs(sCi-13.)<.1){diffuseColor.rgb=uRc*clamp(sMx/.78,.3,1.2);sG=4.;}\\nelse if(uOn.x>.5&&(abs(sCi-1.)<.1")
# the Calipers row
rep("const STYLE={tr:['tr',TRIMS],ac:['tr',TRIMS],in:['tr',TRIMS],rm:['tr',TRIMS],", "const STYLE={tr:['tr',TRIMS],ac:['tr',TRIMS],in:['tr',TRIMS],rm:['tr',TRIMS],cl:['tr',TRIMS]/* (patch 82: calipers) */,")
rep("+row('rm','Rims')+", "+row('rm','Rims')+row('cl','Calipers')+")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 82 applied')
