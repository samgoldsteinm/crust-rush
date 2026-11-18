"""Patch 88 (web v227): brake calipers (and the suspension pieces some wheel models carry) no longer spin with the wheel.
The owner: "the brake calipers are spinning with some of the wheels, brake calipers are stationary and do not move or spin with the
wheel. Please test this for all cars and wheel types and make sure it is fixed".
Why: the downloaded wheel models include what sits inside the wheel: the caliper (every kart wheel set: Redline, Emerald, Stealth,
Turbo, Forged; the Monster wheel; Muscle, Monster, Retro GT, Onyx, SUV, Hatch, Tourer), and on some cars the hub carrier, strut or
brackets (GT, Roadster, Onyx), on the bikes brake parts and a fender arc. All of it was one mesh under the spinning group.
Measured (scratch/paint/calan.js, calsheet.js: every wheel's connected pieces, coloured): such a piece is NOT repeated round the axle
and covers under 200 degrees; spokes, lugs, discs and the tyre are repeated or whole. WHEEL_HOLD lists, per pack, which of those
pieces to hold (a minimum size, or a class): checked by eye on every wheel of every pack (no rule: the pack keeps its wheels whole).
- wheelHold(geo, pack): the wheel's geometry split in two (shared attributes, two index lists), cached on the geometry.
- holdOut: after a wheel mesh is put in its spin group, the held part goes to the steering group (yaw) with the same transform: it
  turns with the steering but does not roll. Its material: the rims' material with the wheel's spoke classes as caliper classes, so a
  wheel set's caliper takes the Calipers colour (it shared its class with the spokes and took the Rims colour).
- PC: the exporter (godot tools/glbexport.js) exports the held part as ph<i> (car's own wheels) and hold_L / hold_R (wheel types);
  kart_builder puts it in a 'wheel_XX_hold' node beside the wheel, view.gd steers it (pc86).
Run once, after patch 87: tools/py.cmd tools/mini/patch88.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 88' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function buildWheel(type,side,M){", r"""/* (patch 88) what inside a wheel model must not roll: the caliper, hub carrier, strut. Per pack: pieces (connected, by position) not
   repeated round the axle, under 200 degrees, at least n triangles, of these classes (cls), reaching no further out than r1 (x the wheel's radius); any: everything inside r1 (the MX bike's hubless ring wheel) */
const WHEEL_HOLD={wheelset:{n:150},monster:{n:150,k:[12,11]},muscle:{n:400,k:[12]},retrogt:{k:[7]},onyx:{n:80},suv:{},hatch:{cls:[9],k:[9]},tourer:{cls:[6]},gt:{},roadster:{cls:[6],r1:3},bike_mx:{any:1,n:1,r1:.86},bike_moto:{cls:[7]}};/* (k: the held caliper's own classes, for the Calipers colour) */
function wheelHold(geo,pack){if(geo.userData.hold!==undefined)return geo.userData.hold;const rule=WHEEL_HOLD[pack];geo.userData.hold=null;if(!rule||!geo.index)return null;
  const P=geo.attributes.position,uv=geo.attributes.uv,I=geo.index.array;let R=0;for(let i=0;i<P.count;i++)R=Math.max(R,Math.hypot(P.getX(i),P.getY(i)));if(!(R>0))return null;
  const km=new Map(),par=new Int32Array(P.count);for(let i=0;i<P.count;i++){const k=Math.round(P.getX(i)*500)+','+Math.round(P.getY(i)*500)+','+Math.round(P.getZ(i)*500);const j=km.get(k);if(j!==undefined)par[i]=j;else{km.set(k,i);par[i]=i;}}
  const f=i=>{while(par[i]!==i){par[i]=par[par[i]];i=par[i];}return i;},u=(a,b)=>{a=f(a);b=f(b);if(a!==b)par[a]=b;};for(let t=0;t<I.length;t+=3){u(I[t],I[t+1]);u(I[t],I[t+2]);}
  const C=new Map();for(let t=0;t<I.length;t+=3){const r=f(I[t]);let c=C.get(r);if(!c)C.set(r,c={t:[],r0:9,r1:0,b:new Set(),cl:{}});c.t.push(t);
    for(let j=0;j<3;j++){const v=I[t+j],x=P.getX(v),y=P.getY(v),q=Math.hypot(x,y)/R;c.r0=Math.min(c.r0,q);c.r1=Math.max(c.r1,q);if(q>.08)c.b.add(Math.floor((Math.atan2(y,x)+Math.PI)/(Math.PI/18))%36);}
    const ci=uv?Math.floor(uv.getX(I[t])*32):-1;c.cl[ci]=(c.cl[ci]||0)+1;}
  const L=[...C.values()],hold=new Set();for(const c of L){const n=c.t.length,top=+Object.entries(c.cl).sort((a,b)=>b[1]-a[1])[0][0];
    if(n<(rule.n||30)||c.r1>=(rule.r1||.95)||top===8)continue;if(!rule.any&&(c.b.size>20||c.r1-c.r0<=.12))continue;if(rule.cls&&!rule.cls.includes(top))continue;
    if(!rule.any&&L.some(d=>d!==c&&d.t.length===n&&Math.abs(d.r1-c.r1)<.03))continue;/* (repeated round the axle: a spoke) */for(const t of c.t)hold.add(t);}
  if(!hold.size)return null;const a=[],b=[];for(let t=0;t<I.length;t+=3)(hold.has(t)?b:a).push(I[t],I[t+1],I[t+2]);
  const mk=ix=>{const g=new THREE.BufferGeometry();for(const k in geo.attributes)g.setAttribute(k,geo.attributes[k]);g.setIndex(new THREE.BufferAttribute(I instanceof Uint32Array?new Uint32Array(ix):new Uint16Array(ix),1));g.computeBoundingSphere();CARGEO.add(g);return g;};
  return geo.userData.hold={spin:mk(a),hold:mk(b)};}
