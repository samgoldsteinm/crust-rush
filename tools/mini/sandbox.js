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
let SBX=false,SBF=false;/* SBX: Sandbox is on. SBF: and the driving is free (the house, the pizza tracks); it is off where you keep to the road */
const SB={loops:[],shapes:[],gates:[],hash:null,col:null,coins:[],rare:[],im:null,grp:null,el:null,save:null,hudT:0,reg:null,S:[],msgT:0},SB_STEP=5.5,SB_R=6.5,SB_HEAD=9,SB_C=48,SB_RAIL=4.2,SB_K=6,SB_Q=8/* heights are kept in eighths of a unit */;
/* ---- the room's own geometry as columns ----
   What is left out, and why: what is not drawn (hidden pieces, the far-detail stand-ins); what you can see through or brush past (glass, nets,
   leaves, grass, cloth: anything transparent, cut out by its picture, or named in SB_SOFT); the track's own surface, edges and undersides
   (the lap gives those exactly: sbSurf) and its small jump ramps (the engine's own rule lifts the kart there); the item boxes (unnamed
   instanced things); and anything lying flatter than 1.2 units (rugs, paving, painted lines). */
const SB_SOFT=/grass|tuft|leaf|petal|cards|ynet|lace|ycl\d|outside|sky|toyroad|toyorange|toyplastic_|toydash|toypad|toyramp|stripes|aoshade|shadow|glow/;
/* (a square is 5 units across in a room and 6 in the garden, which is fifteen times a room's floor; nothing more than 70 units above the track's
   highest point is kept: no kart gets there, and ceilings and high shelves used to fill a square's six places and make false walls) */
function sbColumns(b){const og=SB.kind==='open';let cap=0;for(const p of track){const h=(og?groundAt(p.x,p.y):0)+(p.ey||0);if(h>cap)cap=h;}cap+=og?110:70;const C=(b[1]-b[0])*(b[3]-b[2])>1.2e7?6:5,x0=b[0]-10,z0=b[2]-10,nx=Math.ceil((b[1]-b[0]+20)/C),nz=Math.ceil((b[3]-b[2]+20)/C),cnt=new Uint8Array(nx*nz),thin=new Uint8Array(nx*nz),sp=new Int16Array(nx*nz*SB_K*2),K=SB_K,Q=SB_Q,t0=performance.now();let tris=0,used=0,isThin=false,minTop=0;
  const ins=(c,lo,hi)=>{if(isThin)thin[c]=1;const o=c*K*2,n=cnt[c];let l=Math.max(-32000,Math.floor(lo*Q)),h=Math.min(32000,Math.ceil(hi*Q));
    for(let i=0;i<n;i++){const a=sp[o+i*2],e=sp[o+i*2+1];if(l<=e+12&&h>=a-12){/* touches one already there: they become one (and that may now touch another) */l=Math.min(l,a);h=Math.max(h,e);sp[o+i*2]=sp[o+(n-1)*2];sp[o+i*2+1]=sp[o+(n-1)*2+1];cnt[c]--;return ins(c,l/Q,h/Q);}}
    if(n<K){sp[o+n*2]=l;sp[o+n*2+1]=h;cnt[c]=n+1;return;}
    /* full: join the nearest one (never loses a solid, may fill a gap) */let bi=0,bd=1e9;for(let i=0;i<n;i++){const a=sp[o+i*2],e=sp[o+i*2+1],d=l>e?l-e:a-h;if(d<bd){bd=d;bi=i;}}sp[o+bi*2]=Math.min(sp[o+bi*2],l);sp[o+bi*2+1]=Math.max(sp[o+bi*2+1],h);};
  /* one triangle: every square it lies over gets the stretch of height it has there (the triangle cut to the square) */
  const P=new Float64Array(64),R=new Float64Array(64);
  const tri=(ax,ay,az,bx,by,bz,cx,cy,cz)=>{const ymax=Math.max(ay,by,cy);if(ymax<1.2&&!og)return;const ymin=Math.min(ay,by,cy);if(ymin>cap||ymax<minTop)return;
    /* on a pizza the ground is hills: a triangle that lies on it (the pizza itself, the road, kerbs, painted lines) is ground, not a thing */if(og&&ay<groundAt(ax,az)+2.4&&by<groundAt(bx,bz)+2.4&&cy<groundAt(cx,cz)+2.4)return;const i0=Math.max(0,Math.floor((Math.min(ax,bx,cx)-x0)/C)),i1=Math.min(nx-1,Math.floor((Math.max(ax,bx,cx)-x0)/C)),k0=Math.max(0,Math.floor((Math.min(az,bz,cz)-z0)/C)),k1=Math.min(nz-1,Math.floor((Math.max(az,bz,cz)-z0)/C));if(i0>i1||k0>k1)return;tris++;
    if(i0===i1&&k0===k1){ins(i0*nz+k0,ymin,ymax);return;}
    for(let i=i0;i<=i1;i++)for(let k=k0;k<=k1;k++){const X0=x0+i*C,X1=X0+C,Z0=z0+k*C,Z1=Z0+C;let n=3;P[0]=ax;P[1]=ay;P[2]=az;P[3]=bx;P[4]=by;P[5]=bz;P[6]=cx;P[7]=cy;P[8]=cz;
      for(let e=0;e<4&&n;e++){const ax2=e<2?0:2,lim=e===0?X0:e===1?X1:e===2?Z0:Z1,sg=e%2?-1:1;let m=0;for(let q=0;q<n;q++){const u=q*3,v=((q+1)%n)*3,du=(P[u+ax2]-lim)*sg,dv=(P[v+ax2]-lim)*sg;if(du>=0){R[m*3]=P[u];R[m*3+1]=P[u+1];R[m*3+2]=P[u+2];m++;}if((du>=0)!==(dv>=0)){const t=du/(du-dv);R[m*3]=P[u]+(P[v]-P[u])*t;R[m*3+1]=P[u+1]+(P[v+1]-P[u+1])*t;R[m*3+2]=P[u+2]+(P[v+2]-P[u+2])*t;m++;}}n=m;for(let q=0;q<n*3;q++)P[q]=R[q];}
      if(!n)continue;let lo=1e9,hi=-1e9;for(let q=0;q<n;q++){const y=P[q*3+1];if(y<lo)lo=y;if(y>hi)hi=y;}if((og||hi>=1.2)&&hi>=minTop&&lo<=cap)ins(i*nz+k,lo,hi);}};
  const v=new THREE.Vector3(),M4=new THREE.Matrix4(),W=[0,0,0,0,0,0,0,0,0];world.updateMatrixWorld(true);
  /* (a list, not traverse: the build slices it, web v199, and a loop can pause where a callback cannot) */const OBJ=[];world.traverse(o=>OBJ.push(o));sbObj: for(const o of OBJ){if(!o.isMesh||!o.geometry||!o.geometry.attributes||!o.geometry.attributes.position||o.userData.noCol)continue;for(let p=o;p;p=p.parent)if(!p.visible)continue sbObj;const m=Array.isArray(o.material)?o.material[0]:o.material;if(!m)continue;
    if(!o.userData.col){if(m.transparent||m.alphaTest>0||m.depthWrite===false||m.isShaderMaterial||SB_SOFT.test(m.name||''))continue;if(o.isInstancedMesh&&!m.name)continue;}
    minTop=o.userData.colMin||0;/* (a loop's hoop: only what stands higher than a step is solid. Its low lips lie beside the lanes into and out of the loop, and a kart near the middle rail was bumped up onto them: the owner's "going around the loops is a little glitchy in sandbox mode") */isThin=/toyblue/.test(m.name||'');/* the track's posts, bars and gates: solid to a kart, but the camera looks past them (sbSolid) */const g=o.geometry;if(!g.boundingBox)g.computeBoundingBox();const pa=g.attributes.position,ix=g.index,nt=(ix?ix.count:pa.count)/3,ni=o.isInstancedMesh?o.count:1;
    for(let q=0;q<ni;q++){if(o.isInstancedMesh){o.getMatrixAt(q,M4);M4.premultiply(o.matrixWorld);}else M4.copy(o.matrixWorld);
      /* nowhere near the room, or wholly on the floor: skip it without looking at a triangle */const bb=g.boundingBox;let in0=false,top=-1e9;for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);if(v.y>top)top=v.y;}
      {const lo=new THREE.Vector3(1e9,1e9,1e9),hi=new THREE.Vector3(-1e9,-1e9,-1e9);for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);lo.min(v);hi.max(v);}in0=hi.x>=x0&&lo.x<=x0+nx*C&&hi.z>=z0&&lo.z<=z0+nz*C;}
      if(!in0||(top<1.2&&!og))continue;used++;
      for(let t=0;t<nt;t++){for(let c=0;c<3;c++){const idx=ix?ix.getX(t*3+c):t*3+c;v.fromBufferAttribute(pa,idx).applyMatrix4(M4);W[c*3]=v.x;W[c*3+1]=v.y;W[c*3+2]=v.z;}tri(W[0],W[1],W[2],W[3],W[4],W[5],W[6],W[7],W[8]);}}}
  SB.col={x0,z0,nx,nz,C,cap,cnt,thin,sp,tris,used,ms:Math.round(performance.now()-t0),b};}

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
    /* (the second: the garage's own open door, the whole width of it: no arch is drawn, driving out onto the drive is the passage) */
    gates:[{id:'ga_b',w:'W',p:132,to:'bedroom',at:'b_g',label:'BEDROOM'},{id:'garage>margherita',w:'S',p:0,hw:520,plain:1,to:'margherita',at:'margherita>garage',label:'MARGHERITA RING'}]},
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
/* ---- the rest of the game's tracks (web v192) ----
   Every track is a place in Sandbox. Three kinds:
     toy    the house's four (above): drive anywhere; the ground and the walls are Sandbox's own
     open   the fifteen pizza tracks: drive anywhere on the pizza. The ground is the engine's own (groundAt, and the track's height where it
            is raised); the walls are read from what is drawn, as in the rooms, with whatever lies flat on the ground left out; the edge of
            the world is the crust
     road   Sauce Spiral and the four Neon tracks: the road winds up a tower or hangs in the air, so there you keep to it, either way round,
            with the race's own walls (SBF is off)
   SB_AREA names the part of the world each track is in; SB_LINKS says which tracks a track's passages lead to (the plan's sketch, docs/SANDBOX-PLAN.md).
   A passage on an open track is an arch in the crust; on a road track an arch over the left-hand lane; out of the house it is the garage's open door. */
const SB_AREA={margherita:'Kitchen Country',basil:'Kitchen Country',oven:'Kitchen Country',spiral:'Kitchen Country',bay:'The Bay',lagoon:'The Bay',calzone:'The Bay',tour:'The Bay',
  peaks:'The Old Town',mozz:'The Old Town',napoli:'The Old Town',moon:'The Old Town',frosty:'The Freezer Range',burn:'The Freezer Range',glacier:'The Freezer Range',peak:'The Freezer Range',
  grid:'The Neon District',laser:'The Neon District',holo:'The Neon District',synth:'The Neon District'};
const SB_LINKS={margherita:['garage','basil','oven','bay'],basil:['margherita','mozz','spiral'],oven:['margherita','spiral'],spiral:['oven','basil','frosty'],frosty:['spiral','burn'],burn:['frosty','glacier'],glacier:['burn','peak'],peak:['glacier','synth'],
  mozz:['basil','napoli'],napoli:['mozz','moon','holo'],moon:['napoli','peaks'],peaks:['moon'],calzone:['tour','lagoon'],tour:['calzone'],lagoon:['calzone','bay'],bay:['lagoon','margherita'],
  synth:['peak','laser'],holo:['napoli','grid'],laser:['synth','grid'],grid:['holo','laser']};
function sbRegOf(id){if(SB_REG[id])return SB_REG[id];const m=MAPS.find(q=>q.id===id);if(!m||m.battle||!SB_AREA[id])return null;return SB_REG[id]={name:SB_AREA[id]+' \u00b7 '+m.name,auto:1,kind:m.exact?'road':'open'};}
/* the menu in Sandbox: every track is a place to start, under its cup's tab as usual (the battle arena has no tab) */
function sbMenu(){const cats=document.getElementById('mapCats');if(cats)cats.hidden=false;}
/* ---- the track as ground: a grid of which lap points lie near each cell ---- */
/* (each lap point is entered for the squares its own strip of track covers: from one point's distance behind it to one ahead, edge to edge.
   Entering only the line across the track left gaps on tracks whose points are 8 apart: the kart kept dropping off the surface.) */
function sbHashTrack(){const H=SB.hash=new Map(),W=(SB.kind==='toy'?TOYW():WALLD)+3.4,sl=T.L/N;for(let j=0;j<N;j++){const p=track[j];for(const t of [-sl,0,sl])for(let l=-W;l<=W+.01;l+=16){const c=(Math.floor((p.x+p.nx*l+p.tx*t)/SB_C)+2048)*4096+Math.floor((p.y+p.ny*l+p.ty*t)/SB_C)+2048;let a=H.get(c);if(!a)H.set(c,a=[]);if(a.indexOf(j,Math.max(0,a.length-8))<0)a.push(j);}}}
/* every surface at a point: SB.S filled with [top, underside, lap point or -1], its length returned */
function sbSurf(x,z){const S=SB.S;let n=0;const put=(t,b,j)=>{let q=S[n];if(!q)q=S[n]=[0,0,0,0,0];q[0]=t;q[1]=b;q[2]=j;q[4]=0;n++;};
  SB.inG=null;for(const g of SB.gates){if(g.road)continue;const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-20&&d<SB_GLEN){const l=(x-g.x)*g.tx+(z-g.z)*g.tz;if(l>-g.hw&&l<g.hw){SB.inG=g;return 0;}/* in a passage's mouth or the passage itself: bare floor (the mouth reaches 20 units into the room: a room's wall has a skirting board, and the squares are coarse) */}}
  for(const s of SB.shapes){if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z;if(dx*dx+dz*dz<=s.r*s.r)put(s.h,s.b,-1);}else if(x>=s.x0&&x<=s.x1&&z>=s.z0&&z<=s.z1)put(s.h,s.b,-1);}
  if(SB.rim&&x*x+z*z>SB.rim*SB.rim)put(1e6,-1e9,-1);/* past the crust */
  {const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])put(1e6,-1e9,-1);/* past the room's own edge */else{const i=Math.floor((x-c.x0)/c.C),k=Math.floor((z-c.z0)/c.C),q=i*c.nz+k,o=q*SB_K*2;let low=-1e9;/* (round a full loop the low things, its lips and the rails of its two lanes, are not in the way: the loop's own rules place the kart there. Without this a pizza's loop could not be entered in free driving) */if(c.cnt[q])for(const L of SB.loops){const al=(x-L.p.x)*L.p.tx+(z-L.p.y)*L.p.ty;if(al>-L.r&&al<L.r){const lt=(x-L.p.x)*L.p.nx+(z-L.p.y)*L.p.ny;if(lt>L.a&&lt<L.b){low=L.g0+7.5;break;}}}for(let e=0;e<c.cnt[q];e++){const t=c.sp[o+e*2+1]/SB_Q;if(t>low)put(t,c.sp[o+e*2]/SB_Q,-1);}}}}
  const a=SB.hash&&SB.hash.get((Math.floor(x/SB_C)+2048)*4096+Math.floor(z/SB_C)+2048);
  if(a){/* (on a pizza the track lies on the hills: its height is the ground's plus its own; it has no raised edge to bump over, and its width for
     "the lap is always open" is the road's) */const sl=T.L/N,toy=SB.kind==='toy',W=toy?TOYW():RW+10,g0=toy?0:groundAt(x,z),n0=n;for(const j of a){const p=track[j],dx=x-p.x,dz=z-p.y,u=dx*p.tx+dz*p.ty;if(u<-sl*.75||u>sl*.75)continue;const lat=dx*p.nx+dz*p.ny,al=Math.abs(lat);if(al>(toy?W+3.2:WALLD))continue;
      /* (how far along, with the bend allowed for exactly as the race does in kEy: on the outside of a bend the lap points are further apart than on the
         middle line. Without this the height stepped a little at every lap point on a climbing bend or spiral: the owner's "choppy") */
      const kap=(p.bend||0)/(20*sl),f=Math.max(-2,Math.min(2,u/(1-Math.max(-.7,Math.min(.7,kap*lat)))/sl)),fi=Math.floor(f),e=g0+eyAt(((j+fi)%N+N)%N,f-fi),top=e+(toy&&al>W?SB_RAIL:0);let hit=false;for(let i=n0;i<n;i++){const q=S[i];if(Math.abs(q[1]+2.5-e)<6){hit=true;if(Math.abs(u)<q[3]){q[0]=top;q[1]=e-2.5;q[2]=j;q[3]=Math.abs(u);q[4]=al<=W?1:0;}break;}}
      if(!hit){put(top,e-2.5,j);S[n-1][3]=Math.abs(u);S[n-1][4]=al<=W?1:0;}}}
  return n;}
/* how far above or below the track's surface still counts as "on the track, at its level". In the house a step's height: the track crosses over itself
   there. On a pizza the road is the ground and a kart on it may be up on a jump ramp (the engine's own, 10 or so high) or coming down from one: with one
   level only, any height; where the road has bridges, 20 (web v193: a drawn lip at the end of Margherita Ring's glide ramp caught the kart as it took off) */
