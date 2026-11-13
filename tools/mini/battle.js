/* ================= BALLOON BATTLE =================
   A mode with no lap: karts drive anywhere in an arena, hit each other with items, and each hit pops one of the victim's
   balloons. Timed score battle: five balloons to start, a point for every balloon you pop, at none you come back with
   three and half your score, most points when the clock runs out wins. The plan and the reasons: docs/BALLOON-BATTLE-PLAN.md.
   BATTLE is the switch. A normal race never reads anything here. The engine's hooks into this file (patch19.py):
     stepKart   no track walls, kerbs or off-road slowing; the ground and the walls come from BB.shapes
     aiInput    the CPU drivers are battleAI
     spinOut    a hit that lands calls battleHit
     update0    battleTick runs the clock, the respawns and the finish
     startRace  battleStart puts the karts round the arena
   The arena is a height field made of a few shapes, in the karts' own coordinates (x east, z south: a kart's k.y is z):
     box  [x0,x1,z0,z1,h]   ramp [x0,x1,z0,z1,h0,h1,axis] (its top runs from h0 at the low x or z to h1)   cyl [x,z,r,h]
   One rule gives every wall: nothing drives up a step higher than BB_STEP. What you can see is what stops you, because the
   models are built to these same shapes. */
let BATTLE=false;
const BB={shapes:[],spawn:[],ramps:[],T:180,t:0,over:false,hudT:0,el:null,grp:null},BB_STEP=5.5,BB_R=6.5,BB_START=5,BB_BACK=3;
const BB_COL=['#e3271d','#1f6fd6','#f6c41f','#35a84a','#ff7ab8','#8a4fd6','#ff8a1f','#22b8c8'];
/* ---- the prep table: 760 x 520, a lip all round; bins along the north edge with gaps; a raised route (stacked pizza boxes, a
   board) along the south and east edges, up a propped pizza-box lid in the south-west and down a bread board in the north-east */
function bbArena(){const S=[],X=380,Z=260,H=42;
  /* the table stands in an alcove: tiled walls on its north, east and south sides (nothing gets over those); along the open west
     side, where the cook stands, only the table's raised edge: enough to stop a kart on its wheels, not one in the air */
  S.push({t:'box',x0:-X-8,x1:X+60,z0:-Z-60,z1:-Z,h:500,k:'wall'},{t:'box',x0:-X-8,x1:X+60,z0:Z,z1:Z+60,h:500,k:'wall'},{t:'box',x0:X,x1:X+60,z0:-Z,z1:Z,h:500,k:'wall'},{t:'box',x0:-X-8,x1:-X,z0:-Z,z1:Z,h:7,k:'rim'});
  for(let i=0;i<5;i++){const x0=-338+i*144;S.push({t:'box',x0,x1:x0+100,z0:-212,z1:-150,h:36,k:'bin',i});}
  S.push({t:'ramp',x0:-335,x1:-215,z0:136,z1:232,h0:0,h1:H,ax:'x',k:'lid'});
  S.push({t:'box',x0:-215,x1:232,z0:130,z1:260,h:H,k:'boxes'},{t:'box',x0:232,x1:380,z0:-58,z1:260,h:H,k:'board'});
  S.push({t:'ramp',x0:262,x1:352,z0:-170,z1:-58,h0:0,h1:H,ax:'z',k:'bread'});
  S.push({t:'cyl',x:70,z:-10,r:12,h:90,k:'mill'},{t:'box',x0:-170,x1:-50,z0:34,z1:52,h:17,k:'pin'},{t:'cyl',x:-262,z:-60,r:36,h:22,k:'plates'});
  return S;}
const BB_X0=-388,BB_FLOOR=-312;/* west of the table's edge there is nothing but the kitchen floor, 90 cm down */
function battleG(x,z){if(x<BB_X0)return BB_FLOOR;let h=0;for(const s of BB.shapes){let t=-1;if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z;if(dx*dx+dz*dz<=s.r*s.r)t=s.h;}
    else if(x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1)t=s.t==='box'?s.h:s.h0+(s.h1-s.h0)*(s.ax==='x'?(x-s.x0)/(s.x1-s.x0):(z-s.z0)/(s.z1-s.z0));if(t>h)h=t;}return h;}
