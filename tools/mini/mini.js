/* ================= MINIATURE MAYHEM CUP: toy racing sets built round real rooms =================
   Scale: a kart is a toy car 7.5 cm long, so 1 cm is TU units and every piece of furniture is its real size.
   The track is half the usual width (def.rw): thin orange plastic with raised edges, in pieces that clip together,
   held up by blue plastic piers. Layout data comes from /home/claude/mini (same fields as the Neon Cup's tracks). */
const TU=3.47;const tcm=v=>v*TU;
/* the furniture a track can stand on: boxes in room coordinates [x0,x1,z0,z1,top] */
let TOYF=[],TOYP=[],TOYB=[],TOYENV=null;/* TOYENV: where the room is photographed from for its reflections [x,height,z] *//* TOYP: places where a pier must stand (on a stack of books, say) */
function toyUnder(x,z,below){let h=0;for(const b of TOYF)if(x>=b[0]&&x<=b[1]&&z>=b[2]&&z<=b[3]&&b[4]<=below+.5&&b[4]>h)h=b[4];return h;}
/* The set comes in coloured sections, the way toy track does. TOYSEC lists them per room as [from,to,colour] in fractions of
   the lap (the lap as it is laid out, whichever way it is raced); everything else is orange. Looks only: the race never reads it. */
const TOYCOL={orange:'#ff6a12',red:'#e3271d',yellow:'#f6c41f',blue:'#1f55c8'},TOYSEC={bedroom:[[.073,.253,'red'],[.347,.514,'yellow'],[.783,.938,'blue']]};
function toyColAt(def,j){j=((j%N)+N)%N;const f=(curRev?(N-j)%N:j)/N;for(const q of TOYSEC[def.look]||[])if(f>=q[0]&&f<q[1])return q[2];return 'orange';}
/* runs of one colour between two points of the lap: [[from,to,colour],...] */
function toyRuns(def,j0,j1){const out=[];let a=j0,k=toyColAt(def,j0);for(let j=j0+1;j<=j1;j++){const c=j<j1?toyColAt(def,j):null;if(c!==k){out.push([a,j,k]);a=j;k=c;}}return out;}
function toyPlasticTex(key){const c=cnv(256,512),g=c.getContext('2d');g.fillStyle=TOYCOL[key||'orange'];g.fillRect(0,0,256,512);
  /* one smooth piece of plastic: the only line is the joint where two pieces clip together (the white dashes are on the walls: toyRails) */
  g.fillStyle='rgba(0,0,0,.4)';g.fillRect(0,0,256,3);g.fillStyle='rgba(255,255,255,.28)';g.fillRect(0,3,256,2);
  for(let i=0;i<500;i++){g.fillStyle='rgba('+(Math.random()<.5?'255,255,255':'0,0,0')+','+(Math.random()*.04)+')';g.fillRect(Math.random()*256,Math.random()*512,1+Math.random()*3,1);}return c;}
const TOYW=()=>WALLD+4,TOYOR=key=>!key||key==='orange'?TM.mat('toyorange',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#ff6a12',roughness:.34,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide}))):TM.mat('toyplastic_'+key,()=>toySmooth(new THREE.MeshPhysicalMaterial({color:TOYCOL[key],roughness:.34,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide}))),TOYBL=()=>TM.mat('toyblue',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#1769d6',roughness:.35,clearcoat:.5,clearcoatRoughness:.25})));
/* moulded plastic is smooth: it takes none of the fine surface speckle Ultra gives plain materials */
function toySmooth(m){m.userData.noHQ=true;return m;}
/* the track is glossy plastic that mirrors the room it stands in (the room's own reflections, toyRoomEnv, never an outdoor sky) */
function toyRoadMat(key){key=key||'orange';return TM.mat('toyroad_'+key,()=>toySmooth(new THREE.MeshPhysicalMaterial({map:T2(toyPlasticTex(key),1,1),roughness:.34,metalness:0,clearcoat:1,clearcoatRoughness:.07,envMapIntensity:1,side:THREE.DoubleSide})));}
function toyRoad(def,SJ0,SJ1){for(const q of toyRuns(def,SJ0,SJ1)){const r=strip(q[0],q[1],-TOYW(),TOYW(),.06,toyRoadMat(q[2]),120,true);if(r)r.receiveShadow=true;}}
/* one length of raised edge between two cross-sections: an inner face, a flat top and an outer face */
function toyRailQuad(pos,A,B,s){const quad=(a,b,c,d)=>pos.push(...a,...b,...c,...a,...c,...d);
  if(s>0){quad(A[0],B[0],B[1],A[1]);quad(A[1],B[1],B[2],A[2]);quad(A[2],B[2],B[3],A[3]);}else{quad(A[0],A[1],B[1],B[0]);quad(A[1],A[2],B[2],B[1]);quad(A[2],A[3],B[3],B[2]);}}
function toyRailMesh(pos,key){if(!pos.length)return;const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.computeVertexNormals();const rm=new THREE.Mesh(g,TOYOR(key));rm.castShadow=true;rm.receiveShadow=true;rm.userData.noLift=true;rm.userData.noMerge=true;/* kept out of the merged scenery, which would swap its glossy plastic for a plain batch material */world.add(rm);}
/* the raised edges of the main track, left open where a shortcut leaves or joins and where the loop takes over */
function toyRails(def){const W=TOYW(),by={},dash=[],sp=T.L/N,H=4.2,TH=3,P=j=>track[((j%N)+N)%N],at=(p,o,h)=>{const x=p.x+p.nx*o,z=p.y+p.ny*o;return [x,(p.ey||0)+h,z];},sec=(p,s)=>[at(p,W*s,0),at(p,W*s,H),at(p,(W+TH)*s,H),at(p,(W+TH)*s,-1.6)];
  for(const s of [-1,1])for(let j=0;j<N;j++){const p=P(j),q=P(j+1);if(p.cut)continue;const k=toyColAt(def,j),pos=by[k]||(by[k]=[]),open=(p.ey||0)<=2&&SHORTS.length&&(toyOffShort(p.x+p.nx*W*s,p.y+p.ny*W*s)<3||toyOffShort(q.x+q.nx*W*s,q.y+q.ny*W*s)<3);
    /* a white dash on the wall every 120 units, 36 long: along its top and down its inner face */
    if(!open&&(j*sp)%120<36){const q4=(a,b,c,d)=>dash.push(...a,...b,...c,...a,...c,...d);q4(at(p,(W+.4)*s,H+.05),at(p,(W+TH-.4)*s,H+.05),at(q,(W+TH-.4)*s,H+.05),at(q,(W+.4)*s,H+.05));q4(at(p,(W-.05)*s,1),at(p,(W-.05)*s,3.5),at(q,(W-.05)*s,3.5),at(q,(W-.05)*s,1));}
    if((p.ey||0)>2||!SHORTS.length){toyRailQuad(pos,sec(p,s),sec(q,s),s);continue;}toyRailClip(pos,sec(p,s),sec(q,s),s,toyOffShort);}
  for(const k in by)toyRailMesh(by[k],k);
  if(dash.length){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(dash,3));g.computeVertexNormals();
    const dm=new THREE.Mesh(g,TM.mat('toydash',()=>toySmooth(new THREE.MeshPhysicalMaterial({color:'#f6f5f0',roughness:.4,clearcoat:.6,clearcoatRoughness:.2,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}))));
    dm.receiveShadow=true;dm.userData.noLift=true;dm.userData.noMerge=true;world.add(dm);}}
