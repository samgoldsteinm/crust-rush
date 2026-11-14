"""Sandbox on every track: the edits to tools/mini/sandbox.js that go with patch25.py"""
p = 'D:/crust-rush/source/tools/mini/sandbox.js'
s = open(p, encoding='utf-8', newline='').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80]); s = s.replace(a, b)


def between(a, b, new):
    """replace everything from the start of a up to (not including) b"""
    global s
    assert s.count(a) == 1 and s.count(b) >= 1, (s.count(a), s.count(b), a[:60], b[:60])
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]


rep("let SBX=false;\n", "let SBX=false,SBF=false;/* SBX: Sandbox is on. SBF: and the driving is free (the house, the pizza tracks); it is off where you keep to the road */\n")

# ---- every track is a region
rep("/* the menu in Sandbox: the track list shows only the places that have a region, and no cup tabs */",
    """/* ---- the rest of the game's tracks (web v192) ----
   Every track is a place in Sandbox. Three kinds:
     toy    the house's four (above): drive anywhere; the ground and the walls are Sandbox's own
     open   the fifteen pizza tracks: drive anywhere on the pizza. The ground is the engine's own (groundAt, and the track's height where it
            is raised); the walls are read from what is drawn, as in the rooms, with whatever lies flat on the ground left out; the edge of
            the world is the crust
     road   Sauce Spiral and the four Neon tracks: the road winds up a tower or hangs in the air, so there you keep to it, either way round,
            with the race's own walls (SBF is off)
   SB_AREA names the part of the world each track is in; SB_LINKS says which tracks a track's passages lead to (the plan's sketch, docs/SANDBOX-PLAN.md).
   A passage on an open track is an arch in the crust; on a road track an arch over the left-hand lane; out of the house it is the garage's open door. */
const SB_AREA={margherita:'Kitchen Country',basil:'Kitchen Country',oven:'Kitchen Country',spiral:'Kitchen Country',bay:'The Bay',lagoon:'The Bay',calzone:'The Bay',tour:'The Bay',
  peaks:'The Old Town',mozz:'The Old Town',napoli:'The Old Town',moon:'The Old Town',frosty:'The Freezer Range',burn:'The Freezer Range',glacier:'The Freezer Range',peak:'The Freezer Range',
  grid:'The Neon District',laser:'The Neon District',holo:'The Neon District',synth:'The Neon District'};
const SB_LINKS={margherita:['garage','basil','oven','bay'],basil:['margherita','mozz','spiral'],oven:['margherita','spiral','frosty'],spiral:['oven','basil'],frosty:['oven','burn'],burn:['frosty','glacier'],glacier:['burn','peak'],peak:['glacier','synth'],
  mozz:['basil','napoli'],napoli:['mozz','moon','holo'],moon:['napoli','peaks'],peaks:['moon','calzone'],calzone:['peaks','tour','lagoon'],tour:['calzone'],lagoon:['calzone','bay'],bay:['lagoon','margherita'],
  synth:['peak','holo','laser'],holo:['synth','napoli','grid'],laser:['synth','grid'],grid:['holo','laser']};
function sbRegOf(id){if(SB_REG[id])return SB_REG[id];const m=MAPS.find(q=>q.id===id);if(!m||m.battle||!SB_AREA[id])return null;return SB_REG[id]={name:SB_AREA[id]+' \\u00b7 '+m.name,auto:1,kind:m.exact?'road':'open'};}
/* the menu in Sandbox: every track is a place to start, under its cup's tab as usual (the battle arena has no tab) */""")
between("function sbMenu(){", "/* ---- the track as ground", "function sbMenu(){const cats=document.getElementById('mapCats');if(cats)cats.hidden=false;}\n")

