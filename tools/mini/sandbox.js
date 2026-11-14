/* ================= SANDBOX (free roam) =================
   The plan, the owner's brief and the decisions: docs/SANDBOX-PLAN.md, docs/NEXT-MODES-BRIEF.md.
   SBX is the switch; it is on only while the player is driving in Sandbox (never in the menu's demo, never in a race, never on line).
   Sandbox drives in a track's own world, loaded exactly as it is for a race: nothing about the race is touched. What changes is the
   ground and the walls under the one kart, which come from here instead of from the lap:
     the floor            height 0 everywhere
     the track            a ribbon with its real heights (it crosses over itself: which level you are on goes by your own height),
                          its raised edges a small bump you can drive over where the track lies on the ground
     the things           everything that is drawn: sbColumns() goes through the world's own triangles once, when Sandbox starts, and
                          keeps for every 5-unit square of floor the upright stretches that are solid there (up to four, each a
                          top and an underside). So a wall, a table's legs, the space under a bed and a flowerpot are whatever the
                          picture shows, in any room, with nothing listed by hand. SB.shapes (boxes and cylinders, as in
                          Balloon Battle's arena) is only for what is not drawn
   One rule gives every wall, as in the arena: nothing drives up a step higher than SB_STEP, and what is overhead is not in the way.
   It rides on Balloon Battle's hooks in the engine (BATTLE is on with it; battle.js hands each call over when SBX is set), plus
   the few of its own in patch22.py.
   Regions: SB_REG, one per track world. Only the back garden has its things listed so far (web v188). */
let SBX=false;
const SB={shapes:[],gates:[],hash:null,col:null,coins:[],rare:[],im:null,grp:null,el:null,save:null,hudT:0,reg:null,S:[],msgT:0},SB_STEP=5.5,SB_R=6.5,SB_HEAD=9,SB_C=48,SB_RAIL=4.2,SB_K=6,SB_Q=8/* heights are kept in eighths of a unit */;
/* ---- the room's own geometry as columns ----
   What is left out, and why: what is not drawn (hidden pieces, the far-detail stand-ins); what you can see through or brush past (glass, nets,
   leaves, grass, cloth: anything transparent, cut out by its picture, or named in SB_SOFT); the track's own surface, edges and undersides
   (the lap gives those exactly: sbSurf) and its small jump ramps (the engine's own rule lifts the kart there); the item boxes (unnamed
   instanced things); and anything lying flatter than 1.2 units (rugs, paving, painted lines). */
const SB_SOFT=/grass|tuft|leaf|petal|cards|ynet|lace|ycl\d|outside|sky|toyroad|toyorange|toyplastic_|toydash|toypad|toyramp|stripes|aoshade|shadow|glow/;
/* (a square is 5 units across in a room and 6 in the garden, which is fifteen times a room's floor; nothing more than 70 units above the track's
   highest point is kept: no kart gets there, and ceilings and high shelves used to fill a square's six places and make false walls) */