/* is a kart's footprint (eight points round it) against something too high to climb from the height it is at? -> the way in, or null */
function bbTouch(x,z,wy,out){let nx=0,nz=0,n=0;for(let i=0;i<8;i++){const a=i*.785398,sx=Math.cos(a),sz=Math.sin(a);if(battleG(x+sx*BB_R,z+sz*BB_R)-wy>BB_STEP){nx+=sx;nz+=sz;n++;}}
  if(!n)return 0;const l=Math.hypot(nx,nz);if(l<1e-6){out.x=0;out.z=0;return 2;}out.x=nx/l;out.z=nz/l;return 1;}
const _bbN={x:0,z:0};
function battleWalls(k){const wy=k.wy||0;let r=bbTouch(k.x,k.y,wy,_bbN);
  if(!r){k.bpx=k.x;k.bpy=k.y;return;}
  if(r===2){if(k.bpx!=null){k.x=k.bpx;k.y=k.bpy;}k.speed*=.5;return;}/* walled in on every side: back to where it last stood free */
  const nx=_bbN.x,ny=_bbN.z;for(let n=0;n<16;n++){k.x-=nx*.7;k.y-=ny*.7;if(!bbTouch(k.x,k.y,wy,_bbN))break;}
  const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;
  if(dot>0){if(k===camT&&dot>.3)shake(.25);k.speed*=1-.22*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.5;}
    if(dot>.45&&k.wallT<=0){k.wallT=.35;if(k===player)SFX.bump(.7);sparkWall(k,nx,ny);}}
  if(!bbTouch(k.x,k.y,wy,_bbN)){k.bpx=k.x;k.bpy=k.y;}}
/* a thrown thing against the arena: true if it has just met a wall (and has been turned back off it) */
function battleProjWall(p,h){const g=battleG(p.x,p.y);if(g-(h||0)<=BB_STEP)return false;
  /* which way is the wall? try stepping back along each axis */const bx=p.x-p.vx*.02,by=p.y-p.vy*.02,fx=battleG(bx,p.y)-(h||0)<=BB_STEP,fy=battleG(p.x,by)-(h||0)<=BB_STEP;
  if(fx&&!fy){p.vx=-p.vx;p.x=bx;}else if(fy&&!fx){p.vy=-p.vy;p.y=by;}else{p.vx=-p.vx;p.vy=-p.vy;p.x=bx;p.y=by;}return true;}
/* ---- the round ---- */
function bbSpawnAt(k,i){const s=BB.spawn[i%BB.spawn.length];k.x=k.px=s[0];k.y=k.py=s[1];const a=Math.atan2(-s[1],-s[0]);k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=battleG(k.x,k.y);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.glide=false;k.onRamp=k.onGlide=false;
  k.drift=0;k.charge=0;k.boost=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;k.loop=null;k.sc=null;}
function battleStart(){BB.t=BB.T;BB.over=false;BB.hudT=0;karts.forEach((k,i)=>{k.bal=BB_START;k.bbS=0;k.bbOut=0;k.bbI=i;k.bbA={t:0,tx:0,tz:0,stuck:0,rev:0,fire:0};bbSpawnAt(k,i);});bbBalloons();if(camT){cam.a=camT.ma;camSnap=true;}bbHud(true);}
function battleHit(v,by){if(!BATTLE||BB.over||!(v.bal>0))return;v.bal--;bbPop(v);if(by&&by!==v){by.bbS=(by.bbS||0)+1;if(by===player){SFX.ring&&SFX.ring();showBanner('+1',.5,'sm');}}
  if(v.bal<=0){v.bbS=Math.floor((v.bbS||0)/2);v.bbOut=2.2;if(v===player)showBanner('All popped! Back with '+BB_BACK,1.6,'sm');}BB.hudT=0;}
