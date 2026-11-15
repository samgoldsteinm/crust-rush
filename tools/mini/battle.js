/* ================= BALLOON BATTLE =================
   A mode with no lap: karts drive anywhere in an arena, hit each other with items, and each hit pops one of the victim's
   balloons. The rules since 2026-11-14 (the owner: "you start with 5 then after those are popped you have 3 then after the 3 are popped
   you get 1 after that is popped you are eliminated"): three sets of balloons, 5 then 3 then 1 (BB_SETS); losing the last of a set takes
   the kart out for a moment and brings it back with the next set; losing the single balloon ELIMINATES it. A point for every balloon of
   a rival's you pop (points are never halved now). The round ends when one driver is left, or when the clock (a backstop) runs out.
   Final order: drivers still in first, by points, then sets and balloons left; then the eliminated, the last one out highest.
   The plan and the reasons: docs/BALLOON-BATTLE-PLAN.md.
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
const BB={shapes:[],spawn:[],ramps:[],T:300,t:0,over:false,skip:false,hudT:0,el:null,grp:null},BB_STEP=5.5,BB_R=6.5,BB_SETS=[5,3,1],BB_START=BB_SETS[0],BB_BACK=BB_SETS[1];/* (BB_START and BB_BACK are kept for whatever still reads them: the sets are BB_SETS) */
const BB_COL=['#e3271d','#1f6fd6','#f6c41f','#35a84a','#ff7ab8','#8a4fd6','#ff8a1f','#22b8c8'];
/* ---- the prep table: 1100 x 760 (it was 760 x 520 until 2026-11-14: the owner, "make the map bigger" and "add another higher up section
   or make the higher up section bigger"), the kitchen's tiled walls on three sides and the open west edge with only the table's raised lip.
   Five ingredient pans along the north wall with gaps and a lane behind them, open at both ends.
   THE LONG RAISED ROUTE, 42 up: a torn-off pizza-box lid in the south-west leads up onto five stacks of pizza boxes along the south wall;
   from their east end a baking sheet leads up again to THE TOP, 84 up: three stacked dough trays in the south-east corner; down from it a
   wedge of hard cheese, rind up, to the butcher's block along the east wall (42), and off its north end down a bread board to the table.
   THE ISLAND, 42 up, west of the middle: a cutting board on two crates of tomatoes, a baking sheet down its east side and a bread board
   down its south side; its north and west sides are open edges.
   Each ramp is exactly as wide as the ledge it serves (beside a narrower one was a pocket a kart got stuck in: the owner's play-test of
   2026-11-13), no ramp's foot runs into anything, and no two solid things stand closer than 40 unless they touch.
   On the open floor: a pepper mill, a rolling pin, a stack of plates, two big cans of tomatoes, a bag of flour.
   tools/blender/battle.py draws exactly these shapes: change both together. */
const BB_X=550,BB_Z=380;
function bbArena(){const S=[],X=BB_X,Z=BB_Z,H=42,H2=84;
  /* the table stands in an alcove: tiled walls on its north, east and south sides (nothing gets over those); along the open west
     side, where the cook stands, only the table's raised edge: enough to stop a kart on its wheels, not one in the air */
  S.push({t:'box',x0:-X-8,x1:X+60,z0:-Z-60,z1:-Z,h:500,k:'wall'},{t:'box',x0:-X-8,x1:X+60,z0:Z,z1:Z+60,h:500,k:'wall'},{t:'box',x0:X,x1:X+60,z0:-Z,z1:Z,h:500,k:'wall'},{t:'box',x0:-X-8,x1:-X,z0:-Z,z1:Z,h:7,k:'rim'});
  for(let i=0;i<5;i++){const x0=-364+i*144;S.push({t:'box',x0,x1:x0+100,z0:-332,z1:-270,h:36,k:'bin',i});}/* (none in the north-west corner: the lane behind the pans opens onto the west side there, it is no dead end) */
  /* the long raised route: lid, box stacks, baking sheet, the top, cheese wedge, block, bread board */
  S.push({t:'ramp',x0:-500,x1:-360,z0:240,z1:380,h0:0,h1:H,ax:'x',k:'lid'},{t:'box',x0:-360,x1:250,z0:240,z1:380,h:H,k:'boxes'});
  S.push({t:'ramp',x0:250,x1:380,z0:240,z1:380,h0:H,h1:H2,ax:'x',k:'sheet'},{t:'box',x0:380,x1:550,z0:240,z1:380,h:H2,k:'trays'},{t:'ramp',x0:380,x1:550,z0:110,z1:240,h0:H,h1:H2,ax:'z',k:'wedge'});
  S.push({t:'box',x0:380,x1:550,z0:-100,z1:110,h:H,k:'board'},{t:'ramp',x0:380,x1:550,z0:-230,z1:-100,h0:0,h1:H,ax:'z',k:'bread'});
  /* the island: its ramps run DOWN from it (h0 is the height at the low x or z) */
  S.push({t:'box',x0:-420,x1:-200,z0:-170,z1:-10,h:H,k:'isle'},{t:'ramp',x0:-200,x1:-70,z0:-170,z1:-10,h0:H,h1:0,ax:'x',k:'isleE'},{t:'ramp',x0:-420,x1:-200,z0:-10,z1:120,h0:H,h1:0,ax:'z',k:'isleS'});
  /* on the floor */
  S.push({t:'cyl',x:200,z:10,r:12,h:90,k:'mill'},{t:'box',x0:40,x1:160,z0:110,z1:128,h:17,k:'pin'},{t:'box',x0:7,x1:40,z0:114.5,z1:123.5,h:12.5,k:'pin'},{t:'box',x0:160,x1:193,z0:114.5,z1:123.5,h:12.5,k:'pin'},{t:'cyl',x:20,z:-160,r:36,h:22,k:'plates'});
  S.push({t:'cyl',x:-30,z:50,r:27,h:61,k:'can'},{t:'cyl',x:290,z:150,r:27,h:61,k:'can'},{t:'box',x0:230,x1:300,z0:-190,z1:-140,h:40,k:'sack'});
  return S;}
