"""Patch 52 (web v213, NET_PROTO 117): in a room's Sandbox anyone can start a race at a start line and invite everyone.
The owner: "if a guest player or even the host for that matter tries to start a race online it will send out like an invite to the other
person and they can just be teleported to the race and when the race is over they just stay at the track when they go back into sandbox",
and: "the host would always have to be in an online race in sandbox but this way anyone can start a lobby if the host is not on the
track currently they want to race on but the guest is".
- At a start line in a room's Sandbox the race offer is back (patch 46 had turned it off). Taking it asks: Race with friends, Race alone,
  Cancel (keys 1 / 2 / Esc; controller up / down; driving away cancels).
- Race alone: the start line's own race, off line, while still in the room (NET.soloSb lets goRace past the room's ready-up); leaving it
  is back to Sandbox there, as off line.
- Race with friends: the host sends an invite to everyone (guests ask the host with {t:'sbinv', mi}); each sees "<name> wants to race on
  <track>!" with Join / No thanks (J / N; controller up / down), 10 s to answer. The race is run by the host's computer, so THE HOST HAS TO
  JOIN: if the host says no (or does not answer) the invite is called off and whoever asked is offered a race alone. Otherwise, once
  everyone has answered or the 10 s are up, the host starts an ordinary room race (cfg.sbr = 1, mode 'single') on that track for the
  host and those who joined: NET.sbRace holds their ids, and netAll, the snapshots, the load resend, netMaybeGo and netBuildCfg leave
  everyone else out, so they keep driving in Sandbox (their places still pass through the host).
- After the race, the results' "Back to Sandbox" (sbBack) puts each player back into Sandbox AT THAT TRACK. When the host goes back the
  race ends for everyone still in it ({t:'sbend'}); a guest going back early tells the host ({t:'quit'}).
- Messages: guest -> host sbinv {mi}, sbans {id, yes}; host -> guests sbinv {id, mi, by, name, me}, sbinvx {why: host | busy | go}, sbend.
  The PC speaks the same (scripts/webnet.gd).
Run once: py.cmd tools/mini/patch52.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 52' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


# only the racers hear the race
rep("function netAll(m){for(const c of NET.conns)netSend(c,m);}",
    "function netAll(m){for(const c of NET.conns){if(NET.sbRace&&!NET.sbRace.has(c._id))continue;/* (patch 52: a Sandbox race: its racers only) */netSend(c,m);}}")
rep("for(const c of NET.conns){if(!c.open)continue;const dv=netSnDiv(c);",
    "for(const c of NET.conns){if(!c.open||(NET.sbRace&&!NET.sbRace.has(c._id)))continue;const dv=netSnDiv(c);")
rep("for(const c of NET.conns)if(c.open&&!NET.loaded.has(c._id))netSend(c,{t:'load',cfg:NET.cfg});",
    "for(const c of NET.conns)if(c.open&&!NET.loaded.has(c._id)&&(!NET.sbRace||NET.sbRace.has(c._id)))netSend(c,{t:'load',cfg:NET.cfg});")
rep("const open=NET.conns.filter(c=>c.open),need=open.map(c=>c._id);if(!(need.every(id=>NET.loaded.has(id))&&NET.loaded.has(0)))return;",
    "const open=NET.conns.filter(c=>c.open&&(!NET.sbRace||NET.sbRace.has(c._id))),need=open.map(c=>c._id);if(!(need.every(id=>NET.loaded.has(id))&&NET.loaded.has(0)))return;")
rep("const pl=NET.pl.filter(p=>p.id===0||p.conn&&p.conn.open);",
    "const pl=NET.pl.filter(p=>p.id===0||p.conn&&p.conn.open&&(!NET.sbRace||NET.sbRace.has(p.id)));")
rep("const NET_PROTO=116;", "const NET_PROTO=117;/* (117: patch 52, a Sandbox race from a start line with invites) */")

# messages
rep("else if(d.t==='sp'&&d.p){",
    "else if(d.t==='sbinv'){sbInvStart(d.mi|0,c._id);}else if(d.t==='sbans'){const H=SBI.host;if(H&&H.id===d.id)H.ans.set(c._id,!!d.yes);}/* (patch 52) */\n  else if(d.t==='sp'&&d.p){")
rep("else if(d.t==='sps'){sbnGot(d);}",
    "else if(d.t==='sps'){sbnGot(d);}\n  else if(d.t==='sbinv'){sbInvGot(d);}else if(d.t==='sbinvx'){sbInvOff(d.why);}else if(d.t==='sbend'){if(NET.cfg&&NET.cfg.sbr){if(!SB.back)SB.back=MAPS[NET.cfg.mi].id;sbBack();}}/* (patch 52) */")
rep("else if(d.t==='load'){if(!(NET.cfg&&d.cfg.id&&NET.cfg.id===d.cfg.id))netBeginLoad(d.cfg);}",
    "else if(d.t==='load'){if(!(NET.cfg&&d.cfg.id&&NET.cfg.id===d.cfg.id)){if(d.cfg.sbr){SB.back=MAPS[d.cfg.mi].id;sbiClear();}netBeginLoad(d.cfg);}}")

# the start line's offer in a room
rep("if(NET.sbx&&NET.role)on=false;/* (patch 46) */", "if(!on&&SBI.ask)sbRaceAskPick('c');/* (patch 52: the offer is back in rooms; driving away cancels its question) */")
rep("function sbRaceHere(){if(!SBX||SB.trav||state!=='race'||raceLoading)return;",
    "function sbRaceHere(){if(!SBX||SB.trav||state!=='race'||raceLoading)return;if(performance.now()-(SBI.pickT||0)<600)return;"
    "if(NET.sbx&&NET.role){if(SBI.ask)sbRaceAskPick('f');else if(!SBI.wait&&!SBI.inv)sbRaceAsk();return;}/* (patch 52) */")
rep("function sbBack(){if(!SB.back)return false;const id=SB.back;SB.back=null;if(NET.cfg||NET.role)return false;",
    "function sbBack(){if(!SB.back)return false;const id=SB.back;SB.back=null;"
    "if(NET.role&&!NET.sbx)return false;if(NET.cfg&&!NET.cfg.sbr)return false;"
    "if(NET.cfg){NETLOG.stop();if(NET.role==='host'){netAll({t:'sbend'});NET.sbRace=null;}else netSend(NET.conns[0],{t:'quit'});NET.cfg=null;netClearMirrors();}"
    "NET.soloSb=false;NET.fromNet=!!NET.role;/* (patch 52: a room's Sandbox race, or a race alone in a room, goes back to Sandbox at that track) */")
rep("if(NET.role&&!NET.fromNet&&!(NET.sbx&&mode==='sb')){", "if(NET.role&&!NET.fromNet&&!(NET.sbx&&mode==='sb')&&!NET.soloSb){")
rep("resLive=rows.some(r=>r.racing)?.5:0;$('specBtn').hidden=!specCanWatch();$('resNetLog').hidden=false;}",
    "resLive=rows.some(r=>r.racing)?.5:0;$('specBtn').hidden=!specCanWatch();$('resNetLog').hidden=false;"
    "if(NET.cfg&&NET.cfg.sbr){SBI.res=1;$('againBtn').hidden=true;$('trackBtn').hidden=true;$('toMenuBtn').hidden=false;$('toMenuBtn').textContent='Back to Sandbox';}"
    "else if(SBI.res){SBI.res=0;$('againBtn').hidden=false;$('trackBtn').hidden=false;}/* (patch 52) */}")

# controller and keys
rep("if(SBX&&edge(M.DOWN)&&state==='race')sbPark();",
    "if(SBI.ask){if(edge(M.UP))sbRaceAskPick('f');else if(edge(M.DOWN))sbRaceAskPick('a');}else if(SBI.inv&&SBI.inv.ans==null){if(edge(M.UP))sbInvAnswer(true);else if(edge(M.DOWN))sbInvAnswer(false);}/* (patch 52) */"
    "else if(SBX&&edge(M.DOWN)&&state==='race')sbPark();")
rep("const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp)sbRaceHere();",
    "const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp&&!SBI.ask&&!SBI.inv)sbRaceHere();")

JS = r"""
/* ================= (patch 52) A ROOM'S SANDBOX: A RACE FROM A START LINE, WITH INVITES ================= */
const SBI={ask:null,inv:null,wait:null,host:null,res:0,pickT:0};
const SBI_BTN='font:800 14px system-ui,sans-serif;border:0;border-radius:11px;padding:9px 14px;margin:8px 4px 0;cursor:pointer;';
function sbiEl(id,html){let e=document.getElementById(id);if(!e){e=document.createElement('div');e.id=id;e.setAttribute('role','dialog');
    e.style.cssText='position:absolute;left:50%;transform:translateX(-50%);bottom:max(150px,calc(env(safe-area-inset-bottom) + 150px));z-index:30;width:max-content;max-width:min(92vw,470px);font:700 15px/1.35 system-ui,sans-serif;color:#fff4dc;background:rgba(24,12,8,.93);border:2px solid #f5b62e;border-radius:16px;padding:12px 16px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,.5)';
    e.addEventListener('pointerdown',ev=>ev.stopPropagation());stage.appendChild(e);}if(html!=null)e.innerHTML=html;e.hidden=false;return e;}