function sbColumns(b){let cap=0;for(const p of track)if((p.ey||0)>cap)cap=p.ey;cap+=70;const C=(b[1]-b[0])*(b[3]-b[2])>1.2e7?6:5,x0=b[0]-10,z0=b[2]-10,nx=Math.ceil((b[1]-b[0]+20)/C),nz=Math.ceil((b[3]-b[2]+20)/C),cnt=new Uint8Array(nx*nz),sp=new Int16Array(nx*nz*SB_K*2),K=SB_K,Q=SB_Q,t0=performance.now();let tris=0,used=0;
  const ins=(c,lo,hi)=>{const o=c*K*2,n=cnt[c];let l=Math.max(-32000,Math.floor(lo*Q)),h=Math.min(32000,Math.ceil(hi*Q));
    for(let i=0;i<n;i++){const a=sp[o+i*2],e=sp[o+i*2+1];if(l<=e+12&&h>=a-12){/* touches one already there: they become one (and that may now touch another) */l=Math.min(l,a);h=Math.max(h,e);sp[o+i*2]=sp[o+(n-1)*2];sp[o+i*2+1]=sp[o+(n-1)*2+1];cnt[c]--;return ins(c,l/Q,h/Q);}}
    if(n<K){sp[o+n*2]=l;sp[o+n*2+1]=h;cnt[c]=n+1;return;}
    /* full: join the nearest one (never loses a solid, may fill a gap) */let bi=0,bd=1e9;for(let i=0;i<n;i++){const a=sp[o+i*2],e=sp[o+i*2+1],d=l>e?l-e:a-h;if(d<bd){bd=d;bi=i;}}sp[o+bi*2]=Math.min(sp[o+bi*2],l);sp[o+bi*2+1]=Math.max(sp[o+bi*2+1],h);};
  /* one triangle: every square it lies over gets the stretch of height it has there (the triangle cut to the square) */
  const P=new Float64Array(64),R=new Float64Array(64);
  const tri=(ax,ay,az,bx,by,bz,cx,cy,cz)=>{const ymax=Math.max(ay,by,cy);if(ymax<1.2)return;const ymin=Math.min(ay,by,cy);if(ymin>cap)return;const i0=Math.max(0,Math.floor((Math.min(ax,bx,cx)-x0)/C)),i1=Math.min(nx-1,Math.floor((Math.max(ax,bx,cx)-x0)/C)),k0=Math.max(0,Math.floor((Math.min(az,bz,cz)-z0)/C)),k1=Math.min(nz-1,Math.floor((Math.max(az,bz,cz)-z0)/C));if(i0>i1||k0>k1)return;tris++;
    if(i0===i1&&k0===k1){ins(i0*nz+k0,ymin,ymax);return;}
    for(let i=i0;i<=i1;i++)for(let k=k0;k<=k1;k++){const X0=x0+i*C,X1=X0+C,Z0=z0+k*C,Z1=Z0+C;let n=3;P[0]=ax;P[1]=ay;P[2]=az;P[3]=bx;P[4]=by;P[5]=bz;P[6]=cx;P[7]=cy;P[8]=cz;
      for(let e=0;e<4&&n;e++){const ax2=e<2?0:2,lim=e===0?X0:e===1?X1:e===2?Z0:Z1,sg=e%2?-1:1;let m=0;for(let q=0;q<n;q++){const u=q*3,v=((q+1)%n)*3,du=(P[u+ax2]-lim)*sg,dv=(P[v+ax2]-lim)*sg;if(du>=0){R[m*3]=P[u];R[m*3+1]=P[u+1];R[m*3+2]=P[u+2];m++;}if((du>=0)!==(dv>=0)){const t=du/(du-dv);R[m*3]=P[u]+(P[v]-P[u])*t;R[m*3+1]=P[u+1]+(P[v+1]-P[u+1])*t;R[m*3+2]=P[u+2]+(P[v+2]-P[u+2])*t;m++;}}n=m;for(let q=0;q<n*3;q++)P[q]=R[q];}
      if(!n)continue;let lo=1e9,hi=-1e9;for(let q=0;q<n;q++){const y=P[q*3+1];if(y<lo)lo=y;if(y>hi)hi=y;}if(hi>=1.2&&lo<=cap)ins(i*nz+k,lo,hi);}};
  const v=new THREE.Vector3(),M4=new THREE.Matrix4(),W=[0,0,0,0,0,0,0,0,0];world.updateMatrixWorld(true);
  world.traverse(o=>{if(!o.isMesh||!o.geometry||!o.geometry.attributes||!o.geometry.attributes.position||o.userData.noCol)return;for(let p=o;p;p=p.parent)if(!p.visible)return;const m=Array.isArray(o.material)?o.material[0]:o.material;if(!m)return;
    if(!o.userData.col){if(m.transparent||m.alphaTest>0||m.depthWrite===false||m.isShaderMaterial||SB_SOFT.test(m.name||''))return;if(o.isInstancedMesh&&!m.name)return;}
    const g=o.geometry;if(!g.boundingBox)g.computeBoundingBox();const pa=g.attributes.position,ix=g.index,nt=(ix?ix.count:pa.count)/3,ni=o.isInstancedMesh?o.count:1;
    for(let q=0;q<ni;q++){if(o.isInstancedMesh){o.getMatrixAt(q,M4);M4.premultiply(o.matrixWorld);}else M4.copy(o.matrixWorld);
      /* nowhere near the room, or wholly on the floor: skip it without looking at a triangle */const bb=g.boundingBox;let in0=false,top=-1e9;for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);if(v.y>top)top=v.y;}
      {const lo=new THREE.Vector3(1e9,1e9,1e9),hi=new THREE.Vector3(-1e9,-1e9,-1e9);for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);lo.min(v);hi.max(v);}in0=hi.x>=x0&&lo.x<=x0+nx*C&&hi.z>=z0&&lo.z<=z0+nz*C;}
      if(!in0||top<1.2)continue;used++;
      for(let t=0;t<nt;t++){for(let c=0;c<3;c++){const idx=ix?ix.getX(t*3+c):t*3+c;v.fromBufferAttribute(pa,idx).applyMatrix4(M4);W[c*3]=v.x;W[c*3+1]=v.y;W[c*3+2]=v.z;}tri(W[0],W[1],W[2],W[3],W[4],W[5],W[6],W[7],W[8]);}}});
  SB.col={x0,z0,nx,nz,C,cap,cnt,sp,tris,used,ms:Math.round(performance.now()-t0),b};}