/* raised track: the thin underside of the plastic and blue piers down to whatever is underneath (the floor, a desk, a stack of books) */
function toyDecks(def){const W=TOYW()+3,inGl=j=>GLIDE&&j>=GLIDE.j0&&j<GLIDE.j1,P=j=>track[((j%N)+N)%N],unds={};
  for(let j=0;j<N;j++){const p=P(j),q=P(j+1);if(inGl(j)||inGl(j+1))continue;const pe=p.ey||0,qe=q.ey||0;if(pe<1.5&&qe<1.5)continue;const c=(t,o,h)=>[t.x+t.nx*o,h,t.y+t.ny*o],kc=toyColAt(def,j),und=unds[kc]||(unds[kc]=[]);
    und.push(...c(p,-W,pe-1.6),...c(q,W,qe-1.6),...c(q,-W,qe-1.6),...c(p,-W,pe-1.6),...c(p,W,pe-1.6),...c(q,W,qe-1.6));}
  const mk=(arr,mat,cast)=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(arr,3));g.computeVertexNormals();const m=new THREE.Mesh(g,mat);m.userData.noLift=true;m.castShadow=!!cast;m.receiveShadow=true;world.add(m);return m;};
  for(const kc in unds)mk(unds[kc],toySmooth(new THREE.MeshStandardMaterial({color:new THREE.Color(TOYCOL[kc]).multiplyScalar(.82),roughness:.45,side:THREE.DoubleSide})),true);
  /* piers every 30 cm or so: two tapered posts, a cross beam under the track, tie bars on the tall ones and round feet; none where another road runs underneath */
  const post=[],beam=[],foot=[],tie=[],arm=[];let last=-99;
  for(let j=0;j<N;j++){const p=P(j),e=p.ey||0,force=TOYP.some(q=>(q[0]-p.x)**2+(q[1]-p.y)**2<20);if(e<7||inGl(j)||(j-last<13&&!force))continue;const base=toyUnder(p.x,p.y,e-2);if(e-base<6)continue;let blocked=false;
    for(let i=0;i<N;i+=2){let di=Math.abs(i-j)%N;di=Math.min(di,N-di);if(di<16)continue;const q=track[i],qe=q.ey||0;if(qe>=e-8)continue;if((q.x-p.x)**2+(q.y-p.y)**2<(2*W+10)**2){blocked=true;break;}}
    if(blocked){/* a spiral stands over itself: one post outside the curve, clear of every level, with an arm under the track */
      const q=P(j+4),cr=p.tx*q.ty-p.ty*q.tx;if(Math.abs(cr)<.05||j-last<9)continue;const sd=cr>0?-1:1,ox=p.x+p.nx*(W+7)*sd,oz=p.y+p.ny*(W+7)*sd;let clear=true;
      for(let i=0;i<N;i+=2){const t=track[i];if((t.ey||0)<e-6&&(t.x-ox)**2+(t.y-oz)**2<(W+3)**2){clear=false;break;}}if(!clear)continue;
      last=j;const b2=toyUnder(ox,oz,e-2),hh=e-1-b2;post.push({x:ox,y:b2+hh/2,z:oz,sy:hh,ry:-p.ang});foot.push({x:ox,y:b2+1,z:oz,ry:-p.ang});arm.push({x:p.x+p.nx*(W-6)*sd,y:e-3.4,z:p.y+p.ny*(W-6)*sd,ry:-p.ang});continue;}
    last=j;beam.push({x:p.x,y:e-3.4,z:p.y,ry:-p.ang});
    /* a pier that rests on something (a stack of books) keeps its posts close in, so both stand on it */const po=force?20:W-7;for(const sd of [-1,1]){const x=p.x+p.nx*po*sd,z=p.y+p.ny*po*sd,b2=toyUnder(x,z,e-2),hh=e-5-b2;if(hh<2)continue;post.push({x,y:b2+hh/2,z,sy:hh,ry:-p.ang});foot.push({x,y:b2+1,z,ry:-p.ang});}
    const h=e-5-base;for(let y=base+34;y<e-24&&h>60;y+=42)tie.push({x:p.x,y,z:p.y,ry:-p.ang});}
  const blue=TOYBL();instBatch(new THREE.CylinderGeometry(2.6,3.6,1,4,1).rotateY(Math.PI/4),blue,post,true);instBatch(new THREE.BoxGeometry(8,3.4,2*W+4),blue,beam,true);instBatch(new THREE.CylinderGeometry(6,7.5,2,14),blue,foot,true);instBatch(new THREE.BoxGeometry(2.2,2.2,2*W-14),blue,tie,true);instBatch(new THREE.BoxGeometry(7,3.4,30),blue,arm,true);}
