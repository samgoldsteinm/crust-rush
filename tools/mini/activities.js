/* ================= SANDBOX: THINGS TO DO (web v200; the owner's brief, section 5) =================
   "Add optional activities that start and finish in the world. Include a pizza delivery between two regions with a safe route and a riskier
   shortcut, a drift or jump challenge built around the existing handling, and hidden Easter eggs specific to individual maps. Show the
   objective and coin reward when an activity starts, offer a quick retry, and save unique discoveries."
   - Each activity starts at a marker in the world: a coloured ring on the road with its sign turning above it. Stop in the ring and a
     button offers it, with what to do and the coins it pays (tap; Enter; D-pad up), the same way as "Race here".
   - A delivery runs across places: the clock stands still in a tunnel (the game does), and fast travel, a race from a start line or
     leaving Sandbox ends it ("fast travel can't complete a delivery"). The pizza goes to the start line of the place named.
   - A challenge is done where it starts: drift for so many seconds, or be in the air for so many, before the clock runs out.
   - The end shows what happened and the coins, with Retry (Enter, or A on the pad) and Close (Esc, or B).
   - Saved with the coins (crust-sb): .a[id] = the best time or score and how many times it was done; .e[id] = an Easter egg found.
     The first time an activity is done it pays in full, after that half (so the coins stay worth something).
   Nothing here moves a kart: it reads the kart and pays coins. Off line only, like the rest of Sandbox. */
const SB_ACTS=[
  /* the delivery: Margherita's pizzeria to the start line of Sauce Spiral. Two ways: through Basil Boulevard, or the quicker way through the
     Oven, whose road runs past the flames */
  {id:'del_spiral',kind:'deliver',at:'margherita',f:.035,to:'spiral',T:210,coins:60,par:150,
    name:'Pizza delivery',goal:'Take the pizza to the start line of Sauce Spiral',tip:'Safe: through Basil Boulevard. Quicker: through the Oven Rush Raceway, past the flames.'},
  {id:'del_bedroom',kind:'deliver',at:'kitchen',f:.06,to:'bedroom',T:120,coins:40,par:75,
    name:'Snack delivery',goal:'Take the snack to the start line of Bedroom Blitz',tip:'Through the hall: the garage door is the long way round.'},
  {id:'drift_marg',kind:'drift',at:'margherita',f:.52,need:8,T:30,coins:30,name:'Drift challenge',goal:'Drift for 8 seconds in all, in 30 seconds',tip:'Out on the open pizza there is room for long drifts.'},
  {id:'drift_bay',kind:'drift',at:'bay',f:.3,need:10,T:35,coins:35,name:'Harbour drift',goal:'Drift for 10 seconds in all, in 35 seconds',tip:''},
  {id:'air_yard',kind:'air',at:'backyard',f:.12,need:5,T:45,coins:35,name:'Jump challenge',goal:'Be in the air for 5 seconds in all, in 45 seconds',tip:'The ramps on the track send you highest.'},
  {id:'air_spiral',kind:'air',at:'spiral',f:.5,need:4,T:45,coins:30,name:'Jump challenge',goal:'Be in the air for 4 seconds in all, in 45 seconds',tip:''}];
const SBA={marks:[],act:null,near:null,btn:null,bar:null,end:null,barT:0,padA:false};
function sbActSave(){const sv=sbSave();if(!sv.a||typeof sv.a!=='object')sv.a={};if(!sv.e||typeof sv.e!=='object')sv.e={};return sv;}
/* the marker: a ring on the road in the activity's colour and a sign turning above it (drawn on a canvas: no picture to load) */
function sbActIcon(kind){const c=cnv(256,256),g=c.getContext('2d');g.clearRect(0,0,256,256);const col=kind==='deliver'?'#e8542f':kind==='drift'?'#2fa6e8':'#7bd14a';
  g.fillStyle=col;g.beginPath();g.arc(128,128,118,0,6.2832);g.fill();g.lineWidth=14;g.strokeStyle='#fff4dc';g.stroke();g.fillStyle='#fff4dc';g.strokeStyle='#fff4dc';g.lineCap='round';g.lineJoin='round';
  if(kind==='deliver'){/* a pizza box with a slice on the lid */g.fillRect(58,96,140,74);g.fillStyle=col;g.fillRect(70,108,116,50);g.fillStyle='#fff4dc';g.beginPath();g.moveTo(92,150);g.lineTo(164,150);g.lineTo(128,112);g.closePath();g.fill();}
  else if(kind==='drift'){/* a swirl */g.lineWidth=16;g.beginPath();for(let a=0;a<11;a+=.1){const r=12+a*7.5;const x=128+Math.cos(a)*r,y=128+Math.sin(a)*r;a?g.lineTo(x,y):g.moveTo(x,y);}g.stroke();}
  else{/* a ramp and an arrow up */g.beginPath();g.moveTo(50,184);g.lineTo(150,184);g.lineTo(150,140);g.closePath();g.fill();g.lineWidth=16;g.beginPath();g.moveTo(150,118);g.quadraticCurveTo(178,70,206,96);g.stroke();g.beginPath();g.moveTo(196,72);g.lineTo(210,100);g.lineTo(180,104);g.stroke();}
  return c;}
