"""Patch 44 (web v207; nothing a race reads: online stays 114): usernames and the online leaderboard.
The owner, 2026-11-16: "add an online leaderboard for each map where you can see the top 20 fastest runs from any player that has played";
"each player should have to pick a username and they can change it in settings"; every finished race counts, off line too ("can offline
races still count toward the leaderboard that everyone can see on their game"); boards split "with rivals" and "alone".
The store is the owner's Supabase project (free tier). The SQL that made it is in docs/HANDOVER.md. Players never touch its tables:
- name_free(name), claim_name(token, name) (claims, or renames the holder of that token), whoami(token), submit_run(token, ...);
- the view best_runs: each player's best per map, class, solo; read with the publishable key (it is meant to be public).
The token is 40 random hex characters kept on the device (crust-lb-token): it is what owns the name. Settings > More > Username shows the
name, changes it, and shows the token as an "account code" that brings the name to another device (the PC exe too).
A run is queued on the device (crust-lb-q, at most 40) and sent when the board can be reached and a name is set. Counted: a finished race
(single, Grand Prix, on line) that the kart really finished, not Last Slice, Balloon Battle or Sandbox, not the TESTING autopilot.
Map key: the map id (plus its @recv when a track was changed, so old times do not mix with new); class: small/medium/large/reverse ->
easy/medium/hard/mirror; solo: no other kart on the grid.
Run once: py.cmd tools/mini/patch44.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 44' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# a finished run goes to the board
rep("const h=loadHist();h.unshift({m:MAPS[mapIdx].id,c:clsKey,t,p:player.place,d:Date.now(),dr:selected,pb});",
    "try{lbRun(t);}catch(e){console.warn('leaderboard',e);}/* (patch 44) */const h=loadHist();h.unshift({m:MAPS[mapIdx].id,c:clsKey,t,p:player.place,d:Date.now(),dr:selected,pb});")
# online rooms use the username
rep("function netName(){try{return (store.get('crust-netname')||'').slice(0,14)||RACERS[selected].name;}",
    "function netName(){try{return (lbName()||store.get('crust-netname')||'').slice(0,14)||RACERS[selected].name;}")
# the records screen: a track opens its world board
rep("return '<li><img alt=\"\" src=\"'+shotURL(m.id,'h')+'\"><span class=\"nm\">'+m.name+'</span>'",
    "return '<li class=\"lb-open\" data-m=\"'+i+'\" title=\"World leaderboard\"><img alt=\"\" src=\"'+shotURL(m.id,'h')+'\"><span class=\"nm\">'+m.name+'</span>'")
rep("'<span class=\"tm none\">—</span><span class=\"dt\">No time yet</span>')+'</li>';}).join('');",
    "'<span class=\"tm none\">—</span><span class=\"dt\">No time yet</span>')+'</li>';}).join('');$('recBest').querySelectorAll('li.lb-open').forEach(li=>li.onclick=()=>lbOpen(+li.dataset.m,recCls));")
rep("<section><h3 class=\"label\">Recent races</h3>",
    "<section><h3 class=\"label\">Recent races</h3><p class=\"lb-hint\">Tap a track for its world leaderboard.</p>")
# the Online settings: the username row
rep("    <section class=\"set-group\" data-cat=\"more\"><h3 class=\"label\">Online</h3>\n",
    "    <section class=\"set-group\" data-cat=\"more\"><h3 class=\"label\">Online</h3>\n      <div class=\"set-row\"><div class=\"set-t\"><b>Username</b><small id=\"lbSetNote\">Your name on the world leaderboards and in online rooms.</small></div><div class=\"lb-btns\"><button id=\"lbSetName\" class=\"ghost\" type=\"button\">Change</button><button id=\"lbSetCode\" class=\"ghost\" type=\"button\">Account code</button></div></div>\n")
CSS = r"""
/* (patch 44) the leaderboard and the username sheet */
.rec-best li.lb-open{cursor:pointer}.rec-best li.lb-open:hover{border-color:rgba(255,214,90,.55)}
.lb-hint{margin:-2px 0 4px;font-size:12px;color:rgba(255,244,220,.55)}
.lb-btns{display:flex;gap:6px;flex-wrap:wrap}
.lb-sheet{max-width:720px;width:100%}
.lb-sheet,.lb-name{background:linear-gradient(180deg,rgba(46,24,14,.97),rgba(28,14,8,.97));border:1px solid rgba(255,214,90,.22);border-radius:18px;padding:18px 20px;box-shadow:0 18px 50px rgba(0,0,0,.55)}
.lb-tools{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 10px}.lb-tools .seg{flex:1 1 260px}
.lb-list{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:5px}
.lb-list li{display:grid;grid-template-columns:40px minmax(0,1fr) auto;gap:10px;align-items:center;padding:7px 10px;border-radius:10px;background:rgba(255,244,220,.05)}
.lb-list li.me{background:rgba(255,214,90,.16);outline:1px solid rgba(255,214,90,.5)}
.lb-list .pl{font-family:var(--display);color:var(--cheese);font-size:18px}
.lb-list .nm{font-weight:800;font-size:14px;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lb-list .nm small{display:block;font-weight:500;font-size:11px;color:rgba(255,244,220,.6)}
.lb-list .tm{font-variant-numeric:tabular-nums;font-weight:800}
.lb-list .pf{font-size:9px;font-weight:800;margin-left:6px;padding:1px 5px;border-radius:5px;background:rgba(255,244,220,.15);vertical-align:2px}
.lb-list .empty{display:block;color:rgba(255,244,220,.6);text-align:center;padding:14px}
.lb-foot{margin-top:10px;font-size:13px;color:rgba(255,244,220,.7);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.lb-name{max-width:460px;width:100%}.lb-name p{margin:4px 0 10px;color:rgba(255,244,220,.75);font-size:14px}
.lb-name input{width:100%;box-sizing:border-box;font:inherit;font-size:18px;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,244,220,.25);background:rgba(0,0,0,.25);color:#fff4dc}
.lb-msg{min-height:20px;font-size:13px;margin:6px 0 10px}.lb-msg.ok{color:#8be08b}.lb-msg.bad{color:#ff8a7a}
.lb-row{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap}
.lb-name details{margin-top:14px;font-size:13px;color:rgba(255,244,220,.75)}.lb-name details input{font-size:14px;margin:8px 0}
"""
rep("#stage.cinema .hud-in{opacity:0;transition:opacity .3s}", "#stage.cinema .hud-in{opacity:0;transition:opacity .3s}" + CSS)
JS = r"""
/* ================= (patch 44) USERNAMES AND THE WORLD LEADERBOARD (the owner's Supabase project) ================= */
const LB={url:'https://ymlfwrwrewxxsazylprf.supabase.co',key:'sb_publishable_K_widd5Q0EyMhUm7JVuv_Q_FWXc0CQZ'};
const lbEsc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
const LB_CLS={small:'easy',medium:'medium',large:'hard',reverse:'mirror'},LB_RE=/^[A-Za-z0-9_ .-]{3,16}$/;
function lbToken(){let t='';try{t=store.get('crust-lb-token')||'';}catch(e){}if(t.length<32){const a=new Uint8Array(20);crypto.getRandomValues(a);t=Array.from(a,x=>x.toString(16).padStart(2,'0')).join('');try{store.set('crust-lb-token',t);}catch(e){}}return t;}
function lbName(){try{return store.get('crust-lb-name')||'';}catch(e){return '';}}
async function lbRpc(fn,body){const r=await fetch(LB.url+'/rest/v1/rpc/'+fn,{method:'POST',headers:{apikey:LB.key,'Content-Type':'application/json'},body:JSON.stringify(body)});const tx=await r.text();let j=null;try{j=tx?JSON.parse(tx):null;}catch(e){}if(!r.ok){const e=new Error((j&&j.message)||('HTTP '+r.status));e.server=true;throw e;}return j;}
async function lbBoard(map,cls,solo){const q='best_runs?select=name,driver,kart,platform,time_ms&map=eq.'+encodeURIComponent(map)+'&cls=eq.'+cls+'&solo=eq.'+(solo?'true':'false')+'&order=time_ms.asc,created_at.asc&limit=20';
  const r=await fetch(LB.url+'/rest/v1/'+q,{headers:{apikey:LB.key}});if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}
let LB_VER=null;function lbVer(){if(LB_VER!=null)return Promise.resolve(LB_VER);return fetch('version.json',{cache:'no-store'}).then(r=>r.json()).then(j=>LB_VER=String(j.build||'').replace('crust-rush-','').slice(0,16)).catch(()=>LB_VER='web');}
const lbMapKey=m=>(m.id+(m.recv?'@'+m.recv:'')).slice(0,24);
function lbQueue(){try{return JSON.parse(store.get('crust-lb-q')||'[]')||[];}catch(e){return [];}}
function lbSaveQ(q){try{store.set('crust-lb-q',JSON.stringify(q.slice(-40)));}catch(e){}}
/* a finished race: on the queue, then sent */
function lbRun(t){const m=MAPS[mapIdx];if(!player||!player.finished||player.est||player.auto||BATTLE||SBX||mode==='lss'||!(t>0)||!LB_CLS[clsKey]||m.battle)return;
  const q=lbQueue();q.push({map:lbMapKey(m),cls:LB_CLS[clsKey],ms:Math.round(t*1000),drv:RACERS[selected].name.slice(0,16),kart:(BODIES[playerBuild.b]||BODIES[0]).name.slice(0,32),solo:karts.length===1,at:Date.now()});lbSaveQ(q);lbFlush();}
let lbBusy=false;async function lbFlush(){if(lbBusy||!lbName())return;lbBusy=true;try{const ver=await lbVer();let q=lbQueue();while(q.length){const r=q[0];
      try{await lbRpc('submit_run',{p_token:lbToken(),p_map:r.map,p_cls:r.cls,p_time_ms:r.ms,p_driver:r.drv,p_kart:r.kart,p_platform:'web',p_ver:ver||'web',p_solo:!!r.solo});q.shift();lbSaveQ(q);}
      catch(e){if(e.server&&!/no player/.test(e.message)){q.shift();lbSaveQ(q);continue;}/* (a run the board refuses is dropped; a missing player or no connection waits) */break;}}}finally{lbBusy=false;}}
addEventListener('online',()=>lbFlush());
/* the username sheet: first time the menu is up, and from Settings */
function lbNameSheet(after){let ov=$('lbNameOv');if(!ov){ov=document.createElement('div');ov.id='lbNameOv';ov.className='overlay';ov.innerHTML='<div class="panel sheet lb-name"><header class="g-head"><h2 class="res-title">Pick a username</h2></header>'+
      '<p>Your name on the world leaderboards and in online rooms. 3 to 16 letters, numbers, spaces, _ . or -.</p><input id="lbNameIn" maxlength="16" autocomplete="off" spellcheck="false"><div id="lbNameMsg" class="lb-msg"></div>'+
      '<div class="lb-row"><button id="lbNameLater" class="ghost" type="button">Not now</button><button id="lbNameOk" class="cta" type="button">Save</button></div>'+
      '<details><summary>Already have a username on another device?</summary>Paste its account code (Settings &gt; More &gt; Username &gt; Account code there):<input id="lbCodeIn" autocomplete="off" spellcheck="false"><div class="lb-row"><button id="lbCodeOk" class="ghost" type="button">Use this code</button></div></details></div>';document.body.appendChild(ov);}
  const inp=$('lbNameIn'),msg=$('lbNameMsg'),say=(t,c)=>{msg.textContent=t;msg.className='lb-msg'+(c?' '+c:'');};let tmo=0,seq=0;inp.value=lbName();say('');
  inp.oninput=()=>{clearTimeout(tmo);const v=inp.value.trim();if(!v){say('');return;}if(!LB_RE.test(v)){say('3 to 16 letters, numbers, spaces, _ . or -','bad');return;}if(v.toLowerCase()===lbName().toLowerCase()){say('That is your name now','ok');return;}
    const my=++seq;say('Checking...');tmo=setTimeout(()=>lbRpc('name_free',{p_name:v}).then(ok=>{if(my===seq)say(ok?'Available':'Taken: try another',ok?'ok':'bad');}).catch(()=>{if(my===seq)say('Cannot reach the leaderboard right now','bad');}),350);};
  const close=()=>{ov.hidden=true;if(after)after();};
  $('lbNameLater').onclick=close;
  $('lbNameOk').onclick=async()=>{const v=inp.value.trim();if(!LB_RE.test(v)){say('3 to 16 letters, numbers, spaces, _ . or -','bad');return;}say('Saving...');
    try{const nm=await lbRpc('claim_name',{p_token:lbToken(),p_name:v});try{store.set('crust-lb-name',nm||v);}catch(e){}lbSetNote();say('Saved','ok');lbFlush();setTimeout(close,500);}
    catch(e){say(/taken/.test(e.message)?'Taken: try another':'Cannot reach the leaderboard right now. Try again later.','bad');}};
  $('lbCodeOk').onclick=async()=>{const c=$('lbCodeIn').value.trim().toLowerCase();if(!/^[0-9a-f]{32,64}$/.test(c)){say('That is not an account code','bad');return;}
    try{const nm=await lbRpc('whoami',{p_token:c});if(!nm){say('No username has that code','bad');return;}try{store.set('crust-lb-token',c);store.set('crust-lb-name',nm);}catch(e){}inp.value=nm;lbSetNote();say('Welcome back, '+nm,'ok');lbFlush();setTimeout(close,700);}
    catch(e){say('Cannot reach the leaderboard right now','bad');}};
  ov.hidden=false;setTimeout(()=>inp.focus(),50);}
function lbSetNote(){const e=$('lbSetNote');if(e)e.textContent=lbName()?'You are '+lbName()+' on the world leaderboards and in online rooms.':'Not picked yet: pick one to put your times on the world leaderboards.';}
/* a track's world board: the speed classes, with rivals or alone, the top 20 (each player's best) */
let lbSt={m:0,c:'medium',solo:false};
function lbOpen(mi,cls){lbSt={m:mi,c:cls||clsKey,solo:false};let ov=$('lbOv');if(!ov){ov=document.createElement('div');ov.id='lbOv';ov.className='overlay';ov.innerHTML='<div class="panel sheet lb-sheet"><header class="g-head"><h2 class="res-title" id="lbTitle">Leaderboard</h2><button id="lbDone" class="cta g-done" type="button">Done</button></header>'+
      '<div class="lb-tools"><div class="seg seg4" id="lbCls"></div><div class="seg seg2" id="lbSolo"><button data-s="0">With rivals</button><button data-s="1">Alone</button></div></div><ol id="lbList" class="lb-list"></ol><div class="lb-foot" id="lbFoot"></div></div>';document.body.appendChild(ov);
    $('lbDone').onclick=()=>{ov.hidden=true;};$('lbSolo').querySelectorAll('button').forEach(b=>b.onclick=()=>{lbSt.solo=b.dataset.s==='1';lbDraw();});}
  ov.hidden=false;ov.scrollTop=0;lbDraw();}
let lbSeq=0;function lbDraw(){const m=MAPS[lbSt.m];$('lbTitle').textContent=m.name;
  $('lbCls').innerHTML=Object.keys(CLASSES).map(k=>'<button data-c="'+k+'" aria-pressed="'+(k===lbSt.c)+'">'+CLASSES[k].label+'</button>').join('');$('lbCls').querySelectorAll('button').forEach(b=>b.onclick=()=>{lbSt.c=b.dataset.c;lbDraw();});
  $('lbSolo').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String((b.dataset.s==='1')===lbSt.solo)));
  const me=lbName();$('lbFoot').innerHTML=me?'You race as <b>'+lbEsc(me)+'</b>.':'<span>Pick a username to put your times here.</span><button class="ghost" type="button" id="lbPick">Pick a username</button>';if(!me)$('lbPick').onclick=()=>lbNameSheet(()=>lbDraw());
  const L=$('lbList'),my=++lbSeq;L.innerHTML='<li class="empty">Loading...</li>';
  lbBoard(lbMapKey(m),LB_CLS[lbSt.c],lbSt.solo).then(rows=>{if(my!==lbSeq)return;L.innerHTML=rows.length?rows.map((r,i)=>'<li'+(me&&r.name.toLowerCase()===me.toLowerCase()?' class="me"':'')+'><span class="pl">'+(i+1)+'</span><span class="nm">'+lbEsc(r.name)+'<span class="pf">'+(r.platform==='pc'?'PC':'WEB')+'</span><small>'+lbEsc(r.driver)+' \u00b7 '+lbEsc(r.kart)+'</small></span><span class="tm">'+fmt(r.time_ms/1000)+'</span></li>').join(''):'<li class="empty">No times yet. Be the first!</li>';})
    .catch(()=>{if(my===lbSeq)L.innerHTML='<li class="empty">Cannot reach the leaderboard right now.</li>';});}
addEventListener('cr-booted',()=>{lbSetNote();const n=$('lbSetName'),c=$('lbSetCode');if(n)n.onclick=()=>lbNameSheet();
  if(c)c.onclick=()=>{try{window.prompt('Your account code. Keep it private: it is what makes the username yours. Paste it on another device (Settings > More > Username) to use the same name there.',lbToken());}catch(e){}};
  setTimeout(()=>{let asked=false;try{asked=!!sessionStorage.getItem('crust-lb-asked');sessionStorage.setItem('crust-lb-asked','1');}catch(e){asked=!!window.__lbAsked;window.__lbAsked=1;}if(!lbName()&&!asked&&state==='menu')lbNameSheet();lbFlush();},2500);});
"""
rep("/* ================= ACHIEVEMENTS: lifetime goals that unlock the reward liveries ================= */",
    JS + "/* ================= ACHIEVEMENTS: lifetime goals that unlock the reward liveries ================= */")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 44 applied')
