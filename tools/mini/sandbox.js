/* ================= SANDBOX (free roam) =================
   The plan, the owner's brief and the decisions: docs/SANDBOX-PLAN.md, docs/NEXT-MODES-BRIEF.md.
   SBX is the switch; it is on only while the player is driving in Sandbox (never in the menu's demo, never in a race, never on line).
   Sandbox drives in a track's own world, loaded exactly as it is for a race: nothing about the race is touched. What changes is the
   ground and the walls under the one kart, which come from here instead of from the lap:
     the floor            height 0 everywhere
     the track            a ribbon with its real heights (it crosses over itself: which level you are on goes by your own height),
                          its raised edges a small bump you can drive over where the track lies on the ground
     the things           SB.shapes, the same boxes and cylinders as Balloon Battle's arena, each with a top and (if you can pass
                          beneath it) an underside
   One rule gives every wall, as in the arena: nothing drives up a step higher than SB_STEP, and what is overhead is not in the way.
   It rides on Balloon Battle's hooks in the engine (BATTLE is on with it; battle.js hands each call over when SBX is set), plus
   the few of its own in patch22.py.
   Regions: SB_REG, one per track world. Only the back garden has its things listed so far (web v188). */
let SBX=false;
const SB={shapes:[],hash:null,coins:[],rare:[],im:null,grp:null,el:null,save:null,hudT:0,reg:null,S:[],msgT:0},SB_STEP=5.5,SB_R=6.5,SB_HEAD=9,SB_C=48,SB_RAIL=4.2;
/* ---- the save: one record for the whole of Sandbox ---- */
function sbSave(){if(!SB.save){try{SB.save=JSON.parse(store.get('crust-sb')||'null');}catch(e){}if(!SB.save||typeof SB.save!=='object')SB.save={c:0,r:{}};if(!SB.save.r)SB.save.r={};SB.save.c=+SB.save.c||0;}return SB.save;}
function sbKeep(){try{store.set('crust-sb',JSON.stringify(SB.save));}catch(e){}}
/* ---- regions ---- garden metres -> the karts' own coordinates (x east, z south), as toyYard lays the garden out */
const SB_M=347,sbGX=g=>(g+.75)*SB_M,sbGZ=g=>-(g-3.5)*SB_M;
function sbBox(S,x0,x1,y0,y1,h,k,b){S.push({t:'box',x0:sbGX(x0),x1:sbGX(x1),z0:sbGZ(y1),z1:sbGZ(y0),h:h*SB_M,b:b==null?-1e9:b*SB_M,k});}
function sbCyl(S,x,y,r,h,k){S.push({t:'cyl',x:sbGX(x),z:sbGZ(y),r:r*SB_M,h:h*SB_M,b:-1e9,k});}
const SB_REG={
  /* the back garden: 25.5 m by 7 m between the house wall and three fences (tools/mini/mini.js toyYard, tools/mini/clearcheck.py backyard) */
  backyard:{name:'Home · Back Garden',
    shapes(){const S=[];
      sbBox(S,-60,60,-9,0,3,'the house wall');sbBox(S,-60,60,6.97,12,1.8,'the back fence');sbBox(S,-40,-13.87,-9,12,1.8,'the west fence');sbBox(S,11.57,40,-9,12,1.8,'the east fence');
      sbBox(S,-12.4,-10.0,4.45,6.35,2.1,'the shed');sbCyl(S,3.1,5.2,.3,6,'the tree');
      for(const x of [8.6,10.6]){sbCyl(S,x,5.6,.05,1.3,'a goal post');sbCyl(S,x,6.3,.05,.12,'the goal stay');}sbCyl(S,-8.2,4.2,.05,2,'a washing pole');sbCyl(S,-3.4,4.2,.05,2,'a washing pole');
      /* the drain pipe is an arch over the track: its two feet stop you, its roof is overhead */
      sbBox(S,-4.35,-2.85,5.71-.43,5.71-.36,.25,'the drain pipe');sbBox(S,-4.35,-2.85,5.71+.36,5.71+.43,.25,'the drain pipe');
      for(const [x,y,r,h,k] of [[5.0,.5,.24,.5,'a flowerpot'],[-1.2,.3,.22,.5,'a flowerpot'],[1.4,.32,.26,.5,'a flowerpot'],[6.3,.3,.23,.5,'a flowerpot'],[-8.6,.34,.25,.5,'a flowerpot'],[4.5,1.72,.2,.35,'the watering can'],
        [2.3,3.6,.09,.36,'the gnome'],[-13.3,2.9,.18,.46,'the fuel can'],[-12.4,2.5,.13,.46,'the cone'],[10.9,2.2,.3,.2,'the tyre'],[-3.3,1.2,.14,.13,'the skateboard'],[-4.0,.55,.14,.12,'the shoe'],[1.6,1.45,.22,.08,'the box'],
        [-11.4,2.8,.04,.07,'the tennis ball'],[6.9,1.5,.13,.06,'the bricks'],[-6.2,2.7,.05,.06,'the cube'],[7.4,3.9,.12,.22,'the football'],[-2.4,.35,.2,.12,'the hose']])sbCyl(S,x,y,r,h,k);
      for(const x of [-6.9,-5.9,-4.9,-2.6,-1.5])sbCyl(S,x,6.62,.2,.4,'a flowerpot');
      return S;},
    /* coins that lead you somewhere: polylines in garden metres, a coin every 15 cm; and rings of coins [x,y,radius,count] */
    lines:[[[-12.6,.8],[-10.6,.8]],[[-7.6,.75],[-5.4,.75]],[[8.4,.75],[10.6,.9],[11.0,1.6]],[[11.0,3.2],[11.0,4.6]],[[-1.6,3.1],[-.6,3.75]],[[.4,4.3],[1.6,4.5]],[[4.4,3.4],[5.8,3.0]],[[-9.6,5.4],[-9.6,6.2]],[[-12.9,5.0],[-12.9,6.3]]],
    rings:[[7.4,3.9,.3,8],[2.3,3.6,.25,6]],
    /* the rare ones (saved for good): [x, y, height m above the ground, what it is called in the save] */
    rare:[[-13.55,.3,0,'corner'],[10.35,6.2,0,'goal'],[-3.75,6.62,0,'bed'],[11.25,6.6,0,'far'],[-10.9,4.1,0,'door']],
    /* one more hangs in the air where the track swings out on its way down from the tree: lap fraction, metres beyond the track's edge, metres below it */
    air:[.392,.55,.1,'drop']}
};
/* ---- the track as ground: a grid of which lap points lie near each cell ---- */
function sbHashTrack(){const H=SB.hash=new Map(),W=TOYW()+3.4;for(let j=0;j<N;j++){const p=track[j];let last=-1;for(let l=-W;l<=W+.01;l+=16){const c=(Math.floor((p.x+p.nx*l)/SB_C)+2048)*4096+Math.floor((p.y+p.ny*l)/SB_C)+2048;if(c===last)continue;last=c;let a=H.get(c);if(!a)H.set(c,a=[]);if(a[a.length-1]!==j)a.push(j);}}}
/* every surface at a point: SB.S filled with [top, underside, lap point or -1], its length returned */
function sbSurf(x,z){const S=SB.S;let n=0;const put=(t,b,j)=>{let q=S[n];if(!q)q=S[n]=[0,0,0];q[0]=t;q[1]=b;q[2]=j;n++;};
  for(const s of SB.shapes){if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z;if(dx*dx+dz*dz<=s.r*s.r)put(s.h,s.b,-1);}else if(x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1)put(s.h,s.b,-1);}
  const a=SB.hash&&SB.hash.get((Math.floor(x/SB_C)+2048)*4096+Math.floor(z/SB_C)+2048);
  if(a){const sl=T.L/N,W=TOYW(),n0=n;for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y,u=dx*p.tx+dz*p.ty;if(u<-sl*.75||u>sl*.75)continue;const lat=dx*p.nx+dz*p.ny,al=Math.abs(lat);if(al>W+3.2)continue;
      const f=u/sl,fi=Math.floor(f),e=eyAt(((j+fi)%N+N)%N,f-fi),top=e+(al>W?SB_RAIL:0);let hit=false;for(let i=n0;i<n;i++){const q=S[i];if(Math.abs(q[1]+2.5-e)<6){hit=true;if(Math.abs(u)<q[3]){q[0]=top;q[1]=e-2.5;q[2]=j;q[3]=Math.abs(u);}break;}}
      if(!hit){put(top,e-2.5,j);S[n-1][3]=Math.abs(u);}}}
  return n;}