/* ---- the save: one record for the whole of Sandbox ---- */
function sbSave(){if(!SB.save){try{SB.save=JSON.parse(store.get('crust-sb')||'null');}catch(e){}if(!SB.save||typeof SB.save!=='object')SB.save={c:0,r:{}};if(!SB.save.r)SB.save.r={};SB.save.c=+SB.save.c||0;}return SB.save;}
function sbKeep(){try{store.set('crust-sb',JSON.stringify(SB.save));}catch(e){}}
/* ---- regions ---- garden metres -> the karts' own coordinates (x east, z south), as toyYard lays the garden out */
const SB_M=347,sbGX=g=>(g+.75)*SB_M,sbGZ=g=>-(g-3.5)*SB_M;
function sbBox(S,x0,x1,y0,y1,h,k,b){S.push({t:'box',x0:sbGX(x0),x1:sbGX(x1),z0:sbGZ(y1),z1:sbGZ(y0),h:h*SB_M,b:b==null?-1e9:b*SB_M,k});}
function sbCyl(S,x,y,r,h,k){S.push({t:'cyl',x:sbGX(x),z:sbGZ(y),r:r*SB_M,h:h*SB_M,b:-1e9,k});}
const SB_REG={
  /* the three rooms: their things are read from what is drawn (sbColumns), their coins along the track are laid by sbCoins; the rest is here */
  /* (places in a room: centimetres from its middle, x east, y north; chosen on the room's plan, tools/neon/sbtest.py <room> draws it.
     A rare coin's height 0 = on the floor, which under a bed or a table is the point of it. air:'auto' = one more beside the highest bend of the track) */
  bedroom:{name:'Home \u00b7 Bedroom',room:1,lines:[[[40,-55],[170,-55]],[[-59,60],[66,84]]],rings:[],
    rare:[[176,-45,0,'bed'],[-35,224,0,'desk'],[-100,104,0,'chair'],[-174,214,0,'corner'],[85,128,0,'spiral']],air:'auto',
    gates:[{id:'b_k',w:'W',p:-48,to:'kitchen',at:'k_b',label:'KITCHEN'},{id:'b_g',w:'E',p:22,to:'garage',at:'ga_b',label:'GARAGE'}]},
  kitchen:{name:'Home \u00b7 Kitchen',room:1,lines:[[[66,-88],[133,-88]],[[85,99],[128,41]]],rings:[],
    rare:[[-1,17,0,'table'],[-42,60,0,'chair'],[-174,-218,0,'corner'],[181,80,0,'fridge'],[-186,3,0,'side']],air:'auto',
    gates:[{id:'k_g',w:'E',p:118,to:'backyard',at:'g_k',label:'GARDEN'},{id:'k_b',w:'E',p:-45,to:'bedroom',at:'b_k',label:'BEDROOM'}]},
  garage:{name:'Home \u00b7 Garage',room:1,lines:[[[60,-20],[95,-50]],[[140,-60],[140,-108]],[[-59,-122],[-1,-122]]],rings:[],
    rare:[[162,214,0,'bench'],[-179,27,0,'shelf'],[-162,-88,0,'board'],[-169,214,0,'cabinet'],[133,-218,0,'door']],air:'auto',
    gates:[{id:'ga_b',w:'W',p:132,to:'bedroom',at:'b_g',label:'BEDROOM'}]},
  /* the back garden: 25.5 m by 7 m between the house wall and three fences (tools/mini/mini.js toyYard, tools/mini/clearcheck.py backyard) */
  backyard:{name:'Home · Back Garden',
    /* (the garden's fences, shed, tree, pots and the rest were listed here by hand in v188; since v191 they are read from what is drawn) */
    /* coins that lead you somewhere: polylines in garden metres, a coin every 15 cm; and rings of coins [x,y,radius,count] */
    lines:[[[-12.6,.8],[-10.6,.8]],[[-7.6,.75],[-5.4,.75]],[[8.4,.75],[10.6,.9],[11.0,1.6]],[[11.0,3.2],[11.0,4.6]],[[-1.6,3.1],[-.6,3.75]],[[.4,4.3],[1.6,4.5]],[[4.4,3.4],[5.8,3.0]],[[-9.6,5.4],[-9.6,6.2]],[[-12.9,5.0],[-12.9,6.3]]],
    rings:[[7.4,3.9,.3,8],[2.3,3.6,.25,6]],
    /* the rare ones (saved for good): [x, y, height m above the ground, what it is called in the save] */
    rare:[[-13.55,.3,0,'corner'],[10.35,6.2,0,'goal'],[-3.75,6.62,0,'bed'],[11.25,6.6,0,'far'],[-10.9,4.1,0,'door']],
    /* one more hangs in the air where the track swings out on its way down from the tree: lap fraction, metres beyond the track's edge, metres below it */
    air:[.392,.55,.1,'drop'],
    /* the way indoors: an opening low in the house wall, beside the back door's step */
    gates:[{id:'g_k',w:'S',p:-3.4,to:'kitchen',at:'k_g',label:'KITCHEN'}]}
};
/* the menu in Sandbox: the track list shows only the places that have a region, and no cup tabs */
function sbMenu(){const on=mode==='sb',cats=document.getElementById('mapCats'),ms=document.getElementById('maps');if(!ms)return;if(cats)cats.hidden=on;
  if(on)ms.querySelectorAll('.mapc').forEach((b,i)=>{b.hidden=!SB_REG[MAPS[i].id];});else if(typeof setMapCat==='function'&&typeof mapCat!=='undefined'&&mapCat!=null)setMapCat(mapCatOf(MAPS[mapIdx]));}