const sbLvl=()=>SB.kind==='toy'?SB_STEP+1:MULTI?20:1e9;
/* the ground under a point for something at height wy: the highest surface it could be standing on (no wy: the highest of all) */
function sbG(x,z,wy){if(wy==null)wy=1e9;const n=sbSurf(x,z),S=SB.S;if(SB.inG&&SB.kind!=='toy'&&((x-SB.inG.x)*SB.inG.nx+(z-SB.inG.z)*SB.inG.nz)>-2)return SB.inG.y;/* in a passage through the crust: its own level floor */
  /* on the track's own surface, at the kart's own level, the ground IS the track: nothing drawn there lifts the kart (a start plate, the foot of a banner,
     the root of the tree the spiral winds round: each was a jolt). The same idea as "the lap is always open" below. */
  {const lv=sbLvl();let r=-1e9;for(let i=0;i<n;i++)if(S[i][2]>=0&&S[i][4]&&Math.abs(S[i][1]+2.5-wy)<=lv&&S[i][0]>r)r=S[i][0];if(r>-1e8)return r;}
  let h=SB.kind==='toy'?0:groundAt(x,z);for(let i=0;i<n;i++){const t=S[i][0];if(t<=wy+SB_STEP&&t>h)h=t;}return h;}
/* THE LAP IS ALWAYS OPEN: where the point is on the track's own surface at the kart's own level, nothing drawn there is in the way. The race
   proves nothing real stands on the track; where the picture has the track run through the edge of a worktop or under a low beam, the track wins. */
/* climbing (web v200): how much of the engine's pull back down a slope a kart feels going up, and the steepest ground it can climb at all
   (as a rise over SB_R, the distance the walls are looked for at), both from its off-road (statMods .off: -3.6 to 3.6, 0 a middle kart; with
   kart stats off, 0). A middle kart: 45% of the pull, up to about 40 degrees; the best off-road 15%, 50 degrees; the worst 85%, 26 degrees */
function sbOffRd(k){const sm=k&&k.sm;return sm&&isFinite(sm.off)?sm.off:0;}
function sbGrav(k){return clamp(.45-.085*sbOffRd(k),.12,.9);}
function sbClimb(k){return SB_R*clamp(.84+.1*sbOffRd(k),.45,1.2);}
function sbBlocked(x,z,wy){const n=sbSurf(x,z),S=SB.S,lv=sbLvl();for(let i=0;i<n;i++)if(S[i][2]>=0&&S[i][4]&&Math.abs(S[i][1]+2.5-wy)<=lv)return false;
  if(SB.kind==='open'&&!SB.inG){/* a pizza's own ground: a face that rises more than a step from where the kart stands is a cliff, not a hill (the land beside some tracks climbs 180 in a few lengths), and water deeper than the wheels is a shore */const g0=groundAt(x,z);if(g0>wy+sbClimb(player)||(WATER_Y!=null&&g0<WATER_Y-3&&wy<WATER_Y+SB_HEAD))return true;}
for(let i=0;i<n;i++)if(S[i][0]>wy+SB_STEP&&S[i][1]<wy+SB_HEAD)return true;return false;}
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
/* (near: the race's own answer, the nearest lap point a little way either side of the last one. On a pizza a kart in the air goes by that: a jump or a
   glide over a canyon carries it along the lap with no track under it, and the glide, its rings and the way back out of the canyon all go by the lap point) */
function sbIdx(k,was,near){const n=sbSurf(k.x,k.y),S=SB.S,wy=k.wy||0;let j=was,bd=7,on=false;for(let i=0;i<n;i++){const q=S[i];if(q[2]<0)continue;const d=Math.abs(q[1]+2.5-wy);if(d<bd){bd=d;j=q[2];on=true;}}k.sbOff=!on;if(!on&&near!=null&&SB.kind==='open'&&(k.air||k.glide)){/* (only when that lap point is really nearby: a kart jumping off a hill far out on the pizza is not on the lap) */const p=track[near];if((p.x-k.x)**2+(p.y-k.y)**2<170*170)return near;}return j;}
/* ---- passages: the way from one region to the next ----
   A gate is a low dark opening in a wall with the next place's name over it (SB_REG[..].gates: which wall, how far along it, where it leads
   and which gate there you come out of). Past the wall is a straight dark duct. The owner (2026-11-13): "a smooth transition of driving
   without interruption while the world loads ... the player won't notice the scale changing". How that is kept:
     - as the kart goes in, the picture gives way to the duct itself: dark, ribs rushing past. The ribs are a page animation of
       transform and opacity only, which the browser keeps moving by itself, so they do not stop while the next room is being built
       (building a room is one long step: seconds on a phone; cutting it into slices is the next piece of work on this);
     - the engine's sound keeps running; the kart keeps the speed it went in with and comes out of the matching gate at that speed;
     - nothing is said about loading and nothing is to be pressed. */
const SB_GW=26,SB_GLEN=190;/* a mouth's half width. It was 17: the kart's middle (it is 13 wide as the walls see it) had 21 units to hit, three karts' width, at 150 a second. The owner, 2026-11-14: "it's hard to go into the tunnels and I miss them a lot of times" */
const sbSeed=id=>{let h=7;for(let i=0;i<id.length;i++)h=(h*31+id.charCodeAt(i))%9973;return h/9973;};
function sbGates(){const R=SB.reg,id=SB.regId;SB.gates=[];
  if(SB.kind==='toy'){const b=SB.col.b,cx=R.room?SB_RX:(g=>(g+.75)*SB_M),cz=R.room?SB_RZ:(g=>-(g-3.5)*SB_M);
    for(const d of R.gates||[]){if(!sbRegOf(d.to))continue;const g={id:d.id,to:d.to,at:d.at,label:d.label,hw:d.hw||SB_GW,plain:!!d.plain,y:0};
      if(d.w==='E'){g.x=b[1];g.z=cz(d.p);g.nx=1;g.nz=0;}else if(d.w==='W'){g.x=b[0];g.z=cz(d.p);g.nx=-1;g.nz=0;}else if(d.w==='N'){g.x=cx(d.p);g.z=b[2];g.nx=0;g.nz=-1;}else{g.x=cx(d.p);g.z=b[3];g.nx=0;g.nz=1;}
      g.tx=-g.nz;g.tz=g.nx;SB.gates.push(g);}}
  else{const L=(SB_LINKS[id]||[]).filter(t=>sbRegOf(t)),n=L.length;L.forEach((to,i)=>{const m=MAPS.find(q=>q.id===to),g={id:id+'>'+to,to,at:to+'>'+id,label:(m?m.name:to).toUpperCase(),hw:SB_GW,y:0};
      if(SB.kind==='open'){/* an arch in the crust, each neighbour its own share of the circle: the first bearing near there with clear ground in front of it */
        /* (a bearing will do when a kart can drive straight from the road out to it: the line from the crust inward is followed to the road, then walked back out
           as a kart would drive it, three abreast, with no wall, no cliff, no water and no canyon on the way; and no two arches side by side) */
        const ray=a=>{const c=Math.cos(a),q=Math.sin(a),P=[];let hit=false;for(let r=SB.rim-26;r>60&&!hit;r-=10){const x=c*r,z=q*r;P.push([x,z]);const m=sbSurf(x,z);for(let e=0;e<m;e++)if(SB.S[e][2]>=0&&SB.S[e][4])hit=true;}if(!hit)return false;
          for(let e=P.length-2;e>=0;e--){const w=groundAt(P[e+1][0],P[e+1][1]);for(const o of [-9,0,9]){const x=P[e][0]-q*o,z=P[e][1]+c*o;if(sbBlocked(x,z,w)||pitAt(x,z)>1)return false;}}return true;};
        const a0=(i/n+sbSeed(id))*6.28318;let best=null;/* (where this arch stood the last time you were here, if the way to it is still clear: what counts as in the way depends a little on which far-off things were drawn in full when the place was read, and an arch must not wander between visits) */{const was=((sbSave().g||{})[id]||[]).find(q=>q[2]===g.label);if(was){const a=Math.atan2(was[1],was[0]);if(Math.abs(Math.hypot(was[0],was[1])-SB.rim)<4&&ray(a))best=a;}}for(let t=0;t<90&&best==null;t++){const a=a0+(t%2?1:-1)*Math.ceil(t/2)*.07;if(SB.gates.some(o=>Math.abs(angDiff(a,Math.atan2(o.nz,o.nx)))<.3))continue;if(ray(a))best=a;}if(best==null){best=a0;console.warn('sandbox: no clear way to an arch',id,to);}
        g.nx=Math.cos(best);g.nz=Math.sin(best);g.x=g.nx*SB.rim;g.z=g.nz*SB.rim;g.y=groundAt(g.x-g.nx*24,g.z-g.nz*24);}
      else{/* where you keep to the road: an arch over the left-hand lane, the gates spread round the lap and clear of the start line */
        /* (never on a bend, a jump, a loop or a glide: the first clear lap point either side of its share of the lap) */const far=(j,q,m)=>{let d=j-q;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)>m;},clear=j=>{const p=track[j];if(Math.abs(p.bend||0)>.3||p.open||j<N*.05||j>N*.95)return false;if(GLIDE){let d=j-GLIDE.rj;if(d>N/2)d-=N;if(d<-N/2)d+=N;let w=GLIDE.j1-GLIDE.rj;if(w<0)w+=N;if(d>-30&&d<w+30)return false;}return ramps.every(r=>far(j,r.j,30))&&LOOPS.every(L=>far(j,L.j,40));};let j=Math.round(((i+.5)/n*.86+.07)*N)%N;for(let q=0;q<60;q++){const a=(j+q*5)%N,b=((j-q*5)%N+N)%N;if(clear(a)){j=a;break;}if(clear(b)){j=b;break;}}const p=track[j],lat=-RW*.5;g.road=1;g.j=j;g.x=p.x+p.nx*lat;g.z=p.y+p.ny*lat;g.nx=p.tx;g.nz=p.ty;g.y=groundAt(g.x,g.z)+(p.ey||0);g.hw=RW*.4;}
      g.tx=-g.nz;g.tz=g.nx;SB.gates.push(g);});}
  /* drawn (web v193, the owner: "i dont want the car to dissappear i want to drive on a track where it looks like im going through a tunnel with
     this sort of design", with a picture of bright streaks flying out of the middle of a black screen; "add signs above the tunnels"):
       the mouth      an arch on the wall, its face the warp picture (streaks fly out from its middle); a kart that has driven into it is still drawn
                      (sbPull) so it is seen going in, not cut off by the wall
       the tunnel     behind the mouth: streaks rush along its walls toward you, a lit road on its floor, a bright end. The kart drives it for real
       the sign       a board above the mouth with the name of where it leads (a gantry across the garage's open door)
     On a road in the sky the mouth is an arch over the left-hand lane with no tunnel behind it: the kart drives the warp tunnel while the next place loads (sbTravel). */
  for(const g of SB.gates){const road=!!g.road,proud=R.room?6:0,G=new THREE.Group(),W=g.hw+1,H=road?31:27,arch=(w,h)=>{const sh=new THREE.Shape();sh.moveTo(-w,0);sh.lineTo(-w,h-w*.55);sh.absarc(0,h-w*.55,w,Math.PI,0,true);sh.lineTo(w,0);sh.lineTo(-w,0);return sh;};
    const neon=road&&!!(MAPS[mapIdx]&&MAPS[mapIdx].neon),wood=R.room?'#7a5636':SB.kind==='open'?'#a9743c':'#5d5148';
    /* the sign: its board, the name as large as fits, an arrow either side */
    const sign=(bw,bh)=>{const cv=cnv(1024,256),q=cv.getContext('2d');q.fillStyle=neon?'#06121c':'#f6ecd4';q.fillRect(0,0,1024,256);q.strokeStyle=neon?'#39d0ff':'#5a3d22';q.lineWidth=18;q.strokeRect(9,9,1006,238);q.fillStyle=neon?'#bff1ff':'#3a2513';q.textAlign='center';q.textBaseline='middle';
      let fs=150;q.font='900 '+fs+'px Arial';while(q.measureText(g.label).width>800&&fs>40){fs-=4;q.font='900 '+fs+'px Arial';}q.fillText(g.label,512,134);
      for(const s of [-1,1]){const x=512+s*462;q.beginPath();q.moveTo(x,84);q.lineTo(x+26,168);q.lineTo(x-26,168);q.closePath();q.fillStyle=neon?'#39d0ff':'#b4472a';q.fill();}
      const tx=T2(cv);tx.userData.keepCanvas=true;const B=new THREE.Group(),back=new THREE.Mesh(new THREE.BoxGeometry(bw+2.4,bh+2.4,1.6),neon?new THREE.MeshStandardMaterial({color:'#0c1822',emissive:'#39d0ff',emissiveIntensity:.9,roughness:.4}):new THREE.MeshStandardMaterial({color:wood,roughness:.75}));B.add(back);
      for(const s of [1,-1]){/* (its face is not shaded: a sign in a dark corner of a room reads as well as one in the sun) */const f=new THREE.Mesh(new THREE.PlaneGeometry(bw,bh),new THREE.MeshBasicMaterial({map:tx,toneMapped:false}));f.position.z=s*.9;if(s<0)f.rotation.y=Math.PI;B.add(f);}return B;};
    if(g.plain){/* the garage's open door: a gantry you drive out under */const bw=150,bh=37.5,B=sign(bw,bh);B.position.set(0,66,-14);G.add(B);for(const s of [-1,1]){const p=new THREE.Mesh(new THREE.CylinderGeometry(2.2,2.6,84,10),new THREE.MeshStandardMaterial({color:'#4a4d52',roughness:.5,metalness:.4}));p.position.set(s*(bw/2+4),42,-14);G.add(p);}}
    else{const face=new THREE.Mesh(new THREE.ShapeGeometry(arch(W,H),14),sbWarpMat(0,{c:[0,H*.46],s:H*1.05,core:.5}));face.position.z=proud+(R.room?1.2:.9);G.add(face);
      const ring=arch(W+3.4,H+3.4);ring.holes.push(arch(W,H));const fm=neon?new THREE.MeshStandardMaterial({color:'#12202c',emissive:'#39d0ff',emissiveIntensity:1.6,roughness:.4}):new THREE.MeshStandardMaterial({color:wood,roughness:.7});
      const fr=new THREE.Mesh(new THREE.ExtrudeGeometry(ring,{depth:neon?2.4:1.6,bevelEnabled:false,curveSegments:12}),fm);fr.position.z=proud+.2;fr.castShadow=!neon;G.add(fr);
      if(!road){const L=SB_GLEN+20,rx=W+3,ry=H+7,tg=new THREE.CylinderGeometry(1,1,L,32,1,true);tg.rotateX(Math.PI/2);tg.translate(0,0,-L/2);tg.scale(rx,ry,1);
        const tube=new THREE.Mesh(tg,sbWarpMat(1,{rep:L/60,mat:{side:THREE.BackSide}}));tube.position.z=-.3;G.add(tube);
        const fl=new THREE.Mesh(new THREE.PlaneGeometry(2*rx,L),new THREE.MeshBasicMaterial({map:sbRoadTex(L),toneMapped:false}));fl.rotation.x=-Math.PI/2;fl.position.set(0,.3,-L/2-.3);G.add(fl);
        const end=new THREE.Mesh(new THREE.PlaneGeometry(2*rx,ry),sbWarpMat(0,{c:[.5,.42],s:.55,core:1.1}));end.position.set(0,ry/2,-L+.6);G.add(end);g.inside=[tube,fl,end];tube.visible=fl.visible=end.visible=false;/* (web v194, the owner: "some of the space effect is not just in the tunnels but also behind them": the tunnel's walls are drawn from their inner side, which from outside means its far wall shows through the near one, over a pizza's low crust. sbWarpTick shows it only to a camera that has gone through the mouth) */g.endAt=[g.x+g.nx*(L-1),g.y+ry*.42,g.z+g.nz*(L-1)];}
      /* (the owner, 2026-11-14: "some of the signs for the locations are covered make sure they are more visible": the board stands on two posts well above the
         arch and in front of it, where neither the arch's own rim nor the kart in front of the camera is across it) */
      const bw=Math.max(2*W+40,84),bh=bw/4,B=sign(bw,bh),by=H+17+bh/2,bz=proud+5;B.position.set(0,by,bz);G.add(B);
      for(const sd of [-1,1]){const post=new THREE.Mesh(new THREE.BoxGeometry(2.2,by-H+2,2.2),neon?new THREE.MeshStandardMaterial({color:'#12202c',emissive:'#39d0ff',emissiveIntensity:1.2,roughness:.4}):new THREE.MeshStandardMaterial({color:wood,roughness:.75}));post.position.set(sd*(W+1.5),(by+H-2)/2,bz-1.3);G.add(post);}}
    G.position.set(g.x,g.y,g.z);G.rotation.y=Math.atan2(-g.nx,-g.nz);/* its face looks back at whoever drives up to it */G.userData.sbGate=true;G.traverse(o=>{o.userData.sunlit=true;o.userData.noCol=true;});SB.grp.add(G);}}
/* ---- the warp look ----
   sbWarpMat(tube, o): 0 a flat face (streaks fly out from the point o.c of its own uv, o.s the size of the picture, o.core a bright middle);
   1 the inside of a tunnel (uv.x round it, uv.y along it: the streaks run along it toward whoever is driving in, SB_WV counts their way).
   One clock for every face, one for every tunnel; nothing here is a picture file, so a phone has nothing to lose (freeCanvases). */