/* the ground under a point for something at height wy: the highest surface it could be standing on (no wy: the highest of all) */
function sbG(x,z,wy){if(wy==null)wy=1e9;const n=sbSurf(x,z),S=SB.S;let h=0;for(let i=0;i<n;i++){const t=S[i][0];if(t<=wy+SB_STEP&&t>h)h=t;}return h;}
function sbBlocked(x,z,wy){const n=sbSurf(x,z),S=SB.S;for(let i=0;i<n;i++)if(S[i][0]>wy+SB_STEP&&S[i][1]<wy+SB_HEAD)return true;return false;}
function sbTouch(x,z,wy,out){let nx=0,nz=0,n=0;for(let i=0;i<8;i++){const a=i*.785398,sx=Math.cos(a),sz=Math.sin(a);if(sbBlocked(x+sx*SB_R,z+sz*SB_R,wy)){nx+=sx;nz+=sz;n++;}}
  if(!n)return 0;const l=Math.hypot(nx,nz);if(l<1e-6){out.x=0;out.z=0;return 2;}out.x=nx/l;out.z=nz/l;return 1;}
const _sbN={x:0,z:0};
function sbWalls(k){const wy=k.wy||0;let r=sbTouch(k.x,k.y,wy,_sbN);
  if(!r){k.bpx=k.x;k.bpy=k.y;return;}
  if(r===2){if(k.bpx!=null){k.x=k.bpx;k.y=k.bpy;}k.speed*=.5;return;}
  const nx=_sbN.x,ny=_sbN.z;for(let n=0;n<16;n++){k.x-=nx*.7;k.y-=ny*.7;if(!sbTouch(k.x,k.y,wy,_sbN))break;}
  const vx=Math.cos(k.ma),vy=Math.sin(k.ma),dot=vx*nx+vy*ny;
  if(dot>0){if(k===camT&&dot>.3)shake(.25);k.speed*=1-.22*dot;const tx=vx-dot*nx,ty=vy-dot*ny;if(Math.hypot(tx,ty)>.05){const na=Math.atan2(ty,tx);k.ma=na;k.a+=angDiff(na,k.a)*.5;}
    if(dot>.45&&k.wallT<=0){k.wallT=.35;if(k===player)SFX.bump(.7);sparkWall(k,nx,ny);}}
  if(!sbTouch(k.x,k.y,wy,_sbN)){k.bpx=k.x;k.bpy=k.y;}}