/* (patch 88) put a wheel's held part in its steering group: it steers, it does not roll; a wheel set's caliper takes the Calipers colour */
function holdOut(wh,yaw,M,id,wset,pack){if(!wh||!wh.isMesh||!yaw)return;const h=wheelHold(wh.userData.geo0||wh.geometry,pack);if(!h)return;wh.userData.geo0=wh.userData.geo0||wh.geometry;wh.geometry=h.spin;
  const m=new THREE.Mesh(h.hold,(M&&M.st&&rimVC(M.st,wset?1:0,id,null,(WHEEL_HOLD[pack]||{}).k||[]))||(wset?wheelVC():SH.carVC));m.position.copy(wh.position);m.rotation.copy(wh.rotation);m.scale.copy(wh.scale);m.castShadow=false;m.userData.held=1;yaw.add(m);}
function buildWheel(type,side,M){""")
# rimVC: a held part's material: no spokes, the spoke classes are calipers
rep("const _rvc={};function rimVC(st,ds,id,geo){const r=TRIMS[(st&&st.rm)|0],c=TRIMS[(st&&st.cl)|0],sp=WHEEL_SPOKES[id]||[11],cl=WHEEL_CAL[id]||[];\n"
    "  if(!(r&&r.h)&&!(c&&c.h&&cl.length))return null;const key=[st.rm|0,st.cl|0,ds?'d':'',id,geo?geo.uuid:''].join('|');",
    "const _rvc={};function rimVC(st,ds,id,geo,held){const r=held?null:TRIMS[(st&&st.rm)|0],c=TRIMS[(st&&st.cl)|0],sp=held?[]:WHEEL_SPOKES[id]||[11],cl=held?[...new Set([13,...held,...(WHEEL_CAL[id]||[]),...(WHEEL_SPOKES[id]||[11])])].slice(0,4):WHEEL_CAL[id]||[];/* (patch 88: a held part: its spoke classes are the caliper) */\n"
    "  if(!(r&&r.h)&&!(c&&c.h&&cl.length))return null;const key=[st.rm|0,st.cl|0,ds?'d':'',id,geo?geo.uuid:'',held?'h'+held.join('.'):''].join('|');")
# buildWheel: remember the pack
rep("m.castShadow=false;return m;}\n  const W=new THREE.Group();", "m.castShadow=false;m.userData.pk=wd.pack;m.userData.wid=wd.id;m.userData.wset=wd.pack==='wheelset';return m;}\n  const W=new THREE.Group();")
# the bikes' own wheels
rep("const wh=new THREE.Mesh(cg['w'+wi],rimVC(M.st,0,cfg.car,cg['w'+wi])||SH.carVC);/* (patch 73: the rims' colour) */wh.castShadow=false;spin.add(wh);",
    "const wh=new THREE.Mesh(cg['w'+wi],rimVC(M.st,0,cfg.car,cg['w'+wi])||SH.carVC);/* (patch 73: the rims' colour) */wh.castShadow=false;spin.add(wh);holdOut(wh,yaw,M,cfg.car,0,cfg.car);/* (patch 88) */")
# cars' own wheels and wheel types
rep("else{wh=buildWheel(wt.id,s,M);wh.scale.set(R/1.32,R/1.32,tyreR(R)/1.32*wz);}spin.add(wh);",
    "else{wh=buildWheel(wt.id,s,M);wh.scale.set(R/1.32,R/1.32,tyreR(R)/1.32*wz);}spin.add(wh);"
    "if(wh.userData.pk)holdOut(wh,yaw,M,wh.userData.wid,wh.userData.wset,wh.userData.pk);else if(cfg.car&&wt.id==='standard')holdOut(wh,yaw,M,cfg.car,0,cfg.car);/* (patch 88: the caliper steers, it does not roll) */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 88 applied')