/* ---- the track as ground: a grid of which lap points lie near each cell ---- */
/* (each lap point is entered for the squares its own strip of track covers: from one point's distance behind it to one ahead, edge to edge.
   Entering only the line across the track left gaps on tracks whose points are 8 apart: the kart kept dropping off the surface.) */
function sbHashTrack(){const H=SB.hash=new Map(),W=TOYW()+3.4,sl=T.L/N;for(let j=0;j<N;j++){const p=track[j];for(const t of [-sl,0,sl])for(let l=-W;l<=W+.01;l+=16){const c=(Math.floor((p.x+p.nx*l+p.tx*t)/SB_C)+2048)*4096+Math.floor((p.y+p.ny*l+p.ty*t)/SB_C)+2048;let a=H.get(c);if(!a)H.set(c,a=[]);if(a.indexOf(j,Math.max(0,a.length-8))<0)a.push(j);}}}
/* every surface at a point: SB.S filled with [top, underside, lap point or -1], its length returned */
function sbSurf(x,z){const S=SB.S;let n=0;const put=(t,b,j)=>{let q=S[n];if(!q)q=S[n]=[0,0,0,0,0];q[0]=t;q[1]=b;q[2]=j;q[4]=0;n++;};
  for(const g of SB.gates){const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-20&&d<SB_GLEN){const l=(x-g.x)*g.tx+(z-g.z)*g.tz;if(l>-SB_GW&&l<SB_GW)return 0;/* in a passage's mouth or the passage itself: bare floor (the mouth reaches 20 units into the room: a room's wall has a skirting board, and the squares are coarse) */}}
  for(const s of SB.shapes){if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z;if(dx*dx+dz*dz<=s.r*s.r)put(s.h,s.b,-1);}else if(x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1)put(s.h,s.b,-1);}
  {const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])put(1e6,-1e9,-1);/* past the room's own edge */else{const i=Math.floor((x-c.x0)/c.C),k=Math.floor((z-c.z0)/c.C),q=i*c.nz+k,o=q*SB_K*2;for(let e=0;e<c.cnt[q];e++)put(c.sp[o+e*2+1]/SB_Q,c.sp[o+e*2]/SB_Q,-1);}}}
  const a=SB.hash&&SB.hash.get((Math.floor(x/SB_C)+2048)*4096+Math.floor(z/SB_C)+2048);
  if(a){const sl=T.L/N,W=TOYW(),n0=n;for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y,u=dx*p.tx+dz*p.ty;if(u<-sl*.75||u>sl*.75)continue;const lat=dx*p.nx+dz*p.ny,al=Math.abs(lat);if(al>W+3.2)continue;
      const f=u/sl,fi=Math.floor(f),e=eyAt(((j+fi)%N+N)%N,f-fi),top=e+(al>W?SB_RAIL:0);let hit=false;for(let i=n0;i<n;i++){const q=S[i];if(Math.abs(q[1]+2.5-e)<6){hit=true;if(Math.abs(u)<q[3]){q[0]=top;q[1]=e-2.5;q[2]=j;q[3]=Math.abs(u);q[4]=al<=W?1:0;}break;}}
      if(!hit){put(top,e-2.5,j);S[n-1][3]=Math.abs(u);S[n-1][4]=al<=W?1:0;}}}
  return n;}
/* the ground under a point for something at height wy: the highest surface it could be standing on (no wy: the highest of all) */
function sbG(x,z,wy){if(wy==null)wy=1e9;const n=sbSurf(x,z),S=SB.S;let h=0;for(let i=0;i<n;i++){const t=S[i][0];if(t<=wy+SB_STEP&&t>h)h=t;}return h;}
/* THE LAP IS ALWAYS OPEN: where the point is on the track's own surface at the kart's own level, nothing drawn there is in the way. The race
   proves nothing real stands on the track; where the picture has the track run through the edge of a worktop or under a low beam, the track wins. */