/* which lap point the kart is over, if it is on the track at its own level (the boosters and the loop go by lap point); otherwise the one it had */
function sbIdx(k,was){const n=sbSurf(k.x,k.y),S=SB.S,wy=k.wy||0;let j=was,bd=7,on=false;for(let i=0;i<n;i++){const q=S[i];if(q[2]<0)continue;const d=Math.abs(q[1]+2.5-wy);if(d<bd){bd=d;j=q[2];on=true;}}k.sbOff=!on;return j;}
/* ---- coins ---- */
function sbCoins(){const R=SB.reg,sv=sbSave(),C=SB.coins=[],put=(x,y,z,rare,id)=>C.push({x,y,z,rare:!!rare,id,t:0,ph:C.length*.37});
  /* A kart is 12 units long (a 7.5 cm toy), so a trail of coins is one every 45 units or so: four a second at speed.
     Along the track: a run of six every 3 m, each run a little to one side then the other, none on the loop's own stretch */
  const sl=T.L/N,stp=Math.round(3*SB_M/sl),gap=Math.max(1,Math.round(45/sl));for(let j0=Math.round(stp/2),g=0;j0<N;j0+=stp,g++){if(LOOPS.some(L=>{let d=j0-L.j;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)*sl<420;}))continue;const lat=(g%3-1)*13;for(let q=0;q<6;q++){const p=track[(j0+q*gap)%N];put(p.x+p.nx*lat,(p.ey||0)+5.4,p.y+p.ny*lat);}}
  for(const L of R.lines||[])for(let i=0;i+1<L.length;i++){const a=L[i],b=L[i+1],d=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.round(d/.15));for(let q=i?1:0;q<=n;q++){const x=sbGX(a[0]+(b[0]-a[0])*q/n),z=sbGZ(a[1]+(b[1]-a[1])*q/n);if(!sbBlocked(x,z,0))put(x,sbG(x,z,0)+5.4,z);}}
  for(const [gx,gy,r,n] of R.rings||[])for(let q=0;q<n;q++){const a=q/n*6.28318,x=sbGX(gx+Math.cos(a)*r),z=sbGZ(gy+Math.sin(a)*r);put(x,sbG(x,z,0)+5.4,z);}
  for(const [gx,gy,h,id] of R.rare||[]){const x=sbGX(gx),z=sbGZ(gy);put(x,h*SB_M+8,z,true,SB.regId+':'+id);}
  if(R.air){const j=Math.round(R.air[0]*N)%N,p=track[j],q=track[(j+14)%N],sd=((q.x-p.x)*p.nx+(q.y-p.y)*p.ny)>0?-1:1/* the outside of the bend */,o=TOYW()+R.air[1]*SB_M;put(p.x+p.nx*o*sd,(p.ey||0)-R.air[2]*SB_M,p.y+p.ny*o*sd,true,SB.regId+':'+R.air[3]);}
  for(const c of C)if(c.rare&&sv.r[c.id])c.t=-1;/* found for good */
  /* drawn: the plain ones as one batch of gold discs, the rare ones bigger with a pepperoni face */
  if(SB.grp)scene.remove(SB.grp);SB.grp=new THREE.Group();scene.add(SB.grp);
  const g=new THREE.CylinderGeometry(4.2,4.2,.9,22);g.rotateX(Math.PI/2);const plain=C.filter(c=>!c.rare),im=SB.im=new THREE.InstancedMesh(g,new THREE.MeshStandardMaterial({color:'#ffc93a',roughness:.28,metalness:.85,emissive:'#a86a00',emissiveIntensity:.9}),Math.max(1,plain.length));
  im.frustumCulled=false;im.castShadow=false;im.userData.sunlit=true;SB.grp.add(im);plain.forEach((c,i)=>c.i=i);
  const rg=new THREE.CylinderGeometry(6.4,6.4,1.2,28);rg.rotateX(Math.PI/2);const rm=new THREE.MeshStandardMaterial({color:'#d8402a',roughness:.35,metalness:.35,emissive:'#6a1408',emissiveIntensity:.7}),dg=new THREE.CylinderGeometry(1,1,1.1,12);dg.rotateX(Math.PI/2);const dm=new THREE.MeshStandardMaterial({color:'#8f1d10',roughness:.5}),
    eg=new THREE.TorusGeometry(6.4,.7,8,28),em=new THREE.MeshStandardMaterial({color:'#ffd65a',roughness:.25,metalness:.9,emissive:'#7a4a00',emissiveIntensity:.6});
  for(const c of C)if(c.rare){const G=new THREE.Group();G.add(new THREE.Mesh(rg,rm));G.add(new THREE.Mesh(eg,em));for(const [x,y] of [[-2.0,1.7],[2.2,1.2],[0,-2.3],[-2.4,-1.5],[2.4,-1.8],[.3,3.0]]){const d=new THREE.Mesh(dg,dm);d.scale.set(1.5,1.5,1.3);d.position.set(x,y,0);G.add(d);}try{const sp=new THREE.Sprite(glowMat('#ffb030'));sp.scale.setScalar(34);G.add(sp);}catch(e){}G.position.set(c.x,c.y,c.z);G.traverse(o=>{o.userData.sunlit=true;});c.m=G;G.visible=c.t>=0;SB.grp.add(G);}}
