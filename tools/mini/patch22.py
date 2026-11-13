"""Patch 22 (web v188): the engine's hooks for Sandbox (tools/mini/sandbox.js; docs/SANDBOX-PLAN.md).
Sandbox rides on Balloon Battle's hooks (BATTLE is on while SBX is; battle.js hands over), so only what a battle did not need is here.
Every hook is behind SBX or mode 'sb': a race, a Grand Prix, a battle and a friends' race run exactly the code they ran before.
Run once: py.cmd tools/mini/patch22.py   (then inject_mini.py, which carries sandbox.js in)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'sbArm()' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


# ---- driving
rep("let G=BATTLE?battleG(k.x,k.y):kGround(k),onR=false,gR=false;",
    "let G=BATTLE?battleG(k.x,k.y,k.wy):kGround(k),onR=false,gR=false;")   # the track crosses over itself: which level, by the kart's own height
rep("  {const pj=track[k.idx];if(pj.flo!==undefined&&!k.loop&&!k.glide&&!k.sc){",
    "  {const pj=track[k.idx];if(!SBX&&pj.flo!==undefined&&!k.loop&&!k.glide&&!k.sc){")   # the lap's own side limits are a race's
rep("  else if(rate<k.gRate-260*dt*1.1&&k.speed>60&&!(MULTI&&(track[k.idx].ey||0)>1)){k.air=true;k.big=(k.gRate-rate)>55;",
    "  else if(SBX&&k.wy-G>SB_STEP){k.air=true;k.big=false;k.airT=0;k.wvy=0;}/* off an edge: it falls */\n"
    "  else if(rate<k.gRate-260*dt*1.1&&k.speed>60&&!(MULTI&&(track[k.idx].ey||0)>1)){k.air=true;k.big=(k.gRate-rate)>55;")
rep("let di=best-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=best;",
    "if(SBX)best=sbIdx(k,k.idx);let di=best-k.idx;if(di>N/2)di-=N;if(di<-N/2)di+=N;k.prog+=di;k.idx=best;")
# (and, by hand the same day: in that rule's own launch, `k.big=...&&!SBX` and `k.wvy=Math.min(k.gRate,SBX?22:42)`: crossing the track's raised edge is a small hop)
# (and: the drawn ground under the kart is `SBX?sbG(x,y,z):...`, and the camera's rise with the track's slope is skipped while `camT.sbOff`, the kart being off the track:
#  both read the height of a lap point, and off the track the kart's lap point is only the last one it was on)
# (and: the five heights the kart's body is laid on, `SBX?sbG(..,z+1):surfH(..,J)`: the body sits on Sandbox's ground, not on the slope of a lap point)
# (and: the lap-count finish is `!BATTLE&&k.prog>=LAPS*N`. Driving the track round twice in Sandbox ended it with a results screen; the same
#  rule could end a Balloon Battle for a kart that circled the middle of the table three times)
# ---- one kart, no countdown to speak of, no ghost
rep("  else for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));",
    "  else if(SBX&&!demo)karts.push(makeKart(selected,4,true,diff,playerBuild));\n"
    "  else for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));")
rep("if(k.m&&k.m.g)k.m.g.visible=true;}resetRace(false);if(BATTLE)battleStart();",
    "if(k.m&&k.m.g)k.m.g.visible=true;}sbArm();resetRace(false);if(BATTLE)battleStart();")
rep("state='countdown';cd=3.4;lastCd=4;abilReset();", "state='countdown';cd=SBX?.9:3.4;lastCd=SBX?1:4;abilReset();")
rep("if(mode!=='lss')ghostStart();", "if(mode!=='lss'&&!SBX)ghostStart();")
rep("function toMenu(){LAPS=3;", "function toMenu(){sbOff();LAPS=3;")
# ---- the menu: a fifth mode. Its world for now is the back garden.
rep('<button data-m="bb">Balloon Battle</button></div>', '<button data-m="bb">Balloon Battle</button><button data-m="sb">Sandbox</button></div>')
rep('<div class="seg seg4" id="modeSeg">', '<div class="seg seg5" id="modeSeg">')
rep(".seg4{grid-template-columns:repeat(4,1fr)}",
    ".seg4{grid-template-columns:repeat(4,1fr)}.seg5{grid-template-columns:repeat(5,1fr)}.seg5 button{font-size:12px;padding-left:2px;padding-right:2px}")
rep("{const bi=MAPS.findIndex(m=>m.battle),want=mode==='bb'?bi:mapIdx===bi?0:mapIdx;if(want!==mapIdx&&mode!=='gp'){",
    "{const bi=MAPS.findIndex(m=>m.battle),si=MAPS.findIndex(m=>m.id==='backyard'),want=mode==='bb'?bi:mode==='sb'?si:mapIdx===bi?0:mapIdx;if(want!==mapIdx&&mode!=='gp'){")
rep("{const bi=MAPS.findIndex(m=>m.battle);if(mode==='bb')mapIdx=bi<0?0:bi;else if(MAPS[mapIdx].battle)mapIdx=0;}",
    "{const bi=MAPS.findIndex(m=>m.battle);if(mode==='bb')mapIdx=bi<0?0:bi;else if(MAPS[mapIdx].battle)mapIdx=0;if(mode==='sb'){const si=MAPS.findIndex(m=>m.id==='backyard');if(si>=0)mapIdx=si;}}")
rep("$('maps').hidden=mode==='gp'||mode==='bb';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp'||mode==='bb';$('trackLabel').textContent=mode==='gp'?'Cup':mode==='bb'?'Arena: Prep Table Showdown':'Track';",
    "$('maps').hidden=mode==='gp'||mode==='bb'||mode==='sb';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp'||mode==='bb'||mode==='sb';$('trackLabel').textContent=mode==='gp'?'Cup':mode==='bb'?'Arena: Prep Table Showdown':mode==='sb'?'World: Home, the back garden':'Track';")
rep("{const mn=$('modeNote');if(mn&&mode==='bb'){",
    "{const mn=$('modeNote');if(mn&&mode==='sb'){mn.hidden=false;mn.textContent='Sandbox: drive anywhere, no race and no clock. Leave the track, cross the lawn, look behind things. Gold coins lead the way; six pepperoni coins are hidden in the garden. More of the house and the world beyond are on their way.';}else if(mn&&mode==='bb'){")
rep("$('startBtn').textContent=mode==='bb'?'Start battle':", "$('startBtn').textContent=mode==='sb'?'Start exploring':mode==='bb'?'Start battle':")
rep("mode==='bb'?'Balloon Battle':mode==='lss'?'Last Slice Standing':'Single race')+' · '+CLASSES[clsKey].label;",
    "mode==='sb'?'Sandbox':mode==='bb'?'Balloon Battle':mode==='lss'?'Last Slice Standing':'Single race')+' · '+CLASSES[clsKey].label;")
rep("if(b.dataset.m==='bb'&&NET.role)return;", "if((b.dataset.m==='bb'||b.dataset.m==='sb')&&NET.role)return;")
open(p, 'w', encoding='utf-8', newline='').write(s)

# battle.js hands over to sandbox.js when SBX is set
p = 'D:/crust-rush/source/tools/mini/battle.js'
s = open(p, encoding='utf-8', newline='').read()
rep("function battleG(x,z){if(x<BB_X0)return BB_FLOOR;", "function battleG(x,z,wy){if(SBX)return sbG(x,z,wy);if(x<BB_X0)return BB_FLOOR;")
rep("function battleWalls(k){const wy=k.wy||0;", "function battleWalls(k){if(SBX)return sbWalls(k);const wy=k.wy||0;")
rep("function battleStart(){BB.t=BB.T;", "function battleStart(){if(SBX)return sbStart();BB.t=BB.T;")
rep("function battleHit(v,by){if(!BATTLE||BB.over||!(v.bal>0))return;", "function battleHit(v,by){if(SBX||!BATTLE||BB.over||!(v.bal>0))return;")
rep("function battleTick(dt){if(state!=='race'||BB.over)return;", "function battleTick(dt){if(SBX)return sbTick(dt);if(state!=='race'||BB.over)return;")
rep("function battleRender(time){if(!BATTLE||!BB.grp)return;", "function battleRender(time){if(SBX)return sbRender(time);if(!BATTLE||!BB.grp)return;")
rep("function bbHud(make){let e=BB.el;", "function bbHud(make){if(SBX)return sbHud();let e=BB.el;")
rep("function bbRoll(){const L=", "function bbRoll(){if(SBX)return sbRoll();const L=")
rep("function bbNoNet(){if(mode!=='bb')return;", "function bbNoNet(){if(mode!=='bb'&&mode!=='sb')return;")
rep("function battleLoad(){", "function battleLoad(){if(SBX)sbOff();/* a different world is coming in */")
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'D:/crust-rush/source/tools/mini/inject_mini.py'
s = open(p, encoding='utf-8', newline='').read()
a = "open('D:/crust-rush/source/tools/mini/battle.js',encoding='utf-8',newline='').read()"
assert s.count(a) == 1
s = s.replace(a, a + "+'\\n'+open('D:/crust-rush/source/tools/mini/sandbox.js',encoding='utf-8',newline='').read()")
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'D:/crust-rush/source/tools/mini/sandbox.js'
s = open(p, encoding='utf-8', newline='').read()
rep("const j=Math.round(R.air[0]*N)%N,p=track[j],sd=p.bend>0?-1:1,o=",
    "const j=Math.round(R.air[0]*N)%N,p=track[j],q=track[(j+14)%N],sd=((q.x-p.x)*p.nx+(q.y-p.y)*p.ny)>0?-1:1/* the outside of the bend */,o=")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