/* put a model in the room: design coordinates (x east, y north), y0 its height off the floor, ry its turn */
function toyPut(o,x,y,ry,y0){o.position.set(x,y0||0,-y);o.rotation.y=ry||0;o.userData.noLift=true;o.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false&&!q.material.transparent;q.receiveShadow=true;}});world.add(o);return o;}
/* a soft dark patch on the floor where furniture keeps the light off it (far furniture has no drawn shadow of its own) */
function toyShade(x0,x1,y0,y1,a,h){const c=TM.can('aoshade',64,64,(g,w,hh)=>{const gr=g.createRadialGradient(32,32,6,32,32,32);gr.addColorStop(0,'rgba(0,0,0,1)');gr.addColorStop(.7,'rgba(0,0,0,.75)');gr.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=gr;g.fillRect(0,0,w,hh);}),
  m=TM.mat('aoshade'+a,()=>new THREE.MeshBasicMaterial({map:TM.tex(c,'aoshade'),transparent:true,opacity:a,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1})),p=new THREE.Mesh(new THREE.PlaneGeometry((x1-x0)*1.25,(y1-y0)*1.25),m);
  p.rotation.x=-Math.PI/2;p.position.set((x0+x1)/2,(h||0)+.35,-(y0+y1)/2);p.userData.noLift=true;p.userData.noMerge=true;p.renderOrder=1;world.add(p);}
/* a wall with a rectangular opening: four pieces round the hole. ax 'x' runs along x at z=at, 'z' runs along z at x=at */
function toyWall(ax,at,a0,a1,H,hole,m,face){const T=12*TM.U,mk=(u0,u1,v0,v1)=>{if(u1-u0<1||v1-v0<1)return;const g=TM.uvw(ax==='x'?new THREE.BoxGeometry(u1-u0,v1-v0,T):new THREE.BoxGeometry(T,v1-v0,u1-u0),120),b=new THREE.Mesh(g,m);
    if(ax==='x')b.position.set((u0+u1)/2,(v0+v1)/2,at+face*T/2);else b.position.set(at+face*T/2,(v0+v1)/2,(u0+u1)/2);b.receiveShadow=true;b.castShadow=true;b.userData.noLift=true;world.add(b);};
  if(!hole){mk(a0,a1,0,H);return;}const [h0,h1,y0,y1]=hole;mk(a0,h0,0,H);mk(h1,a1,0,H);mk(h0,h1,0,y0);mk(h0,h1,y1,H);}