function sbFound(){let n=0,t=0;for(const c of SB.coins)if(c.rare){t++;if(c.t<0)n++;}return [n,t];}
/* ---- on and off ---- */
function sbArm(){const def=MAPS[mapIdx],on=mode==='sb'&&!NET.cfg&&!!def&&!!SB_REG[def.id];if(!on){if(SBX)sbOff();return;}
  SBX=true;BATTLE=true;SB.regId=def.id;SB.reg=SB_REG[def.id];SB.shapes=SB.reg.shapes();for(const q of TOYPOSTS)SB.shapes.push({t:'cyl',x:q[0],z:q[1],r:3.4,h:q[2],b:-1e9,k:'a post under the track'});sbHashTrack();sbCoins();SB.hudT=0;SB.msgT=0;SB.camF=1;document.body.classList.add('battle');}
function sbOff(){if(!SBX)return;SBX=false;const def=MAPS[mapIdx];BATTLE=!!(def&&def.battle);if(SB.grp){scene.remove(SB.grp);SB.grp=null;SB.im=null;}SB.coins=[];SB.shapes=[];SB.hash=null;if(SB.el)SB.el.hidden=true;document.body.classList.toggle('battle',BATTLE);}
function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}
  if(BB.grp){scene.remove(BB.grp);BB.grp=null;}sbHud();const f=sbFound();showBanner(SB.reg.name,2.2,'md');}
