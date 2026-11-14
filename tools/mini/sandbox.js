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
  world.traverse(o=>{if(!o.isMesh||!o.geometry||!o.geometry.attributes||!o.geometry.attributes.position||o.userData.noCol)return;for(let p=o;p;p=p.parent)if(!p.visible)return;const m=Array.isArray(o.material)?o.material[0]:o.material;if(!m)return;
    if(!o.userData.col){if(m.transparent||m.alphaTest>0||m.depthWrite===false||m.isShaderMaterial||SB_SOFT.test(m.name||''))return;if(o.isInstancedMesh&&!m.name)return;}
    minTop=o.userData.colMin||0;/* (a loop's hoop: only what stands higher than a step is solid. Its low lips lie beside the lanes into and out of the loop, and a kart near the middle rail was bumped up onto them: the owner's "going around the loops is a little glitchy in sandbox mode") */isThin=/toyblue/.test(m.name||'');/* the track's posts, bars and gates: solid to a kart, but the camera looks past them (sbSolid) */const g=o.geometry;if(!g.boundingBox)g.computeBoundingBox();const pa=g.attributes.position,ix=g.index,nt=(ix?ix.count:pa.count)/3,ni=o.isInstancedMesh?o.count:1;
    for(let q=0;q<ni;q++){if(o.isInstancedMesh){o.getMatrixAt(q,M4);M4.premultiply(o.matrixWorld);}else M4.copy(o.matrixWorld);
      /* nowhere near the room, or wholly on the floor: skip it without looking at a triangle */const bb=g.boundingBox;let in0=false,top=-1e9;for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);if(v.y>top)top=v.y;}
      {const lo=new THREE.Vector3(1e9,1e9,1e9),hi=new THREE.Vector3(-1e9,-1e9,-1e9);for(let c=0;c<8;c++){v.set(c&1?bb.max.x:bb.min.x,c&2?bb.max.y:bb.min.y,c&4?bb.max.z:bb.min.z).applyMatrix4(M4);lo.min(v);hi.max(v);}in0=hi.x>=x0&&lo.x<=x0+nx*C&&hi.z>=z0&&lo.z<=z0+nz*C;}
      if(!in0||(top<1.2&&!og))continue;used++;
      for(let t=0;t<nt;t++){for(let c=0;c<3;c++){const idx=ix?ix.getX(t*3+c):t*3+c;v.fromBufferAttribute(pa,idx).applyMatrix4(M4);W[c*3]=v.x;W[c*3+1]=v.y;W[c*3+2]=v.z;}tri(W[0],W[1],W[2],W[3],W[4],W[5],W[6],W[7],W[8]);}}});
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
function sbBlocked(x,z,wy){const n=sbSurf(x,z),S=SB.S,lv=sbLvl();for(let i=0;i<n;i++)if(S[i][2]>=0&&S[i][4]&&Math.abs(S[i][1]+2.5-wy)<=lv)return false;
  if(SB.kind==='open'&&!SB.inG){/* a pizza's own ground: a face that rises more than a step from where the kart stands is a cliff, not a hill (the land beside some tracks climbs 180 in a few lengths), and water deeper than the wheels is a shore */const g0=groundAt(x,z);if(g0>wy+SB_STEP||(WATER_Y!=null&&g0<WATER_Y-3&&wy<WATER_Y+SB_HEAD))return true;}
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
const SB_GW=17,SB_GLEN=190;
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
     On a road in the sky the mouth is an arch over the left-hand lane with no tunnel behind it: the warp picture covers the load (sbCover). */
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
        const end=new THREE.Mesh(new THREE.PlaneGeometry(2*rx,ry),sbWarpMat(0,{c:[.5,.42],s:.55,core:1.1}));end.position.set(0,ry/2,-L+.6);G.add(end);g.endAt=[g.x+g.nx*(L-1),g.y+ry*.42,g.z+g.nz*(L-1)];}
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
    if((dk>-4&&Math.abs(lk)<g.hw+8)||(dc>0&&Math.abs(lc)<g.hw+12)){pull=true;if(Math.cos(k.rma)*g.nx+Math.sin(k.rma)*g.nz<0)dir=-1;}}
  SB_WV.value=(SB_WV.value+dt*.9*dir+1000)%1000;sbPull(pull);}
/* ---- the cover over a load ----
   Building the next region stops the game for a second or more. For that time the picture is held by a cover the browser itself animates
   (it keeps moving while the game cannot): the last frame, warp streaks flying out of the tunnel's end over it, and the kart on top, cut out of
   its own picture (drawn alone on black and on white: the difference is its outline). Afterwards the cover fades over the new place. */
