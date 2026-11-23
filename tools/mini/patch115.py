"""Patch 115 (web v250): split screen, part A: the menus. The owner: "Can we add split screen to the game" ... "Make it so that you
can assign each controller to each player that way you can use two Bluetooth controllers" ... "Let's add the ability to pick karts
for player 2". Matches the PC (tools/mini/pc120.py, pc122.py).
- Home: Players 1 / 2 (off line; Grand Prix, Single race, Balloon Battle; computers with controller support, not phones).
- With 2 players: driver -> kart -> PLAYER 2 driver -> player 2's kart -> track. Player 2's screens are the same driver and garage
  screens with player 2's driver and kart swapped in (splitMenuSwap: selected/playerBuild <-> SPLIT.sel/SPLIT.build); saved as
  crust-driver2, crust-build2. Player 1's driver is greyed out on player 2's list.
- Player 2's controller: "Choose controller", then press a button on it (padPoll: the first new press on any pad). Kept as its index
  and name (crust-p2pad). Esc or the button again cancels.
- SPLIT is read by the race (patch 116 on).
Run once, after patch 114: py.cmd tools/mini/patch115.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'patch 115' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# CSS
rep("#gBack{margin-right:4px}",
    "#gBack{margin-right:4px}\n"
    "/* (patch 115) split screen's menus */\n"
    ".p2pad{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin:0 0 10px}.p2pad span{font-weight:700;opacity:.88}.p2pad.wait span{color:#ffd34d}"
    ".card.taken{opacity:.32;pointer-events:none;filter:grayscale(.7)}")

# HTML: the Players choice and player 2's controller row
rep('<p class="seg-note" id="itmNote"></p></section>',
    '<p class="seg-note" id="itmNote"></p></section>\n'
    '        <section id="plySec" hidden><h2 class="label">Players</h2><div class="seg seg2" id="plySeg"><button type="button" data-n="1">1 player</button><button type="button" data-n="2">2 players</button></div><p class="seg-note" id="plyNote"></p></section>')
rep('<div class="st-body"><div id="roster" class="roster"></div>',
    '<div class="p2pad" id="p2Pad" hidden><button id="p2PadBtn" class="ghost" type="button">Choose controller</button><span id="p2PadSay"></span></div>\n'
    '      <div class="st-body"><div id="roster" class="roster"></div>')

# state
rep("let selected=(+(store.get('crust-driver')||0)||0)%8,",
    "/* (patch 115) split screen: n players chosen; player 2's driver, kart and controller (index + name); sw: player 2's are swapped into\n"
    "   selected/playerBuild while their menu screens are open (s1/b1 keep player 1's); on: this race is split (patch 116) */\n"
    "const SPLIT={n:store.get('crust-players')==='2'?2:1,sel:(+(store.get('crust-driver2')||1)||0)%8,build:(()=>{try{const b=JSON.parse(store.get('crust-build2')||'null');if(validBuild(b))return b;}catch(e){}return null;})(),\n"
    "  pid:(()=>{try{const v=JSON.parse(store.get('crust-p2pad')||'null');return v&&v.i>=0?v.i:-1;}catch(e){return -1;}})(),pidId:(()=>{try{const v=JSON.parse(store.get('crust-p2pad')||'null');return v&&v.id||'';}catch(e){return '';}})(),\n"
    "  wait:false,wpre:null,swallow:0,sw:false,s1:0,b1:null,on:false};\n"
    "let selected=(+(store.get('crust-driver')||0)||0)%8,")

# helpers, next to goStep; goStep swaps and relabels
rep("let menuStep='home';\nfunction goStep(st){menuStep=st;",
    "let menuStep='home';\n"
    "/* (patch 115) split screen: offered on computers with controller support, off line, in Grand Prix, Single race and Balloon Battle */\n"
    "function splitAble(){return !COARSE&&typeof navigator.getGamepads==='function';}\n"
    "function splitWant(){return SPLIT.n===2&&splitAble()&&!NET.role&&(mode==='gp'||mode==='single'||mode==='bb');}\n"
    "/* player 2's controller as it is now (null when it is not plugged in) */\n"
    "function p2Pad(){let gps;try{gps=navigator.getGamepads?navigator.getGamepads():[];}catch(e){return null;}if(SPLIT.pid<0)return null;\n"
    "  const g=gps&&gps[SPLIT.pid];if(g&&g.connected&&(!SPLIT.pidId||g.id===SPLIT.pidId))return g;for(const q of gps||[])if(q&&q.connected&&SPLIT.pidId&&q.id===SPLIT.pidId){SPLIT.pid=q.index;return q;}return g&&g.connected?g:null;}\n"
    "function padName(id){return String(id||'Controller').replace(/\\s*\\([^)]*(?:STANDARD GAMEPAD|Vendor:)[^)]*\\)\\s*/gi,' ').replace(/\\s+/g,' ').trim().slice(0,40)||'Controller';}\n"
    "function splitSay(){const e=$('p2PadSay'),w=$('p2Pad'),b=$('p2PadBtn');if(!e)return;const g=p2Pad();w.classList.toggle('wait',SPLIT.wait);\n"
    "  b.textContent=SPLIT.wait?'Cancel':g?'Change controller':'Choose controller';\n"
    "  e.textContent=SPLIT.wait?'Press any button on player 2\\'s controller':g?'Player 2: '+padName(g.id)+' (controller '+(g.index+1)+')':'Player 2 needs a controller: plug one in, then choose it';}\n"
    "function splitWait(on){SPLIT.wait=on;if(on){let gps=[];try{gps=navigator.getGamepads?navigator.getGamepads():[];}catch(e){}SPLIT.wpre={};for(const g of gps||[])if(g&&g.connected)SPLIT.wpre[g.index]=g.buttons.map(b=>!!b&&(b.pressed||b.value>.5));}splitSay();}\n"
    "/* while waiting: the first new button press on any controller makes it player 2's (and is not also a click) */\n"
    "function splitCatch(gps){for(const g of gps||[]){if(!g||!g.connected)continue;const was=SPLIT.wpre[g.index]||[];const now=g.buttons.map(b=>!!b&&(b.pressed||b.value>.5));\n"
    "  if(now.some((v,i)=>v&&!was[i])){SPLIT.pid=g.index;SPLIT.pidId=g.id;store.set('crust-p2pad',JSON.stringify({i:g.index,id:g.id}));SPLIT.wait=false;SPLIT.swallow=performance.now()+400;splitSay();refreshMenu();return;}SPLIT.wpre[g.index]=now;}}\n"
    "function splitMenuSwap(on){if(on&&!SPLIT.sw){SPLIT.s1=selected;SPLIT.b1=playerBuild;if(SPLIT.sel===selected)SPLIT.sel=(selected+1)%RACERS.length;\n"
    "    selected=SPLIT.sel;playerBuild=SPLIT.build&&validBuild(SPLIT.build)?SPLIT.build:JSON.parse(JSON.stringify(SPLIT.b1));SPLIT.sw=true;}\n"
    "  else if(!on&&SPLIT.sw){SPLIT.sel=selected;SPLIT.build=playerBuild;selected=SPLIT.s1;playerBuild=SPLIT.b1;SPLIT.sw=false;if(SPLIT.wait)splitWait(false);}}\n"
    "/* the driver and garage screens say whose they are */\n"
    "function splitHeads(st){const two=splitWant(),p2=st==='driver2'||st==='kart2',ds=document.querySelector('[data-step=\"driver\"]'),ts=document.querySelector('[data-step=\"track\"]');\n"
    "  if(ds){const sm=ds.querySelector('.st-t small'),h=ds.querySelector('.st-t h2'),bk=ds.querySelector('.st-back');if(sm)sm.textContent=p2?'Split screen':two?'Player 1 · Step 1 of 5':'Step 1 of 3';if(h)h.textContent=p2?'Player 2: choose a driver':'Choose your driver';\n"
    "    if(bk&&!bk.dataset.was){bk.dataset.back=p2?'kart':'home';bk.innerHTML=p2?'\\u2039 Kart':'\\u2039 Back';}const pp=$('p2Pad');if(pp)pp.hidden=!p2;if(p2)splitSay();}\n"
    "  if(ts){const bk=ts.querySelector('.st-back');if(bk){bk.dataset.back=two?'kart2':'kart';bk.innerHTML=two?'\\u2039 Player 2':'\\u2039 Kart';}}\n"
    "  const gs=document.querySelector('#garage .g-step');if(gs)gs.textContent=p2?'Player 2':two?'Player 1 · Step 2 of 5':'Step 2 of 3';\n"
    "  const gd=$('gDone');if(gd&&!NET.role&&!gd.dataset.was)gd.textContent=two&&!p2?'Player 2 \\u203a':'Choose track \\u203a';\n"
    "  const gb=$('gBack');if(gb)gb.textContent=p2?'\\u2039 Player 2':'\\u2039 Driver';}\n"
    "function goStep(st){splitMenuSwap(st==='driver2'||st==='kart2');splitHeads(st);if(st==='driver2')st='driver';if(st==='kart2')st='kart';/* (patch 115: player 2's screens are these two) */menuStep=st;")
rep("$('qualNote').textContent=QUAL[qKey].note;",
    "$('qualNote').textContent=QUAL[qKey].note;try{plyRefresh();}catch(e){}")
rep("  document.querySelectorAll('.card').forEach((x,j)=>x.setAttribute('aria-pressed',j===selected));",
    "  document.querySelectorAll('.card').forEach((x,j)=>{x.setAttribute('aria-pressed',j===selected);const t=SPLIT.sw&&j===SPLIT.s1;x.classList.toggle('taken',t);x.disabled=t;});")
# the Players choice
rep("document.querySelectorAll('#qual button').forEach(b=>b.onclick=()=>{qKey=b.dataset.q;",
    "function plyRefresh(){const sec=$('plySec');if(!sec)return;sec.hidden=!splitAble()||!!NET.role||!(mode==='gp'||mode==='single'||mode==='bb');\n"
    "  document.querySelectorAll('#plySeg button').forEach(b=>b.setAttribute('aria-pressed',String(+b.dataset.n===SPLIT.n)));const g=SPLIT.n===2?p2Pad():null;\n"
    "  $('plyNote').textContent=SPLIT.n===2?'Split screen on this computer. Player 2 drives with a controller'+(g?': '+padName(g.id):' (you choose it after your kart)')+'.':'Two players? Split screen on this computer, each with their own controller.';}\n"
    "document.querySelectorAll('#plySeg button').forEach(b=>b.onclick=()=>{SPLIT.n=+b.dataset.n===2?2:1;store.set('crust-players',String(SPLIT.n));refreshMenu();});\n"
    "addEventListener('keydown',ev=>{if(SPLIT.wait&&ev.code==='Escape'){ev.preventDefault();ev.stopImmediatePropagation();splitWait(false);}},true);\n"
    "document.querySelectorAll('#qual button').forEach(b=>b.onclick=()=>{qKey=b.dataset.q;")
# saves follow the swap
rep("    b.onclick=()=>{selected=i;store.set('crust-driver',i);refreshMenu();};r.appendChild(b);});",
    "    b.onclick=()=>{selected=i;store.set(SPLIT.sw?'crust-driver2':'crust-driver',i);refreshMenu();};r.appendChild(b);});")
rep("function saveBuild(){store.set('crust-build',JSON.stringify(playerBuild));}",
    "function saveBuild(){store.set(SPLIT.sw?'crust-build2':'crust-build',JSON.stringify(playerBuild));}")
# navigation
rep("if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}goStep('track');};$('garageBtn').onclick=()=>goStep('kart');$('gBack').onclick=()=>{if(gBig){setBig(false);return;}closeGarage();goStep('driver');};",
    "if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}goStep(!SPLIT.sw&&splitWant()?'driver2':'track');/* (patch 115) */};$('garageBtn').onclick=()=>goStep(SPLIT.sw?'kart2':'kart');$('gBack').onclick=()=>{if(gBig){setBig(false);return;}closeGarage();goStep(SPLIT.sw?'driver2':'driver');};\n"
    "  $('p2PadBtn').onclick=()=>splitWait(!SPLIT.wait);")
# the controller press
rep("function padPoll(){let gps;try{gps=navigator.getGamepads?navigator.getGamepads():[];}catch(e){return;}let gp=null;\n",
    "function padPoll(){let gps;try{gps=navigator.getGamepads?navigator.getGamepads():[];}catch(e){return;}let gp=null;\n"
    "  if(SPLIT.wait||performance.now()<SPLIT.swallow){/* (patch 115) choosing player 2's controller: that press is not a click */if(SPLIT.wait)splitCatch(gps);for(const g of gps||[])if(g&&g.connected&&(!gp||g.timestamp>gp.timestamp))gp=g;if(gp)PAD.prev=gp.buttons.map(b=>!!b&&(b.pressed||b.value>.5));return;}\n")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 115 applied')