function sbBlocked(x,z,wy){const n=sbSurf(x,z),S=SB.S;for(let i=0;i<n;i++)if(S[i][2]>=0&&S[i][4]&&Math.abs(S[i][1]+2.5-wy)<=SB_STEP+1)return false;for(let i=0;i<n;i++)if(S[i][0]>wy+SB_STEP&&S[i][1]<wy+SB_HEAD)return true;return false;}
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
/* ---- passages: the way from one region to the next ----
   A gate is a low dark opening in a wall with the next place's name over it (SB_REG[..].gates: which wall, how far along it, where it leads
   and which gate there you come out of). Past the wall is a straight dark duct. The owner (2026-11-13): "a smooth transition of driving
   without interruption while the world loads ... the player won't notice the scale changing". How that is kept:
     - as the kart goes in, the picture gives way to the duct itself: dark, ribs rushing past. The ribs are a page animation of
       transform and opacity only, which the browser keeps moving by itself, so they do not stop while the next room is being built
       (building a room is one long step: seconds on a phone; cutting it into slices is the next piece of work on this);
     - the engine's sound keeps running; the kart keeps the speed it went in with and comes out of the matching gate at that speed;
     - nothing is said about loading and nothing is to be pressed. */
const SB_GW=17,SB_GLEN=190;
function sbGates(){const c=SB.col,b=c.b,R=SB.reg,cx=R.room?SB_RX:(g=>(g+.75)*SB_M),cz=R.room?SB_RZ:(g=>-(g-3.5)*SB_M);SB.gates=[];
  for(const d of R.gates||[]){if(!SB_REG[d.to])continue;const g={id:d.id,to:d.to,at:d.at,label:d.label};
    if(d.w==='E'){g.x=b[1];g.z=cz(d.p);g.nx=1;g.nz=0;}else if(d.w==='W'){g.x=b[0];g.z=cz(d.p);g.nx=-1;g.nz=0;}else if(d.w==='N'){g.x=cx(d.p);g.z=b[2];g.nx=0;g.nz=-1;}else{g.x=cx(d.p);g.z=b[3];g.nx=0;g.nz=1;}
    g.tx=-g.nz;g.tz=g.nx;SB.gates.push(g);
    /* drawn: the opening (flat black, an arch), a wooden surround, the duct behind it (black inside), and a name plate above */
    const G=new THREE.Group(),W=SB_GW+1,H=27,arch=(w,h)=>{const sh=new THREE.Shape();sh.moveTo(-w,0);sh.lineTo(-w,h-w*.55);sh.absarc(0,h-w*.55,w,Math.PI,0,true);sh.lineTo(w,0);sh.lineTo(-w,0);return sh;};
    const hole=new THREE.Mesh(new THREE.ShapeGeometry(arch(W,H),12),new THREE.MeshBasicMaterial({color:'#050403',side:THREE.DoubleSide}));hole.position.z=R.room?7.2:.9;G.add(hole);/* in a room it stands just proud of the skirting board */
    const ring=arch(W+3.4,H+3.4);ring.holes.push(arch(W,H));const fr=new THREE.Mesh(new THREE.ExtrudeGeometry(ring,{depth:1.6,bevelEnabled:false,curveSegments:12}),new THREE.MeshStandardMaterial({color:R.room?'#7a5636':'#5d5148',roughness:.7}));fr.position.z=R.room?6:.2;fr.castShadow=true;G.add(fr);
    const duct=new THREE.Mesh(new THREE.BoxGeometry(2*W+4,H+8,SB_GLEN+20),new THREE.MeshBasicMaterial({color:'#050403',side:THREE.BackSide}));duct.position.set(0,(H+8)/2-.5,-(SB_GLEN+20)/2-.2);G.add(duct);
    const cv=cnv(256,64),q=cv.getContext('2d');q.fillStyle='#f3ead6';q.fillRect(0,0,256,64);q.strokeStyle='#5a3d22';q.lineWidth=6;q.strokeRect(3,3,250,58);q.fillStyle='#3a2513';q.font='900 34px Arial';q.textAlign='center';q.textBaseline='middle';q.fillText(d.label,128,34);
    const tx=T2(cv);tx.userData.keepCanvas=true;const plate=new THREE.Mesh(new THREE.PlaneGeometry(34,8.5),new THREE.MeshStandardMaterial({map:tx,roughness:.8}));plate.position.set(0,H+9.5,R.room?6.6:.7);G.add(plate);
    G.position.set(g.x,0,g.z);G.rotation.y=Math.atan2(-g.nx,-g.nz);/* its face looks back into the room */G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);}}
function sbDuctEl(){let e=SB.duct;if(!e){e=SB.duct=document.createElement('div');e.id='sbDuct';e.style.cssText='position:absolute;inset:0;z-index:5;background:#060403;opacity:0;pointer-events:none;overflow:hidden';
    const st=document.createElement('style');st.textContent='@keyframes sbduct{from{transform:translate(-50%,-50%) scale(.05);opacity:0}12%{opacity:.95}to{transform:translate(-50%,-50%) scale(3.4);opacity:.2}}#sbDuct i{position:absolute;left:50%;top:56%;width:58vmin;height:40vmin;border-radius:46% 46% 6% 6%;border:1.3vmin solid #3b2b1d;box-shadow:inset 0 0 7vmin 1vmin rgba(255,186,104,.09);animation:sbduct 1s linear infinite;will-change:transform,opacity}';document.head.appendChild(st);
    for(let i=0;i<5;i++){const r=document.createElement('i');r.style.animationDelay=(-i*.2)+'s';e.appendChild(r);}stage.appendChild(e);}return e;}