function sbDuctEl(){let e=SB.duct;if(!e){e=SB.duct=document.createElement('div');e.id='sbDuct';e.style.cssText='position:absolute;inset:0;z-index:5;background:#05030a;opacity:0;pointer-events:none;overflow:hidden';
    const st=document.createElement('style');st.textContent='#sbDuct canvas{position:absolute;left:0;top:0;width:100%;height:100%}#sbDuct b{position:absolute;left:50%;top:46%;width:0;height:0}#sbDuct i{position:absolute;left:-90vmax;top:-90vmax;width:180vmax;height:180vmax;background:center/contain no-repeat;animation:sbwarp 1.05s linear infinite;will-change:transform,opacity}'
      +'@keyframes sbwarp{from{transform:scale(.1);opacity:0}14%{opacity:1}75%{opacity:.85}to{transform:scale(2.3);opacity:0}}@keyframes sbbob{from{transform:translateY(-.3%)}to{transform:translateY(.3%)}}#sbDuctK{animation:sbbob .34s ease-in-out infinite alternate;will-change:transform}';document.head.appendChild(st);
    /* the streaks: drawn once */const S=768,c=cnv(S,S),q=c.getContext('2d'),rnd=prng(4711);q.lineCap='round';for(let i=0;i<300;i++){const a=rnd()*6.28318,r0=(.1+rnd()*.5)*S/2,r1=Math.min(S/2,r0+(.08+rnd()*.34)*S/2),t=rnd(),col=t<.45?'255,248,255':t<.72?'160,118,255':t<.9?'110,160,255':'120,255,185',gr=q.createLinearGradient(S/2+Math.cos(a)*r0,S/2+Math.sin(a)*r0,S/2+Math.cos(a)*r1,S/2+Math.sin(a)*r1);
      gr.addColorStop(0,'rgba('+col+',0)');gr.addColorStop(.7,'rgba('+col+','+(.5+rnd()*.5).toFixed(2)+')');gr.addColorStop(1,'rgba('+col+',0)');q.strokeStyle=gr;q.lineWidth=.8+rnd()*2.4;q.beginPath();q.moveTo(S/2+Math.cos(a)*r0,S/2+Math.sin(a)*r0);q.lineTo(S/2+Math.cos(a)*r1,S/2+Math.sin(a)*r1);q.stroke();}
    let url='';try{url=c.toDataURL('image/png');}catch(err){}
    const A=SB.covA=document.createElement('canvas');e.appendChild(A);for(let i=0;i<5;i++){const b=document.createElement('b');b.style.transform='rotate('+(i*67)+'deg)';const r=document.createElement('i');r.style.backgroundImage='url('+url+')';r.style.animationDelay=(-i*.21)+'s';b.appendChild(r);e.appendChild(b);}
    const B=SB.covB=document.createElement('canvas');B.id='sbDuctK';e.appendChild(B);stage.appendChild(e);}return e;}
const _sbBk=new THREE.Color('#000000'),_sbWh=new THREE.Color('#ffffff'),_sbV=new THREE.Vector3();
function sbCover(g){const e=sbDuctEl(),A=SB.covA,B=SB.covB,sw=stage.clientWidth||innerWidth,sh=stage.clientHeight||innerHeight,w=Math.max(64,Math.min(800,sw)),h=Math.max(36,Math.round(w*sh/sw));A.width=B.width=w;A.height=B.height=h;
  const ga=A.getContext('2d'),gb=B.getContext('2d');ga.fillStyle='#05030a';ga.fillRect(0,0,w,h);let vx=.5,vy=.44;
  try{const cv=renderer.domElement,bg=scene.background,hid=[];renderer.setRenderTarget(null);renderer.render(scene,camera);ga.drawImage(cv,0,0,w,h);
    if(g&&g.endAt){_sbV.set(g.endAt[0],g.endAt[1],g.endAt[2]).project(camera);if(_sbV.z<1&&Math.abs(_sbV.x)<.8&&Math.abs(_sbV.y)<.8){vx=(_sbV.x+1)/2;vy=(1-_sbV.y)/2;}}
    /* the kart alone: everything else in the scene hidden for two pictures */let top=player.m.g;while(top.parent&&top.parent!==scene)top=top.parent;for(const o of scene.children)if(o!==top&&!o.isLight&&o.visible){hid.push(o);o.visible=false;}
    const c1=cnv(w,h),c2=cnv(w,h),g1=c1.getContext('2d'),g2=c2.getContext('2d');
    try{scene.background=_sbBk;renderer.render(scene,camera);g1.drawImage(cv,0,0,w,h);scene.background=_sbWh;renderer.render(scene,camera);g2.drawImage(cv,0,0,w,h);}finally{scene.background=bg;for(const o of hid)o.visible=true;}
    const a=g1.getImageData(0,0,w,h).data,b=g2.getImageData(0,0,w,h).data,O=gb.createImageData(w,h),d=O.data;
    for(let i=0;i<a.length;i+=4){const al=Math.max(0,Math.min(255,255-((b[i]-a[i])+(b[i+1]-a[i+1])+(b[i+2]-a[i+2]))/3));if(al<6)continue;const f=255/al;d[i]=Math.min(255,a[i]*f);d[i+1]=Math.min(255,a[i+1]*f);d[i+2]=Math.min(255,a[i+2]*f);d[i+3]=al;}
    gb.putImageData(O,0,0);if(renderer.shadowMap)renderer.shadowMap.needsUpdate=true;}catch(err){console.warn('sandbox cover',err);}
  e.querySelectorAll('b').forEach(q=>{q.style.left=(vx*100).toFixed(1)+'%';q.style.top=(vy*100).toFixed(1)+'%';});e.style.transition='none';e.style.opacity=1;SB.ductO=1;}