/* ---- Bedroom Blitz: a teenager's bedroom, 4.0 x 4.8 m ---- */
function toyBedroom(def){const U=TM.U,X=695,Y=833,H=868,M=TM;
  /* light: a low afternoon sun that reaches the room only through the window (sunBeam, below): warm, hard-edged patches on the desk
     and across the middle of the floor; the rest of the room is in cooler shade, lit by the sky and by what the floor throws back up */
  renderer.toneMappingExposure=.98;hemi.color.set('#cfdcf0');hemi.groundColor.set('#b3937a');hemi.intensity=.54;sun.color.set('#ffdcaa');sun.intensity=2.7;sunDir.set(-.1,.56,-.82).normalize();rimL.intensity=.16;rimL.color.set('#cfe0ff');
  scene.fog=new THREE.Fog('#d8cfc0',6000,30000);scene.background=new THREE.Color('#bcd6f2');Object.assign(POST.grade,{sat:1.04,con:1.05,tint:[1.01,1,.985],vig:.16,bloom:.22,thr:.97});
  /* floor: oak boards 12 cm wide running the length of the room */
  /* the oak boards are a texture pair made by tools/blender/oak_tex.py (every board its own length, tone and ring figure; relief for the grain, the bevels and the gaps): one tile is 1.92 m. The drawn wood stays as the stand-in if the pictures are missing */
  const oak=typeof PROP_TEX!=='undefined'&&PROP_TEX.tex_toy_oak&&PROP_TEX.tex_toy_oak_n,fm=oak?M.mat('oakfloor',()=>{const c=propTex('tex_toy_oak'),n=propTex('tex_toy_oak_n',false);for(const t of [c,n])t.wrapS=t.wrapT=THREE.RepeatWrapping;return new THREE.MeshStandardMaterial({map:c,normalMap:n,normalScale:new THREE.Vector2(.9,.9),roughness:.4,metalness:0,envMapIntensity:.75});}):M.wood('floor','#b08556','#4a2f18',{planks:8,knots:1,rough:.46,env:.55,bump:1.4}),fg=new THREE.PlaneGeometry(2*X,2*Y,1,1);fg.rotateX(-Math.PI/2);M.uvw(fg,oak?192:96,true);const fl=new THREE.Mesh(fg,fm);fl.position.y=-.1;fl.receiveShadow=true;fl.userData.noLift=true;world.add(fl);
  /* walls (the window in the north wall, the door in the south wall), ceiling, skirting boards */
  /* painted walls: smooth, with the fine stipple a roller leaves (2 mm) instead of the cloudy mottling Ultra gives plain materials, which read as noise on a big flat wall. The names stay toy_pt_wall*, which the PC looks for */
  const stip=T2(heightToNormal(M.can('stipple',256,256,(g,w,h,r)=>{for(let y=0;y<h;y+=2)for(let x=0;x<w;x+=2){const v=112+r()*32;g.fillStyle='rgb('+v+','+v+','+v+')';g.fillRect(x,y,2,2);}}),1.1),7,7,true),
    wallM=(key,col)=>M.mat('pt_'+key,()=>{const m=new THREE.MeshStandardMaterial({color:col,roughness:.9,metalness:0,envMapIntensity:.4,normalMap:stip,normalScale:new THREE.Vector2(.35,.35)});m.userData.noHQ=true;return m;}),
    wall=wallM('wall','#e9e3d8'),wall2=wallM('wall2','#93a8a6'),win=[-370,150,330,764],dr=[-300,-14,0,712];
  sunBeam([[win[0],win[1],win[2],win[3],-Y-12*U,-Y]],win[3]/sunDir.y+160);
  toyWall('x',-Y,-X,X,H,[win[0],win[1],win[2],win[3]],wall,-1);toyWall('x',Y,-X,X,H,[dr[0],dr[1],dr[2],dr[3]],wall,1);toyWall('z',-X,-Y,Y,H,null,wall,-1);toyWall('z',X,-Y,Y,H,null,wall2,1);
  const cg=new THREE.PlaneGeometry(2*X,2*Y);cg.rotateX(Math.PI/2);const ce=new THREE.Mesh(cg,wallM('ceiling','#f4f1ea'));ce.position.y=H;ce.userData.noLift=true;world.add(ce);
  const sk=M.paint('skirting','#f6f4ee',.5),sb=(x0,x1,z0,z1)=>{const b=new THREE.Mesh(M.slab(Math.abs(x1-x0)||1.6*U,10*U,Math.abs(z1-z0)||1.6*U,.3*U,.3*U,2),sk);b.position.set((x0+x1)/2,5*U,(z0+z1)/2);b.userData.noLift=true;b.receiveShadow=true;world.add(b);};
  sb(-X,X,-Y+.8*U,-Y+.8*U);sb(-X,dr[0]-9*U,Y-.8*U,Y-.8*U);sb(dr[1]+9*U,X,Y-.8*U,Y-.8*U);sb(-X+.8*U,-X+.8*U,-Y,Y);sb(X-.8*U,X-.8*U,-Y,Y);
  /* the window, the view outside, curtains on a rod */
  const wcx=(win[0]+win[1])/2,wW=(win[1]-win[0])/U,wH=(win[3]-win[2])/U;toyPut(M.window(wW,wH),wcx,Y+4*U,0,win[2]);const out=M.outside(wW*2.6,wH*2.2);out.position.set(wcx,win[2]+wH*U*.55,-Y-60*U);out.userData.noLift=true;out.userData.envGain=6;/* the sky outside is far brighter than the room: in the room's reflections the window is a light */world.add(out);TOYENV=[-120,220,200];
  for(const s of [-1,1])toyPut(M.curtain(58,wH+34,{seed:s+3}),wcx+s*(wW*U/2+8*U),Y-5*U,0,win[3]+22*U).traverse(q=>{if(q.isMesh){q.userData.sunlit=true;q.receiveShadow=false;}});/* the folds reach from 2 to 16 cm off the wall. The curtains are lit from behind at a grazing angle, where the sun's shadow map breaks up into jagged patches on the folds: they throw shadows but are not tested against them */const rod=new THREE.Mesh(M.cyl(1.1*U,1.1*U,(wW+90)*U,12),M.metal('rod','#2a2c31',.4));rod.rotation.z=Math.PI/2;rod.position.set(wcx,win[3]+24*U,-Y+7*U);rod.userData.noLift=true;world.add(rod);
  toyPut(M.door(),(dr[0]+dr[1])/2,-Y+1*U,Math.PI,0);
  /* a ceiling light */
  {const g=new THREE.Group();M.add(g,M.cyl(17*U,17*U,2*U,32),M.paint('ceilrose','#f1eee6',.6),0,-1*U,0);M.add(g,new THREE.SphereGeometry(15*U,28,12,0,6.283,Math.PI/2,Math.PI/2),M.mat('ceilglass',()=>new THREE.MeshStandardMaterial({color:'#fffaf0',emissive:'#fff1d6',emissiveIntensity:.35,roughness:.4})),0,-2*U,0);toyPut(g,0,0,0,H);}
  /* ---- furniture ---- */
  const deskTop=260;toyPut(M.desk({w:200,d:80,h:75}),-123,694,0);TOYF.push([-470,224,-833,-555,deskTop]);
  toyPut(M.deskmat(),-110,738,0,deskTop);toyPut(M.monitor({screen:'game'}),-110,792,0,deskTop+.4*U);/* far enough from the wall that its angled screen clears the curtain */toyPut(M.monitor({arm:true,screen:'desk'}),-338,728,.42,deskTop);toyPut(M.keyboard(),-118,712,0,deskTop+.4*U);toyPut(M.mouse(),-22,706,.1,deskTop+.4*U);
  toyPut(M.pc(),150,733,Math.PI/2*0,deskTop);toyPut(M.mug({color:'#2f5d8a'}),-262,712,.6,deskTop);toyPut(M.sodacan(),30,776,0,deskTop);toyPut(M.books(4,5),-428,770,.3,deskTop);toyPut(M.plant({seed:4}),-452,792,0,deskTop).scale.setScalar(.5);
  /* the chair is pushed back to one side, clear of the sunlight that falls across the floor */toyPut(M.chair({turn:-.5}),-345,372,Math.PI+.35);toyPut(M.floorlamp(),460,455,0);
  /* the bed stands clear of the east wall and of the wall behind its headboard (it used to reach into both); its legs are at the frame's corners, just outside the track that runs underneath */
  toyPut(M.bed(),412,-460,Math.PI);toyPut(M.nightstand(),50,-760,Math.PI);toyPut(M.mug(),32,-756,2,52*U);toyPut(M.books(2,9),66,-764,.2,52*U);
  toyPut(M.dresser(),-617,268,Math.PI/2);TOYF.push([-695,-539,-476,-60,156]);
  /* the start of the climb rests on a stack of books */
  /* placed from the track's real height (not a straight-line guess, which put the top book through the road): the lowest point of the
     climb that clears the stack, then far enough up the slope that the whole stack is under the track */
  {const st=M.books(4,21),top=st.userData.top,T0=j=>track[((j%N)+N)%N];let jb=-1,eb=1e9;for(let j=0;j<N;j++){const q=track[j],e=q.ey||0;if(q.x<-560&&e>=top+5&&e<eb){eb=e;jb=j;}}
    if(jb>=0){const up=(T0(jb+1).ey||0)>eb?1:-1;let k=jb,dd=0;while(dd<48){const a=T0(k),b=T0(k+up);dd+=Math.hypot(b.x-a.x,b.y-a.y);k+=up;}const q=T0(k);toyPut(st,q.x,-q.y,Math.PI/2);TOYF.push([q.x-34,q.x+34,q.y-24,q.y+24,top]);TOYP.push([q.x,q.y]);}}
  toyPut(M.rug({w:110,l:150}),-60,-380,0);
  /* sneakers kicked off by the track */
  toyPut(M.sneaker(),-400,150,.3);toyPut(M.sneaker(),-330,168,.6);toyPut(M.sneaker({color:'#2a2c31',accent:'#39d98a'}),-520,-290,-1.5);toyPut(M.sneaker({color:'#2a2c31',accent:'#39d98a'}),-518,-365,-1.7);
  toyPut(M.bin(),300,770,0);toyPut(M.carton(42,32,22),250,-770,.1);toyPut(M.carton(30,24,18),630,-780,-.2);toyPut(M.plant({seed:15}),-345,-790,0);
  /* the small things left lying about: they show how small the karts are */
  toyPut(M.skateboard(),-60,-470,.5,4.2);toyPut(M.ball(),-300,-560,0);toyPut(M.ball({kind:'tennis'}),-330,470,0);toyPut(M.cube({seed:5}),214,-196,.6);toyPut(M.bricks({seed:3,n:10,spread:8}),-200,236,0);toyPut(M.bricks({seed:8,n:7,spread:7}),-646,-792,0);
  toyPut(M.pencils({seed:2,n:3}),-300,300,0);toyPut(M.pencils({seed:6,n:2,spread:10}),150,330,0);toyPut(M.backpack(),96,-604,-1.2);toyPut(M.controller(),-292,728,.4,deskTop);toyPut(M.cube({seed:9}),196,706,.3,deskTop);
  toyPut(M.setbox(),-130,-722,.15);toyPut(M.trackpiece(),-150,-722,.9,38.4);toyPut(M.trackpiece({l:22}),-248,-664,-.4);
  toyPut(M.poster(50,70,0),-689,268,Math.PI/2,430);toyPut(M.poster(42,60,1),689,-250,-Math.PI/2,500);toyPut(M.poster(42,60,2),689,-430,-Math.PI/2,470);toyPut(M.shelf(),689,250,-Math.PI/2,520);
  /* where furniture keeps the light off the floor */
  toyShade(139,685,-826,-126,.5);toyShade(-470,224,555,833,.34);toyShade(-695,-539,60,476,.3);toyShade(-415,-275,302,442,.22);toyShade(-28,127,-833,-690,.3);}