function sbActMark(a){const j=Math.round(a.f*N)%N,p=track[j],e=(SB.kind==='toy'?0:groundAt(p.x,p.y))+(p.ey||0),G=new THREE.Group(),col=a.kind==='deliver'?'#e8542f':a.kind==='drift'?'#2fa6e8':'#7bd14a';
  const ring=new THREE.Mesh(new THREE.RingGeometry(13,16.5,40,1),new THREE.MeshBasicMaterial({color:col,side:THREE.DoubleSide,toneMapped:false,transparent:true,opacity:.9,depthWrite:false}));ring.rotation.x=-Math.PI/2;ring.position.y=.6;G.add(ring);
  const t=T2(sbActIcon(a.kind));t.userData.keepCanvas=true;const sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,toneMapped:false,depthWrite:false}));sp.scale.setScalar(14);sp.position.y=17;G.add(sp);
  G.position.set(p.x,e,p.y);G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);return {a,G,sp,x:p.x,z:p.y,y:e,j};}
/* a place has been armed (sbArm): its markers, and the delivery's drop-off if one is under way to here */
function sbActArm(){SBA.marks=[];SBA.near=null;for(const a of SB_ACTS)if(a.at===SB.regId)SBA.marks.push(sbActMark(a));sbActBtn(null);
  const A=SBA.act;if(A&&A.a.kind==='deliver'&&A.a.to===SB.regId&&SB.flag){const f=SB.flag,m=new THREE.Mesh(new THREE.RingGeometry(18,23,48,1),new THREE.MeshBasicMaterial({color:'#e8542f',side:THREE.DoubleSide,toneMapped:false,transparent:true,opacity:.85,depthWrite:false}));
    m.rotation.x=-Math.PI/2;m.position.set(f.x,f.y+.8,f.z);SB.grp.add(m);A.drop=m;}
  if(A&&A.a.kind!=='deliver'&&A.a.at!==SB.regId)sbActEnd('left');}
function sbActOff(){if(SBA.act&&!(SB.trav||SB.warp))sbActEnd('left',true);/* (a trip through a tunnel turns Sandbox off and on again: a delivery under way goes on) */SBA.marks=[];SBA.near=null;sbActBtn(null);if(SBA.bar)SBA.bar.hidden=true;}
/* the offer, at a marker */
function sbActBtn(m){let b=SBA.btn;if(!b){if(!m)return;b=SBA.btn=document.createElement('button');b.id='sbActB';b.type='button';
    b.style.cssText='position:absolute;left:50%;bottom:max(96px,calc(env(safe-area-inset-bottom) + 96px));transform:translateX(-50%);z-index:7;max-width:min(92vw,520px);font:800 15px/1.2 system-ui,sans-serif;color:#1b0f0b;background:linear-gradient(#ffd97a,#f5b62e);border:0;border-radius:14px;padding:10px 18px;box-shadow:0 4px 0 #9b6a10,0 8px 18px rgba(0,0,0,.4);cursor:pointer;text-align:left';
    b.innerHTML='<span id="sbActBT"></span><small style="display:block;font-weight:600;font-size:12px;opacity:.8;margin-top:2px" id="sbActBS"></small><small style="display:block;font-weight:600;font-size:11px;opacity:.65;margin-top:2px" id="sbActBK"></small>';
    b.onclick=e=>{e.preventDefault();if(SBA.near)sbActStart(SBA.near.a);};b.addEventListener('pointerdown',e=>e.stopPropagation());stage.appendChild(b);}
  if(m===SBA.shown)return;SBA.shown=m;b.hidden=!m;if(!m)return;const a=m.a,sv=sbActSave(),r=sv.a[a.id],first=!r||!r.n,pay=first?a.coins:Math.round(a.coins/2),touch=typeof COARSE!=='undefined'&&COARSE;
  document.getElementById('sbActBT').textContent=a.name+': '+pay+' coins'+(first?'':' (done before)');document.getElementById('sbActBS').textContent=a.goal+(a.kind==='deliver'?' within '+sbActClock(a.T):'')+'.';
  document.getElementById('sbActBK').textContent=(touch?'Tap to start':'Enter, or D-pad up, to start')+(r&&r.best?' · best '+(a.kind==='deliver'?sbActClock(r.best):r.best.toFixed(1)+' s'):'');}