function sbiHide(id){const e=document.getElementById(id);if(e)e.hidden=true;}
function sbiClear(){SBI.ask=null;SBI.inv=null;SBI.wait=null;clearInterval(SBI.ct);clearInterval(SBI.wt);for(const id of ['sbiAsk','sbiInv','sbiWait'])sbiHide(id);}
const sbiHelp=t=>typeof COARSE!=='undefined'&&COARSE?'':'<div style="font-weight:600;font-size:11px;opacity:.6;margin-top:6px">'+t+'</div>';
/* the start line's question */
function sbRaceAsk(){const mi=mapIdx;SBI.ask={mi};
  sbiEl('sbiAsk','<div>Race on '+lbEsc(MAPS[mi].name)+'</div><div style="font-weight:600;font-size:12.5px;opacity:.8">With friends: everyone in the room is asked to join you here.</div>'+
    '<button id="sbiF" type="button" style="'+SBI_BTN+'background:#f5b62e;color:#1b0f0b">Race with friends</button><button id="sbiA" type="button" style="'+SBI_BTN+'background:#4a3428;color:#fff4dc">Race alone</button><button id="sbiC" type="button" style="'+SBI_BTN+'background:transparent;color:#fff4dc;border:1px solid rgba(255,244,220,.35)">Cancel</button>'+
    sbiHelp('1 friends · 2 alone · Esc cancel · controller: up friends, down alone'));
  $('sbiF').onclick=()=>sbRaceAskPick('f');$('sbiA').onclick=()=>sbRaceAskPick('a');$('sbiC').onclick=()=>sbRaceAskPick('c');}