function sbDuctShow(){const k=player;let o=0;if(SB.trav)o=1;else if(SBX&&k)for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz,l=(k.x-g.x)*g.tx+(k.y-g.z)*g.tz;if(Math.abs(l)<SB_GW+4&&d>2)o=Math.max(o,Math.min(1,(d-2)/34));}
  if(o===0&&!SB.duct)return;const e=sbDuctEl();if(Math.abs((SB.ductO||0)-o)>.015||o===0||o===1){SB.ductO=o;e.style.opacity=o;}}
/* through a gate: the next region is built while the duct fills the picture, and the kart comes out of the matching gate */
async function sbTravel(g){if(SB.trav)return;const mi=MAPS.findIndex(m=>m.id===g.to);if(mi<0||!SB_REG[g.to])return;SB.trav=g;const k=player,sp=Math.max(70,Math.abs(k.speed));sbDuctShow();state='loading';
  try{await paint();await paint();projectiles.forEach(p=>scene.remove(p.mesh));hazards.forEach(h=>scene.remove(h.mesh));projectiles=[];hazards=[];
    mapIdx=mi;try{store.set('crust-map',mi);}catch(e){}loadMap(mi,false);for(const q of karts){q.idx=0;q.prog=0;q.loop=null;q.sc=null;}
    await Promise.all(Object.values(PROPT).map(t=>t.image&&t.image.decode&&!t.image.complete?t.image.decode().catch(()=>{}):null));}catch(e){console.warn('sandbox travel',e);}
  sbArm();const a=SB.gates.find(q=>q.id===g.at)||SB.gates[0];
  if(a){k.x=k.px=a.x+a.nx*(SB_GLEN-60);k.y=k.py=a.z+a.nz*(SB_GLEN-60);const h=Math.atan2(-a.nz,-a.nx);k.a=k.ma=k.pa=k.pma=h;}else{const p=track[0];k.x=k.px=p.x;k.y=k.py=p.y;}
  k.speed=sp;k.wy=k.pwy=k.lastG=0;k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.charge=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;k.idx=sbIdx(k,0);k.rx=k.x;k.ry=k.y;k.rz=0;k.rg=0;k.rma=k.ma;
  cam.a=k.ma;camSnap=true;try{warmScene();}catch(e){}SB.cool=1;state='race';SB.trav=null;SB.hudT=0;sbHud();showBanner(SB.reg.name,2,'md');}