function sbTick(dt){if(state!=='race')return;const k=player;if(!k)return;const sv=sbSave(),y=(k.wy||0)+3.5;let ch=false;
  for(const c of SB.coins){if(c.t<0)continue;if(c.t>0){c.t-=dt;if(c.t<=0){c.t=0;}continue;}const dx=c.x-k.x,dz=c.z-k.y,r=c.rare?12:10.5;if(dx*dx+dz*dz>r*r||Math.abs(c.y-y)>(c.rare?14:10))continue;
    if(c.rare){c.t=-1;sv.r[c.id]=1;sv.c+=10;if(c.m)c.m.visible=false;burst(c.x,c.y,c.z,26,['#ffd65a','#d8402a','#ffffff'],70,2.4);spawnRing(c.x,c.y,c.z,'#ffd65a',26,.5,false);const f=sbFound();showBanner('Pepperoni coin! '+f[0]+' of '+f[1],1.6,'sm');try{SFX.ready();}catch(e){}}
    else{c.t=40;sv.c+=1;burst(c.x,c.y,c.z,5,['#ffd65a','#fff4dc'],34,1.4);try{SFX.pad();}catch(e){}}ch=true;}
  if(ch){sbKeep();SB.hudT=0;}SB.hudT-=dt;if(SB.hudT<=0){SB.hudT=.5;sbHud();}}
const _sbM=new THREE.Matrix4(),_sbQ=new THREE.Quaternion(),_sbP=new THREE.Vector3(),_sbS=new THREE.Vector3(),_sbE=new THREE.Euler();
/* the chase camera must not look from inside a fence or the shed: walk from the kart out to where the camera wants to be and stop short of the
   first solid thing at that height (the track is never in the way: you can see over it). It closes in at once and eases back out. */
function sbSolid(x,z,y){for(const s of SB.shapes){if(s.h<=y||s.b>=y)continue;if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z,r=s.r+2;if(dx*dx+dz*dz<=r*r)return true;}else if(x>=s.x0-3&&x<=s.x1+3&&z>=s.z0-3&&z<=s.z1+3)return true;}return false;}
function sbCam(){const k=camT;if(!k||state==='menu')return;const tx=k.x,tz=k.y,ty=(k.wy||0)+7,cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;let ok=1;
  for(let i=1;i<=16;i++){const f=i/16,g=Math.min(1.06,f+.06);if(sbSolid(tx+(cx-tx)*g,tz+(cz-tz)*g,ty+(cy-ty)*g)){ok=(i-1)/16;break;}}
  const was=SB.camF==null?1:SB.camF;SB.camF=ok<was?ok:Math.min(ok,was+.02);const f=Math.max(.16,SB.camF);if(f>=.999)return;
  camera.position.set(tx+(cx-tx)*f,ty+(cy-ty)*f+(1-f)*9,tz+(cz-tz)*f);camera.lookAt(cam.look.x,cam.look.y+cam.oy*.45,cam.look.z);}
function sbRender(time){if(!SB.grp)return;sbCam();const im=SB.im;for(const c of SB.coins){const a=time*2.6+c.ph;if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}
    _sbE.set(0,a,0);_sbQ.setFromEuler(_sbE);_sbP.set(c.x,c.y,c.z);const s=c.t>0?0:1;_sbS.set(s,s,s);_sbM.compose(_sbP,_sbQ,_sbS);im.setMatrixAt(c.i,_sbM);}
  if(im)im.instanceMatrix.needsUpdate=true;}
function sbHud(){let e=SB.el;if(!e){e=SB.el=document.createElement('div');e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 13px/1.3 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.62);border-radius:12px;padding:8px 12px;pointer-events:none;text-shadow:0 1px 2px #000';stage.appendChild(e);}
  e.hidden=!SBX||state==='menu';if(BB.el)BB.el.hidden=true;if(e.hidden)return;const sv=sbSave(),f=sbFound(),dot=(c,r)=>'<span style="display:inline-block;width:'+r+'px;height:'+r+'px;border-radius:50%;background:'+c+';box-shadow:inset 0 0 0 2px rgba(0,0,0,.25);vertical-align:-2px;margin-right:6px"></span>';
  e.innerHTML='<div style="font-size:11px;letter-spacing:.6px;opacity:.85;text-transform:uppercase">'+SB.reg.name+'</div><div style="font-size:20px;margin-top:2px">'+dot('#ffc93a',15)+sv.c+'</div><div style="margin-top:2px">'+dot('#d8402a',13)+f[0]+' / '+f[1]+'</div>';}
/* what an item box gives here: only the boost (nobody to throw anything at) */
function sbRoll(){return 'chili';}
