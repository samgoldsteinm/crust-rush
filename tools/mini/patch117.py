"""Patch 117 (web v250): split screen, part C: two pictures and two HUDs (as the PC, tools/mini/pc120.py).
- One canvas, two viewports (top: player 1, bottom: player 2). render() is cut in two: camStep (the chase camera) and render2
  (the rest of the frame). splitDraw draws the top half, then swaps player 2's camera in (pSwap: the cam state, camT, camSnap,
  shakeImp, finPunch, the camera's pose and zoom, the grade's boost streaks and motion blur) and draws the bottom half; each half
  has its own post pass (postRender/postLite on a half-height target). Shadows follow each camera (on Fast and phone presets the
  bottom half shares the top half's).
- The camera's aspect is the half's; the narrowest vertical view 52 -> 34 degrees in split screen (a half is very wide).
- Ambient occlusion is off in split screen.
- Kart detail: a kart's distance is to the nearer of the two cameras; player 2's kart is never hidden for being near player 1's camera.
- Player 2's HUD: a copy of player 1's (position, lap, time, speed gauge, drift charge, items, special, banners, wrong way) in the
  bottom half; touch controls hidden; the countdown and Go! on both; Balloon Battle's banners for player 2 on theirs.
Run once, after patch 116: py.cmd tools/mini/patch117.py"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'function splitDraw' not in s, 'already patched'


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:90])
    s = s.replace(a, b)


# CSS
rep("#gBack{margin-right:4px}",
    "#gBack{margin-right:4px}\n"
    "/* (patch 117) split screen: player 1's HUD on the top half, player 2's (a copy) on the bottom */\n"
    "body:not(.split) .hud.hud2{display:none!important}.hud.hud2,.hud.hud2 *{pointer-events:none!important}\n"
    "body.split #stage>.hud{bottom:50%}body.split #stage>.hud.hud2{top:50%;bottom:0}\n"
    "body.split #speedfx,body.split #hitfx,body.split #frostfx{bottom:50%}\n"
    "body.split #stage::after{content:'';position:absolute;left:0;right:0;top:calc(50% - 2px);height:4px;background:#1a0f0a;box-shadow:0 0 0 1px rgba(255,211,77,.35);pointer-events:none;z-index:3}\n"
    "body.split .tzone,body.split .brk,body.split #lookBtn,body.split #ihint,body.split #hitToast{display:none!important}\n"
    "body.split #banner{font-size:clamp(30px,8vmin,80px)}body.split #banner.sm,body.split #banner.md{font-size:clamp(22px,5.5vmin,52px)}")

# player 2's camera state
rep("const cam={a:0,look:new THREE.Vector3(),base:new THREE.Vector3(),roll:0,gp:0,gr:0,sx:0,oy:0,vy:0,pvz:0,pspd:0,F:new THREE.Vector3(),U:new THREE.Vector3(),P:new THREE.Vector3()};",
    "const cam={a:0,look:new THREE.Vector3(),base:new THREE.Vector3(),roll:0,gp:0,gr:0,sx:0,oy:0,vy:0,pvz:0,pspd:0,F:new THREE.Vector3(),U:new THREE.Vector3(),P:new THREE.Vector3()};\n"
    "/* (patch 117) split screen: player 2's chase camera (swapped into cam for the bottom half), where it was last frame, and its pose */\n"
    "const CAM2={a:0,look:new THREE.Vector3(),base:new THREE.Vector3(),roll:0,gp:0,gr:0,sx:0,oy:0,vy:0,pvz:0,pspd:0,F:new THREE.Vector3(),U:new THREE.Vector3(),P:new THREE.Vector3()};\n"
    "SPLIT.c2=new THREE.Vector3();SPLIT.pose={p:new THREE.Vector3(),q:new THREE.Quaternion(),u:new THREE.Vector3(0,1,0),fov:60};SPLIT.half=0;SPLIT.shk=0;SPLIT.fp=0;SPLIT.spd=0;SPLIT.mb=0;")
rep("cam.a=camT.ma;camSnap=true;SPLIT.snap=true;acc=0;",
    "cam.a=camT.ma;camSnap=true;SPLIT.snap=true;if(player2){CAM2.a=player2.ma;SPLIT.shk=0;SPLIT.fp=0;SPLIT.pose.u.set(0,1,0);SPLIT.pose.fov=camera.fov;splitHudReset();}acc=0;")

# render() in two
rep("  if(camT){cam.a=lerpA(cam.a,camT.rma,1-Math.exp(-5.5*dt));\n",
    "  {const a=SPLIT.on&&player2&&state!=='intro'?SPLIT.asp*2:SPLIT.asp;if(a&&Math.abs(camera.aspect-a)>1e-4){camera.aspect=a;camera.updateProjectionMatrix();}}/* (patch 117: a half's shape) */\n"
    "  camStep(time,dt);render2(time,dt);}\n"
    "/* (patch 117) the chase camera, on its own so split screen can run it for player 2 too */\n"
    "function camStep(time,dt){\n"
    "  if(camT){cam.a=lerpA(cam.a,camT.rma,1-Math.exp(-5.5*dt));\n")
rep("bk=(keys.look||PAD.look)!==", "bk=(camT===player2&&player2?PAD2.look:(keys.look||PAD.look))!==")
rep("const lb=(keys.look||PAD.look)&&state==='race'&&camT===player&&!(camT.rth>0);",
    "const lb=(camT===player2&&player2?PAD2.look:(keys.look||PAD.look))&&state==='race'&&(camT===player||camT===player2&&!!player2)&&!(camT.rth>0);")
rep("let vf=clamp(2*Math.atan(Math.tan(hf/2)/camera.aspect)*180/Math.PI,52,100);",
    "let vf=clamp(2*Math.atan(Math.tan(hf/2)/camera.aspect)*180/Math.PI,SPLIT.on&&player2?34:52,100);")
rep("finEnd();}/* (patch 110) */snapSun(camT.rx", "finEnd();}/* (patch 110) */if(!SPLIT.noSun)snapSun(camT.rx")
rep("  if(state==='intro')introCam(dt);if(sky)sky.position.copy(camera.position);rimL.position.set(camera.position.x-sunDir.x*400,camera.position.y+260,camera.position.z-sunDir.z*400);rimL.target.position.set(camera.position.x,camera.position.y-40,camera.position.z);\n",
    "}\n"
    "function camFollow(){if(sky)sky.position.copy(camera.position);rimL.position.set(camera.position.x-sunDir.x*400,camera.position.y+260,camera.position.z-sunDir.z*400);rimL.target.position.set(camera.position.x,camera.position.y-40,camera.position.z);}\n"
    "function render2(time,dt){\n"
    "  if(state==='intro')introCam(dt);camFollow();\n")
rep("const bh=renderer.getDrawingBufferSize(v2).y", "const bh=renderer.getDrawingBufferSize(v2).y/(SPLIT.on&&player2&&state!=='intro'?2:1)")
rep("  drawNow();\n}\n\n/* ================= HUD",
    "  if(SPLIT.on&&player2&&state!=='intro'){if(!LOWQF())renderer.shadowMap.needsUpdate=true;/* (each half moves the shadows to its own kart) */splitDraw(time,dt);}else drawNow();\n}\n"
    "/* (patch 117) split screen: player 2's camera in and out */\n"
    "const _spV=new THREE.Vector3(),_spQ=new THREE.Quaternion();\n"
    "function pSwap(){for(const key of new Set([...Object.keys(cam),...Object.keys(CAM2)])){const a=cam[key],b=CAM2[key];if(b===undefined)delete cam[key];else cam[key]=b;if(a===undefined)delete CAM2[key];else CAM2[key]=a;}\n"
    "  let t=camT;camT=SPLIT.camT2||player2;SPLIT.camT2=t;t=camSnap;camSnap=SPLIT.snap;SPLIT.snap=t;t=shakeImp;shakeImp=SPLIT.shk;SPLIT.shk=t;t=finPunch;finPunch=SPLIT.fp;SPLIT.fp=t;\n"
    "  const P=SPLIT.pose;_spV.copy(camera.position);camera.position.copy(P.p);P.p.copy(_spV);_spQ.copy(camera.quaternion);camera.quaternion.copy(P.q);P.q.copy(_spQ);_spV.copy(camera.up);camera.up.copy(P.u);P.u.copy(_spV);\n"
    "  t=camera.fov;camera.fov=P.fov;P.fov=t;camera.updateProjectionMatrix();\n"
    "  if(POST.M&&POST.M.final){const F=POST.M.final.uniforms;t=F.spd.value;F.spd.value=SPLIT.spd;SPLIT.spd=t;t=F.mb.value;F.mb.value=SPLIT.mb;SPLIT.mb=t;}}\n"
    "/* the top half, then player 2's camera and the bottom half; the whole canvas again after */\n"
    "function splitDraw(time,dt){const S=renderer.getSize(SPLIT.v||(SPLIT.v=new THREE.Vector2())),W=S.x,H=S.y,h=H/2;renderer.setScissorTest(true);\n"
    "  try{SPLIT.half=1;renderer.setViewport(0,h,W,h);renderer.setScissor(0,h,W,h);drawNow();\n"
    "    SPLIT.noSun=LOWQF();pSwap();\n"
    "    try{camStep(time,dt);camFollow();SPLIT.c2.copy(camera.position);renderer.shadowMap.needsUpdate=!SPLIT.noSun;SPLIT.half=2;renderer.setViewport(0,0,W,h);renderer.setScissor(0,0,W,h);drawNow();}\n"
    "    finally{pSwap();camFollow();}}\n"
    "  finally{SPLIT.half=0;SPLIT.noSun=false;renderer.setViewport(0,0,W,H);renderer.setScissor(0,0,W,H);renderer.setScissorTest(false);}}\n"
    "\n/* ================= HUD")
# the post passes draw a half
rep("function postLite(){postInit();const sz=renderer.getDrawingBufferSize(v2);",
    "function postLite(){postInit();const sz=renderer.getDrawingBufferSize(v2);if(SPLIT.half)sz.y=Math.max(1,Math.floor(sz.y/2));")
rep("function postRender(){postInit();const sz=renderer.getDrawingBufferSize(v2);",
    "function postRender(){postInit();const sz=renderer.getDrawingBufferSize(v2);if(SPLIT.half)sz.y=Math.max(1,Math.floor(sz.y/2));/* (patch 117: split screen's half) */")
rep("renderer.capabilities.isWebGL2&&CFG.ao!==false);", "renderer.capabilities.isWebGL2&&CFG.ao!==false&&!SPLIT.on);")
rep("renderer.setSize(w,h,false);camera.aspect=w/h;", "renderer.setSize(w,h,false);camera.aspect=w/h;SPLIT.asp=w/h;")
# kart detail: the nearer camera
rep(",far=k!==camT&&cd2>(m.isFar?LODF-20:LODF)**2;",
    ",far=k!==camT&&k!==player2&&(SPLIT.on&&player2?Math.min(cd2,(x-SPLIT.c2.x)**2+(y-SPLIT.c2.z)**2):cd2)>(m.isFar?LODF-20:LODF)**2;")
rep("{const nh=k!==camT&&cd2<196;", "{const nh=k!==camT&&k!==player2&&cd2<196;")

# player 2's HUD
rep("function hud(dt,time){",
    "/* (patch 117) split screen: player 2's HUD, a copy of player 1's in the bottom half */\n"
    "const H2={el:null};\n"
    "function hud2Make(){if(H2.el)return;const src=document.querySelector('#stage>.hud:not(.hud2)');if(!src)return;const c=src.cloneNode(true);c.classList.add('hud2');c.inert=true;c.setAttribute('aria-hidden','true');\n"
    "  c.querySelectorAll('.tzone,#tbProg,.hud-tr,#netQ,#tdTag,#tdBar,#specBar,.brk,#ihint,#lookBtn,#hitToast,#hudPB').forEach(e=>e.remove());\n"
    "  const q=id=>c.querySelector('#'+id);Object.assign(H2,{el:c,posNum:q('posNum'),posSuf:q('posSuf'),posOf:c.querySelector('.pos-of'),hudLap:q('hudLap'),hudTime:q('hudTime'),bars:[...c.querySelectorAll('#lapBars i')],spd:q('spd'),spdU:q('spdU'),gVal:q('gVal'),gCh:q('gCh'),gauge:q('gauge'),\n"
    "    banner:q('banner'),wrong:q('wrong'),itemBtn:q('itemBtn'),itemIcon:q('itemIcon'),itemBtn2:q('itemBtn2'),slot2:q('slot2'),abil:q('abilBtn')});H2.banner.textContent='';H2.wrong.hidden=true;src.after(c);splitHudReset();}\n"
    "function splitHudReset(){Object.assign(H2,{lapShown:1,pos:0,lap:'',ts:'',sv:-1,it:null,ga:null,ch:null,tn:null,bst:null,bT:0,wT:0});if(!H2.el)return;H2.banner.textContent='';H2.wrong.hidden=true;\n"
    "  if(player2&&H2.abil){const ri=player2.ri,A=ABIL[RACERS[ri].name.toLowerCase()];H2.abil.style.setProperty('--ac',A?A[2]:'#ffe066');H2.abil.style.backgroundImage=PORTRAITS[ri]?'url('+PORTRAITS[ri]+')':'';H2.abil._c=-1;H2.abil.classList.remove('ready');}}\n"
    "function showBanner2(txt,dur,sm){if(!SPLIT.on||!player2)return;hud2Make();const b=H2.banner;if(!b)return;b.textContent=txt;b.classList.toggle('sm',sm===true||sm==='sm');b.classList.toggle('md',sm==='md');b.classList.remove('pop');void b.offsetWidth;b.classList.add('pop');H2.bT=dur;}\n"
    "function hud2(dt,time){if(!SPLIT.on||!player2)return;hud2Make();const E=H2,k=player2;if(!E.el)return;\n"
    "  if(E.bT>0){E.bT-=dt;if(E.bT<=0)E.banner.textContent='';}\n"
    "  {const of=document.querySelector('#stage>.hud:not(.hud2) .pos-of');if(of&&E.posOf&&E.posOf.textContent!==of.textContent)E.posOf.textContent=of.textContent;const u=$('spdU');if(u&&E.spdU.textContent!==u.textContent)E.spdU.textContent=u.textContent;}\n"
    "  const pos=standCache.indexOf(k)+1;if(pos&&pos!==E.pos){E.pos=pos;E.posNum.textContent=pos;E.posSuf.textContent=suf(pos);}\n"
    "  const lap=clamp(Math.floor(Math.max(0,k.prog)/N)+1,1,LAPS),ls=lap+'/'+LAPS;if(ls!==E.lap){E.lap=ls;E.hudLap.textContent=ls;E.bars.forEach((b,i)=>b.classList.toggle('on',i<lap));}\n"
    "  if(state==='race'&&!BATTLE&&!SBX&&!k.finished&&lap>E.lapShown){E.lapShown=lap;showBanner2(lap===LAPS?'Final lap':'Lap '+lap,1.4,true);SFX.lap(lap===LAPS);}\n"
    "  const ts=fmt(k.finished?k.finishTime:raceTime);if(ts!==E.ts){E.ts=ts;E.hudTime.textContent=ts;}\n"
    "  const sv=Math.round(Math.max(0,k.speed)*(CFG.units==='kmh'?1.062:.66));if(sv!==E.sv){E.sv=sv;E.spd.textContent=sv;}\n"
    "  {const ga=Math.min(100,Math.max(0,k.speed)/(BASE_MAX*1.58)*100).toFixed(0);if(ga!==E.ga){E.ga=ga;E.gVal.style.strokeDasharray=ga+' 100';}}\n"
    "  {const chg=k.drift?Math.min(100,k.charge/2.6*100):0,tn=k.drift?(k.tier||0):0;if(Math.abs(chg-(E.ch||0))>.8||tn!==E.tn||(chg===0&&E.ch)){E.ch=chg;E.tn=tn;E.gCh.style.strokeDasharray=chg.toFixed(1)+' 100';E.gCh.style.stroke=['#fff4dc','#ffe066','#ff9a1f','#ff3b1a'][tn];}}\n"
    "  {const b=k.boost>0;if(b!==E.bst){E.bst=b;E.gauge.classList.toggle('boost',b);}}\n"
    "  {const rk=ITEM_KEYS[Math.floor(time*14)%ITEM_KEYS.length],rl=k.roll>0,H=k.held;let s1=k.item||(rl?rk:''),s2=k.item2||(rl&&(k.item||k.pend.length>1)?rk:'');\n"
    "    if(H){const free=k.item||(rl?rk:'');if(H.sl===1){s1=H.it;s2=free;}else{s2=H.it;s1=free;}}const ik=s1+'|'+s2+'|'+(H?H.sl:0);\n"
    "    if(ik!==E.it){E.it=ik;E.itemBtn.classList.toggle('rolling',rl);E.itemBtn.classList.toggle('has',!!s1&&!rl&&!(H&&H.sl===1));E.itemBtn.classList.toggle('held',!!H&&H.sl===1);\n"
    "      E.itemIcon.innerHTML=s1?SVG[s1]:'<span class=\"empty\"></span>';E.slot2.innerHTML=s2?SVG[s2]:'<span class=\"empty\"></span>';E.itemBtn2.classList.toggle('has',!!s2&&!rl&&!(H&&H.sl===2));E.itemBtn2.classList.toggle('held',!!H&&H.sl===2);}}\n"
    "  if(E.abil){const c=k.abC||0,rd=c>=.999;if(rd!==E.abil.classList.contains('ready')||Math.abs(c-(E.abil._c??-1))>.004){E.abil._c=c;E.abil.style.setProperty('--ab',(rd?100:c*100).toFixed(1)+'%');E.abil.classList.toggle('ready',rd);}}\n"
    "  {const tr=track[k.idx],back=state==='race'&&!k.sc&&!k.finished&&k.spin<=0&&k.speed>15&&(Math.cos(k.ma)*tr.tx+Math.sin(k.ma)*tr.ty)<-.4;E.wT=back&&!BATTLE&&!SBX?E.wT+dt:0;const wh=E.wT<.8;if(E.wrong.hidden!==wh)E.wrong.hidden=wh;}}\n"
    "function hud(dt,time){")
rep("if(!SB.warp)hud(dt,time);", "if(!SB.warp){hud(dt,time);try{hud2(dt,time);}catch(e){console.warn('hud2',e);}}")
rep("showBanner(String(n),.9,'md');", "showBanner(String(n),.9,'md');showBanner2(String(n),.9,'md');")
rep("showBanner('Go!',1,'md');", "showBanner('Go!',1,'md');showBanner2('Go!',1,'md');")
# Balloon Battle's banners for player 2
rep("if(k===player||near(k)>0)SFX.elim&&SFX.elim();showBanner(k===player?'Out! '+BB_DOT+' '+ord(alive):k.r.name+' is out',k===player?2.2:1.3,'sm');}",
    "if(k===player||near(k)>0)SFX.elim&&SFX.elim();showBanner(k===player?'Out! '+BB_DOT+' '+ord(alive):k.r.name+' is out',k===player?2.2:1.3,'sm');showBanner2(k===player2?'Out! '+BB_DOT+' '+ord(alive):k.r.name+' is out',k===player2?2.2:1.3,'sm');}")
rep("if(k===player&&!BB.skip)showBanner('Off the table!',1.4,'sm');", "if(k===player&&!BB.skip)showBanner('Off the table!',1.4,'sm');if(k===player2&&!BB.skip)showBanner2('Off the table!',1.4,'sm');")
rep("if(k===player&&k.bal===1&&!BB.skip)showBanner('Last balloon!',1.5,'sm');", "if(k===player&&k.bal===1&&!BB.skip)showBanner('Last balloon!',1.5,'sm');if(k===player2&&k.bal===1&&!BB.skip)showBanner2('Last balloon!',1.5,'sm');")
rep("showBanner(time?'Time!':r[0]===player?'Last one standing!':r[0].r.name+' wins!',2.4,'md');",
    "showBanner(time?'Time!':r[0]===player?'Last one standing!':r[0].r.name+' wins!',2.4,'md');showBanner2(time?'Time!':r[0]===player2?'Last one standing!':r[0].r.name+' wins!',2.4,'md');")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patch 117 applied')