const BB_X0=-BB_X-8,BB_FLOOR=-312;/* west of the table's edge there is nothing but the kitchen floor, 90 cm down */
function battleG(x,z,wy){if(SBX)return sbG(x,z,wy);if(x<BB_X0)return BB_FLOOR;let h=0;for(const s of BB.shapes){let t=-1;if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z;if(dx*dx+dz*dz<=s.r*s.r)t=s.h;}
    else if(x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1)t=s.t==='box'?s.h:s.h0+(s.h1-s.h0)*(s.ax==='x'?(x-s.x0)/(s.x1-s.x0):(z-s.z0)/(s.z1-s.z0));if(t>h)h=t;}return h;}
/* is a kart's footprint (eight points round it) against something too high to climb from the height it is at? -> the way in, or null */
function bbTouch(x,z,wy,out){let nx=0,nz=0,n=0;for(let i=0;i<8;i++){const a=i*.785398,sx=Math.cos(a),sz=Math.sin(a);if(battleG(x+sx*BB_R,z+sz*BB_R)-wy>BB_STEP){nx+=sx;nz+=sz;n++;}}
  if(!n)return 0;const l=Math.hypot(nx,nz);if(l<1e-6){out.x=0;out.z=0;return 2;}out.x=nx/l;out.z=nz/l;return 1;}