/* ---- the pieces of the racing set ---- */
/* the loop: the same full loop the other cups have, scaled to the toy track. The road swings left into it and comes out on the right */
function toyLoops(def){LOOP_DH=5;for(const q of def.tloops||[]){const j=nfj(q[0]),p=track[j];LOOPS.push({j,p:{x:p.x,y:p.y,tx:p.tx,ty:p.ty,nx:p.nx,ny:p.ny,ang:p.ang},g0:groundAt(p.x,p.y)+(p.ey||0),W:WALLD,S:54,lat0:-54,shift:108,full:true,sc:q[1]||LS});}
  LOOPS.sort((a,b)=>a.j-b.j);LOOP=LOOPS[0]||null;for(const L of LOOPS)shiftForLoop(L);if(LOOPS.length){LOOP_TAP=30;LOOP_DIV=60;buildGrid();}}
function toyLoop(L,def){const p=L.p,g0=L.g0,SEG=96,LEAD=3,W=TOYW(),TH=3,H=4.2,pos=[],uv=[],idx=[],rails=[],secs=[[],[]];
  for(let i=-LEAD;i<=SEG;i++){const th=i<0?0:i/SEG*Math.PI*2,al=i<0?i*3.4:LOOPR*Math.sin(th),hg=LOOPR*(1-Math.cos(th)),lat=L.lat0+L.shift*Math.max(0,i)/SEG,nt=-Math.sin(th),nu=Math.cos(th),arc=i<0?i*3.4:LOOPR*th;
    const at=(l,up)=>[p.x+p.tx*(al+nt*up)+p.nx*l,g0+hg+.3+nu*up,p.y+p.ty*(al+nt*up)+p.ny*l];
    for(const sd of [-1,1]){pos.push(...at(lat+sd*W,0));uv.push(sd<0?0:1,arc/120);secs[sd<0?0:1].push([at(lat+sd*W,0),at(lat+sd*W,H),at(lat+sd*(W+TH),H),at(lat+sd*(W+TH),-1.6)]);}
    if(i<SEG){const a=(i+LEAD)*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const lg=new THREE.BufferGeometry();lg.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));lg.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));lg.setIndex(idx);lg.computeVertexNormals();
  const lm=new THREE.Mesh(lg,toyRoadMat());lm.castShadow=lm.receiveShadow=true;lm.userData.noLift=true;world.add(lm);
  for(const k of [0,1])for(let i=0;i<secs[k].length-1;i++)toyRailQuad(rails,secs[k][i],secs[k][i+1],k?1:-1);toyRailMesh(rails);
  /* the frame: a blue arch over the top of the loop that the track clips into, on wide feet, and a spine along the floor between the way in and the way out */
  const G=new THREE.Group();G.position.set(p.x,g0,p.y);G.rotation.y=-p.ang;G.userData.noLift=true;world.add(G);const bl=TOYBL(),top=2*LOOPR,o=L.S+W+TH+9,M=TM;
  for(const sd of [-1,1]){M.add(G,new THREE.CylinderGeometry(4.6,7.4,top+10,4,1).rotateY(Math.PI/4),bl,0,(top+10)/2,sd*o);M.add(G,M.slab(46,3,20,5,1,2),bl,0,1.5,sd*o);
    for(const a of [-1,1])M.add(G,new THREE.BoxGeometry(3,top*.62,3).rotateZ(a*.36),bl,a*13.5,top*.3,sd*o);}
  M.add(G,M.slab(11,9,2*o+12,2,1.4,2),bl,0,top+7.2,0);M.add(G,M.slab(200,3,8,3,1,2),bl,0,1.5,0);
  for(const sd of [-1,1])M.add(G,M.slab(18,3.4,7,1.5,.6,1),bl,0,top+1.2,sd*(W+TH+2.5));
  const sc=TM.can('loopsign',512,128,(g,w,h)=>{g.fillStyle='#f6c21c';g.fillRect(0,0,w,h);g.fillStyle='#1b1b1e';g.fillRect(0,0,w,10);g.fillRect(0,h-10,w,10);g.font='900 84px Arial Black,Impact,sans-serif';g.textAlign='center';g.fillStyle='#d42a20';g.fillText('TURBO LOOP',w/2,94);}),
    sm=TM.mat('loopsign',()=>new THREE.MeshStandardMaterial({map:TM.tex(sc,'loopsign'),roughness:.4}));
  for(const sd of [-1,1]){const pl=M.add(G,new THREE.PlaneGeometry(64,16),sm,sd*5.7,top+16,0,0,sd*Math.PI/2);pl.userData.cast=false;}M.add(G,M.slab(10,17,66,1.5,.6,1),bl,0,top+16,0);
  G.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false;q.receiveShadow=true;}});
  obstacles.push({x:p.x-p.nx*o,y:p.y-p.ny*o,r:6,h:top,j:L.j,lat:999},{x:p.x+p.nx*o,y:p.y+p.ny*o,r:6,h:top,j:L.j,lat:999});}
