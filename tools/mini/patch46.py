"""Patch 46 (web v208, ONLINE VERSION 115 with patch 45): Sandbox on line, free roam together (web first; the PC follows).
The owner, 2026-11-16: "lets add sandbox and balloon battle online to the web version before porting to pc". The brief (NEXT-MODES-BRIEF.md,
Sandbox 8): "Let players share a world, meet up at a named section, cruise together, or split up and explore independently. Synchronize vehicle
movement and the world clock. Keep coins, challenge rewards, garage ownership, and unique collectibles per player. Each client should stream the
areas it needs even when players are on opposite sides of the world." And (Sandbox, online behaviour): the map, pause and fast travel are each
player's own.
How: not the race's model (the host cannot run a world whose places are loaded one per player). Every player's Sandbox runs on their own
screen exactly as off line; the room carries only where everyone is:
- each player sends its car's place 12 times a second ({t:'sp'}: the place's map id, x, y, height, heading, speed; its build every 2 s);
  the host collects them and sends everyone the list ({t:'sps'}), with its world clock (the friends' clocks follow it);
- a friend in the same place is drawn there (their own kart and paint, a name over it, 100 ms behind and smoothed); elsewhere they are
  listed in the corner with where they are; their car never touches yours (nothing on line moves your kart);
- the room starts Sandbox like a race (the host picks Sandbox and a place, everyone readies up), then the host sends {t:'sbgo', mi} and every
  screen starts its own Sandbox there; a friend who joins while the host is roaming is sent in too. NET.cfg stays empty in Sandbox.
- in a room, Sandbox's "Race here" is not offered (a race is the host's to start, from the room).
Run once: py.cmd tools/mini/patch46.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 46' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# a room keeps Sandbox too now
rep("/* (patch 45) a room keeps Balloon Battle; Sandbox is still off line */function sbNoNet(){if(mode==='sb')bbNoNet();}",
    "/* (patch 46) a room keeps Balloon Battle and Sandbox */function sbNoNet(){}")
rep("if(b.dataset.m==='sb'&&NET.role)return;/* Sandbox is off line only for now (Balloon Battle is on line since patch 45) */", "")
# starting: the room's Sandbox goes round the race's loading and waiting
rep("function netHostStart(mi){", "function netHostStart(mi){if(mode==='sb'){/* (patch 46) Sandbox: everyone starts their own, here */NET.sbx={on:true};NET.sbIn=new Set();netAll({t:'sbgo',mi});NET.fromNet=true;goRace(mi);return;}")
rep("async function goRace(mi){if(raceLoading)return;if(NET.role&&!NET.fromNet){",
    "async function goRace(mi){if(raceLoading)return;if(NET.role&&!NET.fromNet&&!(NET.sbx&&mode==='sb')){")
rep("  else if(d.t==='rtc'){if(d.nat)NET.natPeer=d.nat;rtcOnGuest(NET.conns[0],d);}",
    "  else if(d.t==='rtc'){if(d.nat)NET.natPeer=d.nat;rtcOnGuest(NET.conns[0],d);}\n"
    "  else if(d.t==='sbgo'){/* (patch 46) the room's Sandbox: start our own, at the host's place */if(!SBX&&state==='menu'){NET.sbx={on:true};netHideLobby();if(garageOpen)closeGarage();mode='sb';mapIdx=d.mi|0;NET.fromNet=true;goRace(mapIdx);}}\n"
    "  else if(d.t==='sps'){sbnGot(d);}")
rep("  else if(d.t==='rtc'){if(d.nat)c.natPeer=NET.natPeer=d.nat;rtcOnHost(c,d);}",
    "  else if(d.t==='rtc'){if(d.nat)c.natPeer=NET.natPeer=d.nat;rtcOnHost(c,d);}\n"
    "  else if(d.t==='sp'&&d.p){/* (patch 46) a friend's place in Sandbox */const q=Object.assign({},d.p,{id:c._id,at:performance.now()});if(!q.b){const o=NET.sbP&&NET.sbP.get(c._id);if(o)q.b=o.b;}(NET.sbP||(NET.sbP=new Map())).set(c._id,q);if(NET.sbIn)NET.sbIn.add(c._id);sbnPeer(q);}")
rep("netClearMirrors();Object.assign(NET,{role:null,code:'',peer:null,conns:[],me:0,pl:[],cfg:null,fromNet:false,loaded:new Set(),tick:0,seq:0,hist:[],outQ:[],inQ:{},inS:{},inLast:{},ack:{},snaps:[],fxQ:[],nid:0,finSeen:false});netBadge();}",
    "netClearMirrors();Object.assign(NET,{role:null,code:'',peer:null,conns:[],me:0,pl:[],cfg:null,fromNet:false,loaded:new Set(),tick:0,seq:0,hist:[],outQ:[],inQ:{},inS:{},inLast:{},ack:{},snaps:[],fxQ:[],nid:0,finSeen:false,sbx:null,sbP:new Map(),sbIn:new Set()});try{sbnClear();}catch(e){}netBadge();}")
# no "Race here" in a room's Sandbox
rep("function sbRaceBtn(on){", "function sbRaceBtn(on){if(NET.sbx&&NET.role)on=false;/* (patch 46) */")
# leaving Sandbox in a room: back to the room's screen
rep("function toMenu(){if(sbBack())return;sbOff();", "function toMenu(){if(sbBack())return;const wasSb=SBX&&NET.sbx&&NET.role;sbOff();if(wasSb)setTimeout(()=>{if(NET.role&&state==='menu')netShowLobby();},60);")
# friends drawn each frame
rep("try{sbNightFrame(time);}catch(e){console.warn('night',e);}", "try{sbNightFrame(time);}catch(e){console.warn('night',e);}try{sbnRender(time);}catch(e){console.warn('sbnet',e);}")
JS = r"""
/* ================= (patch 46) SANDBOX ON LINE: where everyone is ================= */
const SBN={peers:new Map(),bT:0,el:null,listT:0};
function sbnMine(){const k=player;if(!k)return null;const o={reg:MAPS[mapIdx].id,x:r3(k.rx!=null?k.rx:k.x),y:r3(k.ry!=null?k.ry:k.y),z:r3(k.rz!=null?k.rz:(k.wy||0)),a:r3(k.rma!=null?k.rma:k.ma),sp:r3(k.speed||0),nm:netName(),ri:selected,tr:SB.trav||state!=='race'?1:0};
  const now=performance.now();if(now-SBN.bT>2000){SBN.bT=now;o.b={b:playerBuild.b,w:playerBuild.w,g:playerBuild.g,p:playerBuild.p,t:playerBuild.t||''};}return o;}
