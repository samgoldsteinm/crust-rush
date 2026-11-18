"""Patch 91 (web v228): Gold, Silver and Bronze metallic paints; the Rims colour paints every wheel's real spokes and hub.
The owner: "Gold silver and bronze should also be car color options"; with Gold rims and Gold calipers on the Sport Sedan's Redline
wheels "the spokes/rim is not gold at all and the caliper is gold. Make sure the rims and spokes are changed in the rims section and
the calipers are only changed from the caliper section"; the Chariot's hub: "These are not brake calipers they are either the bearings
or the drum and should not change color from the caliper section but from the rim section instead they are a part of the rim".
Why: patch 82's WHEEL_SPOKES named, for the kart wheel sets, the class their CALIPER is made of (redline 17, emerald and stealth 16,
turbo 18): once 88 held the caliper apart, the Rims colour painted nearly nothing. Measured again on the rolling part only
(scratch/paint/clssheet.js: every wheel coloured by class; spokecls.js: triangles per class inside the spoke limit): Redline's star
spokes are dark 1 with carbon 6 edges and red 17 split accents; Emerald's mesh carbon 6 with gunmetal 15 face and green 16 accents;
Stealth 6 + 15 + 16; Turbo's fan blue 1 + 18 + 15. Cars: the Tourer's hubcap 11 with its chrome centre 10 and ring 7; the Chariot's
spokes 1, rim 6 and hub 2 / 0 (the hub is the bearing cap: part of the wheel); the Retro GT's rim 10 and gunmetal centre star 15; the
Concept's spokes 1 and white ribs 2; the Onyx's spokes 11 and carbon inserts 6. Brake discs (12) and drums / back plates (the Retro
GT's and wheel sets' metal 7) stay out; calipers take only the Calipers colour (88's held part).
- rotorMark (carGeos): a car's brake disc built in its spoke class (Scissor, Mega GT...): its pieces lying over 15% of the wheel's
  radius inboard of the spokes are labelled disc 12 (uv only: the stock look is unchanged), so the Rims colour leaves them.
- PAINTS 24..26: Gold, Silver, Bronze, with a metal finish (PAINT_MET: metalness .85 and a satin roughness under the clear coat);
  their swatches show a metal sheen, the garage says 'Metallic paint'. Appended: a build's p travels online and in saves.
- packWheelGeo: a car pack's wheel used as a wheel type (the Monster wheel) is that car's own wheel for the side (mirroring one
  wheel put its inside out on the left).
- holdOut: a wheel set with a held part is turned round (mirrored in z) when its spokes are not outboard of its caliper: the sets' pack
  has no wheel positions, so every wheel set (and the Monster wheel as a wheel type) showed its caliper side out on the right (+z).
- PC: the same (pc87; the wheel types come from the export).
Run once, after patch 90: tools/py.cmd tools/mini/patch91.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 91' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const WHEEL_SPOKES={suv:[10],retrogt:[10],concept:[1],chariot:[1],skywing:[6],bike_mx:[10],bike_moto:[10],rollpin:[21],grater:[21],comet:[21],oilcan:[21],redline:[17],emerald:[16],stealth:[16],turbo:[18],forged:[19]},",
    "const WHEEL_SPOKES={suv:[10],retrogt:[10,15],concept:[1,2],chariot:[1,6,2,0],tourer:[11,10,7],onyx:[11,6],skywing:[6],bike_mx:[10],bike_moto:[10],rollpin:[21],grater:[21],comet:[21],oilcan:[21],\n"
    "  redline:[1,6,17],emerald:[6,15,16],stealth:[6,15,16],turbo:[1,18,15],forged:[19]},/* (patch 91: measured on the rolling part; not the caliper's class) */")
# the held part's caliper classes: no longer the spoke classes (a wheel set's caliper is held whole: all its classes are caliper)
rep("cl=held?[...new Set([13,...held,...(WHEEL_CAL[id]||[]),...(WHEEL_SPOKES[id]||[11])])].slice(0,4):WHEEL_CAL[id]||[];",
    "cl=held?[...new Set([13,...held,...(WHEEL_CAL[id]||[])])].slice(0,4):WHEEL_CAL[id]||[];")
rep("const WHEEL_HOLD={wheelset:{n:150},", "const WHEEL_HOLD={wheelset:{n:150,k:[16,17,18]}/* (patch 91: the sets' calipers: green 16, red 17, blue 18) */,")
# metallic paints
rep("'#7a0912','#ffd21a','#86c916','#0b4a26','#0e8c86','#2f9bff','#0c1d4d','#2a1150','#b4532a','#c9b28a','#a9adb5','#3a3d43','#f5f6f8','#07080a'];",
    "'#7a0912','#ffd21a','#86c916','#0b4a26','#0e8c86','#2f9bff','#0c1d4d','#2a1150','#b4532a','#c9b28a','#a9adb5','#3a3d43','#f5f6f8','#07080a',\n"
    "  '#d6aa45','#c9cdd3','#b0703a'];/* (patch 91: gold, silver, bronze: metallic, PAINT_MET) */\nconst PAINT_MET={24:{m:.85,r:.26},25:{m:.85,r:.22},26:{m:.85,r:.3}};")
rep("'Crimson','Sunburst','Lime','Racing green','Teal','Sky','Navy','Midnight','Copper','Sand','Silver grey','Gunmetal','Snow','Jet black'];",
    "'Crimson','Sunburst','Lime','Racing green','Teal','Sky','Navy','Midnight','Copper','Sand','Silver grey','Gunmetal','Snow','Jet black','Gold','Silver','Bronze'];")
rep("const paint=new THREE.MeshPhysicalMaterial(lv?{color:col,roughness:.2,metalness:.14,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.45}:{color:col,roughness:.36,metalness:0,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.75})",
    "const pmet=!lv&&PAINT_MET[spec.p],paint=new THREE.MeshPhysicalMaterial(lv?{color:col,roughness:.2,metalness:.14,clearcoat:1,clearcoatRoughness:.03,envMapIntensity:1.45}:pmet?{color:col,roughness:pmet.r,metalness:pmet.m,clearcoat:1,clearcoatRoughness:.04,envMapIntensity:1.5}/* (patch 91: a metal paint) */:{color:col,roughness:.36,metalness:0,clearcoat:1,clearcoatRoughness:.02,envMapIntensity:1.75})")
rep("paint.userData.solid=!lv;", "paint.userData.solid=!lv&&!pmet;paint.userData.met=pmet||null;")
rep("M.carPaint=new THREE.MeshPhysicalMaterial(M.paint.userData.solid?",
    "M.carPaint=new THREE.MeshPhysicalMaterial(M.paint.userData.met?{color:M.paint.color.clone(),vertexColors:true,metalness:M.paint.userData.met.m,roughness:M.paint.userData.met.r,clearcoat:1,clearcoatRoughness:.04,envMapIntensity:1.5}/* (patch 91) */:M.paint.userData.solid?")
rep("b.title=PAINT_NAMES[i];if(c)b.style.background=c;", "b.title=PAINT_NAMES[i];if(c)b.style.background=PAINT_MET[i]?'linear-gradient(135deg,#fff 0%,'+c+' 38%,'+c+' 62%,#2a2420 100%)':c;/* (patch 91: a metal sheen) */")
rep("'<b>'+PAINT_NAMES[playerBuild.p]+'.</b> Solid paint. The Theme tab", "'<b>'+PAINT_NAMES[playerBuild.p]+'.</b> '+(PAINT_MET[playerBuild.p]?'Metallic paint.':'Solid paint.')+' The Theme tab")
# a wheel's facing: its spokes outboard of its caliper (the sets' pack records no wheel positions: they were inside out on one side)
rep("m.position.copy(wh.position);m.rotation.copy(wh.rotation);m.scale.copy(wh.scale);m.castShadow=false;m.userData.held=1;yaw.add(m);}",
    "m.position.copy(wh.position);m.rotation.copy(wh.rotation);m.scale.copy(wh.scale);m.castShadow=false;m.userData.held=1;yaw.add(m);\n"
    "  /* (patch 91) a wheel set: the spokes face out, the caliper in: one built the other way round is turned (a mirror in z) */\n"
    "  const sd=pack==='wheelset'?Math.sign(yaw.position.z):0;if(sd){const sp=WHEEL_SPOKES[id]||[11],za=(g,f)=>{const P=g.attributes.position,uv=g.attributes.uv,I=g.index.array;let z=0,n=0;for(let t=0;t<I.length;t++){const v=I[t];if(f(Math.floor(uv.getX(v)*32))){z+=P.getZ(v);n++;}}return n?z/n:null;};\n"
    "    const zs=za(h.spin,c=>sp.includes(c)),zh=za(h.hold,()=>true);if(zs!=null&&zh!=null&&(zs-zh)*wh.scale.z*sd<0){wh.scale.z*=-1;m.scale.z*=-1;}}}")
# a car's own wheel as a wheel type (the Monster wheel): that car's wheel for this side, as on the car (one mirrored wheel faced in on the left)
rep("function packWheelGeo(pack,g,side){const key=pack+'|'+g+'|'+side;",
    "function packWheelGeo(pack,g,side){{const hw=CAR_PACKS[pack].h.wheels,wi=+g.slice(1);if(hw&&hw[wi]){const j=hw.findIndex(q=>Math.sign(q.c[2])===side&&q.f===hw[wi].f);if(j>=0)g='w'+j;}}/* (patch 91: a car pack's wheel for this side) */const key=pack+'|'+g+'|'+side;")
# a car's brake disc made of its spoke class (the Scissor's, Mega GT's): pieces well inboard of the spokes are labelled disc (12)
rep("  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */",
    "  {const bd=BODIES.find(b=>b.id===id.replace(/_hq$/,''));if(bd&&bd.bike)for(const k in g)if(/^w\\d$/.test(k))wheelTrim(g[k]);}/* (patch 85) */\n"
    "  {const hw=p.h.wheels||[],cid=id.replace(/_hq$/,'');if(cid!=='chariot')for(const k in g){const m=/^w(\\d)$/.exec(k);if(m&&hw[+m[1]])rotorMark(g[k],Math.sign(hw[+m[1]].c[2])||1,WHEEL_SPOKES[cid]||[11]);}}/* (patch 91) */")
rep("/* (patch 85) a bike's wheel: only what lies within its tyre",
    "/* (patch 91) a brake disc built in the spoke class: a piece of those classes lying well inboard (over 15% of the wheel's radius) of\n"
    "   the spokes is labelled disc 12 (its uv only: it keeps its colour, the Rims colour leaves it) */\n"
    "function rotorMark(geo,os,sp){const P=geo.attributes.position,uv=geo.attributes.uv,I=geo.index&&geo.index.array;if(!uv||!I)return;let R=0;for(let i=0;i<P.count;i++)R=Math.max(R,Math.hypot(P.getX(i),P.getY(i)));if(!(R>0))return;\n"
    "  const km=new Map(),par=new Int32Array(P.count);for(let i=0;i<P.count;i++){const k=Math.round(P.getX(i)*500)+','+Math.round(P.getY(i)*500)+','+Math.round(P.getZ(i)*500);const j=km.get(k);if(j!==undefined)par[i]=j;else{km.set(k,i);par[i]=i;}}\n"
    "  const f=i=>{while(par[i]!==i){par[i]=par[par[i]];i=par[i];}return i;};for(let t=0;t<I.length;t+=3){const a=f(I[t]),b=f(I[t+1]);if(a!==b)par[a]=b;const b2=f(I[t+1]),c2=f(I[t+2]);if(b2!==c2)par[b2]=c2;}\n"
    "  const C=new Map();let zs=0,ns=0;for(let t=0;t<I.length;t+=3){if(!sp.includes(Math.floor(uv.getX(I[t])*32)))continue;const z=(P.getZ(I[t])+P.getZ(I[t+1])+P.getZ(I[t+2]))/3;zs+=z;ns++;const r=f(I[t]);let c=C.get(r);if(!c)C.set(r,c={t:[],z:0});c.t.push(t);c.z+=z;}\n"
    "  if(!ns)return;const zm=zs/ns;for(const c of C.values()){if(((c.z/c.t.length)-zm)*os/R>-.15)continue;for(const t of c.t)for(let j=0;j<3;j++)uv.setX(I[t+j],(12+.5)/32);}uv.needsUpdate=true;}\n"
    "/* (patch 85) a bike's wheel: only what lies within its tyre")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 91 applied')
