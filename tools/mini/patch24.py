"""Patch 24 (web v191): a race from Sandbox, and back.
The owner, 2026-11-13: "In sand box mode if you drive up to the start line of a race you can initiate the race track to start a race, the
start lines of race tracks should have little visible markers for the player to see if they want to start a race." (the online half of that
request, the lobby with ready-up, is in docs/SANDBOX-PLAN.md: it needs friends in Sandbox first)
The marker, the prompt and the start are in tools/mini/sandbox.js (sbFlag, sbRaceBtn, sbRaceHere). The engine's part, here:
  - leaving a race that was started from Sandbox goes back to Sandbox, not to the menu (toMenu asks sbBack first);
  - the results screen's second button says so.
  - (by hand the same day) the engine's round outer limit, `if(d>RIM&&!SBX)`: a room's corners and the passages lie outside that circle.
Run once: py.cmd tools/mini/patch24.py   (then inject_mini.py)"""
p = 'D:/crust-rush/source/crust-rush.html'
s = open(p, encoding='utf-8', newline='').read()
assert 'sbBack()' not in s, 'already patched'


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)


rep("function toMenu(){sbOff();LAPS=3;", "function toMenu(){if(sbBack())return;sbOff();LAPS=3;")
rep("$('toMenuBtn').textContent=BATTLE?", "$('toMenuBtn').textContent=SB.back?'Back to Sandbox':BATTLE?")
open(p, 'w', encoding='utf-8', newline='').write(s)