function sbRaceAskPick(w){const a=SBI.ask;SBI.ask=null;SBI.pickT=performance.now();sbiHide('sbiAsk');if(!a||w==='c')return;
  if(w==='a'){sbRaceAlone(a.mi);return;}
  if(NET.role==='host')sbInvStart(a.mi,0);else{netSend(NET.conns[0],{t:'sbinv',mi:a.mi});sbInvWait(a.mi);}}
function sbRaceAlone(mi){if(!SBX||state!=='race')return;if(SBA.act)sbActEnd('cancel');NET.soloSb=true;SB.back=MAPS[mi].id;sbRaceBtn(false);mode='single';goRace(mi);}
/* the host: an invite out, the answers in, then the race (or not) */
function sbInvStart(mi,by){const bc=by?NET.conns.find(c=>c._id===by):null;
  if(SBI.host||NET.cfg||!SBX&&by===0){if(bc)netSend(bc,{t:'sbinvx',why:'busy'});else showBanner('A race is already being set up',1.6,'sm');return;}
  if(!MAPS[mi]){if(bc)netSend(bc,{t:'sbinvx',why:'busy'});return;}
  const id=netRid(),name=by===0?netName():((NET.pl.find(p=>p.id===by)||{}).name||'A friend');
  SBI.host={id,mi,by,name,ans:new Map([[by,true]]),t0:performance.now()};
  for(const c of NET.conns)if(c.open)netSend(c,{t:'sbinv',id,mi,by,name,me:c._id===by?1:0});
  if(by===0)sbInvWait(mi);else if(SBX&&state==='race')sbInvShow({id,mi,name});else SBI.host.ans.set(0,false);
  clearInterval(SBI.tick);SBI.tick=setInterval(sbInvTick,200);}