const _bbN={x:0,z:0};
function battleWalls(k){if(SBX)return sbWalls(k);const wy=k.wy||0;let r=bbTouch(k.x,k.y,wy,_bbN);
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
function bbSpawnAt(k,i){const s=BB.spawn[i%BB.spawn.length];k.x=k.px=s[0];k.y=k.py=s[1];const a=s.length>2?s[2]:Math.atan2(-s[1],-s[0]);k.a=k.ma=k.pa=k.pma=a;k.speed=0;k.wy=k.pwy=k.lastG=battleG(k.x,k.y);k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.glide=false;k.onRamp=k.onGlide=false;
  k.drift=0;k.charge=0;k.boost=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;k.loop=null;k.sc=null;}
function battleStart(){if(SBX)return sbStart();BB.left=karts.length;BB.t=BB.T;BB.over=false;BB.skip=false;BB.hudT=0;karts.forEach((k,i)=>{k.bbL=0;k.bal=BB_SETS[0];k.bbS=0;k.bbOut=0;k.bbDead=false;k.bbPlace=0;k.bbI=i;k.bbA={t:0,tx:0,tz:0,stuck:0,rev:0,fire:0};bbSpawnAt(k,i);});bbBalloons();if(camT){cam.a=camT.ma;camSnap=true;}bbSpecBtn(false);bbHud(true);}
/* a hit that landed: one balloon of the victim's gone, a point to whoever threw it */
function battleHit(v,by){if(SBX||!BATTLE||BB.over||v.bbDead||!(v.bal>0))return;v.bal--;bbPop(v);if(by&&by!==v){by.bbS=(by.bbS||0)+1;if(by===player&&!BB.skip){SFX.ring&&SFX.ring();showBanner('+1',.5,'sm');}}
  if(v.bal<=0)bbSetLost(v,2.2);BB.hudT=0;}
/* the last balloon of a set is gone: out for a moment and back with the next set, or, if that was the single balloon, out for good */
function bbSetLost(k,out){if((k.bbL||0)>=BB_SETS.length-1){bbElim(k);return;}k.bbL=(k.bbL||0)+1;k.bbOut=out;if(k===player&&!BB.skip)showBanner('All popped! Back with '+BB_SETS[k.bbL],1.6,'sm');}
/* eliminated: a bigger pop; the kart is hidden and parked far off the table (as Last Slice Standing does), it is nobody's target and takes
   nothing; its place is the number of drivers that were still in. The player then watches the others (the engine's spectating). */
function bbElim(k){const alive=karts.filter(q=>!q.bbDead).length,stay=k===player&&!BB.skip;/* (the player's own kart stays where it happened, hidden, until the watching starts: the camera is on it) */
  k.bbDead=true;BB.left=alive-1;k.bbPlace=alive;k.bal=0;k.bbOut=0;k.finished=true;k.elim=true;k.place=alive;k.finishTime=raceTime;k.item=null;k.abQ=null;k.auto=true;
  if(!BB.skip){const y=Math.max(0,k.wy||0)+12,c=BB_COL[k.bbI%8];burst(k.x,y,k.y,46,[c,'#ffffff','#ffe066','#ff5a2a'],130,3.4);spawnRing(k.x,y,k.y,c,46,.55,false);spawnRing(k.x,Math.max(0,k.wy||0)+.6,k.y,'#ffffff',70,.7);
    if(k===player||near(k)>0)SFX.elim&&SFX.elim();showBanner(k===player?'Out! '+BB_DOT+' '+ord(alive):k.r.name+' is out',k===player?2.2:1.3,'sm');}
  k.speed=0;k.spin=0;if(k.m&&k.m.g)k.m.g.visible=false;if(!stay)bbAway(k);
  if(stay)setTimeout(()=>{if(!(BATTLE&&!SBX&&player===k&&k.bbDead))return;bbAway(k);if(state==='race'&&!BB.over&&!SPEC.on)bbWatch();},1600);else if(SPEC.on&&camT===k)specSet();
  BB.hudT=0;if(alive-1<=1)bbFinish(false);}
function bbAway(k){k.speed=0;k.x=k.px=50000+(k.bbPlace||1)*300;k.y=k.py=50000;k.wy=k.pwy=k.lastG=0;k.wvy=0;k.gRate=0;k.air=false;k.z=k.pz=0;}
/* under the name of the driver being watched */
function bbSpecInfo(k){const p=k.bbS||0;return k.bbDead?'out':(k.bal||0)+((k.bal||0)===1?' balloon':' balloons')+(k.bbL<BB_SETS.length-1?' ('+BB_SETS.slice((k.bbL||0)+1).join(', then ')+' to come)':', the last')+' '+BB_DOT+' '+p+(p===1?' point':' points');}
/* the order: drivers still in first, by points, then sets left, then balloons; then the eliminated, the last one out highest */
function bbRank(){return karts.slice().sort((a,b)=>(a.bbDead?1:0)-(b.bbDead?1:0)||(a.bbDead?a.bbPlace-b.bbPlace:(b.bbS||0)-(a.bbS||0)||(a.bbL||0)-(b.bbL||0)||(b.bal||0)-(a.bal||0))||a.bbI-b.bbI);}
function bbFinish(time){if(BB.over)return;BB.over=true;const r=bbRank(),sk=BB.skip;BB.skip=false;r.forEach((k,i)=>{k.finished=true;k.place=i+1;if(!k.bbDead)k.finishTime=raceTime;k.auto=true;});finishCount=karts.length;
  showBanner(time?'Time!':r[0]===player?'Last one standing!':r[0].r.name+' wins!',2.4,'md');SFX.finish();resultsAt=sk?.7:2.4;bbHud();}
function battleTick(dt){if(SBX)return sbTick(dt);if(state!=='race'||BB.over)return;BB.t-=dt;
  for(const k of karts){if(k.bbDead||BB.over)continue;if(!(k.bbOut>0)&&(k.wy||0)<-70){/* over the edge: one balloon gone, nobody's point */if(k.bal>0){k.bal--;bbPop(k);}BB.hudT=0;
      if(k.bal<=0){bbSetLost(k,1.3);if(k.bbDead||BB.over)continue;}else{k.bbOut=1.3;if(k===player&&!BB.skip)showBanner('Off the table!',1.4,'sm');}}
    if(k.bbOut>0){k.bbOut-=dt;k.speed*=Math.pow(.02,dt);if(k.bbOut<=0){/* back in, well away from the others */let best=0,bd=-1;for(let i=0;i<BB.spawn.length;i++){const s=BB.spawn[i];let d=1e9;for(const o of karts)if(o!==k&&!o.bbDead)d=Math.min(d,(o.x-s[0])**2+(o.y-s[1])**2);if(d>bd){bd=d;best=i;}}
        bbSpawnAt(k,best);if(!(k.bal>0)){k.bal=BB_SETS[k.bbL||0];if(k===player&&k.bal===1&&!BB.skip)showBanner('Last balloon!',1.5,'sm');}k.inv=3;k.bbOut=0;if(!BB.skip)spawnRing(k.x,k.wy+.6,k.y,'#7fe8ff',40,.6);if(k===camT)camSnap=true;}}}
  if(BB.over)return;if(BB.t<=0){BB.t=0;bbFinish(true);return;}
  BB.hudT-=dt;if(BB.hudT<=0){BB.hudT=.25;bbHud();}}
/* watching after you are out (the engine's spectating: its bar picks the driver and the camera); its Results button here is
   "Skip to results": the rest of the round is then PLAYED OUT at once, many steps a frame with no sound, so the order is a real one */
function bbSpecBtn(on){try{const s=$('specRes').querySelector('span');if(s)s.textContent=on?'Skip to results':'Results';}catch(e){}}
function bbWatch(){specEnter();bbSpecBtn(true);}
function bbSkip(){if(!BATTLE||SBX||BB.over)return false;if(!BB.skip){BB.skip=true;showBanner('Finishing the round...',1.4,'sm');}return true;}
function bbFast(){if(!BB.skip||BB.over||state!=='race')return;const m0=muted,t0=performance.now();muted=true;try{let n=0;while(!BB.over&&n<6000&&performance.now()-t0<11){update(STEP);n++;}}finally{muted=m0;}}
/* ---- the CPU drivers: fetch an item, hunt the nearest rival, shoot when lined up with a clear line, find their way round things ----
   THE DRIVERS' MAP (2026-11-14, for the bigger table with its ramps and levels): the arena as a grid of 20-unit squares (bbGrid, made once
   from the shapes). A square can be stood on if a kart at its middle touches nothing; from a square to the next is a step if the ground
   between them never rises faster than a ramp does, and a drop of any height is a step too (never off the table). bbPath walks that grid
   from the kart to where it wants to be and gives back the furthest square of the way that can be driven at in a straight line (bbClear).
   So no list of ramps is needed: a ramp is simply the only way the ground rises gently. */
const BB_C=20;
function bbReach(k,x,z){return Math.abs(battleG(x,z)-(k.wy||0))<12;}
/* which ramp a point is on (its number in BB.ramps), or -1: only the tests count with this */
function bbZone(x,z){for(let i=0;i<BB.ramps.length;i++){const r=BB.ramps[i];if(x>=r.x0&&x<=r.x1&&z>=r.z0&&z<=r.z1)return i;}return -1;}
function bbGrid(){const X=BB_X,Z=BB_Z,nx=Math.ceil(2*X/BB_C),nz=Math.ceil(2*Z/BB_C),n=nx*nz,h=new Float32Array(n),ok=new Uint8Array(n),ed=new Uint8Array(n),o={x:0,z:0},D=[[1,0],[0,1],[-1,0],[0,-1]];
  for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const x=-X+(i+.5)*BB_C,z=-Z+(j+.5)*BB_C,g=battleG(x,z),q=j*nx+i;h[q]=g;ok[q]=g>-100&&g<400&&!bbTouch(x,z,g,o)?1:0;}
  for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){const q=j*nx+i;if(!ok[q])continue;const x=-X+(i+.5)*BB_C,z=-Z+(j+.5)*BB_C;
    for(let d=0;d<4;d++){const i2=i+D[d][0],j2=j+D[d][1];if(i2<0||j2<0||i2>=nx||j2>=nz||!ok[j2*nx+i2])continue;let p=h[q],good=true;for(let s=1;s<=4;s++){const g=battleG(x+D[d][0]*BB_C*s/4,z+D[d][1]*BB_C*s/4);if(g-p>2.4){good=false;break;}p=g;}if(good)ed[q]|=1<<d;}}
  BB.grid={nx,nz,h,ok,ed,par:new Int32Array(n),mark:new Int32Array(n),stamp:0,q:new Int32Array(n)};}
