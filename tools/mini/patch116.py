"""Patch 116 (web v250): split screen, part B: player 2 in the race (as the PC, tools/mini/pc120.py).
- goRace: SPLIT.on when 2 players are chosen, off line, in Grand Prix / Single race / Balloon Battle, and player 2's controller is
  plugged in (Start with none goes to player 2's screen, which says so). body.split.
- resetRace: player 2 in slot 3 (beside player 1) with their driver and kart, one computer racer fewer; player2 (k.p2).
- Player 2's controller (pad2Poll, PAD2): their kart only, never player 1's; Start pauses. Player 1's controller is any other
  one while racing (either may work the pause menu and results).
- p2Input: player 2's steering, items (the same press/hold as player 1's), ability (Y).
- Finishing: player 2's finish is theirs (no records, no coins); the results wait for both. No cinematic finish; a split race does
  not count for records (RTAINT).
- Balloon Battle: a player who is out watches the other player (or whoever is left) in their half.
Run once, after patch 115: py.cmd tools/mini/patch116.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function pad2Poll' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("let karts=[],player=null,", "let karts=[],player=null,player2=null/* (patch 116: split screen's player 2) */,")
# seating
rep("const others=RACERS.map((_,i)=>i).filter(i=>demo||i!==selected);",
    "const two=!demo&&SPLIT.on&&!NET.cfg&&!SBX,others=RACERS.map((_,i)=>i).filter(i=>demo||i!==selected&&!(two&&i===SPLIT.sel));")
rep("const nc=cpuCount(demo),near=[3,5,2,6,1,7,0].slice(0,nc).concat(demo?[4]:[]);for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));",
    "const nc=Math.max(0,cpuCount(demo)-(two?1:0)),near=(two?[5,2,6,1,7,0]:[3,5,2,6,1,7,0]).slice(0,nc).concat(demo?[4]:[]);for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));\n"
    "    else if(two&&s===3){/* (patch 116) player 2, beside player 1 */const k2=makeKart(SPLIT.sel,s,true,diff,SPLIT.build&&validBuild(SPLIT.build)?SPLIT.build:playerBuild);k2.p2=1;karts.push(k2);}")
rep("{const me=demo?null:(karts.find(k=>k.isPlayer)||karts[4]);player=me;camT=me||karts[4];}",
    "{const me=demo?null:(karts.find(k=>k.isPlayer&&!k.p2)||karts[4]);player=me;camT=me||karts[4];player2=demo?null:(karts.find(k=>k.p2)||null);SPLIT.camT2=player2;}")
rep("cam.a=camT.ma;camSnap=true;acc=0;", "cam.a=camT.ma;camSnap=true;SPLIT.snap=true;acc=0;")
# input
rep(":(k.isPlayer&&!k.auto&&!(k.rush>0&&!(k.megaT>0)&&!(k.pestoT>0)))?playerInput():",
    ":(k===player2&&!k.auto&&!(k.rush>0&&!(k.megaT>0)&&!(k.pestoT>0)))?p2Input(k):(k.isPlayer&&k!==player2&&!k.auto&&!(k.rush>0&&!(k.megaT>0)&&!(k.pestoT>0)))?playerInput():")
rep("if(abilQueued){abilQueued=false;if(player&&state==='race')useAbility(player,lookingBack());}",
    "if(abilQueued){abilQueued=false;if(player&&state==='race')useAbility(player,lookingBack());}if(PAD2.ab){PAD2.ab=false;if(player2&&state==='race')useAbility(player2,PAD2.look||PAD2.back);}")
rep("function playerInput(){",
    "/* (patch 116) split screen: player 2's controller. It drives their kart only; Start pauses */\n"
    "const PAD2={steer:0,gas:false,brake:false,nb:false,look:false,back:false,prev:[],held:[false,false,false],hold:[0,0,0],q:null,ab:false};\n"
    "function pad2Poll(gp){const M=padMap(gp),P=PAD2.prev,pr=i=>i!=null&&i>=0&&padBtn(gp,i),edge=i=>pr(i)&&!P[i];\n"
    "  const ax=gp.axes[0]||0,ay=gp.axes[1]||0,dz=.2,sx=Math.abs(ax)<dz?0:Math.sign(ax)*(Math.abs(ax)-dz)/(1-dz);\n"
    "  if((state==='race'||state==='countdown')&&pauseOv.hidden&&results.hidden){\n"
    "    PAD2.steer=clamp(sx+(pr(M.RIGHT)?1:0)-(pr(M.LEFT)?1:0),-1,1);PAD2.gas=M.GAS.some(pr);PAD2.brake=M.D.some(pr);PAD2.nb=PAD2.gas&&PAD2.brake;PAD2.look=pr(M.X)||pr(M.BACK);PAD2.back=ay>.55;\n"
    "    if(edge(M.Y))PAD2.ab=true;\n"
    "    [[M.I1,1],[M.I2,2]].forEach(([btns,sl])=>{const down=btns.some(pr),was=PAD2.held[sl];if(down===was)return;PAD2.held[sl]=down;const k=player2;if(!k)return;\n"
    "      const it=sl===1?k.item:k.item2,suf=sl===2?'2':'';\n"
    "      if(down){if(k.held&&k.held.sl===sl){PAD2.q='fwd'+suf;PAD2.hold[sl]=0;}else if(it&&HOLDABLE[it]&&mode!=='bb'){PAD2.q='hold'+suf;PAD2.hold[sl]=1;}else{PAD2.q='fwd'+suf;PAD2.hold[sl]=0;}}\n"
    "      else if(PAD2.hold[sl]){PAD2.hold[sl]=0;if(k.held&&k.held.sl===sl)PAD2.q=(ay>.6?'hold':'fwd')+suf;}});\n"
    "    if(edge(M.START))togglePause();}\n"
    "  else{PAD2.steer=0;PAD2.brake=false;PAD2.nb=false;PAD2.look=false;PAD2.back=false;PAD2.held=[false,false,false];}\n"
    "  PAD2.prev=gp.buttons.map(b=>!!b&&(b.pressed||b.value>.5));}\n"
    "function p2Input(k){const it=PAD2.q;PAD2.q=null;const o={steer:PAD2.steer,brake:PAD2.brake,nb:!!PAD2.nb,mul:PAD2.gas?1:0,use:false,back:false,hold:false,holdSl:1,release:null};\n"
    "  if(it)itemIntent(k,it,o);if(o.use&&k.item&&(PAD2.look||PAD2.back)&&!NOBACK.includes(k.item))o.back=true;return o;}\n"
    "function playerInput(){")
rep("for(const g of gps||[])if(g&&g.connected&&(!gp||g.timestamp>gp.timestamp))gp=g;\n  if(!gp){if(PAD.act)",
    "/* (patch 116) split screen: player 2's controller is theirs while racing; either works the menus */\n"
    "  const p2g=SPLIT.on&&player2?p2Pad():null,p2x=p2g&&(state==='race'||state==='countdown')&&pauseOv.hidden&&results.hidden?p2g.index:-1;if(p2g)pad2Poll(p2g);\n"
    "  for(const g of gps||[])if(g&&g.connected&&g.index!==p2x&&(!gp||g.timestamp>gp.timestamp))gp=g;\n"
    "  if(gp&&gp.index!==PAD.pi){if(PAD.pi!=null&&SPLIT.on)PAD.prev=gp.buttons.map(b=>!!b&&(b.pressed||b.value>.5));PAD.pi=gp.index;}/* (a press already down on the other controller is not a new one) */\n"
    "  if(!gp){if(PAD.act)")
# finishing
rep("if(k===player)onPlayerFinish();}}", "if(k===player)onPlayerFinish();else if(k===player2)onP2Finish();}}")
rep("try{finishPunch();}catch(e){}resultsAt=2.4;}",
    "try{if(!SPLIT.on)finishPunch();/* (patch 116: no cinematic finish in split screen) */}catch(e){}resultsAt=2.4;}\n"
    "function onP2Finish(){player2.auto=true;try{showBanner2('Finish!',2.4,'md');}catch(e){}SFX.finish();}")
rep("if(resultsAt>0&&!FIN.on){resultsAt-=dt;", "if(resultsAt>0&&!FIN.on&&!(SPLIT.on&&player2&&!player2.finished)){resultsAt-=dt;/* (patch 116: the results wait for both players) */")
rep("(TD.on||devAlt()))RTAINT=true;", "(TD.on||devAlt()||SPLIT.on))RTAINT=true;")
# in and out of split screen
rep("function toMenu(){if(sbBack())return;", "function toMenu(){if(sbBack())return;SPLIT.on=false;player2=null;document.body.classList.remove('split');/* (patch 116) */")
rep("function startFromMenu(){cpuBuilds=", "function startFromMenu(){if(splitWant()&&!p2Pad()){goStep('driver2');return;}/* (patch 116: player 2 needs their controller) */cpuBuilds=")
rep("NET.fromNet=false;if(!NET.role||!NET.conns.some(c=>c.open))NET.cfg=null;raceLoading=true;",
    "NET.fromNet=false;if(!NET.role||!NET.conns.some(c=>c.open))NET.cfg=null;SPLIT.on=splitWant()&&!NET.cfg&&!!p2Pad();document.body.classList.toggle('split',SPLIT.on);/* (patch 116) */raceLoading=true;")
# Balloon Battle: out
rep("stay=k===player&&!BB.skip;", "stay=(k===player||SPLIT.on&&k===player2)&&!BB.skip;")
rep("if(stay)setTimeout(()=>{if(!(BATTLE&&!SBX&&player===k&&k.bbDead))return;",
    "if(stay)setTimeout(()=>{if(SPLIT.on&&BATTLE&&!SBX&&k.bbDead&&(k===player||k===player2)){bbAway(k);splitWatch(k);return;}/* (patch 116) */if(!(BATTLE&&!SBX&&player===k&&k.bbDead))return;")
rep("function bbElim(k){",
    "/* (patch 116) split screen: a player who is out watches the other player, or whoever is left */\n"
    "function splitWatch(k){const t=[player,player2].find(q=>q&&q!==k&&!q.bbDead)||karts.find(q=>!q.bbDead)||k;if(k===player){camT=t;camSnap=true;}else{SPLIT.camT2=t;SPLIT.snap=true;}}\n"
    "function bbElim(k){")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 116 applied')