# the garage's open door leads out
rep("    gates:[{id:'ga_b',w:'W',p:132,to:'bedroom',at:'b_g',label:'BEDROOM'}]},",
    "    /* (the second: the garage's own open door, the whole width of it: no arch is drawn, driving out onto the drive is the passage) */\n"
    "    gates:[{id:'ga_b',w:'W',p:132,to:'bedroom',at:'b_g',label:'BEDROOM'},{id:'garage>margherita',w:'S',p:0,hw:520,plain:1,to:'margherita',at:'margherita>garage',label:'MARGHERITA RING'}]},")

# ---- columns on a pizza: what lies on the ground is ground
rep("function sbColumns(b){let cap=0;for(const p of track)if((p.ey||0)>cap)cap=p.ey;cap+=70;const C=",
    "function sbColumns(b){const og=SB.kind==='open';let cap=0;for(const p of track){const h=(og?groundAt(p.x,p.y):0)+(p.ey||0);if(h>cap)cap=h;}cap+=og?110:70;const C=")
rep("const ymax=Math.max(ay,by,cy);if(ymax<1.2)return;const ymin=Math.min(ay,by,cy);if(ymin>cap)return;const ",
    "const ymax=Math.max(ay,by,cy);if(ymax<1.2&&!og)return;const ymin=Math.min(ay,by,cy);if(ymin>cap)return;\n"
    "    /* on a pizza the ground is hills: a triangle that lies on it (the pizza itself, the road, kerbs, painted lines) is ground, not a thing */if(og&&ay<groundAt(ax,az)+2.4&&by<groundAt(bx,bz)+2.4&&cy<groundAt(cx,cz)+2.4)return;const ")
rep("if(hi>=1.2&&lo<=cap)ins(i*nz+k,lo,hi);}};", "if((og||hi>=1.2)&&lo<=cap)ins(i*nz+k,lo,hi);}};")
rep("if(!in0||top<1.2)continue;used++;", "if(!in0||(top<1.2&&!og))continue;used++;")

# ---- the track lookup and the surfaces, for a pizza too
rep("function sbHashTrack(){const H=SB.hash=new Map(),W=TOYW()+3.4,sl=T.L/N;", "function sbHashTrack(){const H=SB.hash=new Map(),W=(SB.kind==='toy'?TOYW():WALLD)+3.4,sl=T.L/N;")
rep("  for(const g of SB.gates){const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-20&&d<SB_GLEN){const l=(x-g.x)*g.tx+(z-g.z)*g.tz;if(l>-SB_GW&&l<SB_GW)return 0;",
    "  for(const g of SB.gates){if(g.road)continue;const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-20&&d<SB_GLEN){const l=(x-g.x)*g.tx+(z-g.z)*g.tz;if(l>-g.hw&&l<g.hw)return 0;")
rep("  {const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])put(1e6,-1e9,-1);/* past the room's own edge */else{",
    "  if(SB.rim&&x*x+z*z>SB.rim*SB.rim)put(1e6,-1e9,-1);/* past the crust */\n  {const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])put(1e6,-1e9,-1);/* past the room's own edge */else{")
rep("  if(a){const sl=T.L/N,W=TOYW(),n0=n;for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y,u=dx*p.tx+dz*p.ty;if(u<-sl*.75||u>sl*.75)continue;const lat=dx*p.nx+dz*p.ny,al=Math.abs(lat);if(al>W+3.2)continue;\n"
    "      const f=u/sl,fi=Math.floor(f),e=eyAt(((j+fi)%N+N)%N,f-fi),top=e+(al>W?SB_RAIL:0);",
    "  if(a){/* (on a pizza the track lies on the hills: its height is the ground's plus its own; it has no raised edge to bump over, and its width for\n"
    "     \"the lap is always open\" is the road's) */const sl=T.L/N,toy=SB.kind==='toy',W=toy?TOYW():RW+10,g0=toy?0:groundAt(x,z),n0=n;for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y,u=dx*p.tx+dz*p.ty;if(u<-sl*.75||u>sl*.75)continue;const lat=dx*p.nx+dz*p.ny,al=Math.abs(lat);if(al>(toy?W+3.2:WALLD))continue;\n"
    "      const f=u/sl,fi=Math.floor(f),e=g0+eyAt(((j+fi)%N+N)%N,f-fi),top=e+(toy&&al>W?SB_RAIL:0);")