function bbRank(){return karts.slice().sort((a,b)=>(b.bbS||0)-(a.bbS||0)||(b.bal||0)-(a.bal||0)||a.bbI-b.bbI);}
function battleTick(dt){if(state!=='race'||BB.over)return;BB.t-=dt;
  for(const k of karts){if(!(k.bbOut>0)&&(k.wy||0)<-70){/* over the edge: one balloon gone, nobody's point */if(k.bal>0){k.bal--;bbPop(k);}if(k.bal<=0)k.bbS=Math.floor((k.bbS||0)/2);k.bbOut=1.3;if(k===player)showBanner(k.bal>0?'Off the table!':'All popped! Back with '+BB_BACK,1.4,'sm');BB.hudT=0;}
    if(k.bbOut>0){k.bbOut-=dt;k.speed*=Math.pow(.02,dt);if(k.bbOut<=0){/* back in, well away from the others */let best=0,bd=-1;for(let i=0;i<BB.spawn.length;i++){const s=BB.spawn[i];let d=1e9;for(const o of karts)if(o!==k)d=Math.min(d,(o.x-s[0])**2+(o.y-s[1])**2);if(d>bd){bd=d;best=i;}}
        bbSpawnAt(k,best);if(!(k.bal>0))k.bal=BB_BACK;k.inv=3;k.bbOut=0;spawnRing(k.x,k.wy+.6,k.y,'#7fe8ff',40,.6);if(k===camT)camSnap=true;}}}
  if(BB.t<=0){BB.t=0;BB.over=true;const r=bbRank();r.forEach((k,i)=>{k.finished=true;k.place=i+1;k.finishTime=raceTime;k.auto=true;});finishCount=karts.length;showBanner('Time!',2.4,'md');SFX.finish();resultsAt=2.4;}
  BB.hudT-=dt;if(BB.hudT<=0){BB.hudT=.25;bbHud();}}