/* 12 a second: my place out; on the host, everyone's places back out with the clock; a friend who came into the room late is sent in */
setInterval(()=>{if(!NET.role||!NET.sbx)return;const now=performance.now(),mine=SBX&&player?sbnMine():null;
  if(NET.role==='guest'){const c=NET.conns[0];if(mine&&c){const m={t:'sp',p:mine};if(c.sendF)c.sendF(m);else netSend(c,m);}return;}
  if(mine)(NET.sbP||(NET.sbP=new Map())).set(0,Object.assign(mine,{id:0,at:now,b:mine.b||(NET.sbP.get(0)||{}).b}));
  const l=[];for(const [id,q] of NET.sbP||[])if(now-q.at<4000)l.push(q);const m={t:'sps',ck:SB_CLOCK?+sbClockNow().toFixed(4):null,l};
  for(const c of NET.conns){if(!c.open)continue;if(c.sendF)c.sendF(m);else netSend(c,m);if(SBX&&NET.sbIn&&!NET.sbIn.has(c._id)&&(!c.sbgoT||now-c.sbgoT>2000)){c.sbgoT=now;netSend(c,{t:'sbgo',mi:mapIdx});}}},80);
function sbnGot(d){const now=performance.now();for(const q of d.l||[]){if(q.id===NET.me)continue;sbnPeer(Object.assign({},q,{at:now}));}
  /* the world clock is the host's */if(d.ck!=null&&SBX&&SB_CLOCK){const df=((d.ck-sbClockNow())%1+1.5)%1-.5;if(Math.abs(df)>.004){SB.clock=(d.ck+1)%1;try{sbClockApply();}catch(e){}}}}
function sbnPeer(q){let P=SBN.peers.get(q.id);if(!P){P={id:q.id,s:[]};SBN.peers.set(q.id,P);}P.nm=q.nm;P.ri=q.ri;P.reg=q.reg;P.tr=q.tr;P.at=q.at;if(q.b)P.b=q.b;
  P.s.push({t:q.at,x:q.x,y:q.y,z:q.z,a:q.a,sp:q.sp});if(P.s.length>6)P.s.shift();}
