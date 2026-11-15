"""Patch 35 (web v200): the controller's on-screen pointer and its scrolling are slower on a phone or tablet.
The owner, 2026-11-15 (playing on an iPhone with a controller): "make the onscreen mouse slower on mobile and make the scrolling slower too".
On a touch screen (COARSE) the pointer moves at 55% of its speed and every scroll it drives (the right stick, the arrow held at an edge)
at 50%. A desktop is unchanged. Nothing here moves a kart. Run once: py.cmd tools/mini/patch35.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'PAD_MOB' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function padCursor(gp,M,ax,ay,pr,edge,now){", "const PAD_MOB=()=>typeof COARSE!=='undefined'&&COARSE?.55:1,PAD_MOBS=()=>typeof COARSE!=='undefined'&&COARSE?.5:1;/* (patch 35: slower on a phone) */\nfunction padCursor(gp,M,ax,ay,pr,edge,now){")
rep("sp=(200+1300*f*f)*clamp(Math.min(W,H)/720,.7,1.6);", "sp=(200+1300*f*f)*clamp(Math.min(W,H)/720,.7,1.6)*PAD_MOB();")
rep("else vx+=((dr?1:0)-(dl?1:0))*430;vy+=((pr(M.DOWN)?1:0)-(pr(M.UP)?1:0))*430;", "else vx+=((dr?1:0)-(dl?1:0))*430*PAD_MOB();vy+=((pr(M.DOWN)?1:0)-(pr(M.UP)?1:0))*430*PAD_MOB();")
rep("const d=ry*Math.abs(ry)*1700*dt;", "const d=ry*Math.abs(ry)*1700*PAD_MOBS()*dt;")
rep("sx.scrollBy(rx*Math.abs(rx)*1700*dt,0);", "sx.scrollBy(rx*Math.abs(rx)*1700*PAD_MOBS()*dt,0);")
rep("pull=(d)=>(260+1100*clamp(d/z,0,1))*dt;", "pull=(d)=>(260+1100*clamp(d/z,0,1))*PAD_MOBS()*dt;")
# abilities in Sandbox (the owner, 2026-11-15: "make player abilities work in sandbox"). They were off in every free-driving mode with the
# battle's rules (BATTLE); Sandbox is one, but there nothing forbids them: the meter fills, the button shows (battle.js), and they act on
# your own kart (a boost, the shield, the mega shroom) or fly off with nobody to hit. On a controller Y is Sandbox's map (the owner's
# choice), so there the ability is the right stick's click (R3, standard pads); keys and the on-screen button as anywhere.
rep("function useAbility(k,back){if(BATTLE)return;", "function useAbility(k,back){if(BATTLE&&!SBX)return;")
rep("if(edge(M.Y)&&!(SPEC&&SPEC.on)){if(SBX)sbMap(true,'drive');else abilQueued=true;}", "if(edge(M.Y)&&!(SPEC&&SPEC.on)){if(SBX)sbMap(true,'drive');else abilQueued=true;}if(SBX&&gp.mapping==='standard'&&edge(11))abilQueued=true;")
# how many computer racers (the owner, 2026-11-15: "you can choose to turn cpus off or you can choose how many you want in the game. That way
# if a player wants to just practice they can or if two players want to 1v1 each other they can"). A stepper on the home panel, 0 to 7,
# kept as crust-cpus (7, the full grid, by default). cpuCount(): the menu's attract race always has seven; Last Slice and Balloon Battle at
# least one (they end with one driver left). Offline the rivals take the grid slots nearest the player's (slot 4), so a smaller grid is
# a closer one; online the host's count fills the slots the friends leave (netBuildCfg) and the guests race the list they are sent.
# NET_PROTO 112: an older build in a lobby would not expect a grid of fewer than eight.
rep('<p class="seg-note" id="clsNote"></p></section>', '<p class="seg-note" id="clsNote"></p></section>\n        <section><h2 class="label">Computer racers</h2><div class="seg cpu-step" id="cpuSeg"><button type="button" data-d="-1" aria-label="Fewer computer racers">&minus;</button><b id="cpuVal" aria-live="polite">7</b><button type="button" data-d="1" aria-label="More computer racers">+</button></div><p class="seg-note" id="cpuNote"></p></section>')
rep(".set-row .seg button{padding:8px 4px;font-size:14px}", ".set-row .seg button{padding:8px 4px;font-size:14px}\n.cpu-step{display:grid;grid-template-columns:52px 1fr 52px;align-items:center}.cpu-step b{text-align:center;font-size:20px;font-weight:900}.cpu-step button{font-size:22px;font-weight:900}")
rep("function resetRace(demo){", "let CPUS=(()=>{const v=parseInt(store.get('crust-cpus'),10);return isNaN(v)?7:clamp(v,0,7);})();\n/* how many computer racers this race has (patch 35) */\nfunction cpuCount(demo){if(demo)return 7;return (mode==='lss'||mode==='bb')?Math.max(1,CPUS):CPUS;}\nfunction cpuNote(){const n=cpuCount(false),m=(mode==='lss'||mode==='bb')&&CPUS===0;return (n===0?'None: drive the track on your own':n===1?'One rival: a one-on-one':n+' rivals'+(n===7?': a full grid':''))+(m?' (at least one here)':'')+(mode==='sb'?' \u00b7 for races from a start line':'')+(NET.role==='host'?' \u00b7 friends take seats first':'');}\nfunction resetRace(demo){")
rep("  else for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));else{const ri=others.shift();karts.push(makeKart(ri,s,false,diff,cpuBuilds[ri]));}}",
    "  else{/* the player in slot 4, the rivals in the slots nearest it (patch 35: fewer than seven is a smaller grid) */const nc=cpuCount(demo),near=[3,5,2,6,1,7,0].slice(0,nc).concat(demo?[4]:[]);for(let s=0;s<8;s++){if(!demo&&s===4)karts.push(makeKart(selected,s,true,diff,playerBuild));else if(near.includes(s)){const ri=others.shift();karts.push(makeKart(ri,s,false,diff,cpuBuilds[ri]));}}}")
rep("  for(let s=0;s<8;s++){if(taken.has(s))continue;const ri=others.shift()??(s%RACERS.length);ks.push({slot:s,ri,build:cpuBuilds[ri]||randomBuild(ri),who:-1});}",
    "  {let nc=cpuCount(false);/* the host's count of computer racers fills the seats the friends leave (patch 35) */for(const s of [3,5,2,6,1,7,0,4]){if(nc<=0)break;if(taken.has(s))continue;const ri=others.shift()??(s%RACERS.length);ks.push({slot:s,ri,build:cpuBuilds[ri]||randomBuild(ri),who:-1});taken.add(s);nc--;}}")
rep("document.querySelectorAll('#clsSeg button').forEach(b=>b.onclick=()=>{clsKey=b.dataset.c;store.set('crust-cls',clsKey);refreshMenu();});",
    "document.querySelectorAll('#clsSeg button').forEach(b=>b.onclick=()=>{clsKey=b.dataset.c;store.set('crust-cls',clsKey);refreshMenu();});document.querySelectorAll('#cpuSeg button').forEach(b=>b.onclick=()=>{CPUS=clamp(CPUS+(+b.dataset.d),0,7);store.set('crust-cpus',String(CPUS));refreshMenu();});")
rep("$('clsNote').textContent=CLASSES[clsKey].note;", "$('clsNote').textContent=CLASSES[clsKey].note;{const v=$('cpuVal');if(v)v.textContent=String(CPUS);const n=$('cpuNote');if(n)n.textContent=cpuNote();}")
rep("const NET_PROTO=111", "const NET_PROTO=112")
# hills in Sandbox (the owner: "there are a lot of hills and valleys off the track but you can't drive up any of them ... most cars should be
# able to climb a little and the steeper it gets the more the car struggles until it's too steep and it can't drive up it", cars with good
# off-road doing better). The engine pulls every kart back by the slope under it (sl*165 a second); at full strength that stops a kart on
# anything steeper than about 18 degrees. In Sandbox only, going uphill, it is scaled by sbGrav(k) (sandbox.js: the kart's off-road), and
# the steepest it can climb at all is set there too (sbClimb). Races are untouched: this is behind SBX, which is never on line.
rep("k.speed-=sl*165*dt;}", "k.speed-=sl*165*(SBX&&sl>0?sbGrav(k):1)*dt;}")
# the mechanic's shop in Sandbox's garage (sandbox.js sbShopOpen / sbShopDone): opened from there, the driver screen's back button and the
# garage's last button go back into Sandbox instead of to the menu and the track
rep("closeGarage();if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}goStep('track');};", "closeGarage();if(NET.role==='guest'){netSendPick(true);goStep('home');netShowLobby();return;}if(typeof sbShopDone==='function'&&sbShopDone())return;goStep('track');};")
rep("document.querySelectorAll('#menu .st-back').forEach(b=>b.onclick=()=>goStep(b.dataset.back));", "document.querySelectorAll('#menu .st-back').forEach(b=>b.onclick=()=>{if(b.dataset.back==='home'&&typeof sbShopDone==='function'&&sbShopDone())return;goStep(b.dataset.back);});")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