/* ---- the CPU drivers: fetch an item, hunt the nearest rival they can get at, shoot when lined up, feel their way round walls ---- */
function bbReach(k,x,z){return Math.abs(battleG(x,z)-(k.wy||0))<12;}
function battleAI(k,dt){const A=k.bbA||(k.bbA={t:0,tx:0,tz:0,stuck:0,rev:0,fire:0}),wy=k.wy||0,o={steer:0,drift:false,brake:false,mul:1,use:false,back:false,hold:false,holdSl:1,release:null};
  if(k.bbOut>0||BB.over)return o;A.t-=dt;
  /* the nearest rival on my level */let en=null,ed=1e9;for(const q of karts){if(q===k||q.bbOut>0||!(q.bal>0))continue;const d=Math.hypot(q.x-k.x,q.y-k.y);if(d<ed&&Math.abs((q.wy||0)-wy)<14){ed=d;en=q;}}
  if(A.t<=0){A.t=.45+((k.bbI*37+Math.floor(simTime*3))%7)*.07;let tx=null,tz=0;
    if(k.item&&en&&ed<330){tx=en.x+Math.cos(en.ma)*en.speed*.25;tz=en.y+Math.sin(en.ma)*en.speed*.25;}
    else{let bd=1e9;for(const b of boxes){if(b.r>0)continue;const d=Math.hypot(b.x-k.x,b.y-k.y)*(bbReach(k,b.x,b.y)?1:2.2);if(d<bd){bd=d;tx=b.x;tz=b.y;}}
      if(tx===null&&en){tx=en.x;tz=en.y;}if(tx===null){const s=BB.spawn[(k.bbI*3+Math.floor(simTime/4))%BB.spawn.length];tx=s[0]*.5;tz=s[1]*.5;}}
    /* a target on another level: make for the foot (or the top) of the nearer ramp first */
    if(!bbReach(k,tx,tz)){const up=battleG(tx,tz)>wy+6;let br=null,bd=1e9;for(const r of BB.ramps){const p=up?r.foot:r.top,d=Math.hypot(p[0]-k.x,p[1]-k.y);if(d<bd){bd=d;br=r;}}
      if(br){const a=up?br.foot:br.top,b=up?br.top:br.foot;if(bd<34){tx=b[0];tz=b[1];}else{tx=a[0];tz=a[1];}}}
    A.tx=tx;A.tz=tz;}
  let des=Math.atan2(A.tz-k.y,A.tx-k.x),d=angDiff(des,k.a);
  /* feelers: straight ahead and to each side; a wall ahead turns the kart toward the freer side */
  const feel=(a,r)=>battleG(k.x+Math.cos(k.a+a)*r,k.y+Math.sin(k.a+a)*r)-wy>BB_STEP,f0=feel(0,30)||feel(0,54),fl=feel(-.6,34),fr=feel(.6,34);
  if(f0)d=fl&&!fr?1.2:fr&&!fl?-1.2:(d>=0?1.2:-1.2);else if(fl)d+=.5;else if(fr)d-=.5;
  o.steer=clamp(d*2.2,-1,1);
  /* stuck against something: back off, turning the other way */
  if(Math.abs(k.speed)<14&&k.spin<=0)A.stuck+=dt;else A.stuck=Math.max(0,A.stuck-dt*2);if(A.stuck>.9){A.rev=.9;A.stuck=0;}
  /* going nowhere for four seconds, whatever the speedometer says (sliding along a wall, shunting back and forth): set down again on open table, nothing lost */
  A.pt=(A.pt||0)+dt;if(A.pt>=1){A.pt=0;if(A.px!=null&&Math.hypot(k.x-A.px,k.y-A.pz)<14&&k.spin<=0)A.jam=(A.jam||0)+1;else A.jam=0;A.px=k.x;A.pz=k.y;if(A.jam>=4){A.jam=0;A.px=null;k.bbOut=.01;return o;}}
  if(A.rev>0){A.rev-=dt;o.brake=true;o.steer=-o.steer;}
  /* use what it holds */
  A.fire-=dt;if(k.item&&A.fire<=0&&k.spin<=0&&!(k.roll>0)){const it=k.item;let go=false,back=false;
    if(en){const ang=Math.abs(angDiff(Math.atan2(en.y-k.y,en.x-k.x),k.a));if(it==='oil'||it==='flour'){if(ed<110&&ang>2.2){go=true;back=true;}else if(A.t<.1&&ed>260){go=true;back=true;}}
      else if(it==='chili'||it==='rush'){go=ed<300&&ang<.5;}else if(it==='garlic'){go=ed<200;}else go=ed<260&&ang<.22;}
    else if(it==='chili'||it==='rush'||it==='garlic')go=true;
    if(go){o.use=true;o.back=back;A.fire=.8+((k.bbI*13)%5)*.2;}}
  return o;}
/* ---- balloons: a bunch tied to the back of each kart, one bob apart; a popped one bursts ---- */
function bbBalloons(){if(BB.grp)scene.remove(BB.grp);BB.grp=new THREE.Group();scene.add(BB.grp);const g=new THREE.SphereGeometry(1.9,14,10);g.scale(1,1.22,1);const sg=new THREE.CylinderGeometry(.07,.07,1,4);sg.translate(0,.5,0);
  const sm=new THREE.MeshBasicMaterial({color:'#f4f1ea'});for(const k of karts){const c=BB_COL[k.bbI%8],m=new THREE.MeshStandardMaterial({color:c,roughness:.25,metalness:0,envMapIntensity:.9}),G=new THREE.Group();G.userData.b=[];
    for(let i=0;i<BB_START;i++){const b=new THREE.Mesh(g,m),s=new THREE.Mesh(sg,sm);b.castShadow=true;G.add(b);G.add(s);G.userData.b.push({b,s,ph:i*1.9+k.bbI});}k.bbG=G;BB.grp.add(G);}}