function sbnDrop(P){if(P.m){scene.remove(P.m.g);P.m=null;}if(P.tag){scene.remove(P.tag);P.tag.material.map.dispose();P.tag.material.dispose();P.tag=null;}}
function sbnClear(){for(const P of SBN.peers.values())sbnDrop(P);SBN.peers.clear();if(SBN.el)SBN.el.hidden=true;}
function sbnTag(nm){const c=cnv(256,64),g=c.getContext('2d');g.font='800 30px system-ui,sans-serif';const w=Math.min(240,g.measureText(nm).width+28);g.fillStyle='rgba(18,9,6,.7)';g.beginPath();g.roundRect?g.roundRect(128-w/2,8,w,48,14):g.rect(128-w/2,8,w,48);g.fill();
  g.fillStyle='#fff4dc';g.textAlign='center';g.textBaseline='middle';g.fillText(nm,128,33);const t=T2(c);t.userData.keepCanvas=true;const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,depthTest:false,transparent:true,toneMapped:false}));sp.scale.set(16,4,1);sp.renderOrder=6;return sp;}
/* each frame: friends in this place are drawn 100 ms behind (between the places they sent), others listed in the corner */
function sbnRender(time){if(!NET.role||!NET.sbx){if(SBN.peers.size)sbnClear();return;}const now=performance.now(),here=MAPS[mapIdx].id,list=[];
  for(const P of [...SBN.peers.values()]){if(now-P.at>5000){sbnDrop(P);SBN.peers.delete(P.id);continue;}list.push(P);
    const show=SBX&&state!=='menu'&&!SB.trav&&!P.tr&&P.reg===here&&P.s.length;if(!show){if(P.m)P.m.g.visible=false;if(P.tag)P.tag.visible=false;continue;}
    const key=JSON.stringify([P.ri,P.b||null]);if(!P.m||P.key!==key){if(P.m)scene.remove(P.m.g);try{const m=buildKart(Object.assign({ri:P.ri|0},P.b||{b:0,w:0,g:0,p:0,t:''},{hq:0}));m.g.rotation.order='YZX';m.g.scale.setScalar(KS*m.sf);if(m.gl)m.gl.visible=false;m.g.traverse(o=>{if(o.isMesh)o.castShadow=true;});scene.add(m.g);P.m=m;P.key=key;}catch(e){P.m=null;continue;}}
    if(!P.tag){P.tag=sbnTag(P.nm||'Friend');scene.add(P.tag);}
    const t=now-100,S=P.s;let A=S[0],B=S[S.length-1];for(let i=S.length-1;i>0;i--){if(S[i-1].t<=t){A=S[i-1];B=S[i];break;}}
    let x,y,z,a;if(t>=B.t){const e=Math.min(.2,(t-B.t)/1000);x=B.x+Math.cos(B.a)*B.sp*e;y=B.y+Math.sin(B.a)*B.sp*e;z=B.z;a=B.a;}else{const f=B.t>A.t?clamp((t-A.t)/(B.t-A.t),0,1):1;x=A.x+(B.x-A.x)*f;y=A.y+(B.y-A.y)*f;z=A.z+(B.z-A.z)*f;a=lerpA(A.a,B.a,f);}
    P.m.g.visible=true;P.m.g.position.set(x,z,y);P.m.g.rotation.set(0,-a,0);P.tag.visible=true;P.tag.position.set(x,z+17,y);}
  /* the corner list: who is where (four times a second) */
  if(time-SBN.listT>.25){SBN.listT=time;let e=SBN.el;if(!e){e=SBN.el=document.createElement('div');e.id='sbnList';e.style.cssText='position:absolute;right:max(10px,env(safe-area-inset-right));top:118px;z-index:6;font:700 12px/1.35 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.55);border-radius:10px;padding:6px 10px;pointer-events:none;text-shadow:0 1px 2px #000;max-width:46vw';stage.appendChild(e);}
    e.hidden=!SBX||!list.length||state==='menu';if(!e.hidden)e.innerHTML=list.map(P=>{const r=sbRegOf(P.reg),nm=String(P.nm||'Friend').replace(/[<>&]/g,''),w=P.reg===here?'<span style="color:#8be08b">here</span>':(r?r.name.split(' \u00b7 ').pop():P.reg);return nm+' <span style="opacity:.6">\u00b7</span> '+w;}).join('<br>');}}
"""
rep("/* ================= (patch 44) USERNAMES AND THE WORLD LEADERBOARD", JS + "/* ================= (patch 44) USERNAMES AND THE WORLD LEADERBOARD")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 46 applied')
