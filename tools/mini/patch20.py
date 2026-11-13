"""Patch 20: the items in a Balloon Battle (tools/mini/battle.js). In a race thrown things ride the track (progress along
it and offset across it); an arena has no track, so behind BATTLE they fly free, turn back off the arena's walls, home
straight at a rival, and keep to the level they are on. Nothing changes in a race.
Run once, after patch19.py: py.cmd tools/mini/patch20.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'bbProjWalls(p)' not in s, 'already patched'
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
# who a homing dough ball goes for; how it flies
rep("const tg=back?(st[i+1]||null):(i>0?st[i-1]:null),", "const tg=BATTLE?bbTarget(k,back):back?(st[i+1]||null):(i>0?st[i-1]:null),")
rep("if(p.type==='dough'&&p.target&&!p.target.finished){const tg=p.target;homeStep(", "if(p.type==='dough'&&p.target&&!p.target.finished){const tg=p.target;if(BATTLE)bbHome(p,tg,dt,Math.max(300,Math.abs(tg.speed||0)*1.22+70),5.5);else homeStep(")
# straight fliers meet the arena's walls
rep("else if(p.type!=='wheel'){p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.storm)pepWall(p);}", "else if(p.type!=='wheel'){p.x+=p.vx*dt;p.y+=p.vy*dt;if(BATTLE)bbProjWalls(p);else if(p.storm)pepWall(p);}")
# the pizza cutter goes for whoever is winning, straight there
rep("target:st[0]===k?null:st[0],prog:k.prog+2", "target:BATTLE?bbLeader(k):st[0]===k?null:st[0],prog:k.prog+2")
rep("else if(tg&&!tg.loop&&tg.prog-p.prog>4){", "else if(!BATTLE&&tg&&!tg.loop&&tg.prog-p.prog>4){")
# the freezer: everybody near, not everybody ahead
rep("const sf=standings(),fi=sf.indexOf(k);for(let j=0;j<fi;j++){const o=sf[j];if(o===k||o.finished)continue;", "const sf=BATTLE?karts.filter(o=>o!==k&&!(o.bbOut>0)&&Math.hypot(o.x-k.x,o.y-k.y)<280):standings(),fi=BATTLE?sf.length:sf.indexOf(k);for(let j=0;j<fi;j++){const o=sf[j];if(o===k||o.finished)continue;")
# a lobbed bottle that comes down off the table is gone
rep("if(p.type==='lob'){if(p.t<=0&&overPit(p.x,p.y)){", "if(p.type==='lob'){if(p.t<=0&&(overPit(p.x,p.y)||(BATTLE&&battleG(p.x,p.y)<-100))){")
# levels: a thrown thing or a trap only meets karts on its own level
rep("const sameLvl=(k,p)=>!MULTI||Math.abs((k.wy||0)-pGround(p))<18;", "const sameLvl=(k,p)=>BATTLE?Math.abs((k.wy||0)-(p.bh!=null?p.bh:battleG(p.x,p.y)))<16:!MULTI||Math.abs((k.wy||0)-pGround(p))<18;")
rep("function pGround(p){if(!MULTI)return groundAt(p.x,p.y);", "function pGround(p){if(BATTLE)return p.bh!=null?p.bh:Math.max(0,battleG(p.x,p.y));if(!MULTI)return groundAt(p.x,p.y);")
rep("function hazEy(h){if(!MULTI)return 0;", "function hazEy(h){if(BATTLE)return Math.max(0,battleG(h.x,h.y));if(!MULTI)return 0;")
# an item box gives what a mid-field racer would get; no drivers' specials in a battle (they are built round the lap)
rep("k.pend.push(rollItem(standCache.indexOf(k)))", "k.pend.push(rollItem(BATTLE?3:standCache.indexOf(k)))")
rep("function useAbility(k,back){", "function useAbility(k,back){if(BATTLE)return;")
# (added with web v183) a battle's boxes give only things that work with no track; no corner arrow boards on the table
rep('function rollItem(pos){', 'function rollItem(pos){if(BATTLE)return bbRoll();')
rep('function neonSigns(def){', 'function neonSigns(def){if(def.battle)return;')
rep('(function(){const fR=new THREE.MeshStandardMaterial({map:T2(chevTex(1)),roughness:.45}),', '(function(){if(def.battle)return;/* no bend boards on a battle arena: its ring of track points is bookkeeping, not a road */const fR=new THREE.MeshStandardMaterial({map:T2(chevTex(1)),roughness:.45}),')   # (web v184: these were the boards; neonSigns was not)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