/* ---- a race from its start line ----
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
/* ---- coins ---- */
/* a region's places are written in its own measure: the garden in metres (sbGX, sbGZ), a room in centimetres from its middle, x east and y north (SB_RX, SB_RZ) */
const SB_RX=c=>c*3.47,SB_RZ=c=>-c*3.47;
function sbCoins(){const R=SB.reg,sv=sbSave(),C=SB.coins=[],put=(x,y,z,rare,id)=>C.push({x,y,z,rare:!!rare,id,t:0,ph:C.length*.37}),sbGX=R.room?SB_RX:(g=>(g+.75)*SB_M),sbGZ=R.room?SB_RZ:(g=>-(g-3.5)*SB_M),HM=R.room?3.47:SB_M,STEPL=R.room?15:.15;
  /* A kart is 12 units long (a 7.5 cm toy), so a trail of coins is one every 45 units or so: four a second at speed.
     Along the track: a run of six every 3 m, each run a little to one side then the other, none on the loop's own stretch */
  const sl=T.L/N,stp=Math.round(3*SB_M/sl),gap=Math.max(1,Math.round(45/sl));for(let j0=Math.round(stp/2),g=0;j0<N;j0+=stp,g++){if(LOOPS.some(L=>{let d=j0-L.j;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)*sl<420;}))continue;const lat=(g%3-1)*13;for(let q=0;q<6;q++){const p=track[(j0+q*gap)%N];put(p.x+p.nx*lat,(p.ey||0)+5.4,p.y+p.ny*lat);}}
  for(const L of R.lines||[])for(let i=0;i+1<L.length;i++){const a=L[i],b=L[i+1],d=Math.hypot(b[0]-a[0],b[1]-a[1]),n=Math.max(1,Math.round(d/STEPL));for(let q=i?1:0;q<=n;q++){const x=sbGX(a[0]+(b[0]-a[0])*q/n),z=sbGZ(a[1]+(b[1]-a[1])*q/n);if(!sbBlocked(x,z,0))put(x,sbG(x,z,0)+5.4,z);}}
  for(const [gx,gy,r,n] of R.rings||[])for(let q=0;q<n;q++){const a=q/n*6.28318,x=sbGX(gx+Math.cos(a)*r),z=sbGZ(gy+Math.sin(a)*r);put(x,sbG(x,z,0)+5.4,z);}
  for(const [gx,gy,h,id] of R.rare||[]){const x=sbGX(gx),z=sbGZ(gy);put(x,(h<0?sbG(x,z,1e9):h*HM)+8,z,true,SB.regId+':'+id);}
  if(R.air==='auto'){/* the highest part of the track that is on a bend: the coin hangs 40 units beyond its outer edge, 20 below it */let bj=-1,bs=0;for(let j=0;j<N;j+=2){const p=track[j],q=track[(j+14)%N],turn=Math.abs((q.x-p.x)*p.nx+(q.y-p.y)*p.ny),e=p.ey||0;if(turn>6&&e>40&&e*Math.min(turn,20)>bs&&!LOOPS.some(L=>{let d=j-L.j;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)*sl<300;})){bs=e*Math.min(turn,20);bj=j;}}
    if(bj>=0){const p=track[bj],q=track[(bj+14)%N],sd=((q.x-p.x)*p.nx+(q.y-p.y)*p.ny)>0?-1:1,o=TOYW()+40,x=p.x+p.nx*o*sd,z=p.y+p.ny*o*sd;if(!sbBlocked(x,z,(p.ey||0)-20))put(x,(p.ey||0)-20,z,true,SB.regId+':high');}}
  else if(R.air){const j=Math.round(R.air[0]*N)%N,p=track[j],q=track[(j+14)%N],sd=((q.x-p.x)*p.nx+(q.y-p.y)*p.ny)>0?-1:1/* the outside of the bend */,o=TOYW()+R.air[1]*SB_M;put(p.x+p.nx*o*sd,(p.ey||0)-R.air[2]*SB_M,p.y+p.ny*o*sd,true,SB.regId+':'+R.air[3]);}
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
  SBX=true;BATTLE=true;SB.regId=def.id;SB.reg=SB_REG[def.id];SB.shapes=SB.reg.shapes?SB.reg.shapes():[];{let b=TOYROOM;if(!b){b=[1e9,-1e9,1e9,-1e9];for(const p of track){b[0]=Math.min(b[0],p.x-400);b[1]=Math.max(b[1],p.x+400);b[2]=Math.min(b[2],p.y-400);b[3]=Math.max(b[3],p.y+400);}}sbColumns(b);}sbHashTrack();sbCoins();sbGates();sbFlag();SB.hudT=0;SB.msgT=0;SB.camF=1;document.body.classList.add('battle');}
function sbOff(){if(!SBX)return;SBX=false;const def=MAPS[mapIdx];BATTLE=!!(def&&def.battle);if(SB.grp){scene.remove(SB.grp);SB.grp=null;SB.im=null;}SB.coins=[];SB.shapes=[];SB.gates=[];SB.hash=null;SB.col=null;if(SB.el)SB.el.hidden=true;SB.flag=null;sbRaceBtn(false);if(SB.duct&&!SB.trav){SB.duct.style.opacity=0;SB.ductO=0;}document.body.classList.toggle('battle',BATTLE);}
function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}
  if(BB.grp){scene.remove(BB.grp);BB.grp=null;}sbHud();const f=sbFound();showBanner(SB.reg.name,2.2,'md');}
function sbTick(dt){if(state!=='race'){sbRaceBtn(false);return;}const k=player;if(!k)return;{const f=SB.flag,near=!!f&&!SB.trav&&(k.x-f.x)**2+(k.y-f.z)**2<46*46&&Math.abs((k.wy||0)-f.y)<10;sbRaceBtn(near);if(near){try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp)sbRaceHere();SB.padUp=up;}catch(e){}}}if(SB.cool>0)SB.cool-=dt;else for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d>SB_GLEN-70&&Math.abs((k.x-g.x)*g.tx+(k.y-g.z)*g.tz)<SB_GW+2&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2){sbTravel(g);return;}}
  const sv=sbSave(),y=(k.wy||0)+3.5;let ch=false;
  for(const c of SB.coins){if(c.t<0)continue;if(c.t>0){c.t-=dt;if(c.t<=0){c.t=0;}continue;}const dx=c.x-k.x,dz=c.z-k.y,r=c.rare?12:10.5;if(dx*dx+dz*dz>r*r||Math.abs(c.y-y)>(c.rare?14:10))continue;
    if(c.rare){c.t=-1;sv.r[c.id]=1;sv.c+=10;if(c.m)c.m.visible=false;burst(c.x,c.y,c.z,26,['#ffd65a','#d8402a','#ffffff'],70,2.4);spawnRing(c.x,c.y,c.z,'#ffd65a',26,.5,false);const f=sbFound();showBanner('Pepperoni coin! '+f[0]+' of '+f[1],1.6,'sm');try{SFX.ready();}catch(e){}}
    else{c.t=40;sv.c+=1;burst(c.x,c.y,c.z,5,['#ffd65a','#fff4dc'],34,1.4);try{SFX.pad();}catch(e){}}ch=true;}
  if(ch){sbKeep();SB.hudT=0;}SB.hudT-=dt;if(SB.hudT<=0){SB.hudT=.5;sbHud();}}