function sbActClock(s){s=Math.max(0,Math.ceil(s));return Math.floor(s/60)+':'+String(s%60).padStart(2,'0');}
/* the objective bar at the top while one runs */
function sbActBar(){let e=SBA.bar;if(!e){e=SBA.bar=document.createElement('div');e.id='sbActBar';e.style.cssText='position:absolute;left:50%;top:max(12px,env(safe-area-inset-top));transform:translateX(-50%);z-index:6;max-width:min(94vw,560px);font:700 14px/1.25 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.7);border:2px solid rgba(255,244,220,.35);border-radius:14px;padding:7px 14px;pointer-events:none;text-shadow:0 1px 2px #000;text-align:center';stage.appendChild(e);}
  const A=SBA.act;if(!A||state!=='race'){e.hidden=true;return;}e.hidden=false;const a=A.a,left=a.T-A.t;
  e.innerHTML='<div style="font-size:11px;letter-spacing:.6px;opacity:.8;text-transform:uppercase">'+a.name+'</div><div>'+(a.kind==='deliver'?'To '+sbActPlace(a.to)+' · '+sbActClock(left)+' left':(a.kind==='drift'?'Drifting ':'In the air ')+A.v.toFixed(1)+' / '+a.need+' s · '+sbActClock(left)+' left')+'</div>'
    +'<div style="height:5px;border-radius:3px;background:rgba(255,244,220,.2);margin-top:5px;overflow:hidden"><div style="height:100%;width:'+(a.kind==='deliver'?Math.max(0,100*left/a.T):Math.min(100,100*A.v/a.need)).toFixed(1)+'%;background:'+(left<15?'#e8542f':'#ffd65a')+'"></div></div>';}
function sbActPlace(id){const m=MAPS.find(q=>q.id===id);return m?m.name:id;}
function sbActStart(a){if(SBA.act||state!=='race')return;sbActEndUi(null);const sv=sbActSave(),r=sv.a[a.id];SBA.act={a,t:0,v:0,first:!r||!r.n,from:SB.regId};SBA.near=null;sbActBtn(null);
  showBanner(a.name+': '+a.goal.toLowerCase(),3,'sm');if(a.tip)setTimeout(()=>{if(SBA.act&&SBA.act.a===a&&state==='race')showBanner(a.tip,3.2,'sm');},3100);try{SFX.ready();}catch(e){}SBA.barT=0;sbActBar();}
/* each step of driving (sbTick): markers, and the one under way */
function sbActTick(k,dt){const A=SBA.act;
  if(!A){let near=null;for(const m of SBA.marks){if((k.x-m.x)**2+(k.y-m.z)**2<26*26&&Math.abs((k.wy||0)-m.y)<12){near=m;break;}}SBA.near=near;sbActBtn(near);
    if(near){try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SBA.padUp)sbActStart(near.a);SBA.padUp=up;}catch(e){}}}
  else{const a=A.a;A.t+=dt;if(a.kind==='drift'){if(k.drift&&!k.air&&Math.abs(k.speed)>40)A.v+=dt;}else if(a.kind==='air'){if(k.air&&!k.loop)A.v+=dt;}
    if(a.kind!=='deliver'&&A.v>=a.need)sbActEnd('done');else if(a.kind==='deliver'&&SB.regId===a.to&&SB.flag&&(k.x-SB.flag.x)**2+(k.y-SB.flag.z)**2<30*30&&Math.abs((k.wy||0)-SB.flag.y)<12)sbActEnd('done');
    else if(A.t>=a.T)sbActEnd('time');}
  for(const m of SBA.marks)if(m.sp)m.sp.material.rotation=Math.sin(performance.now()/600)*.15;
  SBA.barT-=dt;if(SBA.barT<=0){SBA.barT=.2;sbActBar();}}