/* can a kart drive straight from one point to the other? The ground on the way neither steps up nor drops, and nothing stands within a kart's half width of the line */
function bbClear(x0,z0,h0,x1,z1){const dx=x1-x0,dz=z1-z0,L=Math.hypot(dx,dz);if(L<1)return true;const n=Math.ceil(L/8),ux=dx/L,uz=dz/L;let p=h0;
  for(let s=1;s<=n;s++){const t=s/n,x=x0+dx*t,z=z0+dz*t,g=battleG(x,z);if(Math.abs(g-p)>3.4)return false;if(battleG(x-uz*BB_R,z+ux*BB_R)-g>BB_STEP||battleG(x+uz*BB_R,z-ux*BB_R)-g>BB_STEP)return false;p=g;}return true;}
/* is there a clear shot from one point to the other? (the ground between them is one surface: no wall, no drop) */
function bbSee(x0,z0,h0,x1,z1){const dx=x1-x0,dz=z1-z0,L=Math.hypot(dx,dz),n=Math.max(1,Math.ceil(L/10));let p=h0;for(let s=1;s<=n;s++){const g=battleG(x0+dx*s/n,z0+dz*s/n);if(Math.abs(g-p)>4.6)return false;p=g;}return true;}
/* the way from the kart to (tx,tz): the point to steer at now, or null if there is no way (in the air, walled in). shy: keep off the squares along the open west edge */
function bbPath(k,tx,tz,shy){const G=BB.grid||(bbGrid(),BB.grid),nx=G.nx,nz=G.nz,X=BB_X,Z=BB_Z,ok=G.ok,H=G.h,mark=G.mark,par=G.par,Q=G.q,
    cell=(x,z,wy)=>{const i=clamp(Math.floor((x+X)/BB_C),0,nx-1),j=clamp(Math.floor((z+Z)/BB_C),0,nz-1),q=j*nx+i;if(ok[q]&&(wy==null||Math.abs(H[q]-wy)<9))return q;
      let b=-1,bd=1e9;for(let dj=-2;dj<=2;dj++)for(let di=-2;di<=2;di++){const i2=i+di,j2=j+dj;if(i2<0||j2<0||i2>=nx||j2>=nz)continue;const p=j2*nx+i2;if(!ok[p]||(wy!=null&&Math.abs(H[p]-wy)>=9))continue;const d=(-X+(i2+.5)*BB_C-x)**2+(-Z+(j2+.5)*BB_C-z)**2;if(d<bd){bd=d;b=p;}}return b;};
  const s=cell(k.x,k.y,k.wy||0),t=cell(tx,tz,null);if(s<0||t<0)return null;if(s===t)return [tx,tz];
  const st=++G.stamp,iw=shy?2:-1;let qh=0,qt=0,found=false;Q[qt++]=s;mark[s]=st;par[s]=-1;
  while(qh<qt){const q=Q[qh++];if(q===t){found=true;break;}const e=G.ed[q];if(!e)continue;let p;
    if(e&1){p=q+1;if(mark[p]!==st){mark[p]=st;par[p]=q;Q[qt++]=p;}}
    if(e&2){p=q+nx;if(mark[p]!==st&&(p%nx>iw||q%nx<=iw)){mark[p]=st;par[p]=q;Q[qt++]=p;}}
    if(e&4){p=q-1;if(mark[p]!==st&&p%nx>iw){mark[p]=st;par[p]=q;Q[qt++]=p;}}
    if(e&8){p=q-nx;if(mark[p]!==st&&(p%nx>iw||q%nx<=iw)){mark[p]=st;par[p]=q;Q[qt++]=p;}}}
  if(!found)return null;const P=[];for(let q=t;q!==-1;q=par[q])P.push(q);P.reverse();
  const n=P.length-1,wy=k.wy||0;if(bbClear(k.x,k.y,wy,tx,tz)&&Math.abs(battleG(tx,tz)-H[t])<9)return [tx,tz];
  let pick=Math.min(n,2);for(let a=Math.min(n,14);a>2;a--){const q=P[a];if(bbClear(k.x,k.y,wy,-X+(q%nx+.5)*BB_C,-Z+(Math.floor(q/nx)+.5)*BB_C)){pick=a;break;}}
  const q=P[pick];return [-X+(q%nx+.5)*BB_C,-Z+(Math.floor(q/nx)+.5)*BB_C];}