rep("function sbG(x,z,wy){if(wy==null)wy=1e9;const n=sbSurf(x,z),S=SB.S;let h=0;", "function sbG(x,z,wy){if(wy==null)wy=1e9;const n=sbSurf(x,z),S=SB.S;let h=SB.kind==='toy'?0:groundAt(x,z);")

# ---- gates of every kind
between("function sbGates(){", "function sbDuctEl(){", r"""const sbSeed=id=>{let h=7;for(let i=0;i<id.length;i++)h=(h*31+id.charCodeAt(i))%9973;return h/9973;};
function sbGates(){const R=SB.reg,id=SB.regId;SB.gates=[];
  if(SB.kind==='toy'){const b=SB.col.b,cx=R.room?SB_RX:(g=>(g+.75)*SB_M),cz=R.room?SB_RZ:(g=>-(g-3.5)*SB_M);
    for(const d of R.gates||[]){if(!sbRegOf(d.to))continue;const g={id:d.id,to:d.to,at:d.at,label:d.label,hw:d.hw||SB_GW,plain:!!d.plain,y:0};
      if(d.w==='E'){g.x=b[1];g.z=cz(d.p);g.nx=1;g.nz=0;}else if(d.w==='W'){g.x=b[0];g.z=cz(d.p);g.nx=-1;g.nz=0;}else if(d.w==='N'){g.x=cx(d.p);g.z=b[2];g.nx=0;g.nz=-1;}else{g.x=cx(d.p);g.z=b[3];g.nx=0;g.nz=1;}
      g.tx=-g.nz;g.tz=g.nx;SB.gates.push(g);}}
  else{const L=(SB_LINKS[id]||[]).filter(t=>sbRegOf(t)),n=L.length;L.forEach((to,i)=>{const m=MAPS.find(q=>q.id===to),g={id:id+'>'+to,to,at:to+'>'+id,label:(m?m.name:to).toUpperCase(),hw:SB_GW,y:0};
      if(SB.kind==='open'){/* an arch in the crust, each neighbour its own share of the circle: the first bearing near there with clear ground in front of it */
        const a0=(i/n+sbSeed(id))*6.28318;let best=a0;for(const da of [0,.14,-.14,.28,-.28,.42,-.42,.56,-.56,.7,-.7,.84,-.84]){const a=a0+da,c=Math.cos(a),q=Math.sin(a);let ok=true;for(let r=SB.rim-26;r>SB.rim-300&&ok;r-=12){const x=c*r,z=q*r;if(sbBlocked(x,z,groundAt(x,z)))ok=false;}if(ok){best=a;break;}}
        g.nx=Math.cos(best);g.nz=Math.sin(best);g.x=g.nx*SB.rim;g.z=g.nz*SB.rim;g.y=groundAt(g.x-g.nx*24,g.z-g.nz*24);}
      else{/* where you keep to the road: an arch over the left-hand lane, the gates spread round the lap and clear of the start line */
        const j=Math.round(((i+.5)/n*.86+.07)*N)%N,p=track[j],lat=-RW*.5;g.road=1;g.j=j;g.x=p.x+p.nx*lat;g.z=p.y+p.ny*lat;g.nx=p.tx;g.nz=p.ty;g.y=groundAt(g.x,g.z)+(p.ey||0);g.hw=RW*.4;}
      g.tx=-g.nz;g.tz=g.nx;SB.gates.push(g);});}
  /* drawn: the opening (flat black, an arch), its surround, the duct behind it (black inside), and a name plate above */
  for(const g of SB.gates){if(g.plain)continue;const proud=R.room?6:0,G=new THREE.Group(),W=g.hw+1,H=g.road?31:27,arch=(w,h)=>{const sh=new THREE.Shape();sh.moveTo(-w,0);sh.lineTo(-w,h-w*.55);sh.absarc(0,h-w*.55,w,Math.PI,0,true);sh.lineTo(w,0);sh.lineTo(-w,0);return sh;};
    const hole=new THREE.Mesh(new THREE.ShapeGeometry(arch(W,H),12),new THREE.MeshBasicMaterial(g.road?{color:'#04060c',side:THREE.DoubleSide,transparent:true,opacity:.86,depthWrite:false}:{color:'#050403',side:THREE.DoubleSide}));hole.position.z=proud+(R.room?1.2:.9);G.add(hole);
    const ring=arch(W+3.4,H+3.4);ring.holes.push(arch(W,H));const fm=g.road?new THREE.MeshStandardMaterial({color:'#12202c',emissive:'#39d0ff',emissiveIntensity:1.6,roughness:.4}):new THREE.MeshStandardMaterial({color:R.room?'#7a5636':SB.kind==='open'?'#a9743c':'#5d5148',roughness:.7});
    const fr=new THREE.Mesh(new THREE.ExtrudeGeometry(ring,{depth:g.road?2.4:1.6,bevelEnabled:false,curveSegments:12}),fm);fr.position.z=proud+.2;fr.castShadow=!g.road;G.add(fr);
    if(!g.road){const duct=new THREE.Mesh(new THREE.BoxGeometry(2*W+4,H+8,SB_GLEN+20),new THREE.MeshBasicMaterial({color:'#050403',side:THREE.BackSide}));duct.position.set(0,(H+8)/2-.5,-(SB_GLEN+20)/2-.2);G.add(duct);}
    const cv=cnv(512,64),q=cv.getContext('2d');q.fillStyle=g.road?'#06121c':'#f3ead6';q.fillRect(0,0,512,64);q.strokeStyle=g.road?'#39d0ff':'#5a3d22';q.lineWidth=6;q.strokeRect(3,3,506,58);q.fillStyle=g.road?'#bff1ff':'#3a2513';q.textAlign='center';q.textBaseline='middle';
    let fs=36;q.font='900 '+fs+'px Arial';while(q.measureText(g.label).width>480&&fs>16){fs-=2;q.font='900 '+fs+'px Arial';}q.fillText(g.label,256,34);
    const tx=T2(cv);tx.userData.keepCanvas=true;const pw=Math.max(34,Math.min(70,g.label.length*4.2)),plate=new THREE.Mesh(new THREE.PlaneGeometry(pw,pw/8),g.road?new THREE.MeshBasicMaterial({map:tx,toneMapped:false}):new THREE.MeshStandardMaterial({map:tx,roughness:.8}));plate.position.set(0,H+9.5,proud+.7);G.add(plate);
    G.position.set(g.x,g.y,g.z);G.rotation.y=Math.atan2(-g.nx,-g.nz);/* its face looks back at whoever drives up to it */G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);}}
""")
rep("function sbDuctShow(){const k=player;let o=0;if(SB.trav)o=1;else if(SBX&&k)for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz,l=(k.x-g.x)*g.tx+(k.y-g.z)*g.tz;if(Math.abs(l)<SB_GW+4&&d>2)o=Math.max(o,Math.min(1,(d-2)/34));}",
    "function sbDuctShow(){const k=player;let o=0;if(SB.trav)o=1;else if(SBX&&k)for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz,l=(k.x-g.x)*g.tx+(k.y-g.z)*g.tz;if(Math.abs(l)>=g.hw+4)continue;\n"
    "    if(g.road){if(d>-26&&d<30&&Math.abs((k.wy||0)-g.y)<14&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2)o=Math.max(o,Math.min(1,(d+26)/24));}else if(g.plain){if(d>14)o=Math.max(o,Math.min(1,(d-14)/50));}else if(d>2)o=Math.max(o,Math.min(1,(d-2)/34));}")
