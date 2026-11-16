"""Patch 45 (web v208, ONLINE VERSION 115): Balloon Battle on line (web first; the PC follows).
The owner, 2026-11-16: "lets add sandbox and balloon battle online to the web version before porting to pc". This is the battle half.
The host runs the battle as it runs a race (its rules, the clock, the CPU drivers, item boxes, hits); friends drive their own karts at once
and send their controls, as in a race. What is new:
- a room may choose Balloon Battle (the mode button and netHost/netJoin no longer drop it; Sandbox still is, until its own patch);
- every kart's battle state goes in the snapshot (NET_REM: bal, bbL, bbS, bbOut, bbDead, bbPlace) and the round's clock and end (bb);
  hence ONLINE VERSION 115;
- a friend's screen: the read-out follows the host's clock; pops, points, "Back with N", "Last balloon!", eliminations show as they do for the
  host's own player; out of the round, the friend watches the others (the engine's spectating) until the round ends, then the results;
  while waiting to come back with a new set the friend's kart is slowed as the host slows it (no rubber band);
- the results on line are in battle order (points, then sets, then balloons; the eliminated by when they went out), each row its points.
Run once: py.cmd tools/mini/patch45.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 45' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const NET_PROTO=114;", "const NET_PROTO=115;")
# the battle fields of every kart travel with the others (the receiver rebuilds the full row; resting values are 0 / false)
rep("'megaT','pestoT','flatT','chiliT','oilT','burnT','est','oliveT'];",
    "'megaT','pestoT','flatT','chiliT','oilT','burnT','est','oliveT','bal','bbL','bbS','bbOut','bbDead','bbPlace'];/* (patch 45: Balloon Battle on line) */")
rep("const NET_ZB=new Set(['air','glide','onRamp','finished','big','trick','est'])",
    "const NET_ZB=new Set(['air','glide','onRamp','finished','big','trick','est','bbDead'])")
# the round's clock and end in every snapshot of a battle
rep("b:boxes.map(b=>b.r>0?Math.round(b.r*20):0),fx:NET.fxQ.splice(0)};",
    "b:boxes.map(b=>b.r>0?Math.round(b.r*20):0),fx:NET.fxQ.splice(0)};if(BATTLE&&!SBX)base.bb=[r3(BB.t),BB.over?1:0];")
# a room keeps Balloon Battle (Sandbox still leaves)
rep("async function netHost(){bbNoNet();", "async function netHost(){sbNoNet();")
rep("  bbNoNet();netReset();NET.role='guest';", "  sbNoNet();netReset();NET.role='guest';")
rep("function bbNoNet(){if(mode!=='bb'&&mode!=='sb')return;",
    "/* (patch 45) a room keeps Balloon Battle; Sandbox is still off line */function sbNoNet(){if(mode==='sb')bbNoNet();}\nfunction bbNoNet(){if(mode!=='bb'&&mode!=='sb')return;")
rep("if((b.dataset.m==='bb'||b.dataset.m==='sb')&&NET.role)return;/* Balloon Battle is off line only for now */",
    "if(b.dataset.m==='sb'&&NET.role)return;/* Sandbox is off line only for now (Balloon Battle is on line since patch 45) */")
# a friend's screen: the battle as the host plays it
rep("  if(d.me&&player&&!player.finished)netReconcile(d.me,d.ack);else if(d.me&&player)netApplyFull(player,d.me);\n  if(player&&player.finished&&!NET.finSeen){NET.finSeen=true;onPlayerFinish();}}",
    "  if(d.me&&player&&!player.finished)netReconcile(d.me,d.ack);else if(d.me&&player)netApplyFull(player,d.me);\n"
    "  if(BATTLE&&!SBX&&d.bb)netBattle(d);\n"
    "  /* (a battle: out of the round is not the end of it; the results come when the round ends) */\n"
    "  if(player&&player.finished&&!NET.finSeen&&!(BATTLE&&!SBX&&!BB.over)){NET.finSeen=true;onPlayerFinish();}}\n"
    "/* (patch 45) Balloon Battle on a friend's screen: what the host's rules did since the last snapshot, shown as the host shows it for its own player */\n"
    "function netBattle(d){const was=BB.over;BB.t=d.bb[0];BB.over=!!d.bb[1];\n"
    "  for(const k of karts){const pb=k.nbB,pl=k.nbL,ps=k.nbS,pd=k.nbD,me=k===player;k.nbB=k.bal;k.nbL=k.bbL;k.nbS=k.bbS;k.nbD=!!k.bbDead;if(pb==null)continue;\n"
    "    if(k.bbDead&&!pd){/* out */if(k.m&&k.m.g)k.m.g.visible=false;if(me||near(k)>0)SFX.elim&&SFX.elim();showBanner(me?'Out! '+BB_DOT+' '+ord(k.bbPlace||1):k.r.name+' is out',me?2.2:1.3,'sm');\n"
    "      if(me)setTimeout(()=>{if(BATTLE&&!SBX&&player===k&&k.bbDead&&state==='race'&&!BB.over&&!SPEC.on)bbWatch();},1600);continue;}\n"
    "    if((k.bal||0)<(pb||0)&&!k.bbDead&&near(k)>0&&SFX.bump)SFX.bump(near(k)*.8);\n"
    "    if(me&&(k.bbS||0)>(ps||0)){SFX.ring&&SFX.ring();showBanner('+1',.5,'sm');}\n"
    "    if(me&&(k.bbL||0)>(pl||0)&&!k.bbDead)showBanner('All popped! Back with '+BB_SETS[k.bbL],1.6,'sm');\n"
    "    if(me&&k.bal===1&&pb===0&&!k.bbDead)showBanner('Last balloon!',1.5,'sm');}\n"
    "  if(BB.over&&!was){const r=bbRank();showBanner(r[0]===player?'Last one standing!':(r[0].netName||r[0].r.name)+' wins!',2.4,'md');}\n"
    "  bbHud();}")
# a friend waiting to come back with a new set is slowed as the host slows it
rep("stepKart(k,inp,dt);netGuestClaims(k,NET.hist[NET.hist.length-1]);}",
    "stepKart(k,inp,dt);if(BATTLE&&!SBX&&k.bbOut>0)k.speed*=Math.pow(.02,dt);/* (patch 45: as battleTick does on the host) */netGuestClaims(k,NET.hist[NET.hist.length-1]);}")
# the results on line: battle order and points
rep("function renderResultsNet(){const rows=netResultRows(),cl=CLASSES[clsKey].label,me=rows.findIndex(r=>r.k===player)+1;",
    "function renderResultsNet(){const bat=BATTLE&&!SBX,rows=bat?bbRank().map(k=>({k,human:!!k.netName,racing:false,est:false,t:0})):netResultRows(),cl=CLASSES[clsKey].label,me=rows.findIndex(r=>r.k===player)+1;")
rep("tm=r.racing?'<em class=\"racing\">racing…</em>':(r.est?'~':'')+fmt(r.t);",
    "tm=bat?bbResRow(k):r.racing?'<em class=\"racing\">racing…</em>':(r.est?'~':'')+fmt(r.t);")
rep("resSub.textContent=MAPS[mapIdx].name+' · '+cl+' class'+(live?' · waiting for friends to finish':'');",
    "resSub.textContent=bat?MAPS[mapIdx].name+' · Balloon Battle':MAPS[mapIdx].name+' · '+cl+' class'+(live?' · waiting for friends to finish':'');")
rep("function onPlayerFinish(){if(mode!=='lss')saveRun();try{achFinish();}catch(e){}player.auto=true;showBanner('Finish!',2.4,'md');SFX.finish();",
    "function onPlayerFinish(){if(BATTLE&&!SBX){/* (patch 45) a battle on a friend's screen: no race time to log, the end of the round has its own banner */player.auto=true;resultsAt=2.4;return;}if(mode!=='lss')saveRun();try{achFinish();}catch(e){}player.auto=true;showBanner('Finish!',2.4,'md');SFX.finish();")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 45 applied')
