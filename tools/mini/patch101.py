"""Patch 101 (web v234): one caliper per wheel, never spinning, rear wheels' at the front, front wheels' at the back.
The owner (the Scissor on Forged wheels: its calipers "sticking out through the rims on the back wheels"): "make sure there is only one
in the front and back on every car that should have it. if it didnt have calipers to begin with then dont add any. also make sure they
dont spin. the rear calipers should be on the front of the wheel and the front calipers on the rear. if there are already calipers on a
car from the 3d model i uploaded then dont change the orientation"; earlier: "if you add the caliper to the wheel model itself than
cars that already had one will have 2. make sure you check all 4 tires on each car combo".
Why the Scissor's showed through: its calipers are in its BODY (patch 97 BODY_CAL), sized for its own wheels; a bigger wheel set's rim
passes through them.
- carBody: a BODY_CAL car's calipers (class 13 by its wheels) are split out of b_vc into their own mesh (userData.bodyCal). On any wheel
  type they are hidden (a wheel set's or the Monster wheel's own caliper shows instead; the Slicks, Hover and Pepperoni discs are closed,
  and the Interceptor's stuck out over the Slicks); on the car's own wheels they stay. Patch 97's hiding of
  the wheel's caliper is undone.
- holdOut on a wheel type (not a car's own wheels from its model): the held caliper is turned about the axle so it sits behind a front
  wheel's axle (155 degrees from forward) and ahead of a rear wheel's (25 degrees). A car's own wheels keep their model's caliper as it was.
- addCal (patch 92: Grand Coupe, Megawatt, SUV): front wheels at the back, rear wheels at the front (it was at the back on all four).
- PC: the exporter exports a wheel type's held part per corner (hold_FL, hold_FR, hold_RL, hold_RR) and a BODY_CAL body's calipers as
  their own node 'bcal'; kart_builder shows bcal unless the wheel type has a pack, and takes the corner's hold (pc93; pc92 undone).
Check: scratch/paint/calaudit.js (every body x every wheel type x four wheels: visible calipers counted; pictures).
Run once, after patch 100: tools/py.cmd tools/mini/patch101.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 101' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# 1. the body's calipers apart
rep("  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);",
    "  /* (patch 101) a car's own calipers in their own mesh: hidden on a wheel type that brings its own */\n"
    "  if(BODY_CAL[cid]&&g.b_vc){const sp=bodyCalSplit(g.b_vc,(CAR_PACKS[id]||CAR_PACKS[cid]).h.wheels||[]);if(sp){const me=new THREE.Mesh(sp.cal,mats.vc);me.castShadow=true;me.receiveShadow=true;me.userData.bodyCal=1;B.add(me);M.bodyCal=me;g={...g,b_vc:sp.rest};}}\n"
    "  for(const k in g){if(!k.startsWith('b_'))continue;const me=new THREE.Mesh(g[k],mats[k.slice(2)]);")
rep("const TAIL_ROOF={interceptor:2.2},TAIL_DEEP={interceptor:1};",
    "const TAIL_ROOF={interceptor:2.2},TAIL_DEEP={interceptor:1};\n"
    "function bodyCalSplit(geo,hw){if(geo.userData.calsplit!==undefined)return geo.userData.calsplit;geo.userData.calsplit=null;const P=geo.attributes.position,uv=geo.attributes.uv,I=geo.index&&geo.index.array;if(!uv||!I)return null;const a=[],b=[];\n"
    "  for(let t=0;t<I.length;t+=3){let cal=false;if(Math.floor(uv.getX(I[t])*32)===13){const x=(P.getX(I[t])+P.getX(I[t+1])+P.getX(I[t+2]))/3,y=(P.getY(I[t])+P.getY(I[t+1])+P.getY(I[t+2]))/3,z=(P.getZ(I[t])+P.getZ(I[t+1])+P.getZ(I[t+2]))/3;\n"
    "    cal=hw.some(q=>Math.hypot(x-q.c[0],y-q.c[1])<q.r*1.1&&Math.abs(z-q.c[2])<q.r);}(cal?b:a).push(I[t],I[t+1],I[t+2]);}if(!b.length)return null;\n"
    "  const mk=ix=>{const g=new THREE.BufferGeometry();for(const k in geo.attributes)g.setAttribute(k,geo.attributes[k]);g.setIndex(new THREE.BufferAttribute(I instanceof Uint32Array?new Uint32Array(ix):new Uint16Array(ix),1));g.computeBoundingSphere();CARGEO.add(g);return g;};\n"
    "  return geo.userData.calsplit={rest:mk(a),cal:mk(b)};}")
rep("for(const w of wheels){const yw=w.spin.parent;if(yw&&yw.parent===g)tilt.add(yw);}",
    "for(const w of wheels){const yw=w.spin.parent;if(yw&&yw.parent===g)tilt.add(yw);}\n"
    "  if(M.bodyCal&&wt&&wt.id!=='standard')M.bodyCal.visible=false;/* (patch 101) the wheel type's own caliper shows instead */")
# 2. the wheel's caliper shown on every car (97 undone), turned on a wheel type
rep("if(wh.userData.pk)holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk,!!(cfg.car&&BODY_CAL[cfg.car]));else if(cfg.car&&wt.id==='standard'){holdOut(wh,yaw,M,cfg.car,0,cfg.car);addCal(wh,yaw,M,cfg.car);}",
    "if(wh.userData.pk)holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk,false,f?1:-1);else if(cfg.car&&wt.id==='standard'){holdOut(wh,yaw,M,cfg.car,0,cfg.car);addCal(wh,yaw,M,cfg.car,f);}/* (patch 101: turned by front / rear) */")
rep("function holdOut(wh,yaw,M,id,wset,pack,noCal){", "function holdOut(wh,yaw,M,id,wset,pack,noCal,fr){")
rep("m.castShadow=false;m.userData.held=1;if(noCal)m.visible=false;/* (patch 97) */yaw.add(m);\n",
    "m.castShadow=false;m.userData.held=1;if(noCal)m.visible=false;/* (patch 97) */yaw.add(m);\n"
    "  if(fr){/* (patch 101) a wheel type's caliper: behind a front axle, ahead of a rear one */if(h.ang==null){const P=h.hold.attributes.position,I=h.hold.index.array;let x=0,y=0;for(let t=0;t<I.length;t++){x+=P.getX(I[t]);y+=P.getY(I[t]);}h.ang=Math.atan2(y,x);}\n"
    "    m.rotation.z+=(fr>0?Math.PI*155/180:Math.PI*25/180)-h.ang;}\n")
# 3. the added calipers
rep("function addCal(wh,yaw,M,id){", "function addCal(wh,yaw,M,id,f){")
rep("addCalGeo(wh.userData.geo0||wh.geometry,os,id)", "addCalGeo(wh.userData.geo0||wh.geometry,os,id,f)")
rep("function addCalGeo(geo,os,id){", "function addCalGeo(geo,os,id,f){")
rep("const k='addcal'+os;", "const k='addcal'+os+(f?'f':'r');")
rep("ang=Math.PI*.8,sh=new THREE.Shape()", "ang=f?Math.PI*.8:Math.PI*.2/* (patch 101: a rear wheel's ahead of its axle) */,sh=new THREE.Shape()")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 101 applied')
# (follow-up in the same release) the SUV's model has its own caliper (held, patch 88): no added one; it takes the Calipers colour.
# The Monster wheel on the Monster Truck is that truck's own wheel: its caliper keeps the model's place.
s = open(p, encoding='utf-8', newline='').read()
rep("const WHEEL_ADDCAL={coupe:1,megawatt:1,suv:1};", "const WHEEL_ADDCAL={coupe:1,megawatt:1};/* (patch 101: the SUV's model has its own) */")
rep(",suv:{},", ",suv:{k:[7,1]}/* (patch 101: its model's caliper takes the Calipers colour) */,")
rep("holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk,false,f?1:-1);", "holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk,false,wh.userData.pk===cfg.car?0:f?1:-1);")
rep("    m.rotation.z+=(fr>0?Math.PI*155/180:Math.PI*25/180)-h.ang;}", "    m.userData.r0=m.rotation.z;m.rotation.z+=(fr>0?Math.PI*155/180:Math.PI*25/180)-h.ang;}/* (r0: the model's own turn, for the PC export) */")
rep("const BODY_CAL={gt:1,hyper:1,interceptor:1,scissor:1,skywing:1,endur:1};", "const BODY_CAL={gt:1,hyper:1,interceptor:1,scissor:1,skywing:1,endur:1,roadster:1};/* (patch 101: the Roadster's behind its hubcaps) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 101 follow-up applied')