function bbPop(k){const y=(k.wy||0)+16;burst(k.x,y,k.y,22,[BB_COL[k.bbI%8],'#ffffff','#ffe066'],80,2.6);spawnRing(k.x,y,k.y,BB_COL[k.bbI%8],18,.3,false);if(near(k)>0&&SFX.bump)SFX.bump(near(k)*.8);}
function battleRender(time){if(!BATTLE||!BB.grp)return;for(const k of karts){const G=k.bbG;if(!G)continue;const m=k.m&&k.m.g;G.visible=!!m&&m.visible&&!(k.bbOut>0);if(!G.visible)continue;
    const px=m.position.x,py=m.position.y,pz=m.position.z,a=k.a,bx=px-Math.cos(a)*5,bz=pz-Math.sin(a)*5,n=G.userData.b.length;
    for(let i=0;i<n;i++){const q=G.userData.b[i],on=i<(k.bal||0);q.b.visible=q.s.visible=on;if(!on)continue;const sp=(i-(Math.min(k.bal,n)-1)/2),sw=Math.sin(time*2.1+q.ph)*.9,lag=Math.min(6,Math.abs(k.speed)*.03),
        x=bx-Math.cos(a)*lag+Math.cos(a+1.5708)*sp*3.0+sw*.4,z=bz-Math.sin(a)*lag+Math.sin(a+1.5708)*sp*3.0,y=py+14+Math.abs(sp)*-1.1+Math.sin(time*1.7+q.ph)*.5;
      q.b.position.set(x,y,z);q.s.position.set(bx,py+3.5,bz);q.s.lookAt(x,y-2.6,z);q.s.rotateX(Math.PI/2);q.s.scale.set(1,Math.hypot(x-bx,y-2.6-py-3.5,z-bz),1);}}}
/* ---- the scoreboard and the clock ---- */
function bbHud(make){let e=BB.el;if(!e){e=BB.el=document.createElement('div');e.id='bbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 13px/1.25 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.62);border-radius:12px;padding:8px 10px;min-width:150px;pointer-events:none;text-shadow:0 1px 2px #000';stage.appendChild(e);}
  e.hidden=!BATTLE||state==='menu';document.body.classList.toggle('battle',BATTLE);if(e.hidden)return;const t=Math.max(0,Math.ceil(BB.t)),mm=Math.floor(t/60),ss=('0'+t%60).slice(-2);
  let h='<div style="font-size:20px;letter-spacing:.5px;margin-bottom:4px">'+mm+':'+ss+'</div>';for(const k of bbRank()){const c=BB_COL[k.bbI%8],me=k===player,nm=(k.netName||(RACERS[k.ri]&&RACERS[k.ri].name)||'Racer');
    h+='<div style="display:flex;gap:6px;align-items:center;'+(me?'color:#ffe066':'')+(k.bbOut>0?';opacity:.5':'')+'"><span style="width:16px;text-align:right">'+(k.bbS||0)+'</span><span style="flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:92px">'+nm+'</span><span style="color:'+c+';letter-spacing:-1px">'+'●'.repeat(Math.max(0,k.bal||0))+'</span></div>';}
  e.innerHTML=h;}
/* ---- the arena as the game sees it: shapes, spawn places, ramps for the CPU drivers, item boxes ---- */
function battleSetup(def){BB.shapes=bbArena();BB.spawn=[[-300,-90],[300,60],[-120,90],[150,-110],[-300,60],[40,100],[300,-120],[-40,-110]];
  BB.ramps=[{foot:[-346,184],top:[-205,184]},{foot:[307,-184],top:[307,-48]}];
  for(const [x,z] of [[-90,-40],[150,60],[-10,-238],[-200,-238],[200,-238],[0,192],[306,120],[-320,-120]])boxes.push({x,y:z,r:0,sv:boxes.length*3,gy:battleG(x,z),dbl:false});}