const SB_WU={value:0},SB_WV={value:0};
function sbWarpMat(tube,o){o=o||{};return new THREE.ShaderMaterial(Object.assign({uniforms:{uT:tube?SB_WV:SB_WU,uTube:{value:tube?1:0},uRep:{value:o.rep||1},uCore:{value:o.core||0},uC:{value:new THREE.Vector2(o.c?o.c[0]:.5,o.c?o.c[1]:.5)},uS:{value:o.s||1}},
  vertexShader:'varying vec2 vU;void main(){vU=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
  fragmentShader:['varying vec2 vU;uniform float uT,uTube,uRep,uCore,uS;uniform vec2 uC;',
   'float h1(float n){return fract(sin(n*91.345)*47453.5453);}',
   'vec3 lay(float a,float r,float n,float sd){float b=floor(a*n),f=fract(a*n),id=b+sd*1000.;float on=step(.5,h1(id)),sp=.55+h1(id+7.)*1.5,ph=fract(r*(1.1+sd*.45)-uT*sp+h1(id+3.)),len=.22+.5*h1(id+11.);',
   '  float s=smoothstep(0.,.07,ph)*smoothstep(len,len*.25,ph),w=smoothstep(.42,.05,abs(f-.5)),t=h1(id+5.);',
   '  vec3 col=t<.45?vec3(1.,.97,1.):t<.72?vec3(.62,.45,1.):t<.9?vec3(.4,.6,1.):vec3(.45,1.,.7);return col*on*s*w*(.5+.5*h1(id+13.));}',
   'void main(){float a,r,d=0.;if(uTube>.5){a=vU.x;r=vU.y*uRep;}else{vec2 p=(vU-uC)/uS;d=length(p)*2.;a=atan(p.y,p.x)/6.2831853+.5;r=log(d+.03)*.6;}',
   '  vec3 c=lay(a,r,70.,0.)+lay(a,r,120.,1.)+lay(a,r,190.,2.)*.8;',
   '  if(uTube<.5){c*=smoothstep(.02,.3,d);c+=vec3(.86,.8,1.)*uCore*exp(-d*d*10.);}else c*=1.15;',
   '  gl_FragColor=vec4(c+vec3(.012,.006,.03),1.);}'].join('\n'),side:THREE.DoubleSide,toneMapped:false,fog:false},o.mat||{}));}
/* the road on the tunnel's floor: dark, a glowing line down each edge, dashes down the middle */
function sbRoadTex(L){if(!SB.roadCv){const c=SB.roadCv=cnv(256,256),q=c.getContext('2d');q.fillStyle='#07050e';q.fillRect(0,0,256,256);const gl=(x,w,col)=>{const gr=q.createLinearGradient(x-w,0,x+w,0);gr.addColorStop(0,'rgba(0,0,0,0)');gr.addColorStop(.5,col);gr.addColorStop(1,'rgba(0,0,0,0)');q.fillStyle=gr;q.fillRect(x-w,0,2*w,256);};
    gl(22,16,'rgba(150,110,255,.95)');gl(234,16,'rgba(150,110,255,.95)');gl(22,4,'#ffffff');gl(234,4,'#ffffff');q.fillStyle='rgba(215,205,255,.9)';q.fillRect(122,20,12,110);q.fillStyle='rgba(120,160,255,.35)';for(const x of [72,184])q.fillRect(x,150,4,90);}
  const t=T2(SB.roadCv);t.userData.keepCanvas=true;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(1,L/42);return t;}
/* a kart inside a passage is drawn in front of the wall it has driven through (its depth is pulled toward the camera; its own parts keep their order) */
function sbPull(on){if(!!SB.pull===on||!player||!player.m)return;SB.pull=on;player.m.g.traverse(o=>{if(!o.isMesh||!o.material)return;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(on){if(m.userData.sbPO===undefined)m.userData.sbPO=[m.polygonOffset,m.polygonOffsetFactor,m.polygonOffsetUnits];m.polygonOffset=true;m.polygonOffsetFactor=0;m.polygonOffsetUnits=-1.4e7;}
    else if(m.userData.sbPO!==undefined){m.polygonOffset=m.userData.sbPO[0];m.polygonOffsetFactor=m.userData.sbPO[1];m.polygonOffsetUnits=m.userData.sbPO[2];delete m.userData.sbPO;}}});}
/* each frame: the warp clocks, and whether the kart is to be drawn through a wall */
function sbWarpTick(dt){const k=player;SB_WU.value=(SB_WU.value+dt*.5)%1000;let pull=false,dir=1;if(SBX&&k)for(const g of SB.gates){if(g.road||g.plain)continue;const dk=(k.rx-g.x)*g.nx+(k.ry-g.z)*g.nz,lk=(k.rx-g.x)*g.tx+(k.ry-g.z)*g.tz,dc=(camera.position.x-g.x)*g.nx+(camera.position.z-g.z)*g.nz,lc=(camera.position.x-g.x)*g.tx+(camera.position.z-g.z)*g.tz;
    if(g.inside){const v=dc>-((SB.reg&&SB.reg.room?7.2:.9)+2)&&Math.abs(lc)<g.hw+14;/* (from just before the mouth's own face, which hides it until then) */if(g.inside[0].visible!==v)for(const o of g.inside)o.visible=v;}
    if((dk>-4&&Math.abs(lk)<g.hw+8)||(dc>0&&Math.abs(lc)<g.hw+12)){pull=true;if(Math.cos(k.rma)*g.nx+Math.sin(k.rma)*g.nz<0)dir=-1;}}
  SB_WV.value=(SB_WV.value+dt*.9*dir+1000)%1000;sbPull(pull);}
/* ---- the no-stop tunnel (web v199) ----
   The owner, 2026-11-14: "the game will never freeze or stop to load it will be one fluid drive through the tunnel right out to the other
   side". (Until v198 the picture was held by a still cover for the second or more the load took.)
   Through a gate the kart drives on in a tunnel of its own (SB.ws: a scene holding only the tube, its road, the light at the end, two lamps
   and a copy of the kart, drawn through the game's own post pass: patch 34's drawNow) while the next place is built a few milliseconds a
   frame. The web build cuts the builders into slices (build/slices.txt, tools/jsparse/slice.js: loadMap.G and sbArm.G are the sliced
   forms; run from the source unbuilt they are missing and the load is one step, as before). The new place's shaders are then compiled in
   the background where the browser can (KHR_parallel_shader_compile), its pictures go to the graphics card one a slice, and warmScene draws
   it once. Then the kart is set down inside the far gate's own tunnel, driving out, and the race goes on.
   While this runs nothing reads the place being built: the frame loop calls sbWarpFrame instead of the race (state 'loading'), and the
   HUD waits. KEEP IT: sbTripG does what the old sbTravel did, in the same order; a new step in a place's load belongs in the sliced path. */
const SB_WL=1800,_sbWM=new THREE.Matrix4(),_sbWN=new THREE.Matrix4(),_sbWQ=new THREE.Quaternion(),_sbWY=new THREE.Vector3(0,1,0);
function sbWarpScene(){let w=SB.ws;if(w)return w;const S=new THREE.Scene(),rx=30,ry=34,L=SB_WL;S.background=new THREE.Color('#05030a');
  const tg=new THREE.CylinderGeometry(1,1,L,40,1,true);tg.rotateX(Math.PI/2);tg.translate(0,0,-L/2+80);tg.scale(rx,ry,1);
  const tube=new THREE.Mesh(tg,sbWarpMat(1,{rep:L/60,mat:{side:THREE.BackSide}}));tube.frustumCulled=false;S.add(tube);
  const ft=sbRoadTex(L),fl=new THREE.Mesh(new THREE.PlaneGeometry(2*rx,L),new THREE.MeshBasicMaterial({map:ft,toneMapped:false}));fl.rotation.x=-Math.PI/2;fl.position.set(0,.3,-L/2+80);fl.frustumCulled=false;S.add(fl);
  const end=new THREE.Mesh(new THREE.PlaneGeometry(2*rx,ry),sbWarpMat(0,{c:[.5,.42],s:.55,core:1.1}));end.position.set(0,ry/2,-L+81);S.add(end);
  S.add(new THREE.HemisphereLight('#d6caff','#1c1030',1.25));const dl=new THREE.DirectionalLight('#ffffff',1.1);dl.position.set(0,60,40);S.add(dl);S.add(dl.target);
  const cam=new THREE.PerspectiveCamera(60,16/9,1,4000);w=SB.ws={S,cam,ft,kart:null,base:new THREE.Vector3(),cb:new THREE.Vector3(),lat:0,cl:0,yaw:0};return w;}
/* the copy of the player's kart, and the camera, moved as one from where they are to the tunnel's start (the kart at the origin facing -z) */
function sbWarpKart(){const w=sbWarpScene(),k=player;if(w.kart){w.S.remove(w.kart);w.kart=null;}if(!k||!k.m||!k.m.g)return;let top=k.m.g;while(top.parent&&top.parent!==scene)top=top.parent;
  top.updateMatrixWorld(true);camera.updateMatrixWorld(true);const c=top.clone(true);c.traverse(o=>{o.frustumCulled=false;});
  _sbWM.makeRotationY(k.rma+Math.PI/2);_sbWN.makeTranslation(-k.rx,-(k.rz==null?k.wy||0:k.rz),-k.ry);_sbWM.multiply(_sbWN);
  _sbWN.multiplyMatrices(_sbWM,top.matrixWorld);_sbWN.decompose(c.position,c.quaternion,c.scale);w.base.copy(c.position);w.q0=c.quaternion.clone();
  _sbWN.multiplyMatrices(_sbWM,camera.matrixWorld);_sbWN.decompose(w.cam.position,w.cam.quaternion,w.cam.scale);w.cb.copy(w.cam.position);
  w.cam.fov=camera.fov;w.cam.near=camera.near;w.cam.far=4000;w.cam.aspect=camera.aspect;w.cam.updateProjectionMatrix();w.S.add(c);w.kart=c;w.lat=0;w.cl=0;w.yaw=0;}
/* through a gate (or fast travel: g.start): from here the kart is in the tunnel until the next place is ready */
function sbTravel(g){if(SB.trav||SB.warp)return;if(g.start&&SBA.act&&!SBA.retry)sbActEnd('cancel');/* (fast travel cannot finish a delivery) */const mi=MAPS.findIndex(m=>m.id===g.to);if(mi<0||!sbRegOf(g.to))return;SB.trav=g;const k=player,sp=Math.max(70,Math.abs(k.speed));
  const w=sbWarpScene();sbWarpKart();w.sp=sp;w.t=0;w.minT=g.start?1.1:.75;w.job=sbTripG(g,mi,sp);w.slow=0;w.log=[];w.pv=null;SB.warp=w;state='loading';sbRaceBtn(false);sbPull(false);}
function* sbTripG(g,mi,sp){const k=player;
  try{projectiles.forEach(p=>scene.remove(p.mesh));hazards.forEach(h=>scene.remove(h.mesh));projectiles=[];hazards=[];
    if(mi!==mapIdx||curRev){mapIdx=mi;try{store.set('crust-map',mi);}catch(e){}if(loadMap.G)yield* loadMap.G(mi,false);else loadMap(mi,false);}for(const q of karts){q.idx=0;q.prog=0;q.loop=null;q.sc=null;q.glide=false;}
    yield "trip1";let ok=false;Promise.all(Object.values(PROPT).map(t=>t.image&&t.image.decode&&!t.image.complete?t.image.decode().catch(()=>{}):null)).then(()=>{ok=true;},()=>{ok=true;});const t0=performance.now();while(!ok&&performance.now()-t0<5000)yield "trip2";}catch(e){console.warn('sandbox travel',e);}
  if(sbArm.G)yield* sbArm.G();else sbArm();yield "trip3";const a=g.start?null:SB.gates.find(q=>q.id===g.at)||SB.gates[0];
  if(a&&a.road){k.x=k.px=a.x+a.nx*34;k.y=k.py=a.z+a.nz*34;k.a=k.ma=k.pa=k.pma=Math.atan2(a.nz,a.nx);k.idx=(a.j+Math.round(34/(T.L/N)))%N;}
  else if(a){const out=a.plain?46:SB_GLEN-60;k.x=k.px=a.x+a.nx*out;k.y=k.py=a.z+a.nz*out;const h=Math.atan2(-a.nz,-a.nx);k.a=k.ma=k.pa=k.pma=h;}
  else{/* no gate to come out of (fast travel): the start line, a little behind it */const j=(N-Math.round(40/(T.L/N)))%N,p=track[j];k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.idx=j;}
  k.speed=sp;k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.charge=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;
  if(SBF){const lvl=a&&!a.road?a.y:((SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0));k.wy=k.pwy=k.lastG=sbG(k.x,k.y,lvl+2);k.idx=sbIdx(k,k.idx);}else k.wy=k.pwy=k.lastG=kGround(k);
  k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rg=k.wy;k.rma=k.ma;cam.a=k.ma;camSnap=true;if(g.shop)sbShopPut(k);/* (fast travel to the mechanic's shop) */yield "trip4";
  yield* sbWarmG();}
/* the new place made ready to draw, a little at a time (done at once, as warmScene alone does it, this was one wait of 0.3 to 1.8 s):
   1. its shaders: renderer.compile on eight things at a time (F: a scene that lends the real one's lights, environment and fog, so the
      programs are the very ones the real draw will ask for), with the built game's three.js told not to wait for each (renderer.__crDefer);
   2. a frame at a time until the driver has finished them (KHR_parallel_shader_compile);
   3. its pictures to the graphics card, one a step;
   4. each thing drawn once on its own into the post pass's target (render layer 30: everything else and the shadows left out). A driver
      finishes a shader for the way it is drawn at its first draw (about 0.1 s each, ten or so on a new place: measured on ANGLE/D3D11) and the
      shapes go up to the card; one a step spreads that out;
   5. warmScene, which then has little left to do (about 0.09 s).
   In Sandbox every shader compiled is then kept (its use count raised once): a place you come back to has none of this to do. */
function* sbWarmG(){try{sunShadeAll();}catch(e){}yield "warm1";
  const objs=[];scene.traverse(o=>{if(o.material)objs.push(o);});
  try{const gl=renderer.getContext(),ext=renderer.extensions.get('KHR_parallel_shader_compile');
    if(ext){const F=new THREE.Scene();F.environment=scene.environment;F.fog=scene.fog;F.traverseVisible=f=>scene.traverseVisible(x=>{if(x.isLight)f(x);});
      for(let i=0;i<objs.length;i+=8){const ch=objs.slice(i,i+8);F.traverse=f=>{for(const x of ch)f(x);};const ck=renderer.debug.checkShaderErrors;renderer.debug.checkShaderErrors=false;renderer.__crDefer=true;
        try{renderer.compile(F,camera);}catch(e){console.warn('sandbox shaders',e);}finally{renderer.debug.checkShaderErrors=ck;renderer.__crDefer=false;}yield "warm2";}
      const t0=performance.now();for(;;){let all=true;for(const p of renderer.info.programs)if(!gl.getProgramParameter(p.program,ext.COMPLETION_STATUS_KHR)){all=false;break;}if(all||performance.now()-t0>8000)break;yield "warm3";}}}catch(e){console.warn('sandbox shaders',e);}
  if(typeof renderer.initTexture==='function'){const seen=new Set(),tex=[];for(const o of objs){const ms=Array.isArray(o.material)?o.material:[o.material];for(const m of ms)for(const key in m){const v=m[key];if(v&&v.isTexture&&!seen.has(v)){seen.add(v);tex.push(v);}}}
    for(const t of tex){try{if(!t.image||t.image.width||t.image.data||t.isRenderTargetTexture)renderer.initTexture(t);}catch(e){}yield "warm4";}}
  {const lights=[];let wc=null,tgt=null;const au=renderer.shadowMap.autoUpdate,nu=renderer.shadowMap.needsUpdate;
    try{scene.traverse(x=>{if(x.isLight&&!x.layers.isEnabled(30)){x.layers.enable(30);lights.push(x);}});wc=camera.clone();wc.layers.set(30);
      try{if(!LOWQF()&&CFG.post!==false){postInit();const sz=renderer.getDrawingBufferSize(v2);postSize(sz.x,sz.y);tgt=POST.rt;}}catch(e){}if(!tgt)tgt=SB.wrt||(SB.wrt=new THREE.WebGLRenderTarget(64,64));
      for(const x of objs){if(!(x.isMesh||x.isPoints||x.isLine||x.isSprite))continue;const fc=x.frustumCulled,L=x.layers.mask;x.layers.enable(30);x.frustumCulled=false;renderer.shadowMap.autoUpdate=false;renderer.shadowMap.needsUpdate=false;
        try{renderer.setRenderTarget(tgt);renderer.render(scene,wc);}catch(e){}finally{renderer.setRenderTarget(null);x.layers.mask=L;x.frustumCulled=fc;renderer.shadowMap.autoUpdate=au;}yield "warm5";}}
    catch(e){console.warn('sandbox draw',e);}finally{for(const x of lights)x.layers.disable(30);renderer.shadowMap.autoUpdate=au;renderer.shadowMap.needsUpdate=nu;}}
  try{warmScene();}catch(e){}
  if(SBX)for(const p of renderer.info.programs)if(!p.__crKeep){p.__crKeep=1;p.usedTimes++;}}
/* each frame in the tunnel: drive, draw, then build for what is left of the frame */
function sbWarpFrame(dt,time){const w=SB.warp,k=player;w.t+=dt;
  if(w.kart){const st=clamp((keys.right?1:0)-(keys.left?1:0)+(PAD.act?PAD.steer:0),-1,1);w.lat=clamp(w.lat+st*dt*42,-14,14);w.yaw+=(-st*.16-w.yaw)*Math.min(1,dt*8);w.cl+=(w.lat*.8-w.cl)*Math.min(1,dt*5);
    w.kart.position.set(w.base.x+w.lat,w.base.y+Math.sin(time*11)*.12,w.base.z);_sbWQ.setFromAxisAngle(_sbWY,w.yaw);w.kart.quaternion.copy(_sbWQ).multiply(w.q0);w.cam.position.set(w.cb.x+w.cl,w.cb.y,w.cb.z);}
  if(k)k.speed=w.sp;SB_WU.value=(SB_WU.value+dt*.5)%1000;SB_WV.value=(SB_WV.value+dt*.9*Math.max(.7,w.sp/150)+1000)%1000;w.ft.offset.y=(w.ft.offset.y+w.sp*dt*w.ft.repeat.y/SB_WL)%1;
  if(Math.abs(w.cam.aspect-camera.aspect)>1e-3){w.cam.aspect=camera.aspect;w.cam.updateProjectionMatrix();}
  const td=performance.now();postRender.s=w.S;postRender.c=w.cam;try{drawNow();}finally{postRender.s=postRender.c=null;}{const d=performance.now()-td;if(d>30&&w.log.length<24)w.log.push([Math.round(d),'draw',w.pv]);}
  if(w.job){const t0=performance.now(),B=COARSE?6:9;try{for(;;){let r;for(let i=0;i<16;i++){const a=performance.now();r=w.job.next();const d=performance.now()-a;if(d>30&&w.log.length<24)w.log.push([Math.round(d),w.pv]);/* (the slices that took long, and the yield before each: SB.lastWarp.log; ids in the build's SLICE_MAP) */w.pv=r.value;if(r.done)break;}if(r.done){w.job=null;break;}if(performance.now()-t0>B)break;}}catch(e){console.warn('sandbox travel',e);w.job=null;}
    const d=performance.now()-t0;if(d>w.slow)w.slow=d;}
  if(!w.job&&w.t>=w.minT)sbWarpOut();}