function sbInvTick(){const H=SBI.host;if(!H){clearInterval(SBI.tick);return;}
  const open=NET.conns.filter(c=>c.open).map(c=>c._id),all=open.every(id=>H.ans.has(id))&&H.ans.has(0),late=performance.now()-H.t0>10500;
  if(SBI.wait)sbInvWaitTxt([...H.ans.values()].filter(Boolean).length);
  if(H.ans.get(0)!==false&&!all&&!late)return;
  clearInterval(SBI.tick);SBI.host=null;
  if(H.ans.get(0)!==true){/* the host is not racing: no race on line */sbiClear();for(const c of NET.conns)if(c.open)netSend(c,{t:'sbinvx',why:'host'});return;}
  sbInvGo(H.mi,open.filter(id=>H.ans.get(id)===true));}
function sbInvGo(mi,ids){sbiClear();NET.sbRace=new Set(ids);for(const c of NET.conns)if(c.open&&!NET.sbRace.has(c._id))netSend(c,{t:'sbinvx',why:'go'});
  if(SBA.act)sbActEnd('cancel');sbRaceBtn(false);SB.back=MAPS[mi].id;mode='single';gp=null;
  if(!cpuBuilds||!cpuBuilds.length)cpuBuilds=RACERS.map(randomBuild);NET.pl[0].ri=selected;NET.pl[0].build=playerBuild;
  const cfg=netBuildCfg(mi);cfg.id=netRid();cfg.sbr=1;NET.loaded=new Set();
  for(const c of NET.conns)if(c.open&&NET.sbRace.has(c._id))netSend(c,{t:'load',cfg});netBeginLoad(cfg);}
/* everyone: an invite in */
function sbInvGot(d){if(d.me){if(SBI.wait)SBI.wait.id=d.id;return;}
  if(!SBX||(state!=='race'&&state!=='paused')||NET.cfg||NET.soloSb){netSend(NET.conns[0],{t:'sbans',id:d.id,yes:false});return;}sbInvShow(d);}
function sbInvShow(d){SBI.inv={id:d.id,t0:performance.now(),mi:d.mi,ans:null};
  sbiEl('sbiInv','<div>'+lbEsc(d.name)+' wants to race on '+lbEsc((MAPS[d.mi]||{}).name||'a track')+'!</div><div style="font-weight:600;font-size:12.5px;opacity:.8">Join and you go straight to the start line.</div>'+
    '<button id="sbiJ" type="button" style="'+SBI_BTN+'background:#f5b62e;color:#1b0f0b">Join</button><button id="sbiN" type="button" style="'+SBI_BTN+'background:#4a3428;color:#fff4dc">No thanks</button><div id="sbiT" style="font-weight:600;font-size:11px;opacity:.6;margin-top:6px"></div>');
  $('sbiJ').onclick=()=>sbInvAnswer(true);$('sbiN').onclick=()=>sbInvAnswer(false);
  clearInterval(SBI.ct);SBI.ct=setInterval(()=>{const I=SBI.inv;if(!I){clearInterval(SBI.ct);return;}const left=Math.max(0,10-(performance.now()-I.t0)/1000),t=$('sbiT');
    if(t)t.textContent=(I.ans?'Joined: waiting for the others':Math.ceil(left)+' s')+(typeof COARSE!=='undefined'&&COARSE?'':' · J join · N no · controller: up join, down no');if(left<=0&&I.ans==null)sbInvAnswer(false);},200);}
