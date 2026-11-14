"""Patch 28 (web v193): a Grand Prix played on line.
The owner, 2026-11-14: "grand prix wasnt working online after one race it was saying race again or change driver but no to the next race option".
What was wrong (read in the source, then seen with tools/neon/gpnet2.py):
  1. The online results screen (renderResultsNet) never looked at the cup: it hid the cup standings and always wrote "Race again" and
     "Change track or driver". (The host's button did go on to the next race, but nothing said so.)
  2. The cup's points were added once, when the HOST finished (finalizeRace): a friend who crossed the line after the host got nothing for
     that race, and the computer racers' places were the estimates of that moment.
Now:
  - on line the cup's points for a race are worked out from the results table itself (netGpNow: everyone by finishing time, as the table
    shows them), shown in the cup standings on every player's screen while the table is up, and only added to the cup when the host goes
    on to the next race (so a friend who finishes late is counted);
  - the host's button says "Next race" (after the fourth race "Play this cup again"), a friend sees the standings and the line
    "Waiting for the host to start the next race";
  - pressing it twice (the lobby in between) does not skip a race or add the points twice (gp.pend).
Nothing in the race messages changes: the cup (cfg.gp) was already sent with every race. No online version change.
Run once: py.cmd tools/mini/patch28.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function netGpNow' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    if s.count(a) == 0 and '\n' in a: a = a.replace('\n', '\r\n'); b = b.replace('\n', '\r\n')
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


rep("  if(gp){gp.last.fill(0);for(const k of karts){const pt=PTS[k.place-1]||0;gp.pts[k.ri]+=pt;gp.last[k.ri]=pt;}}}",
    "  if(gp&&!NET.cfg){/* (on line the cup is scored from the results table, when the host goes on: netGpNow) */gp.last.fill(0);for(const k of karts){const pt=PTS[k.place-1]||0;gp.pts[k.ri]+=pt;gp.last[k.ri]=pt;}}}")
rep("let resLive=0;\nfunction renderResultsNet(){",
    "/* a Grand Prix on line: this race's points by the table as it stands, and the cup with them added (gp.pts itself is only moved on when the host starts the next race) */\n"
    "/* (the cup keeps a computer racer's points under the racer, as off line; a player's under the player (gp.np, by the room's own number for them): two friends may both drive the same racer) */\n"
    "function netGpNow(){const rows=netResultRows(),pts=gp.pts.slice(),np=Object.assign({},gp.np||{}),tot=new Map(),last=new Map();rows.forEach((r,i)=>{const k=r.k,c=NET.cfg&&NET.cfg.karts[karts.indexOf(k)],pt=PTS[i]||0;last.set(k,pt);if(c&&c.who>=0){np[c.who]=(np[c.who]||0)+pt;tot.set(k,np[c.who]);}else{pts[k.ri]+=pt;tot.set(k,pts[k.ri]);}});return {pts,np,last,tot};}\n"
    "let resLive=0;\nfunction renderResultsNet(){")
rep("  $('gpBox').hidden=true;$('trophy').hidden=true;resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' \u00b7 '+cl+' class'+(rows.some(r=>r.racing)?' \u00b7 waiting for friends to finish':'');\n  $('againBtn').textContent='Race again';$('toMenuBtn').textContent='Change track or driver';",
    "  const gb=$('gpBox'),tr=$('trophy'),live=rows.some(r=>r.racing);tr.hidden=true;resTitle.textContent=me===1?'1st place!':me+suf(me)+' place';resSub.textContent=MAPS[mapIdx].name+' \u00b7 '+cl+' class'+(live?' \u00b7 waiting for friends to finish':'');\n"
    "  if(gp){/* the cup: its standings with this race counted, and the way on */const G=netGpNow(),fin=gp.race>=3,order=karts.slice().sort((a,b)=>G.tot.get(b)-G.tot.get(a));gb.hidden=false;$('gpLabel').textContent=CUPS[gp.cup].name+' \u00b7 race '+(gp.race+1)+' of 4'+(live?' \u00b7 so far':'');\n"
    "    $('gpList').innerHTML=order.map((k,i)=>'<li class=\"'+(k===player?'me':'')+'\"><span class=\"pl\">'+(i+1)+'</span><span class=\"sw\" style=\"background:'+k.r.color+'\"></span><span>'+String(k.netName||k.r.name).replace(/[<>&]/g,'')+(k===player?' (you)':'')+'</span><span class=\"tm\"><span class=\"add\">+'+G.last.get(k)+'</span>'+G.tot.get(k)+' pts</span></li>').join('');\n"
    "    if(fin&&!live){const cp=order.indexOf(player)+1;resTitle.textContent=cp===1?'You won the '+CUPS[gp.cup].name+'!':cp+suf(cp)+' in the '+CUPS[gp.cup].name;if(cp<=3){tr.innerHTML=TROPHY(['#ffd54a','#d8dde3','#e09a5a'][cp-1]);tr.hidden=false;}resSub.textContent='Final standings \u00b7 '+cl+' class';}\n"
    "    $('againBtn').textContent=fin?'Play this cup again':'Next race';$('toMenuBtn').textContent='Quit to menu';}\n"
    "  else{gb.hidden=true;$('againBtn').textContent='Race again';$('toMenuBtn').textContent='Change track or driver';}")
rep("$('againBtn').onclick=()=>{if(gp){if(gp.race>=3)startGP();else{gp.race++;goRace(CUP_TRACKS[gp.cup][gp.race]);}}else goRace(mapIdx);};",
    "$('againBtn').onclick=()=>{if(gp&&NET.cfg&&NET.role==='host'){/* on line: the points of the race just run are added now, once; a second press (back from the lobby) asks for the same race again */if(gp.pend){goRace(CUP_TRACKS[gp.cup][gp.race]);return;}const G=netGpNow();gp.pts=G.pts;gp.np=G.np;if(gp.race>=3){startGP();return;}gp.race++;gp.pend=1;goRace(CUP_TRACKS[gp.cup][gp.race]);return;}\n"
    "  if(gp){if(gp.race>=3)startGP();else{gp.race++;goRace(CUP_TRACKS[gp.cup][gp.race]);}}else goRace(mapIdx);};")
rep("clsKey=cfg.cls;mode=cfg.mode;gp=cfg.gp?JSON.parse(JSON.stringify(cfg.gp)):null;", "clsKey=cfg.cls;mode=cfg.mode;gp=cfg.gp?JSON.parse(JSON.stringify(cfg.gp)):null;if(gp)delete gp.pend;")
# ---- found on the way (2026-11-14): a toy room that is already on screen as the menu's picture, built before its Blender models had arrived, was raced
# with the plain code-built stand-ins (the kitchen's table and chairs were solid blocks): the loading screen only waited for the models, and only
# rebuilt the room, when the track had to be changed. Now a room built early is remembered (LATE_BUILD) and built again once the models are in.
rep("function loadMap(mi,rev){const hq=!!(QUAL[qKey]&&QUAL[qKey].hqAll);", "let LATE_BUILD=false;function loadMap(mi,rev){LATE_BUILD=typeof PROP_PACKS!=='undefined'&&!!(MAPS[mi]&&MAPS[mi].toy)&&Object.keys(PROP_PACKS).some(k=>k.startsWith('toy_')&&k.endsWith('_hq')&&!(PROP_PACKS[k].b||PROP_PACKS[k].d));/* a room built before its Blender models arrived: goRace builds it again */const hq=!!(QUAL[qKey]&&QUAL[qKey].hqAll);")
rep("if(m.toy&&!NET.role&&typeof PROP_PACKS!=='undefined'&&(mi!==mapIdx||rev!==curRev)){", "if(m.toy&&!NET.role&&typeof PROP_PACKS!=='undefined'&&(mi!==mapIdx||rev!==curRev||LATE_BUILD)){")
rep("    if(mi!==mapIdx||rev!==curRev){mapIdx=mi;loadMap(mi,rev);}await step(45,", "    if(mi!==mapIdx||rev!==curRev||LATE_BUILD){mapIdx=mi;loadMap(mi,rev);}await step(45,")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