/* the end of one: 'done', 'time', 'cancel' (fast travel, a race), 'left' (left the place of a challenge, or Sandbox) */
function sbActEnd(why,quiet){const A=SBA.act;if(!A)return;SBA.act=null;if(A.drop){try{SB.grp.remove(A.drop);A.drop.geometry.dispose();A.drop.material.dispose();}catch(e){}}if(SBA.bar)SBA.bar.hidden=true;
  const a=A.a,sv=sbActSave();let pay=0,best=false;
  if(why==='done'){const r=sv.a[a.id]||(sv.a[a.id]={n:0});pay=A.first?a.coins:Math.round(a.coins/2);const sc=a.kind==='deliver'?A.t:A.t;/* (a challenge's score: how quickly it was done) */
    if(!r.best||sc<r.best){r.best=+sc.toFixed(1);best=r.n>0;}r.n++;if(a.kind==='deliver'&&A.t<=a.par)pay+=Math.round(a.coins/3);sv.c+=pay;sbKeep();SB.hudT=0;try{SFX.ready();}catch(e){}
    try{const k=player;burst(k.x,(k.wy||0)+8,k.y,30,['#ffd65a','#e8542f','#ffffff'],80,2.6);}catch(e){}}
  if(quiet)return;sbActEndUi({a,why,pay,t:A.t,best,par:a.kind==='deliver'&&why==='done'&&A.t<=a.par});}
function sbActEndUi(o){let e=SBA.end;if(!o){if(e)e.hidden=true;return;}if(!e){e=SBA.end=document.createElement('div');e.id='sbActEnd';e.style.cssText='position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:8;min-width:min(86vw,340px);max-width:92vw;font:700 15px/1.3 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.88);border:2px solid rgba(255,244,220,.45);border-radius:18px;padding:16px 18px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.5)';
    e.innerHTML='<div id="sbActET" style="font:900 22px/1.15 system-ui,sans-serif;margin-bottom:6px"></div><div id="sbActES" style="opacity:.9"></div><div style="display:flex;gap:10px;justify-content:center;margin-top:14px"><button type="button" id="sbActRetry" class="sbActBtn">Retry</button><button type="button" id="sbActClose" class="sbActBtn">Close</button></div>';
    const st=document.createElement('style');st.textContent='.sbActBtn{font:800 15px/1 system-ui,sans-serif;color:#1b0f0b;background:linear-gradient(#ffd97a,#f5b62e);border:0;border-radius:12px;padding:11px 20px;cursor:pointer;box-shadow:0 3px 0 #9b6a10}#sbActClose{background:linear-gradient(#efe6d6,#cbbfa9);box-shadow:0 3px 0 #7d715c}';document.head.appendChild(st);
    for(const b of e.querySelectorAll('button'))b.addEventListener('pointerdown',ev=>ev.stopPropagation());
    e.querySelector('#sbActRetry').onclick=ev=>{ev.preventDefault();sbActRetry();};e.querySelector('#sbActClose').onclick=ev=>{ev.preventDefault();sbActEndUi(null);};
    addEventListener('keydown',ev=>{if(!SBA.end||SBA.end.hidden||!SBX)return;if(ev.code==='Enter'){ev.preventDefault();sbActRetry();}else if(ev.code==='Escape'){ev.preventDefault();ev.stopPropagation();sbActEndUi(null);}},true);stage.appendChild(e);}
  SBA.last=o;e.hidden=false;const a=o.a;const T={done:a.kind==='deliver'?'Delivered!':'Challenge done!',time:'Out of time',cancel:'Delivery ended',left:'Challenge ended'}[o.why];
  e.querySelector('#sbActET').textContent=T;e.querySelector('#sbActES').innerHTML=o.why==='done'?('+'+o.pay+' coins'+(o.par?' (quick delivery bonus)':'')+' · '+sbActClock(o.t)+(o.best?' · a new best':'')):
    o.why==='cancel'?'Fast travel or a race ends a delivery: the pizza has to go by road.':o.why==='left'?'A challenge is done where it starts.':(a.kind==='deliver'?'The pizza went cold.':'So close: try again.');SBA.endT=performance.now();}