const _sbM=new THREE.Matrix4(),_sbQ=new THREE.Quaternion(),_sbP=new THREE.Vector3(),_sbS=new THREE.Vector3(),_sbE=new THREE.Euler();
/* the chase camera must not look from inside a fence or the shed: walk from the kart out to where the camera wants to be and stop short of the
   first solid thing at that height (the track is never in the way: you can see over it). It closes in at once and eases back out. */
function sbSolid(x,z,y){for(const g of SB.gates){const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-12&&d<SB_GLEN+10&&Math.abs((x-g.x)*g.tx+(z-g.z)*g.tz)<SB_GW+1)return false;}{const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])return true;for(let dx=-2;dx<=2;dx+=2)for(let dz=-2;dz<=2;dz+=2){const i=Math.floor((x+dx-c.x0)/c.C),k=Math.floor((z+dz-c.z0)/c.C);if(i<0||k<0||i>=c.nx||k>=c.nz)continue;const q=i*c.nz+k,o=q*SB_K*2;for(let e=0;e<c.cnt[q];e++)if(c.sp[o+e*2]/SB_Q<=y+1&&c.sp[o+e*2+1]/SB_Q>=y-1)return true;}}}for(const s of SB.shapes){if(s.h<=y||s.b>=y)continue;if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z,r=s.r+2;if(dx*dx+dz*dz<=r*r)return true;}else if(x>=s.x0-3&&x<=s.x1+3&&z>=s.z0-3&&z<=s.z1+3)return true;}return false;}
function sbCam(){const k=camT;if(!k||state==='menu')return;const tx=k.x,tz=k.y,ty=(k.wy||0)+7,cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;let ok=1;
  for(let i=1;i<=16;i++){const f=i/16,g=Math.min(1.06,f+.06);if(sbSolid(tx+(cx-tx)*g,tz+(cz-tz)*g,ty+(cy-ty)*g)){ok=(i-1)/16;break;}}
  const was=SB.camF==null?1:SB.camF;SB.camF=ok<was?ok:Math.min(ok,was+.02);const f=Math.max(.16,SB.camF);if(f>=.999)return;
  camera.position.set(tx+(cx-tx)*f,ty+(cy-ty)*f+(1-f)*9,tz+(cz-tz)*f);camera.lookAt(cam.look.x,cam.look.y+cam.oy*.45,cam.look.z);}
function sbRender(time){sbDuctShow();if(!SB.grp)return;sbCam();if(SB.flag){SB.flag.F.rotation.y=time*1.6;SB.flag.F.position.y=12+Math.sin(time*2.2)*1.2;}const im=SB.im;for(const c of SB.coins){const a=time*2.6+c.ph;if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}
    _sbE.set(0,a,0);_sbQ.setFromEuler(_sbE);_sbP.set(c.x,c.y,c.z);const s=c.t>0?0:1;_sbS.set(s,s,s);_sbM.compose(_sbP,_sbQ,_sbS);im.setMatrixAt(c.i,_sbM);}
  if(im)im.instanceMatrix.needsUpdate=true;}
function sbHud(){let e=SB.el;if(!e){e=SB.el=document.createElement('div');e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 13px/1.3 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.62);border-radius:12px;padding:8px 12px;pointer-events:none;text-shadow:0 1px 2px #000';stage.appendChild(e);}
  e.hidden=!SBX||state==='menu';if(BB.el)BB.el.hidden=true;if(e.hidden)return;const sv=sbSave(),f=sbFound(),dot=(c,r)=>'<span style="display:inline-block;width:'+r+'px;height:'+r+'px;border-radius:50%;background:'+c+';box-shadow:inset 0 0 0 2px rgba(0,0,0,.25);vertical-align:-2px;margin-right:6px"></span>';
  e.innerHTML='<div style="font-size:11px;letter-spacing:.6px;opacity:.85;text-transform:uppercase">'+SB.reg.name+'</div><div style="font-size:20px;margin-top:2px">'+dot('#ffc93a',15)+sv.c+'</div><div style="margin-top:2px">'+dot('#d8402a',13)+f[0]+' / '+f[1]+'</div>';}
/* what an item box gives here: only the boost (nobody to throw anything at) */
function sbRoll(){return 'chili';}