/* at the start of Sandbox (sbStart): the tunnel's own scene and the kart's copy drawn once out of sight, so the first trip does not stop to
   compile the kart's shaders for the tunnel's lights (0.3 s, measured) */
function sbWarpPrime(){const w=sbWarpScene();sbWarpKart();if(!w.kart)return;let tgt=null;try{if(!LOWQF()&&CFG.post!==false){postInit();const sz=renderer.getDrawingBufferSize(v2);postSize(sz.x,sz.y);tgt=POST.rt;}}catch(e){}if(!tgt)tgt=SB.wrt||(SB.wrt=new THREE.WebGLRenderTarget(64,64));
  try{renderer.compile(w.S,w.cam);renderer.setRenderTarget(tgt);renderer.render(w.S,w.cam);}catch(e){console.warn('sandbox warp',e);}finally{renderer.setRenderTarget(null);w.S.remove(w.kart);w.kart=null;}}
function sbWarpOut(){const w=SB.warp;SB.warp=null;if(w&&w.kart){w.S.remove(w.kart);w.kart=null;}SB.lastWarp=w?{t:+w.t.toFixed(2),slow:Math.round(w.slow),log:w.log}:null;
  SB.cool=1;state='race';acc=0;SB.trav=null;SB.hudT=0;sbHud();showBanner(SB.reg.name,2,'sm');if(SBA.retry)sbActArrived();}
/* ---- a race from its start line ----
   The start line of the region's track carries a marker: a chequered ring on the road and a small chequered flag turning above it. Drive up
   to it and a button offers the race (tap it; Enter on a keyboard; D-pad up on a controller). The race is an ordinary single race on this
   track at the chosen speed class; when it is over, or left, you are back in Sandbox at the same start line. */
function sbFlag(){if(SB.flag&&SB.flag.glow)SB.flag.glow.dispose();const p=track[0],e=(SB.kind==='toy'?0:groundAt(p.x,p.y))+(p.ey||0),c=cnv(64,64),g=c.getContext('2d');for(let i=0;i<4;i++)for(let j=0;j<4;j++){g.fillStyle=(i+j)%2?'#141210':'#fbf6ea';g.fillRect(i*16,j*16,16,16);}
  const t1=T2(c,6,1),t2=T2(c,1.5,1),G=new THREE.Group();t1.userData.keepCanvas=t2.userData.keepCanvas=true;
  const ring=new THREE.Mesh(new THREE.RingGeometry(11.5,15.5,40,1),new THREE.MeshBasicMaterial({map:t1,side:THREE.DoubleSide,toneMapped:false}));{const uv=ring.geometry.attributes.uv,ps=ring.geometry.attributes.position;for(let i=0;i<uv.count;i++){const a=Math.atan2(ps.getY(i),ps.getX(i)),r=Math.hypot(ps.getX(i),ps.getY(i));uv.setXY(i,a/6.28318+.5,r>13?1:0);}}
  ring.rotation.x=-Math.PI/2;ring.position.y=.55;G.add(ring);
  const F=new THREE.Group(),pole=new THREE.Mesh(new THREE.CylinderGeometry(.45,.45,17,8),new THREE.MeshStandardMaterial({color:'#e9e4d8',roughness:.5,metalness:.3}));pole.position.y=8.5;F.add(pole);
  const fl=new THREE.Mesh(new THREE.PlaneGeometry(10,6.6),new THREE.MeshBasicMaterial({map:t2,side:THREE.DoubleSide,toneMapped:false}));fl.position.set(5,13.6,0);F.add(fl);F.position.y=12;G.add(F);
  let glow=null;try{glow=glowMat('#fff2c0').clone();/* (its own copy: the clock dims it, and glowMat's are shared) */const sp=new THREE.Sprite(glow);sp.scale.setScalar(30);sp.position.y=22;G.add(sp);}catch(e){}
  G.position.set(p.x,e,p.y);G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);SB.flag={G,F,x:p.x,z:p.y,y:e,mats:[ring.material,fl.material],glow};}
function sbRaceBtn(on){let b=SB.raceEl;if(!b){if(!on)return;b=SB.raceEl=document.createElement('button');b.id='sbRace';b.type='button';
    b.style.cssText='position:absolute;left:50%;bottom:max(96px,calc(env(safe-area-inset-bottom) + 96px));transform:translateX(-50%);z-index:7;font:800 15px/1.15 system-ui,sans-serif;color:#1b0f0b;background:linear-gradient(#ffd97a,#f5b62e);border:0;border-radius:14px;padding:10px 18px 10px 44px;box-shadow:0 4px 0 #9b6a10,0 8px 18px rgba(0,0,0,.4);cursor:pointer;white-space:nowrap;text-align:left';
    b.innerHTML='<i style="position:absolute;left:12px;top:50%;width:22px;height:22px;margin-top:-11px;border-radius:5px;background:conic-gradient(#141210 25%,#fbf6ea 0 50%,#141210 0 75%,#fbf6ea 0) 0 0/11px 11px"></i><span id="sbRaceT"></span><small style="display:block;font-weight:600;font-size:11px;opacity:.75" id="sbRaceS"></small>';
    b.onclick=e=>{e.preventDefault();sbRaceHere();};b.addEventListener('pointerdown',e=>e.stopPropagation());stage.appendChild(b);
    addEventListener('keydown',e=>{if(SBX&&SB.raceOn&&state==='race'&&e.code==='Enter'){e.preventDefault();sbRaceHere();}});}
  if(on===SB.raceOn)return;SB.raceOn=on;b.hidden=!on;if(on){const m=MAPS[mapIdx],touch=typeof COARSE!=='undefined'&&COARSE;document.getElementById('sbRaceT').textContent='Race here: '+m.name;document.getElementById('sbRaceS').textContent=CLASSES[clsKey].label+' \u00b7 single race'+(touch?' \u00b7 tap':' \u00b7 Enter, or D-pad up');}}
function sbRaceHere(){if(!SBX||SB.trav||state!=='race'||raceLoading)return;if(SBA.act)sbActEnd('cancel');SB.back=SB.regId;sbRaceBtn(false);mode='single';goRace(mapIdx);}
/* leaving a race that began at a start line in Sandbox: back to Sandbox there (the engine's toMenu asks this first) */
function sbBack(){if(!SB.back)return false;const id=SB.back;SB.back=null;if(NET.cfg||NET.role)return false;const mi=MAPS.findIndex(m=>m.id===id);if(mi<0||!sbRegOf(id))return false;mode='sb';results.hidden=true;pauseOv.hidden=true;goRace(mi);return true;}
/* ---- coins ---- */
/* a region's places are written in its own measure: the garden in metres (sbGX, sbGZ), a room in centimetres from its middle, x east and y north (SB_RX, SB_RZ) */
const SB_RX=c=>c*3.47,SB_RZ=c=>-c*3.47;
function sbCoins(){const R=SB.reg,sv=sbSave(),C=SB.coins=[],put=(x,y,z,rare,id)=>C.push({x,y,z,rare:!!rare,id,t:0,ph:C.length*.37}),sbGX=R.room?SB_RX:(g=>(g+.75)*SB_M),sbGZ=R.room?SB_RZ:(g=>-(g-3.5)*SB_M),HM=R.room?3.47:SB_M,STEPL=R.room?15:.15;
  /* A kart is 12 units long (a 7.5 cm toy), so a trail of coins is one every 45 units or so: four a second at speed.
     Along the track: a run of six every 3 m, each run a little to one side then the other, none on the loop's own stretch */
  const sl=T.L/N,stp=Math.round(3*SB_M/sl),gap=Math.max(1,Math.round(45/sl));for(let j0=Math.round(stp/2),g=0;j0<N;j0+=stp,g++){if(LOOPS.some(L=>{let d=j0-L.j;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)*sl<420;}))continue;const lat=(g%3-1)*13;for(let q=0;q<6;q++){const p=track[(j0+q*gap)%N],x=p.x+p.nx*lat,z=p.y+p.ny*lat;put(x,(SB.kind==='toy'?0:groundAt(x,z))+(p.ey||0)+5.4,z);}}
  if(R.auto&&SB.kind==='open'){/* three pepperoni coins out on the pizza, away from the road: the same places every time (the track's name is the seed); each must have open ground between it and the road */
    const rnd=prng(hashStr(SB.regId)+5);let made=0;for(let t=0;t<400&&made<3;t++){const a=rnd()*6.28318,r=(.3+rnd()*.6)*SB.rim,x=Math.cos(a)*r,z=Math.sin(a)*r,g0=groundAt(x,z);if(sbBlocked(x,z,g0))continue;
      let bj=0,bd=1e18;for(let j=0;j<N;j+=4){const p=track[j],d=(p.x-x)**2+(p.y-z)**2;if(d<bd){bd=d;bj=j;}}const d=Math.sqrt(bd);if(d<WALLD+60||C.some(c=>c.rare&&(c.x-x)**2+(c.z-z)**2<400*400))continue;
      const p=track[bj];let ok=true,pw=groundAt(p.x,p.y);/* (walked from the road to the coin, as a kart would drive it) */for(let q=d-RW;q>=0&&ok;q-=10){const xx=x+(p.x-x)*q/d,zz=z+(p.y-z)*q/d;if(sbBlocked(xx,zz,pw)||pitAt(xx,zz)>1)ok=false;pw=groundAt(xx,zz);}if(!ok)continue;put(x,g0+8,z,true,SB.regId+':'+made);made++;}}
  if(R.auto&&SB.kind==='road')for(const [f,i] of [[.37,0],[.81,1]]){/* two on the road's far edge */const p=track[Math.round(f*N)%N],x=p.x+p.nx*(RW-9),z=p.y+p.ny*(RW-9);put(x,groundAt(x,z)+(p.ey||0)+8,z,true,SB.regId+':'+i);}
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
function sbArm(){const def=MAPS[mapIdx],R=def&&sbRegOf(def.id),on=mode==='sb'&&!NET.cfg&&!!R;if(!on){if(SBX)sbOff();return;}
  SBX=true;SB.regId=def.id;SB.reg=R;SB.kind=R.kind||'toy';SBF=SB.kind!=='road';BATTLE=SBF;SB.shapes=R.shapes?R.shapes():[];SB.rim=0;SB.col=null;SB.hash=null;SB.gates=[];SB.loops=LOOPS.filter(L=>L.full).map(L=>({p:L.p,g0:L.g0,r:LOOPR+34,a:-L.S-L.W-10,b:L.shift-L.S+L.W+10}));
  if(SBF){let b=TOYROOM;if(SB.kind==='open'){const r=RIM+70;b=[-r,r,-r,r];SB.rim=RIM;}else if(!b){b=[1e9,-1e9,1e9,-1e9];for(const p of track){b[0]=Math.min(b[0],p.x-400);b[1]=Math.max(b[1],p.x+400);b[2]=Math.min(b[2],p.y-400);b[3]=Math.max(b[3],p.y+400);}}sbColumns(b);sbHashTrack();}
  sbCoins();sbGates();{/* the map remembers this place's tunnels */const sv=sbSave();if(!sv.g)sv.g={};sv.g[SB.regId]=SB.gates.map(g=>[Math.round(g.x),Math.round(g.z),g.label]);sbKeep();}sbFlag();try{sbActArm();sbEggArm();}catch(e){console.warn('activities',e);}try{sbShopBuild();}catch(e){console.warn('shop',e);}SB.hudT=0;SB.msgT=0;SB.camF=1;if(!SB.trav)sbPark(false);sbMapBtn();document.body.classList.add('battle');document.body.classList.add('sbx');/* (abilities in Sandbox: web v200; on a pad Y, as in a race, since v201) */sbClockArm();}
function sbOff(){if(!SBX)return;try{sbActOff();}catch(e){}sbClockOff();/* the place's own light back, before anything else reads it */SBX=false;SBF=false;const def=MAPS[mapIdx];BATTLE=!!(def&&def.battle);if(SB.grp){/* the passages' own shapes, signs and shaders go with the place (everything else in the group is shared) */for(const G of SB.grp.children)if(G.userData.sbGate)G.traverse(o=>{if(!o.isMesh)return;o.geometry.dispose();const m=o.material;if(m.map)m.map.dispose();m.dispose();});scene.remove(SB.grp);SB.grp=null;SB.im=null;}SB.coins=[];SB.shapes=[];SB.gates=[];SB.hash=null;SB.col=null;if(SB.el)SB.el.hidden=true;SB.flag=null;sbRaceBtn(false);sbPull(false);SB.park=false;if(SB.parkEl)SB.parkEl.hidden=true;if(SB.spdEl)SB.spdEl.hidden=true;sbMapBtn();document.body.classList.toggle('battle',BATTLE);document.body.classList.remove('sbx');}
function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;if(SBF){k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}}
  if(BB.grp){scene.remove(BB.grp);BB.grp=null;}sbHud();const f=sbFound();showBanner(SB.reg.name,2.2,'md');sbClockMats();sbClockApply();try{sbWarpPrime();}catch(e){}if(SB.shopPut&&player){SB.shopPut=false;sbShopPut(player);}/* (the karts have just been built again: their paint and lights join the clock) */}
/* ---- stopping (web v193) ----
   The owner: "if you hold down both brake buttons in sandbox it should completely stop the car and there should be a park button on screen
   that will stop the car in place that way you can stop at races easier". SB.park is the Park button's state (K on a keyboard and D-pad down
   on a controller press it too; pressing the throttle again on a controller lets it off). Both brake buttons held on a touch screen stop the
   kart for as long as they are held (keys.brakeBoth, set where the touches are read). playerInput asks sbStop() and then gives no throttle
   and no brake (a held brake would reverse); sbTick takes the speed down to nothing and keeps it there. */
function sbStop(){if(!SBX)return false;const gas=!!(PAD.act&&PAD.gas);if(SB.park&&gas&&SB.pGas===false&&state==='race')sbPark(false);SB.pGas=gas;return !!SB.park||!!keys.brakeBoth;}
function sbPark(on){if(on==null)on=!SB.park;SB.park=!!on&&SBX;const b=SB.parkEl;if(b){b.setAttribute('aria-pressed',String(SB.park));b.lastChild.textContent=SB.park?'PARKED':'PARK';}}
function sbParkBtn(){let b=SB.parkEl;const show=SBX&&(state==='race'||state==='countdown')&&!SB.trav;if(!b){if(!show)return;b=SB.parkEl=document.createElement('button');b.id='sbPark';b.type='button';b.setAttribute('aria-label','Park: stop the car where it is');b.setAttribute('aria-pressed','false');
    const st=document.createElement('style');st.textContent='#sbPark{position:absolute;left:50%;bottom:max(14px,calc(env(safe-area-inset-bottom) + 14px));transform:translateX(-50%);z-index:7;display:flex;align-items:center;gap:8px;font:800 13px/1 system-ui,sans-serif;letter-spacing:.06em;color:#fff4dc;background:rgba(18,9,6,.62);border:2px solid rgba(255,244,220,.55);border-radius:14px;padding:7px 14px 7px 8px;cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent}#sbPark[hidden]{display:none}#sbPark b{display:grid;place-items:center;width:30px;height:30px;border-radius:8px;background:#2a5bd7;color:#fff;font:900 20px/1 system-ui,sans-serif}#sbPark[aria-pressed=true]{background:#2a5bd7;border-color:#fff}#sbPark[aria-pressed=true] b{background:#fff;color:#2a5bd7}';document.head.appendChild(st);
    b.innerHTML='<b>P</b><span>PARK</span>';b.onclick=e=>{e.preventDefault();sbPark();b.blur();};for(const ev of ['pointerdown','touchstart'])b.addEventListener(ev,e=>e.stopPropagation());stage.appendChild(b);
    addEventListener('keydown',e=>{if(SBX&&state==='race'&&e.code==='KeyK'&&!e.repeat&&!(typeof KEYC!=='undefined'&&KEYC.KeyK)){e.preventDefault();sbPark();}});}
  if(b.hidden===show)b.hidden=!show;}