# travel: any region; arrival by the kind of gate; fast travel to a start line (g.start)
between("async function sbTravel(g){", "/* ---- a race from its start line ----", r"""async function sbTravel(g){if(SB.trav)return;const mi=MAPS.findIndex(m=>m.id===g.to);if(mi<0||!sbRegOf(g.to))return;SB.trav=g;const k=player,sp=Math.max(70,Math.abs(k.speed));sbDuctShow();state='loading';
  try{await paint();await paint();projectiles.forEach(p=>scene.remove(p.mesh));hazards.forEach(h=>scene.remove(h.mesh));projectiles=[];hazards=[];
    if(mi!==mapIdx||curRev){mapIdx=mi;try{store.set('crust-map',mi);}catch(e){}loadMap(mi,false);}for(const q of karts){q.idx=0;q.prog=0;q.loop=null;q.sc=null;q.glide=false;}
    await Promise.all(Object.values(PROPT).map(t=>t.image&&t.image.decode&&!t.image.complete?t.image.decode().catch(()=>{}):null));}catch(e){console.warn('sandbox travel',e);}
  sbArm();const a=g.start?null:SB.gates.find(q=>q.id===g.at)||SB.gates[0];
  if(a&&a.road){k.x=k.px=a.x+a.nx*34;k.y=k.py=a.z+a.nz*34;k.a=k.ma=k.pa=k.pma=Math.atan2(a.nz,a.nx);k.idx=(a.j+Math.round(34/(T.L/N)))%N;}
  else if(a){const out=a.plain?46:SB_GLEN-60;k.x=k.px=a.x+a.nx*out;k.y=k.py=a.z+a.nz*out;const h=Math.atan2(-a.nz,-a.nx);k.a=k.ma=k.pa=k.pma=h;}
  else{/* no gate to come out of (fast travel): the start line, a little behind it */const j=(N-Math.round(40/(T.L/N)))%N,p=track[j];k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.idx=j;}
  k.speed=sp;k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.charge=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;
  if(SBF){const lvl=a&&!a.road?a.y:((SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0));k.wy=k.pwy=k.lastG=sbG(k.x,k.y,lvl+2);k.idx=sbIdx(k,k.idx);}else k.wy=k.pwy=k.lastG=kGround(k);
  k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rg=k.wy;k.rma=k.ma;cam.a=k.ma;camSnap=true;try{warmScene();}catch(e){}SB.cool=1;state='race';SB.trav=null;SB.hudT=0;sbHud();showBanner(SB.reg.name,2,'md');}
""")
rep("function sbFlag(){const p=track[0],e=p.ey||0,", "function sbFlag(){const p=track[0],e=(SB.kind==='toy'?0:groundAt(p.x,p.y))+(p.ey||0),")
rep("const mi=MAPS.findIndex(m=>m.id===id);if(mi<0||!SB_REG[id])return false;mode='sb';", "const mi=MAPS.findIndex(m=>m.id===id);if(mi<0||!sbRegOf(id))return false;mode='sb';")