p = 'D:/crust-rush/source/tools/mini/sandbox.js'
s = open(p, encoding='utf-8', newline='').read()
rep("/* ---- coins ---- */",
    r"""/* ---- a race from its start line ----
   The start line of the region's track carries a marker: a chequered ring on the road and a small chequered flag turning above it. Drive up
   to it and a button offers the race (tap it; Enter on a keyboard; D-pad up on a controller). The race is an ordinary single race on this
   track at the chosen speed class; when it is over, or left, you are back in Sandbox at the same start line. */
function sbFlag(){const p=track[0],e=p.ey||0,c=cnv(64,64),g=c.getContext('2d');for(let i=0;i<4;i++)for(let j=0;j<4;j++){g.fillStyle=(i+j)%2?'#141210':'#fbf6ea';g.fillRect(i*16,j*16,16,16);}
  const t1=T2(c,6,1),t2=T2(c,1.5,1),G=new THREE.Group();t1.userData.keepCanvas=t2.userData.keepCanvas=true;
  const ring=new THREE.Mesh(new THREE.RingGeometry(11.5,15.5,40,1),new THREE.MeshBasicMaterial({map:t1,side:THREE.DoubleSide,toneMapped:false}));{const uv=ring.geometry.attributes.uv,ps=ring.geometry.attributes.position;for(let i=0;i<uv.count;i++){const a=Math.atan2(ps.getY(i),ps.getX(i)),r=Math.hypot(ps.getX(i),ps.getY(i));uv.setXY(i,a/6.28318+.5,r>13?1:0);}}
  ring.rotation.x=-Math.PI/2;ring.position.y=.55;G.add(ring);
  const F=new THREE.Group(),pole=new THREE.Mesh(new THREE.CylinderGeometry(.45,.45,17,8),new THREE.MeshStandardMaterial({color:'#e9e4d8',roughness:.5,metalness:.3}));pole.position.y=8.5;F.add(pole);
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(10,6.6),new THREE.MeshBasicMaterial({map:t2,side:THREE.DoubleSide,toneMapped:false}));fl.position.set(5,13.6,0);F.add(fl);F.position.y=12;G.add(F);
  try{const sp=new THREE.Sprite(glowMat('#fff2c0'));sp.scale.setScalar(30);sp.position.y=22;G.add(sp);}catch(e){}
  G.position.set(p.x,e,p.y);G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);SB.flag={G,F,x:p.x,z:p.y,y:e};}
function sbRaceBtn(on){let b=SB.raceEl;if(!b){if(!on)return;b=SB.raceEl=document.createElement('button');b.id='sbRace';b.type='button';
    b.style.cssText='position:absolute;left:50%;bottom:max(96px,calc(env(safe-area-inset-bottom) + 96px));transform:translateX(-50%);z-index:7;font:800 15px/1.15 system-ui,sans-serif;color:#1b0f0b;background:linear-gradient(#ffd97a,#f5b62e);border:0;border-radius:14px;padding:10px 18px 10px 44px;box-shadow:0 4px 0 #9b6a10,0 8px 18px rgba(0,0,0,.4);cursor:pointer;white-space:nowrap;text-align:left';
    b.innerHTML='<i style="position:absolute;left:12px;top:50%;width:22px;height:22px;margin-top:-11px;border-radius:5px;background:conic-gradient(#141210 25%,#fbf6ea 0 50%,#141210 0 75%,#fbf6ea 0) 0 0/11px 11px"></i><span id="sbRaceT"></span><small style="display:block;font-weight:600;font-size:11px;opacity:.75" id="sbRaceS"></small>';
    b.onclick=e=>{e.preventDefault();sbRaceHere();};b.addEventListener('pointerdown',e=>e.stopPropagation());stage.appendChild(b);
    addEventListener('keydown',e=>{if(SBX&&SB.raceOn&&state==='race'&&e.code==='Enter'){e.preventDefault();sbRaceHere();}});}
  if(on===SB.raceOn)return;SB.raceOn=on;b.hidden=!on;if(on){const m=MAPS[mapIdx],touch=typeof COARSE!=='undefined'&&COARSE;document.getElementById('sbRaceT').textContent='Race here: '+m.name;document.getElementById('sbRaceS').textContent=CLASSES[clsKey].label+' \u00b7 single race'+(touch?' \u00b7 tap':' \u00b7 Enter, or D-pad up');}}
function sbRaceHere(){if(!SBX||SB.trav||state!=='race'||raceLoading)return;SB.back=SB.regId;sbRaceBtn(false);mode='single';goRace(mapIdx);}
/* leaving a race that began at a start line in Sandbox: back to Sandbox there (the engine's toMenu asks this first) */
function sbBack(){if(!SB.back)return false;const id=SB.back;SB.back=null;if(NET.cfg||NET.role)return false;const mi=MAPS.findIndex(m=>m.id===id);if(mi<0||!SB_REG[id])return false;mode='sb';results.hidden=true;pauseOv.hidden=true;goRace(mi);return true;}
/* ---- coins ---- */""")
rep("sbColumns(b);}sbHashTrack();sbCoins();sbGates();", "sbColumns(b);}sbHashTrack();sbCoins();sbGates();sbFlag();")
rep("function sbTick(dt){if(state!=='race')return;const k=player;if(!k)return;", "function sbTick(dt){if(state!=='race'){sbRaceBtn(false);return;}const k=player;if(!k)return;{const f=SB.flag,near=!!f&&!SB.trav&&(k.x-f.x)**2+(k.y-f.z)**2<46*46&&Math.abs((k.wy||0)-f.y)<10;sbRaceBtn(near);if(near){try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp)sbRaceHere();SB.padUp=up;}catch(e){}}}")
rep("function sbRender(time){sbDuctShow();if(!SB.grp)return;sbCam();const im=SB.im;", "function sbRender(time){sbDuctShow();if(!SB.grp)return;sbCam();if(SB.flag){SB.flag.F.rotation.y=time*1.6;SB.flag.F.position.y=12+Math.sin(time*2.2)*1.2;}const im=SB.im;")
rep("if(SB.el)SB.el.hidden=true;if(SB.duct&&!SB.trav)", "if(SB.el)SB.el.hidden=true;SB.flag=null;sbRaceBtn(false);if(SB.duct&&!SB.trav)")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('patched')