function sbTick(dt){sbParkBtn();sbSpdUi();if(state!=='race'){sbRaceBtn(false);sbActBtn(null);return;}const k=player;if(!k)return;sbClockTick(dt);
  if(sbStop()&&!k.loop&&!k.air){const sp=k.speed,d=Math.min(Math.abs(sp),(140+Math.abs(sp)*5)*dt);k.speed=sp-Math.sign(sp)*d;if(Math.abs(k.speed)<1.5)k.speed=0;k.boost=0;k.drift=0;k.charge=0;}
{const f=SB.flag,near=!!f&&!SB.trav&&(k.x-f.x)**2+(k.y-f.z)**2<46*46&&Math.abs((k.wy||0)-f.y)<10;sbRaceBtn(near);if(near){try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp)sbRaceHere();SB.padUp=up;}catch(e){}}}try{sbActTick(k,dt);sbEggTick(k,dt);sbActPad();}catch(e){console.warn('activities',e);}sbShopTick(k);if(state!=='race')return;sbGuide(k,dt);if(SB.cool>0)SB.cool-=dt;else for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d>(g.road?0:g.plain?64:SB_GLEN-70)&&(!g.road||(d<26&&Math.abs((k.wy||0)-g.y)<14))&&Math.abs((k.x-g.x)*g.tx+(k.y-g.z)*g.tz)<g.hw+2&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2){sbTravel(g);return;}}
  const sv=sbSave(),y=(k.wy||0)+3.5;let ch=false;
  for(const c of SB.coins){if(c.t<0)continue;if(c.t>0){c.t-=dt;if(c.t<=0){c.t=0;}continue;}const dx=c.x-k.x,dz=c.z-k.y,r=c.rare?12:10.5;if(dx*dx+dz*dz>r*r||Math.abs(c.y-y)>(c.rare?14:10))continue;
    if(c.rare){c.t=-1;sv.r[c.id]=1;sv.c+=10;if(c.m)c.m.visible=false;burst(c.x,c.y,c.z,26,['#ffd65a','#d8402a','#ffffff'],70,2.4);spawnRing(c.x,c.y,c.z,'#ffd65a',26,.5,false);const f=sbFound();showBanner('Pepperoni coin! '+f[0]+' of '+f[1],1.6,'sm');try{SFX.ready();}catch(e){}}
    else{c.t=40;sv.c+=1;burst(c.x,c.y,c.z,5,['#ffd65a','#fff4dc'],34,1.4);try{SFX.pad();}catch(e){}}ch=true;}
  if(ch){sbKeep();SB.hudT=0;}SB.hudT-=dt;if(SB.hudT<=0){SB.hudT=.5;sbHud();}}
const _sbM=new THREE.Matrix4(),_sbQ=new THREE.Quaternion(),_sbP=new THREE.Vector3(),_sbS=new THREE.Vector3(),_sbE=new THREE.Euler();
/* the chase camera must not look from inside a fence or the shed: walk from the kart out to where the camera wants to be and stop short of the
   first solid thing at that height (the track is never in the way: you can see over it). It closes in at once and eases back out. */
function sbSolid(x,z,y){for(const g of SB.gates){if(g.road)continue;const d=(x-g.x)*g.nx+(z-g.z)*g.nz;if(d>-12&&d<SB_GLEN+10&&Math.abs((x-g.x)*g.tx+(z-g.z)*g.tz)<g.hw+1)return false;}{const c=SB.col;if(c){if(x<c.b[0]||x>c.b[1]||z<c.b[2]||z>c.b[3])return true;for(let dx=-2;dx<=2;dx+=2)for(let dz=-2;dz<=2;dz+=2){const i=Math.floor((x+dx-c.x0)/c.C),k=Math.floor((z+dz-c.z0)/c.C);if(i<0||k<0||i>=c.nx||k>=c.nz)continue;const q=i*c.nz+k,o=q*SB_K*2;if(c.thin[q])continue;for(let e=0;e<c.cnt[q];e++)if(c.sp[o+e*2]/SB_Q<=y+1&&c.sp[o+e*2+1]/SB_Q>=y-1)return true;}}}for(const s of SB.shapes){if(s.h<=y||s.b>=y)continue;if(s.t==='cyl'){const dx=x-s.x,dz=z-s.z,r=s.r+2;if(dx*dx+dz*dz<=r*r)return true;}else if(x>=s.x0-3&&x<=s.x1+3&&z>=s.z0-3&&z<=s.z1+3)return true;}return false;}
function sbCam(){const k=camT;if(!k||state==='menu'||!SBF)return;if(k.loop||k.rth>0){SB.camF=1;return;}/* (web v193, "going around the loops is a little glitchy": the loop's own hoop stood between the camera and the kart, so this pulled the camera in and turned it level, fighting the loop's camera every frame) */const tx=k.x,tz=k.y,ty=(k.wy||0)+7,cx=camera.position.x,cy=camera.position.y,cz=camera.position.z;let ok=1;
  for(let i=1;i<=16;i++){const f=i/16,g=Math.min(1.06,f+.06);if(sbSolid(tx+(cx-tx)*g,tz+(cz-tz)*g,ty+(cy-ty)*g)){ok=(i-1)/16;break;}}
  const was=SB.camF==null?1:SB.camF;SB.camF=ok<was?ok:Math.min(ok,was+.02);const f=Math.max(.16,SB.camF);if(f>=.999)return;
  camera.position.set(tx+(cx-tx)*f,ty+(cy-ty)*f+(1-f)*9,tz+(cz-tz)*f);{/* pulled in close, it looks more and more at the kart itself, so the kart stays in the picture */const w=Math.min(1,(1-f)*1.6);camera.lookAt(cam.look.x+(tx-cam.look.x)*w,cam.look.y+cam.oy*.45+(ty-2-cam.look.y-cam.oy*.45)*w,cam.look.z+(tz-cam.look.z)*w);}}
function sbRender(time){sbSpdUi();{const dt=Math.min(.1,Math.max(0,time-(SB.wT==null?time:SB.wT)));SB.wT=time;sbWarpTick(dt);}if(SBC.stars)SBC.stars.position.copy(camera.position);if(!SB.grp)return;sbCam();if(SB.flag){SB.flag.F.rotation.y=time*1.6;SB.flag.F.position.y=12+Math.sin(time*2.2)*1.2;}const im=SB.im;for(const c of SB.coins){const a=time*2.6+c.ph;if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}
    _sbE.set(0,a,0);_sbQ.setFromEuler(_sbE);_sbP.set(c.x,c.y,c.z);const s=c.t>0?0:1;_sbS.set(s,s,s);_sbM.compose(_sbP,_sbQ,_sbS);im.setMatrixAt(c.i,_sbM);}
  if(im)im.instanceMatrix.needsUpdate=true;}
function sbHud(){let e=SB.el;if(!e){e=SB.el=document.createElement('div');e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 13px/1.3 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.62);border-radius:12px;padding:8px 12px;pointer-events:none;text-shadow:0 1px 2px #000';stage.appendChild(e);}
  e.hidden=!SBX||state==='menu';if(BB.el)BB.el.hidden=true;if(e.hidden)return;const sv=sbSave(),f=sbFound(),dot=(c,r)=>'<span style="display:inline-block;width:'+r+'px;height:'+r+'px;border-radius:50%;background:'+c+';box-shadow:inset 0 0 0 2px rgba(0,0,0,.25);vertical-align:-2px;margin-right:6px"></span>';
  e.innerHTML='<div style="font-size:11px;letter-spacing:.6px;opacity:.85;text-transform:uppercase">'+SB.reg.name+'</div><div style="font-size:20px;margin-top:2px">'+dot('#ffc93a',15)+sv.c+'</div><div style="margin-top:2px">'+dot('#d8402a',13)+f[0]+' / '+f[1]+'</div>'+(SB_CLOCK?'<div style="margin-top:3px;font-size:12px;opacity:.9">'+sbClockIcon()+sbClockStr()+'</div>':'');}
/* what an item box gives here: only the boost (nobody to throw anything at) */
function sbRoll(){return 'chili';}
/* ---- for the PC (docs/SANDBOX-PLAN.md, "Sandbox on the PC") ----
   The PC draws a track from an exported model and cannot read walls from what is drawn: sbExport() hands the exporter (godot/tools/ciexport.py)
   everything Sandbox worked out for the place that is loaded, in the game's own numbers. The grid is sparse, so only the squares that hold
   something are written: `cells` (their numbers, i*nz+k, 32-bit), `cnt` and `thin` (a byte each), `sp` (their low and high pairs, 16-bit, one
   after another). Call it in Sandbox, with an empty save (so the arches stand where a first visit puts them). */
function sbExport(){if(!SBX)return null;const b64=a=>{const u=new Uint8Array(a.buffer,a.byteOffset,a.byteLength);let t='';for(let i=0;i<u.length;i+=32768)t+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(t);};
  const o={v:1,id:SB.regId,kind:SB.kind,free:SBF,name:SB.reg.name,rim:SB.rim||0,step:SB_STEP,r:SB_R,head:SB_HEAD,rail:SB_RAIL,q:SB_Q,k:SB_K,glen:SB_GLEN,lvl:sbLvl(),toyw:SB.kind==='toy'?TOYW():0,
    loops:SB.loops.map(L=>({x:L.p.x,y:L.p.y,tx:L.p.tx,ty:L.p.ty,nx:L.p.nx,ny:L.p.ny,g0:L.g0,r:L.r,a:L.a,b:L.b})),
    gates:SB.gates.map(g=>({id:g.id,to:g.to,at:g.at,label:g.label,x:g.x,y:g.y,z:g.z,nx:g.nx,nz:g.nz,hw:g.hw,road:g.road?1:0,plain:g.plain?1:0,j:g.j==null?-1:g.j})),
    coins:SB.coins.map(c=>[+c.x.toFixed(2),+c.y.toFixed(2),+c.z.toFixed(2),c.rare?1:0,c.id||'']),flag:SB.flag?[SB.flag.x,SB.flag.y,SB.flag.z]:null,shapes:SB.shapes,
    /* (web v199: the activities' markers and the place's Easter egg, activities.js; the PC keeps the same table of activities and eggs and takes the spots from here) */
    acts:(typeof SBA!=='undefined'?SBA.marks:[]).map(m=>({id:m.a.id,x:+m.x.toFixed(2),y:+m.y.toFixed(2),z:+m.z.toFixed(2),j:m.j})),egg:typeof SBA!=='undefined'&&SBA.egg?{id:SBA.egg.E.id,x:+SBA.egg.x.toFixed(2),y:+SBA.egg.y.toFixed(2),z:+SBA.egg.z.toFixed(2),ry:+SBA.egg.G.rotation.y.toFixed(3)}:null};
  const c=SB.col;if(c){const n=c.nx*c.nz;let m=0,tot=0;for(let q=0;q<n;q++)if(c.cnt[q]){m++;tot+=c.cnt[q];}const cells=new Int32Array(m),cnt=new Uint8Array(m),thin=new Uint8Array(m),sp=new Int16Array(tot*2);let i=0,w=0;
    for(let q=0;q<n;q++){const k=c.cnt[q];if(!k)continue;cells[i]=q;cnt[i]=k;thin[i]=c.thin[q];i++;for(let e=0;e<k;e++){sp[w++]=c.sp[q*SB_K*2+e*2];sp[w++]=c.sp[q*SB_K*2+e*2+1];}}
    o.col={x0:c.x0,z0:c.z0,nx:c.nx,nz:c.nz,C:c.C,cap:c.cap,b:c.b,filled:m,spans:tot,cells:b64(cells),cnt:b64(cnt),thin:b64(thin),sp:b64(sp)};}
  return o;}
/* ================= SANDBOX: the world map and fast travel (web v193) =================
   The owner's brief, section 3 (docs/NEXT-MODES-BRIEF.md), and "dont forget to add a map with fast travel in the pause menu and on controller
   make the y button open the map". Opened while driving with Select / View / Back / Minus on a controller (Y until v200; since v201 Y is the special ability, as in a race), or M on a keyboard (again, or
   Back, returns to driving); in the pause menu Map sits directly under Resume (Back returns to the pause menu with Resume ready).
   The picture: the house from above as it really is (SB_WORLD: where each of its four places sits, in metres, the garden wall along y = 0),
   and below and beside it the twenty tracks of the wider world, each a round place with its own lap drawn in it (SB_SPOT: where each sits on
   the map), grouped in their five countries, with a line for every passage (SB_LINKS; the garage's door leads to Margherita Ring).
   Names are plain labels; the chequered pins are the fast-travel points, one at every start line. Picking a pin names it and asks; going
   there is the same warp as a passage. Hidden things are not on the map. On a small screen the map is larger than its window: drag it. */
const SB_WORLD={
  backyard:{name:'BACK GARDEN',box:[-13.9,11.6,0,7],at:(x,z)=>[x/SB_M-.75,3.5-z/SB_M],fill:'#4d8a3c'},
  kitchen:{name:'KITCHEN',box:[-9,-5,-4.8,0],at:(x,z)=>[-7+x/SB_M,-2.4-z/SB_M],fill:'#d9d3c6'},
  bedroom:{name:'BEDROOM',box:[-2,2,-4.8,0],at:(x,z)=>[x/SB_M,-2.4-z/SB_M],fill:'#c9a877'},
  garage:{name:'GARAGE',box:[5.5,9.5,-4.8,0],at:(x,z)=>[7.5+x/SB_M,-2.4-z/SB_M],fill:'#b9bbbd'}};
/* parts of the house that are on the map but not yet places to drive */
const SB_WORLD_MORE=[{name:'HALL',box:[-5,-2,-4.8,0]},{name:'',box:[2,5.5,-4.8,0]}];
const SB_SPOT={margherita:[7.5,-12.5],basil:[16,-12.5],oven:[7.5,-20.5],spiral:[16,-20.5],bay:[-1,-12.5],lagoon:[-9.5,-12.5],calzone:[-9.5,-20.5],tour:[-1,-20.5],
  mozz:[24.5,-12.5],napoli:[33,-12.5],moon:[33,-4.3],peaks:[24.5,-4.3],frosty:[24.5,-20.5],burn:[33,-20.5],glacier:[41.5,-20.5],peak:[50,-20.5],holo:[41.5,-12.5],grid:[50,-12.5],laser:[58.5,-12.5],synth:[58.5,-20.5]};
const SB_SPOT_R=3.1;
/* the countries: a tinted ground behind their places, and a plain name */
const SB_LAND=[['Kitchen Country','#3d3423',[[3.3,20.2,-24.6,-8.4]],[11.75,-8.95]],['The Bay','#1f3d4a',[[-13.7,3.2,-24.6,-8.4]],[-5.25,-8.95]],['The Old Town','#40332f',[[20.3,37.2,-16.6,-.2]],[28.75,-.75]],
  ['The Freezer Range','#2b3f52',[[20.3,54.2,-25.7,-16.7]],[37.25,-25.1]],['The Neon District','#141a33',[[37.3,62.6,-16.6,-8.4],[54.3,62.6,-25.7,-16.6]],[49.9,-8.95]]];
const SBM={el:null,cv:null,open:false,from:'',pick:null,zoom:null,trk:{},pins:[],view:[-14.8,63.1,-26.3,7.9]};
/* a place's tunnels on the map: [map x, map y, where it leads]. The house's are known from its plan; a track's own are known while you are on it, and
   remembered from then on (the save's g); a place you have not been to yet has none on the map (the brief: leave room for discovery) */
function sbMapGates(id){const o=[];if(SB_WORLD[id]){for(const d of (SB_REG[id]&&SB_REG[id].gates)||[]){const a=sbMapGate(id,d.id);if(a)o.push([a[0],a[1],d.label]);}return o;}
  const L=SBX&&id===SB.regId?SB.gates.map(g=>[g.x,g.z,g.label]):(sbSave().g||{})[id]||[];for(const g of L){const a=sbMapAt(id,g[0],g[1]);if(a)o.push([a[0],a[1],g[2]]);}return o;}
/* the window on one place: the whole of it with a margin, in the picture's own shape */
function sbMapView(id){const V0=SBM.view,asp=(V0[3]-V0[2])/(V0[1]-V0[0]);let cx,cy,w,h;if(SB_WORLD[id]){const b=SB_WORLD[id].box;cx=(b[0]+b[1])/2;cy=(b[2]+b[3])/2;w=b[1]-b[0];h=b[3]-b[2];}else{const c=SB_SPOT[id];cx=c[0];cy=c[1];w=h=SB_SPOT_R*2;}
  const hh=Math.max(h*.5*1.3,w*.5*1.3*asp);return [cx-hh/asp,cx+hh/asp,cy-hh,cy+hh];}
function sbMapAt(id,x,z){const W=SB_WORLD[id];if(W)return W.at(x,z);const c=SB_SPOT[id],m=MAPS.find(q=>q.id===id);if(!c||!m)return null;const s=SB_SPOT_R/(m.R||1900);return [c[0]+x*s,c[1]-z*s];}
function sbMapTrack(id){if(SBM.trk[id])return SBM.trk[id];const def=MAPS.find(m=>m.id===id);if(!def||!sbRegOf(id))return null;let t;try{t=makeTrack(def,false).pts;}catch(e){return null;}if(!t||!t.length)return null;const o=[],st=Math.max(1,Math.floor(t.length/260));for(let j=0;j<t.length;j+=st)o.push(sbMapAt(id,t[j].x,t[j].y));
  return SBM.trk[id]={pts:o,start:sbMapAt(id,t[0].x,t[0].y),name:def.name};}