/* the start gate: two blue posts and a chequered banner, the size a toy set would have */
function toyGate(def){const s=track[0],G=new THREE.Group(),bl=TOYBL(),M=TM,o=TOYW()+9,Y=(s.ey||0);G.position.set(s.x,Y,s.y);G.rotation.y=-s.ang;G.userData.noLift=true;world.add(G);
  for(const sd of [-1,1]){M.add(G,new THREE.CylinderGeometry(2.6,3.4,40,4,1).rotateY(Math.PI/4),bl,0,20,sd*o);M.add(G,M.slab(13,2.4,13,3,.6,2),bl,0,1.2,sd*o);}
  const bt=T2(bannerC);bt.userData.keepCanvas=true;const bm=new THREE.MeshStandardMaterial({map:bt,roughness:.5}),b=new THREE.Mesh(new THREE.BoxGeometry(2,12.5,2*o+7),[bm,bm,bl,bl,bl,bl]);b.position.set(0,35,0);G.add(b);
  M.add(G,M.slab(4,3,2*o+12,1.4,.5,1),bl,0,42.4,0);G.traverse(q=>{if(q.isMesh){q.castShadow=true;q.receiveShadow=true;}});
  if(document.fonts)document.fonts.ready.then(()=>{drawBanner();bt.needsUpdate=true;});}