# coins: heights on a pizza; rare coins for the made-up regions
rep("for(let q=0;q<6;q++){const p=track[(j0+q*gap)%N];put(p.x+p.nx*lat,(p.ey||0)+5.4,p.y+p.ny*lat);}}",
    "for(let q=0;q<6;q++){const p=track[(j0+q*gap)%N],x=p.x+p.nx*lat,z=p.y+p.ny*lat;put(x,(SB.kind==='toy'?0:groundAt(x,z))+(p.ey||0)+5.4,z);}}\n"
    "  if(R.auto&&SB.kind==='open'){/* three pepperoni coins out on the pizza, away from the road: the same places every time (the track's name is the seed); each must have open ground between it and the road */\n"
    "    const rnd=prng(hashStr(SB.regId)+5);let made=0;for(let t=0;t<400&&made<3;t++){const a=rnd()*6.28318,r=(.3+rnd()*.6)*SB.rim,x=Math.cos(a)*r,z=Math.sin(a)*r,g0=groundAt(x,z);if(sbBlocked(x,z,g0))continue;\n"
    "      let bj=0,bd=1e18;for(let j=0;j<N;j+=4){const p=track[j],d=(p.x-x)**2+(p.y-z)**2;if(d<bd){bd=d;bj=j;}}const d=Math.sqrt(bd);if(d<WALLD+60||C.some(c=>c.rare&&(c.x-x)**2+(c.z-z)**2<400*400))continue;\n"
    "      const p=track[bj];let ok=true;for(let q=12;q<d-RW&&ok;q+=12){const xx=x+(p.x-x)*q/d,zz=z+(p.y-z)*q/d;if(sbBlocked(xx,zz,groundAt(xx,zz)))ok=false;}if(!ok)continue;put(x,g0+8,z,true,SB.regId+':'+made);made++;}}\n"
    "  if(R.auto&&SB.kind==='road')for(const [f,i] of [[.37,0],[.81,1]]){/* two on the road's far edge */const p=track[Math.round(f*N)%N],x=p.x+p.nx*(RW-9),z=p.y+p.ny*(RW-9);put(x,groundAt(x,z)+(p.ey||0)+8,z,true,SB.regId+':'+i);}")