function battleAI(k,dt){const A=k.bbA||(k.bbA={t:0,tx:0,tz:0,stuck:0,rev:0,fire:0}),wy=k.wy||0,o={steer:0,drift:false,brake:false,mul:1,use:false,back:false,hold:false,holdSl:1,release:null};
  if(k.bbOut>0||BB.over||k.bbDead)return o;A.t-=dt;const last=(k.bbL||0)>=BB_SETS.length-1&&BB.left>2;/* (careful on the last balloon, until it is down to a duel) */
  if(Math.hypot(A.tx-k.x,A.tz-k.y)<26)A.t=Math.min(A.t,.05);/* at the point it was steering for: where next? */
  if(A.t<=0){A.t=.45+((k.bbI*37+Math.floor(simTime*3))%7)*.07;let tx=null,tz=0,aim=false;
    /* the nearest rival it has a clear shot at; the nearest of all, to hunt; the nearest armed one, to keep away from */
    let en=null,ed=1e9,far=null,fd=1e9,arm=null,ad=1e9;for(const q of karts){if(q===k||q.bbDead||q.bbOut>0||!(q.bal>0))continue;const d=Math.hypot(q.x-k.x,q.y-k.y);if(d<fd){fd=d;far=q;}
      if(d<340&&Math.abs((q.wy||0)-wy)<14&&bbSee(k.x,k.y,wy,q.x,q.y)){if(d<ed){ed=d;en=q;}if(q.item&&d<ad){ad=d;arm=q;}}}
    A.en=en;
    if(k.item&&en&&ed<330){tx=en.x+Math.cos(en.ma)*en.speed*.25;tz=en.y+Math.sin(en.ma)*en.speed*.25;aim=true;/* a clear shot: straight at where they will be */}
    else if(k.item&&far&&(!last||fd<300)){tx=far.x;tz=far.y;}/* something to throw: after the nearest rival, wherever on the table */
    else if(last&&!k.item&&arm&&ad<170){/* on the last balloon with nothing to throw, and somebody armed is close: away from them */const a=Math.atan2(k.y-arm.y,k.x-arm.x);tx=clamp(k.x+Math.cos(a)*150,-BB_X+90,BB_X-40);tz=clamp(k.y+Math.sin(a)*150,-BB_Z+40,BB_Z-40);}
    else{/* an item box: a near one, by each driver's own taste (it changes every twenty seconds and spreads them over the table, the top included) */
      let bd=1e9;for(let bi=0;bi<boxes.length;bi++){const b=boxes[bi];if(b.r>0||(last&&b.x<-BB_X+90))continue;const d=Math.hypot(b.x-k.x,b.y-k.y)*(Math.abs(b.gy-wy)<12?1:1.2)*(b.gy>60?.3:1)/* (the box on the top is worth the climb) */*(.55+.9*(((k.bbI*7+bi*13+Math.floor(simTime/20)*5)*2654435761>>>0)%1000)/1000);if(d<bd){bd=d;tx=b.x;tz=b.y;}}
      if(tx===null&&far){tx=far.x;tz=far.y;}if(tx===null){const s=BB.spawn[(k.bbI*3+Math.floor(simTime/4))%BB.spawn.length];tx=s[0]*.5;tz=s[1]*.5;}}
    if(last)tx=Math.max(tx,-BB_X+80);/* the last balloon keeps away from the open edge */
    if(!aim){const W=bbPath(k,tx,tz,last);if(W){tx=W[0];tz=W[1];}}
    A.tx=tx;A.tz=tz;}
  let des=Math.atan2(A.tz-k.y,A.tx-k.x),d=angDiff(des,k.a);const d0=d;
  /* feelers: straight ahead and to each side; a wall ahead turns the kart toward the freer side */
  const feel=(a,r)=>battleG(k.x+Math.cos(k.a+a)*r,k.y+Math.sin(k.a+a)*r)-wy>BB_STEP,f0=feel(0,30)||feel(0,54),fl=feel(-.6,34),fr=feel(.6,34);
  if(f0)d=fl&&!fr?1.2:fr&&!fl?-1.2:(d>=0?1.2:-1.2);else if(fl)d+=.5;else if(fr)d-=.5;
  /* the last balloon, close to the open west edge and heading for it: turn back in */
  if(last&&k.x<-BB_X+60&&Math.cos(k.a)<-.15)d=angDiff(Math.sin(k.a)>=0?1.1:-1.1,k.a);
  o.steer=clamp(d*2.2,-1,1);
  /* the way on lies behind and it is going fast: ease off, so the turn fits between the things on the table */
  if(Math.abs(d0)>1.7&&k.speed>110)o.mul=.4;
  /* nose against something with the way on behind it: back out at once */
  if(A.rev<=0&&Math.abs(d0)>1.5&&Math.abs(k.speed)<40&&feel(0,15)){A.rev=.8;A.stuck=0;}
  /* stuck against something: back off, turning the other way */
  if(Math.abs(k.speed)<14&&k.spin<=0)A.stuck+=dt;else A.stuck=Math.max(0,A.stuck-dt*2);if(A.stuck>.9){A.rev=.9;A.stuck=0;}
  /* going nowhere for four seconds, whatever the speedometer says (sliding along a wall, shunting back and forth): set down again on open table, nothing lost */
  A.pt=(A.pt||0)+dt;if(A.pt>=1){A.pt=0;if(A.px!=null&&Math.hypot(k.x-A.px,k.y-A.pz)<14&&k.spin<=0)A.jam=(A.jam||0)+1;else A.jam=0;A.px=k.x;A.pz=k.y;if(A.jam>=4){A.jam=0;A.px=null;BB.jams=(BB.jams||0)+1;k.bbOut=.01;return o;}}
  if(A.rev>0){A.rev-=dt;o.brake=true;o.steer=clamp(-d0*2.2,-1,1);/* backing: the tail swings so the nose comes round to the way on */}
  /* use what it holds */
  A.fire-=dt;const en=A.en&&!A.en.bbDead&&!(A.en.bbOut>0)&&A.en.bal>0?A.en:null,ed=en?Math.hypot(en.x-k.x,en.y-k.y):1e9;
  if(k.item&&A.fire<=0&&k.spin<=0&&!(k.roll>0)){const it=k.item;let go=false,back=false;
    if(en){const ang=Math.abs(angDiff(Math.atan2(en.y-k.y,en.x-k.x),k.a));if(it==='oil'||it==='flour'){if(ed<110&&ang>2.2){go=true;back=true;}else if(A.t<.1&&ed>260){go=true;back=true;}}
      else if(it==='chili'||it==='rush'){go=ed<300&&ang<.5&&!last;}else if(it==='garlic'){go=ed<200;}else go=ed<290&&ang<.24&&bbSee(k.x,k.y,wy,en.x,en.y);}
    else if(it==='chili'||it==='rush'||it==='garlic')go=!last||Math.cos(k.a)>-.2;
    if(go){o.use=true;o.back=back;A.fire=.8+((k.bbI*13)%5)*.2;}}
  return o;}