function sbInvAnswer(yes){const I=SBI.inv;if(!I||I.ans!=null)return;I.ans=!!yes;
  if(NET.role==='host'){const H=SBI.host;if(H&&H.id===I.id)H.ans.set(0,!!yes);}else netSend(NET.conns[0],{t:'sbans',id:I.id,yes:!!yes});
  if(!yes){SBI.inv=null;clearInterval(SBI.ct);sbiHide('sbiInv');}else{const b=$('sbiJ'),n=$('sbiN');if(b){b.disabled=true;b.textContent='Joined';}if(n)n.hidden=true;}}
/* whoever asked: waiting for the answers */
function sbInvWait(mi){SBI.wait={mi,t0:performance.now()};sbiEl('sbiWait','<div>Asking everyone in the room to race on '+lbEsc(MAPS[mi].name)+'...</div><div id="sbiWT" style="font-weight:600;font-size:12.5px;opacity:.8"></div>');
  sbInvWaitTxt(null);clearInterval(SBI.wt);SBI.wt=setInterval(()=>{if(!SBI.wait){clearInterval(SBI.wt);return;}sbInvWaitTxt(null);if(performance.now()-SBI.wait.t0>16000)sbInvOff('host');},250);}
function sbInvWaitTxt(n){const W=SBI.wait,t=$('sbiWT');if(!W||!t)return;if(n!=null)W.n=n;t.textContent=(W.n!=null?W.n+' in so far · ':'')+Math.max(0,Math.ceil(10-(performance.now()-W.t0)/1000))+' s';}
/* the host's answer: off (no race on line) */
function sbInvOff(why){const asked=!!SBI.wait,mi=SBI.wait?SBI.wait.mi:mapIdx;sbiClear();
  if(why==='busy')showBanner('A race is already being set up',1.8,'sm');
  else if(why==='host'&&asked){const e=sbiEl('sbiAsk','<div>The room\'s host can\'t race right now</div><div style="font-weight:600;font-size:12.5px;opacity:.8">A race on line is run by the host\'s game, so the host has to join it.</div>'+
      '<button id="sbiA2" type="button" style="'+SBI_BTN+'background:#f5b62e;color:#1b0f0b">Race alone</button><button id="sbiC2" type="button" style="'+SBI_BTN+'background:transparent;color:#fff4dc;border:1px solid rgba(255,244,220,.35)">OK</button>');
    $('sbiA2').onclick=()=>{sbiHide('sbiAsk');sbRaceAlone(mi);};$('sbiC2').onclick=()=>sbiHide('sbiAsk');}}
addEventListener('keydown',e=>{if(SBI.ask){if(e.code==='Digit1'||e.code==='Numpad1'){e.preventDefault();sbRaceAskPick('f');}else if(e.code==='Digit2'||e.code==='Numpad2'){e.preventDefault();sbRaceAskPick('a');}else if(e.code==='Escape'){e.preventDefault();e.stopPropagation();sbRaceAskPick('c');}}
  else if(SBI.inv&&SBI.inv.ans==null){if(e.code==='KeyJ'){e.preventDefault();e.stopPropagation();sbInvAnswer(true);}else if(e.code==='KeyN'){e.preventDefault();e.stopPropagation();sbInvAnswer(false);}}},true);
"""
rep("/* ================= (patch 44) USERNAMES AND THE WORLD LEADERBOARD",
    JS + "/* ================= (patch 44) USERNAMES AND THE WORLD LEADERBOARD")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 52 applied')