# arm / off / start / camera
between("function sbArm(){", "function sbOff(){", r"""function sbArm(){const def=MAPS[mapIdx],R=def&&sbRegOf(def.id),on=mode==='sb'&&!NET.cfg&&!!R;if(!on){if(SBX)sbOff();return;}
  SBX=true;SB.regId=def.id;SB.reg=R;SB.kind=R.kind||'toy';SBF=SB.kind!=='road';BATTLE=SBF;SB.shapes=R.shapes?R.shapes():[];SB.rim=0;SB.col=null;SB.hash=null;SB.gates=[];
  if(SBF){let b=TOYROOM;if(SB.kind==='open'){const r=RIM+70;b=[-r,r,-r,r];SB.rim=RIM;}else if(!b){b=[1e9,-1e9,1e9,-1e9];for(const p of track){b[0]=Math.min(b[0],p.x-400);b[1]=Math.max(b[1],p.x+400);b[2]=Math.min(b[2],p.y-400);b[3]=Math.max(b[3],p.y+400);}}sbColumns(b);sbHashTrack();}
  sbCoins();sbGates();sbFlag();SB.hudT=0;SB.msgT=0;SB.camF=1;document.body.classList.add('battle');}
""")
rep("function sbOff(){if(!SBX)return;SBX=false;const def=MAPS[mapIdx];", "function sbOff(){if(!SBX)return;SBX=false;SBF=false;const def=MAPS[mapIdx];")
rep("function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}",
    "function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;if(SBF){k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}}")
rep("function sbCam(){const k=camT;if(!k||state==='menu')return;", "function sbCam(){const k=camT;if(!k||state==='menu'||!SBF)return;")
rep("function sbSolid(x,z,y){for(const g of SB.gates){const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-12&&d<SB_GLEN+10&&Math.abs((x-g.x)*g.tx+(z-g.z)*g.tz)<SB_GW+1)return false;}",
    "function sbSolid(x,z,y){for(const g of SB.gates){if(g.road)continue;const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-12&&d<SB_GLEN+10&&Math.abs((x-g.x)*g.tx+(z-g.z)*g.tz)<g.hw+1)return false;}")
# the gate trigger: by the kind of gate
rep("else for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d>SB_GLEN-70&&Math.abs((k.x-g.x)*g.tx+(k.y-g.z)*g.tz)<SB_GW+2&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2){sbTravel(g);return;}}",
    "else for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d>(g.road?0:g.plain?64:SB_GLEN-70)&&(!g.road||(d<26&&Math.abs((k.wy||0)-g.y)<14))&&Math.abs((k.x-g.x)*g.tx+(k.y-g.z)*g.tz)<g.hw+2&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2){sbTravel(g);return;}}")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