/* ---- balloons: a bunch tied to the back of each kart, one bob apart; a popped one bursts ---- */
function bbBalloons(){if(BB.grp)scene.remove(BB.grp);BB.grp=new THREE.Group();scene.add(BB.grp);const g=new THREE.SphereGeometry(1.9,14,10);g.scale(1,1.22,1);const sg=new THREE.CylinderGeometry(.07,.07,1,4);sg.translate(0,.5,0);
  const sm=new THREE.MeshBasicMaterial({color:'#f4f1ea'});for(const k of karts){const c=BB_COL[k.bbI%8],m=new THREE.MeshStandardMaterial({color:c,roughness:.25,metalness:0,envMapIntensity:.9}),G=new THREE.Group();G.userData.b=[];
    for(let i=0;i<BB_START;i++){const b=new THREE.Mesh(g,m),s=new THREE.Mesh(sg,sm);b.castShadow=true;G.add(b);G.add(s);G.userData.b.push({b,s,ph:i*1.9+k.bbI});}k.bbG=G;BB.grp.add(G);}}
function bbPop(k){if(BB.skip)return;const y=(k.wy||0)+16;burst(k.x,y,k.y,22,[BB_COL[k.bbI%8],'#ffffff','#ffe066'],80,2.6);spawnRing(k.x,y,k.y,BB_COL[k.bbI%8],18,.3,false);if(near(k)>0&&SFX.bump)SFX.bump(near(k)*.8);}
/* the chase camera must not sit inside the boxes, the block or a pan: walk from the kart out to where the camera wants to be and stop short of the
   first thing of the arena that is higher than the camera there. It closes in at once and eases back out. */
function bbCam(){const k=camT;if(!k||state==='menu')return;const tx=k.x,tz=k.y,ty=(k.wy||0)+7,cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;let ok=1;
  for(let i=1;i<=16;i++){const f=i/16,g=Math.min(1.05,f+.05);if(battleG(tx+(cx-tx)*g,tz+(cz-tz)*g)>ty+(cy-ty)*g-2){ok=(i-1)/16;break;}}
  const was=BB.camF==null?1:BB.camF;BB.camF=ok<was?ok:Math.min(ok,was+.02);const f=Math.max(.16,BB.camF);if(f>=.999)return;
  camera.position.set(tx+(cx-tx)*f,ty+(cy-ty)*f+(1-f)*9,tz+(cz-tz)*f);camera.lookAt(cam.look.x,cam.look.y+cam.oy*.45,cam.look.z);}