function sbMapEl(){let e=SBM.el;if(e)return e;e=SBM.el=document.createElement('div');e.id='sbMap';e.className='overlay';e.hidden=true;
  e.innerHTML='<div class="panel" style="max-width:1080px;width:min(1080px,96vw);gap:8px;padding:14px 16px"><div style="display:flex;align-items:baseline;gap:12px"><h2 class="res-title" style="margin:0;font-size:24px">Map</h2><span style="opacity:.75;font-weight:700" id="sbMapWhere"></span><span style="flex:1"></span><span style="font-size:12px;opacity:.7" id="sbMapKey"></span></div>'
    +'<div id="sbMapBox" style="position:relative;width:100%;max-height:min(62vh,640px);border-radius:14px;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:#1b120d;box-shadow:inset 0 0 0 2px rgba(255,255,255,.08)"><div id="sbMapIn" style="position:relative"><canvas id="sbMapCv" style="display:block"></canvas></div></div>'
    +'<div id="sbMapAsk" style="min-height:48px;display:flex;align-items:center;gap:10px;flex-wrap:wrap"><span id="sbMapSay" style="flex:1;font-weight:700;min-width:180px"></span><button id="sbMapMe" class="ghost">Where am I?</button><button id="sbMapGo" class="cta" style="padding:10px 18px;font-size:17px" hidden>Travel here</button><button id="sbMapNo" class="ghost" hidden>Cancel</button><button id="sbMapBack" class="ghost back" data-back="1">Back</button></div></div>';
  stage.appendChild(e);SBM.cv=e.querySelector('#sbMapCv');
  e.querySelector('#sbMapBack').onclick=()=>sbMap(false);e.querySelector('#sbMapMe').onclick=()=>{const q=SBM.pins.find(q=>q.id===SB.regId);if(q)sbMapPick({id:q.id,track:q.name});};e.querySelector('#sbMapNo').onclick=()=>{sbMapPick(null);};e.querySelector('#sbMapGo').onclick=()=>{const p=SBM.pick;if(p)sbMapTravel(p.id);};
  return e;}
/* ---- the speed slider, and the guide into a tunnel's mouth (web v197) ----
   The owner, 2026-11-14: "for sandbox mode make it so that there is a slider on the side of the screen where you can adjust vehicle speed.
   I've noticed that at the default speed it's hard to go into the tunnels and I miss them a lot of times".
   SB.spd, .25 to 1 in steps of .05, is the share of its normal top speed the car may reach in Sandbox (the engine multiplies the throttle by
   it: tools/mini/patch32.py, in playerInput; boosts are scaled the same, reversing is its own slower speed and is not touched). It is kept
   in the save as `v`, so it carries through passages, fast travel and a reload; a race from the start line is not Sandbox and is not slowed.
   On the screen: a vertical track on the right edge, between the item buttons and the drift button (the left edge has the mirror button), dragged by finger or mouse; [ and ] on a keyboard; D-pad left and
   right on a controller (patch32). */
function sbSpd(v){const sv=sbSave();if(SB.spd==null)SB.spd=clamp(Math.round((+sv.v||1)*20)/20,.25,1);if(v==null)return SB.spd;v=clamp(Math.round(v*20)/20,.25,1);if(v===SB.spd)return v;SB.spd=v;sv.v=v;sbKeep();SB.spdDraw=null;sbSpdUi();return v;}
function sbSpdStep(d){return sbSpd(sbSpd()+d*.05);}
function sbSpdUi(){let e=SB.spdEl;const show=SBX&&(state==='race'||state==='countdown')&&!SB.trav&&!SBM.open&&pauseOv.hidden&&setOv.hidden;/* (hidden under the pause sheet and Settings too: sbRender keeps it current while the game is stopped) */if(!e){if(!show)return;e=SB.spdEl=document.createElement('div');e.id='sbSpd';e.setAttribute('role','slider');e.setAttribute('aria-label','Speed in Sandbox');e.setAttribute('aria-valuemin','25');e.setAttribute('aria-valuemax','100');
    const st=document.createElement('style');st.textContent='#sbSpd{position:absolute;right:max(10px,env(safe-area-inset-right));top:max(162px,calc(50% - 64px));z-index:6;width:46px;padding:6px 0 8px;border-radius:12px;background:rgba(18,9,6,.62);color:#fff4dc;font:800 10px/1.15 system-ui,sans-serif;letter-spacing:.04em;text-align:center;text-shadow:0 1px 2px #000;touch-action:none;user-select:none;-webkit-user-select:none;cursor:ns-resize}#sbSpd[hidden]{display:none}#sbSpd b{display:block;font-size:13px;margin-top:1px}#sbSpd i{display:block;position:relative;width:8px;height:min(150px,calc(100vh - 330px));min-height:70px;margin:7px auto 0;border-radius:4px;background:rgba(255,244,220,.25)}#sbSpd i u{position:absolute;left:0;right:0;bottom:0;border-radius:4px;background:#ffc93a}#sbSpd i s{position:absolute;left:-8px;width:24px;height:12px;margin-bottom:-6px;border-radius:6px;background:#fff4dc;box-shadow:0 1px 3px rgba(0,0,0,.6)}';document.head.appendChild(st);
    e.innerHTML='SPEED<b></b><i><u></u><s></s></i>';const tr=e.querySelector('i'),at=ev=>{const r=tr.getBoundingClientRect();sbSpd(.25+.75*clamp((r.bottom-ev.clientY)/Math.max(1,r.height),0,1));};
    e.addEventListener('pointerdown',ev=>{ev.preventDefault();ev.stopPropagation();SB.spdDrag=ev.pointerId;try{e.setPointerCapture(ev.pointerId);}catch(x){}at(ev);});e.addEventListener('pointermove',ev=>{if(SB.spdDrag===ev.pointerId){ev.preventDefault();at(ev);}});for(const n of ['pointerup','pointercancel'])e.addEventListener(n,ev=>{if(SB.spdDrag===ev.pointerId)SB.spdDrag=null;});
    for(const n of ['touchstart','touchmove','touchend','mousedown'])e.addEventListener(n,ev=>ev.stopPropagation());stage.appendChild(e);
    addEventListener('keydown',ev=>{if(!SBX||state!=='race'||SBM.open||SB.trav)return;if(ev.code==='BracketLeft'&&!KEYC.BracketLeft){ev.preventDefault();sbSpdStep(-1);}else if(ev.code==='BracketRight'&&!KEYC.BracketRight){ev.preventDefault();sbSpdStep(1);}});}
  if(e.hidden===show)e.hidden=!show;if(!show)return;
  /* (web v200, the owner's phone: "The speed slider overlaps the item slots by just a little". Twice a second it is set below whichever of
     the item and ability buttons stand above it, with their letter badges, and its track is shortened to fit what is left above the pedals) */
  {const now=performance.now();if(!SB.spdPosT||now-SB.spdPosT>500){SB.spdPosT=now;const er=e.getBoundingClientRect();let lo=0;for(const id of ['itemBtn','itemBtn2','abilBtn','slot2']){const b=document.getElementById(id);if(!b||b.offsetParent===null)continue;const r=b.getBoundingClientRect();if(r.width&&r.right>er.left-4&&r.left<er.right+4&&r.top<er.bottom)lo=Math.max(lo,r.bottom);}
    const top=Math.round(Math.max(162,innerHeight/2-64,lo?lo+18:0));if(e.style.top!==top+'px'){e.style.top=top+'px';e.querySelector('i').style.height=Math.max(56,Math.min(150,innerHeight-top-170))+'px';SB.spdDraw=null;}}}
  const v=sbSpd();if(SB.spdDraw===v)return;SB.spdDraw=v;const f=(v-.25)/.75*100;e.querySelector('b').textContent=Math.round(v*100)+'%';e.querySelector('u').style.height=f+'%';e.querySelector('s').style.bottom=f+'%';e.setAttribute('aria-valuenow',String(Math.round(v*100)));}
/* heading into a mouth a little off its middle, the kart is eased sideways into it instead of meeting the jamb: only in the last 110 units
   before the wall, only when it is pointing in and already within reach of the mouth, and never faster than a kart could steer there */
function sbGuide(k,dt){if(!SBF||k.air||k.loop||!(k.speed>20))return;for(const g of SB.gates){if(g.road)continue;const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d<-110||d>30)continue;const l=(k.x-g.x)*g.tx+(k.y-g.z)*g.tz,lim=Math.max(4,g.hw-10);if(Math.abs(l)<=lim||Math.abs(l)>g.hw+26)continue;if(Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz<.55)continue;if(Math.abs((k.wy||0)-g.y)>12)continue;
    const want=Math.sign(l)*lim,mv=clamp(want-l,-70*dt,70*dt),nx2=k.x+g.tx*mv,ny2=k.y+g.tz*mv;if(d<-22&&sbBlocked(nx2,ny2,k.wy||0))continue;/* (out in the room something may stand beside the kart) */k.x=nx2;k.y=ny2;return;}}
addEventListener('keydown',ev=>{if(SBM.open&&(ev.code==='Escape'||ev.code==='KeyM')){ev.preventDefault();ev.stopImmediatePropagation();if(SBM.pick&&ev.code==='Escape')sbMapPick(null);else sbMap(false);}else if(!SBM.open&&SBX&&state==='race'&&ev.code==='KeyM'&&!ev.repeat&&!KEYC.KeyM){ev.preventDefault();sbMap(true,'drive');}},true);
function sbMapPick(p){SBM.pick=p;SBM.zoom=p?p.id:null;const e=sbMapEl(),say=e.querySelector('#sbMapSay'),go=e.querySelector('#sbMapGo'),no=e.querySelector('#sbMapNo');
  const me=e.querySelector('#sbMapMe');
  if(p){const R=sbRegOf(p.id),here=SBX&&p.id===SB.regId,n=R?sbMapGates(p.id).length:0;if(p.id==='shop'){SBM.zoom=SB_SHOP.id;say.textContent="Mechanic's shop, in the garage: drive in to change your driver and kart";go.hidden=false;no.hidden=false;no.textContent='World map';me.hidden=false;go.textContent='Travel here';go.focus();sbMapDraw();return;}say.textContent=p.track+(R?' · '+R.name.split(' · ')[0]:'')+(here?' · you are here (the blue arrow)':'')+(n?' · the purple rings are its tunnels':' · its tunnels show once you have been there');go.hidden=false;no.hidden=false;no.textContent='World map';me.hidden=here;go.textContent=here?'To the start line':'Travel here';go.focus();}
  else{say.textContent='Pick a chequered pin to look closer at a place and travel to it. Every place can also be driven to.';go.hidden=true;no.hidden=true;me.hidden=!SBX;}
  sbMapDraw();
  for(const q of SBM.pins)q.b.setAttribute('aria-pressed',String(!!p&&q.id===p.id));}
/* the picture: drawn each time the map opens */
function sbMapDraw(){const cv=SBM.cv,box=cv.parentNode.parentNode,Z=SBM.zoom,V=Z?sbMapView(Z):SBM.view,asp=(V[3]-V[2])/(V[1]-V[0]),hMax=Math.max(200,Math.min(innerHeight*.62,640)),wCss=Math.max(940,Math.min(box.clientWidth||600,Math.floor(hMax/asp))),hCss=Math.round(wCss*asp),dpr=Math.min(2,window.devicePixelRatio||1);cv.width=Math.round(wCss*dpr);cv.height=Math.round(hCss*dpr);cv.style.width=wCss+'px';cv.style.height=hCss+'px';cv.parentNode.style.width=wCss+'px';cv.parentNode.style.margin='0 auto';SBM.big=wCss>(box.clientWidth||600)+4||hCss>hMax+4;
  const g=cv.getContext('2d'),s=cv.width/(V[1]-V[0]),X=x=>(x-V[0])*s,Y=y=>(V[3]-y)*s,rect=(b,f,st,lw)=>{g.beginPath();g.rect(X(b[0]),Y(b[3]),(b[1]-b[0])*s,(b[3]-b[2])*s);if(f){g.fillStyle=f;g.fill();}if(st){g.strokeStyle=st;g.lineWidth=lw||2;g.stroke();}};
  const F=px=>'800 '+Math.round(px*dpr)+'px system-ui,sans-serif';g.fillStyle='#22301f';g.fillRect(0,0,cv.width,cv.height);g.textAlign='center';g.textBaseline='middle';g.lineJoin='round';g.lineCap='round';
  /* the countries */for(const [name,col,boxes,at] of SB_LAND){for(const b of boxes)rect(b,col);g.font=F(12);g.fillStyle='rgba(255,255,255,.55)';g.fillText(name.toUpperCase(),X(at[0]),Y(at[1]));}
  /* the house: the ground outside the fences, the garden with its patio, the rooms, the street in front */
  rect(SB_WORLD.backyard.box,SB_WORLD.backyard.fill);rect([-13.9,11.6,0,1.6],'#cfc6b3');rect(SB_WORLD.backyard.box,null,'#6b4f33',3*dpr);
  rect([-9.2,9.7,-5.0,0],'#8f6f5a');for(const m of SB_WORLD_MORE)rect(m.box,'#b8ad9c','#5b4636',1.5*dpr);for(const id of ['kitchen','bedroom','garage'])rect(SB_WORLD[id].box,SB_WORLD[id].fill,'#5b4636',2*dpr);
  rect([-14.6,12.3,-6.3,-5.0],'#55585c');g.font=F(10);g.fillStyle='rgba(255,255,255,.6)';g.fillText('FRONT STREET',X(-4),Y(-5.65));
  /* the passages between the tracks, and the garage's door to Margherita Ring */
  g.setLineDash([6*dpr,6*dpr]);g.strokeStyle='rgba(246,236,212,.75)';g.lineWidth=2.5*dpr;const seen={};
  for(const a in SB_LINKS)for(const b of SB_LINKS[a]){const k=a<b?a+'|'+b:b+'|'+a;if(seen[k])continue;seen[k]=1;const p=b==='garage'?[7.5,-4.8]:SB_SPOT[b],q=SB_SPOT[a];if(!p||!q)continue;g.beginPath();g.moveTo(X(q[0]),Y(q[1]));g.lineTo(X(p[0]),Y(p[1]));g.stroke();}
  g.strokeStyle='rgba(20,12,8,.8)';g.lineWidth=2*dpr;for(const id in SB_WORLD)for(const d of (SB_REG[id]&&SB_REG[id].gates)||[]){if(d.plain||id>d.to)continue;const a=sbMapGate(id,d.id),b=sbMapGate(d.to,d.at);if(!a||!b)continue;g.beginPath();g.moveTo(X(a[0]),Y(a[1]));g.lineTo(X(b[0]),Y(b[1]));g.stroke();}
  g.setLineDash([]);for(const id in SB_WORLD)for(const d of (SB_REG[id]&&SB_REG[id].gates)||[]){if(d.plain)continue;const a=sbMapGate(id,d.id);if(!a)continue;g.beginPath();g.arc(X(a[0]),Y(a[1]),4.5*dpr,0,7);g.fillStyle='#140c08';g.fill();g.strokeStyle='#f3ead6';g.lineWidth=1.5*dpr;g.stroke();}
  /* the round places */for(const id in SB_SPOT){const c=SB_SPOT[id],m=MAPS.find(q=>q.id===id);if(!m)continue;const neon=!!m.exact&&id!=='spiral',r=SB_SPOT_R*s;g.beginPath();g.arc(X(c[0]),Y(c[1]),r,0,7);g.fillStyle=neon?'#0b1020':id==='spiral'?'#b3402a':'#f0cf78';g.fill();g.strokeStyle=neon?'#39d0ff':'#b9773a';g.lineWidth=(neon?2:4)*dpr;g.stroke();}
  /* the tracks */for(const id of Object.keys(SB_WORLD).concat(Object.keys(SB_SPOT))){const t=sbMapTrack(id);if(!t)continue;const m=MAPS.find(q=>q.id===id),neon=!!m.exact&&id!=='spiral',toy=!!SB_WORLD[id];
    for(const [col,w] of toy?[['#7a2a05',.36],['#ff7a1e',.26]]:neon?[['#0d3f55',.5],['#59e0ff',.3]]:[['#4a3423',.52],['#8a8f96',.34]]){g.beginPath();t.pts.forEach((p,i)=>i?g.lineTo(X(p[0]),Y(p[1])):g.moveTo(X(p[0]),Y(p[1])));g.closePath();g.strokeStyle=col;g.lineWidth=Math.max(2,w*s);g.stroke();}}
  /* names: plain, never a button */for(const id in SB_WORLD){const W=SB_WORLD[id],b=W.box;g.font=F(id==='backyard'?14:11);g.fillStyle=id==='backyard'?'rgba(255,255,255,.92)':'rgba(30,18,10,.9)';g.fillText(W.name,X((b[0]+b[1])/2),Y(id==='backyard'?b[3]-.55:b[2]+.45));}
  for(const m of SB_WORLD_MORE)if(m.name){g.font=F(9);g.fillStyle='rgba(30,18,10,.6)';g.fillText(m.name,X((m.box[0]+m.box[1])/2),Y((m.box[2]+m.box[3])/2));}
  /* the tunnels of the places whose tunnels are known: a purple ring; looked at closely, with where each leads */
  for(const id of Object.keys(SB_WORLD).concat(Object.keys(SB_SPOT))){if(Z&&id!==Z)continue;for(const t of sbMapGates(id)){const x=X(t[0]),y=Y(t[1]),r=(Z?9:4)*dpr;g.beginPath();g.arc(x,y,r,0,7);g.fillStyle='#1a0f33';g.fill();g.strokeStyle='#b58cff';g.lineWidth=(Z?4:2)*dpr;g.stroke();g.beginPath();g.arc(x,y,r*.35,0,7);g.fillStyle='#ffffff';g.fill();
      if(Z){const tx='TUNNEL TO '+t[2];g.font=F(12);const w=g.measureText(tx).width+12*dpr,lx=Math.max(w/2+4,Math.min(cv.width-w/2-4,x)),ly=y>cv.height*.5?y-r-13*dpr:y+r+13*dpr;g.fillStyle='rgba(20,10,40,.88)';g.fillRect(lx-w/2,ly-10*dpr,w,20*dpr);g.strokeStyle='#b58cff';g.lineWidth=1.5*dpr;g.strokeRect(lx-w/2,ly-10*dpr,w,20*dpr);g.fillStyle='#f1e8ff';g.fillText(tx,lx,ly+.5*dpr);}}}
  /* you: an arrow where you are, pointing the way you face */
  SBM.me=null;if(SBX&&player){const p=sbMapAt(SB.regId,player.x,player.y);if(p){const a=player.ma,r=(Z?14:9)*dpr;g.save();g.translate(X(p[0]),Y(p[1]));g.rotate(a);g.beginPath();g.moveTo(r*1.25,0);g.lineTo(-r*.8,r*.8);g.lineTo(-r*.35,0);g.lineTo(-r*.8,-r*.8);g.closePath();g.fillStyle='#39d0ff';g.fill();g.strokeStyle='#06222e';g.lineWidth=2*dpr;g.stroke();g.restore();SBM.me=[X(p[0])/dpr,Y(p[1])/dpr];}}
  /* the pins sit over the picture as real buttons (so a finger, a mouse and a controller all reach them) */
  for(const q of SBM.pins){const x=X(q.at[0])/dpr,y=Y(q.at[1])/dpr;q.b.style.left=x+'px';q.b.style.top=y+'px';q.b.hidden=!!Z&&q.id!==Z&&!(q.id==='shop'&&Z===SB_SHOP.id);}}