/* Retry: a challenge starts again where you are (if you are still in its place); a delivery takes you back to its marker by fast travel and starts again */
function sbActRetry(){const o=SBA.last;sbActEndUi(null);if(!o||state!=='race')return;const a=o.a;
  if(a.kind!=='deliver'&&SB.regId===a.at){sbActStart(a);return;}
  if(SB.regId===a.at){const m=SBA.marks.find(q=>q.a===a);if(m){sbActPut(m);sbActStart(a);return;}}
  SBA.retry=a;sbTravel({to:a.at,start:true});}
/* after a fast travel made by Retry: set the kart down on the marker, then start */
function sbActPut(m){const k=player,j=m.j,p=track[j];k.x=k.px=m.x;k.y=k.py=m.z;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.idx=j;k.speed=0;k.rx=k.x;k.ry=k.y;k.rma=k.ma;cam.a=k.ma;camSnap=true;}
function sbActArrived(){const a=SBA.retry;SBA.retry=null;if(!a||SB.regId!==a.at)return;const m=SBA.marks.find(q=>q.a===a);if(m)sbActPut(m);sbActStart(a);}
/* a controller on the end panel: A retries, B closes (read here: the panel is not one of the menus the pad's cursor walks) */
function sbActPad(){if(!SBA.end||SBA.end.hidden)return;try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];if(!gp)return;const a=!!(gp.buttons[0]&&gp.buttons[0].pressed),b=!!(gp.buttons[1]&&gp.buttons[1].pressed);
  if(performance.now()-(SBA.endT||0)>400){if(a&&!SBA.padA)sbActRetry();else if(b&&!SBA.padB)sbActEndUi(null);}SBA.padA=a;SBA.padB=b;}catch(e){}}
/* ---- Easter eggs: one hidden thing a place, in eight places (the brief: "hidden Easter eggs specific to individual maps") ----
   Each is a small model built here, in a spot off the racing line: on a pizza out on open ground that a kart can reach from the road (found
   the way the pepperoni coins' spots are, with another seed, and well away from them); in a room beside one of the hidden coins' spots,
   on clear floor; on a neon road at its far edge. Drive up to it: it hops, says what it is, pays 25 coins once and is saved (.e). The map
   does not show them. */
const SB_EGGS={margherita:{id:'cat',name:'a cat asleep in the sun'},bay:{id:'shell',name:'a seashell washed up on the crust'},frosty:{id:'snowman',name:'a very small snowman'},
  laser:{id:'robot',name:'a lost little robot',f:.62},bedroom:{id:'duck',name:'the rubber duck from the bath',near:'corner'},kitchen:{id:'meatball',name:'a meatball that got away',near:'fridge'},
  garage:{id:'wrench',name:'the wrench everyone was looking for',near:'shelf'},backyard:{id:'gnome',name:'a garden gnome, hiding',near:'far'}};