function battleRender(time){if(SBX)return sbRender(time);if(!BATTLE)return;bbFast();bbCam();if(!BB.grp)return;for(const k of karts){const G=k.bbG;if(!G)continue;const m=k.m&&k.m.g;if(k.bbDead&&m)m.visible=false;/* (each frame: the engine's own drawing of a kart shows it again) */G.visible=!!m&&m.visible&&!(k.bbOut>0)&&!k.bbDead;if(!G.visible)continue;
    const px=m.position.x,py=m.position.y,pz=m.position.z,a=k.a,bx=px-Math.cos(a)*5,bz=pz-Math.sin(a)*5,n=G.userData.b.length;
    for(let i=0;i<n;i++){const q=G.userData.b[i],on=i<(k.bal||0);q.b.visible=q.s.visible=on;if(!on)continue;const sp=(i-(Math.min(k.bal,n)-1)/2),sw=Math.sin(time*2.1+q.ph)*.9,lag=Math.min(6,Math.abs(k.speed)*.03),
        x=bx-Math.cos(a)*lag+Math.cos(a+1.5708)*sp*3.0+sw*.4,z=bz-Math.sin(a)*lag+Math.sin(a+1.5708)*sp*3.0,y=py+14+Math.abs(sp)*-1.1+Math.sin(time*1.7+q.ph)*.5;
      q.b.position.set(x,y,z);q.s.position.set(bx,py+3.5,bz);q.s.lookAt(x,y-2.6,z);q.s.rotateX(Math.PI/2);q.s.scale.set(1,Math.hypot(x-bx,y-2.6-py-3.5,z-bz),1);}}}
/* ---- the read-out ---- */
/* The owner, 2026-11-13: "Remove the hud that lets you see how many balloons everyone has it's way too big and In the way."
   So no list: one small line. Three pips for your own sets (5, 3, 1: a filled pip is a set you still have), the clock, how many drivers
   are left, your points. Everybody's balloons are on their karts; the full table is the results screen. */
const BB_DOT=String.fromCharCode(183),BB_PIP=String.fromCharCode(9679),BB_NOPIP=String.fromCharCode(9675);
function bbHud(make){if(SBX)return sbHud();let e=BB.el;if(!e){e=BB.el=document.createElement('div');e.id='bbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 14px/1 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.55);border-radius:10px;padding:6px 10px;pointer-events:none;text-shadow:0 1px 2px #000;white-space:nowrap';stage.appendChild(e);}
  e.hidden=!BATTLE||state==='menu';document.body.classList.toggle('battle',BATTLE);if(e.hidden)return;const t=Math.max(0,Math.ceil(BB.t)),mm=Math.floor(t/60),ss=('0'+t%60).slice(-2),sep=' <span style="opacity:.55">'+BB_DOT+'</span> ',left=karts.filter(k=>!k.bbDead).length;
  let h='';if(player){const p=player.bbS||0,n=player.bbDead?0:BB_SETS.length-(player.bbL||0);let pp='';for(let i=0;i<BB_SETS.length;i++)pp+=i<n?BB_PIP:BB_NOPIP;
    h+='<span style="color:#ff7a66;letter-spacing:2px" title="sets of balloons left">'+pp+'</span>'+sep+mm+':'+ss+sep+(player.bbDead?'Out '+BB_DOT+' '+ord(player.bbPlace):left+' left')+sep+'<span style="color:#ffe066">'+p+(p===1?' pt':' pts')+'</span>';}else h=mm+':'+ss+sep+left+' left';
  e.innerHTML=h;}
/* a row of the results sheet: points, and that the driver went out */
function bbResRow(k){const p=k.bbS||0,s=p+(p===1?' point':' points');return k.bbDead?'<small style="opacity:.7;font-weight:600">out</small> '+BB_DOT+' '+s:s;}
/* ---- the arena as the game sees it: shapes, spawn places (x, z, heading), the raised parts and the ramps for the CPU drivers, item boxes ---- */
function battleSetup(def){BB.shapes=bbArena();BB.grid=null;const P=Math.PI;
  BB.spawn=[[-490,-220,P/2],[-130,-232,0],[450,-356,P],[300,-100,P],[-300,-90,0],[-150,310,0],[465,20,-P/2],[-400,150,0]];
  /* the ramps, for the record (the CPU drivers find them by the lie of the ground: bbGrid): its low and high ends, a point just off each on its middle line, its own rectangle */
  BB.ramps=[{lo:'F',hi:'L',foot:[-512,310],top:[-348,310],x0:-500,x1:-360,z0:240,z1:380},{lo:'F',hi:'B',foot:[465,-242],top:[465,-88],x0:380,x1:550,z0:-230,z1:-100},
    {lo:'L',hi:'S',foot:[238,310],top:[392,310],x0:250,x1:380,z0:240,z1:380},{lo:'B',hi:'S',foot:[465,98],top:[465,252],x0:380,x1:550,z0:110,z1:240},
    {lo:'F',hi:'I',foot:[-58,-90],top:[-212,-90],x0:-200,x1:-70,z0:-170,z1:-10},{lo:'F',hi:'I',foot:[-310,132],top:[-310,-22],x0:-420,x1:-200,z0:-10,z1:120}];
  /* thirty-one item boxes (sixteen until 2026-11-14, eight before that): a hit is the only way to score, so nobody should be far from one */
  for(const [x,z] of [[-470,-356],[-290,-356],[-50,-356],[190,-356],[-386,-301],[-242,-301],[46,-301],[350,-290],[-490,-120],[-490,60],[-310,-220],[-380,-130],[-30,-90],[110,-80],[320,40],[100,30],[70,190],[210,200],[-230,180],[-460,180],
      [-130,60],[220,-80],[0,-250],[-310,170],[-250,310],[-50,310],[150,310],[500,300],[420,330],[465,-40],[-525,310]])boxes.push({x,y:z,r:0,sv:boxes.length*3,gy:battleG(x,z),dbl:false});}