/* boosters: a strip of arrows across the whole track between two motor housings, the way a toy set fires its cars on */
function toyPadTex(){return TM.can('toypad',256,256,(g,w,h)=>{g.fillStyle='#1b1b1e';g.fillRect(0,0,w,h);g.strokeStyle='#f6c21c';g.lineWidth=26;g.lineJoin='miter';for(let y=-60;y<340;y+=86){g.beginPath();g.moveTo(-10,y+70);g.lineTo(128,y);g.lineTo(266,y+70);g.stroke();}});}
function toyBooster(j,gate){const p=track[((j%N)+N)%N],G=new THREE.Group(),M=TM,bl=TOYBL(),o=TOYW()+3+7.5,Y=(p.ey||0);G.position.set(p.x,Y,p.y);G.rotation.y=-p.ang;G.userData.noLift=true;world.add(G);
  const gy=M.plastic('toygrey','#d9dce2',.4),bk=M.plastic('toyrubber','#16171a',.8),bolt=TM.can('bolt',64,128,(g,w,h)=>{g.fillStyle='#f6c21c';g.fillRect(0,0,w,h);g.fillStyle='#d42a20';g.beginPath();g.moveTo(38,6);g.lineTo(12,70);g.lineTo(30,70);g.lineTo(22,122);g.lineTo(54,52);g.lineTo(36,52);g.closePath();g.fill();}),bm=TM.mat('bolt',()=>new THREE.MeshStandardMaterial({map:TM.tex(bolt,'bolt'),roughness:.4}));
  for(const sd of [-1,1]){if(toyOffShort(p.x+p.nx*sd*o,p.y+p.ny*sd*o)<40)continue;M.add(G,M.slab(40,14,15,3,1.6,2),bl,0,7-1.6,sd*o);M.add(G,M.slab(26,3,11,2.4,.8,2),gy,0,13.6,sd*o);const st=M.add(G,new THREE.PlaneGeometry(9,18),bm,0,15.2,sd*o,-Math.PI/2,0,Math.PI/2);st.userData.cast=false;
    for(const a of [-9,9])M.add(G,M.cyl(7.2,7.2,5,20),bk,a,5.6,sd*(o-6.2));}
  G.traverse(q=>{if(q.isMesh){q.castShadow=q.userData.cast!==false;q.receiveShadow=true;}});}
function toyPads(def){const m=TM.mat('toypad',()=>new THREE.MeshStandardMaterial({map:T2(toyPadTex(),1,1),roughness:.4,emissive:'#f6c21c',emissiveIntensity:.12,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2}));
  const put1=j=>{pads.push({j,lat:0,w:RW+4});const pm=strip(j-2,j+2,-RW-4,RW+4,.14,m,32);if(pm&&pm.isMesh){pm.userData.noMerge=true;pm.castShadow=false;}TOYB.push(j);};
  (def.npads||[]).forEach(q=>put1(nfj(q[0])));for(const L of LOOPS)if(L.full)put1((L.j-13+N)%N);}
function toyRamps(def){const c=TM.can('toyramp',256,256,(g,w,h)=>{g.fillStyle='#ff6a12';g.fillRect(0,0,w,h);g.fillStyle='#fff4dc';for(let y=-40;y<300;y+=64){g.beginPath();g.moveTo(40,y+52);g.lineTo(128,y);g.lineTo(216,y+52);g.lineTo(216,y+74);g.lineTo(128,y+22);g.lineTo(40,y+74);g.closePath();g.fill();}g.fillStyle='#1769d6';g.fillRect(0,0,14,h);g.fillRect(w-14,0,14,h);}),
    topM=new THREE.MeshPhysicalMaterial({map:T2(c,1,1),roughness:.32,clearcoat:.5,clearcoatRoughness:.3}),sideM=new THREE.MeshPhysicalMaterial({color:'#1769d6',roughness:.35,clearcoat:.4,side:THREE.DoubleSide});
  for(const f of def.nramps||[]){let j=nfj(f);if(curRev)j=(j-4+N)%N;const r={j,len:4*T.L/N,w:RW+2,h:6};ramps.push(r);buildRamp(r,topM,sideM);}}