function sbMapGate(id,gid){const R=SB_REG[id],W=SB_WORLD[id];if(!R||!W)return null;const d=(R.gates||[]).find(q=>q.id===gid);if(!d)return null;const b=W.box;if(R.room){const y=(b[2]+b[3])/2+d.p/100,x=(b[0]+b[1])/2+d.p/100;return d.w==='E'?[b[1],y]:d.w==='W'?[b[0],y]:d.w==='N'?[x,b[3]]:[x,b[2]];}return d.w==='S'?[d.p,b[2]]:d.w==='N'?[d.p,b[3]]:d.w==='E'?[b[1],d.p]:[b[0],d.p];}
function sbMapPins(){const box=sbMapEl().querySelector('#sbMapIn');for(const q of SBM.pins)q.b.remove();SBM.pins=[];
  for(const id of Object.keys(SB_WORLD).concat(Object.keys(SB_SPOT))){const t=sbMapTrack(id);if(!t)continue;const b=document.createElement('button');b.type='button';b.className='sbpin';b.setAttribute('aria-label','Travel to '+t.name);
    b.style.cssText='position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #ffd45a;padding:0;cursor:pointer;background:conic-gradient(#141210 25%,#fbf6ea 0 50%,#141210 0 75%,#fbf6ea 0) 0 0/12px 12px;box-shadow:0 2px 6px rgba(0,0,0,.6)';
    b.innerHTML='<span style="position:absolute;left:50%;'+(id==='backyard'?'bottom:100%;margin-bottom:3px;':'top:100%;margin-top:3px;')+'transform:translateX(-50%);font:800 10.5px/1 system-ui,sans-serif;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000,0 0 6px #000;pointer-events:none">'+t.name+'</span>';
    b.onclick=()=>sbMapPick(SBM.zoom===id?null:{id,track:t.name});b.addEventListener('focus',()=>{try{b.scrollIntoView({block:'nearest',inline:'nearest'});}catch(e){}});box.appendChild(b);SBM.pins.push({id,b,at:t.start,name:t.name});}
  /* the mechanic's shop: a pin of its own, round with a spanner, blue (a place to go, not a track) */{const at=sbMapAt(SB_SHOP.id,SB_SHOP.x,SB_SHOP.z);if(at){const b=document.createElement('button');b.type='button';b.className='sbpin';b.setAttribute('aria-label',"Travel to the mechanic's shop");
    b.style.cssText='position:absolute;width:28px;height:28px;margin:-14px 0 0 -14px;border-radius:50%;border:3px solid #fff4dc;padding:0;cursor:pointer;background:#2a5bd7;box-shadow:0 2px 6px rgba(0,0,0,.6);color:#fff;font:900 15px/22px system-ui,sans-serif';
    b.innerHTML='&#128295;<span style="position:absolute;left:50%;top:100%;margin-top:3px;transform:translateX(-50%);font:800 10.5px/1 system-ui,sans-serif;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000,0 0 6px #000;pointer-events:none">Mechanic</span>';
    b.onclick=()=>sbMapPick({id:'shop',track:"Mechanic's shop"});box.appendChild(b);SBM.pins.push({id:'shop',b,at,name:"Mechanic's shop"});}}
  if(!document.getElementById('sbPinCss')){const st=document.createElement('style');st.id='sbPinCss';st.textContent='.sbpin:focus-visible,.sbpin[aria-pressed=true]{outline:3px solid #39d0ff;outline-offset:3px}';document.head.appendChild(st);}}
/* open or close. from: 'drive' (straight from driving: closing goes back to driving) or 'pause' (from the pause menu: closing goes back to it) */
function sbMap(open,from){const e=sbMapEl();if(open===SBM.open)return;if(open){if(!SBX||SB.trav||(state!=='race'&&state!=='paused'))return;SBM.from=from||'drive';
    if(state==='race')togglePause();/* the game stops under the map, exactly as under the pause menu */pauseOv.hidden=true;SBM.open=true;e.hidden=false;sbMapPins();sbMapPick(null);
    e.querySelector('#sbMapWhere').textContent=SB.reg?SB.reg.name:'';if(SB_CLOCK)e.querySelector('#sbMapWhere').insertAdjacentHTML('beforeend','<span style="margin-left:14px;font-size:13px;opacity:.9;white-space:nowrap">'+sbClockIcon()+sbClockStr()+'</span>');e.querySelector('#sbMapKey').textContent=(SBM.big?'Drag the map to see more \u00b7 ':'')+(PAD.act?'Select: close':(typeof COARSE!=='undefined'&&COARSE)?'':'M: close');
    /* the window opens on where you are */{const box=e.querySelector('#sbMapBox');if(SBM.me){box.scrollLeft=Math.max(0,SBM.me[0]-box.clientWidth/2);box.scrollTop=Math.max(0,SBM.me[1]-box.clientHeight/2);}}
    const first=SBM.pins.find(q=>q.id===SB.regId)||SBM.pins[0];if(first)try{first.b.focus({preventScroll:true});}catch(err){first.b.focus();}}
  else{SBM.open=false;e.hidden=true;SBM.pick=null;SBM.zoom=null;if(SBM.from==='pause'){pauseOv.hidden=false;const r=document.getElementById('resumeBtn');if(r)r.focus();}else if(state==='paused')togglePause();}}
/* fast travel: to a place's start line. Only this player moves. */
function sbMapTravel(id){if(id==='shop'){SBM.from='drive';sbMap(false);if(state!=='race')return;sbPark(false);sbTravel({to:SB_SHOP.id,start:true,shop:true});return;}if(!sbRegOf(id))return;SBM.from='drive';sbMap(false);if(state!=='race')return;sbPark(false);sbTravel({to:id,start:true});}
/* the pause menu's Map button, directly under Resume, in Sandbox only */
function sbMapBtn(){let b=document.getElementById('sbMapBtn');if(!b){if(!SBX)return;const r=document.getElementById('resumeBtn');if(!r)return;b=document.createElement('button');b.id='sbMapBtn';b.className='cta';b.type='button';b.textContent='Map';b.style.cssText='background:var(--oven-2);box-shadow:0 5px 0 rgba(0,0,0,.35);border:2px solid var(--oven-3)';r.insertAdjacentElement('afterend',b);b.onclick=()=>sbMap(true,'pause');}
  b.hidden=!SBX;sbBackBtn();}
/* ---- Back to the track (web v199) ----
   The owner, 2026-11-15: "add a button in the pause menu that can just take you right to the nearest spot on the track ... when you click
   the button a confirmation pop up should pop up so the player doesn't accidentally hit the button and get teleported". The button sits
   under Map in Sandbox's pause menu; it asks first (Move me / Cancel; Esc, a tap outside or the pad's pointer on Cancel), then sets the kart down standing still on the
   middle of the nearest stretch of road at the same level (not on a loop), facing the way the track runs, and resumes. A challenge or
   delivery under way goes on: you stay in the same place. */
function sbBackBtn(){let b=document.getElementById('sbBackBtn');if(!b){if(!SBX)return;const m=document.getElementById('sbMapBtn');if(!m)return;b=document.createElement('button');b.id='sbBackBtn';b.className='cta';b.type='button';b.textContent='Back to the track';
    b.style.cssText='background:var(--oven-2);box-shadow:0 5px 0 rgba(0,0,0,.35);border:2px solid var(--oven-3)';m.insertAdjacentElement('afterend',b);b.onclick=()=>sbBackAsk(true);}
  b.hidden=!SBX;}
function sbBackAsk(on){let e=SB.backEl;if(!on){if(e)e.hidden=true;return;}if(!e){e=SB.backEl=document.createElement('div');e.id='sbBackAsk';e.setAttribute('role','dialog');e.setAttribute('aria-modal','true');
    e.style.cssText='position:fixed;inset:0;z-index:90;display:grid;place-items:center;background:rgba(0,0,0,.55)';
    e.innerHTML='<div style="max-width:min(88vw,380px);font:700 15px/1.35 system-ui,sans-serif;color:#fff4dc;background:#1d0f0a;border:2px solid rgba(255,244,220,.45);border-radius:18px;padding:18px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.6)">'
      +'<div style="font:900 20px/1.2 system-ui,sans-serif;margin-bottom:8px">Back to the track?</div><div style="opacity:.85">Your kart will be moved to the nearest part of the track, standing still.</div>'
      +'<div style="display:flex;gap:10px;justify-content:center;margin-top:16px"><button type="button" class="cta" id="sbBackYes">Move me</button><button type="button" class="cta" id="sbBackNo" style="background:var(--oven-2);border:2px solid var(--oven-3)">Cancel</button></div></div>';
    document.body.appendChild(e);e.querySelector('#sbBackYes').onclick=ev=>{ev.preventDefault();sbBackAsk(false);sbBackGo();};e.querySelector('#sbBackNo').onclick=ev=>{ev.preventDefault();sbBackAsk(false);};
    e.addEventListener('click',ev=>{if(ev.target===e)sbBackAsk(false);});addEventListener('keydown',ev=>{if(SB.backEl&&!SB.backEl.hidden&&ev.code==='Escape'){ev.preventDefault();ev.stopPropagation();sbBackAsk(false);}},true);}
  e.hidden=false;try{document.getElementById('sbBackNo').focus();}catch(err){}}
/* the nearest point of the track: by distance, with a difference in level counted three times over (a road overhead is not "near") */
function sbBackJ(k){const sl=T.L/N;let bj=0,bd=1e18;for(let j=0;j<N;j++){if(LOOPS.some(L=>{let d=j-L.j;if(d>N/2)d-=N;if(d<-N/2)d+=N;return Math.abs(d)*sl<420;}))continue;const p=track[j],y=(SB.kind==='toy'?0:groundAt(p.x,p.y))+(p.ey||0),d=(p.x-k.x)**2+(p.y-k.y)**2+9*((k.wy||0)-y)**2;if(d<bd){bd=d;bj=j;}}return bj;}
function sbBackGo(){if(!SBX||!player||SB.warp)return;const k=player,j=sbBackJ(k),p=track[j];k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.idx=j;
  k.speed=0;k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.charge=0;k.spin=0;k.boost=0;k.loop=null;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;
  if(SBF){const lvl=(SB.kind==='toy'?0:groundAt(k.x,k.y))+(p.ey||0);k.wy=k.pwy=k.lastG=sbG(k.x,k.y,lvl+2);k.idx=sbIdx(k,j);}else k.wy=k.pwy=k.lastG=kGround(k);
  k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rg=k.wy;k.rma=k.ma;cam.a=k.ma;camSnap=true;SB.cool=1;if(state==='paused'&&!pauseOv.hidden)togglePause();showBanner('Back on the track',1.6,'sm');}
/* ---- THE CLOCK (web v197): one day and night for the whole Sandbox world (the owner's brief, section 4) ----
   SB.clock runs 0..1 (0 midnight, .25 sunrise, .5 noon, .75 sunset); a day is SB_DAY seconds of driving; it is saved with the coins
   (crust-sb .t), so it carries through tunnels, fast travel, a race from the start line and a reload. It stands still while the
   game is paused or the map is up (sbTick only runs while driving).
   Nothing here is absolute. When a place is armed its own lights, fog, sky, exposure and materials are written down (sbClockArm,
   sbClockMats) and every update scales and tints from that record: at noon a place is exactly the place as raced. sbClockOff puts
   every value back before a race or the menu reads it (sbOff calls it), so nothing a race sees ever changes.
   Three kinds of place: 'out' (open air, and the pizzeria the kitchen pizzas stand in), 'in' (a room of the house: its lamps stay
   on at night and the windows go dark), 'dark' (a place whose own look is night: it is itself at night, and by day its sky and
   fill lift to a deep twilight while its glow stays).
   Cost: the materials are listed once per place; an update (ten a second) is a few hundred number writes. No new light, no new
   shadow pass, no render target, no screen-sized layer. */
/* THE SWITCH. false: nothing of the clock runs (no record, no light or material write, no read-out, nothing saved): every
   entry point below returns at once and Sandbox is exactly as in web v196. UNFINISHED, 2026-11-14: leave it false until the
   night pictures of every kind of place have been looked at (see docs or the hand-back). To work on it: set it true here. */
let SB_CLOCK=true;
const SB_DAY=720,SBC={rec:null,list:[],seen:new Set(),acc:0,keep:0,stars:null};
const _ckWarm=new THREE.Color('#ff9a4a'),_ckMoon=new THREE.Color('#9db8ff'),_ckNightSky=new THREE.Color('#6f8fe0'),_ckNightGnd=new THREE.Color('#10182c'),_ckLamp=new THREE.Color('#ffd2a0'),_ckLampG=new THREE.Color('#8a5a3a'),_ckDusk=new THREE.Color('#ffc8a0'),
  _ckTwTop=new THREE.Color('#1c2458'),_ckTwHor=new THREE.Color('#6a4f9a'),_ckTwBot=new THREE.Color('#1a1c3a'),_ckTwFog=new THREE.Color('#2c2a5e'),_ckTwHemi=new THREE.Color('#9a9ae0'),_ckSk=new THREE.Color(),_ckHz=new THREE.Color(),_ckC=new THREE.Color();
const sbSm=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
function sbClockNow(){if(SB.clock==null){const sv=sbSave();SB.clock=typeof sv.t==='number'&&sv.t>=0&&sv.t<1?sv.t:.4;/* a first visit starts in the middle of the morning */}return SB.clock;}
/* "7:40 pm": to the ten minutes, so the read-out does not flicker */
function sbClockStr(){const m=Math.round(sbClockNow()*144)%144*10,h=Math.floor(m/60),mm=m%60;return ((h+11)%12+1)+':'+(mm<10?'0':'')+mm+(h<12?' am':' pm');}
/* a small sun by day, a crescent by night (drawn with CSS: no picture to load) */
function sbClockIcon(){const e=Math.sin((sbClockNow()-.25)*Math.PI*2);return e>-.05?'<span style="display:inline-block;width:11px;height:11px;border-radius:50%;background:'+(e<.25?'#ffa94a':'#ffd65a')+';box-shadow:0 0 0 2px rgba(255,214,90,.35);vertical-align:-1px;margin:0 7px 0 2px"></span>':'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;box-shadow:inset -4px -1px 0 0 #dfe8ff;vertical-align:-1px;margin:0 6px 0 2px"></span>';}
/* the day's numbers: e the sun's height (-1 midnight .. 1 noon), D daylight 0..1, W the golden hour (1 at sunrise and sunset),
   L the lamps (1 = on), M the moon (it rises only once the sun's light is quite gone, so the two never cross-fade through each other) */
function sbClockF(){const t=sbClockNow(),e=Math.sin((t-.25)*Math.PI*2);return {t,e,D:sbSm(-.2,.24,e),W:Math.exp(-(e/.26)*(e/.26)),L:1-sbSm(-.12,.14,e),M:sbSm(-.2,-.45,e)};}
/* a place has just been armed: write down how it is lit, then light it for the hour */
function sbClockArm(){if(!SB_CLOCK)return;sbClockOff();const def=MAPS[mapIdx],c=o=>o.clone(),d=sunDir;
  const R=SBC.rec={id:def.id,kind:def.theme==='night'?'dark':(def.toy&&def.id!=='backyard')?'in':'out',sun:[c(sun.color),sun.intensity],hemi:[c(hemi.color),c(hemi.groundColor),hemi.intensity],rim:[c(rimL.color),rimL.intensity],dir:c(d),az:Math.atan2(d.z,d.x),el:Math.asin(Math.max(-1,Math.min(1,d.y))),
    turn:!def.toy&&!TOYSUN&&def.theme!=='night',fog:scene.fog?c(scene.fog.color):null,bg:scene.background&&scene.background.isColor?c(scene.background):null,exp:renderer.toneMappingExposure,bloom:POST.grade.bloom,thr:POST.grade.thr,sky:null};
  if(sky&&sky.material&&sky.material.uniforms&&sky.material.uniforms.top){const u=sky.material.uniforms;R.sky={u,top:c(u.top.value),hor:c(u.hor.value),bot:c(u.bot.value),sc:c(u.sunCol.value),sd:c(u.sunDir.value)};}
  SBC.list=[];SBC.seen=new Set();sbClockMats();
  if(R.kind==='out'&&(R.sky||def.id==='backyard')){/* stars, where there is an open sky: one small cloud of points that follows the camera */const P=[];let sd=977;const r=()=>(sd=sd*16807%2147483647)/2147483647;for(let i=0;i<620;i++){const a=r()*Math.PI*2,y=.1+r()*.9,q=Math.sqrt(1-y*y);P.push(Math.cos(a)*q*7600,y*7600,Math.sin(a)*q*7600);}
    const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(P,3));const st=SBC.stars=new THREE.Points(g,new THREE.PointsMaterial({color:'#000000',size:2.1,sizeAttenuation:false,transparent:false,blending:THREE.AdditiveBlending,depthWrite:false,fog:false,toneMapped:false}));st.frustumCulled=false;st.renderOrder=-.9;st.visible=false;scene.add(st);/* (web v199: they were see-through things, drawn after everything solid and sorted among the other see-through things by distance, so they came out in front of the far tree cards, which stand further off than this ball of points. Now they are drawn among the solid things, straight after the sky (renderOrder -1) and before everything else, adding light and writing no depth: whatever is drawn later covers them. They fade by their colour, not by see-through) */}
  sbClockApply();}