function sbCoverOff(){const e=SB.duct;if(!e)return;e.style.transition='opacity .5s ease-out';e.style.opacity=0;SB.ductO=0;}
function sbDuctShow(){/* (until web v193 the picture went dark by how deep in a passage the kart was; now the tunnel is real, and the cover comes only with the load) */}
/* through a gate: the next region is built while the duct fills the picture, and the kart comes out of the matching gate */
async function sbTravel(g){if(SB.trav)return;const mi=MAPS.findIndex(m=>m.id===g.to);if(mi<0||!sbRegOf(g.to))return;SB.trav=g;const k=player,sp=Math.max(70,Math.abs(k.speed));sbCover(g);state='loading';
  try{await paint();await paint();projectiles.forEach(p=>scene.remove(p.mesh));hazards.forEach(h=>scene.remove(h.mesh));projectiles=[];hazards=[];
    if(mi!==mapIdx||curRev){mapIdx=mi;try{store.set('crust-map',mi);}catch(e){}loadMap(mi,false);}for(const q of karts){q.idx=0;q.prog=0;q.loop=null;q.sc=null;q.glide=false;}
    await Promise.all(Object.values(PROPT).map(t=>t.image&&t.image.decode&&!t.image.complete?t.image.decode().catch(()=>{}):null));}catch(e){console.warn('sandbox travel',e);}
  sbArm();const a=g.start?null:SB.gates.find(q=>q.id===g.at)||SB.gates[0];
  if(a&&a.road){k.x=k.px=a.x+a.nx*34;k.y=k.py=a.z+a.nz*34;k.a=k.ma=k.pa=k.pma=Math.atan2(a.nz,a.nx);k.idx=(a.j+Math.round(34/(T.L/N)))%N;}
  else if(a){const out=a.plain?46:SB_GLEN-60;k.x=k.px=a.x+a.nx*out;k.y=k.py=a.z+a.nz*out;const h=Math.atan2(-a.nz,-a.nx);k.a=k.ma=k.pa=k.pma=h;}
  else{/* no gate to come out of (fast travel): the start line, a little behind it */const j=(N-Math.round(40/(T.L/N)))%N,p=track[j];k.x=k.px=p.x;k.y=k.py=p.y;k.a=k.ma=k.pa=k.pma=Math.atan2(p.ty,p.tx);k.idx=j;}
  k.speed=sp;k.wvy=0;k.gRate=0;k.air=false;k.big=false;k.drift=0;k.charge=0;k.spin=0;k.z=k.pz=0;k.bpx=k.x;k.bpy=k.y;
  if(SBF){const lvl=a&&!a.road?a.y:((SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0));k.wy=k.pwy=k.lastG=sbG(k.x,k.y,lvl+2);k.idx=sbIdx(k,k.idx);}else k.wy=k.pwy=k.lastG=kGround(k);
  k.rx=k.x;k.ry=k.y;k.rz=k.wy;k.rg=k.wy;k.rma=k.ma;cam.a=k.ma;camSnap=true;try{warmScene();}catch(e){}SB.cool=1;state='race';SB.trav=null;sbCoverOff();SB.hudT=0;sbHud();showBanner(SB.reg.name,2,'sm');}