/* a shortcut is a single lane of the same orange track */
const TOYSW=sc=>(sc.w||SCW)+5;/* a shortcut lane is drawn this much wider than its driving line each side, so karts stay clear of its edges */
/* how far a point is outside the main track's surface (floor level only): negative = on it */
function toyOffMain(x,z){let bd=1e9;for(let j=0;j<N;j++){const t=track[j];if((t.ey||0)>2)continue;const d=(t.x-x)**2+(t.y-z)**2;if(d<bd)bd=d;}return Math.sqrt(bd)-TOYW();}
/* how far a point is outside a shortcut's lane: negative = inside it */
function toyOffShort(x,z){let b=1e9;for(const sc of SHORTS){const P=sc.pts,W=TOYSW(sc);for(let i=0;i<P.length;i++){const p=P[i],al=(x-p.x)*p.tx+(z-p.y)*p.ty;if(Math.abs(al)>6)continue;const o=Math.abs((x-p.x)*p.nx+(z-p.y)*p.ny)-W;if(o<b)b=o;}}return b;}
/* a length of rail between two cross-sections, cut exactly where `off` (measured at the rail's inner foot) crosses zero, so two
   rails that meet at a junction meet without a gap */
function toyRailClip(pos,A,B,s,off){const mix=(P,Q,t)=>P.map((p,i)=>[p[0]+(Q[i][0]-p[0])*t,p[1]+(Q[i][1]-p[1])*t,p[2]+(Q[i][2]-p[2])*t]),fa=off(A[0][0],A[0][2]),fb=off(B[0][0],B[0][2]);
  if(fa<=0&&fb<=0)return;if(fa>0&&fb>0){toyRailQuad(pos,A,B,s);return;}let lo=0,hi=1;for(let i=0;i<12;i++){const t=(lo+hi)/2,M=mix(A,B,t),f=off(M[0][0],M[0][2]);if((f>0)===(fa>0))lo=t;else hi=t;}
  const M=mix(A,B,(lo+hi)/2);if(fa>0)toyRailQuad(pos,A,M,s);else toyRailQuad(pos,M,B,s);}
/* a shortcut is a single lane of the same orange track, walled all the way: its rails run right up to the main track's */
function toyShortcut(sc,def){const SW=TOYSW(sc),P=sc.pts,pos=[],uv=[],idx=[],rails=[];
  for(let i=0;i<P.length;i++){const p=P[i];for(const sd of [-1,1]){pos.push(p.x+p.nx*SW*sd,.16,p.y+p.ny*SW*sd);uv.push(sd<0?.2:.8,i*8/120);}if(i<P.length-1){const a=i*2;idx.push(a,a+1,a+2,a+1,a+3,a+2);}}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();const m=new THREE.Mesh(g,toyRoadMat());m.receiveShadow=true;m.userData.noLift=true;world.add(m);
  const sec=(p,s)=>[[p.x+p.nx*SW*s,.1,p.y+p.ny*SW*s],[p.x+p.nx*SW*s,4.2,p.y+p.ny*SW*s],[p.x+p.nx*(SW+3)*s,4.2,p.y+p.ny*(SW+3)*s],[p.x+p.nx*(SW+3)*s,-.2,p.y+p.ny*(SW+3)*s]];
  for(const s of [-1,1])for(let i=0;i<P.length-1;i++)toyRailClip(rails,sec(P[i],s),sec(P[i+1],s),s,toyOffMain);toyRailMesh(rails);}
/* Room reflections: once the room is built it is photographed from an open spot into a small cube map, which becomes the map's
   environment: the track, the karts and the floor then mirror the window and the walls. Two passes, so the second sees the first
   one's reflections; karts are left out. Done once per load, no cost per frame. */
function toyRoomEnv(){const P=TOYENV;if(P&&world)try{sunShadeAll();const rt=new THREE.WebGLCubeRenderTarget(LOWQF()?128:256,{type:THREE.HalfFloatType}),cc=new THREE.CubeCamera(4,6000,rt);cc.position.set(P[0],P[1],P[2]);scene.add(cc);
    const hid=[],lit=[];for(const k of karts){if(k.m&&k.m.g.visible){k.m.g.visible=false;hid.push(k.m.g);}}
    world.traverse(o=>{if(o.userData.envGain&&o.material&&o.material.color){lit.push(o,o.material.color.clone());o.material.color.multiplyScalar(o.userData.envGain);}});
    try{for(let i=0;i<2;i++){renderer.shadowMap.needsUpdate=true;cc.update(renderer,scene);const pm=new THREE.PMREMGenerator(renderer),e=pm.fromCubemap(rt.texture).texture;pm.dispose();if(scene.environment)scene.environment.dispose();scene.environment=e;}}
    finally{for(let i=0;i<lit.length;i+=2)lit[i].material.color.copy(lit[i+1]);hid.forEach(g=>g.visible=true);scene.remove(cc);rt.dispose();}}catch(e){console.warn('room reflections',e);}
  applyEnvProbe();}
function buildToy(def){TOYF=[];TOYP=[];TOYB=[];if(def.look==='bedroom')toyBedroom(def);}
function toyScenery(def){toyRails(def);TOYB.forEach(j=>toyBooster(j));/* the motor housings go on last, once the shortcuts are known */}