function sbEggModel(id){const G=new THREE.Group(),S=(c,o)=>new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.55},o||{})),add=(g,m,x,y,z,sx,sy,sz)=>{const o=new THREE.Mesh(g,m);o.position.set(x,y,z);if(sx)o.scale.set(sx,sy,sz);o.castShadow=true;G.add(o);return o;},sph=new THREE.SphereGeometry(1,24,16);
  if(id==='duck'){const y=S('#ffcf1f',{roughness:.22}),o=S('#ff7a1a',{roughness:.3});add(sph,y,0,4,0,6,4.4,5);add(sph,y,3.6,8.6,0,3.3,3.3,3.3);add(sph,o,6.6,8.3,0,1.8,.8,1.5);add(sph,y,-5,6,0,2,2.6,2.4);for(const s of [-1,1])add(sph,S('#111',{roughness:.2}),5.4,9.6,s*1.8,.45,.45,.45);}
  else if(id==='cat'){const f=S('#d98a3c',{roughness:.85}),w=S('#f4e4cc',{roughness:.85});add(sph,f,0,3.2,0,7,3.4,4.6);add(sph,f,6.2,4.2,1,3.3,3,3.2);const ear=new THREE.ConeGeometry(1.2,2.4,10);for(const s of [-1,1]){const e=add(ear,f,6.6,7,1+s*1.8);e.rotation.z=-.2;}add(sph,w,8.7,3.6,1,1.4,1.1,1.5);const t=add(new THREE.TorusGeometry(5,1,10,24,3.4),f,-2,1.4,-2.6);t.rotation.x=Math.PI/2;}
  else if(id==='shell'){const m=S('#f2c4a8',{roughness:.45});for(let i=0;i<11;i++){const r=add(new THREE.CylinderGeometry(.9,.2,9,8),m,0,0,0);r.position.set(Math.sin((i-5)*.27)*4.5,1.2,Math.cos((i-5)*.27)*4.5-3);r.rotation.set(Math.PI/2-.25,(i-5)*.27,0);}add(sph,m,0,1.2,-3.2,2.2,1.2,1.6);}
  else if(id==='snowman'){const s=S('#f7f9ff',{roughness:.9});add(sph,s,0,4,0,4,4,4);add(sph,s,0,10,0,3,3,3);add(sph,s,0,14.6,0,2.1,2.1,2.1);const n=add(new THREE.ConeGeometry(.5,3,10),S('#ff7a1a'),0,14.6,2.6);n.rotation.x=Math.PI/2;for(const x of [-.8,.8])add(sph,S('#111'),x,15.3,1.8,.32,.32,.32);add(new THREE.CylinderGeometry(2.3,2.3,.5,20),S('#222'),0,16.4,0);add(new THREE.CylinderGeometry(1.5,1.5,2.4,20),S('#222'),0,17.8,0);}
  else if(id==='robot'){const b=S('#9aa3ad',{metalness:.7,roughness:.35});add(new THREE.BoxGeometry(6,6,4.4),b,0,6,0);add(new THREE.BoxGeometry(4.6,3.6,3.6),b,0,11,0);for(const x of [-1.1,1.1])add(sph,S('#111',{emissive:'#39d0ff',emissiveIntensity:2.2}),x,11.3,1.85,.6,.6,.3);add(new THREE.CylinderGeometry(.18,.18,2.4,6),b,0,14,0);add(sph,S('#ff4b6e',{emissive:'#ff4b6e',emissiveIntensity:2}),0,15.3,0,.55,.55,.55);for(const x of [-1.6,1.6])add(new THREE.BoxGeometry(1.4,3,2),b,x,1.5,0);}
  else if(id==='meatball'){const m=S('#6e3420',{roughness:.95}),g=new THREE.IcosahedronGeometry(5,3),p=g.attributes.position;for(let i=0;i<p.count;i++){const k=1+.07*Math.sin(i*12.9898)*Math.cos(i*4.1);p.setXYZ(i,p.getX(i)*k,p.getY(i)*k,p.getZ(i)*k);}g.computeVertexNormals();add(g,m,0,5,0);for(let i=0;i<6;i++)add(sph,S('#3f8a2e'),Math.cos(i)*3.6,7.4+Math.sin(i*3)*1.2,Math.sin(i)*3.6,.9,.25,.6);}
  else if(id==='wrench'){const s=S('#c9ced4',{metalness:.9,roughness:.25});add(new THREE.BoxGeometry(16,.9,2.2),s,0,.6,0);for(const x of [-8.6,8.6]){const r=add(new THREE.TorusGeometry(2.1,.9,10,20,4.6),s,x,.6,0);r.rotation.set(Math.PI/2,0,x>0?-.75:2.4);}}
  else if(id==='gnome'){add(sph,S('#2f5fb0'),0,4,0,3.4,4,3.4);add(sph,S('#f1c7a0'),0,9,0,2.4,2.4,2.4);add(new THREE.ConeGeometry(2.6,7,18),S('#d6302a'),0,13.6,0);add(new THREE.ConeGeometry(2.3,4,16),S('#f4f4f0',{roughness:.9}),0,6.6,1.7).rotation.x=Math.PI;add(sph,S('#e88c7a'),0,8.6,2.3,.8,.8,.8);for(const x of [-1.6,1.6])add(new THREE.BoxGeometry(1.8,1.2,3),S('#4a2c18'),x,.6,.6);}
  G.traverse(o=>{o.userData.sunlit=true;});return G;}