/* ---- a race from its start line ----
   The start line of the region's track carries a marker: a chequered ring on the road and a small chequered flag turning above it. Drive up
   to it and a button offers the race (tap it; Enter on a keyboard; D-pad up on a controller). The race is an ordinary single race on this
   track at the chosen speed class; when it is over, or left, you are back in Sandbox at the same start line. */
function sbFlag(){const p=track[0],e=(SB.kind==='toy'?0:groundAt(p.x,p.y))+(p.ey||0),c=cnv(64,64),g=c.getContext('2d');for(let i=0;i<4;i++)for(let j=0;j<4;j++){g.fillStyle=(i+j)%2?'#141210':'#fbf6ea';g.fillRect(i*16,j*16,16,16);}
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
  sbCoins();sbGates();{/* the map remembers this place's tunnels */const sv=sbSave();if(!sv.g)sv.g={};sv.g[SB.regId]=SB.gates.map(g=>[Math.round(g.x),Math.round(g.z),g.label]);sbKeep();}sbFlag();SB.hudT=0;SB.msgT=0;SB.camF=1;if(!SB.trav)sbPark(false);sbMapBtn();document.body.classList.add('battle');}
function sbOff(){if(!SBX)return;SBX=false;SBF=false;const def=MAPS[mapIdx];BATTLE=!!(def&&def.battle);if(SB.grp){/* the passages' own shapes, signs and shaders go with the place (everything else in the group is shared) */for(const G of SB.grp.children)if(G.userData.sbGate)G.traverse(o=>{if(!o.isMesh)return;o.geometry.dispose();const m=o.material;if(m.map)m.map.dispose();m.dispose();});scene.remove(SB.grp);SB.grp=null;SB.im=null;}SB.coins=[];SB.shapes=[];SB.gates=[];SB.hash=null;SB.col=null;if(SB.el)SB.el.hidden=true;SB.flag=null;sbRaceBtn(false);sbPull(false);SB.park=false;if(SB.parkEl)SB.parkEl.hidden=true;sbMapBtn();if(SB.duct&&!SB.trav){SB.duct.style.opacity=0;SB.ductO=0;}document.body.classList.toggle('battle',BATTLE);}
function sbStart(){for(const k of karts){k.bal=0;k.bbS=0;k.bbOut=0;if(SBF){k.wy=k.pwy=k.lastG=sbG(k.x,k.y,(SB.kind==='toy'?0:groundAt(k.x,k.y))+(track[k.idx].ey||0)+2);k.wvy=0;k.gRate=0;k.air=false;k.bpx=k.x;k.bpy=k.y;}}
  if(BB.grp){scene.remove(BB.grp);BB.grp=null;}sbHud();const f=sbFound();showBanner(SB.reg.name,2.2,'md');}
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
function sbTick(dt){sbParkBtn();if(state!=='race'){sbRaceBtn(false);return;}const k=player;if(!k)return;
  if(sbStop()&&!k.loop&&!k.air){const sp=k.speed,d=Math.min(Math.abs(sp),(140+Math.abs(sp)*5)*dt);k.speed=sp-Math.sign(sp)*d;if(Math.abs(k.speed)<1.5)k.speed=0;k.boost=0;k.drift=0;k.charge=0;}
{const f=SB.flag,near=!!f&&!SB.trav&&(k.x-f.x)**2+(k.y-f.z)**2<46*46&&Math.abs((k.wy||0)-f.y)<10;sbRaceBtn(near);if(near){try{const gp=navigator.getGamepads&&navigator.getGamepads()[PAD.idx];const up=!!gp&&gp.buttons[12]&&gp.buttons[12].pressed;if(up&&!SB.padUp)sbRaceHere();SB.padUp=up;}catch(e){}}}if(SB.cool>0)SB.cool-=dt;else for(const g of SB.gates){const d=(k.x-g.x)*g.nx+(k.y-g.z)*g.nz;if(d>(g.road?0:g.plain?64:SB_GLEN-70)&&(!g.road||(d<26&&Math.abs((k.wy||0)-g.y)<14))&&Math.abs((k.x-g.x)*g.tx+(k.y-g.z)*g.tz)<g.hw+2&&Math.cos(k.ma)*g.nx+Math.sin(k.ma)*g.nz>.2){sbTravel(g);return;}}
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
function sbRender(time){{const dt=Math.min(.1,Math.max(0,time-(SB.wT==null?time:SB.wT)));SB.wT=time;sbWarpTick(dt);}if(!SB.grp)return;sbCam();if(SB.flag){SB.flag.F.rotation.y=time*1.6;SB.flag.F.position.y=12+Math.sin(time*2.2)*1.2;}const im=SB.im;for(const c of SB.coins){const a=time*2.6+c.ph;if(c.rare){if(c.m&&c.m.visible){c.m.rotation.y=a;c.m.position.y=c.y+Math.sin(time*2+c.ph)*.8;}continue;}
    _sbE.set(0,a,0);_sbQ.setFromEuler(_sbE);_sbP.set(c.x,c.y,c.z);const s=c.t>0?0:1;_sbS.set(s,s,s);_sbM.compose(_sbP,_sbQ,_sbS);im.setMatrixAt(c.i,_sbM);}
  if(im)im.instanceMatrix.needsUpdate=true;}
function sbHud(){let e=SB.el;if(!e){e=SB.el=document.createElement('div');e.id='sbHud';e.style.cssText='position:absolute;left:max(10px,env(safe-area-inset-left));top:64px;z-index:6;font:700 13px/1.3 system-ui,sans-serif;color:#fff4dc;background:rgba(18,9,6,.62);border-radius:12px;padding:8px 12px;pointer-events:none;text-shadow:0 1px 2px #000';stage.appendChild(e);}
  e.hidden=!SBX||state==='menu';if(BB.el)BB.el.hidden=true;if(e.hidden)return;const sv=sbSave(),f=sbFound(),dot=(c,r)=>'<span style="display:inline-block;width:'+r+'px;height:'+r+'px;border-radius:50%;background:'+c+';box-shadow:inset 0 0 0 2px rgba(0,0,0,.25);vertical-align:-2px;margin-right:6px"></span>';
  e.innerHTML='<div style="font-size:11px;letter-spacing:.6px;opacity:.85;text-transform:uppercase">'+SB.reg.name+'</div><div style="font-size:20px;margin-top:2px">'+dot('#ffc93a',15)+sv.c+'</div><div style="margin-top:2px">'+dot('#d8402a',13)+f[0]+' / '+f[1]+'</div>';}
/* what an item box gives here: only the boost (nobody to throw anything at) */
function sbRoll(){return 'chili';}
/* ================= SANDBOX: the world map and fast travel (web v193) =================
   The owner's brief, section 3 (docs/NEXT-MODES-BRIEF.md), and "dont forget to add a map with fast travel in the pause menu and on controller
   make the y button open the map". Opened while driving with Y or Select / View / Back / Minus on a controller, or M on a keyboard (again, or
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
addEventListener('keydown',ev=>{if(SBM.open&&(ev.code==='Escape'||ev.code==='KeyM')){ev.preventDefault();ev.stopImmediatePropagation();if(SBM.pick&&ev.code==='Escape')sbMapPick(null);else sbMap(false);}else if(!SBM.open&&SBX&&state==='race'&&ev.code==='KeyM'&&!ev.repeat&&!KEYC.KeyM){ev.preventDefault();sbMap(true,'drive');}},true);
function sbMapPick(p){SBM.pick=p;SBM.zoom=p?p.id:null;const e=sbMapEl(),say=e.querySelector('#sbMapSay'),go=e.querySelector('#sbMapGo'),no=e.querySelector('#sbMapNo');
  const me=e.querySelector('#sbMapMe');
  if(p){const R=sbRegOf(p.id),here=SBX&&p.id===SB.regId,n=sbMapGates(p.id).length;say.textContent=p.track+(R?' · '+R.name.split(' · ')[0]:'')+(here?' · you are here (the blue arrow)':'')+(n?' · the purple rings are its tunnels':' · its tunnels show once you have been there');go.hidden=false;no.hidden=false;no.textContent='World map';me.hidden=here;go.textContent=here?'To the start line':'Travel here';go.focus();}
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
  for(const q of SBM.pins){const x=X(q.at[0])/dpr,y=Y(q.at[1])/dpr;q.b.style.left=x+'px';q.b.style.top=y+'px';q.b.hidden=!!Z&&q.id!==Z;}}
function sbMapGate(id,gid){const R=SB_REG[id],W=SB_WORLD[id];if(!R||!W)return null;const d=(R.gates||[]).find(q=>q.id===gid);if(!d)return null;const b=W.box;if(R.room){const y=(b[2]+b[3])/2+d.p/100,x=(b[0]+b[1])/2+d.p/100;return d.w==='E'?[b[1],y]:d.w==='W'?[b[0],y]:d.w==='N'?[x,b[3]]:[x,b[2]];}return d.w==='S'?[d.p,b[2]]:d.w==='N'?[d.p,b[3]]:d.w==='E'?[b[1],d.p]:[b[0],d.p];}
function sbMapPins(){const box=sbMapEl().querySelector('#sbMapIn');for(const q of SBM.pins)q.b.remove();SBM.pins=[];
  for(const id of Object.keys(SB_WORLD).concat(Object.keys(SB_SPOT))){const t=sbMapTrack(id);if(!t)continue;const b=document.createElement('button');b.type='button';b.className='sbpin';b.setAttribute('aria-label','Travel to '+t.name);
    b.style.cssText='position:absolute;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:3px solid #ffd45a;padding:0;cursor:pointer;background:conic-gradient(#141210 25%,#fbf6ea 0 50%,#141210 0 75%,#fbf6ea 0) 0 0/12px 12px;box-shadow:0 2px 6px rgba(0,0,0,.6)';
    b.innerHTML='<span style="position:absolute;left:50%;'+(id==='backyard'?'bottom:100%;margin-bottom:3px;':'top:100%;margin-top:3px;')+'transform:translateX(-50%);font:800 10.5px/1 system-ui,sans-serif;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000,0 0 6px #000;pointer-events:none">'+t.name+'</span>';
    b.onclick=()=>sbMapPick(SBM.zoom===id?null:{id,track:t.name});b.addEventListener('focus',()=>{try{b.scrollIntoView({block:'nearest',inline:'nearest'});}catch(e){}});box.appendChild(b);SBM.pins.push({id,b,at:t.start,name:t.name});}
  if(!document.getElementById('sbPinCss')){const st=document.createElement('style');st.id='sbPinCss';st.textContent='.sbpin:focus-visible,.sbpin[aria-pressed=true]{outline:3px solid #39d0ff;outline-offset:3px}';document.head.appendChild(st);}}
/* open or close. from: 'drive' (straight from driving: closing goes back to driving) or 'pause' (from the pause menu: closing goes back to it) */
function sbMap(open,from){const e=sbMapEl();if(open===SBM.open)return;if(open){if(!SBX||SB.trav||(state!=='race'&&state!=='paused'))return;SBM.from=from||'drive';
    if(state==='race')togglePause();/* the game stops under the map, exactly as under the pause menu */pauseOv.hidden=true;SBM.open=true;e.hidden=false;sbMapPins();sbMapPick(null);
    e.querySelector('#sbMapWhere').textContent=SB.reg?SB.reg.name:'';e.querySelector('#sbMapKey').textContent=(SBM.big?'Drag the map to see more \u00b7 ':'')+(PAD.act?'Y or Select: close':(typeof COARSE!=='undefined'&&COARSE)?'':'M: close');
    /* the window opens on where you are */{const box=e.querySelector('#sbMapBox');if(SBM.me){box.scrollLeft=Math.max(0,SBM.me[0]-box.clientWidth/2);box.scrollTop=Math.max(0,SBM.me[1]-box.clientHeight/2);}}
    const first=SBM.pins.find(q=>q.id===SB.regId)||SBM.pins[0];if(first)try{first.b.focus({preventScroll:true});}catch(err){first.b.focus();}}
  else{SBM.open=false;e.hidden=true;SBM.pick=null;SBM.zoom=null;if(SBM.from==='pause'){pauseOv.hidden=false;const r=document.getElementById('resumeBtn');if(r)r.focus();}else if(state==='paused')togglePause();}}
/* fast travel: to a place's start line. Only this player moves. */
function sbMapTravel(id){if(!sbRegOf(id))return;SBM.from='drive';sbMap(false);if(state!=='race')return;sbPark(false);sbTravel({to:id,start:true});}
/* the pause menu's Map button, directly under Resume, in Sandbox only */
function sbMapBtn(){let b=document.getElementById('sbMapBtn');if(!b){if(!SBX)return;const r=document.getElementById('resumeBtn');if(!r)return;b=document.createElement('button');b.id='sbMapBtn';b.className='cta';b.type='button';b.textContent='Map';b.style.cssText='background:var(--oven-2);box-shadow:0 5px 0 rgba(0,0,0,.35);border:2px solid var(--oven-3)';r.insertAdjacentElement('afterend',b);b.onclick=()=>sbMap(true,'pause');}
  b.hidden=!SBX;}
