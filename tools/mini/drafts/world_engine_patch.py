"""Patch 25 (web v192): Sandbox on every track of the game (tools/mini/sandbox.js; docs/SANDBOX-PLAN.md "The rest of the maps").
Sandbox now has three kinds of region:
  toy    the four places of the house: drive anywhere, ground and walls from sandbox.js (as before)
  open   the fifteen pizza tracks: drive anywhere on the pizza; the ground is the engine's own, the walls are read from what is drawn
  road   Sauce Spiral and the four Neon tracks: the road hangs in the air or winds up a tower, so you keep to it, both ways, with the race's own walls
SBX is on in all three; SBF ("free") is on in the first two, and is what the driving hooks of patch 22 to 24 now ask.
Run once: py.cmd tools/mini/patch25.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'SBF' not in s.split('/* ================= SANDBOX')[0], 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


# ---- the free-driving hooks ask SBF
rep("if(!SBX&&pj.flo!==undefined", "if(!SBF&&pj.flo!==undefined")
rep("else if(SBX&&k.wy-G>SB_STEP)", "else if(SBF&&k.wy-G>SB_STEP)")
rep("if(SBX)best=sbIdx(k,k.idx);", "if(SBF)best=sbIdx(k,k.idx);")
rep("&&!SBX;k.airT=0;k.wvy=Math.min(k.gRate,SBX?22:42);", "&&!(SBF&&SB.kind==='toy');k.airT=0;k.wvy=Math.min(k.gRate,SBF&&SB.kind==='toy'?22:42);")
rep("{let rg=SBX?sbG(x,y,z):", "{let rg=SBF?sbG(x,y,z):")
rep("SBX?sbG(", "SBF?sbG(", 5)
rep("&&!(SBX&&camT.sbOff)", "&&!(SBF&&camT.sbOff)")
rep("if(d>RIM&&!SBX)", "if(d>RIM&&!SBF)")
rep("function scStep(k){if(SBX||!SHORTS.length)return;", "function scStep(k){if(SBF||!SHORTS.length)return;")
# ---- what any Sandbox drive needs, free or not: no finish, no lap banner, no wrong-way warning, its own tick and start, its own item
rep("&&!k.finished&&!BATTLE&&k.prog>=LAPS*N", "&&!k.finished&&!BATTLE&&!SBX&&k.prog>=LAPS*N")
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
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