/* where it goes in this place, or null */
function sbEggSpot(E){const R=SB.reg;
  if(SB.kind==='open'){const rnd=prng(hashStr(SB.regId)+977);for(let t=0;t<500;t++){const a=rnd()*6.28318,r=(.35+rnd()*.55)*SB.rim,x=Math.cos(a)*r,z=Math.sin(a)*r,g0=groundAt(x,z);if(sbBlocked(x,z,g0))continue;
      if(SB.coins.some(c=>c.rare&&(c.x-x)**2+(c.z-z)**2<300*300))continue;let bj=0,bd=1e18;for(let j=0;j<N;j+=4){const p=track[j],d=(p.x-x)**2+(p.y-z)**2;if(d<bd){bd=d;bj=j;}}const d=Math.sqrt(bd);if(d<WALLD+80)continue;
      const p=track[bj];let ok=true,pw=groundAt(p.x,p.y);for(let q=d-RW;q>=0&&ok;q-=10){const xx=x+(p.x-x)*q/d,zz=z+(p.y-z)*q/d;if(sbBlocked(xx,zz,pw)||pitAt(xx,zz)>1)ok=false;pw=groundAt(xx,zz);}if(ok)return [x,g0,z];}return null;}
  if(SB.kind==='road'){const j=Math.round((E.f||.5)*N)%N,p=track[j],s=-1,x=p.x+p.nx*(RW-9)*s,z=p.y+p.ny*(RW-9)*s;return [x,groundAt(x,z)+(p.ey||0),z];}
  const q=(R.rare||[]).find(r=>r[3]===E.near);if(!q)return null;const gx=R.room?SB_RX:(g=>(g+.75)*SB_M),gz=R.room?SB_RZ:(g=>-(g-3.5)*SB_M),x0=gx(q[0]),z0=gz(q[1]);
  const clear=(x,z)=>{const r=TOYW()+30;for(let j=0;j<N;j+=2){const p=track[j];if((p.x-x)**2+(p.y-z)**2<r*r)return false;}return true;};/* (never on or beside the track: hidden means off the racing line) */
  for(let i=0;i<32;i++){const a=i*.3927,d=24+Math.floor(i/16)*16,x=x0+Math.cos(a)*d,z=z0+Math.sin(a)*d,y=sbG(x,z,0);if(!sbBlocked(x,z,y)&&Math.abs(y)<3&&clear(x,z))return [x,y,z];}return null;}
function sbEggArm(){SBA.egg=null;const E=SB_EGGS[SB.regId];if(!E||!SB.grp)return;let s=null;try{s=sbEggSpot(E);}catch(e){console.warn('egg',e);}if(!s)return;const G=sbEggModel(E.id);G.position.set(s[0],s[1],s[2]);G.rotation.y=hashStr(E.id)%628/100;SB.grp.add(G);
  SBA.egg={E,G,x:s[0],y:s[1],z:s[2],hop:0,found:!!sbActSave().e[E.id]};}
function sbEggTick(k,dt){const g=SBA.egg;if(!g)return;if(g.hop>0){g.hop=Math.max(0,g.hop-dt);const h=Math.sin((1-g.hop/.8)*Math.PI);g.G.position.y=g.y+h*7;g.G.rotation.y+=dt*9;}
  if(g.found)return;if((k.x-g.x)**2+(k.y-g.z)**2<18*18&&Math.abs((k.wy||0)-g.y)<14){g.found=true;g.hop=.8;const sv=sbActSave();sv.e[g.E.id]=1;sv.c+=25;sbKeep();SB.hudT=0;
    const n=Object.keys(SB_EGGS).filter(r=>sv.e[SB_EGGS[r].id]).length;showBanner('Easter egg '+n+'/'+Object.keys(SB_EGGS).length+': '+g.E.name+' · +25',3.2,'sm');try{SFX.ready();}catch(e){}
    try{burst(g.x,g.y+8,g.z,26,['#ffd65a','#ffffff','#7bd14a'],70,2.4);}catch(e){}}}