/* on every map load: leaving the arena takes its balloons and its scoreboard away; the HUD's lap and place read-outs are hidden in a battle */
function battleLoad(){if(SBX)sbOff();/* a different world is coming in */if(!document.getElementById('bbCss')){const st=document.createElement('style');st.id='bbCss';st.textContent='body.battle #posNum,body.battle #posSuf,body.battle #tbProg,body.battle #hudLap,body.battle #lapBars,body.battle #hudPB,body.battle #hudTime,body.battle #mini,body.battle #wrong,body.battle:not(.sbx) #abilBtn,body.battle .lapbox,body.battle .posbox{display:none!important}';document.head.appendChild(st);}
  document.body.classList.toggle('battle',BATTLE);if(!BATTLE){if(BB.grp){scene.remove(BB.grp);BB.grp=null;}if(BB.el)BB.el.hidden=true;BB.shapes=[];}}
/* ---- thrown things in the arena (the engine's hooks: patch20.py) ----
   p.bh is the level a thrown thing is on: it follows the ground down a drop and up a ramp, and anything higher than a step is a wall */
function bbProjWalls(p){if(p.bh==null)p.bh=p.owner?Math.max(0,p.owner.wy||0):Math.max(0,battleG(p.x,p.y));if(p.type==='lob'||p.type==='flour')return;/* those are in the air */
  const g=battleG(p.x,p.y);if(g<-100){p.t=0;return;}if(g-p.bh>BB_STEP){if(battleProjWall(p,p.bh)){burst(p.x,p.bh+6,p.y,8,['#ff5a2a','#ffe066','#ffffff'],50,2);if(++p.b>2)p.t=0;}}else p.bh=g;}
/* a homing one turns straight for its rival; a wall in the way stops it */
function bbHome(p,tg,dt,want,tr){let v=Math.hypot(p.vx,p.vy)||want;v+=(want-v)*Math.min(1,dt*3);const des=Math.atan2(tg.y-p.y,tg.x-p.x);let cur=Math.atan2(p.vy,p.vx);cur+=clamp(angDiff(des,cur),-tr*dt,tr*dt);
  p.vx=Math.cos(cur)*v;p.vy=Math.sin(cur)*v;p.x+=p.vx*dt;p.y+=p.vy*dt;if(p.bh==null)p.bh=p.owner?Math.max(0,p.owner.wy||0):0;const g=battleG(p.x,p.y);if(g<-100||g-p.bh>BB_STEP)p.t=0;else p.bh=g;}
/* who a homing thing goes for: the nearest rival in front (or behind, thrown backwards), else the nearest of all */
function bbTarget(k,back){let best=null,bs=1e9;for(const o of karts){if(o===k||o.bbDead||o.bbOut>0||!(o.bal>0))continue;const d=Math.hypot(o.x-k.x,o.y-k.y),a=Math.abs(angDiff(Math.atan2(o.y-k.y,o.x-k.x),k.a+(back?Math.PI:0))),sc=d*(a<.9?1:2.5)+(Math.abs((o.wy||0)-(k.wy||0))>14?400:0);if(sc<bs){bs=sc;best=o;}}return best;}
/* the pizza cutter's mark: whoever is winning (not the thrower) */
function bbLeader(k){for(const o of bbRank())if(o!==k&&!o.bbDead&&!(o.bbOut>0))return o;return null;}
/* Balloon Battle is played off line for now: starting or joining a friends' race leaves the mode and its arena */
function bbNoNet(){if(mode!=='bb'&&mode!=='sb')return;mode='single';try{store.set('crust-mode',mode);}catch(e){}if(MAPS[mapIdx].battle){mapIdx=0;loadMap(0,false);resetRace(true);}try{refreshMenu();}catch(e){}}
/* what a battle's item boxes give. The owner, 2026-11-13: "any homing items should be removed for the balloon game mode, as well as items that drop
   on the floor. It should only be projectiles the player has to aim or speed boosts. The auto drive speed boost items should also be removed".
   So: the pepperoni and the trio (fired where you point), and the chili (a boost you steer yourself). Gone: the dough ball (it homes), the
   olive oil (dropped), the delivery rush (drives itself), the garlic shield (neither).
   Then, the same day: "add flour bomb and meatball to the balloon game mode". The flour bomb is lobbed where you point; the bowling meatball
   rolls straight where you point and turns back off the walls. The meatball is one of the items a player unlocks for races; in a battle
   everybody has it. Only those the player has left switched on. */
const BB_ITEMS=[['pepperoni',3],['trio',2],['meatball',2],['flour',1.5],['chili',2]];
function bbRoll(){if(SBX)return sbRoll();const L=BB_ITEMS.filter(q=>q[0]==='meatball'?ITEMSET[q[0]]!==false:itemOn(q[0]));if(!L.length)return 'pepperoni';let t=0;for(const q of L)t+=q[1];let r=Math.random()*t;for(const q of L){r-=q[1];if(r<=0)return q[0];}return L[0][0];}