/* on every map load: leaving the arena takes its balloons and its scoreboard away; the HUD's lap and place read-outs are hidden in a battle */
function battleLoad(){if(!document.getElementById('bbCss')){const st=document.createElement('style');st.id='bbCss';st.textContent='body.battle #posNum,body.battle #posSuf,body.battle #tbProg,body.battle #hudLap,body.battle #lapBars,body.battle #hudPB,body.battle #hudTime,body.battle #mini,body.battle #wrong,body.battle #abilBtn,body.battle .lapbox,body.battle .posbox{display:none!important}';document.head.appendChild(st);}
  document.body.classList.toggle('battle',BATTLE);if(!BATTLE){if(BB.grp){scene.remove(BB.grp);BB.grp=null;}if(BB.el)BB.el.hidden=true;BB.shapes=[];}}
/* ---- thrown things in the arena (the engine's hooks: patch20.py) ----
   p.bh is the level a thrown thing is on: it follows the ground down a drop and up a ramp, and anything higher than a step is a wall */
function bbProjWalls(p){if(p.bh==null)p.bh=p.owner?Math.max(0,p.owner.wy||0):Math.max(0,battleG(p.x,p.y));if(p.type==='lob'||p.type==='flour')return;/* those are in the air */
  const g=battleG(p.x,p.y);if(g<-100){p.t=0;return;}if(g-p.bh>BB_STEP){if(battleProjWall(p,p.bh)){burst(p.x,p.bh+6,p.y,8,['#ff5a2a','#ffe066','#ffffff'],50,2);if(++p.b>2)p.t=0;}}else p.bh=g;}
/* a homing one turns straight for its rival; a wall in the way stops it */
function bbHome(p,tg,dt,want,tr){let v=Math.hypot(p.vx,p.vy)||want;v+=(want-v)*Math.min(1,dt*3);const des=Math.atan2(tg.y-p.y,tg.x-p.x);let cur=Math.atan2(p.vy,p.vx);cur+=clamp(angDiff(des,cur),-tr*dt,tr*dt);
  p.vx=Math.cos(cur)*v;p.vy=Math.sin(cur)*v;p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.bh==null)p.bh=p.owner?Math.max(0,p.owner.wy||0):0;const g=battleG(p.x,p.y);if(g<-100||g-p.bh>BB_STEP)p.t=0;else p.bh=g;}
/* who a homing thing goes for: the nearest rival in front (or behind, thrown backwards), else the nearest of all */
function bbTarget(k,back){let best=null,bs=1e9;for(const o of karts){if(o===k||o.bbOut>0||!(o.bal>0))continue;const d=Math.hypot(o.x-k.x,o.y-k.y),a=Math.abs(angDiff(Math.atan2(o.y-k.y,o.x-k.x),k.a+(back?Math.PI:0))),sc=d*(a<.9?1:2.5)+(Math.abs((o.wy||0)-(k.wy||0))>14?400:0);if(sc<bs){bs=sc;best=o;}}return best;}
/* the pizza cutter's mark: whoever is winning (not the thrower) */
function bbLeader(k){for(const o of bbRank())if(o!==k&&!(o.bbOut>0))return o;return null;}
/* Balloon Battle is played off line for now: starting or joining a friends' race leaves the mode and its arena */
function bbNoNet(){if(mode!=='bb')return;mode='single';try{store.set('crust-mode',mode);}catch(e){}if(MAPS[mapIdx].battle){mapIdx=0;loadMap(0,false);resetRace(true);}try{refreshMenu();}catch(e){}}
/* what a battle's item boxes give: only the things that work with no track under them (thrown, dropped, or worn), and only those the player has left switched on.
   The others ride the lap (the cannon and the twister follow the road, the sauce and the swap go by race position) and would do nonsense here */
const BB_ITEMS=[['pepperoni',3],['trio',2],['dough',2],['oil',2],['flour',2],['chili',1.5],['garlic',1.5],['rush',1]];
function bbRoll(){const L=BB_ITEMS.filter(q=>itemOn(q[0]));if(!L.length)return 'pepperoni';let t=0;for(const q of L)t+=q[1];let r=Math.random()*t;for(const q of L){r-=q[1];if(r<=0)return q[0];}return L[0][0];}