/* the materials the clock touches, listed once (again when the karts have been rebuilt): k 0 a lit surface (its share of the sky's
   light), 1 a surface with a little glow of its own that stands in for daylight (the tree cards), 2 a lamp (anything that glows
   strongly: windows, signs, neon, a car's lights), 3 paint that no light reaches (unlit scenery: it is dimmed by hand),
   4 a picture of the far distance or of the sky (tinted like the sky). Sandbox's own things (coins, arches, signs, the flag) are
   left alone: they must read at midnight. */
function sbClockMats(){if(!SB_CLOCK||!SBC.rec)return;const S=SBC.seen,walk=o=>{if(o===SB.grp||o===SBC.stars)return;const ms=o.material?(Array.isArray(o.material)?o.material:[o.material]):null;
    if(ms)for(const m of ms){if(!m||S.has(m))continue;S.add(m);
      if(m.isMeshStandardMaterial){const em=m.emissiveIntensity>0&&m.emissive.r+m.emissive.g+m.emissive.b>.02;SBC.list.push({m,k:em?(m.emissiveIntensity>=.3?2:1):0,env:m.envMapIntensity,ei:m.emissiveIntensity});}
      else if((m.isMeshBasicMaterial||m.isSpriteMaterial)&&m.blending!==THREE.AdditiveBlending&&m.color){const far=m.name==='sky_window'/* (the kitchen's window panes: patch 34) */||m.map&&m.toneMapped===false&&(m.fog===false||/outside|ycards|sky|mount|skyline|pano|riverbed|space/.test((m.name||'')+' '+(m.map.name||'')));
        if(far)SBC.list.push({m,k:4,col:m.color.clone()});else if(m.toneMapped!==false)SBC.list.push({m,k:3,col:m.color.clone()});}}
    for(const ch of o.children)walk(ch);};walk(scene);}
function sbClockApply(){const R=SBC.rec;if(!SB_CLOCK||!R)return;const F=sbClockF(),D=F.D,N=1-D,W=F.W,L=F.L,K=R.kind,G=POST.grade;sbSave().t=+F.t.toFixed(4);
  let sunK,hemiK,rimK,envK,paintK,lampK,fillK,expK=1;const sk=_ckSk;
  if(K==='dark'){/* its own look is the night: by day the sky and the fill lift to a deep twilight, the glow stays */
    sunK=1+.3*D;hemiK=1+.6*D;rimK=1;envK=1+.3*D;paintK=1;lampK=1-.1*D;fillK=1;
    sun.color.copy(R.sun[0]);hemi.color.copy(R.hemi[0]).lerp(_ckTwHemi,.3*D);hemi.groundColor.copy(R.hemi[1]);
    if(R.fog)scene.fog.color.copy(R.fog).lerp(_ckTwFog,.5*D);if(R.bg)scene.background.copy(R.bg).lerp(_ckTwFog,.5*D);
    if(R.sky){const u=R.sky.u;u.top.value.copy(R.sky.top).lerp(_ckTwTop,.55*D);u.hor.value.copy(R.sky.hor).lerp(_ckTwHor,.55*D);u.bot.value.copy(R.sky.bot).lerp(_ckTwBot,.55*D);}
    sk.setRGB(1+.5*D,1+.45*D,1+.6*D);G.bloom=R.bloom-.06*D;}
  else{const ins=K==='in';
    sunK=D*(1-.3*W)+N*F.M*(ins?.05:.11);sun.color.copy(R.sun[0]).lerp(_ckWarm,.7*W*D).lerp(_ckMoon,N);
    if(ins){/* a room: its lamps are on at night (a little warmer and dimmer than the day) */hemiK=.6+.4*D;rimK=.5+.5*D;envK=.5+.5*D;paintK=.75+.25*D;lampK=1+1.4*L;fillK=.7+.3*D;hemi.color.copy(R.hemi[0]).lerp(_ckLamp,.55*N);hemi.groundColor.copy(R.hemi[1]).lerp(_ckLampG,.4*N);}
    else{hemiK=.3+.7*D;rimK=.35+.65*D;envK=.2+.8*D;paintK=.16+.84*D;lampK=1+1.1*L;fillK=.3+.7*D;expK=1+.1*N;hemi.color.copy(R.hemi[0]).lerp(_ckNightSky,.75*N).lerp(_ckDusk,.3*W);hemi.groundColor.copy(R.hemi[1]).lerp(_ckNightGnd,.6*N);}
    /* the sky's tint: white by day, warm at the golden hour, a dark blue at night; fog, the background, the sky and every picture of the distance take it */
    sk.setRGB(1,1,1).lerp(_ckC.setRGB(1,.7,.5),.5*W).multiplyScalar(.05+.95*D);sk.r+=.012*N;sk.g+=.02*N;sk.b+=.05*N;
    if(R.fog)scene.fog.color.copy(R.fog).multiply(sk);if(R.bg)scene.background.copy(R.bg).multiply(sk);
    if(R.sky){const u=R.sky.u;u.top.value.copy(R.sky.top).multiply(sk);u.hor.value.copy(R.sky.hor).lerp(_ckWarm,.45*W).multiply(sk);u.bot.value.copy(R.sky.bot).multiply(sk);u.sunCol.value.copy(R.sky.sc).lerp(_ckWarm,.6*W*D).lerp(_ckMoon,N).multiplyScalar(D+N*F.M*.55);}
    G.bloom=R.bloom+(ins?.1:.12)*L;G.thr=R.thr-.03*L;}
  sun.intensity=R.sun[1]*sunK;hemi.intensity=R.hemi[2]*hemiK;rimL.intensity=R.rim[1]*rimK;renderer.toneMappingExposure=R.exp*expK;
  if(R.turn){/* the sun crosses the sky and sets; the moon comes up on the other side once the sun's light is gone (the light is at nothing when they swap) */
    let az,el;if(F.e>-.2){el=Math.max(.3,R.el*(.32+.68*sbSm(0,1,F.e)));az=R.az+(F.t-.5)*2.2;}else{el=Math.max(.55,R.el*.9);az=R.az+2.6+((F.t+.5)%1-.5)*1.2;}
    sunDir.set(Math.cos(el)*Math.cos(az),Math.sin(el),Math.cos(el)*Math.sin(az));if(R.sky)R.sky.u.sunDir.value.copy(sunDir);}
  for(const r of SBC.list){const m=r.m;if(r.k<3){m.envMapIntensity=r.env*envK;if(r.k===1)m.emissiveIntensity=r.ei*fillK;else if(r.k===2)m.emissiveIntensity=r.ei*(r.ei>1?1+(lampK-1)*.4:lampK);}
    else if(r.k===3){m.color.copy(r.col).multiplyScalar(paintK);if(K==='out'){m.color.r*=1-.3*N;m.color.g*=1-.15*N;}}else m.color.copy(r.col).multiply(sk);}
  const st=SBC.stars;if(st){const o=N*N*.95;st.visible=o>.02;st.material.color.setRGB(.93*o,.95*o,o);}/* the start line's flag and ring (web v199): they are drawn unlit and bright, and the night's stronger bloom made a blaze of them; at night they keep about half their brightness and the glow over them a third */const fl=SB.flag;if(fl&&fl.mats){const k=.5+.5*D;for(const m of fl.mats)m.color.setScalar(k);if(fl.glow)fl.glow.opacity=.55*(.33+.67*D);}}
/* each step of driving: the clock goes on; the light follows ten times a second (a step of a ten-thousandth of a day: nothing to see) */
function sbClockTick(dt){if(!SB_CLOCK)return;SB.clock=(sbClockNow()+dt/SB_DAY)%1;SBC.acc+=dt;if(SBC.acc>=.1){SBC.acc=0;sbClockApply();}SBC.keep+=dt;if(SBC.keep>=20){SBC.keep=0;sbKeep();}}
/* everything back as the place itself has it (a race, the menu, or another place is next) */
function sbClockOff(){const R=SBC.rec;if(!R)return;/* (nothing was written down: nothing to put back. With the switch off this is always so) */SBC.rec=null;sun.color.copy(R.sun[0]);sun.intensity=R.sun[1];hemi.color.copy(R.hemi[0]);hemi.groundColor.copy(R.hemi[1]);hemi.intensity=R.hemi[2];rimL.color.copy(R.rim[0]);rimL.intensity=R.rim[1];sunDir.copy(R.dir);
  if(R.fog&&scene.fog)scene.fog.color.copy(R.fog);if(R.bg&&scene.background&&scene.background.isColor)scene.background.copy(R.bg);renderer.toneMappingExposure=R.exp;POST.grade.bloom=R.bloom;POST.grade.thr=R.thr;
  if(R.sky){const u=R.sky.u;u.top.value.copy(R.sky.top);u.hor.value.copy(R.sky.hor);u.bot.value.copy(R.sky.bot);u.sunCol.value.copy(R.sky.sc);u.sunDir.value.copy(R.sky.sd);}
  for(const r of SBC.list){const m=r.m;if(r.k<3){m.envMapIntensity=r.env;m.emissiveIntensity=r.ei;}else m.color.copy(r.col);}SBC.list=[];SBC.seen=new Set();
  if(SBC.stars){scene.remove(SBC.stars);SBC.stars.geometry.dispose();SBC.stars.material.dispose();SBC.stars=null;}if(SB.save&&SB.clock!=null){SB.save.t=+SB.clock.toFixed(4);sbKeep();}}
/* for the tests and for looking: set the hour and light the place for it at once */
function sbClockSet(t){if(!SB_CLOCK)return null;SB.clock=((+t||0)%1+1)%1;sbClockApply();SB.hudT=0;return SB.clock;}
/* ---- the mechanic's shop (web v200) ----
   The owner, 2026-11-15: "in the garage map add a section in the corner or somewhere in the room that will be added to the mini map and have a
   fast travel point. It will be a little mechanic garage shop we can pull the car into and we will enter the garage menu and character select
   where we can change characters and vehicles from inside the game without having to exit and restart".
   A toy garage playset on the garage floor (SB_SHOP: an open spot between the green bin and the tyre, in front of the shelf, chosen by
   searching the floor for room and headroom away from the track). Its walls are solid (SB.shapes); drive in through the open front and the
   driver screen opens (then Build kart, as from the menu); "Back to Sandbox" (the driver screen's back button, or the garage's last button)
   brings you back out of the shop's door with what you chose. On the world map it is a pin of its own in the garage ("Mechanic's shop"),
   and fast travel to it sets you down at its door. */
const SB_SHOP={id:'garage',x:205,z:-443,w:100,d:90,h:46};
function sbShopIn(){return SBX&&SB.regId===SB_SHOP.id;}
function sbShopBuild(){if(!sbShopIn()||!SB.grp)return;const S=SB_SHOP,G=new THREE.Group(),x0=S.x-S.w/2,x1=S.x+S.w/2,z0=S.z-S.d/2,z1=S.z+S.d/2,H=S.h,T=4;
  const pl=(c,o)=>new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.38,metalness:.02},o||{}));
  const box=(w,h,d,m,x,y,z)=>{const o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;G.add(o);return o;};
  const red=pl('#d8342a'),yel=pl('#f5c21b'),blu=pl('#2a5bd7'),gry=pl('#8d949c',{roughness:.6}),drk=pl('#2b2f35',{roughness:.7});
  /* the base and its painted floor */box(S.w+8,2,S.d+8,gry,S.x,1,S.z);
  {const c=cnv(256,256),g=c.getContext('2d');g.fillStyle='#5d636b';g.fillRect(0,0,256,256);g.strokeStyle='#f5c21b';g.lineWidth=10;g.setLineDash([26,16]);g.strokeRect(40,30,176,200);g.setLineDash([]);g.fillStyle='rgba(255,255,255,.12)';for(let i=0;i<8;i++)g.fillRect(0,i*32,256,2);const t=T2(c);t.userData.keepCanvas=true;
    const f=new THREE.Mesh(new THREE.PlaneGeometry(S.w-2*T,S.d-T),new THREE.MeshStandardMaterial({map:t,roughness:.55}));f.rotation.x=-Math.PI/2;f.position.set(S.x,2.05,S.z-T/2);f.receiveShadow=true;G.add(f);}
  /* walls: the back and the two sides, red with a yellow band; the roof blue, with an overhang over the open front */
  box(S.w,H,T,red,S.x,H/2+2,z0+T/2);for(const sx of [x0+T/2,x1-T/2])box(T,H,S.d,red,sx,H/2+2,S.z);
  for(const sx of [x0+T/2,x1-T/2])box(T+.6,5,S.d+.6,yel,sx,H*.62+2,S.z);box(S.w+.6,5,T+.6,yel,S.x,H*.62+2,z0+T/2);
  box(S.w+10,4,S.d+16,blu,S.x,H+4,S.z+4);
  /* the sign over the door */{const c=cnv(512,128),g=c.getContext('2d');g.fillStyle='#fbf3df';g.fillRect(0,0,512,128);g.strokeStyle='#d8342a';g.lineWidth=10;g.strokeRect(5,5,502,118);g.fillStyle='#1b1f26';g.font='900 64px Arial';g.textAlign='center';g.textBaseline='middle';g.fillText('MECHANIC',284,68);
    /* a spanner */g.save();g.translate(72,64);g.rotate(-.7);g.fillStyle='#8d949c';g.fillRect(-36,-7,72,14);g.beginPath();g.arc(-40,0,16,0,6.283);g.arc(40,0,16,0,6.283);g.fill();g.fillStyle='#fbf3df';g.fillRect(-58,-6,16,12);g.fillRect(42,-6,16,12);g.restore();
    const t=T2(c);t.userData.keepCanvas=true;const b=new THREE.Mesh(new THREE.PlaneGeometry(S.w*.86,S.w*.86/4),new THREE.MeshBasicMaterial({map:t,toneMapped:false}));b.position.set(S.x,H+14,z1+12.2);G.add(b);
    box(S.w*.88,S.w*.88/4+2,1.2,drk,S.x,H+14,z1+11.4);}
  /* inside: a stack of tyres, a toolbox, two lift posts */
  {const tg=new THREE.TorusGeometry(5,2.4,10,22);for(let i=0;i<3;i++){const o=new THREE.Mesh(tg,drk);o.rotation.x=Math.PI/2;o.position.set(x0+14,4.5+i*4.6,z0+14);o.castShadow=true;G.add(o);}}
  box(16,12,9,red,x1-16,8,z0+10);box(16.4,2,9.4,gry,x1-16,14.6,z0+10);for(let i=0;i<3;i++)box(14,.6,.4,gry,x1-16,4+i*3.4,z0+14.8);
  for(const sx of [S.x-24,S.x+24])box(3,30,3,yel,sx,17,S.z-14);box(52,2.4,3,yel,S.x,30,S.z-14);
  G.traverse(o=>{o.userData.sunlit=true;});SB.grp.add(G);SB.shopG=G;
  /* solid: the walls (the roof is overhead, out of a kart's way) */const wall=(a,b,c,d)=>SB.shapes.push({t:'box',x0:a,x1:b,z0:c,z1:d,b:0,h:H+2});
  wall(x0,x1,z0,z0+T);wall(x0,x0+T,z0,z1);wall(x1-T,x1,z0,z1);SB.shopIn=false;}
/* each step: driving in opens the driver screen (once a visit: you have to leave the shop before it opens again) */
function sbShopTick(k){if(!sbShopIn())return;const S=SB_SHOP,inside=k.x>S.x-S.w/2+10&&k.x<S.x+S.w/2-10&&k.y>S.z-S.d/2+6&&k.y<S.z+S.d/2-22&&Math.abs(k.wy||0)<8;
  if(inside&&!SB.shopIn&&!SB.trav&&state==='race'){SB.shopIn=true;sbShopOpen();return;}if(!inside&&k.y>S.z+S.d/2+10)SB.shopIn=false;}
function sbShopOpen(){if(SBA&&SBA.act)sbActEnd('cancel');SB.shopBack=true;try{SFX.ready();}catch(e){}toMenu();goStep('driver');sbShopLabels(true);}
function sbShopLabels(on){const d=document.querySelector('[data-step="driver"] .st-back'),g=$('gDone');if(on){if(d){d.dataset.was=d.innerHTML;d.innerHTML='‹ Sandbox';}if(g){g.dataset.was=g.innerHTML;g.innerHTML='Back to Sandbox ›';}}
  else{if(d&&d.dataset.was){d.innerHTML=d.dataset.was;delete d.dataset.was;}if(g&&g.dataset.was){g.innerHTML=g.dataset.was;delete g.dataset.was;}}}
/* the driver screen's back, or the garage's last button: back into Sandbox, out of the shop's door (true: handled) */
function sbShopDone(){if(!SB.shopBack)return false;SB.shopBack=false;sbShopLabels(false);try{closeGarage();}catch(e){}const mi=MAPS.findIndex(m=>m.id===SB_SHOP.id);if(mi<0)return false;mode='sb';SB.shopPut=true;introSkip=true;/* (no fly-over: straight back out of the door) */menu.hidden=true;goRace(mi);return true;}
/* where the kart comes out: just in front of the door, facing away from it */
function sbShopPut(k){const S=SB_SHOP;k.x=k.px=S.x;k.y=k.py=S.z+S.d/2+34;k.a=k.ma=k.pa=k.pma=Math.PI/2;k.speed=0;k.wy=k.pwy=k.lastG=sbG(k.x,k.y,2);k.idx=sbIdx(k,k.idx);k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rma=k.ma;cam.a=k.ma;camSnap=true;SB.shopIn=false;}
