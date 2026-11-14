"""Patch 27 (web v193): Sandbox on every track of the game (tools/mini/sandbox.js; docs/SANDBOX-PLAN.md "The rest of the maps").
Sandbox now has three kinds of region:
  toy    the four places of the house: drive anywhere, ground and walls from sandbox.js (as before)
  open   the fifteen pizza tracks: drive anywhere on the pizza; the ground is the engine's own, the walls are read from what is drawn
  road   Sauce Spiral and the four Neon tracks: the road hangs in the air or winds up a tower, so you keep to it, both ways, with the race's own walls
SBX is on in all three; SBF ("free") is on in the first two, and is what the driving hooks of patch 22 to 24 now ask.
(The picture hooks, rg and the five surfH points, and the chase camera ask BATTLE, which is on exactly when SBF is; the toy slope camera
asks SBX and only runs on toy tracks. None of those needed a change.)
Run once: py.cmd tools/mini/patch27.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'if(SBF)best=sbIdx' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


# ---- the free-driving hooks ask SBF
rep("if(!SBX&&pj.flo!==undefined", "if(!SBF&&pj.flo!==undefined")
rep("else if(SBX&&k.wy-G>SB_STEP)", "else if(SBF&&k.wy-G>SB_STEP)")
rep("if(SBX)best=sbIdx(k,k.idx);", "if(SBF)best=sbIdx(k,k.idx,best);")
rep("&&!SBX;k.airT=0;k.wvy=Math.min(k.gRate,SBX?22:42);", "&&!(SBF&&SB.kind==='toy');k.airT=0;k.wvy=Math.min(k.gRate,SBF&&SB.kind==='toy'?22:42);")
rep("if(d>RIM&&!SBX)", "if(d>RIM&&!SBF)")
rep("function scStep(k){if(SBX||!SHORTS.length)return;", "function scStep(k){if(SBF||!SHORTS.length)return;")
# ---- what any Sandbox drive needs, free or not: no finish, no lap banner, no wrong-way warning, its own tick and start, its own item
rep("&&!k.finished&&!BATTLE&&finAt(k)){", "&&!k.finished&&!BATTLE&&!SBX&&finAt(k)){")
rep("CURP=null;if(BATTLE)battleTick(dt);", "CURP=null;if(BATTLE||SBX)battleTick(dt);")
rep("resetRace(false);if(BATTLE)battleStart();", "resetRace(false);if(BATTLE||SBX)battleStart();")
rep("if(state==='race'&&!BATTLE&&!player.finished&&lap>lapShown)", "if(state==='race'&&!BATTLE&&!SBX&&!player.finished&&lap>lapShown)")
rep("player.wrongT=back&&!BATTLE?", "player.wrongT=back&&!BATTLE&&!SBX?")
rep("function rollItem(pos){if(BATTLE)return bbRoll();", "function rollItem(pos){if(BATTLE||SBX)return bbRoll();")
# ---- the pizza tracks' jump ramps are the engine's own (as the toy tracks'): named so the columns leave them out
rep("topM=new THREE.MeshStandardMaterial({map:T2(rampTex()),roughness:.45}),sideM2=", "topM=new THREE.MeshStandardMaterial({name:'toyramp',map:T2(rampTex()),roughness:.45}),sideM2=")
# ---- the menu: every track is a place to start (not the battle arena)
rep("si=SB_REG[MAPS[mapIdx].id]?mapIdx:MAPS.findIndex(m=>m.id==='backyard'),", "si=sbRegOf(MAPS[mapIdx].id)?mapIdx:MAPS.findIndex(m=>m.id==='backyard'),")
rep("if(mode==='sb'&&!SB_REG[MAPS[mapIdx].id]){", "if(mode==='sb'&&!sbRegOf(MAPS[mapIdx].id)){")
rep("mode==='sb'?'World: Home. Start in':'Track';", "mode==='sb'?'World. Start in':'Track';")

# ---- web v193, Sandbox only (SBX; never in a race, never on line): the owner's play-test
# "some maps you cant go backwards on the tracks but you should be able to go backwards": what stopped a kart driving a toy track the wrong way round was the
# back of every jump ramp (a wall 6 high) and the way out of every loop. Both now work from behind in Sandbox.
#   a ramp from behind: a short slope up its back, then down its face, and no launch off its low end
rep("const hh=r.h*clamp(al,0,r.len)/r.len;const fwd=Math.cos(k.ma)*fx+Math.sin(k.ma)*fy;",
    "const hh=r.h*clamp(al,0,r.len)/r.len;const fwd=Math.cos(k.ma)*fx+Math.sin(k.ma)*fy;"
    "if(SBX&&!r.glide&&fwd*(k.speed<0?-1:1)<-.2&&Math.abs(lat)<=r.w+2){/* (Sandbox, driving the track the wrong way round) */if(al>r.len-1){const hb=r.h*clamp((r.len+6-al)/6,0,1);if(k.wy<=G+hb+2.5){G+=hb;onR=true;k.rBk=2;}continue;}if(al>=0&&k.wy>=G+hh-2.5&&k.wy<=G+hh+2.5){G+=hh;onR=true;k.rBk=2;continue;}}")
rep("  else if(k.onRamp&&!onR&&k.speed>20){k.air=true;k.big=true;", "  else if(k.onRamp&&!onR&&k.speed>20&&!(SBX&&k.rBk>0)){k.air=true;k.big=true;")
rep("  k.onRamp=onR;k.onGlide=gR;k.z=Math.max(0,k.wy-G);", "  k.onRamp=onR;k.onGlide=gR;if(k.rBk>0&&!onR)k.rBk--;k.z=Math.max(0,k.wy-G);")
#   a loop from its far end: ridden the other way round
rep("if(dj>=1&&dj<=8){const P=LOOP.p,al=(k.x-P.x)*P.tx+(k.y-P.y)*P.ty,lt=(k.x-P.x)*P.nx+(k.y-P.y)*P.ny;if(al>=-1){k.loop={th:0,p:P,",
    "if(dj>=1&&dj<=8){const P=LOOP.p,al=(k.x-P.x)*P.tx+(k.y-P.y)*P.ty,lt=(k.x-P.x)*P.nx+(k.y-P.y)*P.ny;if(al>=-1&&!(SBF&&(al>40||Math.abs(lt+LOOP.S)>LOOP.W+8||Math.abs((k.wy||0)-LOOP.g0)>12))&&!(SBX&&(Math.cos(k.ma)*P.tx+Math.sin(k.ma)*P.ty)*(k.speed<0?-1:1)<0)){k.loop={th:0,p:P,")
rep("  for(const LOOP of LOOPS)if(!LOOP.full&&!k.air&&k.speed>50&&k.spin<=0&&!k.loop){",
    "  if(SBX)for(const LOOP of LOOPS)if(!k.loop&&LOOP.full){/* Sandbox: into a loop from its far end, heading back along the track: round it the other way */let dj=k.idx-LOOP.j;if(dj>N/2)dj-=N;if(dj<-N/2)dj+=N;if(dj>=-2&&dj<=8){const P=LOOP.p,al=(k.x-P.x)*P.tx+(k.y-P.y)*P.ty,lt=(k.x-P.x)*P.nx+(k.y-P.y)*P.ny;\n"
    "      if(al<=1&&al>-16&&Math.abs((k.wy||0)-LOOP.g0)<=12&&Math.abs(k.speed)>5&&(Math.cos(k.ma)*P.tx+Math.sin(k.ma)*P.ty)*(k.speed<0?-1:1)<-.3&&lt>2&&lt<LOOP.shift-LOOP.S+LOOP.W+3){k.loop={th:Math.PI*2,rev:1,p:P,lat0:clamp(lt-LOOP.shift,-LOOP.S-LOOP.W+5,-LOOP.S+LOOP.W-5),shift:LOOP.shift,g0:LOOP.g0,j:LOOP.j,full:true,src:LOOP};k.speed=Math.abs(k.speed);k.loopTh=k.pth=Math.PI*2;k.drift=0;k.spin=0;k.air=false;k.big=false;k.glide=false;if(k===player)SFX.pad();}}}\n"
    "  for(const LOOP of LOOPS)if(!LOOP.full&&!k.air&&k.speed>50&&k.spin<=0&&!k.loop&&!(SBF&&(k.x-LOOP.p.x)**2+(k.y-LOOP.p.y)**2>90*90)){")
rep("function loopStep(k,dt){const L=k.loop;k.speed=Math.max(k.speed,BASE_MAX*1.18);L.th+=k.speed*dt/LOOPR;const th=Math.min(L.th,Math.PI*2),",
    "function loopStep(k,dt){const L=k.loop;k.speed=Math.max(k.speed,BASE_MAX*1.18);L.th+=(L.rev?-1:1)*k.speed*dt/LOOPR;const th=Math.max(0,Math.min(L.th,Math.PI*2)),")
rep("k.wy=L.g0+hg+.35;k.z=hg;k.loopTh=th;k.a=k.ma=p.ang;k.drift=0;k.steer*=.9;k.air=false;\n  if(L.th>=Math.PI*2){",
    "k.wy=L.g0+hg+.35;k.z=hg;k.loopTh=th;k.a=k.ma=p.ang+(L.rev?Math.PI:0);k.drift=0;k.steer*=.9;k.air=false;\n"
    "  if(L.rev){/* (Sandbox only) out at the loop's near end, a little before it on the lap */if(L.th<=0){const j=(L.j-3+N)%N;let di=j-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=j;k.loop=null;k.loopTh=0;k.pth=0;k.boost=Math.max(k.boost,1.5);k.wvy=0;k.gRate=0;k.wy=k.lastG=L.g0;k.z=0;if(k===camT)shake(.5);if(k===player)SFX.boost(3);}return;}\n"
    "  if(L.th>=Math.PI*2){")
rep("  else m.g.rotation.set(0,-a,lth);", "  else m.g.rotation.set(0,-a,k.loop&&k.loop.rev?-lth:lth);")
rep("cam.F.set(p.tx*ct,st,p.ty*ct).normalize();cam.U.set(-p.tx*st,ct,-p.ty*st);cam.P.set(camT.rx,camT.rz,camT.ry);",
    "cam.F.set(p.tx*ct,st,p.ty*ct).normalize();cam.U.set(-p.tx*st,ct,-p.ty*st);const lrv=!!(camT.loop&&camT.loop.rev);if(lrv)cam.F.multiplyScalar(-1);cam.P.set(camT.rx,camT.rz,camT.ry);")
rep("camera.up.lerp(cam.U,1-Math.exp(-12*dt)).normalize();cam.a=p.ang;}", "camera.up.lerp(cam.U,1-Math.exp(-12*dt)).normalize();cam.a=p.ang+(lrv?Math.PI:0);}")
# "if you hold down both brake buttons in sandbox it should completely stop the car and there should be a park button on screen"
rep("bEls.forEach(b=>b.classList.toggle('on',bOn.has(b)));keys.brake=brakeT.size>0||brakes.size>0;}", "bEls.forEach(b=>b.classList.toggle('on',bOn.has(b)));keys.brake=brakeT.size>0||brakes.size>0;keys.brakeBoth=bOn.size>1;}")
rep("upd();keys.left=keys.right=keys.brake=false;keys.lookKey=false;", "upd();keys.left=keys.right=keys.brake=false;keys.brakeBoth=false;keys.lookKey=false;")
rep("  if(TD.on&&player&&state==='race'&&!player.finished){tdDrive(player,o);", "  if(SBX&&sbStop()){/* Sandbox: parked, or both brake buttons held: no throttle, and no brake either (held, it would reverse) */o.brake=false;o.nb=false;o.mul=0;}\n  if(TD.on&&player&&state==='race'&&!player.finished){tdDrive(player,o);")
# "on controller make the y button open the map" (Sandbox has no special ability to fire); D-pad down is Park
rep("    if(edge(M.Y)&&!(SPEC&&SPEC.on))abilQueued=true;", "    if(edge(M.Y)&&!(SPEC&&SPEC.on)){if(SBX)sbMap(true,'drive');else abilQueued=true;}if(SBX&&edge(M.BACK))sbMap(true,'drive');if(SBX&&edge(M.DOWN)&&state==='race')sbPark();")
rep("PAD.look=pr(M.X)||pr(M.BACK);", "PAD.look=pr(M.X)||(pr(M.BACK)&&!SBX);/* (in Sandbox Select opens the map) */")
rep("function togglePause(){if(!results.hidden)return;", "function togglePause(){if(SBM.open){sbMap(false);return;}/* (Sandbox's map is up: pause and Start close it) */if(!results.hidden)return;")
rep("    if(edge(M.B))padBack();}\n  if(edge(M.START))togglePause();", "    if(SBM.open&&(edge(M.Y)||edge(M.BACK)))sbMap(false);else\n    if(edge(M.B))padBack();}\n  if(edge(M.START))togglePause();")
# the loop's hoop: its low lips (under a step's height) are not solid in Sandbox, see sbColumns
rep("lm.userData.col=true;/* the loop is solid in Sandbox */", "lm.userData.col=true;lm.userData.colMin=6.5;/* the loop is solid in Sandbox, but for its low lips */")
rep("Leave the track, go under the furniture, look behind things. Gold coins lead the way; pepperoni coins are hidden in every room. Choose where to start: the doors between the rooms, and the world beyond the house, are on their way.",
    "One world: the house, and beyond the garage door every track of the game. Drive anywhere in the rooms and on the pizzas; warp tunnels lead from place to place. Gold coins lead the way; pepperoni coins are hidden everywhere. The map travels fast: Y on a controller, M on a keyboard, or Map in the pause menu. Park stops the car.")
# a glide canyon cannot be jumped from its far side: a kart driving the track the wrong way round in Sandbox that drops into it is set down on the
# other side (the usual place, a little before the ramp) still facing the way it was going
rep("function respawn(k){const j=(GLIDE.rj-24+N)%N,p=track[j];", "function respawn(k){const j=(GLIDE.rj-24+N)%N,p=track[j],bk=SBX&&Math.cos(k.ma)*track[k.idx].tx+Math.sin(k.ma)*track[k.idx].ty<0;")
rep("k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=p.ang;k.speed=BASE_MAX*.5;k.wy=k.pwy=k.lastG=groundAt(p.x,p.y)+(p.ey||0);", "k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=p.ang+(bk?Math.PI:0);k.speed=BASE_MAX*.5;k.wy=k.pwy=k.lastG=groundAt(p.x,p.y)+(p.ey||0);")
# A kart off the track in free driving keeps the last lap point it was on (sbIdx). A loop or a boost pad is ON the track: neither may act on a kart that
# is not (found 2026-11-14: on Basil Boulevard a kart far out on the pizza, its lap point a few before the loop's, was taken into the loop from 1600 away,
# because a loop went by the lap point alone). In free driving the loops' own conditions above ask that the kart is AT the loop (how far along, which lane, what height), and the pads here that it is within 110.
rep("  for(const pd of pads){let dj=k.idx-pd.j;", "  for(const pd of pads){if(SBF){const q=track[pd.j];if((q.x-k.x)**2+(q.y-k.y)**2>110*110)continue;}let dj=k.idx-pd.j;")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
