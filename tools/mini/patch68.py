"""Patch 68 (web v219, NET_PROTO 120): developer options, unlocked by the cheat code DEVELOPER.
The owner: "add a developer settings spot that pops up in settings when you enter the cheat code developer ... sliders for the vehicles
and the ability to adjust character abilities etc." / "turn on and off certain mobs and obstacles on the map" / "a flying option ... push
the left thumbstick down on controller you can fly around, add a pc bind for this too" / "an unlimited pepperoni item option" / "add the
dev options online but only the host can change the settings and if they do it will change for both players" / "put all the dev options in".

DEV (store 'crust-dev'; DEVU = unlocked, store 'crust-dev-on'), shown in Settings under the cheat code box (devUI). Two kinds:
  RACE settings (devR: off line yours; in a room the HOST's, sent as cfg.dev at the start of each race and applied the same on every
  screen, web and PC alike, to every kart; a guest's own are ignored there): vehicle top speed, acceleration, handling, weight, off-road
  grip; drift boost; gravity; ability charge speed and always ready; rival skill; each kind of world hazard (traffic, trains, walkers,
  ponds, the city's) on or off. Off line they change YOUR vehicle only (rivals keep theirs), from the next race (the vehicle ones also at
  once while racing alone).
  THIS DEVICE only (devLocal: off line, never in a room): game speed, field of view, the HUD, flying, invincible, always this item,
  unlimited pepperoni; and the cheats (+1000 coins, the whole style shop).
Flying (devFly, in place of the player's stepKart): the left stick press or G toggles it; steer as usual, the throttle flies forward
and the brake backs off; stick up / I or Page Up climbs, stick down / K or Page Down descends; never below the ground.
Online: cfg.dev changes how karts move, so the online version goes to 120 (the PC applies it the same: webnet / race / kart).
Run once: py.cmd tools/mini/patch68.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 68' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------------------------------------------------------------- state, the two scopes
rep("let NOITM=false,ITMUSED=false,RPAY=0,RDEMO=false;", r"""let NOITM=false,ITMUSED=false,RPAY=0,RDEMO=false;
/* (patch 68) developer options: DEVU unlocked (cheat DEVELOPER); DEV the settings */
let DEVU=store.get('crust-dev-on')==='1';
const DEVDEF={on:1,spd:1,acc:1,hnd:1,wgt:1,off:0,drift:1,grav:1,abil:1,abilReady:0,cpu:1,hz:{traffic:1,train:1,walk:1,pool:1,city:1},speed:1,fov:58,hud:1,fly:0,inv:0,item:'',infPep:0};
let DEV=(()=>{let v={};try{v=JSON.parse(store.get('crust-dev')||'{}')||{};}catch(e){}const d=Object.assign({},DEVDEF,v);d.hz=Object.assign({},DEVDEF.hz,v.hz||{});return d;})();
function devSave(){store.set('crust-dev',JSON.stringify(DEV));}
/* the race settings in force: in a room the host's (cfg.dev), off line yours; null when off */
function devR(){if(NET.cfg)return NET.cfg.dev||null;return DEVU&&DEV.on?DEV:null;}
/* this device only: off line, never in a room */
function devLocal(){return !NET.cfg&&!NET.role&&DEVU&&DEV.on?DEV:null;}
/* a kart's race settings: in a room every kart's; off line only yours */
function devFor(k){const D=devR();return D&&(NET.cfg||k===player)?D:null;}
/* what the host sends: the race settings only */
function devPack(){if(!(DEVU&&DEV.on))return null;const D=DEV;return {spd:D.spd,acc:D.acc,hnd:D.hnd,wgt:D.wgt,off:D.off,drift:D.drift,grav:D.grav,abil:D.abil,abilReady:D.abilReady?1:0,cpu:D.cpu,hz:Object.assign({},D.hz)};}
function devKart(k,isP){const D0=devR(),D=D0&&(NET.cfg||isP||k===player)?D0:null;k.sm0=k.sm0||k.sm;k.sm=Object.assign({},k.sm0);if(!D)return;k.sm.spd*=D.spd;k.sm.acc*=D.acc;k.sm.hnd*=D.hnd;k.sm.wgt*=D.wgt;k.sm.off+=D.off;}""")

# ---------------------------------------------------------------- race settings
rep("    ai:{lane:lat,laneTarget:lat,laneT:1+Math.random()*3,skill:sk,itemDelay:0,inBend:false}};\n",
    "    ai:{lane:lat,laneTarget:lat,laneT:1+Math.random()*3,skill:sk,itemDelay:0,inBend:false}};\n"
    "  try{devKart(k,isPlayer);const D=devR();if(D&&!isPlayer)k.ai.skill*=D.cpu;}catch(e){}/* (patch 68: developer options) */\n")
rep("k.boost=Math.max(k.boost,[0,.55,.9,1.3][tier])", "k.boost=Math.max(k.boost,[0,.55,.9,1.3][tier]*(devFor(k)?devFor(k).drift:1))")
rep("k.wvy-=(k.big?(k.wvy>0?80:110):260)*dt", "k.wvy-=(k.big?(k.wvy>0?80:110):260)*dt*(devFor(k)?devFor(k).grav:1)")
rep("k.abC=Math.min(1,(k.abC||0)+dt/ABIL_TIME)", "k.abC=Math.min(1,(k.abC||0)+dt/ABIL_TIME*(devFor(k)?(devFor(k).abilReady?1e6:devFor(k).abil):1))")
rep("const set=HZSET[def.id]||[];", "const set=(HZSET[def.id]||[]).filter(k=>{const D=devR();return !D||!D.hz||D.hz[k]!==0;});/* (patch 68: a hazard switched off in the developer options) */")
rep("ks.sort((a,b)=>a.slot-b.slot);return {mi,cls:clsKey,mode,gp:gp?JSON.parse(JSON.stringify(gp)):null,karts:ks,ni:itemsOff()};}",
    "ks.sort((a,b)=>a.slot-b.slot);return {mi,cls:clsKey,mode,gp:gp?JSON.parse(JSON.stringify(gp)):null,karts:ks,ni:itemsOff(),dev:devPack()};}/* (patch 68: the host's race settings) */")
rep("const NET_PROTO=119;", "const NET_PROTO=120;/* (120: patch 68, the host's developer options in cfg.dev) */")

# ---------------------------------------------------------------- this device: items, speed, camera, HUD, invincible, flying
rep("function rollItem(pos){", "function rollItem(pos){{const D=devLocal();if(D&&D.item)return D.item;}/* (patch 68: always this item) */")
rep("function update(dt){NET.inUpd=", "function update(dt){try{devFrame(dt);}catch(e){}NET.inUpd=")
rep("if(state==='menu'||state==='race'){acc+=dt;", "if(state==='menu'||state==='race'){acc+=dt*(state==='race'&&devLocal()?devLocal().speed:1);/* (patch 68: game speed) */")
rep("camera.up.set(0,1,0);if(Math.abs(camera.fov-58)>.1){camera.fov=58;", "camera.up.set(0,1,0);const devFov=devLocal()?devLocal().fov:58;if(Math.abs(camera.fov-devFov)>.1){camera.fov=devFov;")
rep("const KB_HELD={left:1,right:1,brake:1,look:1};", "const KB_HELD={left:1,right:1,brake:1,look:1,flyup:1,flydown:1};")
rep("['lights','Headlights (Sandbox)']];", "['lights','Headlights (Sandbox)'],['fly','Fly (developer)'],['flyup','Fly up (developer)'],['flydown','Fly down (developer)']];")
rep("sbback:['KeyT'],lights:['KeyL']};", "sbback:['KeyT'],lights:['KeyL'],fly:['KeyG'],flyup:['KeyI','PageUp'],flydown:['KeyK','PageDown']};")
rep("else if(a==='ability'){if(!e.repeat)abilQueued=true;e.preventDefault();}",
    "else if(a==='ability'){if(!e.repeat)abilQueued=true;e.preventDefault();}else if(a==='fly'){if(!e.repeat)devFlyToggle();e.preventDefault();}")
rep("  const ax=gp.axes[0]||0,ay=gp.axes[1]||0,dz=.2,",
    "  if(edge(10))devFlyToggle();/* (patch 68: the left stick's press toggles flying) */\n  const ax=gp.axes[0]||0,ay=gp.axes[1]||0,dz=.2,")
rep("function spinOut(k,kind,world,force){", "function spinOut(k,kind,world,force){if(k===player&&devLocal()&&devLocal().inv)return false;/* (patch 68: invincible) */")
rep("function stepKart(k,inp,dt){", r"""/* (patch 68) the developer options each step, and flying */
function devFrame(dt){const D=devLocal();document.body.classList.toggle('devnohud',!!(D&&!D.hud));if(!D||!player||state!=='race')return;
  if(D.infPep&&!player.finished&&!player.item&&!player.held)player.item='pepperoni';if(!D.fly&&player.fly)player.fly=false;
  if(typeof PAD!=='undefined'){try{const gps=navigator.getGamepads?navigator.getGamepads():[];let gp=null;for(const g of gps||[])if(g&&g.connected)gp=g;PAD.ay=gp?(Math.abs(gp.axes[1]||0)<.2?0:gp.axes[1]):0;}catch(e){}}}
