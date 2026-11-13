"""Patch 19: the engine's hooks for Balloon Battle (tools/mini/battle.js; docs/BALLOON-BATTLE-PLAN.md).
Every hook is behind BATTLE (or mode 'bb'), so a normal race runs exactly the code it ran before.
Run once: py.cmd tools/mini/patch19.py   (then inject_mini.py, which carries battle.js in)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'battleWalls(k)' not in s, 'already patched'
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
# stepKart: no off-road slowing; arena walls in place of the track's; the arena's ground; no kerb
rep("if(k.boost>0)tp=Math.max(tp,.93);", "if(k.boost>0)tp=Math.max(tp,.93);if(BATTLE)tp=1;")
rep("  {const pj=track[k.idx],lt=(k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny,sg=lt<0?-1:1,lim=", "  if(BATTLE)battleWalls(k);else{const pj=track[k.idx],lt=(k.x-pj.x)*pj.nx+(k.y-pj.y)*pj.ny,sg=lt<0?-1:1,lim=")
rep("let G=kGround(k),onR=false,gR=false;", "let G=BATTLE?battleG(k.x,k.y):kGround(k),onR=false,gR=false;")
rep("if(!k.sc&&!(GLIDE&&k.idx>=GLIDE.j0&&k.idx<GLIDE.j1)){const la=Math.abs(lateral(k));if(la>RW&&la<CURB)G+=kerbH(la);}", "if(!BATTLE&&!k.sc&&!(GLIDE&&k.idx>=GLIDE.j0&&k.idx<GLIDE.j1)){const la=Math.abs(lateral(k));if(la>RW&&la<CURB)G+=kerbH(la);}")
# the CPU drivers, the hit, the clock
rep("function aiInput(k,dt){", "function aiInput(k,dt){if(BATTLE)return battleAI(k,dt);")
rep("k.inv=k.spin+3;if(CURP&&CURP.owner&&k!==CURP.owner)hitNote(", "k.inv=k.spin+3;if(BATTLE)battleHit(k,CURP&&CURP.owner);if(CURP&&CURP.owner&&k!==CURP.owner)hitNote(")
rep("CURP=null;if(mode==='lss'){", "CURP=null;if(BATTLE)battleTick(dt);if(mode==='lss'){")
rep("RW=def.rw||63;LS=RW/63;", "BATTLE=!!def.battle;battleLoad();RW=def.rw||63;LS=RW/63;")
rep("k.m.g.visible=true;}resetRace(false);", "k.m.g.visible=true;}resetRace(false);if(BATTLE)battleStart();")
rep("itemsRender(time,dt);", "itemsRender(time,dt);battleRender(time);")
rep("player.wrongT=back?player.wrongT+dt:0;", "player.wrongT=back&&!BATTLE?player.wrongT+dt:0;")
# the menu: a fourth mode with its one arena; the arena is in no cup and no track list.
# (The button was hidden, and the row three wide, until the mode was ready: web v182.)
rep('<div class="seg seg3" id="modeSeg"><button data-m="gp">Grand Prix</button><button data-m="single">Single race</button><button data-m="lss">Last Slice</button></div>',
    '<div class="seg seg4" id="modeSeg"><button data-m="gp">Grand Prix</button><button data-m="single">Single race</button><button data-m="lss">Last Slice</button><button data-m="bb">Balloon Battle</button></div>')
rep("mode=b.dataset.m;store.set('crust-mode',mode);if(mode==='gp'){", "mode=b.dataset.m;store.set('crust-mode',mode);{const bi=MAPS.findIndex(m=>m.battle),want=mode==='bb'?bi:mapIdx===bi?0:mapIdx;if(want!==mapIdx&&mode!=='gp'){mapIdx=want;loadMap(want,false);resetRace(true);}}if(mode==='gp'){")
rep("const mapCatOf=m=>m.special?'sp':String(m.cup);", "const mapCatOf=m=>m.battle?'bb':m.special?'sp':String(m.cup);")
rep("MAPS.some(m=>m.special)?[['sp'", "MAPS.some(m=>m.special&&!m.battle)?[['sp'")
rep("$('cups').hidden=mode!=='gp';$('maps').hidden=mode==='gp';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp';$('trackLabel').textContent=mode==='gp'?'Cup':'Track';",
    "$('cups').hidden=mode!=='gp';$('maps').hidden=mode==='gp'||mode==='bb';if($('mapsWrap'))$('mapsWrap').hidden=mode==='gp'||mode==='bb';$('trackLabel').textContent=mode==='gp'?'Cup':mode==='bb'?'Arena: Prep Table Showdown':'Track';")
rep("{const mn=$('modeNote');if(mn){mn.hidden=mode!=='lss';mn.textContent='Last Slice Standing:", "{const mn=$('modeNote');if(mn&&mode==='bb'){mn.hidden=false;mn.textContent='Balloon Battle: three minutes on the prep table. Everybody starts with five balloons. Pop a rival\\'s balloon with an item for a point; lose all of yours and you come back with three and half your points. Most points wins.';}else if(mn){mn.hidden=mode!=='lss';mn.textContent='Last Slice Standing:")
rep("$('startBtn').textContent=mode==='gp'?'Start Grand Prix':", "$('startBtn').textContent=mode==='bb'?'Start battle':mode==='gp'?'Start Grand Prix':")
rep("resList.innerHTML=st.map((k,i)=>row(k,i,mode==='lss'?", "resList.innerHTML=st.map((k,i)=>row(k,i,BATTLE?(k.bbS||0)+((k.bbS||0)===1?' point':' points'):mode==='lss'?")
rep("cupIdx=(+(store.get('crust-cup')||0)||0)%CUPS.length,gp=null,raceDone=false;", "cupIdx=(+(store.get('crust-cup')||0)||0)%CUPS.length,gp=null,raceDone=false;{const bi=MAPS.findIndex(m=>m.battle);if(mode==='bb')mapIdx=bi<0?0:bi;else if(MAPS[mapIdx].battle)mapIdx=0;}/* the battle arena is only ever loaded in its own mode */")
# (added later the same day) no battle in a friends' race: the mode's button does nothing while on line, and hosting or joining leaves the mode
rep("document.querySelectorAll('#modeSeg button').forEach(b=>b.onclick=()=>{mode=b.dataset.m;", "document.querySelectorAll('#modeSeg button').forEach(b=>b.onclick=()=>{if(b.dataset.m==='bb'&&NET.role)return;/* Balloon Battle is off line only for now */mode=b.dataset.m;")
rep("async function netHost(){rtcIce();netReset();NET.role='host';", "async function netHost(){bbNoNet();rtcIce();netReset();NET.role='host';")
rep("  netReset();NET.role='guest';const R=new NetRelay();", "  bbNoNet();netReset();NET.role='guest';const R=new NetRelay();")
rep("if(state==='race'&&!player.finished&&lap>lapShown){lapShown=lap;", "if(state==='race'&&!BATTLE&&!player.finished&&lap>lapShown){lapShown=lap;")   # no lap banners: circling the middle of the arena is not a lap
rep("mode==='lss'?'Last Slice Standing':'Single race')+' · '+CLASSES[clsKey].label;", "mode==='bb'?'Balloon Battle':mode==='lss'?'Last Slice Standing':'Single race')+' · '+CLASSES[clsKey].label;")   # the loading screen names the mode
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