function devFlyToggle(){const D=devLocal();if(!D||!D.fly||!player||state!=='race')return;player.fly=!player.fly;if(player.fly){player.wvy=0;player.spin=0;}showBanner(player.fly?'Flying':'Landing',1,'sm');}
function devFly(k,inp,dt){k.air=true;k.loop=null;k.drift=0;k.spin=0;k.charge=0;
  const thr=inp.brake?-.45:(inp.mul>0?1:0);k.speed+=(thr*300-k.speed)*Math.min(1,dt*1.5);k.steer=inp.steer;k.a+=inp.steer*2.1*dt;k.ma=k.a;
  const up=(keys.flyup?1:0)-(keys.flydown?1:0)-(PAD.act?(PAD.ay||0):0);k.wvy=(k.wvy||0)+(Math.max(-1,Math.min(1,up))*150-(k.wvy||0))*Math.min(1,dt*4);
  k.x+=Math.cos(k.a)*k.speed*dt;k.y+=Math.sin(k.a)*k.speed*dt;k.wy=(k.wy||0)+k.wvy*dt;let g=0;try{g=kGround(k);}catch(e){}if(k.wy<g+1){k.wy=g+1;if(k.wvy<0)k.wvy=0;}k.z=0;k.zv=0;}
function stepKart(k,inp,dt){if(k===player&&k.fly&&devLocal()&&devLocal().fly)return devFly(k,inp,dt);""")
# a vehicle slider while racing alone: at once
# (devUI calls devKart(player) when off line)

# ---------------------------------------------------------------- the cheat code, the Settings section
rep("  if(c==='UNLOCK'){CHEAT=true;",
    "  if(c==='DEVELOPER'){DEVU=!DEVU;store.set('crust-dev-on',DEVU?'1':'0');m.textContent=DEVU?'Developer options unlocked: they are just below this box. Enter DEVELOPER again to hide them.':'Developer options hidden.';m.className='cheat-msg ok';try{SFX.ring();}catch(e){}devUI();}\n"
    "  else if(c==='UNLOCK'){CHEAT=true;")
rep('       <p id="cheatMsg" class="cheat-msg" role="status" aria-live="polite"></p>\n     </section>',
    '       <p id="cheatMsg" class="cheat-msg" role="status" aria-live="polite"></p>\n     </section>\n'
    '     <section class="set-group dev" data-cat="more" id="devSec" hidden><h3 class="label">Developer</h3><div id="devBody"></div></section>')
rep("function applyCheat(code){", r"""/* (patch 68) the developer section: rows built from DEVS; a change is saved and, off line while racing, applied to your vehicle at once */
const DEVS=[['Race settings',"Yours off line (your vehicle only). In a room you host they go to everyone's karts at the start of each race; a guest's are not used there.",[
    ['spd','Top speed',.5,2,.05],['acc','Acceleration',.25,3,.05],['hnd','Handling',.25,3,.05],['wgt','Weight',.4,2.5,.05],['off','Off-road grip',-1,2,.1,'+'],
    ['drift','Drift boost',0,3,.1],['grav','Gravity',.2,2,.05],['abil','Ability charge speed',.25,10,.25],['abilReady','Ability always ready','t'],['cpu','Rival skill',.5,1.5,.05]]],
  ['Mobs and obstacles','The moving hazards, on the tracks that have them. Also sent to everyone in a room you host.',[['hz.traffic','Traffic','t'],['hz.train','Trains','t'],['hz.walk','Walkers','t']]],
  ['This device','Off line only.',[['speed','Game speed',.25,2,.05],['fov','Field of view',40,100,1,'°'],['hud','Show the HUD','t'],['fly','Flying (left stick press, or '+kbList('fly')+')','t'],['inv','Invincible','t'],['infPep','Unlimited pepperoni','t'],['item','Always this item','i']]]];
function devGet(k){return k.startsWith('hz.')?DEV.hz[k.slice(3)]:DEV[k];}
function devSet(k,v){if(k.startsWith('hz.'))DEV.hz[k.slice(3)]=v;else DEV[k]=v;devSave();if(!NET.cfg&&player&&state==='race'){try{devKart(player,true);}catch(e){}}}
function devUI(){const sec=$('devSec'),b=$('devBody');if(!sec||!b)return;sec.hidden=!DEVU;if(!DEVU)return;
  const tog=(k,on)=>'<div class="seg seg2 mini" data-dt="'+k+'"><button type="button" data-v="1" aria-pressed="'+!!on+'">On</button><button type="button" data-v="0" aria-pressed="'+!on+'">Off</button></div>';
  let h='<div class="set-row"><div class="set-t"><b>Developer options</b><small>Every setting below; off puts the game back to normal without losing them.</small></div>'+tog('on',DEV.on)+'</div>';
  for(const [title,note,rows] of DEVS){h+='<p class="g-sub">'+title+'</p><p class="dev-note">'+note+'</p>';
    for(const r of rows){const [k,label,a,bb,st,unit]=r,v=devGet(k);
      if(a==='t')h+='<div class="set-row"><div class="set-t"><b>'+label+'</b></div>'+tog(k,v)+'</div>';
      else if(a==='i')h+='<div class="set-row"><div class="set-t"><b>'+label+'</b></div><select data-ds="'+k+'"><option value="">Normal boxes</option>'+ITEM_LIST.map(it=>'<option value="'+it+'"'+(v===it?' selected':'')+'>'+(HELP[it]?HELP[it][0]:it)+'</option>').join('')+'</select></div>';
      else h+='<div class="set-row"><div class="set-t"><b>'+label+'</b></div><div class="vol"><input type="range" data-dk="'+k+'" min="'+a+'" max="'+bb+'" step="'+st+'" value="'+v+'"><output>'+(unit==='°'?v+'°':unit==='+'?(v>0?'+':'')+v:'×'+v)+'</output></div></div>';}}
  h+='<p class="g-sub">Cheats</p><div class="set-row dev-btns"><button type="button" class="cta" data-dc="coins">+1000 coins</button><button type="button" class="cta" data-dc="shop">Unlock the style shop</button><button type="button" class="cta" data-dc="reset">Reset all</button></div>';
  b.innerHTML=h;
  b.querySelectorAll('[data-dt]').forEach(sg=>sg.querySelectorAll('button').forEach(bt=>bt.onclick=()=>{devSet(sg.dataset.dt,+bt.dataset.v);devUI();}));
  b.querySelectorAll('input[data-dk]').forEach(r=>r.oninput=()=>{const k=r.dataset.dk,v=+r.value,o=r.nextElementSibling,row=DEVS.flatMap(x=>x[2]).find(x=>x[0]===k)||[];devSet(k,v);o.textContent=row[5]==='°'?v+'°':row[5]==='+'?(v>0?'+':'')+v:'×'+v;});
  b.querySelectorAll('select[data-ds]').forEach(sl=>sl.onchange=()=>devSet(sl.dataset.ds,sl.value));
  b.querySelectorAll('[data-dc]').forEach(bt=>bt.onclick=()=>{const c=bt.dataset.dc;
    if(c==='coins'){const sv=sbSave();sv.c=(sv.c||0)+1000;sbKeep();achToast(null,'<b>+1000 coins</b> · '+sv.c+' now');}
    else if(c==='shop'){const o=ownedSet();for(const sl of ['tr','gl','hl','sm']){const [g,L]=STYLE[sl];L.forEach((_,i)=>o.add(g+i));}store.set('crust-own',JSON.stringify([...o]));achToast(null,'The whole style shop is yours');}
    else if(c==='reset'){DEV=Object.assign({},DEVDEF,{hz:Object.assign({},DEVDEF.hz)});devSave();devUI();}try{refreshGarage(false);}catch(e){}});}
setTimeout(()=>{try{devUI();}catch(e){}},0);
function applyCheat(code){""")
rep(".cheat-msg{margin:4px 0 0;font-size:13px;min-height:1.2em}",
    ".cheat-msg{margin:4px 0 0;font-size:13px;min-height:1.2em}\n.dev .g-sub{margin:16px 2px 4px}.dev-note{margin:0 2px 6px;font-size:12px;color:var(--muted)}.dev select{padding:8px 10px;border-radius:10px;background:rgba(14,7,4,.55);color:var(--cream);border:1px solid rgba(255,244,220,.2);font:600 14px inherit}\n"
    ".dev-btns{display:flex;flex-wrap:wrap;gap:8px}.dev-btns .cta{padding:9px 14px;font-size:13px}\nbody.devnohud .hud{display:none!important}")
rep("if(mi!==mapIdx||rev!==curRev||LATE_BUILD){mapIdx=mi;loadMap(mi,rev);}",
    "if(mi!==mapIdx||rev!==curRev||LATE_BUILD||hzSig()!==HZBUILT){mapIdx=mi;loadMap(mi,rev);}/* (patch 68: built with other hazards switched off: build it again) */")
rep("function buildHazards(def,R,ctx){HAZ={traffic:[],train:null,walk:[],pool:[],city:[]};",
    "let HZBUILT='';function hzSig(){const D=devR();return D&&D.hz?JSON.stringify(D.hz):'';}
function buildHazards(def,R,ctx){HZBUILT=hzSig();HAZ={traffic:[],train:null,walk:[],pool:[],city:[]};")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 68 applied')
